"""Tests for BotUser model and SQLite-backed user storage."""

import pytest

from app.user_storage import (
    BotUser,
    delete_user_record,
    get_user,
    is_user_blocked,
    list_registered_users,
    update_user_profile,
    upsert_from_telegram,
)

# ---------------------------------------------------------------------------
# BotUser dataclass defaults
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


def test_new_user_default_preferred_language():
    u = BotUser(telegram_user_id=1)
    assert u.preferred_language == "he"


def test_new_user_default_vat_period():
    u = BotUser(telegram_user_id=1)
    assert u.vat_period == "monthly"


# ---------------------------------------------------------------------------
# upsert_from_telegram
# ---------------------------------------------------------------------------


def test_upsert_creates_new_user():
    user = upsert_from_telegram(telegram_user_id=1, username="alice")
    assert user is not None
    assert user.telegram_user_id == 1
    assert user.username == "alice"


def test_upsert_is_idempotent():
    upsert_from_telegram(telegram_user_id=1, username="alice")
    upsert_from_telegram(telegram_user_id=1, username="alice")
    assert len(list_registered_users()) == 1


def test_upsert_updates_username():
    upsert_from_telegram(telegram_user_id=1, username="alice")
    upsert_from_telegram(telegram_user_id=1, username="alice2")
    assert get_user(1).username == "alice2"


def test_upsert_preserves_profile_fields():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, income_tax_rate=0.30)
    upsert_from_telegram(telegram_user_id=1, username="alice")
    assert get_user(1).income_tax_rate == pytest.approx(0.30)


# ---------------------------------------------------------------------------
# get_user
# ---------------------------------------------------------------------------


def test_get_user_returns_none_for_unknown():
    assert get_user(99999) is None


def test_get_user_returns_correct_user():
    upsert_from_telegram(telegram_user_id=42, username="bob")
    user = get_user(42)
    assert user.username == "bob"


# ---------------------------------------------------------------------------
# update_user_profile
# ---------------------------------------------------------------------------


def test_update_income_tax_rate():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, income_tax_rate=0.30)
    assert get_user(1).income_tax_rate == pytest.approx(0.30)


def test_update_onboarding_step():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, onboarding_step="income_tax", onboarding_completed=False)
    user = get_user(1)
    assert user.onboarding_step == "income_tax"
    assert user.onboarding_completed is False


def test_update_profile_notified():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, profile_notified=True)
    assert get_user(1).profile_notified is True


def test_update_business_type():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, business_type="vat_exempt", vat_included_default=False)
    user = get_user(1)
    assert user.business_type == "vat_exempt"
    assert user.vat_included_default is False


def test_update_preferred_language():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, preferred_language="en")
    assert get_user(1).preferred_language == "en"


def test_update_vat_period_to_bi_monthly():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, vat_period="bi_monthly")
    assert get_user(1).vat_period == "bi_monthly"


def test_update_vat_period_back_to_monthly():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, vat_period="bi_monthly")
    update_user_profile(1, vat_period="monthly")
    assert get_user(1).vat_period == "monthly"


def test_vat_period_in_user_summary_dict():
    from app.user_storage import user_summary_dict

    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, vat_period="bi_monthly")
    summary = user_summary_dict(get_user(1))
    assert summary["vat_period"] == "bi_monthly"


def test_preferred_language_persists_across_upsert():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, preferred_language="en")
    upsert_from_telegram(telegram_user_id=1, username="alice")
    assert get_user(1).preferred_language == "en"


def test_update_unknown_field_ignored():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, nonexistent_field="value")
    assert get_user(1) is not None


def test_update_missing_user_returns_none():
    assert update_user_profile(99999, income_tax_rate=0.10) is None


def test_update_persists_across_get():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, income_tax_rate=0.10, national_insurance_rate=0.12)
    user = get_user(1)
    assert user.income_tax_rate == pytest.approx(0.10)
    assert user.national_insurance_rate == pytest.approx(0.12)


# ---------------------------------------------------------------------------
# is_user_blocked / block flag
# ---------------------------------------------------------------------------


def test_new_user_not_blocked():
    upsert_from_telegram(telegram_user_id=1)
    assert is_user_blocked(1) is False


def test_block_user():
    upsert_from_telegram(telegram_user_id=1)
    update_user_profile(1, is_blocked=True)
    assert is_user_blocked(1) is True


def test_unknown_user_not_blocked():
    assert is_user_blocked(99999) is False


# ---------------------------------------------------------------------------
# delete_user_record
# ---------------------------------------------------------------------------


def test_delete_existing_user_returns_true():
    upsert_from_telegram(telegram_user_id=1)
    assert delete_user_record(1) is True
    assert get_user(1) is None


def test_delete_missing_user_returns_false():
    assert delete_user_record(99999) is False


# ---------------------------------------------------------------------------
# list_registered_users
# ---------------------------------------------------------------------------


def test_list_registered_users_empty():
    assert list_registered_users() == []


def test_list_registered_users_returns_all():
    upsert_from_telegram(telegram_user_id=1)
    upsert_from_telegram(telegram_user_id=2)
    ids = [u.telegram_user_id for u in list_registered_users()]
    assert 1 in ids
    assert 2 in ids
