"""
Shared embedding client factories — one for ingestion (upload.py), one
for retrieval (retriever.py).

jina-embeddings-v3 uses task-specific adapters on top of one shared
backbone. The "retrieval.passage" and "retrieval.query" adapters are
trained together as an asymmetric pair so a passage encoded with one
and a query encoded with the other land in a comparable vector space —
this is the intended way to use the model for retrieval, not a
different model per side.
"""
from llama_index.embeddings.jinaai import JinaEmbedding

from core import config


def _build_embed_model(task: str) -> JinaEmbedding:
    return JinaEmbedding(
        api_key=config.JINA_API_KEY,
        model=config.JINA_EMBED_MODEL,
        task=task,
        dimensions=config.EMBED_OUTPUT_DIMENSIONALITY,
        embed_batch_size=config.EMBED_BATCH_SIZE,
    )


def get_document_embed_model() -> JinaEmbedding:
    """Used at ingest time to encode chunks being indexed."""
    return _build_embed_model(task="retrieval.passage")


def get_query_embed_model() -> JinaEmbedding:
    """Used at query time to encode the user's question."""
    return _build_embed_model(task="retrieval.query")