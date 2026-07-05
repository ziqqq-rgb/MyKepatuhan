# pipeline/ingestion/version_control.py
"""
Removes a specific version of a document from Pinecone before its
replacement is ingested. Kept separate from ingest_document on purpose —
deletion is destructive and should always be an explicit, deliberate
step, never an automatic side effect of ingesting a new file.
"""
from core.clients import get_pinecone_index
from pipeline.ingestion.logger import log


def delete_document_version(document_name: str, version: int) -> None:
    index = get_pinecone_index()
    index.delete(filter={
        "document_name": {"$eq": document_name},
        "document_version": {"$eq": version},
    })
    log.warning(f"[VERSION DELETE] Removed '{document_name}' v{version} from Pinecone.")