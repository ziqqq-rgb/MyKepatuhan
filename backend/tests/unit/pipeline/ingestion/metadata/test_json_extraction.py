"""
Unit tests for pipeline/ingestion/metadata/json_extraction.py.

Pure function, no I/O, no mocks needed — just feed it strings and
check what comes back.
"""
import pytest

from pipeline.ingestion.metadata.json_extraction import extract_json


def test_parses_clean_json_directly():
    result = extract_json('{"a": 1, "b": "two"}')
    assert result == {"a": 1, "b": "two"}


def test_strips_json_labeled_markdown_fence():
    raw = '```json\n{"a": 1}\n```'
    assert extract_json(raw) == {"a": 1}


def test_strips_bare_markdown_fence():
    raw = '```\n{"a": 1}\n```'
    assert extract_json(raw) == {"a": 1}


def test_regex_fallback_extracts_object_from_surrounding_text():
    raw = 'Sure, here is the metadata: {"a": 1} — hope that helps!'
    assert extract_json(raw) == {"a": 1}


def test_raises_value_error_when_no_json_present():
    with pytest.raises(ValueError, match="No valid JSON found"):
        extract_json("this is not json at all")


def test_error_message_truncates_long_raw_input():
    raw = "x" * 500
    with pytest.raises(ValueError) as exc_info:
        extract_json(raw)
    # Guards the `raw[:200]` slice in the error message — a huge model
    # response shouldn't blow up log lines.
    assert len(str(exc_info.value)) < 300