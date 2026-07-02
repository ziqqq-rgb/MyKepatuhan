"""
All conversation/message persistence and history formatting lives here.
Routers stay HTTP-only, query.py stays focused on the RAG pipeline.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from core import config
from database.models import Conversation, Message


def create_conversation(db: Session, user_id: str, title: str = "New conversation") -> Conversation:
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_id: str) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_owned_conversation(db: Session, conversation_id: str, user_id: str) -> Conversation | None:
    """Returns the conversation only if it belongs to user_id — prevents cross-user access."""
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != user_id:
        return None
    return conversation


def get_messages(db: Session, conversation_id: str) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def add_message(db: Session, conversation_id: str, role: str, content: str) -> None:
    db.add(Message(conversation_id=conversation_id, role=role, content=content))
    db.commit()


def delete_conversation(db: Session, conversation: Conversation) -> None:
    db.query(Message).filter(Message.conversation_id == conversation.id).delete()
    db.delete(conversation)
    db.commit()


def build_history_prompt(messages: list[Message]) -> str:
    """
    Formats the last N turns as plain text for prompt injection.
    N is *turns* (user+assistant pairs), so we keep the last N*2 messages.
    Returns "" when there's no history — the prompt template treats that as no-op.
    """
    recent = messages[-(config.CHAT_HISTORY_TURNS * 2):]
    if not recent:
        return ""
    return "\n".join(f"{m.role.capitalize()}: {m.content}" for m in recent)

def _truncate_title(text: str, max_len: int = 60) -> str:
    """Collapses a question into a short sidebar-friendly title."""
    cleaned = text.strip().replace("\n", " ")
    return cleaned if len(cleaned) <= max_len else cleaned[:max_len].rstrip() + "..."


def record_turn(db: Session, conversation: Conversation, question: str, answer: str) -> None:
    """
    Saves one user+assistant exchange. If this is the conversation's first
    message, also sets the title from the question — keeps the "New Chat"
    default from lingering forever in the sidebar.
    """
    is_first_turn = conversation.title == "New conversation"

    add_message(db, conversation.id, "user", question)
    add_message(db, conversation.id, "assistant", answer)

    if is_first_turn:
        conversation.title = _truncate_title(question)
        db.commit()