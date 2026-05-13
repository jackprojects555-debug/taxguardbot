"""
One-time migration: imports data/users.json and data/transactions.json into the database.

Safe to run multiple times — existing rows are skipped.
Works with both SQLite (local) and PostgreSQL (production via DATABASE_URL).

Usage:
    python scripts/migrate_json_to_sqlite.py                          # SQLite
    DATABASE_URL=postgresql://... python scripts/migrate_json_to_sqlite.py  # PostgreSQL
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_connection, init_db  # noqa: E402

USERS_FILE = Path("data/users.json")
TRANSACTIONS_FILE = Path("data/transactions.json")

_IS_POSTGRES = bool(os.getenv("DATABASE_URL"))
_INSERT_USERS = """
    INSERT INTO users (
        telegram_user_id, username, display_name, notes, is_blocked,
        onboarding_completed, onboarding_step, profile_notified,
        business_type, vat_included_default,
        income_tax_rate, national_insurance_rate, social_savings_rate,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (telegram_user_id) DO NOTHING
    """
_INSERT_TRANSACTIONS = """
    INSERT INTO transactions (
        id, user_id, amount, vat_included, vat_amount, base_amount,
        income_tax_amount, national_insurance_amount, social_savings_amount,
        total_to_save, remaining_amount, available_amount,
        month, created_at, status, saved_amount, updated_at, canceled_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (user_id, id) DO NOTHING
    """


def migrate_users(conn):
    if not USERS_FILE.exists():
        print(f"  {USERS_FILE} not found — skipping users")
        return 0

    raw = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    count = 0
    for _key, u in raw.items():
        try:
            conn.execute(
                _INSERT_USERS,
                (
                    int(u["telegram_user_id"]),
                    u.get("username"),
                    u.get("display_name"),
                    u.get("notes") or "",
                    int(bool(u.get("is_blocked", False))),
                    int(bool(u.get("onboarding_completed", True))),
                    u.get("onboarding_step"),
                    int(bool(u.get("profile_notified", False))),
                    u.get("business_type", "vat_registered"),
                    int(bool(u.get("vat_included_default", True))),
                    float(u.get("income_tax_rate", 0.20)),
                    float(u.get("national_insurance_rate", 0.08)),
                    float(u.get("social_savings_rate", 0.05)),
                    u.get("created_at", "2026-01-01T00:00:00"),
                    u.get("updated_at", "2026-01-01T00:00:00"),
                ),
            )
            count += 1
        except Exception as e:
            print(f"  WARNING: skipped user {u.get('telegram_user_id')}: {e}")
    return count


def migrate_transactions(conn):
    if not TRANSACTIONS_FILE.exists():
        print(f"  {TRANSACTIONS_FILE} not found — skipping transactions")
        return 0

    raw = json.loads(TRANSACTIONS_FILE.read_text(encoding="utf-8"))
    count = 0
    for user_id_str, txns in raw.items():
        user_id = int(user_id_str)
        for idx, t in enumerate(txns):
            try:
                created_at = t.get("created_at", "2026-01-01T00:00:00")
                total_to_save = float(t["total_to_save"])
                conn.execute(
                    _INSERT_TRANSACTIONS,
                    (
                        int(t.get("id", idx + 1)),
                        user_id,
                        float(t["amount"]),
                        int(bool(t.get("vat_included", True))),
                        float(t["vat_amount"]),
                        float(t["base_amount"]),
                        float(t["income_tax_amount"]),
                        float(t["national_insurance_amount"]),
                        float(t["social_savings_amount"]),
                        total_to_save,
                        float(t.get("remaining_amount", total_to_save)),
                        float(t["available_amount"]),
                        t.get("month") or created_at[:7],
                        created_at,
                        t.get("status", "open"),
                        float(t.get("saved_amount", 0.0)),
                        t.get("updated_at"),
                        t.get("canceled_at"),
                    ),
                )
                count += 1
            except Exception as e:
                print(f"  WARNING: skipped transaction {t.get('id')} for user {user_id}: {e}")
    return count


def main():
    backend = "PostgreSQL" if _IS_POSTGRES else "SQLite"
    print(f"Initializing database ({backend})...")
    init_db()

    with get_connection() as conn:
        print("Migrating users...")
        users = migrate_users(conn)
        print(f"  {users} user rows inserted (existing rows skipped)")

        print("Migrating transactions...")
        txns = migrate_transactions(conn)
        print(f"  {txns} transaction rows inserted (existing rows skipped)")

    print("Migration complete.")


if __name__ == "__main__":
    main()
