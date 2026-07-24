from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.auth.migrations import apply_versioned_migrations
from app.auth.service import Base, User, engine

from .schemas import (
    PublicResearchSliceResponse,
    RESEARCH_SLICE_SCHEMA_VERSION,
    ResearchSliceCreate,
    ResearchSliceListItem,
    ResearchSliceResponse,
    ResearchSliceUpdate,
)


class ResearchSlice(Base):
    __tablename__ = "research_slices"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    research_question = Column(String, nullable=False, default="")
    selection_rationale = Column(String, nullable=False, default="")
    evidence_state = Column(String, nullable=False, default="missing")
    evidence_refs_json = Column(JSON, nullable=False, default=list)
    findings_json = Column(JSON, nullable=False, default=list)
    conclusion_status = Column(String, nullable=False, default="unresolved")
    conclusion = Column(String, nullable=False, default="")
    uncertainty_notes = Column(String, nullable=False, default="")
    schema_version = Column(String, nullable=False, default=RESEARCH_SLICE_SCHEMA_VERSION)
    content_version = Column(Integer, nullable=False, default=1)
    visibility = Column(String, nullable=False, default="private")
    feature_refs_json = Column(JSON, nullable=False)
    time_range_json = Column(JSON, nullable=False)
    view_state_json = Column(JSON, nullable=False)
    filter_state_json = Column(JSON, nullable=False, default=dict)
    comparison_feature_ids_json = Column(JSON, nullable=False, default=list)
    annotations_json = Column(JSON, nullable=False)
    share_token_hash = Column(String, nullable=True, unique=True)
    shared_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def _migration_create_research_slices(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS research_slices (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                description VARCHAR NOT NULL DEFAULT '',
                visibility VARCHAR NOT NULL DEFAULT 'private',
                feature_refs_json JSON NOT NULL,
                time_range_json JSON NOT NULL,
                view_state_json JSON NOT NULL,
                annotations_json JSON NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
    )
    connection.execute(
        text("CREATE INDEX IF NOT EXISTS ix_research_slices_user_id ON research_slices(user_id)")
    )


def _research_slice_columns(connection: Connection) -> set[str]:
    return {row[1] for row in connection.execute(text("PRAGMA table_info(research_slices)"))}


def _migration_research_slices_add_share_capability(connection: Connection) -> None:
    columns = _research_slice_columns(connection)
    if "share_token_hash" not in columns:
        connection.execute(text("ALTER TABLE research_slices ADD COLUMN share_token_hash VARCHAR"))
    if "shared_at" not in columns:
        connection.execute(text("ALTER TABLE research_slices ADD COLUMN shared_at DATETIME"))
    connection.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "ix_research_slices_share_token_hash ON research_slices(share_token_hash)"
        )
    )


def _migration_research_slices_v2(connection: Connection) -> None:
    columns = _research_slice_columns(connection)
    additions = [
        ("research_question", "VARCHAR NOT NULL DEFAULT ''"),
        ("selection_rationale", "VARCHAR NOT NULL DEFAULT ''"),
        ("evidence_state", "VARCHAR NOT NULL DEFAULT 'missing'"),
        ("evidence_refs_json", "JSON NOT NULL DEFAULT '[]'"),
        ("findings_json", "JSON NOT NULL DEFAULT '[]'"),
        ("conclusion_status", "VARCHAR NOT NULL DEFAULT 'unresolved'"),
        ("conclusion", "VARCHAR NOT NULL DEFAULT ''"),
        ("uncertainty_notes", "VARCHAR NOT NULL DEFAULT ''"),
        ("schema_version", "VARCHAR NOT NULL DEFAULT '2.0'"),
        ("content_version", "INTEGER NOT NULL DEFAULT 1"),
        ("filter_state_json", "JSON NOT NULL DEFAULT '{}'"),
        ("comparison_feature_ids_json", "JSON NOT NULL DEFAULT '[]'"),
    ]
    for name, ddl in additions:
        if name not in columns:
            connection.execute(text(f"ALTER TABLE research_slices ADD COLUMN {name} {ddl}"))

    # Deterministic, fail-closed legacy mapping. It preserves ownership/share state and
    # never invents evidence or a conclusion.
    connection.execute(
        text(
            """
            UPDATE research_slices
            SET research_question = CASE
                    WHEN TRIM(COALESCE(research_question, '')) = '' THEN title
                    ELSE research_question
                END,
                selection_rationale = CASE
                    WHEN TRIM(COALESCE(selection_rationale, '')) = ''
                    THEN CASE
                        WHEN TRIM(COALESCE(description, '')) <> '' THEN description
                        ELSE 'Selection rationale was not captured in the legacy slice.'
                    END
                    ELSE selection_rationale
                END,
                evidence_state = CASE
                    WHEN TRIM(COALESCE(evidence_state, '')) = '' THEN 'missing'
                    ELSE evidence_state
                END,
                evidence_refs_json = COALESCE(evidence_refs_json, '[]'),
                findings_json = CASE
                    WHEN findings_json IS NULL OR findings_json = '[]' THEN annotations_json
                    ELSE findings_json
                END,
                conclusion_status = CASE
                    WHEN TRIM(COALESCE(conclusion_status, '')) = '' THEN 'unresolved'
                    ELSE conclusion_status
                END,
                conclusion = COALESCE(conclusion, ''),
                uncertainty_notes = COALESCE(uncertainty_notes, ''),
                schema_version = '2.0',
                content_version = CASE
                    WHEN content_version IS NULL OR content_version < 1 THEN 1
                    ELSE content_version
                END,
                filter_state_json = COALESCE(filter_state_json, '{}'),
                comparison_feature_ids_json = CASE
                    WHEN comparison_feature_ids_json IS NULL THEN '[]'
                    ELSE comparison_feature_ids_json
                END
            """
        )
    )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        apply_versioned_migrations(
            connection,
            [
                (201, "research_slices_create_table", _migration_create_research_slices),
                (202, "research_slices_add_share_capability", _migration_research_slices_add_share_capability),
                (203, "research_slices_product_complete_v2", _migration_research_slices_v2),
            ],
        )


def _dump_model(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def _payload_from_item(item: ResearchSlice) -> dict:
    time_range = item.time_range_json or {}
    view_state = item.view_state_json or {}
    findings = item.findings_json if item.findings_json is not None else (item.annotations_json or [])
    comparison_ids = item.comparison_feature_ids_json or [
        str(entry.get("feature_id", "")).strip()
        for entry in (item.feature_refs_json or [])
        if isinstance(entry, dict) and str(entry.get("feature_id", "")).strip()
    ]
    return {
        "title": item.title,
        "description": item.description or "",
        "research_question": item.research_question or item.title,
        "selection_rationale": item.selection_rationale
        or item.description
        or "Selection rationale was not captured in the legacy slice.",
        "feature_refs": item.feature_refs_json or [],
        "evidence_state": item.evidence_state or "missing",
        "evidence_refs": item.evidence_refs_json or [],
        "findings": findings,
        "conclusion_status": item.conclusion_status or "unresolved",
        "conclusion": item.conclusion or "",
        "uncertainty_notes": item.uncertainty_notes or "",
        "saved_view": {
            "time_range": time_range,
            "view_state": view_state,
            "filter_state": item.filter_state_json or {},
            "comparison_feature_ids": comparison_ids,
        },
        "schema_version": RESEARCH_SLICE_SCHEMA_VERSION,
        "content_version": max(1, int(item.content_version or 1)),
        "time_range": time_range,
        "view_state": view_state,
        "annotations": findings,
        "visibility": "private",
    }


def _content_status(payload: dict) -> str:
    has_question = bool(str(payload.get("research_question") or "").strip())
    has_rationale = bool(str(payload.get("selection_rationale") or "").strip())
    has_findings = bool(payload.get("findings"))
    evidence_explicit = payload.get("evidence_state") in {"supported", "missing"}
    conclusion_explicit = payload.get("conclusion_status") in {"concluded", "unresolved"}
    has_saved_view = bool(payload.get("saved_view"))
    return "complete" if all(
        [has_question, has_rationale, has_findings, evidence_explicit, conclusion_explicit, has_saved_view]
    ) else "incomplete"


def _apply_payload(item: ResearchSlice, payload: ResearchSliceCreate) -> None:
    saved_view = payload.saved_view
    assert saved_view is not None
    findings = payload.findings or []

    item.title = payload.title
    item.description = payload.description
    item.research_question = payload.research_question or payload.title
    item.selection_rationale = payload.selection_rationale or payload.description
    item.feature_refs_json = [_dump_model(entry) for entry in payload.feature_refs]
    item.evidence_state = payload.evidence_state or "missing"
    item.evidence_refs_json = [_dump_model(entry) for entry in payload.evidence_refs]
    item.findings_json = [_dump_model(entry) for entry in findings]
    item.annotations_json = [_dump_model(entry) for entry in findings]
    item.conclusion_status = payload.conclusion_status
    item.conclusion = payload.conclusion
    item.uncertainty_notes = payload.uncertainty_notes
    item.schema_version = RESEARCH_SLICE_SCHEMA_VERSION
    item.content_version = payload.content_version
    item.time_range_json = _dump_model(saved_view.time_range)
    item.view_state_json = _dump_model(saved_view.view_state)
    item.filter_state_json = dict(saved_view.filter_state)
    item.comparison_feature_ids_json = list(saved_view.comparison_feature_ids)
    item.visibility = "private"


def create_research_slice(db: Session, user: User, payload: ResearchSliceCreate) -> ResearchSlice:
    item = ResearchSlice(user_id=user.id)
    _apply_payload(item, payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_user_research_slice(db: Session, user: User, slice_id: str) -> ResearchSlice:
    item = (
        db.query(ResearchSlice)
        .filter(ResearchSlice.id == slice_id, ResearchSlice.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research slice not found")
    return item


def list_user_research_slices(db: Session, user: User) -> list[ResearchSlice]:
    return (
        db.query(ResearchSlice)
        .filter(ResearchSlice.user_id == user.id)
        .order_by(ResearchSlice.updated_at.desc())
        .all()
    )


def update_user_research_slice(db: Session, item: ResearchSlice, payload: ResearchSliceUpdate) -> ResearchSlice:
    current = _payload_from_item(item)
    changes = payload.model_dump(exclude_unset=True)

    # Compatibility mirrors are derived from the canonical v2 fields.
    if "saved_view" in changes:
        changes["time_range"] = changes["saved_view"]["time_range"]
        changes["view_state"] = changes["saved_view"]["view_state"]
    elif "time_range" in changes or "view_state" in changes:
        saved_view = dict(current["saved_view"])
        if "time_range" in changes:
            saved_view["time_range"] = changes["time_range"]
        if "view_state" in changes:
            saved_view["view_state"] = changes["view_state"]
        changes["saved_view"] = saved_view
    if "findings" in changes:
        changes["annotations"] = changes["findings"]
    elif "annotations" in changes:
        changes["findings"] = changes["annotations"]

    merged = {**current, **changes}
    merged["schema_version"] = RESEARCH_SLICE_SCHEMA_VERSION
    merged["content_version"] = max(1, int(current["content_version"])) + 1
    merged["visibility"] = "private"

    try:
        normalized = ResearchSliceCreate.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(include_url=False),
        ) from exc

    _apply_payload(item, normalized)
    db.commit()
    db.refresh(item)
    return item


def delete_user_research_slice(db: Session, item: ResearchSlice) -> None:
    db.delete(item)
    db.commit()


def _hash_share_token(share_token: str) -> str:
    return sha256(share_token.encode("utf-8")).hexdigest()


def rotate_research_slice_share(db: Session, item: ResearchSlice) -> tuple[str, datetime]:
    share_token = token_urlsafe(32)
    shared_at = datetime.utcnow()
    item.share_token_hash = _hash_share_token(share_token)
    item.shared_at = shared_at
    db.commit()
    db.refresh(item)
    return share_token, shared_at


def revoke_research_slice_share(db: Session, item: ResearchSlice) -> None:
    item.share_token_hash = None
    item.shared_at = None
    db.commit()


def get_shared_research_slice(db: Session, share_token: str) -> ResearchSlice:
    normalized_token = share_token.strip()
    if not normalized_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared research slice not found")
    item = (
        db.query(ResearchSlice)
        .filter(ResearchSlice.share_token_hash == _hash_share_token(normalized_token))
        .first()
    )
    if not item or item.shared_at is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared research slice not found")
    return item


def serialize_research_slice(item: ResearchSlice) -> ResearchSliceResponse:
    payload = _payload_from_item(item)
    return ResearchSliceResponse(
        **payload,
        id=item.id,
        owner_id=item.user_id,
        content_status=_content_status(payload),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_research_slice_list_item(item: ResearchSlice) -> ResearchSliceListItem:
    payload = _payload_from_item(item)
    refs = payload["feature_refs"]
    findings = payload["findings"]
    return ResearchSliceListItem(
        id=item.id,
        title=item.title,
        visibility="private",
        is_shared=bool(item.share_token_hash and item.shared_at),
        feature_count=len(refs),
        finding_count=len(findings),
        annotation_count=len(findings),
        evidence_state=payload["evidence_state"],
        conclusion_status=payload["conclusion_status"],
        content_status=_content_status(payload),
        content_version=payload["content_version"],
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_public_research_slice(item: ResearchSlice) -> PublicResearchSliceResponse:
    if item.shared_at is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared research slice not found")
    payload = _payload_from_item(item)
    payload["visibility"] = "shared_read_only"
    return PublicResearchSliceResponse(
        **payload,
        id=item.id,
        content_status=_content_status(payload),
        shared_at=item.shared_at,
        updated_at=item.updated_at,
    )
