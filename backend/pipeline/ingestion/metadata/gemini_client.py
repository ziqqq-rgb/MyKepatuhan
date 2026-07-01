"""
Gemini Flash Lite REST client for metadata enrichment.

Calls the generateContent endpoint directly (rather than the SDK) with
responseMimeType=application/json for structured output, retrying on
429 with exponential backoff so a rate-limit blip doesn't permanently
poison a chunk's metadata with fallback values.
"""
import asyncio
import httpx

from core import config
from pipeline.ingestion.logger import log
from pipeline.ingestion.metadata.json_extraction import extract_json

PROMPT_TEMPLATE = """\
You are an expert Malaysian corporate lawyer. Read the text and extract metadata.
Respond ONLY with a valid JSON object. No markdown, no explanation, no code fences.

{{
  "jurisdiction": "ONE OF: federal, state, local, unknown",
  "authority":    "ONE OF: SSM, KKM, DBKL, MPKj, LHDN, MyIPO, unknown",
  "topic":        "ONE OF: tax, licensing, zoning, employment, registration, compliance, unknown",
  "document_type":"ONE OF: act, guideline, form, fee_schedule, unknown"
}}

TEXT:
{chunk_text}"""

FALLBACK_METADATA = {
    "jurisdiction":  "unknown",
    "authority":     "unknown",
    "topic":         "unknown",
    "document_type": "unknown",
}


class _RateLimited(Exception):
    """Raised internally when Gemini returns 429, to trigger a retry."""


def is_fallback(node) -> bool:
    """True if enrichment failed and the node is stuck on all-unknown defaults."""
    return all(node.metadata.get(k) == v for k, v in FALLBACK_METADATA.items())


def _build_payload(chunk_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(chunk_text=chunk_text)
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",  # Gemini native JSON mode — forces valid JSON output
        },
    }


async def _request_metadata_once(payload: dict) -> dict:
    """
    Makes a single Gemini call and parses the result.
    Raises _RateLimited on HTTP 429 (caller decides whether to retry),
    or ValueError/KeyError if the response is missing expected fields.
    """
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(config.GEMINI_API_URL, json=payload)

    if resp.status_code == 429:
        raise _RateLimited()

    resp.raise_for_status()

    candidates = resp.json().get("candidates", [])
    if not candidates:
        raise ValueError("Empty candidates list in Gemini response")

    raw = candidates[0]["content"]["parts"][0]["text"]
    return extract_json(raw)


async def enrich_single_node_async(semaphore, node, index: int, total: int):
    """
    Calls Gemini 3.1 Flash Lite via the REST generateContent endpoint.
    Retries on 429 with exponential backoff.
    """
    async with semaphore:
        payload = _build_payload(node.text[:config.ENRICHMENT_CONTEXT_CHARS])

        for attempt in range(config.ENRICHMENT_MAX_RETRIES):
            try:
                extracted = await _request_metadata_once(payload)
            except _RateLimited:
                wait = 5 * (2 ** attempt)   # 5s → 10s → 20s
                log.warning(
                    f"  [{index + 1}/{total}] Rate limited — "
                    f"retrying in {wait}s (attempt {attempt + 1}/{config.ENRICHMENT_MAX_RETRIES})"
                )
                await asyncio.sleep(wait)
                continue
            except (ValueError, KeyError) as e:
                log.warning(
                    f"  [{index + 1}/{total}] JSON parse failed — "
                    f"using fallback. ({e})"
                )
                node.metadata.update(FALLBACK_METADATA)
                return False
            except Exception as e:
                log.error(f"  [{index + 1}/{total}] ERROR — {e}")
                node.metadata.update(FALLBACK_METADATA)
                return False
            else:
                node.metadata.update(extracted)
                log.info(f"  [{index + 1}/{total}] OK → {extracted}")
                return True

        # Exhausted all retries
        log.error(
            f"  [{index + 1}/{total}] Rate limited after {config.ENRICHMENT_MAX_RETRIES} retries — "
            f"using fallback."
        )
        node.metadata.update(FALLBACK_METADATA)
        return False