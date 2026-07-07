"""
Generic retry-with-backoff wrapper for rate-limited API calls (e.g. Groq).
Not tied to any specific endpoint — reusable wherever a call can 429.
"""
import time
import logging
# from google.genai.errors import ClientError  # swapped for Groq
from openai import RateLimitError

log = logging.getLogger(__name__)


def call_with_backoff(fn, *args, max_retries: int = 3, **kwargs):
    """
    Calls fn(*args, **kwargs), retrying on HTTP 429 with exponential backoff
    (5s, 10s, 20s...). Re-raises immediately on any other error, and re-raises
    the 429 once retries are exhausted.
    """
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except RateLimitError:
            is_last_attempt = attempt == max_retries - 1
            if is_last_attempt:
                raise

            wait = 5 * (2 ** attempt)
            log.warning(f"[BACKOFF] Rate limited, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)