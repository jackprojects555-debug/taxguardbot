import pytest

import app.database as db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "_DB_PATH", db_path)
    db.init_db()
