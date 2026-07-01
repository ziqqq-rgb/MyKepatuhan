import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.models import User
from auth.utils import get_current_user
from pipeline.retriever import build_query_engine, build_retriever
from services.cache import get_cached_response, set_cached_response
from services.llm_backoff import call_with_backoff
from services.citation_builder import Citation, build_citations

log = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])

query_engine_cache: dict = {}
retriever_cache: dict = {}


class QueryRequest(BaseModel):
    question: str
    authority: Optional[str] = None
    topic: Optional[str] = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    no_results: bool = False


def _empty_response(question: str) -> QueryResponse:
    return QueryResponse(question=question, answer="", citations=[], no_results=True)


def _get_retriever(authority: Optional[str], topic: Optional[str]):
    if not authority and not topic:
        if "default" not in retriever_cache:
            retriever_cache["default"] = build_retriever()
        return retriever_cache["default"]
    return build_retriever(authority=authority, topic=topic)


def _get_query_engine(authority: Optional[str], topic: Optional[str]):
    if not authority and not topic:
        if "default" not in query_engine_cache:
            query_engine_cache["default"] = build_query_engine()
        return query_engine_cache["default"]
    return build_query_engine(authority=authority, topic=topic)


@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    cached = get_cached_response(request.question, request.authority, request.topic)
    if cached:
        return QueryResponse(**cached)

    retriever = _get_retriever(request.authority, request.topic)

    try:
        retrieved_nodes = retriever.retrieve(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

    if not retrieved_nodes:
        return _empty_response(request.question)

    engine = _get_query_engine(request.authority, request.topic)

    try:
        response = call_with_backoff(engine.query, request.question)
    except Exception as e:
        log.error(f"Query failed: {e!r}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    if not response.source_nodes:
        return _empty_response(request.question)

    result = QueryResponse(
        question=request.question,
        answer=str(response.response),
        citations=build_citations(response.source_nodes),
    )
    set_cached_response(request.question, request.authority, request.topic, result.model_dump())
    return result