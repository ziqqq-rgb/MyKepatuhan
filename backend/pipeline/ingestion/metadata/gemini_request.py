"""
Low-level Gemini generateContent call. Knows nothing about retries or
key rotation — just sends one request and translates the HTTP response
into parsed JSON or a typed error.
"""
import httpx

from core import config
from pipeline.ingestion.metadata.json_extraction import extract_json


class RateLimited(Exception):
    """Raised on HTTP 429. Carries the server's suggested wait time, if given."""
    def __init__(self, retry_after_seconds: float | None):
        self.retry_after_seconds = retry_after_seconds
        super().__init__("Gemini rate limit (429)")


async def call_gemini(payload: dict, api_key: str) -> dict:
    """Sends one enrichment request. Raises RateLimited on 429, or
    httpx.HTTPStatusError on any other non-2xx response."""
    url = f"{config.GEMINI_ENRICH_URL_BASE}?key={api_key}"

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, json=payload)

    if response.status_code == 429:
        raise RateLimited(_parse_retry_after(response))

    response.raise_for_status()

    candidates = response.json().get("candidates", [])
    if not candidates:
        raise ValueError("Empty candidates list in Gemini response")

    raw_text = candidates[0]["content"]["parts"][0]["text"]
    return extract_json(raw_text)


def _parse_retry_after(response: httpx.Response) -> float | None:
    """Gemini sometimes sends a Retry-After header — honor the server's
    own number over our guessed exponential backoff when it's present."""
    header = response.headers.get("retry-after")
    try:
        return float(header) if header else None
    except ValueError:
        return None