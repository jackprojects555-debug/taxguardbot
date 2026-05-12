"""Tests for automated reminder report builders."""

from datetime import datetime

from app.models import Transaction
from app.reminders import build_endmonth_report, build_midmonth_report
from app.storage import add_transaction

MONTH = "2026-05"
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
        month=MONTH,
        created_at=NOW,
    )
    defaults.update(overrides)
    return Transaction(**defaults)


# ---------------------------------------------------------------------------
# build_midmonth_report
# ---------------------------------------------------------------------------


def test_midmonth_no_transactions_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    assert build_midmonth_report(1, MONTH) is None


def test_midmonth_only_canceled_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(status="canceled"))
    assert build_midmonth_report(1, MONTH) is None


def test_midmonth_wrong_month_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(month="2026-04"))
    assert build_midmonth_report(1, MONTH) is None


def test_midmonth_contains_income(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(amount=11700.0))
    report = build_midmonth_report(1, MONTH)
    assert report is not None
    assert "11,700" in report


def test_midmonth_contains_month(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    report = build_midmonth_report(1, MONTH)
    assert MONTH in report


def test_midmonth_aggregates_multiple_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(
        1,
        _make_transaction(
            amount=5000.0, total_to_save=2000.0, saved_amount=0.0, remaining_amount=2000.0
        ),
    )
    add_transaction(
        1,
        _make_transaction(
            amount=6000.0, total_to_save=2500.0, saved_amount=0.0, remaining_amount=2500.0
        ),
    )
    report = build_midmonth_report(1, MONTH)
    assert "11,000" in report  # total income
    assert "4,500" in report  # total_to_save


def test_midmonth_skips_canceled_in_aggregation(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(
        1, _make_transaction(amount=5000.0, total_to_save=2000.0, remaining_amount=2000.0)
    )
    add_transaction(1, _make_transaction(amount=9000.0, status="canceled"))
    report = build_midmonth_report(1, MONTH)
    assert "9,000" not in report
    assert "5,000" in report


def test_midmonth_gap_excludes_fully_saved(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(
        1,
        _make_transaction(
            amount=5000.0,
            total_to_save=2000.0,
            saved_amount=2000.0,
            remaining_amount=0.0,
            status="fully_saved",
        ),
    )
    report = build_midmonth_report(1, MONTH)
    assert report is not None
    # gap should be 0
    assert "פער פתוח: ₪0" in report


# ---------------------------------------------------------------------------
# build_endmonth_report
# ---------------------------------------------------------------------------


def test_endmonth_no_transactions_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    assert build_endmonth_report(1, MONTH) is None


def test_endmonth_only_canceled_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(status="canceled"))
    assert build_endmonth_report(1, MONTH) is None


def test_endmonth_contains_all_breakdown_fields(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    report = build_endmonth_report(1, MONTH)
    assert report is not None
    assert "11,700" in report  # income
    assert "1,700" in report  # vat
    assert "2,000" in report  # income_tax
    assert "800" in report  # national_insurance
    assert "500" in report  # social_savings
    assert "5,000" in report  # total_to_save


def test_endmonth_contains_month(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction())
    report = build_endmonth_report(1, MONTH)
    assert MONTH in report


def test_endmonth_aggregates_multiple_transactions(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(
        1,
        _make_transaction(
            amount=5000.0,
            vat_amount=500.0,
            base_amount=4500.0,
            income_tax_amount=900.0,
            national_insurance_amount=360.0,
            social_savings_amount=225.0,
            total_to_save=1985.0,
            remaining_amount=1985.0,
        ),
    )
    add_transaction(
        1,
        _make_transaction(
            amount=6000.0,
            vat_amount=600.0,
            base_amount=5400.0,
            income_tax_amount=1080.0,
            national_insurance_amount=432.0,
            social_savings_amount=270.0,
            total_to_save=2382.0,
            remaining_amount=2382.0,
        ),
    )
    report = build_endmonth_report(1, MONTH)
    assert "11,000" in report  # total income


def test_endmonth_wrong_month_returns_none(tmp_path, monkeypatch):
    import app.storage as st

    monkeypatch.setattr(st, "DATA_FILE", tmp_path / "t.json")
    monkeypatch.setattr(st, "USER_TRANSACTIONS", {})

    add_transaction(1, _make_transaction(month="2026-04"))
    assert build_endmonth_report(1, MONTH) is None
