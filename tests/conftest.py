from copy import deepcopy

import pytest

import app.database as db
import app.message_store as ms


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "_DB_PATH", db_path)
    db.init_db()
    # Isolate message store from on-disk data/messages.json so tests always
    # run against the in-code _DEFAULT_MESSAGES, not local file overrides.
    monkeypatch.setattr(ms, "_MESSAGES", deepcopy(ms._DEFAULT_MESSAGES))
    monkeypatch.setattr(ms, "_load_from_disk_if_changed", lambda: None)
