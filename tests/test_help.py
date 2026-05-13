"""Tests for help message content and language selection."""

from app.message_store import format_message


def test_help_he_contains_key_commands():
    msg = format_message("help_he")
    assert "מצב" in msg
    assert "העברתי" in msg
    assert "עזרה" in msg
    assert "בטל" in msg
    assert "תקן" in msg


def test_help_en_contains_key_commands():
    msg = format_message("help_en")
    assert "status" in msg
    assert "saved" in msg
    assert "help" in msg
    assert "cancel" in msg
    assert "fix" in msg


def test_help_he_is_nonempty():
    assert len(format_message("help_he")) > 50


def test_help_en_is_nonempty():
    assert len(format_message("help_en")) > 50


def test_help_he_and_en_are_different():
    assert format_message("help_he") != format_message("help_en")
