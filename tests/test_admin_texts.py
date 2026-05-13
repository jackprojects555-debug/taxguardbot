"""Tests for admin CMS text endpoints: /api/admin/texts."""

import pytest
from starlette.testclient import TestClient

import app.admin_server as admin_server
from app.admin_server import app
from app.cms import get_text

TEST_TOKEN = "test-admin-token"
AUTH = {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_admin_token(monkeypatch):
    monkeypatch.setattr(admin_server, "ADMIN_TOKEN", TEST_TOKEN)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/admin/texts
# ---------------------------------------------------------------------------


def test_list_texts_returns_200(client):
    resp = client.get("/api/admin/texts", headers=AUTH)
    assert resp.status_code == 200


def test_list_texts_response_has_texts_key(client):
    resp = client.get("/api/admin/texts", headers=AUTH)
    assert "texts" in resp.json()


def test_list_texts_includes_help_defaults(client):
    items = client.get("/api/admin/texts", headers=AUTH).json()["texts"]
    keys = {(i["key"], i["language"]) for i in items}
    assert ("help", "he") in keys
    assert ("help", "en") in keys


def test_list_texts_default_has_source_default(client):
    items = client.get("/api/admin/texts", headers=AUTH).json()["texts"]
    help_he = next(i for i in items if i["key"] == "help" and i["language"] == "he")
    assert help_he["source"] == "default"
    assert help_he["updated_at"] is None
    assert help_he["content"]


def test_list_texts_db_override_shows_source_db(client):
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "Custom"})
    items = client.get("/api/admin/texts", headers=AUTH).json()["texts"]
    help_he = next(i for i in items if i["key"] == "help" and i["language"] == "he")
    assert help_he["source"] == "db"
    assert help_he["content"] == "Custom"
    assert help_he["updated_at"] is not None


def test_list_texts_requires_auth(client):
    resp = client.get("/api/admin/texts")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/admin/texts/{key}
# ---------------------------------------------------------------------------


def test_get_key_known_returns_200(client):
    resp = client.get("/api/admin/texts/help", headers=AUTH)
    assert resp.status_code == 200


def test_get_key_response_shape(client):
    body = client.get("/api/admin/texts/help", headers=AUTH).json()
    assert body["key"] == "help"
    assert isinstance(body["entries"], list)
    assert len(body["entries"]) >= 1


def test_get_key_includes_both_languages(client):
    entries = client.get("/api/admin/texts/help", headers=AUTH).json()["entries"]
    langs = {e["language"] for e in entries}
    assert "he" in langs
    assert "en" in langs


def test_get_key_default_fallback_populated(client):
    entries = client.get("/api/admin/texts/help", headers=AUTH).json()["entries"]
    he = next(e for e in entries if e["language"] == "he")
    assert he["source"] == "default"
    assert he["content"]


def test_get_key_db_override_returned(client):
    client.put("/api/admin/texts/help/en", headers=AUTH, json={"content": "Custom EN"})
    entries = client.get("/api/admin/texts/help", headers=AUTH).json()["entries"]
    en = next(e for e in entries if e["language"] == "en")
    assert en["source"] == "db"
    assert en["content"] == "Custom EN"


def test_get_key_unknown_returns_404(client):
    resp = client.get("/api/admin/texts/totally_unknown_xyz123", headers=AUTH)
    assert resp.status_code == 404


def test_get_key_requires_auth(client):
    resp = client.get("/api/admin/texts/help")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /api/admin/texts/{key}/{lang}
# ---------------------------------------------------------------------------


def test_put_text_returns_200(client):
    resp = client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "Override"})
    assert resp.status_code == 200


def test_put_text_response_shape(client):
    body = client.put(
        "/api/admin/texts/help/he", headers=AUTH, json={"content": "Test content"}
    ).json()
    assert body["key"] == "help"
    assert body["language"] == "he"
    assert body["content"] == "Test content"


def test_put_text_persists_to_db(client):
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "Persisted"})
    assert get_text("help", "he") == "Persisted"


def test_put_text_overwrites_existing(client):
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "First"})
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "Second"})
    assert get_text("help", "he") == "Second"


def test_put_text_empty_content_rejected(client):
    resp = client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "   "})
    assert resp.status_code == 422


def test_put_text_empty_string_rejected(client):
    resp = client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": ""})
    assert resp.status_code == 422


def test_put_text_unsupported_lang_rejected(client):
    resp = client.put("/api/admin/texts/help/fr", headers=AUTH, json={"content": "Bonjour"})
    assert resp.status_code == 400


def test_put_text_requires_auth(client):
    resp = client.put("/api/admin/texts/help/he", json={"content": "No auth"})
    assert resp.status_code == 401


def test_put_text_custom_key_allowed(client):
    resp = client.put(
        "/api/admin/texts/my_custom_key/he", headers=AUTH, json={"content": "Custom value"}
    )
    assert resp.status_code == 200
    assert get_text("my_custom_key", "he") == "Custom value"


# ---------------------------------------------------------------------------
# DELETE /api/admin/texts/{key}/{lang}
# ---------------------------------------------------------------------------


def test_delete_text_removes_override(client):
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "To delete"})
    resp = client.delete("/api/admin/texts/help/he", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    assert get_text("help", "he") is None


def test_delete_text_not_found_returns_false(client):
    resp = client.delete("/api/admin/texts/nonexistent_key/he", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is False


def test_delete_text_restores_to_default(client):
    client.put("/api/admin/texts/help/he", headers=AUTH, json={"content": "Override"})
    client.delete("/api/admin/texts/help/he", headers=AUTH)
    # After delete, GET should show source=default again
    entries = client.get("/api/admin/texts/help", headers=AUTH).json()["entries"]
    he = next(e for e in entries if e["language"] == "he")
    assert he["source"] == "default"


def test_delete_text_requires_auth(client):
    resp = client.delete("/api/admin/texts/help/he")
    assert resp.status_code == 401
