import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User, Conversation
from auth.utils import get_current_user
from pipeline.retriever import build_query_engine, build_retriever
from services.cache import get_cached_response, set_cached_response
from services.llm_backoff import call_with_backoff
from services.citation_builder import Citation, build_citations
from services import conversation_service as conv

log = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])

query_engine_cache: dict = {}
retriever_cache: dict = {}


class QueryRequest(BaseModel):
    question: str
    authority: Optional[str] = None
    topic: Optional[str] = None
    conversation_id: Optional[str] = None  # omit for a stateless, cacheable query


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    no_results: bool = False


def _empty_response(question: str) -> QueryResponse:
    return QueryResponse(question=question, answer="", citations=[], no_results=True)


# ── Conversation resolution ──────────────────────────────

def _resolve_conversation(
    db: Session, conversation_id: Optional[str], user: User
) -> Optional[Conversation]:
    """Returns the owned conversation, or None for a stateless request."""
    if not conversation_id:
        return None
    conversation = conv.get_owned_conversation(db, conversation_id, user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


# ── Engine/retriever selection ───────────────────────────

def _get_retriever(authority: Optional[str], topic: Optional[str]):
    if not authority and not topic:
        if "default" not in retriever_cache:
            retriever_cache["default"] = build_retriever()
        return retriever_cache["default"]
    return build_retriever(authority=authority, topic=topic)


def _get_query_engine(authority: Optional[str], topic: Optional[str], history: str):
    """
    The default (no filters, no history) engine is cached — it's the hot
    path. Anything with history gets a fresh engine, since history is baked
    into its prompt template per-request and can't be shared.
    """
    if not authority and not topic and not history:
        if "default" not in query_engine_cache:
            query_engine_cache["default"] = build_query_engine()
        return query_engine_cache["default"]
    return build_query_engine(authority=authority, topic=topic, history=history)


# ── Pipeline steps-----

def _retrieve_or_500(retriever, question: str):
    try:
        return retriever.retrieve(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


def _generate_or_500(engine, question: str):
    try:
        return call_with_backoff(engine.query, question)
    except Exception as e:
        log.error(f"Query failed: {e!r}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# ── Route ─────────────────────────────────────────────────

@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    conversation = _resolve_conversation(db, request.conversation_id, current_user)
    history = (
        conv.build_history_prompt(conv.get_messages(db, conversation.id))
        if conversation else ""
    )

    # Cache is for stateless queries only — conversation turns are persisted
    # in Postgres instead, since their answer depends on prior context.
    if not conversation:
        cached = get_cached_response(request.question, request.authority, request.topic)
        if cached:
            return QueryResponse(**cached)

    retriever = _get_retriever(request.authority, request.topic)
    retrieved_nodes = _retrieve_or_500(retriever, request.question)
    if not retrieved_nodes:
        return _empty_response(request.question)

    engine = _get_query_engine(request.authority, request.topic, history)
    response = _generate_or_500(engine, request.question)
    if not response.source_nodes:
        return _empty_response(request.question)

    result = QueryResponse(
        question=request.question,
        answer=str(response.response),
        citations=build_citations(response.source_nodes),
    )

    if conversation:
        conv.record_turn(db, conversation, request.question, result.answer)
    else:
        set_cached_response(request.question, request.authority, request.topic, result.model_dump())

    return result