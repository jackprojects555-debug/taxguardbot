from datetime import datetime
from typing import Optional

from app.message_store import format_message
from app.models import Transaction
from app.storage import get_transactions, update_transaction


def _find_latest_open(user_id: int) -> Optional[Transaction]:
    """Return the most recent open or partially_saved transaction for the user."""
    for t in reversed(get_transactions(user_id)):
        if t.status in ("open", "partially_saved"):
            return t
    return None


def _parse_transfer_amount(text: str) -> Optional[float]:
    """Parse a transfer amount string. Returns None if invalid or non-positive."""
    t = text.strip().replace(",", "").replace("₪", "").replace(" ", "")
    try:
        val = float(t)
    except ValueError:
        return None
    return val if val > 0 else None


def process_transfer(user_id: int, amount_text: str) -> str:
    """
    Handle an העברתי command.
    amount_text: "" for full transfer, numeric string for partial.
    Returns the formatted Hebrew reply.
    """
    target = _find_latest_open(user_id)
    if target is None:
        return format_message("transfer_no_open_he")

    if amount_text:
        amount = _parse_transfer_amount(amount_text)
        if amount is None:
            return format_message("transfer_invalid_amount_he")
        amount = min(amount, target.remaining_amount)
    else:
        amount = target.remaining_amount

    new_saved = target.saved_amount + amount
    new_remaining = round(target.remaining_amount - amount, 2)
    now = datetime.now()

    if new_remaining <= 0:
        update_transaction(
            user_id,
            target.id,
            saved_amount=new_saved,
            remaining_amount=0.0,
            status="fully_saved",
            updated_at=now,
        )
        return format_message("transfer_full_success_he", amount=new_saved)

    update_transaction(
        user_id,
        target.id,
        saved_amount=new_saved,
        remaining_amount=new_remaining,
        status="partially_saved",
        updated_at=now,
    )
    return format_message("transfer_partial_success_he", saved=new_saved, remaining=new_remaining)
