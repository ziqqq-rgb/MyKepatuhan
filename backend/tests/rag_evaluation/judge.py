"""
Builds the Ragas judge LLM + embeddings, backed by Gemini via OpenAI
compatibility, routed through a shared RateLimiter so judge calls never
exceed quota — regardless of how many sub-calls a metric fires internally.
"""
import httpx
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory

from core import config
from tests.rag_evaluation.rate_limiter import RateLimiter, RateLimitedTransport


def build_judge(limiter: RateLimiter):
    """Pass the SAME limiter instance used for generation — judge and
    generation share one Gemini API key and one quota."""
    client = AsyncOpenAI(
        api_key=config.GEMINI_GENERATION_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        http_client=httpx.AsyncClient(transport=RateLimitedTransport(limiter)),
    )
    llm = llm_factory(model=config.GEMINI_GENERATION_MODEL, provider="openai", client=client)
    embeddings = embedding_factory(model=config.RAGAS_JUDGE_EMBEDDING_MODEL, provider="openai", client=client)
    return llm, embeddings