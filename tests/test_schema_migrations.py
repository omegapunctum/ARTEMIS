import importlib
import json
import os
import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest


def _reload_services(monkeypatch: pytest.MonkeyPatch, db_path: Path):
    monkeypatch.setenv("AUTH_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-schema-migrations")
    monkeypatch.setenv("AUTH_SESSION_BACKEND", "memory")

    import app.auth.service as auth_service
    import app.drafts.service as drafts_service
    import app.research_slices.service as research_slices_service

    auth_service = importlib.reload(auth_service)
    drafts_service = importlib.reload(drafts_service)
    research_slices_service = importlib.reload(research_slices_service)
    return auth_service, drafts_service, research_slices_service


def _table_columns(db_path: Path, table_name: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _schema_versions(db_path: Path) -> list[int]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT version FROM schema_version ORDER BY version").fetchall()
    return [int(row[0]) for row in rows]


def test_schema_migrations_apply_on_fresh_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "fresh.db"
    auth_service, drafts_service, research_slices_service = _reload_services(monkeypatch, db_path)

    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()

    assert "is_admin" in _table_columns(db_path, "users")

    draft_columns = _table_columns(db_path, "drafts")
    assert {"image_url", "status", "publish_status", "airtable_record_id", "published_at", "payload"}.issubset(draft_columns)

    research_slice_columns = _table_columns(db_path, "research_slices")
    assert {\n        "share_token_hash",\n        "shared_at",\n        "research_question",\n        "selection_rationale",\n        "evidence_state",\n        "evidence_refs_json",\n        "findings_json",\n        "conclusion_status",\n        "conclusion",\n        "uncertainty_notes",\n        "schema_version",\n        "content_version",\n        "filter_state_json",\n        "comparison_feature_ids_json",\n    }.issubset(research_slice_columns)
    assert _schema_versions(db_path) == [1, 101, 102, 103, 104, 105, 106, 201, 202, 203]


def test_schema_migrations_are_idempotent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "idempotent.db"
    auth_service, drafts_service, research_slices_service = _reload_services(monkeypatch, db_path)

    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()
    first_versions = _schema_versions(db_path)

    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()
    second_versions = _schema_versions(db_path)

    assert first_versions == second_versions == [1, 101, 102, 103, 104, 105, 106, 201, 202, 203]


def test_schema_migrations_upgrade_partially_evolved_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "partial.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT NOT NULL, password_hash TEXT NOT NULL)")
        conn.execute(
            """
            CREATE TABLE drafts (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                geometry TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
            """
        )
        conn.commit()

    auth_service, drafts_service, research_slices_service = _reload_services(monkeypatch, db_path)
    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()

    assert "is_admin" in _table_columns(db_path, "users")
    draft_columns = _table_columns(db_path, "drafts")
    assert {"image_url", "status", "publish_status", "airtable_record_id", "published_at", "payload"}.issubset(draft_columns)
    research_slice_columns = _table_columns(db_path, "research_slices")
    assert {\n        "share_token_hash",\n        "shared_at",\n        "research_question",\n        "selection_rationale",\n        "evidence_state",\n        "evidence_refs_json",\n        "findings_json",\n        "conclusion_status",\n        "conclusion",\n        "uncertainty_notes",\n        "schema_version",\n        "content_version",\n        "filter_state_json",\n        "comparison_feature_ids_json",\n    }.issubset(research_slice_columns)
    assert _schema_versions(db_path) == [1, 101, 102, 103, 104, 105, 106, 201, 202, 203]


def test_auth_and_drafts_flow_works_after_migration_init(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "flow.db"
    auth_service, drafts_service, research_slices_service = _reload_services(monkeypatch, db_path)

    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()

    db = auth_service.SessionLocal()
    try:
        email = f"migration-flow-{uuid4().hex}@example.com"
        auth_service.register_user(db, email, "password123")
        user = db.query(auth_service.User).filter(auth_service.User.email == email).first()
        assert user is not None

        draft = drafts_service.create_draft(
            db,
            user,
            "Draft title",
            "Draft description",
            {"type": "Point", "coordinates": [37.6, 55.7]},
            payload={"name_ru": "Draft title"},
        )
        assert draft.id is not None
        assert draft.status == "draft"
    finally:
        db.close()


def test_research_slice_v2_migration_preserves_legacy_owner_and_share(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "legacy-slice.db"
    legacy_annotations = [
        {"id": "ann-legacy", "type": "interpretation", "text": "Legacy finding"}
    ]

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE research_slices (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                description VARCHAR NOT NULL DEFAULT '',
                visibility VARCHAR NOT NULL DEFAULT 'private',
                feature_refs_json JSON NOT NULL,
                time_range_json JSON NOT NULL,
                view_state_json JSON NOT NULL,
                annotations_json JSON NOT NULL,
                share_token_hash VARCHAR,
                shared_at DATETIME,
                created_at DATETIME,
                updated_at DATETIME
            )
            """
        )
        conn.execute(
            """
            INSERT INTO research_slices (
                id, user_id, title, description, visibility,
                feature_refs_json, time_range_json, view_state_json, annotations_json,
                share_token_hash, shared_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'private', ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (
                "legacy-1",
                "owner-1",
                "Legacy comparison",
                "Two selected buildings",
                json.dumps([{"feature_id": "recA"}, {"feature_id": "recB"}]),
                json.dumps({"start": 1500, "end": 1700, "mode": "range"}),
                json.dumps({"center": [10, 20], "zoom": 5, "selected_feature_id": "recA"}),
                json.dumps(legacy_annotations),
                "hashed-share-token",
                "2026-07-24 00:00:00",
            ),
        )
        conn.commit()

    auth_service, drafts_service, research_slices_service = _reload_services(monkeypatch, db_path)
    auth_service.init_db()
    drafts_service.init_db()
    research_slices_service.init_db()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT user_id, share_token_hash, shared_at, research_question,
                   selection_rationale, evidence_state, findings_json,
                   conclusion_status, schema_version, content_version
            FROM research_slices WHERE id = 'legacy-1'
            """
        ).fetchone()

    assert row is not None
    assert row[0] == "owner-1"
    assert row[1] == "hashed-share-token"
    assert row[2] is not None
    assert row[3] == "Legacy comparison"
    assert row[4] == "Two selected buildings"
    assert row[5] == "missing"
    assert json.loads(row[6]) == legacy_annotations
    assert row[7] == "unresolved"
    assert row[8] == "2.0"
    assert row[9] == 1
