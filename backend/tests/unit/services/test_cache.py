"""
Unit tests for services/cache.py.

`_redis` is resolved once at import time from get_redis_client(), so
tests monkeypatch the module-level `_redis` directly rather than
intercepting the factory call.
"""
import pytest

from services import cache


class _FakeRedis:
    def __init__(self):
        self.store = {}
        self.raise_on_get = False
        self.raise_on_set = False

    def get(self, key):
        if self.raise_on_get:
            raise RuntimeError("redis down")
        return self.store.get(key)

    def set(self, key, value, ex=None):
        if self.raise_on_set:
            raise RuntimeError("redis down")
        self.store[key] = value


@pytest.fixture
def fake_redis(monkeypatch):
    redis = _FakeRedis()
    monkeypatch.setattr(cache, "_redis", redis)
    return redis


class TestGetCachedResponse:
    def test_returns_none_when_redis_disabled(self, monkeypatch):
        monkeypatch.setattr(cache, "_redis", None)
        assert cache.get_cached_response("q", None, None) is None

    def test_returns_none_on_cache_miss(self, fake_redis):
        assert cache.get_cached_response("q", None, None) is None

    def test_returns_parsed_json_on_hit(self, fake_redis):
        cache.set_cached_response("q", "SSM", "tax", {"answer": "42"})
        assert cache.get_cached_response("q", "SSM", "tax") == {"answer": "42"}

    def test_fails_open_on_redis_error(self, fake_redis):
        fake_redis.raise_on_get = True
        assert cache.get_cached_response("q", None, None) is None


class TestSetCachedResponse:
    def test_noop_when_redis_disabled(self, monkeypatch):
        monkeypatch.setattr(cache, "_redis", None)
        cache.set_cached_response("q", None, None, {"answer": "42"})  # must not raise

    def test_fails_open_on_redis_error(self, fake_redis):
        fake_redis.raise_on_set = True
        cache.set_cached_response("q", None, None, {"answer": "42"})  # must not raise


class TestCacheKeyBuilding:
    def test_same_question_different_case_and_whitespace_share_a_key(self, fake_redis):
        cache.set_cached_response("  What is TAX?  ", "SSM", "tax", {"answer": "42"})
        assert cache.get_cached_response("what is tax?", "SSM", "tax") == {"answer": "42"}

    def test_different_authority_is_a_different_cache_entry(self, fake_redis):
        cache.set_cached_response("q", "SSM", "tax", {"answer": "ssm-answer"})
        assert cache.get_cached_response("q", "KKM", "tax") is None