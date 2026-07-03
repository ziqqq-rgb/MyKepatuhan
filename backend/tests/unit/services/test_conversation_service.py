"""
Unit tests for services/conversation_service.py.

build_history_prompt and _truncate_title are pure functions and are
tested directly. record_turn touches a db Session, so it's exercised
with a minimal fake session that just tracks add()/commit() calls —
a real SQLAlchemy session isn't needed to verify the title-setting logic.
"""
from types import SimpleNamespace

from core import config
from services.conversation_service import _truncate_title, build_history_prompt, record_turn


def _message(role, content):
    return SimpleNamespace(role=role, content=content)


class _FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commits += 1


class TestBuildHistoryPrompt:
    def test_empty_history_returns_empty_string(self):
        assert build_history_prompt([]) == ""

    def test_formats_role_and_content(self):
        messages = [_message("user", "Hi"), _message("assistant", "Hello")]
        assert build_history_prompt(messages) == "User: Hi\nAssistant: Hello"

    def test_keeps_only_the_last_n_turns(self):
        messages = [_message("user", f"msg-{i}") for i in range(config.CHAT_HISTORY_TURNS * 2 + 4)]
        result = build_history_prompt(messages)
        assert "msg-0" not in result
        assert f"msg-{len(messages) - 1}" in result


class TestTruncateTitle:
    def test_short_text_is_unchanged(self):
        assert _truncate_title("What is the tax rate?") == "What is the tax rate?"

    def test_collapses_newlines(self):
        assert _truncate_title("What is\nthe tax rate?") == "What is the tax rate?"

    def test_long_text_is_truncated_with_ellipsis(self):
        result = _truncate_title("a" * 100, max_len=60)
        assert result == "a" * 60 + "..."
        assert len(result) == 63


class TestRecordTurn:
    def test_sets_title_from_question_on_first_turn(self):
        db = _FakeSession()
        conversation = SimpleNamespace(id="conv-1", title="New conversation")

        record_turn(db, conversation, "What is the tax rate?", "It's 24%.")

        assert conversation.title == "What is the tax rate?"
        assert db.commits >= 1

    def test_does_not_overwrite_title_on_later_turns(self):
        db = _FakeSession()
        conversation = SimpleNamespace(id="conv-1", title="Tax rate question")

        record_turn(db, conversation, "And for SMEs?", "17% for the first 150k.")

        assert conversation.title == "Tax rate question"

    def test_saves_both_user_and_assistant_messages(self):
        db = _FakeSession()
        conversation = SimpleNamespace(id="conv-1", title="New conversation")

        record_turn(db, conversation, "Question", "Answer")

        assert [m.role for m in db.added] == ["user", "assistant"]