"""
httpx.get is monkeypatched at the module level so no real network call
is made. A minimal _FakeResponse stands in for httpx.Response — only
status_code and json() are ever touched by verify_stack_access_token.
"""
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from auth.oauth import verify_stack_access_token


class _FakeResponse:
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self._body = body

    def json(self) -> dict:
        return self._body


class TestVerifyStackAccessToken:
    def test_returns_email_from_snake_case_field(self, monkeypatch):
        monkeypatch.setattr(
            "auth.oauth.httpx.get",
            lambda *a, **kw: _FakeResponse(200, {"primary_email": "user@example.com"}),
        )
        assert verify_stack_access_token("valid-token") == "user@example.com"

    def test_falls_back_to_camel_case_field(self, monkeypatch):
        monkeypatch.setattr(
            "auth.oauth.httpx.get",
            lambda *a, **kw: _FakeResponse(200, {"primaryEmail": "user@example.com"}),
        )
        assert verify_stack_access_token("valid-token") == "user@example.com"

    def test_missing_email_raises_401(self, monkeypatch):
        monkeypatch.setattr(
            "auth.oauth.httpx.get",
            lambda *a, **kw: _FakeResponse(200, {}),
        )
        with pytest.raises(HTTPException) as exc_info:
            verify_stack_access_token("valid-token")
        assert exc_info.value.status_code == 401

    def test_non_200_response_raises_401(self, monkeypatch):
        monkeypatch.setattr(
            "auth.oauth.httpx.get",
            lambda *a, **kw: _FakeResponse(401, {"error": "invalid session"}),
        )
        with pytest.raises(HTTPException) as exc_info:
            verify_stack_access_token("expired-token")
        assert exc_info.value.status_code == 401

    def test_network_error_raises_503(self, monkeypatch):
        def _raise(*args, **kwargs):
            raise httpx.RequestError("connection failed")

        monkeypatch.setattr("auth.oauth.httpx.get", _raise)

        with pytest.raises(HTTPException) as exc_info:
            verify_stack_access_token("valid-token")
        assert exc_info.value.status_code == 503

    def test_sends_required_stack_auth_headers(self, monkeypatch):
        captured = {}

        def _fake_get(url, headers, timeout):
            captured["url"] = url
            captured["headers"] = headers
            return _FakeResponse(200, {"primary_email": "user@example.com"})

        monkeypatch.setattr("auth.oauth.httpx.get", _fake_get)

        verify_stack_access_token("my-token")

        assert captured["headers"]["x-stack-access-token"] == "my-token"
        assert captured["headers"]["x-stack-access-type"] == "server"
        assert "x-stack-project-id" in captured["headers"]
        assert "x-stack-secret-server-key" in captured["headers"]