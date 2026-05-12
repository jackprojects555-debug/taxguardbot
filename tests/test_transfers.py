"""Tests for transfer confirmation logic."""

from datetime import datetime

import pytest

from app.models import Transaction
from app.storage import add_transaction, get_transaction_by_id
from app.transfers import _parse_transfer_amount, process_transfer

NOW = datetime(2026, 5, 12, 10, 0, 0)


def _make_transaction(**overrides) -> Transaction:
    defaults = dict(
        amount=11700.0,
        vat_included=True,
        vat_amount=1700.0,
        base_amount=10000.0,
        income_tax_amount=2000.0,
        national_insurance_amount=800.0,
        social_savings_amount=500.0,
        total_to_save=5000.0,
        remaining_amount=5000.0,
        available_amount=6700.0,
        month="2026-05",
        created_at=NOW,
    )
    defaults.update(overrides)
    return Transaction(**defaults)


# ---------------------------------------------------------------------------
# _parse_transfer_amount
# ---------------------------------------------------------------------------


def test_parse_amount_integer():
    assert _parse_transfer_amount("4000") == pytest.approx(4000.0)


def test_parse_amount_with_comma():
    assert _parse_transfer_amount("4,000") == pytest.approx(4000.0)


def test_parse_amount_with_shekel():
    assert _parse_transfer_amount("₪4000") == pytest.approx(4000.0)


def test_parse_amount_decimal():
    assert _parse_transfer_amount("1500.50") == pytest.approx(1500.50)


def test_parse_amount_zero_returns_none():
    assert _parse_transfer_amount("0") is None


def test_parse_amount_negative_returns_none():
    assert _parse_transfer_amount("-100") is None


def test_parse_amount_non_numeric_returns_none():
    assert _parse_transfer_amount("abc") is None


def test_parse_amount_empty_returns_none():
    assert _parse_transfer_amount("") is None


# ---------------------------------------------------------------------------
# process_transfer — full transfer
# ---------------------------------------------------------------------------


def test_full_transfer_marks_fully_saved(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "")

    t = get_transaction_by_id(1, 1)
    assert t.status == "fully_saved"
    assert t.saved_amount == pytest.approx(5000.0)
    assert t.remaining_amount == pytest.approx(0.0)


def test_full_transfer_returns_success_message(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    reply = process_transfer(1, "")
    assert "5,000" in reply
    assert "נסגרה" in reply


def test_full_transfer_sets_updated_at(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "")

    t = get_transaction_by_id(1, 1)
    assert t.updated_at is not None


# ---------------------------------------------------------------------------
# process_transfer — partial transfer
# ---------------------------------------------------------------------------


def test_partial_transfer_updates_saved_and_remaining(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "2000")

    t = get_transaction_by_id(1, 1)
    assert t.status == "partially_saved"
    assert t.saved_amount == pytest.approx(2000.0)
    assert t.remaining_amount == pytest.approx(3000.0)


def test_partial_transfer_returns_partial_message(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    reply = process_transfer(1, "2000")
    assert "2,000" in reply
    assert "3,000" in reply


def test_partial_transfer_accumulates_on_second_call(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "2000")
    process_transfer(1, "2000")

    t = get_transaction_by_id(1, 1)
    assert t.saved_amount == pytest.approx(4000.0)
    assert t.remaining_amount == pytest.approx(1000.0)
    assert t.status == "partially_saved"


def test_second_transfer_completes_transaction(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "3000")
    process_transfer(1, "2000")

    t = get_transaction_by_id(1, 1)
    assert t.status == "fully_saved"
    assert t.remaining_amount == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# process_transfer — amount capping
# ---------------------------------------------------------------------------


def test_amount_exceeding_remaining_is_capped(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    process_transfer(1, "9999")

    t = get_transaction_by_id(1, 1)
    assert t.status == "fully_saved"
    assert t.saved_amount == pytest.approx(5000.0)
    assert t.remaining_amount == pytest.approx(0.0)


def test_capped_transfer_reports_actual_amount(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    reply = process_transfer(1, "9999")
    assert "5,000" in reply
    assert "נסגרה" in reply


# ---------------------------------------------------------------------------
# process_transfer — targets most recent open transaction
# ---------------------------------------------------------------------------


def test_targets_most_recent_open(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(
        1, _make_transaction(amount=1000.0, total_to_save=200.0, remaining_amount=200.0)
    )
    add_transaction(
        1, _make_transaction(amount=5000.0, total_to_save=1000.0, remaining_amount=1000.0)
    )

    process_transfer(1, "")

    t1 = get_transaction_by_id(1, 1)
    t2 = get_transaction_by_id(1, 2)
    assert t1.status == "open"      # untouched
    assert t2.status == "fully_saved"


def test_skips_fully_saved_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(total_to_save=5000.0, remaining_amount=5000.0))
    add_transaction(1, _make_transaction(total_to_save=3000.0, remaining_amount=3000.0))

    # Close second transaction
    process_transfer(1, "")

    # Now only first should be targeted
    process_transfer(1, "")
    t1 = get_transaction_by_id(1, 1)
    assert t1.status == "fully_saved"


# ---------------------------------------------------------------------------
# process_transfer — error cases
# ---------------------------------------------------------------------------


def test_no_open_transactions_returns_message(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = process_transfer(1, "")
    assert "אין" in reply


def test_invalid_amount_returns_message(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    reply = process_transfer(1, "abc")
    assert "לא תקין" in reply

    # Transaction unchanged
    t = get_transaction_by_id(1, 1)
    assert t.status == "open"
