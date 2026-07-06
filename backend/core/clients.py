"""
Shared client/model factories used by both the ingestion pipeline
(upload.py) and the retrieval pipeline (retriever.py). Factoring them
here means both sides always use the identical embedding model, dims,
and reranker config — no silent drift between ingest-time and
query-time behavior.
"""
from google.genai import types
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.postprocessor.jinaai_rerank import JinaRerank
from pinecone import Pinecone
from upstash_redis import Redis
import logging
from core import config


log = logging.getLogger(__name__)


def get_embed_model(api_key: str | None = None) -> GoogleGenAIEmbedding:
    """Returns a Gemini Embedding client. Defaults to the primary embed
    key; pass `api_key` to build one client per key for a rotation pool
    (see pipeline/ingestion/upload.py)."""
    return GoogleGenAIEmbedding(
        model_name=config.GEMINI_EMBED_MODEL,
        api_key=api_key or config.GEMINI_EMBED_API_KEY,
        embed_batch_size=config.EMBED_BATCH_SIZE,
        embedding_config=types.EmbedContentConfig(
            output_dimensionality=config.EMBED_OUTPUT_DIMENSIONALITY,
        ),
    )
    
def get_reranker() -> JinaRerank:
    """Returns the shared Jina reranker client — hosted API, no local model."""
    return JinaRerank(
        model=config.JINA_RERANK_MODEL,
        api_key=config.JINA_API_KEY,
        top_n=config.RERANK_TOP_N,
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
