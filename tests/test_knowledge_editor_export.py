"""Portable published history: coherent capture, strict privacy and unsigned integrity."""
import copy
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from threading import Event, Thread
from uuid import uuid4

import pytest
from sqlalchemy import event, select, text

from app.knowledge_editor import public_export as export
from app.knowledge_editor import service as editor
from app.knowledge_editor.schemas import PublishRequest
from test_knowledge_editor import (BASE, PRIVATE_QUOTE, accepted, anonymous, call, complete_content,
    correction, created, pilot, publication_payload, published, submitted)

ROOT = Path(__file__).resolve().parents[1]


def publish_first(pilot):
    return published(pilot, accepted(pilot, submitted(pilot, created(pilot))))


def accept_correction(pilot, item, statement="Published correction"):
    next_item = correction(pilot, item)
    content = copy.deepcopy(next_item["content"])
    content["human_authored_attestation"] = True
    content["claim"]["statement"] = statement
    next_item = call(pilot, "put", f"/drafts/{next_item['id']}",
        {"expected_version": next_item["version"], "content": content})
    return accepted(pilot, submitted(pilot, next_item))


def download(pilot, entity_id, status=200):
    response = pilot.client.get(f"{BASE}/public/objects/{entity_id}/export")
    assert response.status_code == status, response.text
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    return response


def resign(package, snapshots=False):
    if snapshots:
        for snapshot in package["snapshots"]:
            snapshot["public_payload_digest"] = export.digest({key: value for key, value in snapshot.items()
                if key != "public_payload_digest"})
        package["manifest"]["snapshots"] = [{"snapshot_id": snapshot["snapshot_id"],
            "revision_id": snapshot["revision_id"], "snapshot_digest": export.digest(snapshot)}
            for snapshot in package["snapshots"]]
    package["package_digest"] = export.digest({key: value for key, value in package.items() if key != "package_digest"})
    return package


def run_cli(path, *args):
    return subprocess.run([sys.executable, str(ROOT / "scripts/verify_knowledge_editor_export.py"), str(path), *args],
        cwd=ROOT.parent, capture_output=True, text=True, timeout=20,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "AUTH_DATABASE_URL": "not-a-database-url"})


def test_exact_public_snapshots_deterministic_download_and_no_mutation(pilot, tmp_path):
    first = publish_first(pilot)
    second = published(pilot, accept_correction(pilot, first))
    with pilot.sessions() as db:
        before = {table.name: db.execute(select(table)).all() for table in [editor.EditorObject.__table__,
            editor.EditorDraft.__table__, editor.EditorRevision.__table__, editor.EditorPublication.__table__, editor.EditorEvent.__table__]}
    response = download(pilot, first["entity_id"])
    package = response.json()
    export.validate_package(package)
    assert package["current_snapshot_id"] == second["published_snapshot_id"]
    assert package["snapshots"] == sorted([anonymous(pilot, f"/public/snapshots/{item['published_snapshot_id']}")
        for item in (first, second)], key=lambda snapshot: (snapshot["published_at"], snapshot["snapshot_id"]))
    assert package["manifest"]["unresolved_predecessor_revision_ids"] == []
    assert response.content == export.canonical_bytes(package) == download(pilot, first["entity_id"]).content
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.headers["content-disposition"] == f'attachment; filename="artemis-editor-{first["entity_id"]}-public.json"'
    raw = response.text
    for forbidden in [PRIVATE_QUOTE, "owner@example.test", "owner_id", "actor_id", "reviewer_actor_id", "native_expression",
            "Examined the candidate", "Correct the wording", "published_snapshots", "access_token"]:
        assert forbidden not in raw
    with pilot.sessions() as db:
        after = {table.name: db.execute(select(table)).all() for table in [editor.EditorObject.__table__,
            editor.EditorDraft.__table__, editor.EditorRevision.__table__, editor.EditorPublication.__table__, editor.EditorEvent.__table__]}
    assert after == before
    path = tmp_path / "portable.json"
    path.write_bytes(response.content)
    before_files = set(tmp_path.iterdir())
    before_stat = path.stat()
    result = run_cli(path)
    assert result.returncode == 0 and "unsigned" in result.stdout
    assert result.stderr == "" and first["entity_id"] not in result.stdout
    assert set(tmp_path.iterdir()) == before_files and path.stat().st_mtime_ns == before_stat.st_mtime_ns


def test_accepted_unpublished_state_and_explicit_gap_no_private_chain(pilot):
    first = publish_first(pilot)
    original = download(pilot, first["entity_id"]).content
    unpublished = accept_correction(pilot, first, "PRIVATE_ACCEPTED_UNPUBLISHED_statement")
    assert download(pilot, first["entity_id"]).content == original
    last = published(pilot, accept_correction(pilot, unpublished))
    package = download(pilot, first["entity_id"]).json()
    assert len(package["snapshots"]) == 2
    assert package["manifest"]["unresolved_predecessor_revision_ids"] == [unpublished["accepted_revision_id"]]
    assert package["snapshots"][-1]["predecessor_revision_id"] == unpublished["accepted_revision_id"]
    assert package["current_snapshot_id"] == last["published_snapshot_id"]
    assert "PRIVATE_ACCEPTED_UNPUBLISHED" not in json.dumps(package)
    assert unpublished["accepted_revision_id"] not in [snapshot["revision_id"] for snapshot in package["snapshots"]]
    private = created(pilot, {"entity": {"name": "PRIVATE_UNRELATED_DRAFT"}})
    assert download(pilot, first["entity_id"]).json() == package
    assert private["entity_id"] not in json.dumps(package)
    export.validate_package(package)


def test_missing_never_published_and_private_are_indistinguishable(pilot):
    private = created(pilot)
    accepted_private = accepted(pilot, submitted(pilot, created(pilot)))
    responses = [download(pilot, entity_id, 404) for entity_id in [str(uuid4()), private["entity_id"], accepted_private["entity_id"]]]
    assert [response.json()["detail"] for response in responses] == [{"code": "publication_not_found"}] * 3
    for unsafe in ["not-a-uuid", 'title\".json', "%0d%0aInjected"]:
        response = download(pilot, unsafe, 404)
        assert "content-disposition" not in response.headers


def corrupt_publication(pilot, item, mutate, recompute=True):
    with pilot.engine.begin() as conn:
        conn.execute(text("DROP TRIGGER knowledge_editor_publications_immutable_update"))
        row = conn.execute(select(editor.EditorPublication.__table__).where(
            editor.EditorPublication.id == item["published_snapshot_id"])).mappings().one()
        payload = copy.deepcopy(row["public_payload"])
        changes = mutate(payload, row)
        if changes is None:
            changes = {"public_payload": payload, "payload_digest": editor.digest(payload) if recompute else "0" * 64}
        conn.execute(editor.EditorPublication.__table__.update().where(
            editor.EditorPublication.id == item["published_snapshot_id"]).values(**changes))


@pytest.mark.parametrize("kind", ["digest", "unknown_root", "unknown_nested", "snapshot", "revision", "entity", "series",
    "claim_subject", "evidence_claim", "evidence_source", "private_expression", "null_position", "missing_time", "bad_date", "bad_url"])
def test_corrupted_storage_fails_closed_without_diagnostic_content(pilot, kind):
    item = publish_first(pilot)
    marker = "PRIVATE_CORRUPTION_DIAGNOSTIC"
    def mutate(payload, _row):
        if kind == "digest": return {"payload_digest": "0" * 64}
        if kind == "unknown_root": payload["private_marker"] = marker
        elif kind == "unknown_nested": payload["source"]["private_marker"] = marker
        elif kind in {"snapshot", "revision", "entity", "series"}:
            payload[{"snapshot":"snapshot_id", "revision":"revision_id", "entity":"entity_id", "series":"target_series_id"}[kind]] = str(uuid4())
        elif kind == "claim_subject": payload["claim"]["subject_id"] = str(uuid4())
        elif kind == "evidence_claim": payload["evidence"]["claim_id"] = str(uuid4())
        elif kind == "evidence_source": payload["evidence"]["source_id"] = str(uuid4())
        elif kind == "private_expression": payload["evidence"]["native_expression"] = marker
        elif kind == "null_position": payload["entity"]["position"] = [1, 2]
        elif kind == "missing_time": del payload["published_at"]
        elif kind == "bad_date": payload["published_at"] = "2026-99-99T25:99:99"
        elif kind == "bad_url": payload["source"]["url"] = "https://user:secret@example.test/"
    corrupt_publication(pilot, item, mutate)
    response = download(pilot, item["entity_id"], 500)
    assert response.json()["detail"] == {"code": "public_export_unavailable"}
    assert marker not in response.text and PRIVATE_QUOTE not in response.text
    assert "content-disposition" not in response.headers


def test_current_pointer_and_invalid_system_filename_fail_closed(pilot):
    item = publish_first(pilot)
    with pilot.engine.begin() as conn:
        conn.execute(editor.EditorObject.__table__.update().where(editor.EditorObject.id == item["entity_id"]).values(
            published_snapshot_id=str(uuid4())))
    download(pilot, item["entity_id"], 500)
    # Even corruption that gives root and all public references the same unsafe
    # identifier must never turn a user string into a header filename.
    unsafe = 'unsafe"name'
    with pilot.engine.begin() as conn:
        conn.execute(editor.EditorObject.__table__.update().where(editor.EditorObject.id == item["entity_id"]).values(
            id=unsafe, published_snapshot_id=item["published_snapshot_id"]))
    def mutate(payload, _row):
        payload["entity_id"] = payload["entity"]["id"] = payload["claim"]["subject_id"] = unsafe
        return {"entity_id": unsafe, "public_payload": payload, "payload_digest": editor.digest(payload)}
    corrupt_publication(pilot, item, mutate)
    assert "content-disposition" not in download(pilot, unsafe, 500).headers


@pytest.mark.parametrize("kind", ["package_hash", "snapshot_hash", "payload_hash", "unsupported_version", "unknown_root", "unknown_nested",
    "manifest_missing", "manifest_extra", "duplicate", "duplicate_revision", "missing_snapshot", "pointer", "order", "entity", "series", "gap", "cycle"])
def test_offline_schema_integrity_and_reference_tampering_rejected(pilot, tmp_path, kind):
    first = publish_first(pilot)
    second = published(pilot, accept_correction(pilot, first))
    package = download(pilot, first["entity_id"]).json()
    if kind == "package_hash": package["package_digest"] = "0" * 64
    elif kind == "snapshot_hash": package["manifest"]["snapshots"][0]["snapshot_digest"] = "0" * 64
    elif kind == "payload_hash": package["snapshots"][0]["public_payload_digest"] = "0" * 64
    elif kind == "unsupported_version": package["schema_version"] = "knowledge-editor-public-export-v99"
    elif kind == "unknown_root": package["actor_id"] = "PRIVATE_RECORD_CONTENT"
    elif kind == "unknown_nested": package["snapshots"][0]["source"]["actor_id"] = "PRIVATE_RECORD_CONTENT"
    elif kind == "manifest_missing": package["manifest"]["snapshots"].pop()
    elif kind == "manifest_extra": package["manifest"]["snapshots"].append(copy.deepcopy(package["manifest"]["snapshots"][0]))
    elif kind == "duplicate": package["snapshots"].append(copy.deepcopy(package["snapshots"][0])); resign(package, True)
    elif kind == "duplicate_revision": package["snapshots"][1]["revision_id"] = package["snapshots"][0]["revision_id"]; resign(package, True)
    elif kind == "missing_snapshot": package["snapshots"].pop()
    elif kind == "pointer": package["current_snapshot_id"] = str(uuid4())
    elif kind == "order": package["snapshots"].reverse(); resign(package, True)
    elif kind in {"entity", "series"}: package[{"entity":"entity_id", "series":"target_series_id"}[kind]] = str(uuid4())
    elif kind == "gap": package["manifest"]["unresolved_predecessor_revision_ids"] = [str(uuid4())]
    elif kind == "cycle":
        package["snapshots"][0]["predecessor_revision_id"] = second["accepted_revision_id"]
        resign(package, True)
    if kind != "package_hash": resign(package)
    path = tmp_path / "invalid.json"
    path.write_bytes(export.canonical_bytes(package))
    result = run_cli(path)
    assert result.returncode == 1
    assert result.stdout == "Public export verification failed.\n" and result.stderr == ""
    assert "PRIVATE_RECORD_CONTENT" not in result.stdout


@pytest.mark.parametrize("data", [b'{"schema_version":1,"schema_version":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
    b'\xffPRIVATE_RECORD_CONTENT', b'{"x":', b'[' * 2000 + b']' * 2000, b'null', b'[]'])
def test_malformed_offline_json_generic_failure(tmp_path, data):
    path = tmp_path / "invalid.json"
    path.write_bytes(data)
    result = run_cli(path)
    assert result.returncode == 1 and result.stdout == "Public export verification failed.\n" and result.stderr == ""


def test_rehashed_text_changes_are_unsigned_integrity_not_authenticity(pilot):
    item = publish_first(pilot)
    package = download(pilot, item["entity_id"]).json()
    package["snapshots"][0]["claim"]["statement"] = "A changed assertion with recomputed unsigned hashes."
    resign(package, True)
    # Integrity cannot prove content came from this server, a source or a signer.
    export.validate_package(package)


def test_literal_publication_timestamp_ties_sort_by_snapshot_id(pilot):
    first = publish_first(pilot)
    published(pilot, accept_correction(pilot, first))
    package = download(pilot, first["entity_id"]).json()
    initial, corrected = package["snapshots"]
    corrected["published_at"] = initial["published_at"]
    initial["snapshot_id"] = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    corrected["snapshot_id"] = "00000000-0000-0000-0000-000000000000"
    package["current_snapshot_id"] = corrected["snapshot_id"]
    package["snapshots"] = [corrected, initial]
    resign(package, True)
    # Tie ordering is mechanical; it does not redefine the predecessor chain.
    export.validate_package(package)


def test_plain_offline_command_does_not_write_checkout_bytecode(pilot, tmp_path):
    import shutil
    item = publish_first(pilot)
    checkout = tmp_path / "checkout"
    for relative in ["app/__init__.py", "app/knowledge_editor/__init__.py", "app/knowledge_editor/public_export.py",
            "app/knowledge_editor/public_export.schema.json", "scripts/verify_knowledge_editor_export.py"]:
        target = checkout / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    path = checkout / "portable.json"
    path.write_bytes(download(pilot, item["entity_id"]).content)
    before = {entry.relative_to(checkout) for entry in checkout.rglob("*")}
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONDONTWRITEBYTECODE"}
    result = subprocess.run([sys.executable, str(checkout / "scripts/verify_knowledge_editor_export.py"), str(path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=20, env=environment)
    assert result.returncode == 0 and result.stderr == ""
    assert {entry.relative_to(checkout) for entry in checkout.rglob("*")} == before


def test_stale_identity_map_root_and_pending_mutations_do_not_affect_read(pilot):
    first = publish_first(pilot)
    next_item = accept_correction(pilot, first)
    with pilot.sessions() as db:
        stale = db.get(editor.EditorObject, first["entity_id"])
        assert stale.published_snapshot_id == first["published_snapshot_id"]
        second = published(pilot, next_item)
        assert stale.published_snapshot_id == first["published_snapshot_id"]
        stale.published_snapshot_id = str(uuid4())  # Must not autoflush a read.
        package = json.loads(export.public_export(db, first["entity_id"]))
        assert package["current_snapshot_id"] == second["published_snapshot_id"] and len(package["snapshots"]) == 2
    assert download(pilot, first["entity_id"]).json()["current_snapshot_id"] == second["published_snapshot_id"]


def test_single_select_consistent_view_during_concurrent_publication(pilot):
    first = publish_first(pilot)
    next_item = accept_correction(pilot, first)
    with pilot.engine.begin() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
    writer_finished = Event()
    errors = []
    statements = []
    worker = None
    def writer():
        try:
            with pilot.sessions() as db:
                editor.publish_revision(db, db.get(editor.User, "owner"), db.get(editor.EditorDraft, next_item["id"]),
                    PublishRequest(**publication_payload(next_item)))
        except Exception as exc:
            errors.append(exc)
        finally:
            writer_finished.set()
    def interleave(conn, cursor, statement, parameters, context, executemany):
        nonlocal worker
        if statement.lstrip().upper().startswith("SELECT") and "knowledge_editor_publications" in statement and worker is None:
            statements.append(statement)
            worker = Thread(target=writer)
            worker.start()
            assert writer_finished.wait(10), "Concurrent writer failed to finish"
    event.listen(pilot.engine, "after_cursor_execute", interleave)
    try:
        with pilot.sessions() as db:
            before = json.loads(export.public_export(db, first["entity_id"]))
    finally:
        event.remove(pilot.engine, "after_cursor_execute", interleave)
        if worker: worker.join(10)
    assert worker is not None and not errors and len(statements) == 1
    assert before["current_snapshot_id"] == first["published_snapshot_id"] and len(before["snapshots"]) == 1
    export.validate_package(before)
    after = download(pilot, first["entity_id"]).json()
    assert len(after["snapshots"]) == 2 and after["current_snapshot_id"] != before["current_snapshot_id"]
    sql = statements[0].lower()
    assert "owner_id" not in sql and "knowledge_editor_revisions" not in sql and "knowledge_editor_events" not in sql
    assert "knowledge_editor_drafts" not in sql


def test_download_unchanged_after_isolated_sqlite_restore(pilot, tmp_path):
    first = publish_first(pilot)
    original = download(pilot, first["entity_id"]).content
    backup = tmp_path / "restored.db"
    with sqlite3.connect(pilot.db_path) as source, sqlite3.connect(backup) as target:
        source.backup(target)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    restored = create_engine(f"sqlite:///{backup}")
    try:
        with sessionmaker(bind=restored)() as db:
            assert export.public_export(db, first["entity_id"]) == original
    finally:
        restored.dispose()


def test_shared_size_bound_atomic_413_and_bounded_offline_read(pilot, tmp_path, monkeypatch):
    item = publish_first(pilot)
    response = download(pilot, item["entity_id"])
    monkeypatch.setattr(export, "MAX_PACKAGE_BYTES", len(response.content) - 1)
    failed = download(pilot, item["entity_id"], 413)
    assert failed.json()["detail"] == {"code": "export_too_large"} and "content-disposition" not in failed.headers
    path = tmp_path / "oversized.json"
    path.write_bytes(response.content)
    with pytest.raises(export.PublicExportTooLarge): export.verify_file(path)
    # A sparse oversized file checks the real CLI's fixed cap with little disk use.
    with path.open("wb") as stream: stream.truncate(32 * 1024 * 1024 + 1)
    result = run_cli(path)
    assert result.returncode == 1 and result.stdout == "Public export verification failed.\n" and result.stderr == ""


def test_verifier_does_not_follow_source_links_or_load_database(pilot, tmp_path):
    item = publish_first(pilot)
    package = download(pilot, item["entity_id"]).json()
    package["snapshots"][0]["source"]["url"] = "https://127.0.0.1:1/never-contact-this"
    resign(package, True)
    path = tmp_path / "offline.json"
    path.write_bytes(export.canonical_bytes(package))
    script = '''import socket, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
def blocked(*args, **kwargs): raise AssertionError("network forbidden")
socket.socket.connect = blocked
socket.socket.connect_ex = blocked
socket.create_connection = blocked
socket.getaddrinfo = blocked
from app.knowledge_editor.public_export import verify_file
verify_file(sys.argv[2])
assert "app.auth.service" not in sys.modules
assert "app.knowledge_editor.service" not in sys.modules
print("offline")
'''
    result = subprocess.run([sys.executable, "-B", "-c", script, str(ROOT), str(path)],
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0 and result.stdout == "offline\n" and result.stderr == ""
