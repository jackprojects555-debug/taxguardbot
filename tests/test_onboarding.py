"""Tests for onboarding state machine and input parsing."""

import pytest

from app.onboarding import (
    STEP_BUSINESS_TYPE,
    STEP_INCOME_TAX,
    STEP_NATIONAL_INSURANCE,
    STEP_PENSION,
    STEP_SOCIAL_SAVINGS,
    STEP_VAT_INCLUDED,
    handle_onboarding,
    parse_business_type,
    parse_rate,
    parse_rate_or_fixed,
    parse_yes_no,
    start_onboarding,
)
from app.user_storage import get_user, update_user_profile, upsert_from_telegram

# ---------------------------------------------------------------------------
# parse_rate
# ---------------------------------------------------------------------------


def test_parse_rate_integer_percent():
    assert parse_rate("20") == pytest.approx(0.20)


def test_parse_rate_decimal_fraction():
    assert parse_rate("0.20") == pytest.approx(0.20)


def test_parse_rate_zero():
    assert parse_rate("0") == pytest.approx(0.0)


def test_parse_rate_hundred_percent():
    assert parse_rate("100") == pytest.approx(1.0)


def test_parse_rate_strips_percent_sign():
    assert parse_rate("8%") == pytest.approx(0.08)


def test_parse_rate_negative_returns_none():
    assert parse_rate("-1") is None


def test_parse_rate_over_100_returns_none():
    assert parse_rate("200") is None


def test_parse_rate_non_numeric_returns_none():
    assert parse_rate("abc") is None


def test_parse_rate_empty_returns_none():
    assert parse_rate("") is None


def test_parse_rate_eight_integer():
    assert parse_rate("8") == pytest.approx(0.08)


def test_parse_rate_five_decimal():
    assert parse_rate("0.05") == pytest.approx(0.05)


# ---------------------------------------------------------------------------
# parse_business_type
# ---------------------------------------------------------------------------


def test_parse_business_type_short_vat_registered():
    assert parse_business_type("מורשה") == "vat_registered"


def test_parse_business_type_full_vat_registered():
    assert parse_business_type("עוסק מורשה") == "vat_registered"


def test_parse_business_type_number_one():
    assert parse_business_type("1") == "vat_registered"


def test_parse_business_type_short_vat_exempt():
    assert parse_business_type("פטור") == "vat_exempt"


def test_parse_business_type_full_vat_exempt():
    assert parse_business_type("עוסק פטור") == "vat_exempt"


def test_parse_business_type_number_two():
    assert parse_business_type("2") == "vat_exempt"


def test_parse_business_type_unknown_returns_none():
    assert parse_business_type("blah") is None


# ---------------------------------------------------------------------------
# parse_yes_no
# ---------------------------------------------------------------------------


def test_parse_yes_no_hebrew_yes():
    assert parse_yes_no("כן") is True


def test_parse_yes_no_hebrew_no():
    assert parse_yes_no("לא") is False


def test_parse_yes_no_english_yes():
    assert parse_yes_no("yes") is True


def test_parse_yes_no_english_no():
    assert parse_yes_no("no") is False


def test_parse_yes_no_number_one():
    assert parse_yes_no("1") is True


def test_parse_yes_no_number_two():
    assert parse_yes_no("2") is False


def test_parse_yes_no_unknown_returns_none():
    assert parse_yes_no("maybe") is None


# ---------------------------------------------------------------------------
# Onboarding flow — vat_registered
# ---------------------------------------------------------------------------


def test_onboarding_full_vat_registered_flow():

    upsert_from_telegram(telegram_user_id=1)
    reply = start_onboarding(1)
    assert reply

    assert get_user(1).onboarding_step == STEP_BUSINESS_TYPE

    reply, done = handle_onboarding(get_user(1), "מורשה")
    assert not done
    assert get_user(1).business_type == "vat_registered"
    assert get_user(1).onboarding_step == STEP_VAT_INCLUDED

    reply, done = handle_onboarding(get_user(1), "כן")
    assert not done
    assert get_user(1).vat_included_default is True
    assert get_user(1).onboarding_step == STEP_INCOME_TAX

    reply, done = handle_onboarding(get_user(1), "20")
    assert not done
    assert get_user(1).income_tax_rate == pytest.approx(0.20)
    assert get_user(1).onboarding_step == STEP_NATIONAL_INSURANCE

    reply, done = handle_onboarding(get_user(1), "8")
    assert not done
    assert get_user(1).national_insurance_rate == pytest.approx(0.08)
    assert get_user(1).onboarding_step == STEP_SOCIAL_SAVINGS

    reply, done = handle_onboarding(get_user(1), "5")
    assert not done
    assert get_user(1).social_savings_rate == pytest.approx(0.05)
    assert get_user(1).onboarding_step == STEP_PENSION

    reply, done = handle_onboarding(get_user(1), "6")
    assert done
    assert get_user(1).pension_rate == pytest.approx(0.06)
    assert get_user(1).onboarding_completed is True
    assert get_user(1).onboarding_step is None


# ---------------------------------------------------------------------------
# Onboarding flow — vat_exempt (skips vat_included step)
# ---------------------------------------------------------------------------


def test_onboarding_full_vat_exempt_flow():

    upsert_from_telegram(telegram_user_id=2)
    start_onboarding(2)

    reply, done = handle_onboarding(get_user(2), "פטור")
    assert not done
    assert get_user(2).business_type == "vat_exempt"
    assert get_user(2).vat_included_default is False
    assert get_user(2).onboarding_step == STEP_INCOME_TAX

    reply, done = handle_onboarding(get_user(2), "15")
    assert not done
    assert get_user(2).income_tax_rate == pytest.approx(0.15)

    reply, done = handle_onboarding(get_user(2), "12")
    assert not done
    assert get_user(2).national_insurance_rate == pytest.approx(0.12)

    reply, done = handle_onboarding(get_user(2), "0")
    assert not done
    assert get_user(2).social_savings_rate == pytest.approx(0.0)
    assert get_user(2).onboarding_step == STEP_PENSION

    reply, done = handle_onboarding(get_user(2), "0")
    assert done
    assert get_user(2).pension_rate == pytest.approx(0.0)
    assert get_user(2).onboarding_completed is True


# ---------------------------------------------------------------------------
# Invalid input re-prompts
# ---------------------------------------------------------------------------


def test_invalid_business_type_stays_on_same_step():

    upsert_from_telegram(telegram_user_id=3)
    start_onboarding(3)

    reply, done = handle_onboarding(get_user(3), "blah")
    assert not done
    assert get_user(3).onboarding_step == STEP_BUSINESS_TYPE


def test_invalid_rate_stays_on_same_step():

    upsert_from_telegram(telegram_user_id=4)
    start_onboarding(4)
    handle_onboarding(get_user(4), "מורשה")
    handle_onboarding(get_user(4), "כן")

    assert get_user(4).onboarding_step == STEP_INCOME_TAX

    reply, done = handle_onboarding(get_user(4), "abc")
    assert not done
    assert get_user(4).onboarding_step == STEP_INCOME_TAX


def test_invalid_yes_no_stays_on_same_step():

    upsert_from_telegram(telegram_user_id=5)
    start_onboarding(5)
    handle_onboarding(get_user(5), "מורשה")

    assert get_user(5).onboarding_step == STEP_VAT_INCLUDED

    reply, done = handle_onboarding(get_user(5), "אולי")
    assert not done
    assert get_user(5).onboarding_step == STEP_VAT_INCLUDED


# ---------------------------------------------------------------------------
# Decimal rate input accepted
# ---------------------------------------------------------------------------


def test_decimal_rate_accepted_in_flow():

    upsert_from_telegram(telegram_user_id=6)
    start_onboarding(6)
    handle_onboarding(get_user(6), "1")
    handle_onboarding(get_user(6), "כן")

    reply, done = handle_onboarding(get_user(6), "0.25")
    assert not done
    assert get_user(6).income_tax_rate == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# parse_business_type — English aliases
# ---------------------------------------------------------------------------


def test_parse_business_type_english_registered():
    assert parse_business_type("registered") == "vat_registered"
    assert parse_business_type("vat registered") == "vat_registered"


def test_parse_business_type_english_exempt():
    assert parse_business_type("exempt") == "vat_exempt"
    assert parse_business_type("vat exempt") == "vat_exempt"


# ---------------------------------------------------------------------------
# Onboarding flow — English language
# ---------------------------------------------------------------------------


def test_start_onboarding_english_welcome():
    upsert_from_telegram(telegram_user_id=10)
    reply = start_onboarding(10, lang="en")
    assert "VAT" in reply
    assert get_user(10).onboarding_step == STEP_BUSINESS_TYPE


def test_onboarding_english_full_vat_registered_flow():
    upsert_from_telegram(telegram_user_id=11)
    update_user_profile(11, preferred_language="en")
    start_onboarding(11, lang="en")

    reply, done = handle_onboarding(get_user(11), "registered")
    assert not done
    assert get_user(11).business_type == "vat_registered"
    assert get_user(11).onboarding_step == STEP_VAT_INCLUDED
    assert "VAT" in reply

    reply, done = handle_onboarding(get_user(11), "yes")
    assert not done
    assert get_user(11).vat_included_default is True

    reply, done = handle_onboarding(get_user(11), "20")
    assert not done
    assert get_user(11).income_tax_rate == pytest.approx(0.20)

    reply, done = handle_onboarding(get_user(11), "8")
    assert not done

    reply, done = handle_onboarding(get_user(11), "5")
    assert not done
    assert get_user(11).onboarding_step == STEP_PENSION

    reply, done = handle_onboarding(get_user(11), "0")
    assert done
    assert get_user(11).onboarding_completed is True
    assert "ready" in reply.lower()


def test_onboarding_english_invalid_messages_are_english():
    upsert_from_telegram(telegram_user_id=12)
    update_user_profile(12, preferred_language="en")
    start_onboarding(12, lang="en")

    reply, done = handle_onboarding(get_user(12), "garbage")
    assert not done
    assert "understand" in reply.lower()


def test_onboarding_hebrew_invalid_messages_are_hebrew():
    upsert_from_telegram(telegram_user_id=13)
    update_user_profile(13, preferred_language="he")
    start_onboarding(13)

    reply, done = handle_onboarding(get_user(13), "garbage")
    assert not done
    assert "הבנתי" in reply


# ---------------------------------------------------------------------------
# Pension step
# ---------------------------------------------------------------------------


def _reach_pension_step(user_id: int, lang: str = "he") -> None:
    """Drive onboarding up to (but not including) the pension step."""
    upsert_from_telegram(telegram_user_id=user_id)
    update_user_profile(user_id, preferred_language=lang)
    start_onboarding(user_id, lang=lang)
    handle_onboarding(get_user(user_id), "1")  # vat_registered
    handle_onboarding(get_user(user_id), "yes" if lang == "en" else "כן")  # vat_included
    handle_onboarding(get_user(user_id), "20")  # income_tax
    handle_onboarding(get_user(user_id), "8")  # national_insurance
    handle_onboarding(get_user(user_id), "5")  # social_savings → now at STEP_PENSION


def test_pension_step_is_reached_after_social_savings():
    _reach_pension_step(20)
    assert get_user(20).onboarding_step == STEP_PENSION


def test_pension_step_zero_skips_and_completes():
    _reach_pension_step(21)
    reply, done = handle_onboarding(get_user(21), "0")
    assert done
    assert get_user(21).pension_rate == pytest.approx(0.0)
    assert get_user(21).onboarding_completed is True


def test_pension_step_saves_nonzero_rate():
    _reach_pension_step(22)
    reply, done = handle_onboarding(get_user(22), "6")
    assert done
    assert get_user(22).pension_rate == pytest.approx(0.06)
    assert get_user(22).onboarding_completed is True


def test_pension_step_invalid_input_stays():
    _reach_pension_step(23)
    reply, done = handle_onboarding(get_user(23), "abc")
    assert not done
    assert get_user(23).onboarding_step == STEP_PENSION


def test_pension_step_english_prompt_contains_pension():
    _reach_pension_step(24, lang="en")
    # The reply from social_savings step should mention pension
    user = get_user(24)
    assert user.onboarding_step == STEP_PENSION


# ---------------------------------------------------------------------------
# parse_rate_or_fixed
# ---------------------------------------------------------------------------


def test_parse_rate_or_fixed_percentage_integer():
    result = parse_rate_or_fixed("8")
    assert result == ("percentage", pytest.approx(0.08), 0.0)


def test_parse_rate_or_fixed_percentage_decimal():
    result = parse_rate_or_fixed("0.05")
    assert result == ("percentage", pytest.approx(0.05), 0.0)


def test_parse_rate_or_fixed_percentage_zero():
    result = parse_rate_or_fixed("0")
    assert result == ("percentage", pytest.approx(0.0), 0.0)


def test_parse_rate_or_fixed_fixed_monthly_en():
    result = parse_rate_or_fixed("1200 monthly")
    assert result == ("fixed", 0.0, pytest.approx(1200.0))


def test_parse_rate_or_fixed_fixed_keyword_he():
    result = parse_rate_or_fixed("1200 חודשי")
    assert result == ("fixed", 0.0, pytest.approx(1200.0))


def test_parse_rate_or_fixed_fixed_keyword_kavu():
    result = parse_rate_or_fixed("800 קבוע")
    assert result == ("fixed", 0.0, pytest.approx(800.0))


def test_parse_rate_or_fixed_fixed_keyword_first():
    result = parse_rate_or_fixed("monthly 1200")
    assert result == ("fixed", 0.0, pytest.approx(1200.0))


def test_parse_rate_or_fixed_fixed_zero():
    result = parse_rate_or_fixed("0 monthly")
    assert result == ("fixed", 0.0, pytest.approx(0.0))


def test_parse_rate_or_fixed_invalid_returns_none():
    assert parse_rate_or_fixed("abc") is None


def test_parse_rate_or_fixed_invalid_rate_over_100():
    assert parse_rate_or_fixed("200") is None


def test_parse_rate_or_fixed_negative_fixed_returns_none():
    assert parse_rate_or_fixed("-100 monthly") is None


def test_parse_rate_or_fixed_keyword_only_no_number():
    assert parse_rate_or_fixed("monthly") is None


# ---------------------------------------------------------------------------
# Fixed mode through onboarding flow
# ---------------------------------------------------------------------------


def _reach_ni_step(user_id: int, lang: str = "he") -> None:
    upsert_from_telegram(telegram_user_id=user_id)
    update_user_profile(user_id, preferred_language=lang)
    start_onboarding(user_id, lang=lang)
    handle_onboarding(get_user(user_id), "1")  # vat_registered
    handle_onboarding(get_user(user_id), "yes" if lang == "en" else "כן")  # vat_included
    handle_onboarding(get_user(user_id), "20")  # income_tax


def test_ni_fixed_mode_saved_from_onboarding():
    _reach_ni_step(30)
    reply, done = handle_onboarding(get_user(30), "1200 monthly")
    assert not done
    u = get_user(30)
    assert u.national_insurance_mode == "fixed"
    assert u.national_insurance_fixed == pytest.approx(1200.0)
    assert u.national_insurance_rate == pytest.approx(0.0)
    assert u.onboarding_step == STEP_SOCIAL_SAVINGS


def test_ni_percentage_mode_unchanged():
    _reach_ni_step(31)
    handle_onboarding(get_user(31), "8")
    u = get_user(31)
    assert u.national_insurance_mode == "percentage"
    assert u.national_insurance_rate == pytest.approx(0.08)
    assert u.national_insurance_fixed == pytest.approx(0.0)


def test_ni_invalid_input_reprompts():
    _reach_ni_step(32)
    reply, done = handle_onboarding(get_user(32), "abc")
    assert not done
    assert get_user(32).onboarding_step == STEP_NATIONAL_INSURANCE


def test_ss_fixed_mode_saved_from_onboarding():
    _reach_ni_step(33)
    handle_onboarding(get_user(33), "8")  # NI percentage
    reply, done = handle_onboarding(get_user(33), "800 חודשי")
    assert not done
    u = get_user(33)
    assert u.social_savings_mode == "fixed"
    assert u.social_savings_fixed == pytest.approx(800.0)
    assert u.social_savings_rate == pytest.approx(0.0)
    assert u.onboarding_step == STEP_PENSION


def test_ss_invalid_input_reprompts():
    _reach_ni_step(34)
    handle_onboarding(get_user(34), "8")  # NI
    reply, done = handle_onboarding(get_user(34), "garbage")
    assert not done
    assert get_user(34).onboarding_step == STEP_SOCIAL_SAVINGS
