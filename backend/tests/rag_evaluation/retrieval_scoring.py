"""
Lean scorer for retrieval-strategy comparison: Context Precision + Context
Recall only (both need just the judge LLM, no embeddings).

Checkpointed per row via checkpoint.py — a quota failure mid-run loses at
most one row, not the whole strategy.
"""
import asyncio
from ragas.metrics.collections import ContextPrecision, ContextRecall

from tests.rag_evaluation import checkpoint


async def score_retrieval_rows(rows: list[dict], judge_llm, strategy: str) -> list[dict]:
    scored = checkpoint.load_scored_rows(strategy)
    done = checkpoint.already_scored_questions(strategy)
    pending = [row for row in rows if row["question"] not in done]

    if not pending:
        print(f"  [{strategy}] all {len(rows)} rows already scored — using checkpoint.")
        return scored

    print(f"  [{strategy}] resuming: {len(scored)} done, {len(pending)} remaining.")
    precision = ContextPrecision(llm=judge_llm)
    recall = ContextRecall(llm=judge_llm)

    for i, row in enumerate(pending):
        print(f"  -> Scoring row {i + 1}/{len(pending)}...")

        p = await precision.ascore(
            user_input=row["question"], reference=row["reference"], retrieved_contexts=row["contexts"]
        )
        await asyncio.sleep(2)
        r = await recall.ascore(
            user_input=row["question"], retrieved_contexts=row["contexts"], reference=row["reference"]
        )

        scored.append({**row, "scores": {"context_precision": p.value, "context_recall": r.value}})
        checkpoint.save_scored_rows(strategy, scored)  # persist immediately, not at the end

        if i < len(pending) - 1:
            await asyncio.sleep(15)

    return scored