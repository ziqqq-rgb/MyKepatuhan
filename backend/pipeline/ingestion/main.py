import sys
from pathlib import Path
from dotenv import load_dotenv

from pipeline.ingestion.logger import log
from pipeline.ingestion.parse import stage_parse
from pipeline.ingestion.metadata import stage_enrich
from pipeline.ingestion.sanitize import stage_sanitize
from pipeline.ingestion.upload import stage_upload
from pipeline.ingestion.checkpointing import is_duplicate, register_document
from pipeline.ingestion.naming import parse_document_name
load_dotenv()

def ingest_document(file_path: str, source_title: str | None = None) -> None:
    doc_name = Path(file_path).stem  # internal checkpoint/dedup key — unchanged
    display_title = Path(source_title).stem if source_title else doc_name
    document_name, document_version = parse_document_name(doc_name)

    log.info(f"\n{'='*60}")
    log.info(f"INGESTING: {file_path} (name='{document_name}', version={document_version})")
    log.info(f"{'='*60}")

    duplicate, file_hash = is_duplicate(file_path)
    if duplicate:
        return

    nodes = stage_parse(file_path)
    for node in nodes:
        node.metadata["source_document"] = display_title
        node.metadata["document_name"] = document_name
        node.metadata["document_version"] = document_version

    nodes = stage_enrich(nodes, doc_name)
    nodes = stage_sanitize(nodes)
    stage_upload(nodes, doc_name)

    register_document(file_path, doc_name, file_hash)

    log.info(f"\n✅ DONE: '{doc_name}' is fully ingested into Pinecone.\n")

def ingest_folder(folder_path: str) -> None:
    """
    Ingests every PDF in `folder_path`, one at a time. A failure on one
    file is logged and skipped, it never stops the rest of the batch.
    Already-ingested files are skipped automatically via the existing
    hash/upload checkpoints inside ingest_document().
    """
    pdf_paths = sorted(Path(folder_path).glob("*.pdf"))
    if not pdf_paths:
        log.warning(f"[BATCH] No PDF files found in '{folder_path}'.")
        return

    log.info(f"[BATCH] Found {len(pdf_paths)} PDF(s) in '{folder_path}'.")
    succeeded, failed = [], []

    for i, path in enumerate(pdf_paths, start=1):
        log.info(f"[BATCH] ({i}/{len(pdf_paths)}) Ingesting '{path.name}'...")
        try:
            ingest_document(str(path))
            succeeded.append(path.name)
        except Exception as e:
            log.error(f"[BATCH] FAILED on '{path.name}': {e}", exc_info=True)
            failed.append(path.name)

    log.info(f"[BATCH DONE] {len(succeeded)} succeeded, {len(failed)} failed.")
    if failed:
        log.warning(f"[BATCH] Failed files: {failed}")