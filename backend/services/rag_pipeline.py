"""
Orchestrates one query through the RAG pipeline: retrieve -> rerank -> generate.

Split into two functions (retrieve_and_rerank, generate_answer) instead of
one query engine so the same nodes can be reused for both generation and
citations, without retrieving from Pinecone a second time.
"""
from llama_index.core.schema import NodeWithScore

from pipeline.retriever import build_retriever, rerank_nodes, build_response_synthesizer
from services.llm_backoff import call_with_backoff

_default_retriever = None

def _get_retriever(authority: str | None, topic: str | None):
    global _default_retriever
    if authority or topic:
        return build_retriever(authority=authority, topic=topic)
    if _default_retriever is None:
        _default_retriever = build_retriever()
    return _default_retriever


def warm_up() -> None:
    """Pre-builds the default retriever at startup so the first real
    request doesn't pay that construction cost."""
    _get_retriever(authority=None, topic=None)


def retrieve_and_rerank(
    question: str, authority: str | None, topic: str | None
) -> list[NodeWithScore]:
    """Retrieves candidate nodes, then reranks them. Returns the final,
    trimmed node list — used for both generation context and citations."""
    retriever = _get_retriever(authority, topic)
    candidates = retriever.retrieve(question)
    if not candidates:
        return []
    return rerank_nodes(candidates, question)


def generate_answer(
    question: str, nodes: list[NodeWithScore], history: str, target_language: str
) -> str:
    """Synthesizes an answer from nodes already retrieved by the caller.
    Never re-retrieves — pass the output of retrieve_and_rerank() here."""
    synthesizer = build_response_synthesizer(history=history, target_language=target_language)
    response = call_with_backoff(synthesizer.synthesize, question, nodes=nodes)
    return str(response)