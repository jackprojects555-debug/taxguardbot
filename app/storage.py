from datetime import datetime
from typing import List, Optional

from app.database import get_connection
from app.models import Transaction


def _row_to_transaction(row) -> Transaction:
    return Transaction(
        id=row["id"],
        amount=row["amount"],
        vat_included=bool(row["vat_included"]),
        vat_amount=row["vat_amount"],
        base_amount=row["base_amount"],
        income_tax_amount=row["income_tax_amount"],
        national_insurance_amount=row["national_insurance_amount"],
        social_savings_amount=row["social_savings_amount"],
        pension_amount=row["pension_amount"] if row["pension_amount"] is not None else 0.0,
        total_to_save=row["total_to_save"],
        remaining_amount=row["remaining_amount"],
        available_amount=row["available_amount"],
        month=row["month"],
        created_at=datetime.fromisoformat(row["created_at"]),
        status=row["status"],
        saved_amount=row["saved_amount"],
        updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        canceled_at=datetime.fromisoformat(row["canceled_at"]) if row["canceled_at"] else None,
    )


def add_transaction(user_id: int, transaction: Transaction) -> Transaction:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM transactions WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        next_id = row["next_id"]
        transaction.id = next_id
        conn.execute(
            """
            INSERT INTO transactions (
                id, user_id, amount, vat_included, vat_amount, base_amount,
                income_tax_amount, national_insurance_amount, social_savings_amount,
                pension_amount, total_to_save, remaining_amount, available_amount,
                month, created_at, status, saved_amount, updated_at, canceled_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                next_id,
                user_id,
                transaction.amount,
                int(transaction.vat_included),
                transaction.vat_amount,
                transaction.base_amount,
                transaction.income_tax_amount,
                transaction.national_insurance_amount,
                transaction.social_savings_amount,
                transaction.pension_amount,
                transaction.total_to_save,
                transaction.remaining_amount,
                transaction.available_amount,
                transaction.month,
                transaction.created_at.isoformat(),
                transaction.status,
                transaction.saved_amount,
                transaction.updated_at.isoformat() if transaction.updated_at else None,
                transaction.canceled_at.isoformat() if transaction.canceled_at else None,
            ),
        )
    return transaction


def get_transactions(user_id: int) -> List[Transaction]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        ).fetchall()
    return [_row_to_transaction(r) for r in rows]


def get_transaction_by_id(user_id: int, transaction_id: int) -> Optional[Transaction]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND id = ?",
            (user_id, transaction_id),
        ).fetchone()
    return _row_to_transaction(row) if row else None


def update_transaction(user_id: int, transaction_id: int, **kwargs) -> Optional[Transaction]:
    allowed = {
        "status",
        "saved_amount",
        "remaining_amount",
        "updated_at",
        "canceled_at",
        "amount",
        "vat_amount",
        "base_amount",
        "income_tax_amount",
        "national_insurance_amount",
        "pension_amount",
        "social_savings_amount",
        "total_to_save",
        "available_amount",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_transaction_by_id(user_id, transaction_id)

    def _serialize(v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    set_clause = ", ".join(f"{col} = ?" for col in updates)
    values = [_serialize(v) for v in updates.values()]
    values += [user_id, transaction_id]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE transactions SET {set_clause} WHERE user_id = ? AND id = ?",
            values,
        )
    return get_transaction_by_id(user_id, transaction_id)


def clear_transactions(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))


def list_user_ids_with_transactions() -> List[int]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT user_id FROM transactions ORDER BY user_id ASC"
        ).fetchall()
    return [r["user_id"] for r in rows]


def delete_all_transactions(user_id: int) -> None:
    clear_transactions(user_id)
