import json
import asyncio
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import checkpoint_exists, load_checkpoint, save_checkpoint, checkpoint_path

CONCURRENT_REQUESTS = 5
BATCH_SAVE_EVERY = 50

PROMPT_TEMPLATE = """
You are an expert Malaysian corporate lawyer. Read the following text chunk and extract the metadata.
You MUST respond ONLY with a valid JSON object matching this exact format. Do not include markdown formatting or explanations.

{{
  "jurisdiction": "Choose ONE: federal, state, local, any related or unknown",
  "authority": "Choose ONE: SSM, KKM, DBKL, MPKj, LHDN, any related or unknown",
  "topic": "Choose ONE: tax, licensing, zoning, employment, registration, any related or unknown",
  "document_type": "Choose ONE: act, guideline, form, fee_schedule, any related or unknown"
}}

TEXT TO ANALYZE:
{chunk_text}
"""

async def enrich_single_node_async(llm, semaphore, node, index: int, total: int):
    """
    Enrich one node concurrently. The semaphore limits how many
    run at the same time so Ollama isn't overwhelmed.
    """
    async with semaphore:
        prompt = PROMPT_TEMPLATE.format(chunk_text=node.text[:1500])
        try:
            response = await llm.acomplete(prompt)
            extracted = json.loads(response.text)
            node.metadata.update(extracted)
            log.info(f"  [{index + 1}/{total}] OK")
            return True
        except json.JSONDecodeError:
            log.warning(f"  [{index + 1}/{total}] SKIPPED — LLM returned invalid JSON")
            return False
        except Exception as e:
            log.error(f"  [{index + 1}/{total}] ERROR — {e}")
            return False

async def enrich_batch_async(llm, nodes: list, start_index: int, doc_name: str) -> None:
    """Run enrichment concurrently over all remaining nodes with periodic saves."""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    remaining = nodes[start_index:]
    total = len(nodes)

    # Split remaining nodes into chunks of BATCH_SAVE_EVERY
    # so we can save progress periodically between batches
    for batch_start in range(0, len(remaining), BATCH_SAVE_EVERY):
        batch = remaining[batch_start: batch_start + BATCH_SAVE_EVERY]
        actual_indices = range(
            start_index + batch_start,
            start_index + batch_start + len(batch)
        )

        tasks = [
            enrich_single_node_async(llm, semaphore, node, idx, total)
            for node, idx in zip(batch, actual_indices)
        ]

        await asyncio.gather(*tasks)

        completed_up_to = start_index + batch_start + len(batch)
        
        # FIX: Actually trigger the save_checkpoint function!
        save_checkpoint("nodes_enriched_partial", doc_name, (nodes, completed_up_to))
        log.info(f"  [PARTIAL SAVE] Progress saved at node {completed_up_to}/{total}.")

def stage_enrich(nodes: list, doc_name: str) -> list:
    """
    Enrich nodes with LLM-extracted metadata — runs concurrently.
    Checkpoints every {BATCH_SAVE_EVERY} nodes so a crash doesn't restart from zero.
    """
    from llama_index.llms.ollama import Ollama

    # Skip entirely if already done
    if checkpoint_exists("nodes_enriched", doc_name):
        log.info(f"[SKIP] Enrichment already done for '{doc_name}'. Loading checkpoint.")
        return load_checkpoint("nodes_enriched", doc_name)

    # Resume from partial progress if a crash happened mid-way
    partial = load_checkpoint("nodes_enriched_partial", doc_name)
    start_index = 0
    if partial is not None:
        saved_nodes, start_index = partial
        for i in range(start_index):
            nodes[i].metadata = saved_nodes[i].metadata
        log.info(f"[RESUME] Resuming enrichment from node {start_index}/{len(nodes)}.")

    llm = Ollama(
        model="gemma4:e4b",
        temperature=0.1,
        request_timeout=120,
    )

    log.info(
        f"[START] Enriching {len(nodes) - start_index} remaining nodes "
        f"({CONCURRENT_REQUESTS} at a time) for '{doc_name}'..."
    )

    # Note: We pass doc_name down into the async function now so it can save!
    asyncio.run(enrich_batch_async(llm, nodes, start_index, doc_name))

    # Save final completed result
    save_checkpoint("nodes_enriched", doc_name, nodes)

    # Clean up the partial checkpoint
    partial_path = checkpoint_path("nodes_enriched_partial", doc_name)
    if partial_path.exists():
        partial_path.unlink()
        log.info(f"[CLEANUP] Removed partial checkpoint for '{doc_name}'.")

    log.info(f"[DONE] Enrichment complete for '{doc_name}'.")
    return nodes