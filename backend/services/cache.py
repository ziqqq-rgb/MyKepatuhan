"""
Query-response cache backed by Upstash Redis.

Caches the full QueryResponse (answer + citations) keyed by a hash of
the normalized question + filters. A cache hit skips retrieval,
reranking, AND the Gemini generation call — the three most expensive
steps in the query pipeline.

Fails open: if Redis is unreachable or disabled, get/set just no-op
so a request never fails because of the cache.
"""
import hashlib
import json
import logging

from core import config
from core.clients import get_redis_client

log = logging.getLogger(__name__)

_redis = get_redis_client()


def _build_key(question: str, authority: str | None, topic: str | None) -> str:
    """One cache entry per distinct (question, authority, topic) combo."""
    normalized = f"{question.strip().lower()}|{authority or ''}|{topic or ''}"
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"query_cache:{digest}"


def get_cached_response(question: str, authority: str | None, topic: str | None) -> dict | None:
    """Returns a cached response dict, or None on a miss / disabled cache."""
    if _redis is None:
        return None
    try:
        raw = _redis.get(_build_key(question, authority, topic))
    except Exception as e:
        log.warning(f"[CACHE] GET failed, skipping cache: {e}")
        return None
    return json.loads(raw) if raw else None


def set_cached_response(question: str, authority: str | None, topic: str | None, response: dict) -> None:
    """Stores a response dict with the configured TTL. No-ops if Redis is unavailable."""
    if _redis is None:
        return
    try:
        key = _build_key(question, authority, topic)
        _redis.set(key, json.dumps(response), ex=config.CACHE_TTL_SECONDS)
    except Exception as e:
        log.warning(f"[CACHE] SET failed, skipping cache: {e}")