import httpx
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory

from core import config
from services.key_rotation import RoundRobinPool
from tests.rag_evaluation.rate_limiter import RateLimiter, RateLimitedTransport


def build_judge(limiter: RateLimiter):
    """Pass the SAME limiter instance used for generation — judge and
    generation calls draw from the same rotating key pool and quota."""
    key_pool = RoundRobinPool(config.GEMINI_GENERATION_API_KEYS)
    client = AsyncOpenAI(
        api_key=key_pool.next(),  # placeholder — overwritten per-request by the transport
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        http_client=httpx.AsyncClient(transport=RateLimitedTransport(limiter, key_pool)),
    )
    llm = llm_factory(model=config.GEMINI_GENERATION_MODEL, provider="openai", client=client)
    embeddings = embedding_factory(model=config.RAGAS_JUDGE_EMBEDDING_MODEL, provider="openai", client=client)
    return llm, embeddings