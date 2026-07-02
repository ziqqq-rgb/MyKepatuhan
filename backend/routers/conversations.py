from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.utils import get_current_user
from database.db import get_db
from database.models import User
from services import conversation_service as svc

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    title: str = "New conversation"


@router.post("", response_model=ConversationOut)
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Called when the user clicks 'New Chat'."""
    return svc.create_conversation(db, current_user.id, request.title)


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Powers the 'Saved Conversations' sidebar."""
    return svc.list_conversations(db, current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = svc.get_owned_conversation(db, conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return svc.get_messages(db, conversation_id)


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = svc.get_owned_conversation(db, conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    svc.delete_conversation(db, conversation)