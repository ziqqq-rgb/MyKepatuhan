from typing import Awaitable, Callable

from tests.rag_evaluation import checkpoint
from tests.rag_evaluation.pipeline_runner import run_single_question
from tests.rag_evaluation.rate_limiter import RateLimiter

ScoreFn = Callable[[dict], Awaitable[dict]]


async def run_scored_evaluation(
    checkpoint_key: str,
    questions: list[dict],
    retriever,
    limiter: RateLimiter,
    score_fn: ScoreFn,
) -> list[dict]:
    scored = checkpoint.load_scored_rows(checkpoint_key)
    done = checkpoint.already_scored_questions(checkpoint_key)
    pending = [q for q in questions if q["question"] not in done]

    if not pending:
        print(f"  [{checkpoint_key}] all {len(questions)} questions already done.")
        return scored

    print(f"  [{checkpoint_key}] resuming: {len(scored)} done, {len(pending)} remaining.")

    for i, item in enumerate(pending):
        print(f"  -> [{checkpoint_key}] {i + 1}/{len(pending)}: {item['question'][:60]}")
        row = await run_single_question(retriever, item, limiter)
        if row is None:
            print("     [SKIP] no contexts retrieved")
            continue

        row["scores"] = await score_fn(row)
        scored.append(row)
        checkpoint.save_scored_rows(checkpoint_key, scored)

    return scored