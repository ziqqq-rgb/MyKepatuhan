"""
RAG evaluation entry point.

Wires together pipeline_runner -> judge -> scoring, then reports and
saves results. All the actual logic lives in those three modules.

Install:
    pip install ragas google-genai

Run (from evaluation/):
    python eval_ragas.py
"""
import asyncio
import csv
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(message)s")

from pipeline.retriever import build_query_engine
from backend.test.evaluation.questions import TEST_QUESTIONS
from backend.test.evaluation.judge import build_judge
from backend.test.evaluation.pipeline_runner import run_questions
from backend.test.evaluation.scoring import score_rows

METRIC_NAMES = ["faithfulness", "answer_relevancy", "answer_correctness"]


def summarize(scored_rows: list[dict]) -> dict:
    """Averages each metric across all rows, plus mean latency."""
    n = len(scored_rows)
    return {
        "n_questions": n,
        "scores": {
            name: round(sum(r["scores"][name] for r in scored_rows) / n, 4)
            for name in METRIC_NAMES
        },
        "mean_latency_ms": round(sum(r["latency_ms"] for r in scored_rows) / n, 1),
    }


def save_results(scored_rows: list[dict], summary: dict) -> Path:
    """Writes per-row CSV and a summary JSON, timestamped, to results/."""
    ts = time.strftime("%Y%m%d_%H%M")
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    csv_path = out_dir / f"ragas_eval_{ts}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "reference", "latency_ms", *METRIC_NAMES])
        writer.writeheader()
        for row in scored_rows:
            writer.writerow({
                "question": row["question"],
                "answer": row["answer"],
                "reference": row["reference"],
                "latency_ms": row["latency_ms"],
                **row["scores"],
            })

    summary_path = out_dir / f"ragas_summary_{ts}.json"
    summary_path.write_text(json.dumps({**summary, "timestamp": ts}, indent=2))

    return out_dir


def main():
    print("Loading RAG pipeline...")
    query_engine = build_query_engine()

    print(f"Running {len(TEST_QUESTIONS)} questions...")
    rows = run_questions(query_engine, TEST_QUESTIONS)
    if not rows:
        print("No rows produced contexts — aborting.")
        return

    print("Scoring with Ragas...")
    judge_llm, judge_embeddings = build_judge()
    scored_rows = asyncio.run(score_rows(rows, judge_llm, judge_embeddings))

    summary = summarize(scored_rows)
    out_dir = save_results(scored_rows, summary)

    print("\n=== RESULTS ===")
    for name, value in summary["scores"].items():
        print(f"  {name:<20} {value}")
    print(f"  {'mean_latency_ms':<20} {summary['mean_latency_ms']}")
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()