"""Tests for BotUser model, serialization, and backward compatibility."""

import json

import pytest

from app.user_storage import (
    BotUser,
    _dict_to_user,
    _user_to_dict,
    get_user,
    update_user_profile,
    upsert_from_telegram,
)

# ---------------------------------------------------------------------------
# BotUser defaults — new user created without profile fields
# ---------------------------------------------------------------------------


def test_new_user_onboarding_not_completed():
    u = BotUser(telegram_user_id=1)
    assert u.onboarding_completed is False


def test_new_user_onboarding_step_is_none():
    u = BotUser(telegram_user_id=1)
    assert u.onboarding_step is None


def test_new_user_profile_notified_false():
    u = BotUser(telegram_user_id=1)
    assert u.profile_notified is False


def test_new_user_default_business_type():
    u = BotUser(telegram_user_id=1)
    assert u.business_type == "vat_registered"


def test_new_user_default_vat_included():
    u = BotUser(telegram_user_id=1)
    assert u.vat_included_default is True


def test_new_user_default_income_tax_rate():
    u = BotUser(telegram_user_id=1)
    assert u.income_tax_rate == pytest.approx(0.20)


def test_new_user_default_national_insurance_rate():
    u = BotUser(telegram_user_id=1)
    assert u.national_insurance_rate == pytest.approx(0.08)


def test_new_user_default_social_savings_rate():
    u = BotUser(telegram_user_id=1)
    assert u.social_savings_rate == pytest.approx(0.05)


# ---------------------------------------------------------------------------
# Backward compatibility — loading old JSON records (no new fields)
# ---------------------------------------------------------------------------

OLD_FORMAT_RECORD = {
    "telegram_user_id": 999,
    "username": "olduser",
    "display_name": "Old User",
    "notes": "",
    "is_blocked": False,
    "created_at": "2026-01-01T10:00:00",
    "updated_at": "2026-01-01T10:00:00",
}


def test_old_record_loads_without_error():
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.telegram_user_id == 999


def test_old_record_onboarding_completed_defaults_true():
    """Existing users must not be re-onboarded after PROD-001 upgrade."""
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.onboarding_completed is True


def test_old_record_profile_notified_defaults_false():
    """Existing users should receive the one-time profile defaults notification."""
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.profile_notified is False


def test_old_record_rates_match_previous_hardcoded_values():
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.income_tax_rate == pytest.approx(0.20)
    assert user.national_insurance_rate == pytest.approx(0.08)
    assert user.social_savings_rate == pytest.approx(0.05)


def test_old_record_business_type_defaults_vat_registered():
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.business_type == "vat_registered"


def test_old_record_vat_included_default_true():
    user = _dict_to_user(OLD_FORMAT_RECORD)
    assert user.vat_included_default is True


# ---------------------------------------------------------------------------
# Serialization round-trip — new fields survive save/load
# ---------------------------------------------------------------------------


def test_round_trip_preserves_business_type():
    u = BotUser(telegram_user_id=1, business_type="vat_exempt")
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.business_type == "vat_exempt"


def test_round_trip_preserves_vat_included_default():
    u = BotUser(telegram_user_id=1, vat_included_default=False)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.vat_included_default is False


def test_round_trip_preserves_income_tax_rate():
    u = BotUser(telegram_user_id=1, income_tax_rate=0.30)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.income_tax_rate == pytest.approx(0.30)


def test_round_trip_preserves_national_insurance_rate():
    u = BotUser(telegram_user_id=1, national_insurance_rate=0.12)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.national_insurance_rate == pytest.approx(0.12)


def test_round_trip_preserves_social_savings_rate():
    u = BotUser(telegram_user_id=1, social_savings_rate=0.0)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.social_savings_rate == pytest.approx(0.0)


def test_round_trip_preserves_onboarding_completed():
    u = BotUser(telegram_user_id=1, onboarding_completed=True)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.onboarding_completed is True


def test_round_trip_preserves_onboarding_step():
    u = BotUser(telegram_user_id=1, onboarding_step="income_tax")
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.onboarding_step == "income_tax"


def test_round_trip_preserves_profile_notified():
    u = BotUser(telegram_user_id=1, profile_notified=True)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.profile_notified is True


def test_round_trip_onboarding_step_none():
    u = BotUser(telegram_user_id=1, onboarding_step=None)
    reloaded = _dict_to_user(_user_to_dict(u))
    assert reloaded.onboarding_step is None


# ---------------------------------------------------------------------------
# update_user_profile — field updates and persistence
# ---------------------------------------------------------------------------


def test_update_user_profile_income_tax_rate(tmp_path, monkeypatch):
    import app.user_storage as us

    monkeypatch.setattr(us, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(us, "USERS", {})

    upsert_from_telegram(telegram_user_id=42, username="test")
    update_user_profile(42, income_tax_rate=0.30)

    user = get_user(42)
    assert user.income_tax_rate == pytest.approx(0.30)


def test_update_user_profile_onboarding_step(tmp_path, monkeypatch):
    import app.user_storage as us

    monkeypatch.setattr(us, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(us, "USERS", {})

    upsert_from_telegram(telegram_user_id=42, username="test")
    update_user_profile(42, onboarding_step="income_tax", onboarding_completed=False)

    user = get_user(42)
    assert user.onboarding_step == "income_tax"
    assert user.onboarding_completed is False


def test_update_user_profile_unknown_field_ignored(tmp_path, monkeypatch):
    import app.user_storage as us

    monkeypatch.setattr(us, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(us, "USERS", {})

    upsert_from_telegram(telegram_user_id=42, username="test")
    update_user_profile(42, nonexistent_field="value")  # must not raise

    user = get_user(42)
    assert user is not None


def test_update_user_profile_missing_user_returns_none(tmp_path, monkeypatch):
    import app.user_storage as us

    monkeypatch.setattr(us, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(us, "USERS", {})

    result = update_user_profile(99999, income_tax_rate=0.10)
    assert result is None


def test_update_user_profile_persists_to_disk(tmp_path, monkeypatch):
    import app.user_storage as us

    users_file = tmp_path / "users.json"
    monkeypatch.setattr(us, "USERS_FILE", users_file)
    monkeypatch.setattr(us, "USERS", {})

    upsert_from_telegram(telegram_user_id=42, username="test")
    update_user_profile(42, income_tax_rate=0.10, profile_notified=True)

    raw = json.loads(users_file.read_text())
    assert raw["42"]["income_tax_rate"] == pytest.approx(0.10)
    assert raw["42"]["profile_notified"] is True
