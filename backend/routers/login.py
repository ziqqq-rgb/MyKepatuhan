from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.db import get_db
from database.models import User
from auth.utils import verify_password, create_access_token

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
    email: str

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login with email + password. Returns a JWT access token."""
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
def get_me(db: Session = Depends(get_db), token: str = ""):
    """Returns the currently authenticated user's profile."""
    from auth.utils import get_current_user
    from fastapi import Request
    pass 

@router.post("/oauth-login")
def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Bridge endpoint for Google Sign-In via Stack Auth"""
    # 1. Check if the user already exists in your Postgres DB
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # 2. If they are a brand new Google user, create a profile for them!
        # We give them a dummy password because Google handles their actual auth
        user = User(
            email=request.email,
            hashed_password="OAUTH_USER_NO_PASSWORD", 
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Issue the standard FastAPI JWT so they can query the RAG engine
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
    