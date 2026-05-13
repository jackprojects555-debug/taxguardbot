import os
import sqlite3
from pathlib import Path

_DB_PATH = Path("data/taxguard.db")

# DOUBLE PRECISION is accepted by SQLite (maps to REAL affinity) and is the
# correct 8-byte float type in PostgreSQL. BIGINT is accepted by SQLite too.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_user_id BIGINT PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    notes TEXT NOT NULL DEFAULT '',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    onboarding_completed INTEGER NOT NULL DEFAULT 0,
    onboarding_step TEXT,
    profile_notified INTEGER NOT NULL DEFAULT 0,
    business_type TEXT NOT NULL DEFAULT 'vat_registered',
    vat_included_default INTEGER NOT NULL DEFAULT 1,
    income_tax_rate DOUBLE PRECISION NOT NULL DEFAULT 0.20,
    national_insurance_rate DOUBLE PRECISION NOT NULL DEFAULT 0.08,
    social_savings_rate DOUBLE PRECISION NOT NULL DEFAULT 0.05,
    preferred_language TEXT NOT NULL DEFAULT 'he',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    vat_included INTEGER NOT NULL,
    vat_amount DOUBLE PRECISION NOT NULL,
    base_amount DOUBLE PRECISION NOT NULL,
    income_tax_amount DOUBLE PRECISION NOT NULL,
    national_insurance_amount DOUBLE PRECISION NOT NULL,
    social_savings_amount DOUBLE PRECISION NOT NULL,
    total_to_save DOUBLE PRECISION NOT NULL,
    remaining_amount DOUBLE PRECISION NOT NULL,
    available_amount DOUBLE PRECISION NOT NULL,
    month TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    saved_amount DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    updated_at TEXT,
    canceled_at TEXT,
    PRIMARY KEY (user_id, id)
);

CREATE TABLE IF NOT EXISTS bot_texts (
    key TEXT NOT NULL,
    language TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (key, language)
)
"""


class _Conn:
    """Wraps a raw DB connection, normalising ? vs %s across SQLite and PostgreSQL."""

    def __init__(self, raw, is_postgres: bool):
        self._raw = raw
        self._is_postgres = is_postgres

    def _adapt(self, sql: str) -> str:
        return sql.replace("?", "%s") if self._is_postgres else sql

    def execute(self, sql: str, params=()):
        adapted = self._adapt(sql)
        if self._is_postgres:
            cur = self._raw.cursor()
            cur.execute(adapted, params)
            return cur
        return self._raw.execute(adapted, params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self._raw.commit()
        else:
            self._raw.rollback()
        self._raw.close()


def get_connection() -> _Conn:
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        return _Conn(conn, is_postgres=True)
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return _Conn(conn, is_postgres=False)


_MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN preferred_language TEXT NOT NULL DEFAULT 'he'",
]


def _apply_migrations(conn) -> None:
    for stmt in _MIGRATIONS:
        try:
            conn.execute(stmt)
        except Exception:
            pass  # column already exists


def init_db() -> None:
    statements = [s.strip() for s in _SCHEMA.split(";") if s.strip()]
    with get_connection() as conn:
        for stmt in statements:
            conn.execute(stmt)
        _apply_migrations(conn)


init_db()
