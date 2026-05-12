import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models import Transaction

USER_TRANSACTIONS: Dict[int, List[Transaction]] = {}
DATA_FILE = Path("data/transactions.json")


def _transaction_to_dict(transaction: Transaction) -> dict:
    return {
        "id": transaction.id,
        "amount": transaction.amount,
        "vat_included": transaction.vat_included,
        "vat_amount": transaction.vat_amount,
        "base_amount": transaction.base_amount,
        "income_tax_amount": transaction.income_tax_amount,
        "national_insurance_amount": transaction.national_insurance_amount,
        "social_savings_amount": transaction.social_savings_amount,
        "total_to_save": transaction.total_to_save,
        "remaining_amount": transaction.remaining_amount,
        "available_amount": transaction.available_amount,
        "month": transaction.month,
        "created_at": transaction.created_at.isoformat(),
        "status": transaction.status,
        "saved_amount": transaction.saved_amount,
        "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
        "canceled_at": transaction.canceled_at.isoformat() if transaction.canceled_at else None,
    }


def _dict_to_transaction(raw: dict, fallback_id: int = 1) -> Transaction:
    """Deserialize a transaction dict. fallback_id is used for old records that lack an id."""
    created_at = datetime.fromisoformat(raw["created_at"])
    total_to_save = float(raw["total_to_save"])
    return Transaction(
        amount=float(raw["amount"]),
        vat_included=bool(raw["vat_included"]),
        vat_amount=float(raw["vat_amount"]),
        base_amount=float(raw["base_amount"]),
        income_tax_amount=float(raw["income_tax_amount"]),
        national_insurance_amount=float(raw["national_insurance_amount"]),
        social_savings_amount=float(raw["social_savings_amount"]),
        total_to_save=total_to_save,
        remaining_amount=float(raw.get("remaining_amount", total_to_save)),
        available_amount=float(raw["available_amount"]),
        month=raw.get("month") or created_at.strftime("%Y-%m"),
        created_at=created_at,
        id=int(raw.get("id", fallback_id)),
        status=raw.get("status", "open"),
        saved_amount=float(raw.get("saved_amount", 0.0)),
        updated_at=datetime.fromisoformat(raw["updated_at"]) if raw.get("updated_at") else None,
        canceled_at=datetime.fromisoformat(raw["canceled_at"]) if raw.get("canceled_at") else None,
    )


def _ensure_data_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def _save_to_file():
    _ensure_data_file()
    payload = {
        str(user_id): [_transaction_to_dict(t) for t in transactions]
        for user_id, transactions in USER_TRANSACTIONS.items()
    }
    DATA_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_from_file():
    USER_TRANSACTIONS.clear()
    _ensure_data_file()
    content = DATA_FILE.read_text(encoding="utf-8").strip()
    if not content:
        DATA_FILE.write_text("{}", encoding="utf-8")
        return

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        payload = {}

    for user_id_str, raw_transactions in payload.items():
        user_id = int(user_id_str)
        USER_TRANSACTIONS[user_id] = [
            _dict_to_transaction(raw, idx + 1)
            for idx, raw in enumerate(raw_transactions)
        ]


def add_transaction(user_id: int, transaction: Transaction) -> Transaction:
    if user_id not in USER_TRANSACTIONS:
        USER_TRANSACTIONS[user_id] = []
    transaction.id = len(USER_TRANSACTIONS[user_id]) + 1
    USER_TRANSACTIONS[user_id].append(transaction)
    _save_to_file()
    return transaction


def get_transactions(user_id: int) -> List[Transaction]:
    return USER_TRANSACTIONS.get(user_id, [])


def get_transaction_by_id(user_id: int, transaction_id: int) -> Optional[Transaction]:
    for t in USER_TRANSACTIONS.get(user_id, []):
        if t.id == transaction_id:
            return t
    return None


def update_transaction(user_id: int, transaction_id: int, **kwargs) -> Optional[Transaction]:
    """Update mutable fields on a stored transaction and persist."""
    t = get_transaction_by_id(user_id, transaction_id)
    if t is None:
        return None
    allowed = {"status", "saved_amount", "remaining_amount", "updated_at", "canceled_at"}
    for field, value in kwargs.items():
        if field in allowed:
            setattr(t, field, value)
    _save_to_file()
    return t


def clear_transactions(user_id: int):
    USER_TRANSACTIONS.pop(user_id, None)
    _save_to_file()


def list_user_ids_with_transactions() -> List[int]:
    return sorted(USER_TRANSACTIONS.keys())


def delete_all_transactions(user_id: int) -> None:
    clear_transactions(user_id)


_load_from_file()
