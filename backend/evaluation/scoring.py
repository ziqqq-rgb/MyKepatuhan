"""
Scores RAG pipeline outputs with Ragas' collections metrics.

Updated to respect Gemini's Free Tier rate limits (15 RPM) by 
evaluating sequentially and introducing deliberate pacing.
"""
import asyncio
from ragas.metrics.collections import AnswerCorrectness, AnswerRelevancy, Faithfulness

async def score_rows(rows: list[dict], judge_llm, judge_embeddings) -> list[dict]:
    """Returns each row enriched with a `scores` dict of metric -> float."""
    faithfulness = Faithfulness(llm=judge_llm)
    answer_relevancy = AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings)
    answer_correctness = AnswerCorrectness(llm=judge_llm, embeddings=judge_embeddings)

    scored_rows = []
    
    for i, row in enumerate(rows):
        print(f"  -> Scoring row {i+1}/{len(rows)}...")
        
        scores = await _score_row(row, faithfulness, answer_relevancy, answer_correctness)
        scored_rows.append({**row, "scores": scores})
        
        # Pacing: Gemini Free Tier allows 15 RPM. 
        # One row consumes ~4-6 requests. We wait 20s between rows 
        # to ensure we safely average ~3 rows per minute.
        if i < len(rows) - 1:
            print("     (Waiting 20s to respect Gemini free-tier rate limits...)")
            await asyncio.sleep(20)

    return scored_rows

async def _score_row(row: dict, faithfulness, answer_relevancy, answer_correctness) -> dict:
    """Runs the three metrics for a single row sequentially to prevent burst limit errors."""
    
    # 1. Faithfulness
    faith = await faithfulness.ascore(
        user_input=row["question"],
        response=row["answer"],
        retrieved_contexts=row["contexts"],
    )
    await asyncio.sleep(2) # Small buffer between metrics
    
    # 2. Answer Relevancy
    relevancy = await answer_relevancy.ascore(
        user_input=row["question"],
        response=row["answer"],
    )
    await asyncio.sleep(2) # Small buffer between metrics
    
    # 3. Answer Correctness
    correctness = await answer_correctness.ascore(
        user_input=row["question"],
        response=row["answer"],
        reference=row["reference"],
    )
    
    return {
        "faithfulness": faith.value,
        "answer_relevancy": relevancy.value,
        "answer_correctness": correctness.value,
    }