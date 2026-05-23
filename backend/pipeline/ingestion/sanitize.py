import json
from pipeline.ingestion.logger import log

def stage_sanitize(nodes: list) -> list:
    """
    Convert complex metadata values to strings, drop massive Docling layout data,
    and enforce size limits for Pinecone compatibility.
    """
    # Docling attaches massive layout arrays that exceed Pinecone's 40KB limit.
    # We do not need these for vector search, so we drop them completely.
    KEYS_TO_DROP = ["doc_items", "layout", "bounding_box", "paths", "styles"]

    for node in nodes:
        # Iterate over a copy of keys so we can safely delete items
        for key in list(node.metadata.keys()):
            
            # 1. Drop known bloated keys entirely
            if key in KEYS_TO_DROP:
                del node.metadata[key]
                continue
                
            value = node.metadata[key]

            # 2. Stringify complex types (dicts/lists)
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                node.metadata[key] = value
            # Convert None to empty string
            elif value is None:
                node.metadata[key] = ""
                value = ""
                
            # 3. Truncate any unusually long strings (Pinecone limit is 40KB total)
            # 10,000 characters is roughly 10KB, leaving plenty of room.
            if isinstance(value, str) and len(value) > 10000:
                node.metadata[key] = value[:10000] + "...[TRUNCATED]"

    log.info(f"[DONE] Metadata sanitized and size-limited for {len(nodes)} nodes.")
    return nodes