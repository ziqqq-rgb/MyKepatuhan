import httpx
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory

from core import config
from services.key_rotation import RoundRobinPool
from tests.rag_evaluation.rate_limiter import RateLimiter, RateLimitedTransport


def build_judge(limiter: RateLimiter):
    """Pass the SAME limiter instance used for generation — judge and
    generation calls draw from the same rotating key pool and quota.

    max_tokens is set explicitly: ragas' llm_factory falls back to
    instructor's default of 1024, which is too small for metrics like
    Faithfulness (it decomposes the answer into many atomic claims before
    scoring). Too low a budget makes Gemini return a truncated JSON
    payload, which instructor raises as IncompleteOutputException
    ("The output is incomplete due to a max_tokens length limit.")
    instead of a usable score.
    """
    key_pool = RoundRobinPool(config.GEMINI_GENERATION_API_KEYS)
    client = AsyncOpenAI(
        api_key=key_pool.next(),  # placeholder — overwritten per-request by the transport
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        http_client=httpx.AsyncClient(transport=RateLimitedTransport(limiter, key_pool)),
    )
    llm = llm_factory(
        model=config.GEMINI_GENERATION_MODEL,
        provider="openai",
        client=client,
        max_tokens=config.RAGAS_JUDGE_MAX_TOKENS,
    )
    embeddings = embedding_factory(model=config.RAGAS_JUDGE_EMBEDDING_MODEL, provider="openai", client=client)
    return llm, embeddings