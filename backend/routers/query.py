from logging import log
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import asyncio
import time
from google.genai.errors import ClientError 

from database.models import User
from auth.utils import get_current_user
from pipeline.retriever import build_query_engine, build_retriever

router = APIRouter(prefix="/query", tags=["Query"])

query_engine_cache: dict = {}
retriever_cache: dict = {}


class QueryRequest(BaseModel):
    question: str
    authority: Optional[str] = None
    topic: Optional[str] = None


class Citation(BaseModel):
    rank: int
    authority: str
    topic: str
    document_type: str
    document_title: str
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    no_results: bool = False

def _call_with_backoff(fn, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except ClientError as e:
            if getattr(e, "code", None) == 429 and attempt < max_retries - 1:
                wait = 5 * (2 ** attempt)
                time.sleep(wait)
                continue
            raise

@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not request.authority and not request.topic:
        retriever = retriever_cache.get("default")
        if retriever is None:
            retriever = build_retriever()
            retriever_cache["default"] = retriever
    else:
        retriever = build_retriever(authority=request.authority, topic=request.topic)

    try:
        retrieved_nodes = retriever.retrieve(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

    if not retrieved_nodes:
        return QueryResponse(
            question=request.question,
            answer="",
            citations=[],
            no_results=True,
        )

    if not request.authority and not request.topic:
        engine = query_engine_cache.get("default")
        if engine is None:
            engine = build_query_engine()
            query_engine_cache["default"] = engine
    else:
        engine = build_query_engine(authority=request.authority, topic=request.topic)

    try:
        response = _call_with_backoff(engine.query, request.question)
    except Exception as e:
        log.error(f"Query failed: {e!r}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    if not response.source_nodes:
        return QueryResponse(
            question=request.question,
            answer="",
            citations=[],
            no_results=True,
        )

    citations = [
        Citation(
            rank=i + 1,
            authority=node.node.metadata.get("authority", "Unknown"),
            topic=node.node.metadata.get("topic", "Unknown"),
            document_type=node.node.metadata.get("document_type", "Unknown"),
            document_title=node.node.metadata.get("source_document", "Unknown source"),
            score=round(node.score or 0.0, 4),
            excerpt=(
                node.node.text[:300] + "..."
                if len(node.node.text) > 300
                else node.node.text
            ),
        )
        for i, node in enumerate(response.source_nodes)
    ]

    return QueryResponse(
        question=request.question,
        answer=str(response.response),
        citations=citations,
    )