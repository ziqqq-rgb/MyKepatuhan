"""
Builds the enrichment prompt and Gemini request payload.
Pure functions only, no I/O — easy to unit test in isolation.
"""
from core import config

_PROMPT_TEMPLATE = """\
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


def build_enrichment_payload(chunk_text: str) -> dict:
    """Returns the Gemini generateContent request body for one chunk."""
    prompt = _PROMPT_TEMPLATE.format(chunk_text=chunk_text[:config.ENRICHMENT_CONTEXT_CHARS])
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }