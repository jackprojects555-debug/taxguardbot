import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app.models import Transaction

# storage לפי משתמש (telegram_id)
USER_TRANSACTIONS: Dict[int, List[Transaction]] = {}
DATA_FILE = Path("data/transactions.json")


def _transaction_to_dict(transaction: Transaction) -> dict:
    return {
        "amount": transaction.amount,
        "vat_included": transaction.vat_included,
        "vat_amount": transaction.vat_amount,
        "base_amount": transaction.base_amount,
        "income_tax_amount": transaction.income_tax_amount,
        "national_insurance_amount": transaction.national_insurance_amount,
        "social_savings_amount": transaction.social_savings_amount,
        "total_to_save": transaction.total_to_save,
        "available_amount": transaction.available_amount,
        "created_at": transaction.created_at.isoformat(),
    }


def _dict_to_transaction(raw: dict) -> Transaction:
    return Transaction(
        amount=raw["amount"],
        vat_included=raw["vat_included"],
        vat_amount=raw["vat_amount"],
        base_amount=raw["base_amount"],
        income_tax_amount=raw["income_tax_amount"],
        national_insurance_amount=raw["national_insurance_amount"],
        social_savings_amount=raw["social_savings_amount"],
        total_to_save=raw["total_to_save"],
        available_amount=raw["available_amount"],
        created_at=datetime.fromisoformat(raw["created_at"]),
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
            _dict_to_transaction(raw_transaction) for raw_transaction in raw_transactions
        ]


def add_transaction(user_id: int, transaction: Transaction):
    if user_id not in USER_TRANSACTIONS:
        USER_TRANSACTIONS[user_id] = []

    USER_TRANSACTIONS[user_id].append(transaction)
    _save_to_file()


def get_transactions(user_id: int) -> List[Transaction]:
    return USER_TRANSACTIONS.get(user_id, [])


def clear_transactions(user_id: int):
    USER_TRANSACTIONS.pop(user_id, None)
    _save_to_file()


def list_user_ids_with_transactions() -> List[int]:
    return sorted(USER_TRANSACTIONS.keys())


def delete_all_transactions(user_id: int) -> None:
    """Remove stored transactions for user (empty bucket). Same persistence as reset."""
    clear_transactions(user_id)


_load_from_file()
