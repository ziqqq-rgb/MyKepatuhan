import uuid

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
import httpx
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core import config
from database.db import get_db
from database.models import User
from auth.oauth import verify_google_id_token
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
    id_token: str
    

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
    email = verify_google_id_token(request.id_token)   # ← verified, not trusted input

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password="OAUTH_USER_NO_PASSWORD", is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/callback")
async def google_oauth_callback(code: str, db: Session = Depends(get_db)):
    """
    Handles the redirect from Google, verifying the user and issuing a JWT.
    """
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=token_payload)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Google authentication failed.")
        google_token = token_res.json().get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    async with httpx.AsyncClient() as client:
        user_res = await client.get(user_info_url, headers={"Authorization": f"Bearer {google_token}"})
        user_data = user_res.json()
        
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no associated email.")

    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            hashed_password=uuid.uuid4().hex,
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})

    # ensure this points to your real domain (e.g., https://mykepatuhan.com/login)
    frontend_redirect_url = f"http://localhost:3000/login?token={access_token}"
    return RedirectResponse(url=frontend_redirect_url)