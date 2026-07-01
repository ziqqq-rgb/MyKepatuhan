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
    Parse JSON from model response robustly:
    1. Direct parse
    2. Strip markdown fences then parse
    3. Regex extract first {...} block
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    stripped = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {raw[:200]}")