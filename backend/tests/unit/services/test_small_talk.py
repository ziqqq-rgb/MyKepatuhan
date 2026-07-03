"""
Unit tests for services/small_talk.py.

Pure regex logic — no I/O, no dependencies, nothing to mock.
"""
import pytest

from services.small_talk import is_greeting, greeting_response


@pytest.mark.parametrize("text", [
    "hye",
    "hello!!",
    "Hi",
    "good morning",
    "selamat pagi",
    "  hey  ",
])
def test_pure_greeting_returns_true(text):
    assert is_greeting(text) is True


@pytest.mark.parametrize("text", [
    "hye, license for restaurant?",
    "hello, what's the tax rate for SMEs?",
    "good morning, do I need a business license?",
])
def test_greeting_attached_to_a_question_returns_false(text):
    # A greeting is only "pure" small talk if nothing follows it —
    # otherwise the real question must still reach the RAG pipeline.
    assert is_greeting(text) is False


def test_non_greeting_returns_false():
    assert is_greeting("What is the corporate tax rate in Malaysia?") is False


def test_empty_string_returns_false():
    assert is_greeting("") is False


def test_greeting_response_english():
    assert "compliance assistant" in greeting_response("en")


def test_greeting_response_malay():
    assert "pematuhan" in greeting_response("ms")


def test_greeting_response_unknown_language_falls_back_to_english():
    assert greeting_response("fr") == greeting_response("en")