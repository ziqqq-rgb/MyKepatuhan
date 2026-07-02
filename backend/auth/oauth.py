from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status

from core import config

_google_request = google_requests.Request()


def verify_google_id_token(token: str) -> str:
    """
    Verifies a Google-issued ID token and returns the verified email.
    Raises 401 if the token is invalid, expired, or not meant for this app.
    """
    try:
        claims = google_id_token.verify_oauth2_token(
            token, _google_request, config.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token.",
        )

    if not claims.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is not verified.",
        )

    return claims["email"]