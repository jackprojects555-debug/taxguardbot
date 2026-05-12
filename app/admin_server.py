"""HTTP admin API and dashboard HTML for TaxGuardBot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from app.message_store import get_messages_snapshot, replace_messages
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
        "amount": t.amount,
        "vat_included": t.vat_included,
        "vat_amount": t.vat_amount,
        "base_amount": t.base_amount,
        "income_tax_amount": t.income_tax_amount,
        "national_insurance_amount": t.national_insurance_amount,
        "social_savings_amount": t.social_savings_amount,
        "total_to_save": t.total_to_save,
        "available_amount": t.available_amount,
        "created_at": t.created_at.isoformat(),
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


class UserCreateBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: str = ""
    is_blocked: bool = False


class UserUpdateBody(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    notes: Optional[str] = None
    is_blocked: Optional[bool] = None


@app.post("/api/admin/users", dependencies=[Depends(verify_admin)])
async def admin_create_or_replace_user(body: UserCreateBody) -> dict:
    u = create_or_update_admin(
        telegram_user_id=body.telegram_user_id,
        username=body.username,
        display_name=body.display_name,
        notes=body.notes,
        is_blocked=body.is_blocked,
    )
    return user_summary_dict(u)


@app.patch("/api/admin/users/{telegram_user_id}", dependencies=[Depends(verify_admin)])
async def admin_patch_user(telegram_user_id: int, body: UserUpdateBody) -> dict:
    if get_user(telegram_user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    u = create_or_update_admin(
        telegram_user_id=telegram_user_id,
        username=body.username,
        display_name=body.display_name,
        notes=body.notes,
        is_blocked=body.is_blocked,
    )
    return user_summary_dict(u)


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
