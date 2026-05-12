import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

MESSAGES_FILE = Path("data/messages.json")

_DEFAULT_MESSAGES: Dict[str, str] = {
    "reset_keywords_note": (
        "Triggers reset (comma-separated for display): reset, אפס, נקה, מחק — "
        "detection remains code-defined; customize reply text via reset_success_en."
    ),
    "status_command_note": (
        'Summary command keyword "מצב" is code-defined for matching; '
        "customize output via status_* keys."
    ),
    "vat_excluded_keyword_note": (
        'Amount parsing treats "נוכה" as VAT excluded; customize copy in '
        "transaction_* messages only."
    ),
    "reset_success_en": "All data has been reset.",
    "user_blocked_he": "הגישה לבוט חסומה למשתמש זה.",
    "status_no_data_he": "אין עדיין נתונים החודש.",
    "status_summary_he": (
        "סיכום עד כה:\n\n"
        "הכנסות: ₪{total_income:,.0f}\n\n"
        "מע״מ: ₪{total_vat:,.0f}\n"
        "מס הכנסה: ₪{total_income_tax:,.0f}\n"
        "ביטוח לאומי: ₪{total_national_insurance:,.0f}\n"
        "סוציאליות: ₪{total_social_savings:,.0f}\n\n"
        "לשמירה: ₪{total_to_save:,.0f}\n"
        "פנוי: ₪{total_available:,.0f}"
    ),
    "invalid_input_empty_en": "Invalid input. Please enter a number.",
    "unsupported_format_en": "Unsupported format. Please enter full number.",
    "amount_must_be_positive_en": "Amount must be positive.",
    "transaction_success_he": (
        "נכנסו ₪{amount:,.0f}\n\n"
        "להפרשה:\n\n"
        "מע״מ: ₪{vat_amount:,.0f}\n"
        "מס הכנסה: ₪{income_tax_amount:,.0f}\n"
        "ביטוח לאומי: ₪{national_insurance_amount:,.0f}\n"
        "סוציאליות: ₪{social_savings_amount:,.0f}\n\n"
        "סה״כ להעברה עכשיו: ₪{total_to_save:,.0f}\n"
        "כסף פנוי אמיתי: ₪{available_amount:,.0f}\n\n"
        "פעולה מומלצת: העבר עכשיו ₪{total_to_save:,.0f} לחשבון השמירה שלך."
    ),
    "invalid_number_en": "Invalid input. Please enter a number.",
    # Onboarding
    "profile_notified_he": "הפרופיל שלך הוגדר בברירות מחדל. לשינוי הגדרות שלח: הגדרות",
    "onboarding_welcome_he": (
        "ברוך הבא! נגדיר את הפרופיל שלך.\n\nאיזה סוג עסק יש לך?\n1 — עוסק מורשה\n2 — עוסק פטור"
    ),
    "onboarding_ask_vat_included_he": 'האם המחירים שלך כוללים מע"מ?\nכן / לא',
    "onboarding_ask_income_tax_he": "מה שיעור מס ההכנסה שלך? (לדוגמה: 20 או 0.20)",
    "onboarding_ask_national_insurance_he": "מה שיעור ביטוח לאומי שלך? (לדוגמה: 8 או 0.08)",
    "onboarding_ask_social_savings_he": "מה שיעור הסוציאליות שלך? (לדוגמה: 5 או 0.05)",
    "onboarding_complete_he": ("ההגדרות נשמרו. הבוט מוכן לשימוש!\nשלח סכום כדי לחשב את ההפרשות."),
    "onboarding_invalid_business_type_he": "לא הבנתי. שלח 1 לעוסק מורשה או 2 לעוסק פטור.",
    "onboarding_invalid_yes_no_he": "לא הבנתי. שלח כן או לא.",
    "onboarding_invalid_rate_he": "לא הבנתי. שלח מספר, למשל: 20 או 0.20",
}

_MESSAGES: Dict[str, str] = deepcopy(_DEFAULT_MESSAGES)
_loaded_mtime: Optional[float] = None


def _ensure_messages_file():
    MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MESSAGES_FILE.exists():
        MESSAGES_FILE.write_text(
            json.dumps(_DEFAULT_MESSAGES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _persist():
    _ensure_messages_file()
    MESSAGES_FILE.write_text(
        json.dumps(_MESSAGES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    global _loaded_mtime
    _loaded_mtime = MESSAGES_FILE.stat().st_mtime


def _read_file_payload() -> Dict[str, Any]:
    _ensure_messages_file()
    content = MESSAGES_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    try:
        raw = json.loads(content)
        return raw if isinstance(raw, dict) else {}
    except json.JSONDecodeError:
        return {}


def _apply_payload_to_memory(raw: Dict[str, Any]):
    global _MESSAGES
    merged = deepcopy(_DEFAULT_MESSAGES)
    for key, val in raw.items():
        if isinstance(val, str):
            merged[str(key)] = val
    _MESSAGES = merged


def _load_from_disk_if_changed():
    global _loaded_mtime
    _ensure_messages_file()
    mtime = MESSAGES_FILE.stat().st_mtime
    if _loaded_mtime == mtime:
        return
    raw = _read_file_payload()
    _apply_payload_to_memory(raw)
    _loaded_mtime = mtime


def reload_messages():
    """Force reload from disk (e.g. after admin save in the same process)."""
    global _loaded_mtime
    _loaded_mtime = None
    _load_from_disk_if_changed()


def get_messages_snapshot() -> Dict[str, str]:
    _load_from_disk_if_changed()
    return deepcopy(_MESSAGES)


def replace_messages(messages: Dict[str, str]):
    merged = deepcopy(_DEFAULT_MESSAGES)
    for key, val in messages.items():
        if not isinstance(val, str):
            continue
        k = str(key)
        if k in _DEFAULT_MESSAGES and val.strip() == "":
            merged[k] = _DEFAULT_MESSAGES[k]
        else:
            merged[k] = val
    global _MESSAGES
    _MESSAGES = merged
    _persist()


def format_message(key: str, **kwargs: Any) -> str:
    _load_from_disk_if_changed()
    template = _MESSAGES.get(key) or _DEFAULT_MESSAGES.get(key) or ""
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template


def default_message_keys() -> Dict[str, str]:
    return deepcopy(_DEFAULT_MESSAGES)


_ensure_messages_file()
_load_from_disk_if_changed()
