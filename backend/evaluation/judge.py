from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory

from core import config

def build_judge():
    """Returns (judge_llm, judge_embeddings), both backed by Gemini via OpenAI compatibility."""
    
    # 1. Initialize ONE AsyncOpenAI client for both Generation and Embeddings.
    # This natively supports asynchronous gather() and bypasses all SDK friction.
    client = AsyncOpenAI(
        api_key=config.GEMINI_GENERATION_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # 2. Build the LLM using the native factory
    llm = llm_factory(
        model=config.GEMINI_GENERATION_MODEL,
        provider="openai",
        client=client
    )
    
    # 3. Build the Embeddings using the native factory
    # This satisfies the strict "modern embeddings" check from Ragas collections
    embeddings = embedding_factory(
        model=config.RAGAS_JUDGE_EMBEDDING_MODEL,
        provider="openai",
        client=client
    )
    
    return llm, embeddings