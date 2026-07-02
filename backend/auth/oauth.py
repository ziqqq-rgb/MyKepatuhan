"""
Verifies a Stack Auth session by calling Stack's server API.

The frontend authenticates the user entirely through Stack Auth (Google
sign-in is configured in the Stack dashboard, not here). This module's
only job is confirming the access token the frontend hands us belongs
to a real, currently-valid Stack session before we mint our own JWT.
"""
import httpx
from fastapi import HTTPException, status

from core import config

STACK_USER_URL = "https://api.stack-auth.com/api/v1/users/me"


def verify_stack_access_token(access_token: str) -> str:
    """Returns the verified email for a valid Stack Auth session, or raises 401."""
    headers = {
        "x-stack-access-type": "server",
        "x-stack-project-id": config.STACK_PROJECT_ID,
        "x-stack-secret-server-key": config.STACK_SECRET_SERVER_KEY,
        "x-stack-access-token": access_token,
    }

    try:
        response = httpx.get(STACK_USER_URL, headers=headers, timeout=10)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the authentication provider.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    # Stack's REST response field is snake_case in most of their API; the
    # JS SDK exposes it as primaryEmail. Checking both makes this robust
    # to either casing — confirm the actual field with one manual test call.
    body = response.json()
    email = body.get("primary_email") or body.get("primaryEmail")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Stack Auth account has no associated email.",
        )
    return email