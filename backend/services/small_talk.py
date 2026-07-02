"""
Detects small talk (greetings) so it short-circuits before retrieval.

Without this, a greeting like "hye" still gets sent through the RAG
pipeline: the retriever always returns top_k nodes (no similarity
cutoff), and the LLM — correctly following the QA prompt's own rule for
unrelated context — replies with the "I cannot find the answer..."
fallback. That fallback is meant for genuinely unrelated legal
questions, not greetings, so we handle greetings separately instead.
"""
import re

# Matches a leading greeting word plus any trailing punctuation/comma,
# e.g. "hye," or "hello!!" or "selamat pagi -". Used two ways below:
#   - if nothing is left after stripping it, the message IS the greeting
#   - if something is left ("hye, license for restaurant?"), we leave the
#     message untouched and let it flow into RAG as a normal question
_GREETING_PREFIX = re.compile(
    r"^\s*(hi|hye|hyee|hyeee|hey|hello|helo|yo|salam|selamat pagi|selamat petang|"
    r"selamat tengah hari|apa khabar|good morning|good evening|good afternoon)"
    r"[\s,!.?-]*",
    re.IGNORECASE,
)

_GREETING_RESPONSES = {
    "en": (
        "Hi! I'm your Malaysian compliance assistant. What can I help today? "
    ),
    "ms": (
        "Hai! Saya pembantu pematuhan perundangan Malaysia. Ada apa yang boleh saya bantu hari ini?"

    ),
}


def is_greeting(text: str) -> bool:
    """True only for a pure greeting with no other content, e.g. 'hye' or
    'good morning!'. A greeting attached to a real question ('hye, license
    for a restaurant?') returns False so the question still reaches RAG."""
    stripped = text.strip()
    if not _GREETING_PREFIX.match(stripped):
        return False
    remainder = _GREETING_PREFIX.sub("", stripped, count=1)
    return not remainder.strip()


def greeting_response(language: str) -> str:
    return _GREETING_RESPONSES.get(language, _GREETING_RESPONSES["en"])