import re
import json
import asyncio
import httpx
from shapely import node
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import checkpoint_exists, load_checkpoint, save_checkpoint, checkpoint_path

CONCURRENT_REQUESTS = 5
BATCH_SAVE_EVERY    = 50
OLLAMA_BASE_URL     = "http://localhost:11434"
ENRICH_MODEL        = "gemma3:1b"
ENRICHMENT_CONTEXT_CHARS = 2000 

PROMPT_TEMPLATE = """\
You are an expert Malaysian corporate lawyer. Read the text and extract metadata.
Respond ONLY with a valid JSON object. No markdown, no explanation, no code fences.

{{
  "jurisdiction": "ONE OF: federal, state, local, unknown",
  "authority":    "ONE OF: SSM, KKM, DBKL, MPKj, LHDN, MyIPO, unknown",
  "topic":        "ONE OF: tax, licensing, zoning, employment, registration, compliance, unknown",
  "document_type":"ONE OF: act, guideline, form, fee_schedule, unknown"
}}

TEXT:
{chunk_text}"""

FALLBACK_METADATA = {
    "jurisdiction": "unknown",
    "authority":    "unknown",
    "topic":        "unknown",
    "document_type":"unknown",
}

def _extract_json(raw: str) -> dict:
    """
    Try to parse JSON from the model response robustly:
    1. Direct parse
    2. Strip markdown code fences then parse
    3. Regex extract first {...} block
    """
    # 1. Direct
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Strip ```json ... ``` fences
    stripped = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 3. Grab first { ... } block
    match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {raw[:200]}")


def _is_fallback(node) -> bool:
    """True if this node's metadata is exactly the fallback defaults — i.e. enrichment failed for it."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


async def enrich_single_node_async(semaphore, node, index: int, total: int):
    """
    Call Ollama /api/generate directly (not /api/chat) so the response
    shape is always { "response": "..." } regardless of parallel settings.
    """
    async with semaphore:
        prompt = PROMPT_TEMPLATE.format(chunk_text=node.text[:ENRICHMENT_CONTEXT_CHARS])
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model":  ENRICH_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",      # Ollama JSON mode — forces valid JSON output
                        "options": {"temperature": 0.1},
                    },
                )
                resp.raise_for_status()
                raw = resp.json()["response"]   # always "response" on /api/generate

            extracted = _extract_json(raw)
            node.metadata.update(extracted)
            log.info(f"  [{index + 1}/{total}] OK")
            return True

        except (ValueError, KeyError) as e:
            log.warning(f"  [{index + 1}/{total}] JSON parse failed — using fallback. ({e})")
            node.metadata.update(FALLBACK_METADATA)
            return False
        except Exception as e:
            log.error(f"  [{index + 1}/{total}] ERROR — {e}")
            node.metadata.update(FALLBACK_METADATA)
            return False


async def enrich_batch_async(nodes: list, start_index: int, doc_name: str) -> None:
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    remaining = nodes[start_index:]
    total     = len(nodes)

    for batch_start in range(0, len(remaining), BATCH_SAVE_EVERY):
        batch          = remaining[batch_start: batch_start + BATCH_SAVE_EVERY]
        actual_indices = range(
            start_index + batch_start,
            start_index + batch_start + len(batch),
        )

        tasks = [
            enrich_single_node_async(semaphore, node, idx, total)
            for node, idx in zip(batch, actual_indices)
        ]
        await asyncio.gather(*tasks)

        completed_up_to = start_index + batch_start + len(batch)
        save_checkpoint("nodes_enriched_partial", doc_name, (nodes, completed_up_to))
        log.info(f"  [PARTIAL SAVE] Progress saved at node {completed_up_to}/{total}.")


def stage_enrich(nodes: list, doc_name: str) -> list:
    """
    Enrich nodes with LLM-extracted metadata.
    Calls /api/generate directly to avoid the /api/chat JSON shape mismatch.
    """
    if checkpoint_exists("nodes_enriched", doc_name):
        log.info(f"[SKIP] Enrichment already done for '{doc_name}'. Loading checkpoint.")
        return load_checkpoint("nodes_enriched", doc_name)

    partial = load_checkpoint("nodes_enriched_partial", doc_name)
    start_index = 0
    if partial is not None:
        saved_nodes, start_index = partial
        for i in range(start_index):
            nodes[i].metadata = saved_nodes[i].metadata
        log.info(f"[RESUME] Resuming enrichment from node {start_index}/{len(nodes)}.")

    log.info(
        f"[START] Enriching {len(nodes) - start_index} remaining nodes "
        f"({CONCURRENT_REQUESTS} at a time) for '{doc_name}'..."
    )

    asyncio.run(enrich_batch_async(nodes, start_index, doc_name))

    fallback_count = sum(1 for n in nodes if _is_fallback(n))
    if fallback_count:
        pct = fallback_count / len(nodes) * 100
        log.warning(
            f"[ENRICHMENT QUALITY] '{doc_name}': {fallback_count}/{len(nodes)} "
            f"chunks ({pct:.1f}%) fell back to default metadata and will be "
            f"invisible to authority/topic filters."
        )

    save_checkpoint("nodes_enriched", doc_name, nodes)
