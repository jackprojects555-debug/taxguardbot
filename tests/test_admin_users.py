"""Tests for admin user endpoints — focused on vat_period (V2-009)."""

import pytest
from starlette.testclient import TestClient

import app.admin_server as admin_server
from app.admin_server import app
from app.user_storage import get_user, upsert_from_telegram

TEST_TOKEN = "test-admin-token"
AUTH = {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_admin_token(monkeypatch):
    monkeypatch.setattr(admin_server, "ADMIN_TOKEN", TEST_TOKEN)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# vat_period default
# ---------------------------------------------------------------------------


def test_created_user_has_monthly_vat_period_by_default(client):
    resp = client.post(
        "/api/admin/users",
        headers=AUTH,
        json={"telegram_user_id": 1},
    )
    assert resp.status_code == 200
    assert resp.json()["vat_period"] == "monthly"


# ---------------------------------------------------------------------------
# POST /api/admin/users — vat_period field
# ---------------------------------------------------------------------------


def test_create_user_with_bi_monthly_vat_period(client):
    resp = client.post(
        "/api/admin/users",
        headers=AUTH,
        json={"telegram_user_id": 2, "vat_period": "bi_monthly"},
    )
    assert resp.status_code == 200
    assert resp.json()["vat_period"] == "bi_monthly"


def test_create_user_invalid_vat_period_rejected(client):
    resp = client.post(
        "/api/admin/users",
        headers=AUTH,
        json={"telegram_user_id": 3, "vat_period": "quarterly"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /api/admin/users/{id} — vat_period field
# ---------------------------------------------------------------------------


def test_patch_user_updates_vat_period(client):
    upsert_from_telegram(telegram_user_id=10)
    resp = client.patch(
        "/api/admin/users/10",
        headers=AUTH,
        json={"vat_period": "bi_monthly"},
    )
    assert resp.status_code == 200
    assert resp.json()["vat_period"] == "bi_monthly"
    assert get_user(10).vat_period == "bi_monthly"


def test_patch_user_invalid_vat_period_rejected(client):
    upsert_from_telegram(telegram_user_id=11)
    resp = client.patch(
        "/api/admin/users/11",
        headers=AUTH,
        json={"vat_period": "weekly"},
    )
    assert resp.status_code == 422


def test_patch_user_vat_period_back_to_monthly(client):
    upsert_from_telegram(telegram_user_id=12)
    client.patch("/api/admin/users/12", headers=AUTH, json={"vat_period": "bi_monthly"})
    resp = client.patch("/api/admin/users/12", headers=AUTH, json={"vat_period": "monthly"})
    assert resp.status_code == 200
    assert resp.json()["vat_period"] == "monthly"
