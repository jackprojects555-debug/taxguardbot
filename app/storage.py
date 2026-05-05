from typing import Dict, List
from app.models import Transaction


# storage לפי משתמש (telegram_id)
USER_TRANSACTIONS: Dict[int, List[Transaction]] = {}


def add_transaction(user_id: int, transaction: Transaction):
    if user_id not in USER_TRANSACTIONS:
        USER_TRANSACTIONS[user_id] = []

    USER_TRANSACTIONS[user_id].append(transaction)


def get_transactions(user_id: int) -> List[Transaction]:
    return USER_TRANSACTIONS.get(user_id, [])


def clear_transactions(user_id: int):
    USER_TRANSACTIONS.pop(user_id, None)