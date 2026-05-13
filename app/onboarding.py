from typing import Optional, Tuple

from app.cms import t
from app.message_store import format_message
from app.user_storage import BotUser, update_user_profile

STEP_BUSINESS_TYPE = "business_type"
STEP_VAT_INCLUDED = "vat_included"
STEP_INCOME_TAX = "income_tax_rate"
STEP_NATIONAL_INSURANCE = "national_insurance_rate"
STEP_SOCIAL_SAVINGS = "social_savings_rate"
STEP_PENSION = "pension_rate"


def parse_rate(text: str) -> Optional[float]:
    """Parse "20" → 0.20 or "0.20" → 0.20. Returns None if invalid or out of [0, 1]."""
    t = text.strip().replace(",", "").replace("%", "")
    try:
        val = float(t)
    except ValueError:
        return None
    if val > 1:
        val = val / 100
    if val < 0 or val > 1:
        return None
    return val


def parse_business_type(text: str) -> Optional[str]:
    t = text.strip().lower()
    if t in ("מורשה", "עוסק מורשה", "1", "vat registered", "registered"):
        return "vat_registered"
    if t in ("פטור", "עוסק פטור", "2", "vat exempt", "exempt"):
        return "vat_exempt"
    return None


def parse_yes_no(text: str) -> Optional[bool]:
    t = text.strip()
    if t in ("כן", "yes", "y", "1", "כולל"):
        return True
    if t in ("לא", "no", "n", "2", "לא כולל"):
        return False
    return None


def start_onboarding(user_id: int, lang: str = "he") -> str:
    update_user_profile(user_id, onboarding_step=STEP_BUSINESS_TYPE)
    return t("onboarding_welcome", lang)


def handle_onboarding(user: BotUser, text: str) -> Tuple[str, bool]:
    """Process one onboarding input. Returns (reply_text, is_now_complete)."""
    step = user.onboarding_step
    lang = user.preferred_language or "he"

    if step == STEP_BUSINESS_TYPE:
        business_type = parse_business_type(text)
        if business_type is None:
            return format_message(f"onboarding_invalid_business_type_{lang}"), False
        if business_type == "vat_exempt":
            update_user_profile(
                user.telegram_user_id,
                business_type=business_type,
                vat_included_default=False,
                onboarding_step=STEP_INCOME_TAX,
            )
            return format_message(f"onboarding_ask_income_tax_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            business_type=business_type,
            onboarding_step=STEP_VAT_INCLUDED,
        )
        return format_message(f"onboarding_ask_vat_included_{lang}"), False

    if step == STEP_VAT_INCLUDED:
        val = parse_yes_no(text)
        if val is None:
            return format_message(f"onboarding_invalid_yes_no_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            vat_included_default=val,
            onboarding_step=STEP_INCOME_TAX,
        )
        return format_message(f"onboarding_ask_income_tax_{lang}"), False

    if step == STEP_INCOME_TAX:
        rate = parse_rate(text)
        if rate is None:
            return format_message(f"onboarding_invalid_rate_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            income_tax_rate=rate,
            onboarding_step=STEP_NATIONAL_INSURANCE,
        )
        return format_message(f"onboarding_ask_national_insurance_{lang}"), False

    if step == STEP_NATIONAL_INSURANCE:
        rate = parse_rate(text)
        if rate is None:
            return format_message(f"onboarding_invalid_rate_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            national_insurance_rate=rate,
            onboarding_step=STEP_SOCIAL_SAVINGS,
        )
        return format_message(f"onboarding_ask_social_savings_{lang}"), False

    if step == STEP_SOCIAL_SAVINGS:
        rate = parse_rate(text)
        if rate is None:
            return format_message(f"onboarding_invalid_rate_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            social_savings_rate=rate,
            onboarding_step=STEP_PENSION,
        )
        return format_message(f"onboarding_ask_pension_{lang}"), False

    if step == STEP_PENSION:
        rate = parse_rate(text)
        if rate is None:
            return format_message(f"onboarding_invalid_rate_{lang}"), False
        update_user_profile(
            user.telegram_user_id,
            pension_rate=rate,
            onboarding_step=None,
            onboarding_completed=True,
        )
        return format_message(f"onboarding_complete_{lang}"), True

    # Unknown step — restart from the beginning
    update_user_profile(user.telegram_user_id, onboarding_step=STEP_BUSINESS_TYPE)
    return format_message(f"onboarding_welcome_{lang}"), False
