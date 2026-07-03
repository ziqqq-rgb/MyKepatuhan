"""
Lean scorer for retrieval-strategy comparison: Context Precision + Context
Recall only. Both need just the judge LLM (no embeddings), so this is about
half the Gemini calls of the full generation-metrics suite in scoring.py —
kept separate so routine strategy comparisons don't pay for unrelated
generation metrics.
"""
import asyncio
from ragas.metrics.collections import ContextPrecision, ContextRecall


async def score_retrieval_rows(rows: list[dict], judge_llm) -> list[dict]:
    precision = ContextPrecision(llm=judge_llm)
    recall = ContextRecall(llm=judge_llm)

    scored = []
    for i, row in enumerate(rows):
        print(f"  -> Scoring row {i + 1}/{len(rows)}...")

        p = await precision.ascore(
            user_input=row["question"], reference=row["reference"], retrieved_contexts=row["contexts"]
        )
        await asyncio.sleep(2)
        r = await recall.ascore(
            user_input=row["question"], retrieved_contexts=row["contexts"], reference=row["reference"]
        )
        scored.append({**row, "scores": {"context_precision": p.value, "context_recall": r.value}})

        if i < len(rows) - 1:
            await asyncio.sleep(15)  # Gemini free-tier pacing (lighter than full suite)

    return scored