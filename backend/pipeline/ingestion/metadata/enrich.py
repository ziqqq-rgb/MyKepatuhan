"""
Orchestrates metadata enrichment across all nodes of a document:
batches concurrent Gemini calls, checkpoints partial progress so a
rate-limit interruption can resume rather than restart from scratch,
and audits the final fallback rate.
"""
import asyncio

from core import config
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import (
    checkpoint_exists, load_checkpoint, save_checkpoint
)
from pipeline.ingestion.metadata.gemini_client import (
    enrich_single_node_async, is_fallback
)


async def enrich_batch_async(nodes: list, start_index: int, doc_name: str) -> None:
    semaphore = asyncio.Semaphore(config.ENRICHMENT_CONCURRENT_REQUESTS)
    remaining = nodes[start_index:]
    total     = len(nodes)

    for batch_start in range(0, len(remaining), config.ENRICHMENT_BATCH_SAVE_EVERY):
        batch          = remaining[batch_start: batch_start + config.ENRICHMENT_BATCH_SAVE_EVERY]
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
        f"({config.ENRICHMENT_CONCURRENT_REQUESTS} concurrent) for '{doc_name}' "
        f"via Gemini 3.1 Flash Lite..."
    )

    asyncio.run(enrich_batch_async(nodes, start_index, doc_name))

    # ── Fallback-rate audit ──
    fallback_count = sum(1 for n in nodes if is_fallback(n))
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