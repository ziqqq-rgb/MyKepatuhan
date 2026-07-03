"""
Unit tests for pipeline/ingestion/checkpointing.py.

checkpointing.py resolves CHECKPOINT_DIR, UPLOADED_LOG, and
HASH_REGISTRY once, at import time. The `isolated_checkpoint_dir`
fixture below redirects all three into a per-test tmp_path so tests
never touch the real .checkpoints/ directory in the repo and never
leak state between tests.
"""
import pytest

from pipeline.ingestion import checkpointing as ckpt


@pytest.fixture
def isolated_checkpoint_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(ckpt, "CHECKPOINT_DIR", tmp_path)
    monkeypatch.setattr(ckpt, "UPLOADED_LOG", tmp_path / "uploaded_docs.json")
    monkeypatch.setattr(ckpt, "HASH_REGISTRY", tmp_path / "hash_registry.json")
    return tmp_path


class TestSaveLoadCheckpoint:
    def test_round_trip_returns_same_data(self, isolated_checkpoint_dir):
        ckpt.save_checkpoint("nodes_raw", "act-1956", {"nodes": [1, 2, 3]})

        assert ckpt.checkpoint_exists("nodes_raw", "act-1956")
        assert ckpt.load_checkpoint("nodes_raw", "act-1956") == {"nodes": [1, 2, 3]}

    def test_missing_checkpoint_returns_none(self, isolated_checkpoint_dir):
        assert ckpt.load_checkpoint("nodes_raw", "does-not-exist") is None

    def test_path_sanitizes_slashes_in_doc_name(self, isolated_checkpoint_dir):
        path = ckpt.checkpoint_path("nodes_raw", "folder/doc\\name")
        assert "/" not in path.name
        assert "\\" not in path.name


class TestUploadedLog:
    def test_starts_empty(self, isolated_checkpoint_dir):
        assert ckpt.load_uploaded_log() == set()

    def test_tracks_multiple_doc_names(self, isolated_checkpoint_dir):
        ckpt.mark_as_uploaded("act-1956")
        ckpt.mark_as_uploaded("act-1967")

        assert ckpt.load_uploaded_log() == {"act-1956", "act-1967"}


class TestDuplicateDetection:
    """
    is_duplicate() checks file *content* hash, not filename — two files
    with different names but identical bytes should be flagged as dupes.
    """

    def test_flags_identical_content_under_different_filenames(
        self, isolated_checkpoint_dir, tmp_path
    ):
        file_a = tmp_path / "a.pdf"
        file_b = tmp_path / "b.pdf"
        file_a.write_bytes(b"%PDF-1.4 same content")
        file_b.write_bytes(b"%PDF-1.4 same content")

        is_dup, file_hash = ckpt.is_duplicate(str(file_a))
        assert is_dup is False  # first time this hash is seen
        ckpt.register_document(str(file_a), "doc-a", file_hash)

        is_dup, dup_hash = ckpt.is_duplicate(str(file_b))
        assert is_dup is True
        assert dup_hash == file_hash

    def test_does_not_flag_different_content(self, isolated_checkpoint_dir, tmp_path):
        file_a = tmp_path / "a.pdf"
        file_c = tmp_path / "c.pdf"
        file_a.write_bytes(b"%PDF-1.4 content one")
        file_c.write_bytes(b"%PDF-1.4 completely different content")

        _, hash_a = ckpt.is_duplicate(str(file_a))
        ckpt.register_document(str(file_a), "doc-a", hash_a)

        is_dup, _ = ckpt.is_duplicate(str(file_c))
        assert is_dup is False