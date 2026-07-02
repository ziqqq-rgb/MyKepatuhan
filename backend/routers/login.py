from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError 

from database.db import get_db
from database.models import User
from auth.oauth import verify_stack_access_token
from auth.utils import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


class OAuthLoginRequest(BaseModel):
    access_token: str | None = None


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Email/password login — unrelated to Google/Stack, unchanged."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/oauth-login", response_model=TokenResponse)
def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    if not request.access_token:
        raise HTTPException(status_code=401, detail="Missing Stack access token.")
    email = verify_stack_access_token(request.access_token)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password="OAUTH_USER_NO_PASSWORD", is_admin=False)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()
        else:
            db.refresh(user)

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token)