"""
Orchestrates one query through the RAG pipeline: retrieve -> rerank -> generate.

Split into two functions (retrieve_and_rerank, generate_answer) instead of
one query engine so the same nodes can be reused for both generation and
citations, without retrieving from Pinecone a second time.
"""
# from google.genai.errors import ClientError  # swapped for Groq
from openai import RateLimitError
from llama_index.core.schema import NodeWithScore

from pipeline.retriever import (
    build_retriever, rerank_nodes, build_response_synthesizer,
    get_next_llm, llm_pool_size,
)
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
    """
    Synthesizes an answer from nodes already retrieved by the caller.
    Never re-retrieves — pass the output of retrieve_and_rerank() here.

    Tries each Groq key once, round-robin: on a 429, move to the next
    key immediately instead of sleeping, since spare quota is likely
    sitting idle on the others. Only the final key in the pass gets
    call_with_backoff's full exponential retry, as a last resort if
    every key is exhausted.
    """
    pool_size = llm_pool_size()
    for key_attempt in range(pool_size):
        is_last_key = key_attempt == pool_size - 1
        llm = get_next_llm()
        synthesizer = build_response_synthesizer(llm, history=history, target_language=target_language)
        try:
            max_retries = 3 if is_last_key else 1
            response = call_with_backoff(
                synthesizer.synthesize, question, nodes=nodes, max_retries=max_retries
            )
            return str(response)
        except RateLimitError:
            if not is_last_key:
                continue
            raise

def generate_answer_stream(question: str, nodes: list[NodeWithScore], history: str, target_language: str):
    """
    Same inputs as generate_answer(), but yields the answer token-by-token
    instead of returning it in one block.

    Trade-off vs generate_answer(): no key-rotation retry *within* a single
    request. Once the first token has reached the client, switching keys
    and restarting would mean re-sending an answer from scratch — worse UX
    than occasionally letting one attempt fail. Rotation still happens
    *across* requests via get_next_llm().
    """
    llm = get_next_llm()
    synthesizer = build_response_synthesizer(llm, history=history, target_language=target_language, streaming=True)
    response = synthesizer.synthesize(question, nodes=nodes)
    yield from response.response_gen