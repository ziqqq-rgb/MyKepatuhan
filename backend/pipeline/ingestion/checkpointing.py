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