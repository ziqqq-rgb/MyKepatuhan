import sys
from pathlib import Path
from dotenv import load_dotenv

from pipeline.ingestion.logger import log
from pipeline.ingestion.parse import stage_parse
from pipeline.ingestion.metadata import stage_enrich
from pipeline.ingestion.sanitize import stage_sanitize
from pipeline.ingestion.upload import stage_upload

load_dotenv()

def ingest_document(file_path: str) -> None:
    doc_name = Path(file_path).stem
    log.info(f"\n{'='*60}")
    log.info(f"INGESTING: {file_path}")
    log.info(f"{'='*60}")

    # Pass the data sequentially through the pipeline
    nodes = stage_parse(file_path)
    nodes = stage_enrich(nodes, doc_name)
    nodes = stage_sanitize(nodes)
    stage_upload(nodes, doc_name)

    log.info(f"\n✅ DONE: '{doc_name}' is fully ingested into Pinecone.\n")

