"""
Proactive per-key request throttle for Gemini calls.

Reacting to 429s with backoff only kicks in *after* a key's quota
window is already blown. This limiter instead makes each key wait for
an open slot before sending, so five concurrent enrichment calls
can't all pile onto the same key's per-minute budget at once.
"""
import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """Allows at most `max_per_minute` calls per rolling 60s window."""

    def __init__(self, max_per_minute: int):
        self._max_per_minute = max_per_minute
        self._call_times: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            self._evict_expired(now)

            if len(self._call_times) >= self._max_per_minute:
                wait_seconds = 60 - (now - self._call_times[0])
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                now = time.monotonic()
                self._evict_expired(now)

            self._call_times.append(now)

    def _evict_expired(self, now: float) -> None:
        while self._call_times and now - self._call_times[0] > 60:
            self._call_times.popleft()