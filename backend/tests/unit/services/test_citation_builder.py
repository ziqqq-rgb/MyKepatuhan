"""
Unit tests for services/citation_builder.py.

Uses SimpleNamespace to stand in for LlamaIndex's NodeWithScore —
we only need `.node.metadata`, `.node.text`, and `.score`, so a real
NodeWithScore would just add noise.
"""
from types import SimpleNamespace

from services.citation_builder import _truncate, build_citations


def _fake_source_node(text="some excerpt", score=0.9, metadata=None):
    node = SimpleNamespace(text=text, metadata=metadata or {})
    return SimpleNamespace(node=node, score=score)


class TestTruncate:
    def test_leaves_short_text_unchanged(self):
        assert _truncate("short text") == "short text"

    def test_truncates_long_text_with_ellipsis(self):
        text = "a" * 400
        result = _truncate(text, max_chars=300)
        assert result == "a" * 300 + "..."

    def test_respects_custom_max_chars(self):
        assert _truncate("hello world", max_chars=5) == "hello..."


class TestBuildCitations:
    def test_ranks_start_at_one_in_source_order(self):
        nodes = [_fake_source_node(), _fake_source_node(), _fake_source_node()]
        citations = build_citations(nodes)
        assert [c.rank for c in citations] == [1, 2, 3]

    def test_reads_metadata_fields(self):
        node = _fake_source_node(metadata={
            "authority": "SSM",
            "topic": "registration",
            "document_type": "act",
            "source_document": "Registration of Businesses Act 1956",
        })
        citation = build_citations([node])[0]

        assert citation.authority == "SSM"
        assert citation.topic == "registration"
        assert citation.document_type == "act"
        assert citation.document_title == "Registration of Businesses Act 1956"

    def test_missing_metadata_defaults_to_unknown(self):
        citation = build_citations([_fake_source_node(metadata={})])[0]

        assert citation.authority == "Unknown"
        assert citation.topic == "Unknown"
        assert citation.document_type == "Unknown"
        assert citation.document_title == "Unknown source"

    def test_score_rounds_to_four_decimal_places(self):
        citation = build_citations([_fake_source_node(score=0.123456789)])[0]
        assert citation.score == 0.1235

    def test_none_score_defaults_to_zero(self):
        citation = build_citations([_fake_source_node(score=None)])[0]
        assert citation.score == 0.0

    def test_excerpt_is_truncated(self):
        citation = build_citations([_fake_source_node(text="x" * 400)])[0]
        assert citation.excerpt == "x" * 300 + "..."