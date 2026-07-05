import os
from dotenv import load_dotenv

load_dotenv()

def get_env_or_fail(var_name: str) -> str:
  
    #Raises an immediate error if missing to prevent silent security failures.
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"CRITICAL SECURITY ERROR: Missing required environment variable '{var_name}'")
    return value


GEMINI_ENRICH_API_KEY = get_env_or_fail("GEMINI_KEY")
GEMINI_GENERATION_API_KEY = os.getenv("GEMINI_GENERATION_KEY", GEMINI_ENRICH_API_KEY)
GEMINI_API_KEY = GEMINI_ENRICH_API_KEY
GEMINI_EMBED_API_KEY = os.getenv("GEMINI_EMBED_KEY", GEMINI_API_KEY) 
JINA_API_KEY = get_env_or_fail("JINA_API_KEY")

_raw_generation_keys = os.getenv("GEMINI_GENERATION_KEYS", "")
GEMINI_GENERATION_API_KEYS = (
    [k.strip() for k in _raw_generation_keys.split(",") if k.strip()]
    or [GEMINI_GENERATION_API_KEY]
)

PINECONE_API_KEY = get_env_or_fail("PINECON_KEY")
JWT_SECRET_KEY = get_env_or_fail("JWT_SECRET_KEY")
DATABASE_URL = get_env_or_fail("DATABASE_URL")
STACK_PROJECT_ID = get_env_or_fail("STACK_PROJECT_ID")
STACK_SECRET_SERVER_KEY = get_env_or_fail("STACK_SECRET_SERVER_KEY")

# Strict CORS: Remove the "*" fallback. If it's empty, default to localhost for dev safely.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

# ─────────────────────────────────────────
# Auth
# ─────────────────────────────────────────
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ─────────────────────────────────────────
# Embedding model
# ─────────────────────────────────────────
GEMINI_EMBED_MODEL = "gemini-embedding-001"
EMBED_OUTPUT_DIMENSIONALITY = 1536
EMBED_BATCH_SIZE = 50
DOCLING_TOKENIZER_MODEL = "nomic-ai/nomic-embed-text-v1.5"  
DOCLING_MAX_TOKENS = 512

# ─────────────────────────────────────────
# Pinecone
# ─────────────────────────────────────────
PINECONE_INDEX_NAME = "mykepatuhan"

# ─────────────────────────────────────────
# Gemini Settings
# ─────────────────────────────────────────
GEMINI_ENRICH_MODEL = "gemini-3.1-flash-lite"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_ENRICH_MODEL}:generateContent?key={GEMINI_API_KEY}"
)
ENRICHMENT_CONCURRENT_REQUESTS = 5   
ENRICHMENT_BATCH_SAVE_EVERY = 50
ENRICHMENT_CONTEXT_CHARS = 2000
ENRICHMENT_MAX_RETRIES = 3

GEMINI_GENERATION_MODEL = "gemini-3.1-flash-lite"
GEMINI_GENERATION_TEMPERATURE = 0.0
RAGAS_JUDGE_EMBEDDING_MODEL = "gemini-embedding-2"

# ─────────────────────────────────────────
# Retrieval / reranking
# ─────────────────────────────────────────
RETRIEVAL_TOP_K = 15          
RERANK_TOP_N = 3              
JINA_RERANK_MODEL = "jina-reranker-v2-base-multilingual"  
HYBRID_ALPHA = 0.6

# ─────────────────────────────────────────
# Sanitize stage
# ─────────────────────────────────────────
SANITIZE_KEYS_TO_DROP = ["doc_items", "layout", "bounding_box", "paths", "styles"]
SANITIZE_MAX_STRING_LENGTH = 10000

# ─────────────────────────────────────────
# Cache & History
# ─────────────────────────────────────────
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 60 * 60 * 24)) 
CHAT_HISTORY_TURNS = 3

# ─────────────────────────────────────────
# Uploads
# ─────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 20))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
