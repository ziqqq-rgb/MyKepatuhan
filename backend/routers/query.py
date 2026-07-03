import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User, Conversation
from auth.utils import get_current_user
from core.rate_limit import limiter
from services.rag_pipeline import retrieve_and_rerank, generate_answer
from services.cache import get_cached_response, set_cached_response
from services.citation_builder import Citation, build_citations
from services.language import detect_language
from services import small_talk
from services import conversation_service as conv

log = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="The user compliance query or question.")
    authority: Optional[str] = None
    topic: Optional[str] = None
    conversation_id: Optional[UUID4] = Field(None, description="Optional existing conversation thread ID.")


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    no_results: bool = False


def _empty_response(question: str) -> QueryResponse:
    return QueryResponse(question=question, answer="", citations=[], no_results=True)


def _resolve_conversation(db: Session, conversation_id: Optional[UUID4], user: User) -> Optional[Conversation]:
    """Returns the owned conversation, or None for a stateless request."""
    if not conversation_id:
        return None
    conversation = conv.get_owned_conversation(db, str(conversation_id), user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


def _handle_greeting(db: Session, conversation: Optional[Conversation], question: str) -> QueryResponse:
    """Greetings never enter the RAG pipeline — answered directly."""
    language = detect_language(question)
    answer = small_talk.greeting_response(language)
    if conversation:
        conv.record_turn(db, conversation, question, answer)
    return QueryResponse(question=question, answer=answer, citations=[])


@router.post("", response_model=QueryResponse)
@limiter.limit("5/minute")
def query(
    request: Request,
    query_req: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = query_req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    conversation = _resolve_conversation(db, query_req.conversation_id, current_user)

    if small_talk.is_greeting(question):
        return _handle_greeting(db, conversation, question)

    history = conv.build_history_prompt(conv.get_messages(db, conversation.id)) if conversation else ""

    # Stateless requests can hit the response cache. Bypassed once a
    # conversation exists, since prior turns change the correct answer.
    if not conversation:
        cached = get_cached_response(query_req.question, query_req.authority, query_req.topic)
        if cached:
            return QueryResponse(**cached)

    try:
        nodes = retrieve_and_rerank(question, query_req.authority, query_req.topic)
    except Exception as e:
        log.error(f"Retrieval failed for question '{question}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal system error occurred during document retrieval.")

    if not nodes:
        return _empty_response(question)

    target_language = detect_language(question)
    try:
        answer = generate_answer(question, nodes, history, target_language)
    except Exception as e:
        log.error(f"LLM generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal system error occurred during response generation.")

    result = QueryResponse(question=question, answer=answer, citations=build_citations(nodes))

    if conversation:
        conv.record_turn(db, conversation, question, result.answer)
    else:
        set_cached_response(query_req.question, query_req.authority, query_req.topic, result.model_dump())

    return result