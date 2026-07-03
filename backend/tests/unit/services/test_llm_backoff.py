"""
Unit tests for services/llm_backoff.py.

`time.sleep` is monkeypatched so tests run instantly instead of waiting
through real exponential backoff (5s, 10s, 20s...).

_RateLimitError mimics google.genai.errors.ClientError without calling
its real constructor — we only need an exception with a `.code`
attribute that `call_with_backoff` can catch and inspect.
"""
import pytest
from google.genai.errors import ClientError

from services.llm_backoff import call_with_backoff


class _RateLimitError(ClientError):
    def __init__(self, code=429):
        self.code = code  # skip ClientError.__init__, we only need .code


class _OtherClientError(ClientError):
    def __init__(self, code=400):
        self.code = code


def test_returns_result_on_first_success():
    calls = []

    def fn():
        calls.append(1)
        return "ok"

    assert call_with_backoff(fn) == "ok"
    assert len(calls) == 1


def test_retries_on_429_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr("services.llm_backoff.time.sleep", lambda s: sleeps.append(s))

    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise _RateLimitError()
        return "ok"

    result = call_with_backoff(flaky, max_retries=5)

    assert result == "ok"
    assert attempts["count"] == 3
    assert sleeps == [5, 10]  # exponential backoff before attempts 2 and 3


def test_raises_after_exhausting_all_retries(monkeypatch):
    monkeypatch.setattr("services.llm_backoff.time.sleep", lambda s: None)

    def always_rate_limited():
        raise _RateLimitError()

    with pytest.raises(ClientError):
        call_with_backoff(always_rate_limited, max_retries=3)


def test_non_429_error_raises_immediately_without_retry(monkeypatch):
    sleeps = []
    monkeypatch.setattr("services.llm_backoff.time.sleep", lambda s: sleeps.append(s))

    attempts = {"count": 0}

    def bad_request():
        attempts["count"] += 1
        raise _OtherClientError(code=400)

    with pytest.raises(ClientError):
        call_with_backoff(bad_request, max_retries=3)

    assert attempts["count"] == 1  # no retry for non-rate-limit errors
    assert sleeps == []