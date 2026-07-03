from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from auth.utils import hash_password
from core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

REGISTER_RATE_LIMIT = "10/minute"
MIN_PASSWORD_LENGTH = 8


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit(REGISTER_RATE_LIMIT)
def register(request: Request, register_request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == register_request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    if len(register_request.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
        )

    user = User(
        email=register_request.email,
        hashed_password=hash_password(register_request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user