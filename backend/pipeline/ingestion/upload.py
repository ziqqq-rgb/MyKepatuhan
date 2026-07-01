from llama_index.core import Settings
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import load_uploaded_log, mark_as_uploaded


def stage_upload(nodes: list, doc_name: str) -> None:
    """Embed nodes and upload to Pinecone. Skips if already uploaded."""
    uploaded = load_uploaded_log()
    if doc_name in uploaded:
        log.info(f"[SKIP] '{doc_name}' already uploaded to Pinecone. Skipping.")
        return

    log.info(f"[START] Embedding and uploading '{doc_name}' ({len(nodes)} nodes) to Pinecone...")

    from llama_index.vector_stores.pinecone import PineconeVectorStore
    from llama_index.core import VectorStoreIndex, StorageContext
    from core.clients import get_embed_model, get_pinecone_index

    embed_model = get_embed_model()
    Settings.embed_model = embed_model

    pinecone_index = get_pinecone_index()

    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index,
        #add_sparse_vector=True,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    mark_as_uploaded(doc_name)
    log.info(f"[DONE] '{doc_name}' successfully uploaded to Pinecone.")