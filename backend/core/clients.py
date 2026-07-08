# backend/core/clients.py
"""
Shared client/model factories used by both the ingestion pipeline
(upload.py) and the retrieval pipeline (retriever.py). Factoring them
here means both sides always use the identical embedding model, dims,
and reranker config, no silent drift between ingest-time and
query-time behavior.
"""
import logging

from llama_index.postprocessor.jinaai_rerank import JinaRerank
from pinecone import Pinecone
from upstash_redis import Redis

from core import config

log = logging.getLogger(__name__)


def get_reranker() -> JinaRerank:
    return JinaRerank(
        model=config.JINA_RERANK_MODEL,
        api_key=config.JINA_API_KEY,
        top_n=config.RERANK_TOP_N,
    )


def get_pinecone_index() -> "Index":
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index(config.PINECONE_INDEX_NAME)


def get_redis_client() -> "Redis | None":

    if not config.CACHE_ENABLED:
        return None

    if not config.UPSTASH_REDIS_REST_URL or not config.UPSTASH_REDIS_REST_TOKEN:
        log.warning("[REDIS] Missing Upstash credentials — caching disabled.")
        return None

    try:
        client = Redis(
            url=config.UPSTASH_REDIS_REST_URL,
            token=config.UPSTASH_REDIS_REST_TOKEN,
        )
        client.ping()  # fail fast at startup, not on first request
        return client
    except Exception as e:
        log.warning(f"[REDIS] Could not connect ({e}) — caching disabled.")
        return None