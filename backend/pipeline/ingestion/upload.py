"""
Embeds nodes and upserts them to Pinecone via the shared Jina AI
embedding client (see core/embeddings.py). Jina's limits (100 RPM /
100K TPM) comfortably cover a full document's chunks in a handful of
batched requests — no manual pacing needed.
"""
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

from core.clients import get_pinecone_index
from core.embeddings import get_document_embed_model
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import load_uploaded_log, mark_as_uploaded


def stage_upload(nodes: list, doc_name: str) -> None:
    """Embed nodes and upload to Pinecone. Skips if already uploaded."""
    uploaded = load_uploaded_log()
    if doc_name in uploaded:
        log.info(f"[SKIP] '{doc_name}' already uploaded to Pinecone. Skipping.")
        return

    log.info(f"[START] Embedding and uploading '{doc_name}' ({len(nodes)} nodes) to Pinecone...")

    embed_model = get_document_embed_model()
    Settings.embed_model = embed_model

    vector_store = PineconeVectorStore(pinecone_index=get_pinecone_index())
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    mark_as_uploaded(doc_name)
    log.info(f"[DONE] '{doc_name}' successfully uploaded to Pinecone.")