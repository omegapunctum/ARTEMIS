from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.auth.migrations import apply_versioned_migrations
from app.auth.service import Base, User, engine

from .schemas import (
    PublicResearchSliceResponse,
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
    visibility = Column(String, nullable=False, default="private")
    feature_refs_json = Column(JSON, nullable=False)
    time_range_json = Column(JSON, nullable=False)
    view_state_json = Column(JSON, nullable=False)
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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        apply_versioned_migrations(
            connection,
            [
                (201, "research_slices_create_table", _migration_create_research_slices),
                (202, "research_slices_add_share_capability", _migration_research_slices_add_share_capability),
            ],
        )




def _dump_model(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value

def create_research_slice(db: Session, user: User, payload: ResearchSliceCreate) -> ResearchSlice:
    item = ResearchSlice(
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        visibility="private",
        feature_refs_json=[_dump_model(entry) for entry in payload.feature_refs],
        time_range_json=_dump_model(payload.time_range),
        view_state_json=_dump_model(payload.view_state),
        annotations_json=[_dump_model(entry) for entry in payload.annotations],
    )
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
    changes = payload.model_dump(exclude_unset=True)

    if "title" in changes:
        item.title = changes["title"]
    if "description" in changes:
        item.description = changes["description"]
    if "feature_refs" in changes:
        refs = changes["feature_refs"] or []
        item.feature_refs_json = [_dump_model(entry) for entry in refs]
    if "time_range" in changes:
        time_range = changes["time_range"]
        item.time_range_json = _dump_model(time_range)
    if "view_state" in changes:
        view_state = changes["view_state"]
        item.view_state_json = _dump_model(view_state)
    if "annotations" in changes:
        annotations = changes["annotations"] or []
        item.annotations_json = [_dump_model(entry) for entry in annotations]

    item.visibility = "private"

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
    return ResearchSliceResponse(
        id=item.id,
        title=item.title,
        description=item.description or "",
        feature_refs=item.feature_refs_json or [],
        time_range=item.time_range_json or {},
        view_state=item.view_state_json or {},
        annotations=item.annotations_json or [],
        owner_id=item.user_id,
        visibility="private",
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_research_slice_list_item(item: ResearchSlice) -> ResearchSliceListItem:
    refs = item.feature_refs_json or []
    annotations = item.annotations_json or []
    return ResearchSliceListItem(
        id=item.id,
        title=item.title,
        visibility="private",
        is_shared=bool(item.share_token_hash and item.shared_at),
        feature_count=len(refs),
        annotation_count=len(annotations),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_public_research_slice(item: ResearchSlice) -> PublicResearchSliceResponse:
    if item.shared_at is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared research slice not found")
    return PublicResearchSliceResponse(
        id=item.id,
        title=item.title,
        description=item.description or "",
        feature_refs=item.feature_refs_json or [],
        time_range=item.time_range_json or {},
        view_state=item.view_state_json or {},
        annotations=item.annotations_json or [],
        visibility="shared_read_only",
        shared_at=item.shared_at,
        updated_at=item.updated_at,
    )
