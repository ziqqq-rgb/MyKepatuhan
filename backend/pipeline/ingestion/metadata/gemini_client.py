"""
Orchestrates enrichment calls: pairs each key with its own rate
limiter, rotates on 429, and falls back to default metadata only if
every key is exhausted.
"""
import asyncio
import logging
from dataclasses import dataclass

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


@dataclass
class KeySlot:
    """One API key plus its own independent rate-limit budget."""
    api_key: str
    limiter: AsyncRateLimiter


_key_pool = RoundRobinPool([
    KeySlot(key, AsyncRateLimiter(config.GEMINI_ENRICH_MAX_RPM_PER_KEY))
    for key in config.GEMINI_ENRICH_API_KEYS
])
log.info(
    f"[ENRICH] Gemini key pool: {len(_key_pool)} key(s), "
    f"{config.GEMINI_ENRICH_MAX_RPM_PER_KEY} req/min budget each."
)


def is_fallback(node) -> bool:
    """True if enrichment failed and the node is stuck on all-unknown defaults."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


async def _fetch_with_key_rotation(payload: dict, index: int, total: int) -> dict | None:
    """
    Tries each key once, round-robin, waiting for that key's own rate
    budget before every attempt. A 429 rotates to the next key
    immediately; only the last key in the pool falls back to full
    exponential backoff. Returns None if every key is exhausted.
    """
    pool_size = len(_key_pool)

    for key_attempt in range(pool_size):
        is_last_key = key_attempt == pool_size - 1
        slot = _key_pool.next()
        retries = config.ENRICHMENT_MAX_RETRIES if is_last_key else 1

        for attempt in range(retries):
            await slot.limiter.acquire()
            try:
                return await call_gemini(payload, slot.api_key)
            except RateLimited as e:
                if not is_last_key:
                    log.warning(
                        f"  [{index + 1}/{total}] Rate limited on key "
                        f"{key_attempt + 1}/{pool_size} — rotating to next key."
                    )
                    break
                wait = e.retry_after_seconds or 5 * (2 ** attempt)
                log.warning(
                    f"  [{index + 1}/{total}] Rate limited — "
                    f"retrying in {wait:.0f}s (attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(wait)

    return None


async def enrich_single_node_async(semaphore, node, index: int, total: int):
    """Calls Gemini 3.1 Flash Lite for one node, falling back to default
    metadata on parse failure or total quota exhaustion."""
    async with semaphore:
        payload = build_enrichment_payload(node.text)

        try:
            extracted = await _fetch_with_key_rotation(payload, index, total)
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
                f"{len(_key_pool)} key(s) — using fallback."
            )
            node.metadata.update(FALLBACK_METADATA)
            return False

        node.metadata.update(extracted)
        log.info(f"  [{index + 1}/{total}] OK → {extracted}")
        return True