import json
from core import config
from pipeline.ingestion.logger import log

def stage_sanitize(nodes: list) -> list:
    """
    Convert complex metadata values to strings, drop massive Docling layout data,
    and enforce size limits for Pinecone compatibility.
    """
    for node in nodes:
        # Iterate over a copy of keys so we can safely delete items
        for key in list(node.metadata.keys()):

            # Drop known bloated keys entirely
            if key in config.SANITIZE_KEYS_TO_DROP:
                del node.metadata[key]
                continue

            value = node.metadata[key]

            # Stringify complex types (dicts/lists)
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                node.metadata[key] = value
            # Convert None to empty string
            elif value is None:
                node.metadata[key] = ""
                value = ""

            # Truncate any unusually long strings (Pinecone limit is 40KB total)
            if isinstance(value, str) and len(value) > config.SANITIZE_MAX_STRING_LENGTH:
                node.metadata[key] = value[:config.SANITIZE_MAX_STRING_LENGTH] + "...[TRUNCATED]"

    log.info(f"[DONE] Metadata sanitized and size-limited for {len(nodes)} nodes.")
    return nodes