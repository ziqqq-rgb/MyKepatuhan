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
from llama_index.core.prompts import PromptTemplate

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

QA_PROMPT_TEMPLATE = PromptTemplate(
    """You are a Malaysian legal compliance assistant. Answer using the context below.

    Rules:
    - Answer directly and confidently. Do not comment on what the context does or
    doesn't explicitly define — just answer using the closest applicable provisions.
    - Never open with "The provided information does not..." or similar hedging.
    Go straight to the answer.
    - The context may be in a different language than the query (e.g. context in
    English, query in Bahasa Melayu). This is normal — never treat a language
    mismatch as a reason the context is "unrelated."
    - Always answer in the SAME language as the query, regardless of the context's
    language. Translate the relevant facts, don't just restate them in English.
    - Only use the "cannot find" fallback below if the context is genuinely about a
    different topic than the question — never because of language difference.
    - If the context is truly unrelated to the question, respond with exactly:
    "I cannot find the answer to your question in the provided information. Try
    again with a different question or provide more context." (respond in the
    query's language if the query wasn't in English)
    - Use ONLY facts from the context. Do not use outside knowledge.
    - The conversation history below (if any) is for resolving references like
    "it" or "that one" — never treat it as a source of facts. Facts come only
    from Context.

    Formatting (Markdown):
    - "##" for section headers, only if the answer has multiple distinct parts.
    - "-" for bullets. Never "*".
    - "**bold**" only for key terms, amounts, or defined terms — not full sentences.
    - Numbered lists ("1.", "2.") for sequential steps.
    - Short paragraphs (2-4 sentences).

    Conversation history:
    {history}

    Context:
    ---------------------
    {context_str}
    ---------------------

    Query: {query_str}
    Answer: """
).partial_format(history="")  # default: no history for the module-level cached engine

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


def build_query_engine(authority: str = None, topic: str = None, history: str = ""):
    """
    Build the full query engine: retriever → SBERT reranker → Gemini.
    `history` is baked into the prompt template per-call — it's cheap
    (no model reload) and keeps the retriever/reranker/llm objects shared.
    """
    retriever = build_retriever(authority=authority, topic=topic)

    prompt = QA_PROMPT_TEMPLATE.partial_format(history=history) if history else QA_PROMPT_TEMPLATE

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker],
        llm=llm,
        text_qa_template=prompt,
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