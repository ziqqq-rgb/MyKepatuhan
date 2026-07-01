"""
Scores RAG pipeline outputs with Ragas' collections metrics.

Collections metrics (Faithfulness, AnswerRelevancy, AnswerCorrectness)
are scored per-row via `.ascore()`, not through `ragas.evaluate()` --
that function only accepts the older `Metric` base class. Scoring the
three metrics for a row concurrently keeps wall-clock time down since
they're independent Gemini calls.
"""
import asyncio

from ragas.metrics.collections import AnswerCorrectness, AnswerRelevancy, Faithfulness


async def score_rows(rows: list[dict], judge_llm, judge_embeddings) -> list[dict]:
    """Returns each row enriched with a `scores` dict of metric -> float."""
    faithfulness = Faithfulness(llm=judge_llm)
    answer_relevancy = AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings)
    answer_correctness = AnswerCorrectness(llm=judge_llm, embeddings=judge_embeddings)

    return [
        {**row, "scores": await _score_row(row, faithfulness, answer_relevancy, answer_correctness)}
        for row in rows
    ]


async def _score_row(row: dict, faithfulness, answer_relevancy, answer_correctness) -> dict:
    """Runs the three metrics for a single row concurrently."""
    faith, relevancy, correctness = await asyncio.gather(
        faithfulness.ascore(
            user_input=row["question"],
            response=row["answer"],
            retrieved_contexts=row["contexts"],
        ),
        answer_relevancy.ascore(
            user_input=row["question"],
            response=row["answer"],
        ),
        answer_correctness.ascore(
            user_input=row["question"],
            response=row["answer"],
            reference=row["reference"],
        ),
    )
    return {
        "faithfulness": faith.value,
        "answer_relevancy": relevancy.value,
        "answer_correctness": correctness.value,
    }