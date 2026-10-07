"""The bounded editorial lifecycle and its failure/privacy boundaries."""
import copy
import json
import sqlite3
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import sessionmaker

from app.auth import service as auth
from app.auth.routes import router as auth_router
from app.auth.service import User, get_db
from app.auth.utils import create_access_token
from app.knowledge_editor import service as editor
from app.knowledge_editor.routes import router, knowledge_editor_error_handler
from app.observability import ObservabilityMiddleware

BASE = "/api/knowledge-editor"
PRIVATE_QUOTE = "PRIVATE_SOURCE_EXPRESSION_not_for_publication_1931"


def complete_content():
    return {
        "entity": {"name": "Test architecture object", "description": "Editorial identification"},
        "source": {"title": "Institutional catalogue", "author": None, "source_type": "institutional",
            "url": "https://example.org/catalogue", "bibliographic_reference": None,
            "publication": None, "accessed_on": "2026-10-07", "rights": "unknown"},
        "claim": {"statement": "The catalogue dates completion to 1931.", "claim_kind": "factual",
            "origin": "user", "confidence": "unknown", "confidence_basis": None,
            "uncertainty": "The original document was not examined."},
        "evidence": {"locator": "Catalogue entry, section 2", "relation_to_claim": "supports",
            "evidence_strength": "direct", "native_expression": PRIVATE_QUOTE, "native_precision": "unresolved"},
        "human_authored_attestation": True,
    }


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    db_path = tmp_path / "pilot.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(auth, "engine", engine)
    monkeypatch.setenv("MODERATOR_EMAILS", "")
    # Never reload modules or touch the configured working/auth database.
    User.__table__.create(bind=engine, checkfirst=True)
    editor.init_db()
    sessions = sessionmaker(bind=engine, autoflush=False)
    with sessions() as db:
        for actor_id, admin in [("owner", True), ("reviewer", True), ("author", False), ("other", False)]:
            db.add(User(id=actor_id, email=f"{actor_id}@example.test", password_hash="unused", is_admin=admin))
        db.commit()

    app = FastAPI()
    app.add_middleware(ObservabilityMiddleware)
    app.add_exception_handler(editor.KnowledgeEditorError, knowledge_editor_error_handler)
    app.include_router(auth_router, prefix="/api")
    app.include_router(router, prefix="/api")

    def isolated_db():
        with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = isolated_db
    client = TestClient(app, raise_server_exceptions=False)
    def headers(actor="owner"):
        return {"Authorization": f"Bearer {create_access_token(actor)}"}
    yield SimpleNamespace(client=client, sessions=sessions, engine=engine, db_path=db_path, headers=headers)
    client.close()
    engine.dispose()


def call(pilot, method, path, payload=None, actor="owner", expected=200):
    response = getattr(pilot.client, method)(BASE + path, json=payload, headers=pilot.headers(actor)) if method != "get" else pilot.client.get(BASE + path, headers=pilot.headers(actor))
    assert response.status_code == expected, response.text
    return response.json() if response.content else None


def created(pilot, content=None, actor="owner"):
    return call(pilot, "post", "/drafts", {"content": complete_content() if content is None else content}, actor, 201)


def submitted(pilot, item, actor="owner"):
    return call(pilot, "post", f"/drafts/{item['id']}/submit", {"expected_version": item["version"]}, actor)


def review_payload(item, decision="accept"):
    return {"expected_version": item["version"], "submitted_digest": item["submitted_digest"],
        "expected_predecessor_revision_id": item["predecessor_revision_id"], "decision": decision,
        "reason": "Examined the candidate and cited source in the stated scope."}


def accepted(pilot, item, actor="owner"):
    return call(pilot, "post", f"/drafts/{item['id']}/review", review_payload(item), actor)


def publication_payload(item):
    return {"expected_version": item["version"], "accepted_revision_id": item["accepted_revision_id"],
        "accepted_revision_digest": item["accepted_revision_digest"], "expected_object_version": item["object_version"],
        "expected_publication_id": item["published_snapshot_id"]}


def published(pilot, item, actor="owner"):
    return call(pilot, "post", f"/drafts/{item['id']}/publish", publication_payload(item), actor)


def correction(pilot, item):
    return call(pilot, "post", f"/revisions/{item['accepted_revision_id']}/corrections", {
        "expected_revision_id": item["accepted_revision_id"], "expected_object_version": item["object_version"],
        "reason": "Correct the wording after checking the exact locator."}, expected=201)


def anonymous(pilot, path, expected=200):
    response = pilot.client.get(BASE + path)
    assert response.status_code == expected, response.text
    return response.json()


def assert_epistemic_preserved(public):
    assert public["claim"]["review_state"] == "draft"
    assert public["claim"]["evidence_state"] == "missing"
    assert public["claim"]["confidence"] == "unknown"
    assert public["source"]["review_state"] == "draft"
    assert public["evidence"]["review_state"] == "draft"
    assert public["evidence"]["normalized_value"] is None
    assert public["entity"]["world_time"] is None
    assert public["entity"]["position"] is None


def test_complete_owner_loop_correction_keeps_old_publication_and_private_packet(pilot):
    first = created(pilot)
    assert first["state"] == "draft" and first["version"] == 1
    submitted_first = submitted(pilot, first)
    accepted_first = accepted(pilot, submitted_first)
    assert accepted_first["review_mode"] == "owner_self_review"
    anonymous(pilot, f"/public/objects/{first['entity_id']}", 404)
    first = published(pilot, accepted_first)
    snapshot_id = first["published_snapshot_id"]
    old_public = anonymous(pilot, f"/public/snapshots/{snapshot_id}")
    assert_epistemic_preserved(old_public)
    assert old_public["review_mode"] == "owner_self_review"
    assert PRIVATE_QUOTE not in json.dumps(old_public)
    assert "owner@example.test" not in json.dumps(old_public)
    assert "actor_id" not in json.dumps(old_public)
    assert "Examined the candidate" not in json.dumps(old_public)
    corrected = correction(pilot, first)
    assert corrected["entity_id"] == first["entity_id"]
    assert corrected["target_series_id"] == first["target_series_id"]
    for field in ("claim_id", "source_id", "evidence_link_id"):
        assert corrected[field] != first[field]
    assert corrected["content"]["human_authored_attestation"] is False
    data = copy.deepcopy(corrected["content"])
    data["claim"]["statement"] = "The catalogue's 1931 attribution remains a candidate."
    data["human_authored_attestation"] = True
    corrected = call(pilot, "put", f"/drafts/{corrected['id']}", {"expected_version": corrected["version"], "content": data})
    corrected = accepted(pilot, submitted(pilot, corrected))
    still_old = anonymous(pilot, f"/public/objects/{first['entity_id']}")
    assert still_old["snapshot_id"] == snapshot_id
    corrected = published(pilot, corrected)
    latest = anonymous(pilot, f"/public/objects/{first['entity_id']}")
    assert latest["snapshot_id"] == corrected["published_snapshot_id"] != snapshot_id
    assert len(latest["published_snapshots"]) == 2
    old_again = anonymous(pilot, f"/public/snapshots/{snapshot_id}")
    assert old_again == old_public
    assert "published_snapshots" not in old_again
    assert old_again["claim"] == old_public["claim"]
    assert old_again["public_payload_digest"] == old_public["public_payload_digest"]
    history = call(pilot, "get", f"/drafts/{corrected['id']}/history")
    assert len(history["revisions"]) == 2
    packets = [row["packet"] for row in history["revisions"]]
    assert packets[1]["operation"] == "correct"
    assert packets[1]["predecessor_revision_id"] == packets[0]["revision_id"]
    assert packets[0]["source_value"]["raw_expression"] == PRIVATE_QUOTE
    for row in history["revisions"]:
        assert editor.digest(row["packet"]) == row["revision_digest"]
        assert row["packet"]["source_value_digest"] == editor.digest(row["packet"]["source_value"])
    assert {entry["action"] for entry in history["events"]} >= {"created", "submitted", "reviewed", "published", "correction_created", "saved"}


def test_distinct_account_review_is_transparent_not_independent_verification(pilot):
    item = created(pilot, actor="author")
    item = submitted(pilot, item, "author")
    assert len(call(pilot, "get", "/review-queue", actor="reviewer")) == 1
    item = accepted(pilot, item, "reviewer")
    assert item["review_mode"] == "separate_principal_review"
    item = published(pilot, item, "reviewer")
    public = anonymous(pilot, f"/public/objects/{item['entity_id']}")
    assert public["review_mode"] == "separate_principal_review"
    assert "independent" not in json.dumps(public)
    assert_epistemic_preserved(public)


def test_incomplete_draft_survives_readback_but_cannot_submit(pilot):
    item = created(pilot, {"entity": {"name": "Only a name"}})
    read = call(pilot, "get", f"/drafts/{item['id']}")
    assert read["content"] == item["content"]
    response = call(pilot, "post", f"/drafts/{item['id']}/submit", {"expected_version": 1}, expected=422)
    assert response["detail"]["code"] == "submission_incomplete"
    assert "evidence.native_expression" in response["detail"]["fields"]
    assert "evidence.locator" in response["detail"]["fields"]
    assert call(pilot, "get", f"/drafts/{item['id']}")["state"] == "draft"


@pytest.mark.parametrize("field", ["locator", "native_expression"])
def test_exact_locator_and_native_expression_required(pilot, field):
    content = complete_content()
    content["evidence"][field] = "  "
    item = created(pilot, content)
    call(pilot, "post", f"/drafts/{item['id']}/submit", {"expected_version": 1}, expected=422)


@pytest.mark.parametrize("url", ["javascript:alert(1)", "data:text/html,hello", "https://user:password@example.org/a", "https://example.org/\nprivate", "https://example.org:invalid/a", "https://example.org/a b"])
def test_unsafe_url_rejected(pilot, url):
    content = complete_content()
    content["source"]["url"] = url
    created_payload = {"content": content}
    call(pilot, "post", "/drafts", created_payload, expected=422)


def test_bibliographic_source_does_not_require_url_or_invent_license_author(pilot):
    content = complete_content()
    content["source"]["url"] = None
    content["source"]["bibliographic_reference"] = "Catalogue, volume 1, ISBN not recorded."
    item = published(pilot, accepted(pilot, submitted(pilot, created(pilot, content))))
    public = anonymous(pilot, f"/public/objects/{item['entity_id']}")
    assert public["source"]["url"] is None
    assert public["source"]["author"] is None
    assert public["source"]["rights"] == "unknown"


@pytest.mark.parametrize("part,key,value", [
    ("claim", "review_state", "reviewed"), ("claim", "evidence_state", "supported"),
    ("claim", "origin", "ai"), ("source", "source_type", "ai"),
    ("evidence", "normalized_value", 1931), ("evidence", "native_precision", "exact"),
    ("entity", "id", "existing-frozen-id"), ("entity", "latitude", 45),
])
def test_forged_system_semantics_and_identity_rejected(pilot, part, key, value):
    content = complete_content()
    content[part][key] = value
    call(pilot, "post", "/drafts", {"content": content}, expected=422)


def test_author_cannot_assign_reviewer_mode_or_actor(pilot):
    item = submitted(pilot, created(pilot))
    payload = review_payload(item)
    payload["review_mode"] = "separate_principal_review"
    payload["reviewer_actor_id"] = "reviewer"
    call(pilot, "post", f"/drafts/{item['id']}/review", payload, expected=422)
    assert call(pilot, "get", f"/drafts/{item['id']}")["state"] == "submitted"


def test_confidence_requires_basis_and_approval_never_raises_it(pilot):
    content = complete_content()
    content["claim"]["confidence"] = "low"
    call(pilot, "post", "/drafts", {"content": content}, expected=422)
    content["claim"]["confidence_basis"] = "Only one mediated catalogue source."
    item = published(pilot, accepted(pilot, submitted(pilot, created(pilot, content))))
    public = anonymous(pilot, f"/public/objects/{item['entity_id']}")
    assert public["claim"]["confidence"] == "low"
    assert public["claim"]["confidence_basis"] == content["claim"]["confidence_basis"]
    assert public["claim"]["evidence_state"] == "missing"


def test_access_controls_and_registration_never_grants_moderator(pilot):
    item = created(pilot, actor="author")
    assert pilot.client.get(BASE + f"/drafts/{item['id']}").status_code == 401
    call(pilot, "get", f"/drafts/{item['id']}", actor="other", expected=404)
    call(pilot, "put", f"/drafts/{item['id']}", {"expected_version": 1, "content": complete_content()}, actor="other", expected=404)
    call(pilot, "get", "/review-queue", actor="author", expected=403)
    item = submitted(pilot, item, "author")
    call(pilot, "post", f"/drafts/{item['id']}/review", review_payload(item), actor="author", expected=403)
    item = accepted(pilot, item, "reviewer")
    call(pilot, "post", f"/drafts/{item['id']}/publish", publication_payload(item), actor="author", expected=403)
    call(pilot, "post", f"/revisions/{item['accepted_revision_id']}/corrections", {
        "expected_revision_id": item["accepted_revision_id"], "expected_object_version": item["object_version"], "reason": "Try taking ownership"}, actor="other", expected=404)
    bad_registration = pilot.client.post("/api/auth/register", json={"email": "new@example.com", "password": "password123", "is_admin": True})
    assert bad_registration.status_code in {201, 422}  # auth schema may ignore unknown fields; it never grants privileges.
    if bad_registration.status_code == 201:
        with pilot.sessions() as db:
            assert db.query(User).filter_by(email="new@example.com").one().is_admin is False


def test_moderator_email_allowlist_is_server_authority(pilot, monkeypatch):
    monkeypatch.setenv("MODERATOR_EMAILS", " author@example.test ")
    assert call(pilot, "get", "/capabilities", actor="author")["can_review"] is True
    item = accepted(pilot, submitted(pilot, created(pilot, actor="author"), "author"), "author")
    assert item["review_mode"] == "owner_self_review"


def test_stale_save_review_digest_and_submitted_edit_rejected(pilot):
    item = created(pilot)
    replacement = {"expected_version": 1, "content": complete_content()}
    item = call(pilot, "put", f"/drafts/{item['id']}", replacement)
    call(pilot, "put", f"/drafts/{item['id']}", replacement, expected=409)
    item = submitted(pilot, item)
    call(pilot, "put", f"/drafts/{item['id']}", {**replacement, "expected_version": item["version"]}, expected=409)
    payload = review_payload(item)
    payload["submitted_digest"] = "0" * 64
    call(pilot, "post", f"/drafts/{item['id']}/review", payload, expected=409)
    payload = review_payload(item)
    payload["expected_version"] -= 1
    call(pilot, "post", f"/drafts/{item['id']}/review", payload, expected=409)
    item = accepted(pilot, item)
    call(pilot, "post", f"/drafts/{item['id']}/review", review_payload(item), expected=409)
    call(pilot, "put", f"/drafts/{item['id']}", {"expected_version": item["version"], "content": complete_content()}, expected=409)
    with pilot.sessions() as db:
        assert db.query(editor.EditorRevision).count() == 1


@pytest.mark.parametrize("decision", ["request_changes", "reject"])
def test_return_for_changes_reopens_editing_and_preserves_exact_review_receipt(pilot, decision):
    item = submitted(pilot, created(pilot))
    returned = call(pilot, "post", f"/drafts/{item['id']}/review", review_payload(item, decision))
    assert returned["state"] == ("rejected" if decision == "reject" else "request_changes")
    assert returned["capabilities"]["can_edit"] is True
    assert returned["accepted_revision_id"] is None
    changed = copy.deepcopy(returned["content"])
    changed["claim"]["statement"] = "The source proposes a tentative date."
    updated = call(pilot, "put", f"/drafts/{item['id']}", {"expected_version": returned["version"], "content": changed})
    assert updated["submitted_digest"] is None
    updated = accepted(pilot, submitted(pilot, updated))
    history = call(pilot, "get", f"/drafts/{item['id']}/history")
    reviews = [event for event in history["events"] if event["action"] == "reviewed"]
    assert [event["payload"]["decision"] for event in reviews] == [decision, "accept"]
    assert reviews[0]["payload"]["submitted_digest"] == item["submitted_digest"] != updated["submitted_digest"]


def test_publication_requires_exact_accepted_version_digest_and_pointer(pilot):
    item = created(pilot)
    payload = {"expected_version": item["version"], "accepted_revision_id": "fake", "accepted_revision_digest": "0" * 64,
        "expected_object_version": 1, "expected_publication_id": None}
    call(pilot, "post", f"/drafts/{item['id']}/publish", payload, expected=409)
    item = accepted(pilot, submitted(pilot, item))
    payload = publication_payload(item)
    bad = {**payload, "accepted_revision_digest": "0" * 64}
    call(pilot, "post", f"/drafts/{item['id']}/publish", bad, expected=409)
    bad = {**payload, "expected_publication_id": "not-the-current-publication"}
    call(pilot, "post", f"/drafts/{item['id']}/publish", bad, expected=409)
    item = published(pilot, item)
    call(pilot, "post", f"/drafts/{item['id']}/publish", payload, expected=409)
    # Even with refreshed version/pointer, accepted revision cannot be published twice.
    call(pilot, "post", f"/drafts/{item['id']}/publish", publication_payload(item), expected=409)
    with pilot.sessions() as db:
        assert db.query(editor.EditorPublication).count() == 1


def test_competing_corrections_cannot_fork_or_republish_stale_accepted_head(pilot):
    first = published(pilot, accepted(pilot, submitted(pilot, created(pilot))))
    a, b = correction(pilot, first), correction(pilot, first)
    submitted_candidates = []
    for item in [a, b]:
        content = item["content"]
        content["human_authored_attestation"] = True
        item = call(pilot, "put", f"/drafts/{item['id']}", {"expected_version": item["version"], "content": content})
        submitted_candidates.append(submitted(pilot, item))
    a, b = submitted_candidates
    a = accepted(pilot, a)
    call(pilot, "post", f"/drafts/{b['id']}/review", review_payload(b), expected=409)
    first_refreshed = call(pilot, "get", f"/drafts/{first['id']}")
    call(pilot, "post", f"/drafts/{first['id']}/publish", publication_payload(first_refreshed), expected=409)
    call(pilot, "post", f"/revisions/{first['accepted_revision_id']}/corrections", {
        "expected_revision_id": first["accepted_revision_id"], "expected_object_version": first["object_version"], "reason": "Old predecessor"}, expected=409)
    assert anonymous(pilot, f"/public/objects/{first['entity_id']}")["snapshot_id"] == first["published_snapshot_id"]
    with pilot.sessions() as db:
        assert db.query(editor.EditorRevision).count() == 2


def test_accepted_not_published_and_private_candidates_never_leak(pilot):
    item = accepted(pilot, submitted(pilot, created(pilot)))
    assert anonymous(pilot, "/public/objects") == []
    anonymous(pilot, f"/public/objects/{item['entity_id']}", 404)
    anonymous(pilot, f"/public/snapshots/{item['accepted_revision_id']}", 404)
    response = pilot.client.get(BASE + f"/drafts/{item['id']}/history")
    assert response.status_code == 401
    assert PRIVATE_QUOTE not in response.text


def test_immutable_accepted_public_and_event_rows_reject_direct_sql_change(pilot):
    published(pilot, accepted(pilot, submitted(pilot, created(pilot))))
    for model in [editor.EditorRevision, editor.EditorPublication, editor.EditorEvent]:
        for operation in ["UPDATE", "DELETE"]:
            statement = f"UPDATE {model.__tablename__} SET id=id" if operation == "UPDATE" else f"DELETE FROM {model.__tablename__}"
            with pytest.raises(DatabaseError, match="immutable_editor_record"):
                with pilot.engine.begin() as connection:
                    connection.execute(text(statement))


def test_restart_and_sqlite_backup_restore_preserve_bytes_and_private_closure(pilot, tmp_path):
    item = published(pilot, accepted(pilot, submitted(pilot, created(pilot))))
    original = anonymous(pilot, f"/public/objects/{item['entity_id']}")
    with pilot.sessions() as db:
        revision = db.get(editor.EditorRevision, item["accepted_revision_id"])
        packet_before = revision.packet
        digest_before = revision.packet_digest
        events_before = [(row.id, row.payload) for row in db.query(editor.EditorEvent).order_by(editor.EditorEvent.created_at, editor.EditorEvent.id)]
    restored_path = tmp_path / "restored.db"
    # sqlite.backup captures a consistent database, including triggers; raw copies
    # while a writer is running are not advertised as valid backups.
    with sqlite3.connect(pilot.db_path) as source, sqlite3.connect(restored_path) as destination:
        source.backup(destination)
    pilot.engine.dispose()
    # A fresh connection to the original persistent file reads the same record.
    with pilot.sessions() as reopened:
        assert editor.public_object(reopened, item["entity_id"]) == original
    restored_engine = create_engine(f"sqlite:///{restored_path}")
    with sessionmaker(bind=restored_engine)() as db:
        assert editor.public_object(db, item["entity_id"]) == original
        restored_revision = db.get(editor.EditorRevision, item["accepted_revision_id"])
        assert restored_revision.packet == packet_before
        assert restored_revision.packet_digest == digest_before == editor.digest(restored_revision.packet)
        assert [(row.id, row.payload) for row in db.query(editor.EditorEvent).order_by(editor.EditorEvent.created_at, editor.EditorEvent.id)] == events_before
    with pytest.raises(DatabaseError, match="immutable_editor_record"):
        with restored_engine.begin() as connection:
            connection.execute(text("DELETE FROM knowledge_editor_revisions"))
    restored_engine.dispose()


def test_sql_failure_does_not_acknowledge_saved_draft(pilot, monkeypatch):
    def unavailable(*args, **kwargs):
        raise RuntimeError("isolated simulated commit failure")
    monkeypatch.setattr(editor, "commit", unavailable)
    response = pilot.client.post(BASE + "/drafts", json={"content": complete_content()}, headers=pilot.headers())
    assert response.status_code == 500
    with pilot.sessions() as db:
        assert db.query(editor.EditorDraft).count() == 0
        assert db.query(editor.EditorObject).count() == 0


def test_no_atlas_airtable_call_on_editor_accept_publish(pilot, monkeypatch):
    import app.moderation.service as legacy
    def forbidden(*args, **kwargs):
        pytest.fail("editor touched legacy Airtable publish")
    monkeypatch.setattr(legacy, "create_airtable_feature", forbidden)
    monkeypatch.setattr(legacy, "find_existing_airtable_feature", forbidden)
    monkeypatch.setattr(legacy, "approve_draft", forbidden)
    published(pilot, accepted(pilot, submitted(pilot, created(pilot))))


def test_private_api_responses_not_cached(pilot):
    response = pilot.client.get(BASE + "/drafts", headers=pilot.headers())
    assert response.headers["cache-control"] == "no-store"


def test_moderator_cannot_read_unsubmitted_draft_or_private_sibling_correction(pilot):
    initial = created(pilot, actor="author")
    call(pilot, "get", f"/drafts/{initial['id']}", actor="reviewer", expected=404)
    call(pilot, "get", f"/drafts/{initial['id']}/history", actor="reviewer", expected=404)
    initial = accepted(pilot, submitted(pilot, initial, "author"), "reviewer")
    candidate = call(pilot, "post", f"/revisions/{initial['accepted_revision_id']}/corrections", {
        "expected_revision_id": initial["accepted_revision_id"], "expected_object_version": initial["object_version"],
        "reason": "Private unsubmitted correction"}, actor="author", expected=201)
    call(pilot, "get", f"/drafts/{candidate['id']}", actor="reviewer", expected=404)
    history = call(pilot, "get", f"/drafts/{initial['id']}/history", actor="reviewer")
    assert all(row["draft_id"] != candidate["id"] for row in history["events"])
    assert "Private unsubmitted correction" not in json.dumps(history)


def test_tampered_submitted_content_fails_closed_against_saved_digest(pilot):
    item = submitted(pilot, created(pilot))
    altered = copy.deepcopy(item["content"])
    altered["claim"]["statement"] = "Unauthorized replacement."
    with pilot.sessions() as db:
        db.query(editor.EditorDraft).filter_by(id=item["id"]).update({"content": altered})
        db.commit()
    call(pilot, "post", f"/drafts/{item['id']}/review", review_payload(item), expected=409)
    with pilot.sessions() as db:
        assert db.query(editor.EditorRevision).count() == 0


def test_literal_native_expression_and_unresolved_precision_survive_revision(pilot):
    content = complete_content()
    raw = '  circa 1931?\n"Основание не проверено" — 文献\n  '
    content["evidence"]["native_expression"] = raw
    item = accepted(pilot, submitted(pilot, created(pilot, content)))
    packet = call(pilot, "get", f"/drafts/{item['id']}/history")["revisions"][0]["packet"]
    assert packet["source_value"] == {"raw_expression": raw, "precision": "unresolved", "normalized_value": None}
    assert packet["content"]["evidence"]["native_expression"] == raw


def test_sql_cas_rejects_cached_draft_from_another_session(pilot):
    item = created(pilot)
    with pilot.sessions() as first, pilot.sessions() as second:
        stale = first.get(editor.EditorDraft, item["id"])
        fresh = second.get(editor.EditorDraft, item["id"])
        user = second.get(User, "owner")
        from app.knowledge_editor.schemas import CandidateContent
        editor.replace_draft(second, user, fresh, 1, CandidateContent.model_validate(complete_content()))
        with pytest.raises(editor.KnowledgeEditorError) as failure:
            editor.replace_draft(first, first.get(User, "owner"), stale, 1, CandidateContent.model_validate(complete_content()))
        assert failure.value.status_code == 409
    assert call(pilot, "get", f"/drafts/{item['id']}")["version"] == 2


def test_stale_competing_correction_can_be_rejected_without_accepting_fork(pilot):
    first = accepted(pilot, submitted(pilot, created(pilot)))
    pending = []
    for candidate in [correction(pilot, first), correction(pilot, first)]:
        data = candidate["content"]
        data["human_authored_attestation"] = True
        candidate = call(pilot, "put", f"/drafts/{candidate['id']}", {"expected_version": candidate["version"], "content": data})
        pending.append(submitted(pilot, candidate))
    accepted(pilot, pending[0])
    call(pilot, "post", f"/drafts/{pending[1]['id']}/review", review_payload(pending[1]), expected=409)
    rejected = call(pilot, "post", f"/drafts/{pending[1]['id']}/review", review_payload(pending[1], "reject"))
    assert rejected["state"] == "rejected"
    assert rejected["accepted_revision_id"] is None
    assert call(pilot, "get", "/review-queue") == []
