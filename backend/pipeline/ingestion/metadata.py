import os
import re
import json
import asyncio
import httpx
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import (
    checkpoint_exists, load_checkpoint, save_checkpoint
)
from dotenv import load_dotenv
load_dotenv()
# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

CONCURRENT_REQUESTS      = 5       # Flash Lite allows 15 RPM — 5 concurrent is safe headroom
BATCH_SAVE_EVERY         = 50
ENRICHMENT_CONTEXT_CHARS = 2000
MAX_RETRIES              = 3

GEMINI_API_KEY  = os.getenv("GEMINI_KEY")
ENRICH_MODEL    = "gemini-3.1-flash-lite"

# ─────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────

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
    "jurisdiction":  "unknown",
    "authority":     "unknown",
    "topic":         "unknown",
    "document_type": "unknown",
}

# ─────────────────────────────────────────
# JSON EXTRACTION
# ─────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    """
    Parse JSON from model response robustly:
    1. Direct parse
    2. Strip markdown fences then parse
    3. Regex extract first {...} block
    Since we use responseMimeType=application/json, step 1 should
    almost always succeed — the others are a safety net.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    stripped = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {raw[:200]}")


def _is_fallback(node) -> bool:
    """True if enrichment failed and the node is stuck on all-unknown defaults."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


# ─────────────────────────────────────────
# ASYNC ENRICHMENT
# ─────────────────────────────────────────

async def enrich_single_node_async(semaphore, node, index: int, total: int):
    """
    Calls Gemini 3.1 Flash Lite via the REST generateContent endpoint.
    Retries on 429 with exponential backoff — a rate-limit blip shouldn't
    permanently poison a chunk's metadata with fallback values.
    """
    async with semaphore:
        prompt = PROMPT_TEMPLATE.format(chunk_text=node.text[:ENRICHMENT_CONTEXT_CHARS])

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",  # Gemini native JSON mode — forces valid JSON output
            },
        }

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.post( json=payload)

                if resp.status_code == 429:
                    wait = 5 * (2 ** attempt)   # 5s → 10s → 20s
                    log.warning(
                        f"  [{index + 1}/{total}] Rate limited — "
                        f"retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()

                candidates = resp.json().get("candidates", [])
                if not candidates:
                    raise ValueError("Empty candidates list in Gemini response")

                raw = candidates[0]["content"]["parts"][0]["text"]
                extracted = _extract_json(raw)
                node.metadata.update(extracted)
                log.info(f"  [{index + 1}/{total}] OK → {extracted}")
                return True

            except (ValueError, KeyError) as e:
                log.warning(
                    f"  [{index + 1}/{total}] JSON parse failed — "
                    f"using fallback. ({e})"
                )
                node.metadata.update(FALLBACK_METADATA)
                return False

            except Exception as e:
                log.error(f"  [{index + 1}/{total}] ERROR — {e}")
                node.metadata.update(FALLBACK_METADATA)
                return False

        # Exhausted all retries
        log.error(
            f"  [{index + 1}/{total}] Rate limited after {MAX_RETRIES} retries — "
            f"using fallback."
        )
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
        results = await asyncio.gather(*tasks)

        completed_up_to = start_index + batch_start + len(batch)
        save_checkpoint("nodes_enriched_partial", doc_name, (nodes, completed_up_to))

        fallbacks_this_batch = sum(1 for r in results if not r)
        log.info(
            f"  [PARTIAL SAVE] Progress: {completed_up_to}/{total} nodes "
            f"({fallbacks_this_batch} fallbacks this batch)"
        )


# ─────────────────────────────────────────
# STAGE ENTRY POINT
# ─────────────────────────────────────────

def stage_enrich(nodes: list, doc_name: str) -> list:
    """
    Enrich nodes with LLM-extracted metadata via Gemini 3.1 Flash Lite.
    Checkpoints partial progress so a rate-limit interruption can resume
    rather than restart from scratch.
    """
    if checkpoint_exists("nodes_enriched", doc_name):
        log.info(
            f"[SKIP] Enrichment already done for '{doc_name}'. "
            f"Loading checkpoint."
        )
        return load_checkpoint("nodes_enriched", doc_name)

    partial = load_checkpoint("nodes_enriched_partial", doc_name)
    start_index = 0
    if partial is not None:
        saved_nodes, start_index = partial
        for i in range(start_index):
            nodes[i].metadata = saved_nodes[i].metadata
        log.info(
            f"[RESUME] Resuming enrichment from node "
            f"{start_index}/{len(nodes)}."
        )

    log.info(
        f"[START] Enriching {len(nodes) - start_index} remaining nodes "
        f"({CONCURRENT_REQUESTS} concurrent) for '{doc_name}' "
        f"via Gemini 3.1 Flash Lite..."
    )

    asyncio.run(enrich_batch_async(nodes, start_index, doc_name))

    # ── Fallback-rate audit ──
    fallback_count = sum(1 for n in nodes if _is_fallback(n))
    if fallback_count:
        pct = fallback_count / len(nodes) * 100
        log.warning(
            f"[ENRICHMENT QUALITY] '{doc_name}': {fallback_count}/{len(nodes)} "
            f"chunks ({pct:.1f}%) fell back to default metadata — these chunks "
            f"will be invisible to authority/topic filters."
        )
    else:
        log.info(
            f"[ENRICHMENT QUALITY] '{doc_name}': all {len(nodes)} chunks "
            f"enriched successfully."
        )

    save_checkpoint("nodes_enriched", doc_name, nodes)
    return nodes