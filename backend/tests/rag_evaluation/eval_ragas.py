"""
Full generation-quality evaluation: runs the golden dataset through the
production RAG pipeline and scores each answer with Ragas (faithfulness,
answer relevancy, answer correctness).

Resumable via checkpoint.py — safe to re-run after a crash or quota error.

Run (from backend/):
    python -m tests.rag_evaluation.eval_ragas
"""
import csv
import json
import time
import asyncio
from functools import partial
from pathlib import Path

from core import config
from pipeline.retriever import build_retriever
from tests.rag_evaluation.golden_dataset import TEST_QUESTIONS
from tests.rag_evaluation.judge import build_judge
from tests.rag_evaluation.evaluation_loop import run_scored_evaluation
from tests.rag_evaluation.scoring import score_row
from tests.rag_evaluation.rate_limiter import RateLimiter

GEMINI_FREE_TIER_RPM = 15  # per-key quota — scaled by pool size in main()
METRIC_NAMES = ["faithfulness", "answer_relevancy", "answer_correctness"]
CHECKPOINT_KEY = "full_generation_eval"


def _summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "n_questions": n,
        "scores": {m: round(sum(r["scores"][m] for r in rows) / n, 4) for m in METRIC_NAMES},
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / n, 1),
    }


def _save_results(rows: list[dict], summary: dict) -> Path:
    """Writes a per-row CSV and a summary JSON, timestamped, to results/."""
    ts = time.strftime("%Y%m%d_%H%M")
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / f"ragas_eval_{ts}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "reference", "latency_ms", *METRIC_NAMES])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "question": row["question"], "answer": row["answer"],
                "reference": row["reference"], "latency_ms": row["latency_ms"],
                **row["scores"],
            })

    (out_dir / f"ragas_summary_{ts}.json").write_text(json.dumps({**summary, "timestamp": ts}, indent=2))
    return out_dir


async def main():
    limiter = RateLimiter(max_calls=GEMINI_FREE_TIER_RPM * len(config.GEMINI_GENERATION_API_KEYS))
    judge_llm, judge_embeddings = build_judge(limiter)
    score_fn = partial(score_row, judge_llm=judge_llm, judge_embeddings=judge_embeddings)

    print(f"Running {len(TEST_QUESTIONS)} questions against the production pipeline...")
    rows = await run_scored_evaluation(CHECKPOINT_KEY, TEST_QUESTIONS, build_retriever(), limiter, score_fn)

    if not rows:
        print("No rows produced contexts — aborting.")
        return

    summary = _summarize(rows)
    out_dir = _save_results(rows, summary)

    print("\n=== RESULTS ===")
    for name, value in summary["scores"].items():
        print(f"  {name:<20} {value}")
    print(f"  {'mean_latency_ms':<20} {summary['mean_latency_ms']}")
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())