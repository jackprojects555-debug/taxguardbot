"""Tests for command_registry: parse_command, parse_income, is_unsupported_format."""

import pytest

from app.command_registry import is_unsupported_format, parse_command, parse_income

# ---------------------------------------------------------------------------
# Exact alias commands
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["מצב", "status", "STATUS", "Status"])
def test_status_aliases(text):
    assert parse_command(text) == ("status", {})


@pytest.mark.parametrize("text", ["רשימה", "list", "LIST"])
def test_list_aliases(text):
    assert parse_command(text) == ("list", {})


@pytest.mark.parametrize("text", ["אחרון", "last", "LAST"])
def test_last_aliases(text):
    assert parse_command(text) == ("last", {})


@pytest.mark.parametrize("text", ["עזרה", "help", "HELP"])
def test_help_aliases(text):
    assert parse_command(text) == ("help", {})


@pytest.mark.parametrize("text", ["בטל אחרון", "cancel last", "Cancel Last"])
def test_cancel_last_aliases(text):
    assert parse_command(text) == ("cancel_last", {})


@pytest.mark.parametrize("text", ["אפס", "נקה", "מחק", "reset", "clear", "delete", "RESET"])
def test_reset_aliases(text):
    assert parse_command(text) == ("reset", {})


@pytest.mark.parametrize("text", ["העברתי", "saved", "SAVED"])
def test_saved_no_amount(text):
    action, args = parse_command(text)
    assert action == "saved"
    assert args["amount_text"] == ""


# ---------------------------------------------------------------------------
# Parametric commands
# ---------------------------------------------------------------------------


def test_saved_with_hebrew_amount():
    action, args = parse_command("העברתי 4000")
    assert action == "saved"
    assert args["amount_text"] == "4000"


def test_saved_with_english_amount():
    action, args = parse_command("saved 4000")
    assert action == "saved"
    assert args["amount_text"] == "4000"


def test_cancel_by_id_hebrew():
    assert parse_command("בטל 3") == ("cancel_id", {"transaction_id": 3})


def test_cancel_by_id_english():
    assert parse_command("cancel 5") == ("cancel_id", {"transaction_id": 5})


def test_cancel_by_id_case_insensitive():
    assert parse_command("Cancel 2") == ("cancel_id", {"transaction_id": 2})


def test_fix_last_hebrew():
    assert parse_command("תקן אחרון 23400") == ("fix_last", {"amount_text": "23400"})


def test_fix_last_english():
    assert parse_command("fix last 23400") == ("fix_last", {"amount_text": "23400"})


def test_fix_last_case_insensitive():
    assert parse_command("Fix Last 23400") == ("fix_last", {"amount_text": "23400"})


def test_fix_by_id_hebrew():
    assert parse_command("תקן 2 23400") == (
        "fix_id",
        {"transaction_id": 2, "amount_text": "23400"},
    )


def test_fix_by_id_english():
    assert parse_command("fix 2 23400") == (
        "fix_id",
        {"transaction_id": 2, "amount_text": "23400"},
    )


# ---------------------------------------------------------------------------
# Income parsing via parse_command
# ---------------------------------------------------------------------------


def test_plain_number():
    action, args = parse_command("11700")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)
    assert args["vat_override"] is None


def test_number_with_commas():
    action, args = parse_command("11,700")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)


def test_number_with_shekel_sign():
    action, args = parse_command("₪11,700")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)


def test_decimal_amount():
    action, args = parse_command("5500.50")
    assert action == "income"
    assert args["amount"] == pytest.approx(5500.50)


def test_vat_excluded_hebrew_modifier():
    action, args = parse_command("11700 נוכה")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)
    assert args["vat_override"] is False


def test_vat_excluded_english_modifier():
    action, args = parse_command("11700 vat excluded")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)
    assert args["vat_override"] is False


def test_vat_excluded_novat_modifier():
    action, args = parse_command("11700 novat")
    assert action == "income"
    assert args["amount"] == pytest.approx(11700)
    assert args["vat_override"] is False


def test_shekel_with_vat_modifier():
    action, args = parse_command("₪5,000 נוכה")
    assert action == "income"
    assert args["amount"] == pytest.approx(5000)
    assert args["vat_override"] is False


# ---------------------------------------------------------------------------
# parse_income standalone
# ---------------------------------------------------------------------------


def test_parse_income_plain():
    assert parse_income("11700") == (11700.0, None)


def test_parse_income_negative_returns_none():
    assert parse_income("-100") is None


def test_parse_income_zero_returns_none():
    assert parse_income("0") is None


def test_parse_income_empty_returns_none():
    assert parse_income("") is None


def test_parse_income_text_returns_none():
    assert parse_income("hello") is None


def test_parse_income_k_suffix_returns_none():
    assert parse_income("11k") is None


# ---------------------------------------------------------------------------
# is_unsupported_format
# ---------------------------------------------------------------------------


def test_k_suffix_detected():
    assert is_unsupported_format("11k") is True
    assert is_unsupported_format("5K") is True


def test_plain_number_not_unsupported():
    assert is_unsupported_format("11700") is False


def test_text_not_unsupported():
    assert is_unsupported_format("hello") is False


# ---------------------------------------------------------------------------
# Unknown / unrecognised input
# ---------------------------------------------------------------------------


def test_unknown_text_returns_none():
    assert parse_command("blahblah") is None


def test_partial_command_returns_none():
    assert parse_command("בטל") is None


def test_empty_string_returns_none():
    assert parse_command("  ") is None
