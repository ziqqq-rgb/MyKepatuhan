import sys
from pathlib import Path
from dotenv import load_dotenv

from pipeline.ingestion.logger import log
from pipeline.ingestion.parse import stage_parse
from pipeline.ingestion.metadata import stage_enrich
from pipeline.ingestion.sanitize import stage_sanitize
from pipeline.ingestion.upload import stage_upload
from pipeline.ingestion.checkpointing import is_duplicate, register_document

load_dotenv()

def ingest_document(file_path: str, source_title: str | None = None) -> None:
    doc_name = Path(file_path).stem  # internal checkpoint/dedup key — unchanged
    display_title = Path(source_title).stem if source_title else doc_name

    log.info(f"\n{'='*60}")
    log.info(f"INGESTING: {file_path}")
    log.info(f"{'='*60}")

    duplicate, file_hash = is_duplicate(file_path)
    if duplicate:
        return

    nodes = stage_parse(file_path)
    for node in nodes:
        node.metadata["source_document"] = display_title

    nodes = stage_enrich(nodes, doc_name)
    nodes = stage_sanitize(nodes)
    stage_upload(nodes, doc_name)

    register_document(file_path, doc_name, file_hash)

    log.info(f"\n✅ DONE: '{doc_name}' is fully ingested into Pinecone.\n")

