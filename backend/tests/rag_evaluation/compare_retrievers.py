"""
Compares dense / sparse / hybrid retrieval. Every Gemini call shares one
RateLimiter, so pacing is correct no matter which retriever is fastest.
Resumable via checkpoint.py.

Run: python compare_retrievers.py
"""
import asyncio
import json
import time
from functools import partial
from pathlib import Path

from pipeline.retriever import build_query_engine
from tests.rag_evaluation.golden_dataset import TEST_QUESTIONS
from tests.rag_evaluation.retrievers import RETRIEVAL_STRATEGIES
from tests.rag_evaluation.retrieval_scoring import score_retrieval_row
from tests.rag_evaluation.evaluation_loop import run_scored_evaluation
from tests.rag_evaluation.judge import build_judge
from tests.rag_evaluation.rate_limiter import RateLimiter

GEMINI_FREE_TIER_RPM = 15


def _summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "context_precision": round(sum(r["scores"]["context_precision"] for r in rows) / n, 4),
        "context_recall": round(sum(r["scores"]["context_recall"] for r in rows) / n, 4),
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / n, 1),
    }


async def main():
    limiter = RateLimiter(max_calls=GEMINI_FREE_TIER_RPM)
    judge_llm, _ = build_judge(limiter)
    summary = {}

    for name, build_retriever_fn in RETRIEVAL_STRATEGIES.items():
        print(f"\n=== Strategy: {name} ===")
        try:
            query_engine = build_query_engine(retriever=build_retriever_fn())
            score_fn = partial(score_retrieval_row, judge_llm=judge_llm)
            rows = await run_scored_evaluation(name, TEST_QUESTIONS, query_engine, limiter, score_fn)
        except Exception as e:
            print(f"  [STOPPED] '{name}' failed: {e}")
            print("  Progress is saved. Re-run this script later to resume.")
            return

        if rows:
            summary[name] = _summarize(rows)

    print("\n=== RETRIEVAL STRATEGY COMPARISON ===")
    for name, s in summary.items():
        print(f"  {name:<8} precision={s['context_precision']}  recall={s['context_recall']}  latency={s['mean_latency_ms']}ms")

    if summary:
        out_dir = Path(__file__).parent / "results"
        out_dir.mkdir(exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M")
        (out_dir / f"retrieval_comparison_{ts}.json").write_text(json.dumps(summary, indent=2))
        print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())