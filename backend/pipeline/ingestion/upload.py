import os
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import load_uploaded_log, mark_as_uploaded

def stage_upload(nodes: list, doc_name: str) -> None:
    """Embed nodes and upload to Pinecone. Skips if already uploaded."""
    uploaded = load_uploaded_log()
    if doc_name in uploaded:
        log.info(f"[SKIP] '{doc_name}' already uploaded to Pinecone. Skipping.")
        return

    log.info(f"[START] Embedding and uploading '{doc_name}' ({len(nodes)} nodes) to Pinecone...")

    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.pinecone import PineconeVectorStore
    from llama_index.core import VectorStoreIndex, Settings, StorageContext
    from pinecone import Pinecone

    PINECONE_API_KEY = os.getenv("PINECON_KEY")

    embed_model = OllamaEmbedding(
        model_name="nomic-embed-text-v2-moe",
        embed_batch_size=50,
    )
    Settings.embed_model = embed_model

    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index("mykepatuhan")

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    mark_as_uploaded(doc_name)
    log.info(f"[DONE] '{doc_name}' successfully uploaded to Pinecone.")