from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.vector_stores.pinecone import PineconeVectorStore
from google.genai import types

from core import config
from core.clients import get_embed_model, get_pinecone_index


# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

embed_model = get_embed_model()
Settings.embed_model = embed_model

llm = GoogleGenAI(
    api_key=config.GEMINI_GENERATION_API_KEY,
    model=config.GEMINI_GENERATION_MODEL,
    temperature=config.GEMINI_GENERATION_TEMPERATURE,
    generation_config=types.GenerateContentConfig(
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    ),
)
Settings.llm = llm

reranker = SentenceTransformerRerank(
    model=config.RERANKER_MODEL,
    top_n=config.RERANK_TOP_N,
)


# ─────────────────────────────────────────
# PINECONE + INDEX
# ─────────────────────────────────────────

pinecone_index = get_pinecone_index()

vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    #add_sparse_vector=True,
)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)


def build_retriever(authority: str = None, topic: str = None):
    filters = []

    if authority:
        filters.append(MetadataFilter(
            key="authority",
            value=authority,
            operator=FilterOperator.EQ,
        ))

    if topic:
        filters.append(MetadataFilter(
            key="topic",
            value=topic,
            operator=FilterOperator.EQ,
        ))

    metadata_filters = MetadataFilters(filters=filters) if filters else None

    retriever = index.as_retriever(
        vector_store_query_mode="default",   # pure dense — hybrid is non-functional on this index
        similarity_top_k=config.RETRIEVAL_TOP_K,
        filters=metadata_filters,
    )
    return retriever


def build_query_engine(authority: str = None, topic: str = None):
    """
    Build the full query engine: retriever → SBERT reranker → Gemini.
    """
    retriever = build_retriever(authority=authority, topic=topic)

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker],
        llm=llm,
    )
    return query_engine


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