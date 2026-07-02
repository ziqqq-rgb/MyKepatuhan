"""
Lightweight language detection (English vs Bahasa Melayu).

Used for two things:
1. Picking which canned response to use for small talk (greetings).
2. Telling the LLM explicitly which language to answer in — relying on it
   to infer "same language as the query" from a Malay-heavy context has
   proven unreliable, so we detect it ourselves and state it directly.
"""
from langdetect import detect, LangDetectException


_MALAY_CODES = {"ms", "id"}



def detect_language(text: str) -> str:
    try:
        code = detect(text)
    except LangDetectException:
        return "en"
    return "ms" if code in _MALAY_CODES else "en"