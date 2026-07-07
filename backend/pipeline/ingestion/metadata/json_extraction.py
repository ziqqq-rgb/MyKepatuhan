"""
Robust JSON extraction from LLM responses.

Since the Gemini calls use responseMimeType=application/json, the
direct parse below should almost always succeed — the markdown-fence
and regex fallbacks exist purely as a safety net for malformed output.
"""
import json
import re


def extract_json(raw: str) -> dict:
    """
    Parse a JSON object from model response text.

    Tries, in order: direct parse, markdown-fence-stripped parse, regex
    extraction of the first {...} block. Raises ValueError if none of
    these yields a dict — this also catches the case where the model
    returns valid but wrongly-shaped JSON (e.g. a list of values instead
    of a {"key": "value"} object), which parses fine but isn't usable
    metadata.
    """
    for candidate in _attempt_parses(raw):
        if isinstance(candidate, dict):
            return candidate

    raise ValueError(f"No valid JSON object found in response: {raw[:200]}")


def _attempt_parses(raw: str):
    """Yields each parse attempt's result (any JSON type), valid or not —
    extract_json filters for dict-shaped ones."""
    try:
        yield json.loads(raw)
    except json.JSONDecodeError:
        pass

    stripped = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        yield json.loads(stripped)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
    if match:
        try:
            yield json.loads(match.group())
        except json.JSONDecodeError:
            pass