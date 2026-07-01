"""
Centralized configuration for the MyKepatuhan backend.

This module only collects existing environment variables and tuning
constants that were previously scattered across individual pipeline
files (metadata.py, retriever.py, upload.py). No values or defaults
have been changed, this is a relocation, not a behavior change.
"""
import os
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────
# Secrets / external service credentials
# ─────────────────────────────────────────

GEMINI_ENRICH_API_KEY = os.getenv("GEMINI_KEY")
GEMINI_GENERATION_API_KEY = os.getenv("GEMINI_GENERATION_KEY", GEMINI_ENRICH_API_KEY)
GEMINI_API_KEY = GEMINI_ENRICH_API_KEY
PINECONE_API_KEY = os.getenv("PINECON_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


# ─────────────────────────────────────────
# Auth
# ─────────────────────────────────────────

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ─────────────────────────────────────────
# Embedding model (shared by ingestion + retrieval)
# ─────────────────────────────────────────

EMBED_MODEL_NAME = "nomic-embed-text-v2-moe"
EMBED_BATCH_SIZE = 50
EMBED_QUERY_INSTRUCTION = "search_query: "
EMBED_TEXT_INSTRUCTION = "search_document: "

# Used only by the Docling tokenizer in parse.py (separate from the
# Ollama embedding model name above — this is the HF tokenizer source)
DOCLING_TOKENIZER_MODEL = "nomic-ai/nomic-embed-text-v1.5"
DOCLING_MAX_TOKENS = 512


# ─────────────────────────────────────────
# Pinecone
# ─────────────────────────────────────────

PINECONE_INDEX_NAME = "mykepatuhan"


# ─────────────────────────────────────────
# Gemini enrichment (metadata.py)
# ─────────────────────────────────────────

GEMINI_ENRICH_MODEL = "gemini-3.1-flash-lite"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_ENRICH_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

ENRICHMENT_CONCURRENT_REQUESTS = 5   # Flash Lite allows 15 RPM — 5 concurrent is safe headroom
ENRICHMENT_BATCH_SAVE_EVERY = 50
ENRICHMENT_CONTEXT_CHARS = 2000
ENRICHMENT_MAX_RETRIES = 3


# ─────────────────────────────────────────
# Gemini generation (retriever.py)
# ─────────────────────────────────────────

GEMINI_GENERATION_MODEL = "gemini-3.1-flash-lite"
GEMINI_GENERATION_TEMPERATURE = 0.0


# ─────────────────────────────────────────
# Retrieval / reranking (retriever.py)
# ─────────────────────────────────────────

RETRIEVAL_TOP_K = 15          # candidates retrieved before reranking
RERANK_TOP_N = 3              # results kept after reranking
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# Hybrid alpha: 0.0 = pure BM25 (keyword), 1.0 = pure dense (semantic)
# 0.6 = lean semantic but still respect exact legal terms
# NOTE: currently unused — the index is dense-only, see retriever.py
HYBRID_ALPHA = 0.6


# ─────────────────────────────────────────
# Sanitize stage (sanitize.py)
# ─────────────────────────────────────────

# Docling attaches massive layout arrays that exceed Pinecone's 40KB limit.
# These are dropped entirely since they aren't needed for vector search.
SANITIZE_KEYS_TO_DROP = ["doc_items", "layout", "bounding_box", "paths", "styles"]

# Pinecone metadata limit is 40KB total; 10,000 chars (~10KB) leaves headroom.
SANITIZE_MAX_STRING_LENGTH = 10000