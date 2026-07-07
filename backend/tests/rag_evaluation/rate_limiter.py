import asyncio
import time
from collections import deque

import httpx

from services.key_rotation import RoundRobinPool


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._call_times: deque[float] = deque()

    async def wait_if_needed(self) -> None:
        now = time.monotonic()
        while self._call_times and now - self._call_times[0] > self.period_seconds:
            self._call_times.popleft()

        if len(self._call_times) >= self.max_calls:
            await asyncio.sleep(self.period_seconds - (now - self._call_times[0]) + 0.1)
            now = time.monotonic()

        self._call_times.append(now)


class RateLimitedTransport(httpx.AsyncHTTPTransport):
    """
    Paces every outgoing request, and (if given a key_pool) rewrites the
    Authorization header per request to rotate across Gemini keys — same
    round-robin pattern as enrichment/generation, applied at the transport
    so no per-call code needs to know rotation is happening.
    """
    def __init__(self, limiter: RateLimiter, key_pool: RoundRobinPool[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._limiter = limiter
        self._key_pool = key_pool

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        await self._limiter.wait_if_needed()
        if self._key_pool is not None:
            request.headers["Authorization"] = f"Bearer {self._key_pool.next()}"
        return await super().handle_async_request(request)