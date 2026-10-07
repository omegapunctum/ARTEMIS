from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.service import User
from app.moderation.service import is_moderator
from .schemas import CandidateContent, CorrectionRequest, PublishRequest, ReviewRequest

# These tables represent editorial candidates, not canonical historical acceptance.
# Read the current auth module at initialization; tests may rebind its engine.
Base = auth_service.Base
SCHEMA_VERSION = "knowledge-editor-v1"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_id() -> str:
    return str(uuid4())


def digest(value) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


class EditorObject(Base):
    __tablename__ = "knowledge_editor_objects"
    id = Column(String, primary_key=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_series_id = Column(String, nullable=False, unique=True)
    version = Column(Integer, nullable=False, default=1)
    accepted_revision_id = Column(String, nullable=True)
    published_snapshot_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class EditorDraft(Base):
    __tablename__ = "knowledge_editor_drafts"
    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey("knowledge_editor_objects.id"), nullable=False, index=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    source_id = Column(String, nullable=False)
    claim_id = Column(String, nullable=False)
    evidence_link_id = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    state = Column(String, nullable=False, default="draft")
    content = Column(JSON, nullable=False)
    content_digest = Column(String, nullable=False)
    submitted_digest = Column(String, nullable=True)
    predecessor_revision_id = Column(String, nullable=True)
    correction_reason = Column(String, nullable=True)
    accepted_revision_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow)


class EditorRevision(Base):
    __tablename__ = "knowledge_editor_revisions"
    __table_args__ = (UniqueConstraint("predecessor_revision_id"),)
    id = Column(String, primary_key=True)
    draft_id = Column(String, ForeignKey("knowledge_editor_drafts.id"), nullable=False, unique=True)
    entity_id = Column(String, ForeignKey("knowledge_editor_objects.id"), nullable=False, index=True)
    predecessor_revision_id = Column(String, nullable=True)
    packet = Column(JSON, nullable=False)
    packet_digest = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class EditorPublication(Base):
    __tablename__ = "knowledge_editor_publications"
    id = Column(String, primary_key=True)
    revision_id = Column(String, ForeignKey("knowledge_editor_revisions.id"), nullable=False, unique=True)
    entity_id = Column(String, ForeignKey("knowledge_editor_objects.id"), nullable=False, index=True)
    public_payload = Column(JSON, nullable=False)
    payload_digest = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class EditorEvent(Base):
    __tablename__ = "knowledge_editor_events"
    id = Column(String, primary_key=True)
    draft_id = Column(String, ForeignKey("knowledge_editor_drafts.id"), nullable=False, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


def init_db() -> None:
    """Additive, owner-startup-only initialization; never rebuild legacy rows."""
    tables = [model.__table__ for model in (EditorObject, EditorDraft, EditorRevision, EditorPublication, EditorEvent)]
    if auth_service.engine.dialect.name != "sqlite":
        raise RuntimeError("Knowledge Editor v1 requires its reviewed SQLite backend")
    Base.metadata.create_all(bind=auth_service.engine, tables=tables, checkfirst=True)
    with auth_service.engine.begin() as connection:
        for model in (EditorRevision, EditorPublication, EditorEvent):
            table = model.__tablename__
            for operation in ("UPDATE", "DELETE"):
                connection.execute(text(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_immutable_{operation.lower()} "
                    f"BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable_editor_record'); END"
                ))


class KnowledgeEditorError(HTTPException):
    """Scoped errors keep machine-readable editor conflicts out of legacy handlers."""


def fail(code: str, status: int = 409, **fields):
    raise KnowledgeEditorError(status_code=status, detail={"code": code, **fields})


def moderator(user: User) -> None:
    if not is_moderator(user):
        fail("moderator_required", 403)


def object_for(db: Session, entity_id: str) -> EditorObject:
    item = db.get(EditorObject, entity_id)
    if item is None:
        fail("record_not_found", 404)
    return item


def private_draft(db: Session, user: User, draft_id: str, *, author_only: bool = False) -> EditorDraft:
    item = db.get(EditorDraft, draft_id)
    if item is None or (item.owner_id != user.id and (author_only or not is_moderator(user) or item.state == "draft")):
        fail("record_not_found", 404)
    return item


def event(db: Session, draft: EditorDraft, user: User, action: str, payload: dict) -> None:
    db.add(EditorEvent(id=new_id(), draft_id=draft.id, actor_id=user.id, action=action, payload=payload))


def commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        fail("concurrent_transition")


def cas_draft(db: Session, item: EditorDraft, version: int, states: set[str], changes: dict) -> None:
    count = db.query(EditorDraft).filter(
        EditorDraft.id == item.id, EditorDraft.version == version, EditorDraft.state.in_(states)
    ).update({**changes, "version": version + 1, "updated_at": utcnow()}, synchronize_session=False)
    if count != 1:
        db.rollback()
        fail("stale_version_or_state")


def serialize_draft(db: Session, item: EditorDraft, user: User) -> dict:
    db.refresh(item)
    obj = object_for(db, item.entity_id)
    revision = db.get(EditorRevision, item.accepted_revision_id) if item.accepted_revision_id else None
    can_moderate = is_moderator(user)
    editable = item.owner_id == user.id and item.state in {"draft", "request_changes", "rejected"}
    return {
        "id": item.id, "entity_id": item.entity_id, "target_series_id": obj.target_series_id,
        "source_id": item.source_id, "claim_id": item.claim_id, "evidence_link_id": item.evidence_link_id,
        "owner_id": item.owner_id, "version": item.version, "object_version": obj.version,
        "state": item.state, "content": item.content, "content_digest": item.content_digest,
        "submitted_digest": item.submitted_digest, "predecessor_revision_id": item.predecessor_revision_id,
        "correction_reason": item.correction_reason, "accepted_revision_id": item.accepted_revision_id,
        "accepted_revision_digest": revision.packet_digest if revision else None,
        "latest_accepted_revision_id": obj.accepted_revision_id, "published_snapshot_id": obj.published_snapshot_id,
        "review_mode": revision.packet["review_receipt"]["review_mode"] if revision else None,
        "epistemic": {"claim_review_state": "draft", "source_review_state": "draft", "evidence_link_review_state": "draft", "evidence_state": "missing"},
        "created_at": item.created_at.isoformat(), "updated_at": item.updated_at.isoformat(),
        "capabilities": {"can_edit": editable, "can_submit": editable,
            "can_review": can_moderate and item.state == "submitted",
            "can_publish": can_moderate and item.state == "accepted" and obj.accepted_revision_id == item.accepted_revision_id
                and not db.query(EditorPublication).filter_by(revision_id=item.accepted_revision_id).first(),
            "can_correct": item.owner_id == user.id and revision is not None and obj.accepted_revision_id == item.accepted_revision_id},
    }


def create_draft(db: Session, user: User, content: CandidateContent) -> EditorDraft:
    data = content.model_dump(mode="json")
    obj = EditorObject(id=new_id(), owner_id=user.id, target_series_id=new_id(), version=1)
    item = EditorDraft(id=new_id(), entity_id=obj.id, owner_id=user.id, source_id=new_id(), claim_id=new_id(),
        evidence_link_id=new_id(), version=1, state="draft", content=data, content_digest=digest(data))
    db.add(obj)
    db.add(item)
    event(db, item, user, "created", {"version": 1, "content_digest": item.content_digest, "content": data})
    commit(db)
    return item


def replace_draft(db: Session, user: User, item: EditorDraft, version: int, content: CandidateContent) -> EditorDraft:
    if item.owner_id != user.id:
        fail("record_not_found", 404)
    data = content.model_dump(mode="json")
    hashed = digest(data)
    cas_draft(db, item, version, {"draft", "request_changes", "rejected"},
        {"content": data, "content_digest": hashed, "state": "draft", "submitted_digest": None})
    event(db, item, user, "saved", {"version": version + 1, "content_digest": hashed, "content": data})
    commit(db)
    return item


def submit_draft(db: Session, user: User, item: EditorDraft, version: int) -> EditorDraft:
    if item.owner_id != user.id:
        fail("record_not_found", 404)
    if item.version != version or item.state not in {"draft", "request_changes", "rejected"}:
        fail("stale_version_or_state")
    gaps = CandidateContent.model_validate(item.content).submission_gaps()
    if gaps:
        fail("submission_incomplete", 422, fields=gaps)
    obj = object_for(db, item.entity_id)
    if obj.accepted_revision_id != item.predecessor_revision_id:
        fail("stale_predecessor")
    cas_draft(db, item, version, {"draft", "request_changes", "rejected"},
        {"state": "submitted", "submitted_digest": item.content_digest})
    event(db, item, user, "submitted", {"version": version + 1, "submitted_digest": item.content_digest,
        "predecessor_revision_id": item.predecessor_revision_id})
    commit(db)
    return item


def review_draft(db: Session, user: User, item: EditorDraft, request: ReviewRequest) -> EditorDraft:
    moderator(user)
    if item.version != request.expected_version or item.state != "submitted":
        fail("stale_version_or_state")
    if item.submitted_digest != request.submitted_digest or digest(item.content) != request.submitted_digest:
        fail("submitted_digest_mismatch")
    if request.expected_predecessor_revision_id != item.predecessor_revision_id:
        fail("stale_predecessor")
    obj = object_for(db, item.entity_id)
    if request.decision == "accept" and obj.accepted_revision_id != item.predecessor_revision_id:
        fail("stale_predecessor")
    mode = "owner_self_review" if user.id == item.owner_id else "separate_principal_review"
    if item.content["claim"]["origin"] != "user" or not item.content["human_authored_attestation"]:
        fail("human_authored_proposal_required", 422)
    changes = {"state": request.decision if request.decision != "accept" else "accepted"}
    if request.decision == "reject":
        changes["state"] = "rejected"
    revision = None
    if request.decision == "accept":
        revision_id = new_id()
        now = utcnow().isoformat()
        source_value = {"raw_expression": item.content["evidence"]["native_expression"], "precision": "unresolved", "normalized_value": None}
        source_packet = {"source": item.content["source"], "evidence": item.content["evidence"], "source_value": source_value}
        packet = {"schema_version": SCHEMA_VERSION, "revision_id": revision_id, "entity_id": obj.id,
            "target_series_id": obj.target_series_id, "source_id": item.source_id, "claim_id": item.claim_id,
            "evidence_link_id": item.evidence_link_id, "operation": "correct" if item.predecessor_revision_id else "initial",
            "predecessor_revision_id": item.predecessor_revision_id, "correction_reason": item.correction_reason,
            "recorded_at": now, "content": item.content, "submitted_digest": item.submitted_digest,
            "source_value": source_value, "source_value_digest": digest(source_value), "source_packet_digest": digest(source_packet),
            "epistemic": {"claim_review_state": "draft", "source_review_state": "draft", "evidence_link_review_state": "draft", "evidence_state": "missing"},
            "review_receipt": {"reviewer_actor_id": user.id, "author_actor_id": item.owner_id,
                "review_mode": mode, "reason": request.reason, "editorial_only": True}}
        revision = EditorRevision(id=revision_id, draft_id=item.id, entity_id=obj.id,
            predecessor_revision_id=item.predecessor_revision_id, packet=packet, packet_digest=digest(packet))
        # Atomic head transition prevents two revisions accepting the same predecessor.
        count = db.query(EditorObject).filter(EditorObject.id == obj.id,
            EditorObject.accepted_revision_id == item.predecessor_revision_id,
            EditorObject.version == obj.version).update(
                {"accepted_revision_id": revision_id, "version": obj.version + 1}, synchronize_session=False)
        if count != 1:
            db.rollback()
            fail("stale_predecessor")
        changes["accepted_revision_id"] = revision_id
    cas_draft(db, item, request.expected_version, {"submitted"}, changes)
    if revision is not None:
        db.add(revision)
    event(db, item, user, "reviewed", {"decision": request.decision, "reason": request.reason,
        "review_mode": mode, "submitted_digest": request.submitted_digest,
        "version": request.expected_version + 1, "revision_id": revision.id if revision else None})
    commit(db)
    return item


def publish_revision(db: Session, user: User, item: EditorDraft, request: PublishRequest) -> EditorDraft:
    moderator(user)
    if item.state != "accepted" or item.version != request.expected_version:
        fail("stale_version_or_state")
    revision = db.get(EditorRevision, request.accepted_revision_id)
    if revision is None or revision.id != item.accepted_revision_id:
        fail("accepted_revision_required")
    if revision.packet_digest != request.accepted_revision_digest or digest(revision.packet) != request.accepted_revision_digest:
        fail("accepted_revision_digest_mismatch")
    obj = object_for(db, item.entity_id)
    snapshot_id = new_id()
    now = utcnow().isoformat()
    packet = revision.packet
    public = {"schema_version": SCHEMA_VERSION, "snapshot_id": snapshot_id, "entity_id": obj.id,
        "target_series_id": obj.target_series_id, "revision_id": revision.id, "revision_digest": revision.packet_digest,
        "predecessor_revision_id": revision.predecessor_revision_id, "content_digest": packet["submitted_digest"],
        "published_at": now, "review_mode": packet["review_receipt"]["review_mode"],
        "editorial_only": True, "publication_scope": "editorial_candidate_not_globe_corpus",
        "entity": {"id": obj.id, "type": "architecture", **packet["content"]["entity"], "position": None, "world_time": None},
        "source": {"id": packet["source_id"], **packet["content"]["source"], "review_state": "draft"},
        "claim": {"id": packet["claim_id"], "subject_id": obj.id, **packet["content"]["claim"], "review_state": "draft", "evidence_state": "missing"},
        "evidence": {"id": packet["evidence_link_id"], "claim_id": packet["claim_id"], "source_id": packet["source_id"],
            **{key: packet["content"]["evidence"][key] for key in ("locator", "relation_to_claim", "evidence_strength", "native_precision")},
            "normalized_value": None, "review_state": "draft"},
        "source_value_digest": packet["source_value_digest"], "source_packet_digest": packet["source_packet_digest"]}
    count = db.query(EditorObject).filter(EditorObject.id == obj.id,
        EditorObject.accepted_revision_id == revision.id, EditorObject.version == request.expected_object_version,
        EditorObject.published_snapshot_id == request.expected_publication_id).update(
            {"published_snapshot_id": snapshot_id, "version": request.expected_object_version + 1}, synchronize_session=False)
    if count != 1:
        db.rollback()
        fail("stale_publication")
    cas_draft(db, item, request.expected_version, {"accepted"}, {})
    db.add(EditorPublication(id=snapshot_id, revision_id=revision.id, entity_id=obj.id,
        public_payload=public, payload_digest=digest(public)))
    event(db, item, user, "published", {"snapshot_id": snapshot_id, "revision_id": revision.id,
        "revision_digest": revision.packet_digest, "public_payload_digest": digest(public),
        "version": request.expected_version + 1, "previous_snapshot_id": request.expected_publication_id})
    commit(db)
    return item


def create_correction(db: Session, user: User, revision_id: str, request: CorrectionRequest) -> EditorDraft:
    revision = db.get(EditorRevision, revision_id)
    if revision is None:
        fail("record_not_found", 404)
    obj = object_for(db, revision.entity_id)
    if obj.owner_id != user.id:
        fail("record_not_found", 404)
    if revision.id != request.expected_revision_id or obj.accepted_revision_id != revision.id or obj.version != request.expected_object_version:
        fail("stale_predecessor")
    # Revision packets remain immutable. A correction receives new content identities.
    data = json.loads(json.dumps(revision.packet["content"]))
    data["human_authored_attestation"] = False
    item = EditorDraft(id=new_id(), entity_id=obj.id, owner_id=user.id, source_id=new_id(), claim_id=new_id(),
        evidence_link_id=new_id(), version=1, state="draft", content=data, content_digest=digest(data),
        predecessor_revision_id=revision.id, correction_reason=request.reason)
    db.add(item)
    event(db, item, user, "correction_created", {"version": 1, "predecessor_revision_id": revision.id,
        "reason": request.reason, "content_digest": item.content_digest, "content": data})
    commit(db)
    return item


def history(db: Session, user: User, item: EditorDraft) -> dict:
    # Include all drafts in this author's series, including retained prior publications.
    drafts = db.query(EditorDraft).filter_by(entity_id=item.entity_id).all()
    ids = [row.id for row in drafts if item.owner_id == user.id or row.state != "draft"]
    query = db.query(EditorEvent).filter(EditorEvent.draft_id.in_(ids))
    if item.owner_id != user.id:
        query = query.filter(EditorEvent.action.in_(["submitted", "reviewed", "published"]))
    events = query.order_by(EditorEvent.created_at, EditorEvent.id).all()
    revisions = db.query(EditorRevision).filter_by(entity_id=item.entity_id).order_by(EditorRevision.created_at).all()
    return {"entity_id": item.entity_id,
        "events": [{"id": row.id, "draft_id": row.draft_id, "actor_id": row.actor_id, "action": row.action,
            "recorded_at": row.created_at.isoformat(), "payload": row.payload} for row in events],
        "revisions": [{"revision_id": row.id, "revision_digest": row.packet_digest, "packet": row.packet} for row in revisions]}


def public_history(db: Session, entity_id: str) -> list[dict]:
    obj = db.get(EditorObject, entity_id)
    if obj is None or not obj.published_snapshot_id:
        fail("publication_not_found", 404)
    rows = db.query(EditorPublication).filter_by(entity_id=entity_id).order_by(EditorPublication.created_at).all()
    return [{"snapshot_id": entry.id, "revision_id": entry.revision_id,
        "published_at": entry.public_payload["published_at"]} for entry in rows]


def public_snapshot(db: Session, snapshot_id: str) -> dict:
    row = db.get(EditorPublication, snapshot_id)
    if row is None:
        fail("publication_not_found", 404)
    # This complete response is immutable. Mutable history lives on object URLs.
    return {**row.public_payload, "public_payload_digest": row.payload_digest}


def public_object(db: Session, entity_id: str) -> dict:
    obj = db.get(EditorObject, entity_id)
    if obj is None or not obj.published_snapshot_id:
        fail("publication_not_found", 404)
    return {**public_snapshot(db, obj.published_snapshot_id), "published_snapshots": public_history(db, entity_id)}
