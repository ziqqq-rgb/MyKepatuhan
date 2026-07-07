import time

from pipeline.retriever import build_query_engine
from tests.rag_evaluation.rate_limiter import RateLimiter


async def run_single_question(retriever, item: dict, limiter: RateLimiter) -> dict | None:
    """Builds a fresh query engine per question — cheap, just reuses the
    already-built retriever/reranker/LLM-pool — so generation rotates to
    the next Gemini key every call instead of pinning the whole run to
    one key. Returns None if retrieval came back empty."""
    await limiter.wait_if_needed()

    query_engine = build_query_engine(retriever=retriever)

    t0 = time.perf_counter()
    response = await query_engine.aquery(item["question"])
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