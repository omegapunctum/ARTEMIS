"""Local editor delivery: stable credentials, safe backups, actual app wiring."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from scripts.knowledge_editor_backup import copy_database
from scripts.run_knowledge_editor import configure


def test_launcher_keeps_existing_secret_and_private_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", os.environ.copy())
    original_mask = os.umask(0o077)
    try:
        configure(tmp_path / "runtime", "owner@example.com", 8000)
        secret = (tmp_path / "runtime/auth-secret.key").read_bytes()
        configure(tmp_path / "runtime", "owner@example.com", 8001)
        assert (tmp_path / "runtime/auth-secret.key").read_bytes() == secret
        assert os.environ["AUTH_SECRET_KEY"].encode() == secret
        assert os.environ["AUTH_DATABASE_URL"].endswith("/runtime/editor.sqlite3")
        assert os.environ["AUTH_SESSION_BACKEND"] == "memory"
        assert os.environ["MIGRATION_STARTUP_ROLE"] == "owner"
        assert os.environ["CORS_ALLOW_ORIGINS"] == "http://127.0.0.1:8001,http://localhost:8001"
        assert (tmp_path / "runtime/auth-secret.key").stat().st_mode & 0o077 == 0
    finally:
        os.umask(original_mask)


def test_launcher_does_not_replace_invalid_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", os.environ.copy())
    (tmp_path / "auth-secret.key").write_text("invalid")
    original_mask = os.umask(0o077)
    try:
        with pytest.raises(ValueError, match="invalid"):
            configure(tmp_path, "owner@example.com", 8000)
        assert (tmp_path / "auth-secret.key").read_text() == "invalid"
    finally:
        os.umask(original_mask)


def test_backup_restores_committed_wal_and_never_overwrites(tmp_path):
    source, backup, restored = (tmp_path / name for name in ("working.db", "backup.db", "restored.db"))
    with sqlite3.connect(source) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE revisions (id TEXT PRIMARY KEY, payload TEXT)")
        db.execute("INSERT INTO revisions VALUES ('r1', 'private synthetic packet')")
        db.commit()
        digest = copy_database(source, backup)
        assert len(digest) == 64
        copy_database(backup, restored)
        with sqlite3.connect(restored) as reopened:
            assert reopened.execute("SELECT * FROM revisions").fetchall() == [("r1", "private synthetic packet")]
        with pytest.raises(ValueError, match="new file"):
            copy_database(backup, source)
        assert db.execute("SELECT COUNT(*) FROM revisions").fetchone()[0] == 1
    assert backup.stat().st_mode & 0o077 == 0


def test_actual_app_serves_editor_and_preserves_scoped_errors(tmp_path):
    root = Path(__file__).resolve().parents[1]
    script = '''
import json
from fastapi.testclient import TestClient
from app.main import app
from app.auth import service as auth
from app.auth.utils import create_access_token
from app.knowledge_editor import service as editor
with auth.SessionLocal() as db:
    db.add(auth.User(id="synthetic-owner", email="owner@example.com", password_hash="unused", is_admin=True))
    db.commit()
headers={"Authorization":"Bearer "+create_access_token("synthetic-owner")}
with TestClient(app) as client:
    page=client.get("/editor/")
    assert page.status_code == 200 and 'id="record-form"' in page.text
    assert page.headers["cache-control"] == "no-store"
    assert client.get("/editor/editor.js").status_code == 200
    assert client.get("/api/knowledge-editor/drafts").status_code == 401
    created=client.post("/api/knowledge-editor/drafts", headers=headers, json={"content":{}})
    assert created.status_code == 201, created.text
    record=created.json()
    failure=client.post("/api/knowledge-editor/drafts/"+record["id"]+"/submit", headers=headers, json={"expected_version":record["version"]})
    assert failure.status_code == 422, failure.text
    assert failure.json()["error"] == "submission_incomplete", failure.text
    assert failure.json()["detail"]["fields"], failure.text
    assert failure.headers["cache-control"] == "no-store"
    assert client.get("/api/knowledge-editor/public/objects").json() == []
    with auth.engine.connect() as db:
        from sqlalchemy import text
        triggers=db.execute(text("SELECT name FROM sqlite_master WHERE type='trigger'")).scalars().all()
        assert any("knowledge_editor_revisions" in name for name in triggers), triggers
print(json.dumps({"actual_app_wiring":"PASS"}))
'''
    env = {**os.environ, "PYTHONPATH": str(root), "APP_ENV": "test",
           "AUTH_SECRET_KEY": "synthetic-editor-integration-secret-key-only",
           "AUTH_SESSION_BACKEND": "memory", "MIGRATION_STARTUP_ROLE": "owner",
           "AUTH_DATABASE_URL": "sqlite:///" + str(tmp_path / "integration.db"),
           "COOKIE_SECURE": "false", "MODERATOR_EMAILS": "owner@example.com"}
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, env=env,
                            text=True, capture_output=True, timeout=40)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"actual_app_wiring": "PASS"' in result.stdout
