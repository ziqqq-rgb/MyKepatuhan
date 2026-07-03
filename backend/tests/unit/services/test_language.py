"""
Uses real langdetect calls for unambiguous short sentences, and
monkeypatches `detect` directly for edge cases (exceptions, boundary
language codes) where relying on the real detector would be flaky.
"""
import pytest
from langdetect import LangDetectException

from services import language


def test_detects_english():
    assert language.detect_language("What is the corporate tax rate in Malaysia?") == "en"


def test_detects_malay():
    assert language.detect_language("Apa kadar cukai korporat di Malaysia?") == "ms"


@pytest.mark.parametrize("code", ["ms", "id"])
def test_malay_and_indonesian_codes_both_map_to_ms(monkeypatch, code):
    monkeypatch.setattr(language, "detect", lambda text: code)
    assert language.detect_language("some text") == "ms"


def test_non_malay_code_maps_to_en(monkeypatch):
    monkeypatch.setattr(language, "detect", lambda text: "fr")
    assert language.detect_language("un texte") == "en"


def test_detection_failure_falls_back_to_en(monkeypatch):
    def _raise(text):
        raise LangDetectException(1, "no features in text")

    monkeypatch.setattr(language, "detect", _raise)
    assert language.detect_language("") == "en"