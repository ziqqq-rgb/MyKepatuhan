"""
conftest.py seeds JWT_SECRET_KEY before config is imported, so
create_access_token/decode_token exercise a real jose/jwt round trip
without needing a live secret.
"""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import jwt

from auth.utils import (
    create_access_token,
    decode_token,
    get_current_admin,
    hash_password,
    verify_password,
)
from core import config


class TestPasswordHashing:
    def test_hash_is_not_the_plaintext(self):
        assert hash_password("correct-horse") != "correct-horse"

    def test_correct_password_verifies(self):
        hashed = hash_password("correct-horse")
        assert verify_password("correct-horse", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct-horse")
        assert verify_password("wrong-password", hashed) is False


class TestAccessToken:
    def test_round_trip_preserves_payload(self):
        token = create_access_token({"sub": "user-123"})
        assert decode_token(token)["sub"] == "user-123"

    def test_token_carries_an_expiry_claim(self):
        token = create_access_token({"sub": "user-123"})
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        assert "exp" in payload

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not-a-real-token")
        assert exc_info.value.status_code == 401

    def test_token_signed_with_wrong_secret_raises_401(self):
        bad_token = jwt.encode({"sub": "user-123"}, "wrong-secret", algorithm=config.JWT_ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(bad_token)
        assert exc_info.value.status_code == 401


class TestGetCurrentAdmin:
    def test_admin_user_passes_through(self):
        admin_user = SimpleNamespace(is_admin=True)
        assert get_current_admin(admin_user) is admin_user

    def test_non_admin_user_raises_403(self):
        regular_user = SimpleNamespace(is_admin=False)
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(regular_user)
        assert exc_info.value.status_code == 403