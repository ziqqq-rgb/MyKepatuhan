"""
Full RAG evaluation: Faithfulness, Answer Relevancy, Answer Correctness on
the production (dense) retriever. Resumable via checkpoint.py.

Run: python eval_ragas.py
"""
import asyncio
import csv
import json
import time
from functools import partial
from pathlib import Path

from pipeline.retriever import build_query_engine
from tests.rag_evaluation.golden_dataset import TEST_QUESTIONS
from tests.rag_evaluation.scoring import score_row
from tests.rag_evaluation.evaluation_loop import run_scored_evaluation
from tests.rag_evaluation.judge import build_judge
from tests.rag_evaluation.rate_limiter import RateLimiter

GEMINI_FREE_TIER_RPM = 15
METRIC_NAMES = ["faithfulness", "answer_relevancy", "answer_correctness"]
CHECKPOINT_KEY = "full_eval"


def _summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "n_questions": n,
        "scores": {name: round(sum(r["scores"][name] for r in rows) / n, 4) for name in METRIC_NAMES},
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / n, 1),
    }


def _save_results(rows: list[dict], summary: dict) -> Path:
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
    limiter = RateLimiter(max_calls=GEMINI_FREE_TIER_RPM)
    judge_llm, judge_embeddings = build_judge(limiter)
    query_engine = build_query_engine()  # production dense retriever
    score_fn = partial(score_row, judge_llm=judge_llm, judge_embeddings=judge_embeddings)

    rows = await run_scored_evaluation(CHECKPOINT_KEY, TEST_QUESTIONS, query_engine, limiter, score_fn)
    if not rows:
        print("No rows scored — aborting.")
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