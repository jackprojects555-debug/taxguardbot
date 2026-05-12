"""Tests for correction commands: show_last, show_list, cancel, correct."""

from datetime import datetime

import pytest

from app.corrections import (
    cancel_by_id,
    cancel_last,
    correct_by_id,
    correct_last,
    show_last,
    show_list,
)
from app.models import Transaction
from app.storage import add_transaction, get_transaction_by_id
from app.user_storage import BotUser

CURRENT_MONTH = datetime.now().strftime("%Y-%m")
NOW = datetime(2026, 5, 12, 10, 0, 0)

TEST_USER = BotUser(
    telegram_user_id=1,
    income_tax_rate=0.20,
    national_insurance_rate=0.08,
    social_savings_rate=0.05,
    onboarding_completed=True,
)


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
        month=CURRENT_MONTH,
        created_at=NOW,
    )
    defaults.update(overrides)
    return Transaction(**defaults)


# ---------------------------------------------------------------------------
# show_last
# ---------------------------------------------------------------------------


def test_show_last_no_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = show_last(1)
    assert "אין" in reply


def test_show_last_returns_transaction_details(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=11700.0))
    reply = show_last(1)
    assert "11,700" in reply
    assert "#1" in reply


def test_show_last_skips_canceled(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=5000.0))
    add_transaction(1, _make_transaction(amount=9000.0, status="canceled"))

    reply = show_last(1)
    assert "5,000" in reply
    assert "9,000" not in reply


def test_show_last_all_canceled_returns_no_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(status="canceled"))
    reply = show_last(1)
    assert "אין" in reply


# ---------------------------------------------------------------------------
# show_list
# ---------------------------------------------------------------------------


def test_show_list_no_transactions_this_month(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    # Transaction from a past month
    add_transaction(1, _make_transaction(month="2020-01"))
    reply = show_list(1)
    assert "אין" in reply


def test_show_list_shows_current_month(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=11700.0))
    reply = show_list(1)
    assert "11,700" in reply
    assert "#1" in reply


def test_show_list_excludes_other_months(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=5000.0, month="2020-01"))
    add_transaction(1, _make_transaction(amount=9000.0))  # current month

    reply = show_list(1)
    assert "9,000" in reply
    assert "5,000" not in reply


def test_show_list_caps_at_five(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    for i in range(7):
        add_transaction(1, _make_transaction(amount=float(1000 + i * 100)))

    reply = show_list(1)
    # Only last 5 — first two should not appear (#1 = 1000, #2 = 1100)
    assert "#1" not in reply
    assert "#2" not in reply
    assert "#7" in reply


def test_show_list_most_recent_first(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(1, _make_transaction(amount=2000.0))

    reply = show_list(1)
    assert reply.index("#2") < reply.index("#1")


# ---------------------------------------------------------------------------
# cancel_by_id
# ---------------------------------------------------------------------------


def test_cancel_by_id_marks_canceled(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    cancel_by_id(1, 1)

    assert get_transaction_by_id(1, 1).status == "canceled"


def test_cancel_by_id_sets_canceled_at(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    cancel_by_id(1, 1)

    assert get_transaction_by_id(1, 1).canceled_at is not None


def test_cancel_by_id_not_found(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = cancel_by_id(1, 99)
    assert "לא נמצאה" in reply


def test_cancel_by_id_already_canceled(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(status="canceled"))
    reply = cancel_by_id(1, 1)
    assert "כבר בוטלה" in reply


# ---------------------------------------------------------------------------
# cancel_last
# ---------------------------------------------------------------------------


def test_cancel_last_targets_most_recent_non_canceled(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(1, _make_transaction(amount=2000.0))

    cancel_last(1)

    assert get_transaction_by_id(1, 1).status == "open"
    assert get_transaction_by_id(1, 2).status == "canceled"


def test_cancel_last_no_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = cancel_last(1)
    assert "אין" in reply


# ---------------------------------------------------------------------------
# correct_by_id
# ---------------------------------------------------------------------------


def test_correct_by_id_recalculates_amounts(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=11700.0))
    correct_by_id(1, 1, "23400", TEST_USER)

    t = get_transaction_by_id(1, 1)
    assert t.amount == pytest.approx(23400.0)
    assert t.vat_amount == pytest.approx(23400 * 17 / 117)
    assert t.total_to_save > 0


def test_correct_by_id_resets_saved_amount(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(saved_amount=3000.0, status="partially_saved"))
    correct_by_id(1, 1, "11700", TEST_USER)

    t = get_transaction_by_id(1, 1)
    assert t.saved_amount == pytest.approx(0.0)
    assert t.status == "open"


def test_correct_by_id_remaining_equals_new_total_to_save(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    correct_by_id(1, 1, "11700", TEST_USER)

    t = get_transaction_by_id(1, 1)
    assert t.remaining_amount == pytest.approx(t.total_to_save)


def test_correct_by_id_not_found(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = correct_by_id(1, 99, "5000", TEST_USER)
    assert "לא נמצאה" in reply


def test_correct_by_id_canceled_transaction(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(status="canceled"))
    reply = correct_by_id(1, 1, "5000", TEST_USER)
    assert "מבוטלת" in reply


def test_correct_by_id_invalid_amount(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    reply = correct_by_id(1, 1, "abc", TEST_USER)
    assert "לא תקין" in reply

    # Transaction unchanged
    assert get_transaction_by_id(1, 1).amount == pytest.approx(11700.0)


def test_correct_by_id_uses_user_rates(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(vat_included=False))

    high_rate_user = BotUser(
        telegram_user_id=1,
        income_tax_rate=0.30,
        national_insurance_rate=0.10,
        social_savings_rate=0.05,
        onboarding_completed=True,
    )
    correct_by_id(1, 1, "10000", high_rate_user)

    t = get_transaction_by_id(1, 1)
    assert t.income_tax_amount == pytest.approx(10000 * 0.30)
    assert t.national_insurance_amount == pytest.approx(10000 * 0.10)


# ---------------------------------------------------------------------------
# correct_last
# ---------------------------------------------------------------------------


def test_correct_last_targets_most_recent_non_canceled(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=5000.0))
    add_transaction(1, _make_transaction(amount=9000.0))

    correct_last(1, "20000", TEST_USER)

    assert get_transaction_by_id(1, 1).amount == pytest.approx(5000.0)  # untouched
    assert get_transaction_by_id(1, 2).amount == pytest.approx(20000.0)


def test_correct_last_no_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    reply = correct_last(1, "5000", TEST_USER)
    assert "אין" in reply
