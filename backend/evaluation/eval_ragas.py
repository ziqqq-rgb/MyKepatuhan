"""
RAG evaluation using Ragas.

Replaces the old notebook (manual async loops over LlamaIndex's
FaithfulnessEvaluator / RelevancyEvaluator / CorrectnessEvaluator, judged
by a local Ollama model unrelated to the actual generation LLM).

Ragas does the same job in one call: build a dataset of
question/answer/contexts/reference, hand it to evaluate(), get scores back.
The judge here is the SAME Gemini model used in production (retriever.py),
so scores reflect how the real pipeline behaves — no separate local judge
model to install or keep in sync.

Install:
    pip install ragas langchain-google-genai langchain-ollama datasets

Run (from evaluation/):
    python eval_ragas.py
"""
import json
import sys
import time
from pathlib import Path

# Fix path to backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import Dataset
from ragas import evaluate

from ragas.metrics.collections import Faithfulness, AnswerRelevancy, AnswerCorrectness
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings

from core import config
from pipeline.retriever import build_query_engine
from questions import TEST_QUESTIONS


def run_queries(query_engine) -> list[dict]:
    """Run every test question through the real RAG pipeline."""
    rows = []
    for item in TEST_QUESTIONS:
        t0 = time.perf_counter()
        response = query_engine.query(item["question"])
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        contexts = [n.node.text for n in response.source_nodes if n.node.text.strip()]
        if not contexts:
            print(f"  [SKIP] no contexts: {item['question'][:60]}")
            continue

        rows.append({
            "question": item["question"],
            "answer": str(response.response),
            "contexts": contexts,
            "reference": item["reference"],
            "latency_ms": latency_ms,
        })
        print(f"  [OK] {latency_ms:>7.0f}ms  {item['question'][:60]}")
    return rows


def main():
    print("Loading RAG pipeline...")
    query_engine = build_query_engine()

    print(f"Running {len(TEST_QUESTIONS)} questions...")
    rows = run_queries(query_engine)
    if not rows:
        print("No rows produced contexts — aborting.")
        return

    dataset = Dataset.from_list([
        {k: r[k] for k in ("question", "answer", "contexts", "reference")}
        for r in rows
    ])

    # 1. Judge LLM = same Gemini model the pipeline uses for generation.
    judge_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(
        model=config.GEMINI_GENERATION_MODEL,
        google_api_key=config.GEMINI_GENERATION_API_KEY,
        temperature=0,
    ))

    # Judge embeddings = same embedding model the pipeline uses for retrieval.
    judge_embeddings = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(model=config.EMBED_MODEL_NAME)
    )

    # 2. Instantiate metrics with llm/embeddings injected directly — the
    # `collections` API requires this at construction time, not at evaluate().
    metrics_list = [
        Faithfulness(llm=judge_llm),
        AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings),
        AnswerCorrectness(llm=judge_llm, embeddings=judge_embeddings),
    ]

    print("Scoring with Ragas...")
    results = evaluate(
        dataset,
        metrics=metrics_list,
    )

    df = results.to_pandas()
    ts = time.strftime("%Y%m%d_%H%M")
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / f"ragas_eval_{ts}.csv", index=False)

    score_cols = [m.name for m in metrics_list]
    summary = {
        "timestamp": ts,
        "n_questions": len(df),
        "scores": {c: round(float(df[c].mean()), 4) for c in score_cols if c in df.columns},
        "mean_latency_ms": round(sum(r["latency_ms"] for r in rows) / len(rows), 1),
    }
    (out_dir / f"ragas_summary_{ts}.json").write_text(json.dumps(summary, indent=2))

    print("\n=== RESULTS ===")
    for k, v in summary["scores"].items():
        print(f"  {k:<20} {v}")
    print(f"  {'mean_latency_ms':<20} {summary['mean_latency_ms']}")
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()