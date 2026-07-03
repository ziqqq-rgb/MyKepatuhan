"""
Nodes are stood in with SimpleNamespace since stage_sanitize only
ever touches `.metadata`.
"""
import json
from types import SimpleNamespace

from core import config
from pipeline.ingestion.sanitize import stage_sanitize


def _node(metadata: dict):
    return SimpleNamespace(metadata=metadata)


def test_drops_keys_marked_for_removal():
    node = _node({"doc_items": [1, 2, 3], "authority": "SSM"})
    result = stage_sanitize([node])[0]
    assert "doc_items" not in result.metadata
    assert result.metadata["authority"] == "SSM"


def test_stringifies_dict_values():
    node = _node({"nested": {"a": 1}})
    result = stage_sanitize([node])[0]
    assert result.metadata["nested"] == json.dumps({"a": 1})


def test_stringifies_list_values():
    node = _node({"tags": ["a", "b"]})
    result = stage_sanitize([node])[0]
    assert result.metadata["tags"] == json.dumps(["a", "b"])


def test_none_becomes_empty_string():
    node = _node({"page": None})
    result = stage_sanitize([node])[0]
    assert result.metadata["page"] == ""


def test_long_string_is_truncated_with_suffix():
    node = _node({"blob": "x" * (config.SANITIZE_MAX_STRING_LENGTH + 100)})
    result = stage_sanitize([node])[0]
    assert result.metadata["blob"] == "x" * config.SANITIZE_MAX_STRING_LENGTH + "...[TRUNCATED]"


def test_short_string_is_left_untouched():
    node = _node({"authority": "SSM"})
    result = stage_sanitize([node])[0]
    assert result.metadata["authority"] == "SSM"


def test_processes_multiple_nodes_independently():
    nodes = [_node({"authority": "SSM"}), _node({"authority": "KKM"})]
    result = stage_sanitize(nodes)
    assert [n.metadata["authority"] for n in result] == ["SSM", "KKM"]