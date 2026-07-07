from llama_index.core import VectorStoreIndex, Settings, get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.schema import QueryBundle, NodeWithScore
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
# from llama_index.llms.google_genai import GoogleGenAI  # swapped for Groq
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
# from google.genai import types  # only needed for the old GoogleGenAI generation_config

from core import config
from pipeline.prompts import QA_PROMPT_TEMPLATE, LANGUAGE_LABELS
from services.key_rotation import RoundRobinPool
from core.clients import get_pinecone_index, get_reranker
from core.embeddings import get_query_embed_model

embed_model = get_query_embed_model()
Settings.embed_model = embed_model


# def _build_llm(api_key: str) -> GoogleGenAI:
#     return GoogleGenAI(
#         api_key=api_key,
#         model=config.GEMINI_GENERATION_MODEL,
#         temperature=config.GEMINI_GENERATION_TEMPERATURE,
#         generation_config=types.GenerateContentConfig(
#             automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
#         ),
#     )


def _build_llm(api_key: str) -> Groq:
    return Groq(
        api_key=api_key,
        model=config.GROQ_GENERATION_MODEL,
        temperature=config.GROQ_GENERATION_TEMPERATURE,
    )


# One client per Groq project key, built once at import — rotating
# pre-built clients avoids the construction cost on every request.
_llm_pool = RoundRobinPool([_build_llm(key) for key in config.GROQ_GENERATION_API_KEYS])

# LlamaIndex internals that read Settings.llm directly need a default;
# actual per-request rotation happens via get_next_llm().
Settings.llm = _llm_pool.items[0]

reranker = get_reranker()

# PINECONE + INDEX
pinecone_index = get_pinecone_index()

vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    #add_sparse_vector=True,
)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)


def get_next_llm() -> Groq:
    """Rotates round-robin across Groq generation keys so no single
    project's RPM/RPD quota takes all the traffic."""
    return _llm_pool.next()


def llm_pool_size() -> int:
    return len(_llm_pool)


def build_retriever(authority: str = None, topic: str = None):
    """Builds a dense-only Pinecone retriever, optionally filtered by metadata."""
    filters = []

    if authority:
        filters.append(MetadataFilter(key="authority", value=authority, operator=FilterOperator.EQ))
    if topic:
        filters.append(MetadataFilter(key="topic", value=topic, operator=FilterOperator.EQ))

    metadata_filters = MetadataFilters(filters=filters) if filters else None

    return index.as_retriever(
        vector_store_query_mode="default",   # pure dense — hybrid is non-functional on this index
        similarity_top_k=config.RETRIEVAL_TOP_K,
        filters=metadata_filters,
    )


def rerank_nodes(nodes: list[NodeWithScore], question: str) -> list[NodeWithScore]:
    """Reranks retrieved nodes with the shared SBERT cross-encoder, trimming to RERANK_TOP_N."""
    return reranker.postprocess_nodes(nodes, query_bundle=QueryBundle(query_str=question))


def build_response_synthesizer(
    llm: Groq = None,
    history: str = "",
    target_language: str = "en",
    streaming: bool = False,
):
    """
    Generates an answer from nodes it's given — never retrieves on its own,
    so the live query path can reuse already-retrieved, already-reranked
    nodes instead of hitting Pinecone twice.

    `llm` defaults to the next rotated client if not passed explicitly.
    `streaming=True` returns a response whose `.response_gen` yields tokens
    incrementally, instead of blocking until the full answer is ready.
    """
    language_label = LANGUAGE_LABELS.get(target_language, "English")
    prompt = QA_PROMPT_TEMPLATE.partial_format(history=history, target_language=language_label)
    return get_response_synthesizer(llm=llm or get_next_llm(), text_qa_template=prompt, streaming=streaming)


def build_query_engine(
    authority: str = None,
    topic: str = None,
    history: str = "",
    target_language: str = "en",
    retriever=None,  
):
    if retriever is None:
        retriever = build_retriever(authority=authority, topic=topic)
    language_label = LANGUAGE_LABELS.get(target_language, "English")
    prompt = QA_PROMPT_TEMPLATE.partial_format(history=history, target_language=language_label)

    return RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker],
        llm=get_next_llm(),
        text_qa_template=prompt,
    )

def print_citations(response) -> None:
    print("\n--- CITATIONS ---")
    for i, node in enumerate(response.source_nodes):
        meta = node.node.metadata
        print(
            f"[{i+1}] "
            f"Authority: {meta.get('authority', 'Unknown')} | "
            f"Topic: {meta.get('topic', 'Unknown')} | "
            f"Type: {meta.get('document_type', 'Unknown')} | "
            f"Score: {node.score:.4f}"
        )