import os
from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.google_genai import GoogleGenAI          
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank


# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

PINECONE_API_KEY  = os.getenv("PINECON_KEY")
GEMINI_API_KEY    = os.getenv("GEMINI_KEY")

# How many candidates to retrieve before reranking
RETRIEVAL_TOP_K = 15

# How many results to keep after reranking
RERANK_TOP_N = 3

# Hybrid alpha: 0.0 = pure BM25 (keyword), 1.0 = pure dense (semantic)
# 0.6 = lean semantic but still respect exact legal terms
HYBRID_ALPHA = 0.6


# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

embed_model = OllamaEmbedding(
    model_name="nomic-embed-text-v2-moe",
    embed_batch_size=50,
    query_instruction="search_query: ",
    text_instruction="search_document: ",
)
Settings.embed_model = embed_model


llm = GoogleGenAI(
    api_key=GEMINI_API_KEY,
    model="gemini-3.1-flash-lite",
    temperature=0.0,
)
Settings.llm = llm


reranker = SentenceTransformerRerank(
    model="BAAI/bge-reranker-v2-m3",
    top_n=RERANK_TOP_N,
)


# ─────────────────────────────────────────
# PINECONE + INDEX
# ─────────────────────────────────────────

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("mykepatuhan")

vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    add_sparse_vector=True,   
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
        vector_store_query_mode="hybrid",   
        similarity_top_k=RETRIEVAL_TOP_K,
        alpha=HYBRID_ALPHA,
        filters=metadata_filters,
    )

    return retriever

def build_query_engine(authority: str = None, topic: str = None):
    """
    Build the full query engine: hybrid retriever → SBERT reranker → Gemini.
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

