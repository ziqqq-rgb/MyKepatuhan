"""
Enrichment call orchestration: rotates across Gemini API keys, paced by
one shared rate limiter.

IMPORTANT: build_enrichment_state() must be called fresh for each
asyncio.run() invocation (i.e. once per document — see enrich_batch_async),
never stored at module scope. asyncio.Lock binds to whichever event loop
first awaits it; a module-level singleton reused across multiple
asyncio.run() calls (one per document in a batch) binds to the first
document's loop, then errors on every document after it with
"bound to a different event loop".
"""
import asyncio
from typing import NamedTuple

from core import config
from pipeline.ingestion.logger import log
from pipeline.ingestion.metadata.gemini_payload import build_enrichment_payload
from pipeline.ingestion.metadata.gemini_request import call_gemini, RateLimited
from services.key_rotation import RoundRobinPool
from services.gemini_rate_limiter import AsyncRateLimiter

FALLBACK_METADATA = {
    "jurisdiction":  "unclassified",
    "authority":     "unclassified",
    "topic":         "unclassified",
    "document_type": "unclassified",
}


class EnrichmentState(NamedTuple):
    """Bundles one document's key pool and rate limiter."""
    key_pool: RoundRobinPool
    limiter: AsyncRateLimiter


def build_enrichment_state() -> EnrichmentState:
    """Creates a fresh key pool + rate limiter for one enrichment run."""
    return EnrichmentState(
        key_pool=RoundRobinPool(config.GEMINI_ENRICH_API_KEYS),
        limiter=AsyncRateLimiter(config.GEMINI_ENRICH_MAX_RPM),
    )


def is_fallback(node) -> bool:
    """True if enrichment failed and the node is stuck on all-unknown defaults."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


async def _fetch_with_key_rotation(
    payload: dict, state: EnrichmentState, index: int, total: int
) -> dict | None:
    """
    Each attempt waits for the shared rate budget, then tries the next
    key. If a full pass through every key still gets rate limited, backs
    off and retries the whole pool, up to ENRICHMENT_MAX_RETRIES cycles.
    Returns None only if every cycle is exhausted.
    """
    pool_size = len(state.key_pool)

    for cycle in range(config.ENRICHMENT_MAX_RETRIES):
        for key_attempt in range(pool_size):
            api_key = state.key_pool.next()
            await state.limiter.acquire()

            try:
                return await call_gemini(payload, api_key)
            except RateLimited:
                log.warning(
                    f"  [{index + 1}/{total}] Rate limited on key "
                    f"{key_attempt + 1}/{pool_size} (cycle {cycle + 1}/{config.ENRICHMENT_MAX_RETRIES})."
                )

        wait = 5 * (2 ** cycle)
        log.warning(f"  [{index + 1}/{total}] Full key pool exhausted — waiting {wait}s.")
        await asyncio.sleep(wait)

    return None


async def enrich_single_node_async(
    semaphore: asyncio.Semaphore,
    node,
    index: int,
    total: int,
    state: EnrichmentState,
) -> bool:
    """Calls Gemini for one node, falling back to default metadata on
    parse failure or total quota exhaustion."""
    async with semaphore:
        payload = build_enrichment_payload(node.text)

        try:
            extracted = await _fetch_with_key_rotation(payload, state, index, total)
        except (ValueError, KeyError) as e:
            log.warning(f"  [{index + 1}/{total}] JSON parse failed — using fallback. ({e})")
            node.metadata.update(FALLBACK_METADATA)
            return False
        except Exception as e:
            log.error(f"  [{index + 1}/{total}] ERROR — {e}")
            node.metadata.update(FALLBACK_METADATA)
            return False

        if extracted is None:
            log.error(
                f"  [{index + 1}/{total}] Rate limited across all "
                f"{len(state.key_pool)} key(s) — using fallback."
            )
            node.metadata.update(FALLBACK_METADATA)
            return False

        node.metadata.update(extracted)
        log.info(f"  [{index + 1}/{total}] OK → {extracted}")
        return True