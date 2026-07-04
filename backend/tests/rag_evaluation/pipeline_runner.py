"""Runs one question through the RAG pipeline: retrieve -> rerank -> generate."""
import time
from tests.rag_evaluation.rate_limiter import RateLimiter


async def run_single_question(query_engine, item: dict, limiter: RateLimiter) -> dict | None:
    """Returns None if retrieval came back empty — Ragas can't score
    faithfulness without context."""
    await limiter.wait_if_needed()  # generation is one Gemini call

    t0 = time.perf_counter()
    response = await query_engine.aquery(item["question"])  # async: avoids nested event loop
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    contexts = [n.node.text for n in response.source_nodes if n.node.text.strip()]
    if not contexts:
        return None

    return {
        "question": item["question"],
        "answer": str(response.response),
        "contexts": contexts,
        "reference": item["reference"],
        "latency_ms": latency_ms,
    }