"""
Generic round-robin rotation over a fixed pool of resources (e.g. one
GoogleGenAI client per Gemini project key).

Round-robin instead of an "is this key in use" lock: Gemini's limits are
per-minute/per-day quotas, not a concurrency cap, so a mutex-style check
adds contention for no real protection. Spreading requests evenly across
keys is what actually multiplies your effective quota.
"""
import itertools
import threading
from typing import Generic, TypeVar

T = TypeVar("T")


class RoundRobinPool(Generic[T]):
    """Thread-safe round-robin cursor over a fixed list of items."""

    def __init__(self, items: list[T]):
        if not items:
            raise ValueError("RoundRobinPool requires at least one item")
        self.items = items
        self._cycle = itertools.cycle(items)
        self._lock = threading.Lock()

    def __len__(self) -> int:
        return len(self.items)

    def next(self) -> T:
        with self._lock:
            return next(self._cycle)