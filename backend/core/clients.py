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
from pinecone.data.index import Index as PineconeIndex

from core import config


def get_embed_model() -> OllamaEmbedding:
    """Returns the shared nomic-embed-text-v2-moe embedding model."""
    return OllamaEmbedding(
        model_name=config.EMBED_MODEL_NAME,
        embed_batch_size=config.EMBED_BATCH_SIZE,
        query_instruction=config.EMBED_QUERY_INSTRUCTION,
        text_instruction=config.EMBED_TEXT_INSTRUCTION,
    )


def get_pinecone_index() -> PineconeIndex:
    """Returns the shared 'mykepatuhan' Pinecone index client."""
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index(config.PINECONE_INDEX_NAME)