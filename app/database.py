import sqlite3
from pathlib import Path

_DB_PATH = Path("data/taxguard.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_user_id INTEGER PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    notes TEXT NOT NULL DEFAULT '',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    onboarding_completed INTEGER NOT NULL DEFAULT 0,
    onboarding_step TEXT,
    profile_notified INTEGER NOT NULL DEFAULT 0,
    business_type TEXT NOT NULL DEFAULT 'vat_registered',
    vat_included_default INTEGER NOT NULL DEFAULT 1,
    income_tax_rate REAL NOT NULL DEFAULT 0.20,
    national_insurance_rate REAL NOT NULL DEFAULT 0.08,
    social_savings_rate REAL NOT NULL DEFAULT 0.05,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    vat_included INTEGER NOT NULL,
    vat_amount REAL NOT NULL,
    base_amount REAL NOT NULL,
    income_tax_amount REAL NOT NULL,
    national_insurance_amount REAL NOT NULL,
    social_savings_amount REAL NOT NULL,
    total_to_save REAL NOT NULL,
    remaining_amount REAL NOT NULL,
    available_amount REAL NOT NULL,
    month TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    saved_amount REAL NOT NULL DEFAULT 0.0,
    updated_at TEXT,
    canceled_at TEXT,
    PRIMARY KEY (user_id, id)
);
"""


def get_connection() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(_SCHEMA)


init_db()
