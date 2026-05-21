from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.models import User
from auth.utils import get_current_user
from pipeline.retriever import build_query_engine

 
router = APIRouter(prefix="/query", tags=["Query"])
 
query_engine_cache: dict = {}
 

class QueryRequest(BaseModel):
    question: str
    authority: Optional[str] = None
    topic: Optional[str] = None
 
 
class Citation(BaseModel):
    rank: int
    authority: str
    topic: str
    document_type: str
    score: float
    excerpt: str
 
 
class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
 

@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),   
    ):
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
 
 
    if not request.authority and not request.topic:
        engine = query_engine_cache.get("default")
        if engine is None:
            engine = build_query_engine()
            query_engine_cache["default"] = engine
    else:
        engine = build_query_engine(
            authority=request.authority,
            topic=request.topic,
        )
 
    try:
        response = engine.query(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
 
    citations = [
        Citation(
            rank=i + 1,
            authority=node.node.metadata.get("authority", "Unknown"),
            topic=node.node.metadata.get("topic", "Unknown"),
            document_type=node.node.metadata.get("document_type", "Unknown"),
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
 
