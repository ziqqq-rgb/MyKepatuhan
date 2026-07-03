"""
Minimal JSON checkpoint for retrieval-comparison runs — one file per
strategy under results/checkpoints/. Each row is saved as soon as it's
scored, so a quota or rate-limit failure loses at most the row in
flight, not the whole strategy.
"""
import json
from pathlib import Path

CHECKPOINT_DIR = Path(__file__).parent / "results" / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def _path(strategy: str) -> Path:
    return CHECKPOINT_DIR / f"{strategy}.json"


def load_scored_rows(strategy: str) -> list[dict]:
    path = _path(strategy)
    return json.loads(path.read_text()) if path.exists() else []


def save_scored_rows(strategy: str, rows: list[dict]) -> None:
    _path(strategy).write_text(json.dumps(rows, indent=2))


def already_scored_questions(strategy: str) -> set[str]:
    return {row["question"] for row in load_scored_rows(strategy)}