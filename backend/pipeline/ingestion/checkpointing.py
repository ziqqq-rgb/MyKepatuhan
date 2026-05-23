from datetime import datetime
import hashlib
import json
import pickle
from pathlib import Path
from pipeline.ingestion.logger import log

CHECKPOINT_DIR = Path(".checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)

# File that tracks which document names have been uploaded
UPLOADED_LOG = CHECKPOINT_DIR / "uploaded_docs.json"

def checkpoint_path(stage: str, doc_name: str) -> Path:
    """Returns the file path for a given stage + document checkpoint."""
    safe_name = doc_name.replace("/", "_").replace("\\", "_")
    return CHECKPOINT_DIR / f"{safe_name}__{stage}.pkl"

def save_checkpoint(stage: str, doc_name: str, data) -> None:
    path = checkpoint_path(stage, doc_name)
    
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        pickle.dump(data, f)
    log.info(f"[CHECKPOINT SAVED] stage={stage} | doc={doc_name} → {path}")

def load_checkpoint(stage: str, doc_name: str):
    path = checkpoint_path(stage, doc_name)
    if path.exists():
        with open(path, "rb") as f:
            data = pickle.load(f)
        log.info(f"[CHECKPOINT LOADED] stage={stage} | doc={doc_name} ← {path}")
        return data
    return None

def checkpoint_exists(stage: str, doc_name: str) -> bool:
    return checkpoint_path(stage, doc_name).exists()

def load_uploaded_log() -> set:
    if UPLOADED_LOG.exists():
        with open(UPLOADED_LOG) as f:
            return set(json.load(f))
    return set()

def mark_as_uploaded(doc_name: str) -> None:
    uploaded = load_uploaded_log()
    uploaded.add(doc_name)
    with open(UPLOADED_LOG, "w") as f:
        json.dump(list(uploaded), f, indent=2)



HASH_REGISTRY = CHECKPOINT_DIR / "hash_registry.json"

def load_hash_registry() -> dict:
    if HASH_REGISTRY.exists():
        with open(HASH_REGISTRY) as f:
            return json.load(f)
    return {}

def save_hash_registry(registry: dict) -> None:
    with open(HASH_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2)

def compute_file_hash(file_path: str) -> str:
    """Returns SHA-256 hex digest of file contents."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def is_duplicate(file_path: str):
    """Returns (is_duplicate, file_hash). Checks registry, not filename."""
    file_hash = compute_file_hash(file_path)
    registry = load_hash_registry()
    if file_hash in registry:
        original = registry[file_hash]
        log.warning(
            f"[DUPLICATE] '{Path(file_path).name}' is identical to "
            f"'{original['file']}' (ingested {original['ingested_at']}). Skipping."
        )
        return True, file_hash
    return False, file_hash

def register_document(file_path: str, doc_name: str, file_hash: str) -> None:
    """Record this document in the hash registry after successful ingestion."""
    registry = load_hash_registry()
    registry[file_hash] = {
        "doc_name": doc_name,
        "file": Path(file_path).name,
        "ingested_at": datetime.now().isoformat(),
    }
    save_hash_registry(registry)
    log.info(f"[REGISTRY] Recorded '{doc_name}' (hash: {file_hash[:12]}...)")