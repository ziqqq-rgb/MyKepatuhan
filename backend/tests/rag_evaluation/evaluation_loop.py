"""
Shared scored-evaluation loop for both eval_ragas.py (generation quality)
and compare_retrievers.py (retrieval quality). Resumes from checkpoint,
and isolates per-row judge failures so one bad row can't take down the
whole run.
"""
import logging
from typing import Awaitable, Callable

from tests.rag_evaluation import checkpoint
from tests.rag_evaluation.pipeline_runner import run_single_question
from tests.rag_evaluation.rate_limiter import RateLimiter

log = logging.getLogger(__name__)

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
    skipped_count = 0

    for i, item in enumerate(pending):
        print(f"  -> [{checkpoint_key}] {i + 1}/{len(pending)}: {item['question'][:60]}")
        row = await run_single_question(retriever, item, limiter)
        if row is None:
            print("     [SKIP] no contexts retrieved")
            continue

        try:
            row["scores"] = await score_fn(row)
        except Exception as e:
            # A judge call failing (truncated structured output, transient
            # API error, etc.) shouldn't kill the whole run. The row is
            # never marked "done" in the checkpoint, so it's automatically
            # retried the next time this script runs.
            log.warning(f"  [{checkpoint_key}] SKIP (scoring failed) — {item['question'][:60]}: {e}")
            skipped_count += 1
            continue

        scored.append(row)
        checkpoint.save_scored_rows(checkpoint_key, scored)

    if skipped_count:
        print(f"  [{checkpoint_key}] {skipped_count} row(s) skipped due to scoring errors — re-run to retry them.")

    return scored