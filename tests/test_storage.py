"""Tests for transaction storage (SQLite-backed)."""

from datetime import datetime

import pytest

from app.models import Transaction
from app.storage import (
    add_transaction,
    clear_transactions,
    get_transaction_by_id,
    get_transactions,
    list_user_ids_with_transactions,
    update_transaction,
)

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
# add_transaction — ID assignment
# ---------------------------------------------------------------------------


def test_add_transaction_assigns_id_starting_at_one():
    t = add_transaction(1, _make_transaction())
    assert t.id == 1


def test_add_transaction_increments_id():
    t1 = add_transaction(1, _make_transaction())
    t2 = add_transaction(1, _make_transaction())
    assert t1.id == 1
    assert t2.id == 2


def test_add_transaction_ids_independent_per_user():
    t_u1 = add_transaction(1, _make_transaction())
    t_u2 = add_transaction(2, _make_transaction())
    assert t_u1.id == 1
    assert t_u2.id == 1


def test_add_transaction_persists():
    add_transaction(1, _make_transaction(amount=9000.0))
    rows = get_transactions(1)
    assert len(rows) == 1
    assert rows[0].amount == pytest.approx(9000.0)


def test_add_transaction_preserves_fields():
    ts = datetime(2026, 5, 12, 10, 0, 0)
    t = add_transaction(
        1,
        _make_transaction(
            amount=5000.0,
            vat_included=False,
            status="open",
            saved_amount=0.0,
            month="2026-05",
            created_at=ts,
        ),
    )
    fetched = get_transaction_by_id(1, t.id)
    assert fetched.amount == pytest.approx(5000.0)
    assert fetched.vat_included is False
    assert fetched.month == "2026-05"
    assert fetched.created_at == ts


# ---------------------------------------------------------------------------
# get_transactions
# ---------------------------------------------------------------------------


def test_get_transactions_empty():
    assert get_transactions(1) == []


def test_get_transactions_ordered_by_id():
    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(1, _make_transaction(amount=2000.0))
    rows = get_transactions(1)
    assert rows[0].id == 1
    assert rows[1].id == 2


def test_get_transactions_isolated_per_user():
    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(2, _make_transaction(amount=2000.0))
    assert len(get_transactions(1)) == 1
    assert get_transactions(1)[0].amount == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# get_transaction_by_id
# ---------------------------------------------------------------------------


def test_get_transaction_by_id_finds_correct():
    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(1, _make_transaction(amount=2000.0))
    t = get_transaction_by_id(1, 2)
    assert t is not None
    assert t.amount == pytest.approx(2000.0)


def test_get_transaction_by_id_returns_none_for_missing():
    add_transaction(1, _make_transaction())
    assert get_transaction_by_id(1, 99) is None


def test_get_transaction_by_id_returns_none_for_unknown_user():
    assert get_transaction_by_id(999, 1) is None


# ---------------------------------------------------------------------------
# update_transaction
# ---------------------------------------------------------------------------


def test_update_transaction_updates_status():
    add_transaction(1, _make_transaction())
    update_transaction(1, 1, status="fully_saved")
    assert get_transaction_by_id(1, 1).status == "fully_saved"


def test_update_transaction_updates_saved_and_remaining():
    add_transaction(1, _make_transaction())
    update_transaction(1, 1, saved_amount=2000.0, remaining_amount=3000.0, status="partially_saved")
    t = get_transaction_by_id(1, 1)
    assert t.saved_amount == pytest.approx(2000.0)
    assert t.remaining_amount == pytest.approx(3000.0)
    assert t.status == "partially_saved"


def test_update_transaction_returns_none_for_missing():
    assert update_transaction(1, 99, status="fully_saved") is None


def test_update_transaction_returns_updated_transaction():
    add_transaction(1, _make_transaction())
    result = update_transaction(1, 1, status="fully_saved")
    assert result is not None
    assert result.status == "fully_saved"


def test_update_transaction_ignores_unknown_fields():
    add_transaction(1, _make_transaction())
    result = update_transaction(1, 1, nonexistent_field="value")
    assert result is not None


def test_update_transaction_preserves_datetime():
    ts = datetime(2026, 5, 13, 9, 0, 0)
    add_transaction(1, _make_transaction())
    update_transaction(1, 1, updated_at=ts)
    assert get_transaction_by_id(1, 1).updated_at == ts


# ---------------------------------------------------------------------------
# clear_transactions / list_user_ids_with_transactions
# ---------------------------------------------------------------------------


def test_clear_transactions_removes_all_for_user():
    add_transaction(1, _make_transaction())
    add_transaction(1, _make_transaction())
    clear_transactions(1)
    assert get_transactions(1) == []


def test_clear_transactions_does_not_affect_other_users():
    add_transaction(1, _make_transaction())
    add_transaction(2, _make_transaction())
    clear_transactions(1)
    assert len(get_transactions(2)) == 1


def test_list_user_ids_with_transactions():
    add_transaction(3, _make_transaction())
    add_transaction(7, _make_transaction())
    ids = list_user_ids_with_transactions()
    assert 3 in ids
    assert 7 in ids


def test_list_user_ids_empty():
    assert list_user_ids_with_transactions() == []
