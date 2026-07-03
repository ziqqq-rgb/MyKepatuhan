"""
Compares dense / sparse / hybrid retrieval on the same golden question set.
Run: python compare_retrievers.py
"""
import asyncio
import json
import time
from pathlib import Path

from pipeline.retriever import build_query_engine
from tests.rag_evaluation.questions import TEST_QUESTIONS
from tests.rag_evaluation.retrievers import RETRIEVAL_STRATEGIES
from tests.rag_evaluation.pipeline_runner import run_questions
from tests.rag_evaluation.judge import build_judge
from tests.rag_evaluation.retrieval_scoring import score_retrieval_rows


def _summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "context_precision": round(sum(r["scores"]["context_precision"] for r in rows) / n, 4),
        "context_recall": round(sum(r["scores"]["context_recall"] for r in rows) / n, 4),
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / n, 1),
    }


def main():
    judge_llm, _ = build_judge()  # embeddings unused for these two metrics
    summary = {}

    for name, build_retriever_fn in RETRIEVAL_STRATEGIES.items():
        print(f"\n=== Strategy: {name} ===")
        query_engine = build_query_engine(retriever=build_retriever_fn())
        rows = run_questions(query_engine, TEST_QUESTIONS)
        if not rows:
            print(f"  [SKIP] '{name}' returned no contexts for any question.")
            continue
        scored = asyncio.run(score_retrieval_rows(rows, judge_llm))
        summary[name] = _summarize(scored)

    print("\n=== RETRIEVAL STRATEGY COMPARISON ===")
    for name, s in summary.items():
        print(f"  {name:<8} precision={s['context_precision']}  recall={s['context_recall']}  latency={s['mean_latency_ms']}ms")

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M")
    (out_dir / f"retrieval_comparison_{ts}.json").write_text(json.dumps(summary, indent=2))
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()