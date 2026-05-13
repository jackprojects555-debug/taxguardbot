"""
CMS layer for bot texts.

t(key, lang, **kwargs) is the primary entry point:
  1. Try bot_texts DB table (admin-editable overrides).
  2. Fall back to message_store.py hard-coded default for f"{key}_{lang}".
  3. Fall back to f"{key}_he" if the language variant is missing.
  4. Return a bracketed debug marker if the key is completely unknown.

get_text / set_text / delete_text give the admin API direct DB access.
list_texts returns all current DB overrides.
"""

from datetime import datetime
from typing import Optional

from app.database import get_connection
from app.message_store import format_message


def t(key: str, lang: str, **kwargs) -> str:
    content = get_text(key, lang) or _fallback(key, lang) or f"[{key}_{lang}]"
    if not kwargs:
        return content
    try:
        return content.format(**kwargs)
    except (KeyError, ValueError):
        return content


def _fallback(key: str, lang: str) -> str:
    return format_message(f"{key}_{lang}") or format_message(f"{key}_he")


def get_text(key: str, lang: str) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT content FROM bot_texts WHERE key = ? AND language = ?",
            (key, lang),
        ).fetchone()
    return row["content"] if row else None


def set_text(key: str, lang: str, content: str) -> None:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO bot_texts (key, language, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (key, language) DO UPDATE SET
                content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (key, lang, content, now),
        )


def delete_text(key: str, lang: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM bot_texts WHERE key = ? AND language = ?",
            (key, lang),
        )
    return cursor.rowcount > 0


def list_texts() -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT key, language, content, updated_at FROM bot_texts ORDER BY key, language"
        ).fetchall()
    return [dict(r) for r in rows]
