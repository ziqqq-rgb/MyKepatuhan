"""
Gemini Flash Lite REST client for metadata enrichment.

Calls the generateContent endpoint directly (rather than the SDK) with
responseMimeType=application/json for structured output. Rotates across
every configured enrichment key on a 429 — only the last key in the
pool falls back to exponential backoff — so one exhausted quota doesn't
poison a chunk's metadata with fallback values.
"""
import asyncio
import httpx

from core import config
from pipeline.ingestion.logger import log
from pipeline.ingestion.metadata.json_extraction import extract_json
from services.key_rotation import RoundRobinPool

PROMPT_TEMPLATE = """\
You are an expert Malaysian corporate lawyer. Read the text and extract metadata.
Respond ONLY with a valid JSON object. No markdown, no explanation, no code fences.
If the text does NOT fit the examples, do NOT use "unknown". Instead, dynamically generate a highly specific, accurate category based on the text.


{{
  "jurisdiction": "Use 'federal', 'state', or 'local'. If none fit, generate a specific jurisdiction type.",
  "authority":    "Use 'SSM', 'KKM', 'DBKL', 'MPKj', 'LHDN', or 'MyIPO'. If another body issued this, output that specific agency acronym (e.g., 'KWSP', 'PERKESO', 'DOSH').",
  "topic":        "Use 'tax', 'licensing', 'zoning', 'employment', 'registration', or 'compliance'. If it covers a different legal topic, create a precise corporate law topic name (e.g., 'foreign equity', 'data protection').",
  "document_type":"Use 'act', 'guideline', 'form', or 'fee_schedule'. If it is a different document class, generate the exact type (e.g., 'gazette', 'circular', 'appeal letter')."
}}

TEXT:
{chunk_text}"""

# Fallback values remain as hard system failures (e.g., if API completely times out or crashes)
FALLBACK_METADATA = {
    "jurisdiction":  "unclassified",
    "authority":     "unclassified",
    "topic":         "unclassified",
    "document_type": "unclassified",
}



# One key per rotation slot, built once at import — same pattern as the
# generation LLM pool in pipeline/retriever.py.
_key_pool = RoundRobinPool(config.GEMINI_ENRICH_API_KEYS)


class _RateLimited(Exception):
    """Raised internally when Gemini returns 429, to trigger a retry/rotation."""


def is_fallback(node) -> bool:
    """True if enrichment failed and the node is stuck on all-unknown defaults."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


def _build_payload(chunk_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(chunk_text=chunk_text)
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",  # Gemini native JSON mode — forces valid JSON output
        },
    }


async def _request_metadata_once(payload: dict, api_key: str) -> dict:
    """
    Makes a single Gemini call with the given key and parses the result.
    Raises _RateLimited on HTTP 429, or ValueError/KeyError if the
    response is missing expected fields.
    """
    url = f"{config.GEMINI_ENRICH_URL_BASE}?key={api_key}"
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code == 429:
        raise _RateLimited()

    resp.raise_for_status()

    candidates = resp.json().get("candidates", [])
    if not candidates:
        raise ValueError("Empty candidates list in Gemini response")

    raw = candidates[0]["content"]["parts"][0]["text"]
    return extract_json(raw)


async def _fetch_with_key_rotation(payload: dict, index: int, total: int) -> dict | None:
    """
    Tries each enrichment key once, round-robin. A 429 rotates to the
    next key immediately; the last key in the pool gets full exponential
    backoff (ENRICHMENT_MAX_RETRIES attempts) as a final fallback.
    Returns None only if every key is rate-limited.
    """
    pool_size = len(_key_pool)

    for key_attempt in range(pool_size):
        is_last_key = key_attempt == pool_size - 1
        api_key = _key_pool.next()
        retries = config.ENRICHMENT_MAX_RETRIES if is_last_key else 1

        for attempt in range(retries):
            try:
                return await _request_metadata_once(payload, api_key)
            except _RateLimited:
                if not is_last_key:
                    log.warning(
                        f"  [{index + 1}/{total}] Rate limited on key "
                        f"{key_attempt + 1}/{pool_size} — rotating to next key."
                    )
                    break
                wait = 5 * (2 ** attempt)
                log.warning(
                    f"  [{index + 1}/{total}] Rate limited — "
                    f"retrying in {wait}s (attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(wait)

    return None


async def enrich_single_node_async(semaphore, node, index: int, total: int):
    """Calls Gemini 3.1 Flash Lite via the REST generateContent endpoint."""
    async with semaphore:
        payload = _build_payload(node.text[:config.ENRICHMENT_CONTEXT_CHARS])

        try:
            extracted = await _fetch_with_key_rotation(payload, index, total)
        except (ValueError, KeyError) as e:
            log.warning(f"  [{index + 1}/{total}] JSON parse failed — using fallback. ({e})")
            node.metadata.update(FALLBACK_METADATA)
            return False
        except Exception as e:
            log.error(f"  [{index + 1}/{total}] ERROR — {e}")
            node.metadata.update(FALLBACK_METADATA)
            return False

        if extracted is None:
            log.error(
                f"  [{index + 1}/{total}] Rate limited across all "
                f"{len(_key_pool)} key(s) — using fallback."
            )
            node.metadata.update(FALLBACK_METADATA)
            return False

        node.metadata.update(extracted)
        log.info(f"  [{index + 1}/{total}] OK → {extracted}")
        return True