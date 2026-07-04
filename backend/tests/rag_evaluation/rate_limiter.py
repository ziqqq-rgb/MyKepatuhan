"""
Sliding-window rate limiter shared by every Gemini call in the eval suite —
generation and judge calls use the same API key, so they draw from the
same 15 RPM free-tier quota and must share one counter.
"""
import asyncio
import time
from collections import deque

import httpx


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._call_times: deque[float] = deque()

    async def wait_if_needed(self) -> None:
        """Blocks just long enough to keep calls under `max_calls` within
        the trailing window. Call immediately before any Gemini request."""
        now = time.monotonic()
        while self._call_times and now - self._call_times[0] > self.period_seconds:
            self._call_times.popleft()

        if len(self._call_times) >= self.max_calls:
            await asyncio.sleep(self.period_seconds - (now - self._call_times[0]) + 0.1)
            now = time.monotonic()

        self._call_times.append(now)


class RateLimitedTransport(httpx.AsyncHTTPTransport):
    """
    Wraps the OpenAI client's real transport so every outgoing request is
    throttled — including the multiple internal calls a single Ragas metric
    can fire (e.g. ContextPrecision calls the judge once per context). This
    is the only place that reliably sees every call, since pacing at the
    orchestration layer can't see what happens inside a library.
    """
    def __init__(self, limiter: RateLimiter, **kwargs):
        super().__init__(**kwargs)
        self._limiter = limiter

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        await self._limiter.wait_if_needed()
        return await super().handle_async_request(request)