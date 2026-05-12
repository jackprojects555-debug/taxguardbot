import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BotUser:
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: str = ""
    is_blocked: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


USERS: Dict[int, BotUser] = {}
USERS_FILE = Path("data/users.json")


def _user_to_dict(user: BotUser) -> dict:
    return {
        "telegram_user_id": user.telegram_user_id,
        "username": user.username,
        "display_name": user.display_name,
        "notes": user.notes,
        "is_blocked": user.is_blocked,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


def _dict_to_user(raw: dict) -> BotUser:
    return BotUser(
        telegram_user_id=int(raw["telegram_user_id"]),
        username=raw.get("username"),
        display_name=raw.get("display_name"),
        notes=raw.get("notes") or "",
        is_blocked=bool(raw.get("is_blocked", False)),
        created_at=datetime.fromisoformat(raw["created_at"]),
        updated_at=datetime.fromisoformat(raw["updated_at"]),
    )


def _ensure_users_file():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text("{}", encoding="utf-8")


def _save_users():
    _ensure_users_file()
    payload = {str(uid): _user_to_dict(u) for uid, u in USERS.items()}
    USERS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_users():
    USERS.clear()
    _ensure_users_file()
    content = USERS_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return
    for key, raw in payload.items():
        try:
            uid = int(key)
            USERS[uid] = _dict_to_user(raw)
        except (ValueError, KeyError, TypeError):
            continue


def upsert_from_telegram(
    telegram_user_id: int,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
) -> BotUser:
    now = datetime.now()
    existing = USERS.get(telegram_user_id)
    if existing:
        changed = False
        if username is not None and existing.username != username:
            existing.username = username
            changed = True
        if display_name is not None and existing.display_name != display_name:
            existing.display_name = display_name
            changed = True
        if changed:
            existing.updated_at = now
            _save_users()
        return existing
    user = BotUser(
        telegram_user_id=telegram_user_id,
        username=username,
        display_name=display_name,
        created_at=now,
        updated_at=now,
    )
    USERS[telegram_user_id] = user
    _save_users()
    return user


def is_user_blocked(telegram_user_id: int) -> bool:
    user = USERS.get(telegram_user_id)
    return bool(user and user.is_blocked)


def list_registered_users() -> List[BotUser]:
    return list(USERS.values())


def get_user(telegram_user_id: int) -> Optional[BotUser]:
    return USERS.get(telegram_user_id)


def create_or_update_admin(
    telegram_user_id: int,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    notes: Optional[str] = None,
    is_blocked: Optional[bool] = None,
) -> BotUser:
    now = datetime.now()
    existing = USERS.get(telegram_user_id)
    if existing:
        if username is not None:
            existing.username = username
        if display_name is not None:
            existing.display_name = display_name
        if notes is not None:
            existing.notes = notes
        if is_blocked is not None:
            existing.is_blocked = is_blocked
        existing.updated_at = now
        _save_users()
        return existing
    user = BotUser(
        telegram_user_id=telegram_user_id,
        username=username,
        display_name=display_name,
        notes=notes or "",
        is_blocked=bool(is_blocked) if is_blocked is not None else False,
        created_at=now,
        updated_at=now,
    )
    USERS[telegram_user_id] = user
    _save_users()
    return user


def delete_user_record(telegram_user_id: int) -> bool:
    if telegram_user_id not in USERS:
        return False
    USERS.pop(telegram_user_id, None)
    _save_users()
    return True


def user_summary_dict(user: BotUser) -> dict:
    data = _user_to_dict(user)
    data["telegram_user_id"] = user.telegram_user_id
    return data


_load_users()
