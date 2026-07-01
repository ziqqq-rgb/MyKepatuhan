"""
Shared client/model factories used by both the ingestion pipeline
(upload.py) and the retrieval pipeline (retriever.py).

Previously, both files independently constructed an identical
OllamaEmbedding instance and Pinecone index client. Factoring them
here removes that duplication so the two pipelines can't silently
drift apart (e.g. one side changing instruction prefixes without the
other). Behavior is unchanged — same model name, same args.
"""
from llama_index.embeddings.ollama import OllamaEmbedding
from pinecone import Pinecone
from upstash_redis import Redis
import logging
from core import config

log = logging.getLogger(__name__)


def get_embed_model() -> OllamaEmbedding:
    """Returns the shared nomic-embed-text-v2-moe embedding model."""
    return OllamaEmbedding(
        model_name=config.EMBED_MODEL_NAME,
        embed_batch_size=config.EMBED_BATCH_SIZE,
        query_instruction=config.EMBED_QUERY_INSTRUCTION,
        text_instruction=config.EMBED_TEXT_INSTRUCTION,
    )

def get_pinecone_index() -> "Index":
    """Returns the shared 'mykepatuhan' Pinecone index client."""
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index(config.PINECONE_INDEX_NAME)

def get_redis_client() -> "Redis | None":
    """
    Returns the shared Upstash Redis client, or None if caching is
    disabled or misconfigured. Callers must handle None — caching
    is always optional, never a hard dependency.
    """
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
