"""
Runs the real RAG pipeline (retriever -> reranker -> Gemini generation)
against a fixed set of test questions, capturing what Ragas needs to
score each one: the answer, the retrieved contexts, and latency.
"""
import logging
import time

log = logging.getLogger(__name__)


def run_questions(query_engine, questions: list[dict]) -> list[dict]:
    """
    Executes every question through query_engine. Skips any question with
    no retrieved context, since Ragas can't score faithfulness without one.
    """
    rows = []
    for item in questions:
        row = _run_single(query_engine, item)
        if row is None:
            log.warning(f"[SKIP] no contexts: {item['question'][:60]}")
            continue
        rows.append(row)
        log.info(f"[OK] {row['latency_ms']:>7.0f}ms  {item['question'][:60]}")
    return rows


def _run_single(query_engine, item: dict) -> dict | None:
    """Runs one question, returns None if retrieval came back empty."""
    t0 = time.perf_counter()
    response = query_engine.query(item["question"])
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