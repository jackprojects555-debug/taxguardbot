from datetime import datetime
from typing import Optional

from app.calculations import calculate_income_split
from app.message_store import format_message
from app.models import Transaction
from app.storage import get_transaction_by_id, get_transactions, update_transaction
from app.user_storage import BotUser

STATUS_LABELS = {
    "open": "פתוח",
    "partially_saved": "הועבר חלקית",
    "fully_saved": "הועבר",
    "canceled": "בוטל",
}


def _find_last_active(user_id: int) -> Optional[Transaction]:
    for t in reversed(get_transactions(user_id)):
        if t.status != "canceled":
            return t
    return None


def _parse_amount(text: str) -> Optional[float]:
    t = text.strip().replace(",", "").replace("₪", "")
    try:
        val = float(t)
        return val if val > 0 else None
    except ValueError:
        return None


def _format_detail(t: Transaction) -> str:
    return format_message(
        "transaction_detail_he",
        id=t.id,
        month=t.month,
        amount=t.amount,
        total_to_save=t.total_to_save,
        saved_amount=t.saved_amount,
        remaining_amount=t.remaining_amount,
        status=STATUS_LABELS.get(t.status, t.status),
    )


def show_last(user_id: int) -> str:
    t = _find_last_active(user_id)
    if t is None:
        return format_message("no_transactions_he")
    return _format_detail(t)


def show_list(user_id: int) -> str:
    current_month = datetime.now().strftime("%Y-%m")
    month_txns = [t for t in get_transactions(user_id) if t.month == current_month]
    if not month_txns:
        return format_message("no_transactions_he")
    recent = month_txns[-5:]
    rows = [
        format_message(
            "transaction_list_row_he",
            id=t.id,
            amount=t.amount,
            status=STATUS_LABELS.get(t.status, t.status),
        )
        for t in reversed(recent)
    ]
    return format_message("list_header_he") + "\n" + "\n".join(rows)


def cancel_last(user_id: int) -> str:
    t = _find_last_active(user_id)
    if t is None:
        return format_message("no_transactions_he")
    return cancel_by_id(user_id, t.id)


def cancel_by_id(user_id: int, transaction_id: int) -> str:
    t = get_transaction_by_id(user_id, transaction_id)
    if t is None:
        return format_message("transaction_not_found_he")
    if t.status == "canceled":
        return format_message("transaction_already_canceled_he")
    now = datetime.now()
    update_transaction(user_id, transaction_id, status="canceled", canceled_at=now, updated_at=now)
    return format_message("cancel_success_he", id=transaction_id)


def correct_last(user_id: int, amount_str: str, user: BotUser) -> str:
    t = _find_last_active(user_id)
    if t is None:
        return format_message("no_transactions_he")
    return correct_by_id(user_id, t.id, amount_str, user)


def correct_by_id(user_id: int, transaction_id: int, amount_str: str, user: BotUser) -> str:
    t = get_transaction_by_id(user_id, transaction_id)
    if t is None:
        return format_message("transaction_not_found_he")
    if t.status == "canceled":
        return format_message("transaction_canceled_cannot_correct_he")

    amount = _parse_amount(amount_str)
    if amount is None:
        return format_message("correction_invalid_amount_he")

    result = calculate_income_split(
        amount=amount,
        vat_included=t.vat_included,
        income_tax_rate=user.income_tax_rate,
        national_insurance_rate=user.national_insurance_rate,
        social_savings_rate=user.social_savings_rate,
    )
    now = datetime.now()
    update_transaction(
        user_id,
        transaction_id,
        amount=result["amount"],
        vat_amount=result["vat_amount"],
        base_amount=result["base_amount"],
        income_tax_amount=result["income_tax_amount"],
        national_insurance_amount=result["national_insurance_amount"],
        social_savings_amount=result["social_savings_amount"],
        total_to_save=result["total_to_save"],
        available_amount=result["available_amount"],
        remaining_amount=result["total_to_save"],
        saved_amount=0.0,
        status="open",
        updated_at=now,
    )
    return format_message(
        "correction_success_he",
        id=transaction_id,
        amount=result["amount"],
        total_to_save=result["total_to_save"],
        available_amount=result["available_amount"],
    )
