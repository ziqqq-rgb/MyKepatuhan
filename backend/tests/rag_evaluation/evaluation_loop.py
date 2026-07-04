"""
Shared run-score-checkpoint loop. compare_retrievers.py (retrieval metrics)
and eval_ragas.py (full generation metrics) need the identical shape: run
each question, score it, save immediately, skip what's already checkpointed.
The only difference between them is which scorer runs — passed in as `score_fn`.
"""
from typing import Awaitable, Callable

from tests.rag_evaluation import checkpoint
from tests.rag_evaluation.pipeline_runner import run_single_question
from tests.rag_evaluation.rate_limiter import RateLimiter

ScoreFn = Callable[[dict], Awaitable[dict]]


async def run_scored_evaluation(
    checkpoint_key: str,
    questions: list[dict],
    query_engine,
    limiter: RateLimiter,
    score_fn: ScoreFn,
) -> list[dict]:
    """Resumable: safe to re-run after a crash or quota error."""
    scored = checkpoint.load_scored_rows(checkpoint_key)
    done = checkpoint.already_scored_questions(checkpoint_key)
    pending = [q for q in questions if q["question"] not in done]

    if not pending:
        print(f"  [{checkpoint_key}] all {len(questions)} questions already done.")
        return scored

    print(f"  [{checkpoint_key}] resuming: {len(scored)} done, {len(pending)} remaining.")

    for i, item in enumerate(pending):
        print(f"  -> [{checkpoint_key}] {i + 1}/{len(pending)}: {item['question'][:60]}")
        row = await run_single_question(query_engine, item, limiter)       
        if row is None:
            print("     [SKIP] no contexts retrieved")
            continue

        row["scores"] = await score_fn(row)
        scored.append(row)
        checkpoint.save_scored_rows(checkpoint_key, scored)

    return scored