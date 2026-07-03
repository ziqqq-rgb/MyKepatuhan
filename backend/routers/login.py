from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db import get_db
from database.models import User
from auth.oauth import verify_stack_access_token
from auth.utils import verify_password, create_access_token, get_current_user
from core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_RATE_LIMIT = "10/minute"


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
    access_token: str  # Stack Auth session token — not a raw Google token


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Email/password login — unrelated to Google/Stack, unchanged."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not _password_matches(user, form_data.password):
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


def _password_matches(user: User, plain_password: str) -> bool:
    """
    Wraps verify_password so a malformed hash (e.g. Google-only accounts,
    which store a sentinel instead of a real bcrypt hash) fails the login
    cleanly instead of raising and surfacing as a 500.
    """
    try:
        return verify_password(plain_password, user.hashed_password)
    except ValueError:
        return False


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/oauth-login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
def oauth_login(request: Request, oauth_request: OAuthLoginRequest, db: Session = Depends(get_db)):
    email = verify_stack_access_token(oauth_request.access_token)

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