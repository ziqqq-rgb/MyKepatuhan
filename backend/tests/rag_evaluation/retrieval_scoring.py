"""Scores one row's retrieval quality: Context Precision + Context Recall."""
from ragas.metrics.collections import ContextPrecision, ContextRecall


async def score_retrieval_row(row: dict, judge_llm) -> dict:
    precision = await ContextPrecision(llm=judge_llm).ascore(
        user_input=row["question"], reference=row["reference"], retrieved_contexts=row["contexts"]
    )
    recall = await ContextRecall(llm=judge_llm).ascore(
        user_input=row["question"], retrieved_contexts=row["contexts"], reference=row["reference"]
    )
    return {"context_precision": precision.value, "context_recall": recall.value}