from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.database import get_connection


@dataclass
class BotUser:
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: str = ""
    is_blocked: bool = False
    onboarding_completed: bool = False
    onboarding_step: Optional[str] = None
    profile_notified: bool = False
    business_type: str = "vat_registered"
    vat_included_default: bool = True
    income_tax_rate: float = 0.20
    national_insurance_rate: float = 0.08
    social_savings_rate: float = 0.05
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


def _row_to_user(row) -> BotUser:
    return BotUser(
        telegram_user_id=row["telegram_user_id"],
        username=row["username"],
        display_name=row["display_name"],
        notes=row["notes"] or "",
        is_blocked=bool(row["is_blocked"]),
        onboarding_completed=bool(row["onboarding_completed"]),
        onboarding_step=row["onboarding_step"],
        profile_notified=bool(row["profile_notified"]),
        business_type=row["business_type"],
        vat_included_default=bool(row["vat_included_default"]),
        income_tax_rate=row["income_tax_rate"],
        national_insurance_rate=row["national_insurance_rate"],
        social_savings_rate=row["social_savings_rate"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def upsert_from_telegram(
    telegram_user_id: int,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
) -> BotUser:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_user_id, username, display_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                username = COALESCE(excluded.username, username),
                display_name = COALESCE(excluded.display_name, display_name),
                updated_at = CASE
                    WHEN excluded.username IS NOT username
                         OR excluded.display_name IS NOT display_name
                    THEN excluded.updated_at
                    ELSE updated_at
                END
            """,
            (telegram_user_id, username, display_name, now, now),
        )
    return get_user(telegram_user_id)


def update_user_profile(telegram_user_id: int, **kwargs) -> Optional[BotUser]:
    allowed = {
        "business_type",
        "vat_included_default",
        "income_tax_rate",
        "national_insurance_rate",
        "social_savings_rate",
        "onboarding_completed",
        "onboarding_step",
        "profile_notified",
        "notes",
        "is_blocked",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_user(telegram_user_id)

    updates["updated_at"] = datetime.now().isoformat()

    def _serialize(v):
        if isinstance(v, bool):
            return int(v)
        return v

    set_clause = ", ".join(f"{col} = ?" for col in updates)
    values = [_serialize(v) for v in updates.values()]
    values.append(telegram_user_id)

    with get_connection() as conn:
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE telegram_user_id = ?",
            values,
        )
    return get_user(telegram_user_id)


def is_user_blocked(telegram_user_id: int) -> bool:
    user = get_user(telegram_user_id)
    return bool(user and user.is_blocked)


def list_registered_users() -> List[BotUser]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY telegram_user_id ASC").fetchall()
    return [_row_to_user(r) for r in rows]


def get_user(telegram_user_id: int) -> Optional[BotUser]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_user_id = ?", (telegram_user_id,)
        ).fetchone()
    return _row_to_user(row) if row else None


def create_or_update_admin(
    telegram_user_id: int,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    notes: Optional[str] = None,
    is_blocked: Optional[bool] = None,
) -> BotUser:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_user_id, username, display_name, notes, is_blocked,
                               created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                username = COALESCE(excluded.username, username),
                display_name = COALESCE(excluded.display_name, display_name),
                notes = COALESCE(excluded.notes, notes),
                is_blocked = COALESCE(excluded.is_blocked, is_blocked),
                updated_at = excluded.updated_at
            """,
            (
                telegram_user_id,
                username,
                display_name,
                notes or "",
                int(is_blocked) if is_blocked is not None else None,
                now,
                now,
            ),
        )
    return get_user(telegram_user_id)


def delete_user_record(telegram_user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM users WHERE telegram_user_id = ?", (telegram_user_id,))
    return cursor.rowcount > 0


def user_summary_dict(user: BotUser) -> dict:
    return {
        "telegram_user_id": user.telegram_user_id,
        "username": user.username,
        "display_name": user.display_name,
        "notes": user.notes,
        "is_blocked": user.is_blocked,
        "onboarding_completed": user.onboarding_completed,
        "onboarding_step": user.onboarding_step,
        "profile_notified": user.profile_notified,
        "business_type": user.business_type,
        "vat_included_default": user.vat_included_default,
        "income_tax_rate": user.income_tax_rate,
        "national_insurance_rate": user.national_insurance_rate,
        "social_savings_rate": user.social_savings_rate,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
