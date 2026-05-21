import json
from pipeline.ingestion.logger import log

def stage_sanitize(nodes: list) -> list:
    """Convert complex metadata values to strings for Pinecone compatibility."""
    for node in nodes:
        for key, value in list(node.metadata.items()):
            if isinstance(value, (dict, list)):
                node.metadata[key] = json.dumps(value)
            elif value is None:
                node.metadata[key] = ""
    log.info(f"[DONE] Metadata sanitized for {len(nodes)} nodes.")
    return nodes