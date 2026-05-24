from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
import httpx
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.db import get_db
from database.models import User
from auth.utils import verify_password, create_access_token
from auth.utils import get_current_user

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
    """Returns the currently authenticated user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
    }

@router.post("/oauth-login")
def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        user = User(
            email=request.email,
            hashed_password="OAUTH_USER_NO_PASSWORD",
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
    