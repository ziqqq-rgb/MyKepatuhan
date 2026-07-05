"""
Detects small talk (greetings) so it short-circuits before the RAG pipeline.

Without this, a greeting like "hye" still gets sent through the RAG
pipeline: the retriever always returns top_k nodes (no similarity
cutoff), and the LLM — correctly following the QA prompt's own rule for
unrelated context — replies with the "I cannot find the answer..."
fallback. That fallback is meant for genuinely unrelated legal
questions, not greetings, so we handle greetings separately instead.
"""
import re

# Matches anything that isn't a letter/number/whitespace (commas, "!!",
# "-", etc.) so "Hye!!," and "hye" normalize to the same string.
_PUNCTUATION_RE = re.compile(r"[^\w\s]", re.UNICODE)

GREETING_PHRASES = {
    # --- English Casual/Standard ---
    "hi", "hii", "hiii", "hiiii", "hye", "hyee", "hyeee", "hey", "heyy", "heyyy", 
    "hello", "helo", "helllo", "hallo", "greetings", "good morning", "goodmorning", 
    "good afternoon", "goodafternoon", "good evening", "goodevening", "good night", 
    "goodnight", "morning", "afternoon", "evening", "sup", "what's up", "whats up", 
    "how are you", "how r u", "how ru", "how are ya", "hey there",
    
    # --- Malay Standard ---
    "salam", "hai", "haii", "haiii", "selamat pagi", "selamatpagi", 
    "selamat petang", "selamatpetang", "selamat tengah hari", "selamattengahhari", 
    "selamat malam", "selamatmalam", "apa khabar", "apakhabar", "apa kabar", 
    "apakabar", "salam sejahtera", "salamsejahtera",
    
    # --- Malaysian Colloquial/Informal ---
    "boss", "bos", "bang", "kak", "kakak", "dik", "tumpang tanya", "tumpan tanya",
    "slm", "salam 1malaysia", "salam 1 malaysia", "hai bos", "hello bos", 
    "selamat tengahari", "selamattengahari"
}

_GREETING_RESPONSES = {
    "en": "Hi! I'm your Malaysian compliance assistant. What can I help today? ",
    "ms": "Hai! Saya pembantu pematuhan perundangan Malaysia. Ada apa yang boleh saya bantu hari ini?",
}


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse repeated whitespace.
    'Hye!!,  ' and 'hye' both become 'hye' so phrase lookup is exact."""
    no_punctuation = _PUNCTUATION_RE.sub(" ", text.lower())
    return " ".join(no_punctuation.split())


def is_greeting(text: str) -> bool:
    """True only for a pure greeting with no other content, e.g. 'hye' or
    'good morning!'. A greeting attached to a real question ('hye, license
    for a restaurant?') returns False so the question still reaches RAG."""
    return _normalize(text) in GREETING_PHRASES


def greeting_response(language: str) -> str:
    return _GREETING_RESPONSES.get(language, _GREETING_RESPONSES["en"])