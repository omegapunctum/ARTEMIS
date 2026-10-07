"""Read-only portable public history and unsigned integrity verification.

This module's offline validation path imports no database or HTTP application.
Hashes prove internal consistency only; they establish no signer authenticity,
source correctness, rights or historical acceptance.
"""
from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "knowledge-editor-public-export-v1"
PUBLICATION_SCOPE = "editorial_candidate_not_globe_corpus"
MAX_PACKAGE_BYTES = 32 * 1024 * 1024
_SCHEMA = json.loads(Path(__file__).with_name("public_export.schema.json").read_text(encoding="utf-8"))
_VALIDATOR = Draft202012Validator(_SCHEMA, format_checker=FormatChecker())
_SNAPSHOT_VALIDATOR = Draft202012Validator(
    {"$ref": "#/$defs/snapshot", "$defs": _SCHEMA["$defs"]}, format_checker=FormatChecker())


class InvalidPublicExport(ValueError):
    """Deliberately generic: never expose content in errors or logs."""


class PublicExportTooLarge(InvalidPublicExport):
    pass


def invalid():
    raise InvalidPublicExport("invalid_public_export")


def canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def validate_snapshot(snapshot: dict) -> None:
    _SNAPSHOT_VALIDATOR.validate(snapshot)
    # The schema checks naive ISO shape; check calendar/time values as well.
    datetime.fromisoformat(snapshot["published_at"])
    entity, source, claim, evidence = (snapshot[key] for key in ("entity", "source", "claim", "evidence"))
    if (entity["id"] != snapshot["entity_id"] or claim["subject_id"] != entity["id"]
            or evidence["claim_id"] != claim["id"] or evidence["source_id"] != source["id"]
            or snapshot["predecessor_revision_id"] == snapshot["revision_id"]):
        invalid()
    url = source["url"]
    if url is not None:
        parsed = urlsplit(url)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(ord(char) < 32 or char.isspace() for char in url)):
            invalid()
        parsed.port  # Reject invalid ports without requesting the URL.
    if claim["confidence"] != "unknown" and not (claim["confidence_basis"] or "").strip():
        invalid()
    payload = {key: value for key, value in snapshot.items() if key != "public_payload_digest"}
    if digest(payload) != snapshot["public_payload_digest"]:
        invalid()


def validate_package(package: dict) -> None:
    """Check the fixed local schema, all three hashes and public references."""
    _VALIDATOR.validate(package)
    snapshots = package["snapshots"]
    snapshot_ids = [snapshot["snapshot_id"] for snapshot in snapshots]
    revision_ids = [snapshot["revision_id"] for snapshot in snapshots]
    if (len(set(snapshot_ids)) != len(snapshot_ids) or len(set(revision_ids)) != len(revision_ids)
            or package["current_snapshot_id"] not in snapshot_ids
            or snapshots != sorted(snapshots, key=lambda item: (item["published_at"], item["snapshot_id"]))):
        invalid()
    predecessors = {snapshot["revision_id"]: snapshot["predecessor_revision_id"] for snapshot in snapshots}
    manifest = []
    gaps = set()
    checked_revisions = set()
    for snapshot in snapshots:
        validate_snapshot(snapshot)
        if snapshot["entity_id"] != package["entity_id"] or snapshot["target_series_id"] != package["target_series_id"]:
            invalid()
        predecessor = snapshot["predecessor_revision_id"]
        if predecessor is not None:
            if predecessor not in predecessors:
                gaps.add(predecessor)
        seen = set()
        cursor = snapshot["revision_id"]
        while cursor in predecessors and cursor not in checked_revisions:
            if cursor in seen:
                invalid()
            seen.add(cursor)
            cursor = predecessors[cursor]
        checked_revisions.update(seen)
        manifest.append({"snapshot_id": snapshot["snapshot_id"], "revision_id": snapshot["revision_id"],
            "snapshot_digest": digest(snapshot)})
    if (package["manifest"]["snapshots"] != manifest
            or package["manifest"]["unresolved_predecessor_revision_ids"] != sorted(gaps)
            or digest({key: value for key, value in package.items() if key != "package_digest"}) != package["package_digest"]):
        invalid()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            invalid()
        result[key] = value
    return result


def _reject_constant(_value):
    invalid()


def verify_file(path) -> None:
    """Read at most the shared bound + 1 byte; no writes, URLs or database."""
    with open(path, "rb") as stream:
        data = stream.read(MAX_PACKAGE_BYTES + 1)
    if len(data) > MAX_PACKAGE_BYTES:
        raise PublicExportTooLarge("export_too_large")
    package = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    validate_package(package)


def public_export(db, entity_id: str) -> bytes:
    """Capture only scalar root and immutable publication columns in one SELECT.

    Scalar columns bypass stale ORM identity-map roots. A single statement makes
    pointer/history coherent even when a publication commits concurrently.
    """
    from sqlalchemy import select
    from .service import EditorObject, EditorPublication, fail

    statement = select(EditorObject.id, EditorObject.target_series_id, EditorObject.published_snapshot_id,
        EditorPublication.id, EditorPublication.revision_id, EditorPublication.entity_id,
        EditorPublication.public_payload, EditorPublication.payload_digest).outerjoin(
            EditorPublication, EditorPublication.entity_id == EditorObject.id).where(
                EditorObject.id == entity_id, EditorObject.published_snapshot_id.isnot(None))
    # A read-only operation must not flush pending mutations in a reused session.
    with db.no_autoflush:
        rows = db.execute(statement).all()
    if not rows:
        fail("publication_not_found", 404)
    root_id, series_id, current_id = rows[0][:3]
    snapshots = []
    for row in rows:
        obj_id, obj_series, obj_current, snapshot_id, revision_id, published_entity, payload, payload_digest = row
        if (row[:3] != rows[0][:3] or not isinstance(payload, dict)
                or "public_payload_digest" in payload
                or payload.get("snapshot_id") != snapshot_id or payload.get("revision_id") != revision_id
                or payload.get("entity_id") != published_entity or published_entity != obj_id
                or payload.get("target_series_id") != obj_series):
            invalid()
        snapshots.append({**payload, "public_payload_digest": payload_digest})
    snapshots.sort(key=lambda item: (item["published_at"], item["snapshot_id"]))
    revision_ids = {snapshot["revision_id"] for snapshot in snapshots}
    package = {"schema_version": SCHEMA_VERSION, "publication_scope": PUBLICATION_SCOPE,
        "entity_id": root_id, "target_series_id": series_id, "current_snapshot_id": current_id,
        "manifest": {"snapshots": [{"snapshot_id": snapshot["snapshot_id"], "revision_id": snapshot["revision_id"],
            "snapshot_digest": digest(snapshot)} for snapshot in snapshots],
            "unresolved_predecessor_revision_ids": sorted({snapshot["predecessor_revision_id"] for snapshot in snapshots
                if snapshot["predecessor_revision_id"] is not None and snapshot["predecessor_revision_id"] not in revision_ids})},
        "snapshots": snapshots}
    package["package_digest"] = digest(package)
    validate_package(package)
    data = canonical_bytes(package)
    if len(data) > MAX_PACKAGE_BYTES:
        raise PublicExportTooLarge("export_too_large")
    return data
