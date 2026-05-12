"""Tests for Transaction model, storage serialization, and backward compatibility."""

import json
from datetime import datetime

import pytest

from app.models import Transaction
from app.storage import (
    _dict_to_transaction,
    _transaction_to_dict,
    add_transaction,
    get_transaction_by_id,
    get_transactions,
    update_transaction,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
# Backward compatibility — old records without new fields
# ---------------------------------------------------------------------------

OLD_FORMAT_RECORD = {
    "amount": 11700.0,
    "vat_included": True,
    "vat_amount": 1700.0,
    "base_amount": 10000.0,
    "income_tax_amount": 2000.0,
    "national_insurance_amount": 800.0,
    "social_savings_amount": 500.0,
    "total_to_save": 5000.0,
    "available_amount": 6700.0,
    "created_at": "2026-01-15T10:00:00",
}


def test_old_record_loads_without_error():
    t = _dict_to_transaction(OLD_FORMAT_RECORD, fallback_id=1)
    assert t.amount == pytest.approx(11700.0)


def test_old_record_status_defaults_open():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.status == "open"


def test_old_record_saved_amount_defaults_zero():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.saved_amount == pytest.approx(0.0)


def test_old_record_remaining_amount_defaults_to_total_to_save():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.remaining_amount == pytest.approx(5000.0)


def test_old_record_month_derived_from_created_at():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.month == "2026-01"


def test_old_record_id_uses_fallback():
    t = _dict_to_transaction(OLD_FORMAT_RECORD, fallback_id=3)
    assert t.id == 3


def test_old_record_updated_at_defaults_none():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.updated_at is None


def test_old_record_canceled_at_defaults_none():
    t = _dict_to_transaction(OLD_FORMAT_RECORD)
    assert t.canceled_at is None


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


def test_round_trip_preserves_status():
    t = _make_transaction(status="partially_saved")
    assert _dict_to_transaction(_transaction_to_dict(t)).status == "partially_saved"


def test_round_trip_preserves_saved_amount():
    t = _make_transaction(saved_amount=2000.0)
    assert _dict_to_transaction(_transaction_to_dict(t)).saved_amount == pytest.approx(2000.0)


def test_round_trip_preserves_remaining_amount():
    t = _make_transaction(remaining_amount=3000.0)
    assert _dict_to_transaction(_transaction_to_dict(t)).remaining_amount == pytest.approx(3000.0)


def test_round_trip_preserves_month():
    t = _make_transaction(month="2026-03")
    assert _dict_to_transaction(_transaction_to_dict(t)).month == "2026-03"


def test_round_trip_preserves_id():
    t = _make_transaction()
    t.id = 7
    assert _dict_to_transaction(_transaction_to_dict(t)).id == 7


def test_round_trip_preserves_updated_at():
    ts = datetime(2026, 5, 13, 9, 0, 0)
    t = _make_transaction(updated_at=ts)
    reloaded = _dict_to_transaction(_transaction_to_dict(t))
    assert reloaded.updated_at == ts


def test_round_trip_preserves_canceled_at():
    ts = datetime(2026, 5, 14, 12, 0, 0)
    t = _make_transaction(canceled_at=ts)
    reloaded = _dict_to_transaction(_transaction_to_dict(t))
    assert reloaded.canceled_at == ts


def test_round_trip_none_updated_at():
    t = _make_transaction(updated_at=None)
    assert _dict_to_transaction(_transaction_to_dict(t)).updated_at is None


# ---------------------------------------------------------------------------
# add_transaction — ID assignment
# ---------------------------------------------------------------------------


def test_add_transaction_assigns_id_starting_at_one(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    t = add_transaction(1, _make_transaction())
    assert t.id == 1


def test_add_transaction_increments_id(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    t1 = add_transaction(1, _make_transaction())
    t2 = add_transaction(1, _make_transaction())
    assert t1.id == 1
    assert t2.id == 2


def test_add_transaction_ids_independent_per_user(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    t_u1 = add_transaction(1, _make_transaction())
    t_u2 = add_transaction(2, _make_transaction())
    assert t_u1.id == 1
    assert t_u2.id == 1  # user 2 starts at 1 independently


def test_add_transaction_persists_id_to_disk(tmp_path, monkeypatch):
    import app.storage as st

    f = tmp_path / "transactions.json"
    monkeypatch.setattr(st, "DATA_FILE", f)
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    raw = json.loads(f.read_text())
    assert raw["1"][0]["id"] == 1


# ---------------------------------------------------------------------------
# get_transaction_by_id
# ---------------------------------------------------------------------------


def test_get_transaction_by_id_finds_correct(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=1000.0))
    add_transaction(1, _make_transaction(amount=2000.0))

    t = get_transaction_by_id(1, 2)
    assert t is not None
    assert t.amount == pytest.approx(2000.0)


def test_get_transaction_by_id_returns_none_for_missing(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    assert get_transaction_by_id(1, 99) is None


def test_get_transaction_by_id_returns_none_for_unknown_user(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    assert get_transaction_by_id(999, 1) is None


# ---------------------------------------------------------------------------
# update_transaction
# ---------------------------------------------------------------------------


def test_update_transaction_updates_status(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    update_transaction(1, 1, status="fully_saved")

    assert get_transactions(1)[0].status == "fully_saved"


def test_update_transaction_updates_saved_and_remaining(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    update_transaction(1, 1, saved_amount=2000.0, remaining_amount=3000.0, status="partially_saved")

    t = get_transactions(1)[0]
    assert t.saved_amount == pytest.approx(2000.0)
    assert t.remaining_amount == pytest.approx(3000.0)
    assert t.status == "partially_saved"


def test_update_transaction_returns_none_for_missing(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    result = update_transaction(1, 99, status="fully_saved")
    assert result is None


def test_update_transaction_persists_to_disk(tmp_path, monkeypatch):
    import app.storage as st

    f = tmp_path / "transactions.json"
    monkeypatch.setattr(st, "DATA_FILE", f)
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    update_transaction(1, 1, status="fully_saved", saved_amount=5000.0, remaining_amount=0.0)

    raw = json.loads(f.read_text())
    assert raw["1"][0]["status"] == "fully_saved"
    assert raw["1"][0]["saved_amount"] == pytest.approx(5000.0)
    assert raw["1"][0]["remaining_amount"] == pytest.approx(0.0)


def test_update_transaction_ignores_unknown_fields(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "transactions.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    result = update_transaction(1, 1, nonexistent_field="value")
    assert result is not None
