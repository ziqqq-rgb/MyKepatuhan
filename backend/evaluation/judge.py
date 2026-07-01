"""
Builds the Ragas judge: one Gemini LLM + one Gemini embedding model,
sharing a single client. Kept separate from scoring/orchestration so
the judge model can be swapped without touching either.
"""
from google import genai
from ragas.llms import llm_factory
from ragas.embeddings import GoogleEmbeddings

from core import config


def build_judge():
    """Returns (judge_llm, judge_embeddings), both backed by Gemini."""
    client = genai.Client(api_key=config.GEMINI_GENERATION_API_KEY)

    llm = llm_factory(
        config.GEMINI_GENERATION_MODEL,
        provider="google",
        client=client,
        adapter="litellm",
    )
    embeddings = GoogleEmbeddings(client=client, model=config.RAGAS_JUDGE_EMBEDDING_MODEL)
    return llm, embeddings