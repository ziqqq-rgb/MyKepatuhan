"""Scores one row's generation quality: Faithfulness, Answer Relevancy, Answer Correctness."""
from ragas.metrics.collections import AnswerCorrectness, AnswerRelevancy, Faithfulness


async def score_row(row: dict, judge_llm, judge_embeddings) -> dict:
    faithfulness = await Faithfulness(llm=judge_llm).ascore(
        user_input=row["question"], response=row["answer"], retrieved_contexts=row["contexts"]
    )
    relevancy = await AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings).ascore(
        user_input=row["question"], response=row["answer"]
    )
    correctness = await AnswerCorrectness(llm=judge_llm, embeddings=judge_embeddings).ascore(
        user_input=row["question"], response=row["answer"], reference=row["reference"]
    )
    return {
        "faithfulness": faithfulness.value,
        "answer_relevancy": relevancy.value,
        "answer_correctness": correctness.value,
    }