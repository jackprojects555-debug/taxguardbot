"""HTTP admin API and dashboard HTML for TaxGuardBot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from app.cms import delete_text, get_text, list_texts, set_text
from app.message_store import default_message_keys, get_messages_snapshot, replace_messages
from app.storage import (
    delete_all_transactions,
    get_transactions,
    list_user_ids_with_transactions,
)
from app.user_storage import (
    create_or_update_admin,
    delete_user_record,
    get_user,
    list_registered_users,
    update_user_profile,
    user_summary_dict,
)

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()

STATIC_PATH = Path(__file__).resolve().parent / "static" / "admin.html"

app = FastAPI(title="TaxGuard Admin", version="1")


def _verify_authorization_header(authorization: str | None) -> None:
    if not ADMIN_TOKEN:
        raise HTTPException(
            status_code=503,
            detail=(
                "ADMIN_TOKEN is not configured. Set ADMIN_TOKEN in the "
                "environment before using the admin API."
            ),
        )
    token = (authorization or "").strip()
    expected = f"Bearer {ADMIN_TOKEN}"
    if token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_admin(authorization: str | None = Header(default=None)) -> None:
    _verify_authorization_header(authorization)


def _transaction_to_api(t) -> dict:
    return {
        "id": t.id,
        "amount": t.amount,
        "vat_included": t.vat_included,
        "vat_amount": t.vat_amount,
        "base_amount": t.base_amount,
        "income_tax_amount": t.income_tax_amount,
        "national_insurance_amount": t.national_insurance_amount,
        "social_savings_amount": t.social_savings_amount,
        "total_to_save": t.total_to_save,
        "remaining_amount": t.remaining_amount,
        "available_amount": t.available_amount,
        "month": t.month,
        "created_at": t.created_at.isoformat(),
        "status": t.status,
        "saved_amount": t.saved_amount,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        "canceled_at": t.canceled_at.isoformat() if t.canceled_at else None,
    }


def _user_row(telegram_user_id: int) -> dict:
    u = get_user(telegram_user_id)
    txns = get_transactions(telegram_user_id)
    if u:
        row = user_summary_dict(u)
        row["implicit_only"] = False
    else:
        row = {
            "telegram_user_id": telegram_user_id,
            "username": None,
            "display_name": None,
            "notes": "",
            "is_blocked": False,
            "created_at": None,
            "updated_at": None,
            "implicit_only": True,
        }
    row["transaction_count"] = len(txns)
    return row


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/admin/users", dependencies=[Depends(verify_admin)])
async def admin_list_users() -> dict:
    registered = {u.telegram_user_id: u for u in list_registered_users()}
    all_ids = sorted(set(registered.keys()) | set(list_user_ids_with_transactions()))
    return {"users": [_user_row(uid) for uid in all_ids]}


_VAT_PERIODS = ("monthly", "bi_monthly")


class UserCreateBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: str = ""
    is_blocked: bool = False
    business_type: str = "vat_registered"
    vat_period: str = "monthly"
    vat_included_default: bool = True
    income_tax_rate: float = Field(0.20, ge=0.0, le=1.0)
    national_insurance_rate: float = Field(0.08, ge=0.0, le=1.0)
    social_savings_rate: float = Field(0.05, ge=0.0, le=1.0)
    onboarding_completed: bool = False
    profile_notified: bool = False

    @field_validator("business_type")
    @classmethod
    def validate_business_type(cls, v: str) -> str:
        if v not in ("vat_registered", "vat_exempt"):
            raise ValueError("business_type must be 'vat_registered' or 'vat_exempt'")
        return v

    @field_validator("vat_period")
    @classmethod
    def validate_vat_period(cls, v: str) -> str:
        if v not in _VAT_PERIODS:
            raise ValueError(f"vat_period must be one of: {', '.join(_VAT_PERIODS)}")
        return v


class UserUpdateBody(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: Optional[str] = None
    is_blocked: Optional[bool] = None
    business_type: Optional[str] = None
    vat_period: Optional[str] = None
    vat_included_default: Optional[bool] = None
    income_tax_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    national_insurance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    social_savings_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    onboarding_completed: Optional[bool] = None
    profile_notified: Optional[bool] = None

    @field_validator("business_type")
    @classmethod
    def validate_business_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("vat_registered", "vat_exempt"):
            raise ValueError("business_type must be 'vat_registered' or 'vat_exempt'")
        return v

    @field_validator("vat_period")
    @classmethod
    def validate_vat_period(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in _VAT_PERIODS:
            raise ValueError(f"vat_period must be one of: {', '.join(_VAT_PERIODS)}")
        return v


@app.post("/api/admin/users", dependencies=[Depends(verify_admin)])
async def admin_create_or_replace_user(body: UserCreateBody) -> dict:
    create_or_update_admin(
        telegram_user_id=body.telegram_user_id,
        username=body.username,
        display_name=body.display_name,
        notes=body.notes,
        is_blocked=body.is_blocked,
    )
    update_user_profile(
        body.telegram_user_id,
        business_type=body.business_type,
        vat_period=body.vat_period,
        vat_included_default=body.vat_included_default,
        income_tax_rate=body.income_tax_rate,
        national_insurance_rate=body.national_insurance_rate,
        social_savings_rate=body.social_savings_rate,
        onboarding_completed=body.onboarding_completed,
        profile_notified=body.profile_notified,
    )
    return user_summary_dict(get_user(body.telegram_user_id))


@app.patch("/api/admin/users/{telegram_user_id}", dependencies=[Depends(verify_admin)])
async def admin_patch_user(telegram_user_id: int, body: UserUpdateBody) -> dict:
    if get_user(telegram_user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    create_or_update_admin(
        telegram_user_id=telegram_user_id,
        username=body.username,
        display_name=body.display_name,
        notes=body.notes,
        is_blocked=body.is_blocked,
    )
    profile_updates = {
        k: v
        for k, v in {
            "business_type": body.business_type,
            "vat_period": body.vat_period,
            "vat_included_default": body.vat_included_default,
            "income_tax_rate": body.income_tax_rate,
            "national_insurance_rate": body.national_insurance_rate,
            "social_savings_rate": body.social_savings_rate,
            "onboarding_completed": body.onboarding_completed,
            "profile_notified": body.profile_notified,
        }.items()
        if v is not None
    }
    if profile_updates:
        update_user_profile(telegram_user_id, **profile_updates)
    return user_summary_dict(get_user(telegram_user_id))


@app.delete("/api/admin/users/{telegram_user_id}", dependencies=[Depends(verify_admin)])
async def admin_delete_user(
    telegram_user_id: int,
    delete_transactions: bool = False,
) -> dict:
    deleted_registry = delete_user_record(telegram_user_id)
    if delete_transactions:
        delete_all_transactions(telegram_user_id)
    return {
        "deleted_registry": deleted_registry,
        "cleared_transactions": bool(delete_transactions),
    }


@app.get(
    "/api/admin/users/{telegram_user_id}/transactions",
    dependencies=[Depends(verify_admin)],
)
async def admin_user_transactions(telegram_user_id: int) -> dict:
    return {"transactions": [_transaction_to_api(t) for t in get_transactions(telegram_user_id)]}


_KNOWN_LANGS = ("he", "en")


def _split_message_key(combined: str):
    """Split 'help_he' → ('help', 'he'). Returns (None, None) if no language suffix."""
    for lang in _KNOWN_LANGS:
        if combined.endswith(f"_{lang}"):
            return combined[: -(len(lang) + 1)], lang
    return None, None


def _effective_entries_for_key(key: str) -> list:
    defaults = default_message_keys()
    result = []
    for lang in _KNOWN_LANGS:
        db_content = get_text(key, lang)
        if db_content is not None:
            result.append({"language": lang, "content": db_content, "source": "db"})
        elif f"{key}_{lang}" in defaults:
            result.append(
                {"language": lang, "content": defaults[f"{key}_{lang}"], "source": "default"}
            )
    return result


@app.get("/api/admin/texts", dependencies=[Depends(verify_admin)])
async def admin_list_texts() -> dict:
    defaults = default_message_keys()
    known: dict[tuple, str] = {}
    for combined, content in defaults.items():
        base_key, lang = _split_message_key(combined)
        if base_key is not None:
            known[(base_key, lang)] = content

    db_entries = {(r["key"], r["language"]): r for r in list_texts()}
    all_pairs = sorted(set(known.keys()) | set(db_entries.keys()))
    result = []
    for key, lang in all_pairs:
        if (key, lang) in db_entries:
            r = db_entries[(key, lang)]
            result.append(
                {
                    "key": key,
                    "language": lang,
                    "content": r["content"],
                    "source": "db",
                    "updated_at": r["updated_at"],
                }
            )
        else:
            result.append(
                {
                    "key": key,
                    "language": lang,
                    "content": known[(key, lang)],
                    "source": "default",
                    "updated_at": None,
                }
            )
    return {"texts": result}


@app.get("/api/admin/texts/{key}", dependencies=[Depends(verify_admin)])
async def admin_get_text_key(key: str) -> dict:
    entries = _effective_entries_for_key(key)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No text entries found for key: {key}")
    return {"key": key, "entries": entries}


class TextPutBody(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        return v


@app.put("/api/admin/texts/{key}/{lang}", dependencies=[Depends(verify_admin)])
async def admin_put_text(key: str, lang: str, body: TextPutBody) -> dict:
    if lang not in _KNOWN_LANGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {lang}. Use one of: {', '.join(_KNOWN_LANGS)}",
        )
    set_text(key, lang, body.content)
    return {"key": key, "language": lang, "content": body.content}


@app.delete("/api/admin/texts/{key}/{lang}", dependencies=[Depends(verify_admin)])
async def admin_delete_text(key: str, lang: str) -> dict:
    deleted = delete_text(key, lang)
    return {"deleted": deleted}


class MessagesReplaceBody(BaseModel):
    messages: Dict[str, str]

    @field_validator("messages", mode="before")
    @classmethod
    def ensure_str_values(cls, v: Any):
        if not isinstance(v, dict):
            raise ValueError("messages must be an object")
        out: Dict[str, str] = {}
        for key, val in v.items():
            if val is None:
                continue
            out[str(key)] = str(val)
        return out


@app.get("/api/admin/messages", dependencies=[Depends(verify_admin)])
async def admin_get_messages() -> dict:
    return {"messages": get_messages_snapshot()}


@app.put("/api/admin/messages", dependencies=[Depends(verify_admin)])
async def admin_put_messages(body: MessagesReplaceBody) -> dict:
    replace_messages(body.messages)
    return {"messages": get_messages_snapshot()}


@app.get("/admin")
@app.get("/")
async def admin_ui():
    if not STATIC_PATH.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Missing admin UI file at {STATIC_PATH}",
        )
    return FileResponse(STATIC_PATH, media_type="text/html; charset=utf-8")


def main():
    import uvicorn

    host = os.getenv("ADMIN_HOST", "127.0.0.1")
    port = int(os.getenv("ADMIN_PORT", "8080"))
    uvicorn.run("app.admin_server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
