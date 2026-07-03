"""
Eval-only retriever variants for comparing sparse (BM25) vs dense (Pinecone)
vs hybrid retrieval quality.

BM25 needs node text, which Pinecone doesn't return in bulk, so the sparse
index is built locally from the same '*__nodes_enriched.pkl' checkpoints the
ingestion pipeline already produces — no new infrastructure required.
"""
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever

from core import config
from pipeline.retriever import build_retriever
from pipeline.ingestion.checkpointing import CHECKPOINT_DIR


def _load_all_enriched_nodes() -> list:
    """Loads every enriched-node checkpoint written during ingestion."""
    nodes = []
    for path in CHECKPOINT_DIR.glob("*__nodes_enriched.pkl"):
        import pickle
        with open(path, "rb") as f:
            nodes.extend(pickle.load(f))
    if not nodes:
        raise RuntimeError(
            "No ingestion checkpoints found — ingest at least one document "
            "before comparing retrieval strategies."
        )
    return nodes


def build_sparse_retriever(top_k: int = config.RETRIEVAL_TOP_K) -> BM25Retriever:
    """BM25 retriever built from local ingestion checkpoints (no Pinecone)."""
    docstore = SimpleDocumentStore()
    docstore.add_documents(_load_all_enriched_nodes())
    return BM25Retriever.from_defaults(docstore=docstore, similarity_top_k=top_k)


def build_hybrid_retriever(top_k: int = config.RETRIEVAL_TOP_K) -> QueryFusionRetriever:
    """
    Combines the production Pinecone dense retriever with local BM25 via
    reciprocal-rank fusion. num_queries=1 disables LLM query expansion, so
    this stays a pure retrieval-strategy comparison, not a query-rewriting one.
    """
    return QueryFusionRetriever(
        [build_retriever(), build_sparse_retriever(top_k)],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
    )


# name -> zero-arg factory, so compare_retrievers.py can loop over this
RETRIEVAL_STRATEGIES = {
    "dense": build_retriever,
    "sparse": build_sparse_retriever,
    "hybrid": build_hybrid_retriever,
}