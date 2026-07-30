#!/usr/bin/env python3
"""Validate ARTEMIS world-model contract fixtures without runtime migration."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_RELATIVE = Path("fixtures/world_model/v1")
SCHEMA_VERSION = "1.0.0"
REVIEW_SCOPE_ID = "world-model-v1-canonical"
REQUIRED_REVIEW_SCOPE = (
    "docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md",
    "docs/ENTITY_MODEL.md",
    "docs/EPISTEMIC_CONTRACT.md",
    "fixtures/world_model/v1/schema.json",
    "fixtures/world_model/v1/package.json",
    "fixtures/world_model/v1/coverage_manifest.json",
    "fixtures/world_model/v1/compatibility/architecture_atlas_projection.json",
    "fixtures/world_model/v1/sources/field-notebook-alpha.md",
    "fixtures/world_model/v1/sources/field-notebook-beta.md",
    "scripts/validate_world_model_fixtures.py",
    "tests/test_world_model_fixtures.py",
    "requirements.txt",
)
REVIEW_ARTIFACT_FIELDS = (
    "artifact_format",
    "review_id",
    "reviewer_id",
    "reviewer_instance_id",
    "review_track",
    "independence_method",
    "frozen_commit",
    "reviewed_content_sha256",
    "decision",
    "critical_findings",
    "unresolved_material_findings",
    "independence_attestation",
)

COLLECTION_TYPES = {
    "entities": "Entity",
    "events": "Event",
    "states": "State",
    "processes": "Process",
    "trajectories": "Trajectory",
    "regions": "Region",
    "relations": "Relation",
    "derived_observations": "DerivedObservation",
    "claims": "Claim",
    "evidence_links": "EvidenceLink",
    "uncertainties": "Uncertainty",
    "synchronized_views": "SynchronizedView",
    "sources": "Source",
    "layers": "Layer",
}

ALLOWED_CLAIM_KINDS = {
    "factual",
    "observation",
    "inference",
    "interpretation",
    "hypothesis",
    "counterfactual",
}
ALLOWED_ORIGINS = {"curator", "user", "ai", "system", "imported"}
ALLOWED_REVIEW_STATES = {"draft", "reviewed", "contested", "rejected", "superseded"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unknown"}
ALLOWED_EVIDENCE_STATES = {"supported", "mixed", "challenged", "missing", "not_applicable"}
ALLOWED_EVIDENCE_RELATIONS = {"supports", "challenges", "contextualizes"}
ALLOWED_EVIDENCE_STRENGTH = {"direct", "indirect", "background"}
ALLOWED_RECONSTRUCTION_MODES = {
    "historical_assertion",
    "scholarly_reconstruction",
    "alternative_reconstruction",
    "analytical_model",
    "hypothesis",
    "counterfactual",
}
DERIVED_ONLY_PREDICATES = {
    "co_present",
    "temporal_overlap",
    "spatial_overlap",
    "before",
    "after",
    "route_intersection",
    "similarity",
}
ALLOWED_RELATION_DIRECTIONALITY = {"directed", "symmetric"}
DIRECTED_RELATION_PREDICATES = {"influence"}
COMPATIBILITY_SNAPSHOT_FIELDS = (
    "name_en",
    "name_ru",
    "date_start",
    "date_end",
    "latitude",
    "longitude",
    "coordinates_confidence",
    "coordinates_source",
    "source_url",
    "layer_type",
    "validated",
)
COMPATIBILITY_SOURCE_DATASET_FIELDS = {
    "repository",
    "commit",
    "path",
    "source_file_sha256",
    "record_id",
    "canonical_feature_id",
    "record_sha256",
}
COMPATIBILITY_LOSSES = [
    "The current reviewed Source has no bibliographic locator, so no target EvidenceLink is created.",
    "The legacy coordinates_source value does not identify a source record with a reproducible locator.",
    "The legacy exact coordinate confidence is preserved only as legacy metadata; target spatial precision is unknown.",
    "The date strings provide year precision but no claim-level supporting locator.",
    "The current point feature does not encode construction Events, use States, Processes, temporal geometry or uncertainty.",
]
COMPATIBILITY_DETERMINISM_RULE = (
    "The same pinned input snapshot must produce this exact projection; "
    "missing target semantics remain missing."
)
REFERENCE_KEYS = {
    "claim_refs",
    "uncertainty_refs",
    "layer_refs",
    "participant_refs",
    "basis_claim_refs",
    "target_refs",
    "input_claim_refs",
    "place_refs",
    "region_refs",
    "input_refs",
    "local_context_refs",
    "global_context_refs",
    "derived_observation_refs",
    "active_layer_refs",
    "included_layer_refs",
    "selected_object_refs",
    "reference_refs",
}
SINGLE_REFERENCE_KEYS = {
    "subject_ref",
    "object_ref",
    "place_ref",
    "region_ref",
    "claim_ref",
    "claim_id",
    "source_id",
    "subject_or_claim_ref",
}
CONTEXT_OBJECT_TYPES = {
    "Entity",
    "Event",
    "State",
    "Process",
    "Trajectory",
    "Region",
    "Relation",
    "DerivedObservation",
}
REFERENCE_TYPE_RULES = {
    "claim_refs": {"Claim"},
    "basis_claim_refs": {"Claim"},
    "input_claim_refs": {"Claim"},
    "uncertainty_refs": {"Uncertainty"},
    "layer_refs": {"Layer"},
    "active_layer_refs": {"Layer"},
    "included_layer_refs": {"Layer"},
    "participant_refs": {"Entity"},
    "place_refs": {"Entity"},
    "region_refs": {"Region"},
    "input_refs": CONTEXT_OBJECT_TYPES,
    "local_context_refs": CONTEXT_OBJECT_TYPES,
    "global_context_refs": CONTEXT_OBJECT_TYPES,
    "selected_object_refs": CONTEXT_OBJECT_TYPES,
    "reference_refs": CONTEXT_OBJECT_TYPES,
    "target_refs": CONTEXT_OBJECT_TYPES,
    "derived_observation_refs": {"DerivedObservation"},
}
SINGLE_REFERENCE_TYPE_RULES = {
    "subject_ref": {"Entity"},
    "object_ref": {"Entity"},
    "place_ref": {"Entity"},
    "region_ref": {"Region"},
    "claim_ref": {"Claim"},
    "claim_id": {"Claim"},
    "source_id": {"Source"},
    "subject_or_claim_ref": {"Claim", "Trajectory", "Region", "WorldSlice"},
}


class FixtureValidationError(ValueError):
    """Raised when a fixture violates the executable world-model contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureValidationError(message)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FixtureValidationError(f"missing artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(f"invalid JSON in {path}: {exc}") from exc


def _validate_json_schema(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise FixtureValidationError(f"invalid fixture JSON Schema: {exc.message}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<package>"
        raise FixtureValidationError(f"package.json fails schema.json at {location}: {error.message}")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _normalize_review_scope_bytes(relative_path: str, raw: bytes) -> bytes:
    if relative_path == str(PACKAGE_RELATIVE / "package.json"):
        package = json.loads(raw.decode("utf-8"))
        package.pop("status", None)
        record_time = package.get("record_time")
        if isinstance(record_time, dict):
            record_time = dict(record_time)
            record_time["reviewed_at"] = None
            package["record_time"] = record_time
        return _canonical_json_bytes(package)
    return raw


def _review_scope_bytes(relative_path: str, path: Path) -> bytes:
    return _normalize_review_scope_bytes(relative_path, path.read_bytes())


def compute_review_scope_digest(
    root: Path = REPO_ROOT,
    registry: dict[str, Any] | None = None,
) -> str:
    registry = registry or _read_json(root / PACKAGE_RELATIVE / "review_registry.json")
    _require(
        registry.get("review_scope_id") == REVIEW_SCOPE_ID,
        "review registry must use the canonical immutable review scope",
    )
    _require("review_scope" not in registry, "review registry must not define a mutable review_scope")
    digest = hashlib.sha256()
    for relative_path in REQUIRED_REVIEW_SCOPE:
        path = root / relative_path
        _require(path.is_file(), f"review_scope artifact is missing: {relative_path}")
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_review_scope_bytes(relative_path, path))
        digest.update(b"\0")
    return digest.hexdigest()


def _git_output(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", "-C", str(root), *args),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise FixtureValidationError(f"git verification failed: {detail or args[0]}") from exc
    return result.stdout


def _git_commit_exists(root: Path, commit: str) -> bool:
    try:
        result = subprocess.run(
            ("git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def compute_review_scope_digest_at_commit(root: Path, commit: str) -> str:
    _git_output(root, "cat-file", "-e", f"{commit}^{{commit}}")
    _git_output(root, "merge-base", "--is-ancestor", commit, "HEAD")
    digest = hashlib.sha256()
    for relative_path in REQUIRED_REVIEW_SCOPE:
        raw = _git_output(root, "show", f"{commit}:{relative_path}")
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_normalize_review_scope_bytes(relative_path, raw))
        digest.update(b"\0")
    return digest.hexdigest()


def _parse_temporal_bound(value: object, *, upper: bool) -> date:
    _require(isinstance(value, str), "co-presence temporal bounds must be strings")
    try:
        if re.fullmatch(r"\d{4}", value):
            year = int(value)
            return date(year, 12, 31) if upper else date(year, 1, 1)
        if re.fullmatch(r"\d{4}-\d{2}", value):
            year, month = (int(part) for part in value.split("-"))
            if upper:
                return date(year, month, calendar.monthrange(year, month)[1])
            return date(year, month, 1)
        return date.fromisoformat(value)
    except ValueError as exc:
        raise FixtureValidationError(f"unsupported temporal bound for co-presence: {value}") from exc


def _temporal_overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_start = _parse_temporal_bound(left.get("start"), upper=False)
    left_end = _parse_temporal_bound(left.get("end"), upper=True)
    right_start = _parse_temporal_bound(right.get("start"), upper=False)
    right_end = _parse_temporal_bound(right.get("end"), upper=True)
    return max(left_start, right_start) <= min(left_end, right_end)


def _temporal_contains(container: dict[str, Any], nested: dict[str, Any]) -> bool:
    return (
        _parse_temporal_bound(container.get("start"), upper=False)
        <= _parse_temporal_bound(nested.get("start"), upper=False)
        and _parse_temporal_bound(container.get("end"), upper=True)
        >= _parse_temporal_bound(nested.get("end"), upper=True)
    )


def _object_temporal_extents(item: dict[str, Any]) -> list[dict[str, Any]]:
    direct = item.get("temporal_extent")
    if isinstance(direct, dict):
        return [direct]
    nested: list[dict[str, Any]] = []
    for key in ("segments", "geometry_versions", "stages"):
        values = item.get(key)
        if isinstance(values, list):
            nested.extend(
                value["temporal_extent"]
                for value in values
                if isinstance(value, dict) and isinstance(value.get("temporal_extent"), dict)
            )
    return nested


def _object_spatial_anchor_refs(item: dict[str, Any]) -> set[str]:
    anchors: set[str] = set()
    if item.get("type") == "Region" and isinstance(item.get("id"), str):
        anchors.add(item["id"])
    extents: list[dict[str, Any]] = []
    direct = item.get("spatial_extent")
    if isinstance(direct, dict):
        extents.append(direct)
    for key in ("segments", "geometry_versions", "stages"):
        values = item.get(key)
        if isinstance(values, list):
            extents.extend(
                value["spatial_extent"]
                for value in values
                if isinstance(value, dict) and isinstance(value.get("spatial_extent"), dict)
            )
    for extent in extents:
        for key in ("place_ref", "region_ref"):
            if isinstance(extent.get(key), str):
                anchors.add(extent[key])
        for key in ("place_refs", "region_refs"):
            refs = extent.get(key)
            if isinstance(refs, list):
                anchors.update(ref for ref in refs if isinstance(ref, str))
    return anchors


def _spatial_signature(extent: object) -> tuple[str, str] | None:
    if not isinstance(extent, dict):
        return None
    if extent.get("kind") == "named_place" and isinstance(extent.get("place_ref"), str):
        return ("place", extent["place_ref"])
    if extent.get("kind") == "region_ref" and isinstance(extent.get("region_ref"), str):
        return ("region", extent["region_ref"])
    if extent.get("kind") in {"point", "path", "polygon", "multipolygon"}:
        return ("geometry", json.dumps(extent.get("geometry"), sort_keys=True))
    return None


def _index(items: object, expected_type: str, context: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(items, list) and items, f"{context} must be a non-empty array")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        _require(isinstance(item, dict), f"{context} contains a non-object")
        item_id = item.get("id")
        _require(isinstance(item_id, str) and item_id, f"{context} item is missing id")
        _require(item_id not in indexed, f"{context} contains duplicate id {item_id}")
        _require(item.get("type") == expected_type, f"{item_id} must have type {expected_type}")
        indexed[item_id] = item
    return indexed


def _walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _validate_extent(
    extent: object,
    *,
    context: str,
    dimension: str,
    claim_ids: set[str],
    fixture_mode: str,
) -> None:
    _require(isinstance(extent, dict), f"{context} {dimension} extent must be an object")
    kind = extent.get("kind")
    precision = extent.get("precision")
    basis = extent.get("basis_claim_refs")
    _require(isinstance(kind, str) and kind, f"{context} {dimension} extent needs kind")
    _require(isinstance(precision, str) and precision, f"{context} {dimension} extent needs precision")
    _require(isinstance(basis, list), f"{context} {dimension} extent needs basis_claim_refs")
    _require(len(basis) == len(set(basis)), f"{context} {dimension} extent has duplicate basis Claims")
    for claim_id in basis:
        _require(claim_id in claim_ids, f"{context} {dimension} extent has orphan basis Claim {claim_id}")

    if precision != "unknown":
        _require(basis, f"{context} cannot assert {dimension} precision {precision} without a basis Claim")
    if precision == "fixture_defined":
        _require(
            fixture_mode == "synthetic_contract_fixture",
            f"{context} may use fixture_defined precision only in a synthetic contract fixture",
        )

    if dimension == "temporal":
        _require("certainty" in extent, f"{context} temporal extent needs certainty")
        start = extent.get("start")
        end = extent.get("end")
        if kind == "instant":
            _require(start == end, f"{context} instant must have equal start/end")
        if kind == "closed_interval":
            _require(start is not None and end is not None, f"{context} interval is open")
        if isinstance(start, str) and isinstance(end, str):
            _require(
                _parse_temporal_bound(start, upper=False) <= _parse_temporal_bound(end, upper=True),
                f"{context} temporal extent start must not follow end",
            )
        alternatives = extent.get("alternatives", [])
        _require(isinstance(alternatives, list), f"{context} alternatives must be an array")
        for alternative in alternatives:
            _require(isinstance(alternative, dict), f"{context} temporal alternative must be an object")
            _require(
                all(
                    isinstance(alternative.get(field), str) and alternative[field]
                    for field in ("start", "end", "precision")
                ),
                f"{context} temporal alternative needs start, end and precision",
            )
            _require(
                _parse_temporal_bound(alternative["start"], upper=False)
                <= _parse_temporal_bound(alternative["end"], upper=True),
                f"{context} temporal alternative start must not follow end",
            )
            alt_basis = alternative.get("basis_claim_refs")
            _require(isinstance(alt_basis, list) and alt_basis, f"{context} temporal alternative needs basis Claims")
            for claim_id in alt_basis:
                _require(claim_id in claim_ids, f"{context} temporal alternative has orphan Claim {claim_id}")

    if dimension == "spatial":
        if kind in {"point", "path", "polygon", "multipolygon"}:
            geometry = extent.get("geometry")
            _require(isinstance(geometry, dict), f"{context} {kind} needs geometry")
            _validate_geometry(geometry, kind=kind, context=context)
        elif kind == "named_place":
            _require(isinstance(extent.get("place_ref"), str), f"{context} named_place needs place_ref")
        elif kind == "region_ref":
            _require(isinstance(extent.get("region_ref"), str), f"{context} region_ref needs region_ref")
        elif kind == "multiple_places":
            _require(
                isinstance(extent.get("place_refs"), list) and len(extent["place_refs"]) >= 2,
                f"{context} multiple_places needs at least two place refs",
            )
        elif kind == "multiple_regions":
            _require(
                isinstance(extent.get("region_refs"), list) and len(extent["region_refs"]) >= 2,
                f"{context} multiple_regions needs at least two Region refs",
            )
        elif kind == "composite_scope":
            _require(
                isinstance(extent.get("region_refs"), list) and extent["region_refs"],
                f"{context} composite_scope needs Region refs",
            )
            _require(
                isinstance(extent.get("place_refs"), list) and extent["place_refs"],
                f"{context} composite_scope needs Place refs",
            )
        elif kind == "unknown":
            _require(precision == "unknown", f"{context} unknown space must use unknown precision")
            _require("geometry" not in extent, f"{context} unknown space must not invent geometry")


def _validate_geometry(geometry: dict[str, Any], *, kind: str, context: str) -> None:
    expected_types = {
        "point": "Point",
        "path": "LineString",
        "polygon": "Polygon",
        "multipolygon": "MultiPolygon",
    }
    _require(
        set(geometry) == {"type", "coordinates"},
        f"{context} geometry must contain only GeoJSON type and coordinates",
    )
    _require(
        geometry.get("type") == expected_types[kind],
        f"{context} {kind} must use GeoJSON {expected_types[kind]}",
    )
    coordinates = geometry.get("coordinates")

    def position(value: object) -> bool:
        return (
            isinstance(value, list)
            and 2 <= len(value) <= 3
            and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
            and -180 <= value[0] <= 180
            and -90 <= value[1] <= 90
        )

    def line(value: object) -> bool:
        return isinstance(value, list) and len(value) >= 2 and all(position(item) for item in value)

    def ring(value: object) -> bool:
        return (
            isinstance(value, list)
            and len(value) >= 4
            and all(position(item) for item in value)
            and value[0] == value[-1]
        )

    def polygon(value: object) -> bool:
        return isinstance(value, list) and len(value) >= 1 and all(ring(item) for item in value)

    valid = {
        "point": position,
        "path": line,
        "polygon": polygon,
        "multipolygon": (
            lambda value: isinstance(value, list)
            and len(value) >= 1
            and all(polygon(item) for item in value)
        ),
    }[kind](coordinates)
    _require(valid, f"{context} has invalid GeoJSON {expected_types[kind]} coordinates")


def _validate_claims(
    claims: dict[str, dict[str, Any]],
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    links_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link_id, link in evidence_links.items():
        claim_id = link.get("claim_id")
        source_id = link.get("source_id")
        _require(claim_id in claims, f"{link_id} has orphan Claim {claim_id}")
        _require(source_id in sources, f"{link_id} has orphan Source {source_id}")
        _require(link.get("relation_to_claim") in ALLOWED_EVIDENCE_RELATIONS, f"{link_id} has invalid relation")
        _require(link.get("evidence_strength") in ALLOWED_EVIDENCE_STRENGTH, f"{link_id} has invalid strength")
        _require(link.get("review_state") in ALLOWED_REVIEW_STATES, f"{link_id} has invalid review state")
        locator = link.get("locator")
        _require(isinstance(locator, str) and locator, f"{link_id} needs a locator")
        source_path = package_root / str(sources[source_id].get("uri"))
        _require(source_path.is_file(), f"{link_id} source artifact is missing: {source_path}")
        _require(locator in source_path.read_text(encoding="utf-8"), f"{link_id} locator is not reproducible")
        links_by_claim[claim_id].append(link)

    for claim_id, claim in claims.items():
        _require(
            isinstance(claim.get("statement"), str) and claim["statement"].strip(),
            f"{claim_id} needs an atomic statement",
        )
        _require(claim.get("claim_kind") in ALLOWED_CLAIM_KINDS, f"{claim_id} has invalid claim kind")
        _require(claim.get("origin") in ALLOWED_ORIGINS, f"{claim_id} has invalid origin")
        _require(claim.get("review_state") in ALLOWED_REVIEW_STATES, f"{claim_id} has invalid review state")
        _require(claim.get("confidence") in ALLOWED_CONFIDENCE, f"{claim_id} has invalid confidence")
        state = claim.get("evidence_state")
        _require(state in ALLOWED_EVIDENCE_STATES, f"{claim_id} has invalid evidence state")
        links = links_by_claim.get(claim_id, [])
        reviewed = [link for link in links if link.get("review_state") == "reviewed"]
        relations = {link.get("relation_to_claim") for link in reviewed}
        if {"supports", "challenges"}.issubset(relations):
            derived_state = "mixed"
        elif "supports" in relations:
            derived_state = "supported"
        elif "challenges" in relations:
            derived_state = "challenged"
        elif claim.get("claim_kind") == "observation" and claim.get("origin") == "system":
            derived_state = "not_applicable"
        else:
            derived_state = "missing"
        _require(
            state == derived_state,
            f"{claim_id} evidence_state must be derived as {derived_state}, got {state}",
        )
        if state == "not_applicable":
            _require(not links, f"{claim_id} says not_applicable but has EvidenceLinks")


def _validate_claim_dependency_graph(claims: dict[str, dict[str, Any]]) -> None:
    graph = {
        claim_id: [str(ref) for ref in claim.get("input_claim_refs", [])]
        for claim_id, claim in claims.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(claim_id: str) -> None:
        _require(claim_id not in visiting, f"Claim input dependency cycle includes {claim_id}")
        if claim_id in visited:
            return
        visiting.add(claim_id)
        for input_claim_id in graph[claim_id]:
            visit(input_claim_id)
        visiting.remove(claim_id)
        visited.add(claim_id)

    for claim_id in graph:
        visit(claim_id)


def _validate_claim_ownership(
    indexes: dict[str, dict[str, dict[str, Any]]],
    claims: dict[str, dict[str, Any]],
) -> None:
    for collection in (
        "entities",
        "events",
        "states",
        "processes",
        "trajectories",
        "regions",
        "relations",
    ):
        for owner_id, item in indexes[collection].items():
            for claim_id in item.get("claim_refs", []):
                _require(
                    owner_id in claims[str(claim_id)].get("target_refs", []),
                    f"{owner_id} claim_ref {claim_id} must target its owner",
                )


def _validate_sources(sources: dict[str, dict[str, Any]], package_root: Path) -> None:
    for source_id, source in sources.items():
        _require(source.get("source_type") == "fixture_document", f"{source_id} must be a fixture document")
        _require(source.get("review_state") == "reviewed", f"{source_id} must be reviewed")
        provenance = source.get("provenance")
        _require(isinstance(provenance, dict), f"{source_id} needs provenance")
        _require(
            provenance.get("historical_authority") is False,
            f"{source_id} must not masquerade as historical authority",
        )
        source_path = package_root / str(source.get("uri"))
        _require(source_path.is_file(), f"{source_id} file is missing")
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        _require(source.get("sha256") == digest, f"{source_id} checksum drift")


def _locator_passage(source_path: Path, locator: str) -> str:
    text = source_path.read_text(encoding="utf-8")
    start = text.find(locator)
    _require(start >= 0, f"locator is not reproducible: {locator}")
    passage_start = start + len(locator)
    next_locator = text.find("LOCATOR[", passage_start)
    return text[passage_start:] if next_locator < 0 else text[passage_start:next_locator]


def _supporting_passages(
    claim_id: str,
    *,
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    package_root: Path,
) -> list[str]:
    passages = []
    for link in evidence_links.values():
        if (
            link.get("claim_id") == claim_id
            and link.get("relation_to_claim") == "supports"
            and link.get("review_state") == "reviewed"
        ):
            source = sources[str(link["source_id"])]
            passages.append(
                _locator_passage(package_root / str(source["uri"]), str(link["locator"]))
            )
    return passages


def _geometry_assertion_expression(geometry: object) -> str:
    return (
        "GEOMETRY_ASSERTION["
        + json.dumps(geometry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "]"
    )


def _extent_assertion_expression(
    *,
    owner_ref: str,
    context_ref: str,
    context_kind: str,
    context_mode: str,
    dimension: str,
    extent: dict[str, Any],
) -> str:
    binding = {
        "owner_ref": owner_ref,
        "context_ref": context_ref,
        "context_kind": context_kind,
        "context_mode": context_mode,
        "dimension": dimension,
        "extent": extent,
    }
    digest = hashlib.sha256(_canonical_json_bytes(binding)).hexdigest()
    return (
        f"EXTENT_ASSERTION[owner={owner_ref};context={context_ref};kind={context_kind};"
        f"mode={context_mode};dimension={dimension};sha256={digest}]"
    )


def _extent_contexts(
    package: dict[str, Any],
) -> Iterable[tuple[str, str, str, str, dict[str, Any]]]:
    for event in package.get("events", []):
        yield event["id"], event["id"], "Event", "none", event
    for state in package.get("states", []):
        yield state["id"], state["id"], "State", "none", state
    for process in package.get("processes", []):
        yield (
            process["id"],
            process["id"],
            "Process",
            str(process.get("process_mode", "none")),
            process,
        )
        for stage in process.get("stages", []):
            yield process["id"], stage["id"], "ProcessStage", "none", stage
    for trajectory in package.get("trajectories", []):
        for segment in trajectory.get("segments", []):
            yield (
                trajectory["id"],
                segment["id"],
                "TrajectorySegment",
                str(segment.get("segment_kind", "none")),
                segment,
            )
    for region in package.get("regions", []):
        for version in region.get("geometry_versions", []):
            yield (
                region["id"],
                version["id"],
                "RegionGeometryVersion",
                str(version.get("reconstruction_mode", "none")),
                version,
            )


def _validate_context_bound_extents(
    package: dict[str, Any],
    *,
    claims: dict[str, dict[str, Any]],
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    expected_by_claim: dict[str, set[str]] = defaultdict(set)
    checked = 0
    for owner_ref, context_ref, context_kind, context_mode, context in _extent_contexts(package):
        dimensions: list[tuple[str, dict[str, Any]]] = []
        temporal = context.get("temporal_extent")
        if isinstance(temporal, dict):
            dimensions.append(("temporal", temporal))
            for index, alternative in enumerate(temporal.get("alternatives", [])):
                dimensions.append((f"temporal-alternative-{index}", alternative))
        spatial = context.get("spatial_extent")
        if isinstance(spatial, dict):
            dimensions.append(("spatial", spatial))
        for dimension, extent in dimensions:
            basis = extent.get("basis_claim_refs")
            _require(
                isinstance(basis, list) and basis,
                f"{context_ref} {dimension} needs source- or inference-bound basis Claims",
            )
            expression = _extent_assertion_expression(
                owner_ref=owner_ref,
                context_ref=context_ref,
                context_kind=context_kind,
                context_mode=context_mode,
                dimension=dimension,
                extent=extent,
            )
            for claim_id in basis:
                claim = claims[str(claim_id)]
                expected_by_claim[str(claim_id)].add(expression)
                _require(
                    owner_ref in claim.get("target_refs", []),
                    f"{context_ref} {dimension} basis Claim {claim_id} must target owner {owner_ref}",
                )
                _require(
                    expression in claim.get("extent_assertions", []),
                    f"{context_ref} {dimension} basis Claim {claim_id} lacks exact EXTENT_ASSERTION",
                )
                if (
                    claim.get("origin") == "system"
                    and claim.get("evidence_state") == "not_applicable"
                ):
                    expected_inputs: set[str] | None = None
                    if context_kind == "Process" and context_mode == "analytical_model":
                        expected_inputs = {
                            str(input_claim_id)
                            for stage in context.get("stages", [])
                            for extent_key in ("temporal_extent", "spatial_extent")
                            for input_claim_id in stage.get(extent_key, {}).get(
                                "basis_claim_refs", []
                            )
                        }
                    _require(
                        expected_inputs is not None
                        and set(claim.get("input_claim_refs", [])) == expected_inputs,
                        f"{claim_id} derived extent inputs must exactly match context premises",
                    )
                else:
                    passages = _supporting_passages(
                        str(claim_id),
                        evidence_links=evidence_links,
                        sources=sources,
                        package_root=package_root,
                    )
                    _require(
                        any(expression in passage for passage in passages),
                        f"{context_ref} {dimension} EXTENT_ASSERTION is absent from reviewed locator",
                    )
            checked += 1
    for claim_id, claim in claims.items():
        declared = set(claim.get("extent_assertions", []))
        _require(
            declared == expected_by_claim.get(claim_id, set()),
            f"{claim_id} extent_assertions must exactly match its basis roles",
        )
    _require(checked >= 35, "fixture package must exercise context-bound temporal and spatial extents")


def _validate_source_bound_geometries(
    package: dict[str, Any],
    *,
    claims: dict[str, dict[str, Any]],
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    geometry_extents: list[tuple[str, dict[str, Any]]] = []
    for collection in ("events", "states", "processes", "trajectories", "regions", "relations"):
        for item in package.get(collection, []):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            owner_id = item["id"]
            direct = item.get("spatial_extent")
            if isinstance(direct, dict) and isinstance(direct.get("geometry"), dict):
                geometry_extents.append((owner_id, direct))
            for key in ("segments", "stages", "geometry_versions"):
                for nested in item.get(key, []):
                    extent = nested.get("spatial_extent") if isinstance(nested, dict) else None
                    if isinstance(extent, dict) and isinstance(extent.get("geometry"), dict):
                        geometry_extents.append((owner_id, extent))

    for owner_id, node in geometry_extents:
        geometry = node["geometry"]
        basis = node.get("basis_claim_refs", [])
        expression = _geometry_assertion_expression(geometry)
        supported = False
        for claim_id in basis:
            claim = claims.get(str(claim_id))
            if (
                not isinstance(claim, dict)
                or owner_id not in claim.get("target_refs", [])
                or expression not in str(claim.get("statement", ""))
            ):
                continue
            passages = _supporting_passages(
                str(claim_id),
                evidence_links=evidence_links,
                sources=sources,
                package_root=package_root,
            )
            if any(expression in passage for passage in passages):
                supported = True
                break
        _require(supported, "exact geometry must be stated by a basis Claim and reviewed supporting locator")
    _require(
        len(geometry_extents) >= 6,
        "fixture package must exercise source-bound Event and Region geometries",
    )


def _validate_event_participants(
    events: dict[str, dict[str, Any]],
    *,
    claims: dict[str, dict[str, Any]],
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    entities: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    for event_id, event in events.items():
        for participant_ref in event.get("participant_refs", []):
            _require(
                str(participant_ref) in entities,
                f"{event_id} participant {participant_ref} must resolve to an Entity",
            )
            assertion = (
                f"PARTICIPANT_ASSERTION[event={event_id};participant={participant_ref}]"
            )
            supported = False
            for claim_id in event.get("claim_refs", []):
                claim = claims.get(str(claim_id))
                if not isinstance(claim, dict):
                    continue
                targets = set(claim.get("target_refs", []))
                if (
                    {event_id, participant_ref} <= targets
                    and assertion in str(claim.get("statement", ""))
                ):
                    passages = _supporting_passages(
                        str(claim_id),
                        evidence_links=evidence_links,
                        sources=sources,
                        package_root=package_root,
                    )
                    if any(assertion in passage for passage in passages):
                        supported = True
                        break
            _require(
                supported,
                f"{event_id} participant {participant_ref} must be bound by a reviewed Claim and locator",
            )


def _validate_relation_extent_evidence(
    relation_id: str,
    relation: dict[str, Any],
    claim: dict[str, Any],
    *,
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    entities: dict[str, dict[str, Any]],
    regions: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    supporting_passages = _supporting_passages(
        str(claim.get("id")),
        evidence_links=evidence_links,
        sources=sources,
        package_root=package_root,
    )
    _require(supporting_passages, f"{relation_id} needs source-bound supporting evidence")
    statement = str(claim.get("statement", ""))
    subject = entities.get(str(relation.get("subject_ref")))
    object_ = entities.get(str(relation.get("object_ref")))
    endpoint_refs = {str(relation.get("subject_ref")), str(relation.get("object_ref"))}
    target_refs = set(claim.get("target_refs", []))
    _require(
        {relation_id} | endpoint_refs <= target_refs,
        f"{relation_id} Claim must target the Relation and both endpoints",
    )
    endpoint_labels = {
        str(item.get("label"))
        for item in (subject, object_)
        if isinstance(item, dict) and isinstance(item.get("label"), str)
    }
    _require(
        len(endpoint_labels) == 2
        and all(label in statement for label in endpoint_labels)
        and any(all(label in passage for label in endpoint_labels) for passage in supporting_passages),
        f"{relation_id} endpoints are not stated by its Claim and supporting locator",
    )
    directionality = relation.get("directionality")
    _require(
        directionality in ALLOWED_RELATION_DIRECTIONALITY,
        f"{relation_id} has invalid directionality",
    )
    if relation.get("predicate") in DIRECTED_RELATION_PREDICATES:
        _require(directionality == "directed", f"{relation_id} predicate requires directed directionality")
    if directionality == "directed":
        subject_label = str(subject.get("label")) if isinstance(subject, dict) else ""
        object_label = str(object_.get("label")) if isinstance(object_, dict) else ""

        def states_ordered_roles(text: str) -> bool:
            subject_position = text.find(subject_label)
            object_position = text.find(object_label)
            return subject_position >= 0 and object_position > subject_position

        _require(
            states_ordered_roles(statement)
            and any(states_ordered_roles(passage) for passage in supporting_passages),
            f"{relation_id} directed endpoint roles are not stated subject-to-object",
        )

    temporal = relation.get("temporal_extent", {})
    start = temporal.get("start")
    end = temporal.get("end")
    temporal_expression = (
        f"on {start}"
        if temporal.get("kind") == "instant"
        else f"during {start}–{end}"
        if isinstance(start, str) and isinstance(end, str)
        else ""
    )
    statement_lower = statement.lower()
    _require(
        temporal_expression
        and temporal_expression.lower() in statement_lower
        and any(temporal_expression.lower() in passage.lower() for passage in supporting_passages),
        f"{relation_id} temporal extent is not stated by its Claim and supporting locator",
    )

    spatial = relation.get("spatial_extent", {})
    spatial_expressions: set[str] = set()
    for key, registry in (("place_ref", entities), ("region_ref", regions)):
        ref = spatial.get(key)
        item = registry.get(str(ref)) if isinstance(ref, str) else None
        if isinstance(item, dict) and isinstance(item.get("label"), str):
            spatial_expressions.add(item["label"])
    for key, registry in (("place_refs", entities), ("region_refs", regions)):
        for ref in spatial.get(key, []):
            item = registry.get(str(ref))
            if isinstance(item, dict) and isinstance(item.get("label"), str):
                spatial_expressions.add(item["label"])
    geometry = spatial.get("geometry")
    if isinstance(geometry, dict):
        spatial_expressions.add(
            json.dumps(geometry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        )
    if spatial.get("kind") == "unknown":
        spatial_expressions.add("unknown")
    _require(
        spatial_expressions
        and all(expression in statement for expression in spatial_expressions)
        and any(
            all(expression in passage for expression in spatial_expressions)
            for passage in supporting_passages
        ),
        f"{relation_id} spatial extent is not stated by its Claim and supporting locator",
    )
    expected_binding = {
        "relation_ref": relation_id,
        "subject_ref": relation.get("subject_ref"),
        "predicate": relation.get("predicate"),
        "object_ref": relation.get("object_ref"),
        "directionality": relation.get("directionality"),
        "temporal_extent": relation.get("temporal_extent"),
        "spatial_extent": relation.get("spatial_extent"),
        "mechanism": relation.get("mechanism"),
        "scope": relation.get("scope"),
    }
    _require(
        claim.get("relation_binding") == expected_binding,
        f"{relation_id} Claim relation_binding must exactly match Relation semantics",
    )
    binding_expression = (
        "RELATION_ASSERTION["
        + json.dumps(
            expected_binding,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "]"
    )
    _require(
        any(binding_expression in passage for passage in supporting_passages),
        f"{relation_id} supporting locator must state the exact relation_binding",
    )


def _validate_references(
    package: dict[str, Any],
    type_registry: dict[str, str | None],
    entity_kinds: dict[str, str],
) -> None:
    for item in _walk(package):
        item_id = item.get("id", package.get("package_id", "package"))
        for key in REFERENCE_KEYS:
            if key not in item:
                continue
            refs = item[key]
            _require(isinstance(refs, list), f"{item_id}.{key} must be an array")
            _require(len(refs) == len(set(refs)), f"{item_id}.{key} contains duplicates")
            for ref in refs:
                _require(ref in type_registry, f"{item_id}.{key} has orphan reference {ref}")
                allowed_types = REFERENCE_TYPE_RULES[key]
                _require(
                    type_registry[ref] in allowed_types,
                    f"{item_id}.{key} must reference {sorted(allowed_types)}, got {type_registry[ref]} for {ref}",
                )
                if key == "place_refs":
                    _require(entity_kinds.get(ref) == "Place", f"{item_id}.{key} must reference Place {ref}")
        for key in SINGLE_REFERENCE_KEYS:
            if key in item:
                ref = item[key]
                _require(
                    isinstance(ref, str) and ref in type_registry,
                    f"{item_id}.{key} has orphan reference {ref}",
                )
                allowed_types = SINGLE_REFERENCE_TYPE_RULES[key]
                _require(
                    type_registry[ref] in allowed_types,
                    f"{item_id}.{key} must reference {sorted(allowed_types)}, got {type_registry[ref]} for {ref}",
                )
                if key == "place_ref":
                    _require(entity_kinds.get(ref) == "Place", f"{item_id}.{key} must reference Place {ref}")


def _validate_compatibility(root: Path, *, require_ready: bool) -> None:
    path = root / PACKAGE_RELATIVE / "compatibility" / "architecture_atlas_projection.json"
    projection = _read_json(path)
    _require(
        set(projection)
        == {
            "schema_version",
            "projection_id",
            "source_dataset",
            "input_snapshot",
            "target_projection",
            "losses_and_unknowns",
            "determinism_rule",
        },
        "compatibility projection envelope must be closed",
    )
    _require(projection.get("schema_version") == SCHEMA_VERSION, "compatibility projection version drift")
    _require(
        projection.get("projection_id") == "architecture-atlas-villa-savoye-to-world-model-v1",
        "compatibility projection identity drift",
    )
    source_dataset = projection.get("source_dataset")
    _require(isinstance(source_dataset, dict), "compatibility projection needs source_dataset")
    _require(
        set(source_dataset) == COMPATIBILITY_SOURCE_DATASET_FIELDS,
        "compatibility source_dataset envelope must be closed",
    )
    _require(
        source_dataset.get("repository") == "omegapunctum/ARTEMIS"
        and source_dataset.get("path") == "data/features.json",
        "compatibility source provenance drift",
    )
    _require(
        source_dataset.get("record_id") == "rec1GDGqssFGehzEx"
        and source_dataset.get("canonical_feature_id")
        == "1f49bb51-07a2-4c86-8101-edb6e525503e",
        "compatibility Villa Savoye source identity drift",
    )
    commit = source_dataset.get("commit")
    _require(
        isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
        "compatibility projection must pin a commit",
    )
    _require(
        isinstance(source_dataset.get("source_file_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", source_dataset["source_file_sha256"]) is not None,
        "compatibility projection must pin the source file checksum",
    )
    target = projection.get("target_projection")
    _require(isinstance(target, dict), "compatibility projection needs target_projection")
    _require(target.get("invented_fields") == [], "compatibility projection invented target fields")
    entity = target.get("entity")
    _require(isinstance(entity, dict), "compatibility projection needs target Entity")
    spatial = entity.get("spatial_extent")
    _require(
        isinstance(spatial, dict) and spatial.get("precision") == "unknown",
        "legacy coordinate confidence must not become target precision without evidence",
    )
    claims = target.get("claims")
    _require(isinstance(claims, list) and claims, "compatibility projection needs imported Claims")
    layers = target.get("layers")
    uncertainties = target.get("uncertainties")
    _require(isinstance(layers, list) and layers, "compatibility projection needs explicit target Layers")
    _require(
        isinstance(uncertainties, list) and uncertainties,
        "compatibility projection needs explicit target Uncertainties",
    )
    target_items = [entity, *claims, *layers, *uncertainties]
    target_registry = {
        item.get("id"): item
        for item in target_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    _require(len(target_registry) == len(target_items), "compatibility projection has duplicate or missing target ids")
    target_types = {item_id: str(item.get("type")) for item_id, item in target_registry.items()}
    for claim in claims:
        _require(claim.get("origin") == "imported", "compatibility Claim must preserve imported origin")
        _require(claim.get("evidence_state") == "missing", "compatibility Claim must expose missing evidence")
        _require(claim.get("evidence_link_refs") == [], "compatibility projection must not invent EvidenceLinks")
        _require(claim.get("target_refs") == [entity.get("id")], "compatibility Claim target must resolve to Entity")
    for key in ("claim_refs", "uncertainty_refs", "layer_refs"):
        refs = entity.get(key)
        _require(isinstance(refs, list), f"compatibility Entity needs {key}")
        for ref in refs:
            _require(ref in target_registry, f"compatibility Entity has dangling {key} reference {ref}")
    for claim in claims:
        for ref in claim.get("uncertainty_refs", []):
            _require(ref in target_registry, f"compatibility Claim has dangling uncertainty reference {ref}")
    for uncertainty in uncertainties:
        _require(
            uncertainty.get("subject_or_claim_ref") in target_registry,
            "compatibility Uncertainty has dangling subject_or_claim_ref",
        )
    for item in target_items:
        item_id = str(item.get("id"))
        for node in _walk(item):
            for key, value in node.items():
                if key in REFERENCE_KEYS:
                    _require(isinstance(value, list), f"compatibility {item_id}.{key} must be an array")
                    for ref in value:
                        _require(
                            isinstance(ref, str) and ref in target_registry,
                            f"compatibility {item_id}.{key} has dangling reference {ref}",
                        )
                        allowed = REFERENCE_TYPE_RULES.get(key)
                        if allowed is not None:
                            _require(
                                target_types[ref] in allowed,
                                f"compatibility {item_id}.{key} has invalid target type for {ref}",
                            )
                elif key in SINGLE_REFERENCE_KEYS:
                    _require(
                        isinstance(value, str) and value in target_registry,
                        f"compatibility {item_id}.{key} has dangling reference {value}",
                    )
    losses = projection.get("losses_and_unknowns")
    _require(
        losses == COMPATIBILITY_LOSSES,
        "compatibility projection must preserve the exact material losses",
    )
    _require(
        projection.get("determinism_rule") == COMPATIBILITY_DETERMINISM_RULE,
        "compatibility determinism rule drift",
    )

    canonical_path = root / str(source_dataset.get("path"))
    _require(canonical_path.is_file(), "pinned Architecture Atlas source file is missing")
    source_bytes = canonical_path.read_bytes()
    pinned_source_available = _git_commit_exists(root, str(commit))
    if pinned_source_available:
        source_bytes = _git_output(root, "show", f"{commit}:{source_dataset.get('path')}")
    elif require_ready:
        _git_output(root, "cat-file", "-e", f"{commit}^{{commit}}")
    if pinned_source_available:
        source_file_digest = hashlib.sha256(source_bytes).hexdigest()
        _require(
            source_dataset.get("source_file_sha256") == source_file_digest,
            "pinned Architecture Atlas source commit/file checksum drift",
        )
    try:
        records = json.loads(source_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureValidationError("pinned Architecture Atlas source file is invalid JSON") from exc
    record = next(
        (
            item
            for item in records
            if isinstance(item, dict) and item.get("id") == source_dataset.get("record_id")
        ),
        None,
    )
    _require(record is not None, "pinned Architecture Atlas compatibility record is absent")
    record_digest = hashlib.sha256(_canonical_json_bytes(record)).hexdigest()
    _require(
        source_dataset.get("record_sha256") == record_digest,
        "pinned Architecture Atlas compatibility record checksum drift",
    )
    fields = record.get("fields")
    snapshot = projection.get("input_snapshot")
    _require(isinstance(fields, dict) and isinstance(snapshot, dict), "compatibility input is malformed")
    _require(
        all(key in fields for key in COMPATIBILITY_SNAPSHOT_FIELDS),
        "pinned Architecture Atlas record is missing a required compatibility field",
    )
    expected_snapshot = {key: fields[key] for key in COMPATIBILITY_SNAPSHOT_FIELDS}
    _require(
        snapshot == expected_snapshot,
        "compatibility input_snapshot must exactly mirror the pinned record fields",
    )
    _require(
        fields.get("id") == source_dataset.get("canonical_feature_id") == entity.get("id"),
        "compatibility canonical Entity identity drift",
    )
    canonical_entity_id = str(source_dataset.get("canonical_feature_id"))
    expected_claims = {
        "compat-claim-villa-savoye-date": (
            f"The legacy record gives the interval {fields['date_start']}–{fields['date_end']}."
        ),
        "compat-claim-villa-savoye-location": (
            f"The legacy record gives the point [{fields['longitude']}, {fields['latitude']}]."
        ),
    }
    expected_target = {
        "entity": {
            "id": canonical_entity_id,
            "type": "Entity",
            "entity_kind": "Object",
            "label": fields["name_en"],
            "temporal_extent": {
                "kind": "closed_interval",
                "start": fields["date_start"],
                "end": fields["date_end"],
                "precision": "year",
                "certainty": "legacy_unverified",
                "basis_claim_refs": ["compat-claim-villa-savoye-date"],
            },
            "spatial_extent": {
                "kind": "point",
                "geometry": {
                    "type": "Point",
                    "coordinates": [fields["longitude"], fields["latitude"]],
                },
                "precision": "unknown",
                "legacy_precision_value": fields["coordinates_confidence"],
                "basis_claim_refs": ["compat-claim-villa-savoye-location"],
            },
            "claim_refs": list(expected_claims),
            "uncertainty_refs": ["compat-uncertainty-villa-savoye-provenance"],
            "layer_refs": ["compat-layer-architecture"],
        },
        "claims": [
            {
                "id": claim_id,
                "type": "Claim",
                "statement": statement,
                "target_refs": [canonical_entity_id],
                "claim_kind": "factual",
                "origin": "imported",
                "review_state": "draft",
                "confidence": "unknown",
                "evidence_state": "missing",
                "evidence_link_refs": [],
                "uncertainty_refs": ["compat-uncertainty-villa-savoye-provenance"],
            }
            for claim_id, statement in expected_claims.items()
        ],
        "layers": [
            {
                "id": "compat-layer-architecture",
                "type": "Layer",
                "label": "Architecture Atlas compatibility layer",
            }
        ],
        "uncertainties": [
            {
                "id": "compat-uncertainty-villa-savoye-provenance",
                "type": "Uncertainty",
                "subject_or_claim_ref": canonical_entity_id,
                "dimension": "missing_evidence",
                "description": "The legacy record has source-like fields but no claim-level locator.",
                "effect": "Target Claims remain draft with missing evidence and unknown spatial precision.",
            }
        ],
        "invented_fields": [],
    }
    _require(
        target == expected_target,
        "compatibility target projection drifted from the deterministic pinned mapping",
    )
    _require(
        {str(claim.get("id")) for claim in claims} == set(expected_claims),
        "compatibility projection invented or omitted a mapped Claim",
    )
    _require(
        set(target) == {"entity", "claims", "layers", "uncertainties", "invented_fields"},
        "compatibility target projection contains an unmapped field",
    )
    _require(
        set(entity)
        == {
            "id",
            "type",
            "entity_kind",
            "label",
            "temporal_extent",
            "spatial_extent",
            "claim_refs",
            "uncertainty_refs",
            "layer_refs",
        },
        "compatibility Entity contains an unmapped field",
    )
    _require(
        entity.get("label") == snapshot.get("name_en")
        and entity.get("temporal_extent", {}).get("start") == snapshot.get("date_start")
        and entity.get("temporal_extent", {}).get("end") == snapshot.get("date_end")
        and entity.get("spatial_extent", {}).get("geometry", {}).get("coordinates")
        == [snapshot.get("longitude"), snapshot.get("latitude")]
        and entity.get("spatial_extent", {}).get("legacy_precision_value")
        == snapshot.get("coordinates_confidence"),
        "compatibility Entity drifted from deterministic source mapping",
    )
    for claim in claims:
        claim_id = str(claim["id"])
        _require(
            set(claim)
            == {
                "id",
                "type",
                "statement",
                "target_refs",
                "claim_kind",
                "origin",
                "review_state",
                "confidence",
                "evidence_state",
                "evidence_link_refs",
                "uncertainty_refs",
            },
            f"compatibility Claim {claim_id} contains an unmapped field",
        )
        _require(
            claim.get("statement") == expected_claims[claim_id]
            and claim.get("target_refs") == [canonical_entity_id],
            f"compatibility Claim {claim_id} drifted from deterministic source mapping",
        )
    _require(
        entity.get("claim_refs") == list(expected_claims),
        "compatibility Entity Claim mapping drift",
    )
    _require(
        [layer.get("id") for layer in layers] == ["compat-layer-architecture"]
        and snapshot.get("layer_type") == "architecture",
        "compatibility Layer mapping drift",
    )
    _require(
        set(layers[0]) == {"id", "type", "label"}
        and layers[0].get("label") == "Architecture Atlas compatibility layer",
        "compatibility Layer contains an unmapped field",
    )
    _require(
        [uncertainty.get("id") for uncertainty in uncertainties]
        == ["compat-uncertainty-villa-savoye-provenance"],
        "compatibility Uncertainty mapping drift",
    )
    _require(
        set(uncertainties[0])
        == {"id", "type", "subject_or_claim_ref", "dimension", "description", "effect"},
        "compatibility Uncertainty contains an unmapped field",
    )


def _validate_coverage(
    package: dict[str, Any],
    indexes: dict[str, dict[str, dict[str, Any]]],
    registry: set[str],
    root: Path,
) -> None:
    manifest = _read_json(root / PACKAGE_RELATIVE / "coverage_manifest.json")
    _require(manifest.get("schema_version") == SCHEMA_VERSION, "coverage manifest version drift")
    _require(manifest.get("package_id") == package.get("package_id"), "coverage package id drift")
    counts = Counter()
    for collection, expected_type in COLLECTION_TYPES.items():
        if collection == "derived_observations":
            continue
        counts[expected_type] = len(indexes[collection])
    required = manifest.get("required_object_kinds")
    _require(isinstance(required, dict), "coverage manifest needs required_object_kinds")
    _require(dict(counts) == required, f"coverage counts drift: expected {required}, got {dict(counts)}")

    scenarios = manifest.get("required_scenarios")
    _require(isinstance(scenarios, dict), "coverage manifest needs scenarios")
    for scenario, ref in scenarios.items():
        if scenario == "compatibility_projection":
            _require(
                (root / PACKAGE_RELATIVE / str(ref)).is_file(),
                "coverage manifest compatibility projection is missing",
            )
        else:
            _require(ref in registry, f"coverage scenario {scenario} has orphan reference {ref}")

    exclusions = manifest.get("known_exclusions")
    _require(isinstance(exclusions, list) and exclusions, "coverage manifest needs known exclusions")
    for exclusion in exclusions:
        _require(
            isinstance(exclusion, dict) and exclusion.get("assertion_kind") == "corpus_exclusion",
            "fixture absence must be represented only as corpus exclusion",
        )
    spatial_summary = manifest.get("spatial_bounds")
    _require(
        isinstance(spatial_summary, str)
        and all(label in spatial_summary for label in ("Fixture Basin", "South Coast", "Far Observatory")),
        "coverage manifest must name every WorldSlice spatial scope component",
    )


def _parse_review_artifact(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        if key not in REVIEW_ARTIFACT_FIELDS:
            continue
        _require(key not in parsed, f"fixture review artifact duplicates {key}")
        parsed[key] = value.strip()
    missing = set(REVIEW_ARTIFACT_FIELDS) - set(parsed)
    _require(not missing, f"fixture review artifact is missing fields: {sorted(missing)}")
    return parsed


def _artifact_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _validate_reviews(root: Path, package: dict[str, Any], *, require_ready: bool) -> None:
    registry = _read_json(root / PACKAGE_RELATIVE / "review_registry.json")
    _require(registry.get("schema_version") == SCHEMA_VERSION, "review registry version drift")
    _require(registry.get("package_id") == package.get("package_id"), "review registry package drift")
    _require(registry.get("required_review_count") == 2, "fixture package requires two reviews")
    _require(
        registry.get("review_scope_id") == REVIEW_SCOPE_ID and "review_scope" not in registry,
        "fixture reviews must use the canonical immutable review scope",
    )
    computed_content_digest = compute_review_scope_digest(root, registry)
    reviews = registry.get("reviews")
    _require(isinstance(reviews, list), "review registry reviews must be an array")
    reviewer_ids: list[str] = []
    reviewer_instance_ids: list[str] = []
    review_ids: list[str] = []
    review_tracks: list[str] = []
    artifact_paths: list[str] = []
    for review in reviews:
        _require(isinstance(review, dict), "fixture review must be an object")
        for field in (
            "review_id",
            "reviewer_id",
            "reviewer_instance_id",
            "review_track",
            "independence_method",
            "artifact",
            "artifact_sha256",
            "frozen_commit",
            "reviewed_content_sha256",
            "decision",
            "critical_findings",
            "unresolved_material_findings",
            "independence_attestation",
        ):
            _require(field in review, f"fixture review is missing {field}")
        for field in ("review_id", "reviewer_id", "reviewer_instance_id"):
            value = review[field]
            _require(
                isinstance(value, str)
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{2,}", value) is not None,
                f"fixture review {field} must be a non-empty stable identifier",
            )
        for field in ("critical_findings", "unresolved_material_findings"):
            value = review[field]
            _require(
                type(value) is int and value >= 0,
                f"fixture review {field} must be a non-negative integer",
            )
        _require(
            review["review_track"] in {"semantic-model", "validator-integrity"},
            "fixture review has invalid review_track",
        )
        _require(
            review["decision"] in {"READY", "CHANGES_REQUIRED"},
            "fixture review has invalid decision",
        )
        _require(
            type(review["independence_attestation"]) is bool,
            "fixture review independence_attestation must be boolean",
        )
        _require(
            review["independence_method"] == "separate_agent_task",
            "fixture review needs separate_agent_task independence_method",
        )
        _require(
            isinstance(review["artifact_sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", review["artifact_sha256"]) is not None,
            "fixture review artifact_sha256 must be a SHA-256 digest",
        )
        _require(
            isinstance(review["frozen_commit"], str)
            and re.fullmatch(r"[0-9a-f]{40}", review["frozen_commit"]) is not None,
            "fixture review frozen_commit must be a full Git SHA",
        )
        _require(
            isinstance(review["reviewed_content_sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", review["reviewed_content_sha256"]) is not None,
            "fixture review reviewed_content_sha256 must be a SHA-256 digest",
        )
        reviewer_ids.append(str(review["reviewer_id"]))
        reviewer_instance_ids.append(str(review["reviewer_instance_id"]))
        review_ids.append(str(review["review_id"]))
        review_tracks.append(str(review["review_track"]))
        artifact_path = str(review["artifact"])
        artifact_paths.append(artifact_path)
        candidate = Path(artifact_path)
        _require(
            not candidate.is_absolute() and ".." not in candidate.parts and candidate.suffix == ".md",
            "fixture review artifact path must be a safe Markdown path",
        )
        artifact = root / candidate
        _require(artifact.is_file(), f"fixture review artifact is missing: {artifact}")
        artifact_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        _require(review.get("artifact_sha256") == artifact_digest, "fixture review artifact checksum drift")
        artifact_fields = _parse_review_artifact(artifact)
        expected_artifact_fields = {
            "artifact_format": "artemis-review-attestation-v1",
            **{
                field: _artifact_value(review.get(field))
                for field in REVIEW_ARTIFACT_FIELDS
                if field != "artifact_format"
            },
        }
        _require(
            artifact_fields == expected_artifact_fields,
            "fixture review artifact/registry drift",
        )
    for values, message in (
        (review_ids, "review ids"),
        (reviewer_ids, "reviewer identities"),
        (reviewer_instance_ids, "reviewer invocation identities"),
        (review_tracks, "review tracks"),
        (artifact_paths, "review artifacts"),
    ):
        _require(len(values) == len(set(values)), f"fixture {message} must be distinct")
    ready_records = (
        len(reviews) == registry["required_review_count"]
        and set(review_tracks) == {"semantic-model", "validator-integrity"}
        and all(
            review.get("decision") == "READY"
            and review.get("critical_findings") == 0
            and review.get("unresolved_material_findings") == 0
            and review.get("independence_attestation") is True
            and review.get("independence_method") == "separate_agent_task"
            for review in reviews
        )
    )
    expected_status = "READY" if ready_records else "REVIEW_REQUIRED"
    _require(registry.get("status") == expected_status, "review registry status drift")
    _require(package.get("status") == expected_status, "fixture package status drift")
    if expected_status == "READY":
        frozen = registry.get("frozen_commit")
        _require(
            isinstance(frozen, str) and re.fullmatch(r"[0-9a-f]{40}", frozen) is not None,
            "READY reviews need one frozen commit",
        )
        _require(
            registry.get("reviewed_content_sha256") == computed_content_digest,
            "READY review registry does not match current reviewed content",
        )
        frozen_content_digest = compute_review_scope_digest_at_commit(root, frozen)
        _require(
            frozen_content_digest == computed_content_digest,
            "frozen commit does not contain the reviewed semantic content",
        )
        _require(
            isinstance(package.get("record_time", {}).get("reviewed_at"), str)
            and package["record_time"]["reviewed_at"],
            "READY package needs record_time.reviewed_at",
        )
        for review in reviews:
            _require(review.get("frozen_commit") == frozen, "reviews must inspect the same frozen commit")
            _require(
                review.get("reviewed_content_sha256") == computed_content_digest,
                "review does not bind the current semantic content",
            )
    if require_ready:
        _require(expected_status == "READY", "two independent READY reviews are required")


def validate_package(root: Path = REPO_ROOT, *, require_ready: bool = False) -> dict[str, int]:
    package_root = root / PACKAGE_RELATIVE
    schema = _read_json(package_root / "schema.json")
    package = _read_json(package_root / "package.json")
    _require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema draft drift")
    _require(schema.get("$id", "").endswith(f"/{SCHEMA_VERSION}"), "schema id/version drift")
    _validate_json_schema(package, schema)
    _require(package.get("schema_version") == SCHEMA_VERSION, "package schema version drift")
    _require(package.get("fixture_mode") == "synthetic_contract_fixture", "v1 package must be synthetic")
    _require(package.get("world_slice", {}).get("type") == "WorldSlice", "package needs WorldSlice")

    indexes = {
        collection: _index(package.get(collection), expected_type, collection)
        for collection, expected_type in COLLECTION_TYPES.items()
    }
    claims = indexes["claims"]
    claim_ids = set(claims)
    fixture_mode = str(package.get("fixture_mode"))
    world_slice = package["world_slice"]
    _validate_extent(
        world_slice.get("temporal_bounds"),
        context=str(world_slice.get("id")),
        dimension="temporal",
        claim_ids=claim_ids,
        fixture_mode=fixture_mode,
    )
    _validate_extent(
        world_slice.get("spatial_bounds"),
        context=str(world_slice.get("id")),
        dimension="spatial",
        claim_ids=claim_ids,
        fixture_mode=fixture_mode,
    )

    type_registry: dict[str, str | None] = {}
    for item in _walk(package):
        item_id = item.get("id")
        if isinstance(item_id, str):
            _require(item_id not in type_registry, f"package contains duplicate global id {item_id}")
            item_type = item.get("type")
            type_registry[item_id] = item_type if isinstance(item_type, str) else None
    registry = set(type_registry) | {str(package["package_id"])}
    entity_kinds = {
        entity_id: str(entity.get("entity_kind"))
        for entity_id, entity in indexes["entities"].items()
    }

    _validate_sources(indexes["sources"], package_root)
    _validate_claims(claims, indexes["evidence_links"], indexes["sources"], package_root)
    _validate_references(package, type_registry, entity_kinds)
    _validate_claim_dependency_graph(claims)
    _validate_claim_ownership(indexes, claims)

    for collection in ("events", "states", "processes", "relations"):
        for item_id, item in indexes[collection].items():
            _validate_extent(
                item.get("temporal_extent"),
                context=item_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                item.get("spatial_extent"),
                context=item_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )

    for event_id, event in indexes["events"].items():
        temporal_extent = event.get("temporal_extent", {})
        primary_basis = set(temporal_extent.get("basis_claim_refs", []))
        alternative_claim_ids: set[str] = set()
        for alternative in temporal_extent.get("alternatives", []):
            alternative_basis = set(alternative.get("basis_claim_refs", []))
            alternative_claim_ids.update(alternative_basis)
            _require(
                alternative_basis.isdisjoint(primary_basis),
                f"{event_id} alternative date needs a distinct supporting Claim",
            )
            for claim_id in alternative_basis:
                claim = claims[claim_id]
                _require(
                    event_id in claim.get("target_refs", [])
                    and claim.get("evidence_state") in {"supported", "mixed"},
                    f"{event_id} alternative Claim {claim_id} must target the Event and have reviewed evidence",
                )
        if alternative_claim_ids:
            uncertainty_records = [
                indexes["uncertainties"][uncertainty_id]
                for uncertainty_id in event.get("uncertainty_refs", [])
                if indexes["uncertainties"][uncertainty_id].get("dimension") == "temporal_value"
            ]
            _require(uncertainty_records, f"{event_id} alternative date needs temporal uncertainty")
            _require(
                any(
                    primary_basis | alternative_claim_ids
                    <= set(uncertainty.get("basis_claim_refs", []))
                    for uncertainty in uncertainty_records
                ),
                f"{event_id} temporal uncertainty must bind every alternative-date Claim",
            )
    _validate_event_participants(
        indexes["events"],
        claims=claims,
        evidence_links=indexes["evidence_links"],
        sources=indexes["sources"],
        entities=indexes["entities"],
        package_root=package_root,
    )

    for process_id, process in indexes["processes"].items():
        _require(
            process.get("process_mode") in ALLOWED_RECONSTRUCTION_MODES,
            f"{process_id} needs an explicit process_mode",
        )
        stages = process.get("stages")
        _require(isinstance(stages, list) and len(stages) >= 2, f"{process_id} needs at least two stages")
        region_refs: set[str] = set()
        process_temporal = process.get("temporal_extent", {})
        previous_end: date | None = None
        for stage in stages:
            stage_id = str(stage.get("id"))
            _validate_extent(
                stage.get("temporal_extent"),
                context=stage_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                stage.get("spatial_extent"),
                context=stage_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            stage_spatial = stage.get("spatial_extent", {})
            stage_temporal = stage.get("temporal_extent", {})
            _require(
                stage_spatial.get("kind") == "region_ref",
                f"{process_id} contract fixture stages must reference Regions",
            )
            region_ref = str(stage_spatial.get("region_ref"))
            region_refs.add(region_ref)
            _require(
                _temporal_contains(process_temporal, stage_temporal),
                f"{stage_id} temporal extent must remain within {process_id}",
            )
            stage_start = _parse_temporal_bound(stage_temporal.get("start"), upper=False)
            stage_end = _parse_temporal_bound(stage_temporal.get("end"), upper=True)
            _require(
                previous_end is None or stage_start > previous_end,
                f"{process_id} stages must be temporally ordered and non-overlapping",
            )
            previous_end = stage_end
            stage_claim_refs = set(stage.get("claim_refs", []))
            extent_basis = set(stage_temporal.get("basis_claim_refs", [])) | set(
                stage_spatial.get("basis_claim_refs", [])
            )
            _require(
                stage_claim_refs == extent_basis,
                f"{stage_id} Claim refs must exactly bind its temporal and spatial premises",
            )
            for claim_id in stage_claim_refs:
                _require(
                    region_ref in claims[claim_id].get("target_refs", []),
                    f"{stage_id} Claim {claim_id} must target its Region",
                )
        _require(len(region_refs) >= 2, f"{process_id} must span more than one Region")
        process_spatial = process.get("spatial_extent", {})
        _require(
            process_spatial.get("kind") == "multiple_regions"
            and set(process_spatial.get("region_refs", [])) == region_refs,
            f"{process_id} multiple_regions extent must match its stage Regions",
        )
        if process.get("process_mode") == "analytical_model":
            stage_marker_claims = {
                claim_id
                for stage in stages
                for claim_id in stage["temporal_extent"]["basis_claim_refs"]
            }
            direct_basis = set(process.get("temporal_extent", {}).get("basis_claim_refs", [])) | set(
                process.get("spatial_extent", {}).get("basis_claim_refs", [])
            )
            _require(
                len(direct_basis) == 1,
                f"{process_id} direct extents need one system derivation Claim",
            )
            derived_claim_id = next(iter(direct_basis))
            derived_claim = claims[derived_claim_id]
            _require(
                derived_claim_id in process.get("claim_refs", [])
                and derived_claim.get("claim_kind") == "observation"
                and derived_claim.get("origin") == "system"
                and derived_claim.get("evidence_state") == "not_applicable"
                and set(derived_claim.get("input_claim_refs", [])) == stage_marker_claims,
                f"{process_id} direct extent basis must be the system observation bound to every stage",
            )

    for trajectory_id, trajectory in indexes["trajectories"].items():
        segments = trajectory.get("segments")
        _require(isinstance(segments, list) and len(segments) >= 2, f"{trajectory_id} needs segments")
        inferred = []
        for segment in segments:
            segment_id = str(segment.get("id"))
            _require(
                segment.get("segment_kind") in {"presence", "movement", "inferred_gap"},
                f"{segment_id} has invalid segment kind",
            )
            _validate_extent(
                segment.get("temporal_extent"),
                context=segment_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                segment.get("spatial_extent"),
                context=segment_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            if segment.get("segment_kind") == "inferred_gap":
                inferred.append(segment)
                _require(segment.get("uncertainty_refs"), f"{segment_id} inferred gap needs uncertainty")
                _require(
                    segment.get("spatial_extent", {}).get("kind") == "unknown",
                    f"{segment_id} must not invent a route geometry",
                )
        _require(inferred, f"{trajectory_id} must exercise an inferred gap")

    changing_regions: list[str] = []
    alternative_regions: list[str] = []
    for region_id, region in indexes["regions"].items():
        versions = region.get("geometry_versions")
        _require(isinstance(versions, list) and versions, f"{region_id} needs geometry versions")
        geometries: set[str] = set()
        alternatives = []
        for version in versions:
            version_id = str(version.get("id"))
            _require(
                version.get("reconstruction_mode") in ALLOWED_RECONSTRUCTION_MODES,
                f"{version_id} has invalid reconstruction mode",
            )
            _validate_extent(
                version.get("temporal_extent"),
                context=version_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                version.get("spatial_extent"),
                context=version_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            geometries.add(json.dumps(version.get("spatial_extent", {}).get("geometry"), sort_keys=True))
            if version.get("reconstruction_mode") == "alternative_reconstruction":
                alternatives.append(version)
                _require(version.get("uncertainty_refs"), f"{version_id} alternative needs uncertainty")
        if len(geometries) >= 2:
            changing_regions.append(region_id)
        if alternatives:
            alternative_regions.append(region_id)
    _require(changing_regions, "fixture package needs a Region whose geometry changes")
    _require(alternative_regions, "fixture package needs an alternative Region reconstruction")
    _validate_source_bound_geometries(
        package,
        claims=claims,
        evidence_links=indexes["evidence_links"],
        sources=indexes["sources"],
        package_root=package_root,
    )
    _validate_context_bound_extents(
        package,
        claims=claims,
        evidence_links=indexes["evidence_links"],
        sources=indexes["sources"],
        package_root=package_root,
    )

    challenged_influence_relations: list[str] = []
    for relation_id, relation in indexes["relations"].items():
        predicate = relation.get("predicate")
        _require(predicate not in DERIVED_ONLY_PREDICATES, f"{relation_id} stores derived {predicate} as Relation")
        relation_claims = relation.get("claim_refs")
        _require(
            isinstance(relation_claims, list) and len(relation_claims) == 1,
            f"{relation_id} must bind exactly one Relation Claim",
        )
        claim = claims[relation_claims[0]]
        _require(
            claim.get("evidence_state") in {"supported", "mixed"},
            f"{relation_id} needs reviewed claim-level evidence",
        )
        _validate_relation_extent_evidence(
            relation_id,
            relation,
            claim,
            evidence_links=indexes["evidence_links"],
            sources=indexes["sources"],
            entities=indexes["entities"],
            regions=indexes["regions"],
            package_root=package_root,
        )
        if predicate == "influence":
            _require(
                isinstance(relation.get("mechanism"), str) and relation["mechanism"].strip(),
                f"{relation_id} influence needs an explicit mechanism",
            )
            _require(
                isinstance(relation.get("scope"), str) and relation["scope"].strip(),
                f"{relation_id} influence needs an explicit scope",
            )
            _require(
                claim.get("evidence_state") == "mixed"
                and claim.get("review_state") == "contested"
                and claim.get("uncertainty_refs"),
                f"{relation_id} challenged influence must preserve conflict and uncertainty",
            )
            challenged_influence_relations.append(relation_id)
    _require(challenged_influence_relations, "fixture package needs a challenged influence Claim")

    context_objects: dict[str, dict[str, Any]] = {}
    for collection in ("entities", "events", "states", "processes", "trajectories", "regions", "relations"):
        context_objects.update(indexes[collection])
    slice_space = world_slice.get("spatial_bounds", {})
    _require(
        slice_space.get("kind") == "composite_scope",
        "WorldSlice fixture must declare an explicit composite spatial scope",
    )
    declared_slice_refs = set(slice_space.get("place_refs", [])) | set(slice_space.get("region_refs", []))
    modeled_place_refs = {
        entity_id
        for entity_id, entity in indexes["entities"].items()
        if entity.get("entity_kind") == "Place"
    }
    modeled_anchor_refs = set().union(
        *(_object_spatial_anchor_refs(item) for item in context_objects.values())
    )
    _require(
        modeled_place_refs | modeled_anchor_refs <= declared_slice_refs,
        "WorldSlice spatial bounds omit modeled Place or Region context",
    )
    slice_time = world_slice["temporal_bounds"]
    for item in context_objects.values():
        for extent in _object_temporal_extents(item):
            _require(
                _temporal_contains(slice_time, extent),
                f"WorldSlice temporal bounds omit modeled context {item.get('id')}",
            )
            for alternative in extent.get("alternatives", []):
                _require(
                    _temporal_contains(slice_time, alternative),
                    f"WorldSlice temporal bounds omit alternative context {item.get('id')}",
                )
    co_presence_observations: list[str] = []
    for observation_id, observation in indexes["derived_observations"].items():
        _require(observation.get("relation_created") is False, f"{observation_id} must not create Relation")
        claim = claims.get(observation.get("claim_ref"))
        _require(isinstance(claim, dict), f"{observation_id} needs observation Claim")
        _require(
            claim.get("claim_kind") == "observation"
            and claim.get("origin") == "system"
            and claim.get("evidence_state") == "not_applicable",
            f"{observation_id} epistemic dimensions are collapsed",
        )
        if observation.get("observation_kind") == "co_presence":
            input_refs = observation.get("input_refs")
            _require(
                isinstance(input_refs, list) and len(input_refs) == 2,
                f"{observation_id} co-presence needs exactly two inputs",
            )
            inputs = [context_objects.get(ref) for ref in input_refs]
            _require(all(isinstance(item, dict) for item in inputs), f"{observation_id} has invalid inputs")
            left, right = inputs
            input_claim_refs = {
                claim_id
                for item in inputs
                for extent_key in ("temporal_extent", "spatial_extent")
                for claim_id in item.get(extent_key, {}).get("basis_claim_refs", [])
            }
            _require(
                claim.get("target_refs") == [observation_id]
                and set(claim.get("input_claim_refs", [])) == input_claim_refs,
                f"{observation_id} Claim must target the observation and bind every input premise",
            )
            _require(
                _temporal_overlaps(left.get("temporal_extent", {}), right.get("temporal_extent", {})),
                f"{observation_id} co-presence inputs do not overlap in time",
            )
            left_space = _spatial_signature(left.get("spatial_extent"))
            right_space = _spatial_signature(right.get("spatial_extent"))
            _require(
                left_space is not None and left_space == right_space,
                f"{observation_id} co-presence inputs do not overlap in space",
            )
            subjects = {left.get("subject_ref"), right.get("subject_ref")}
            _require(
                None not in subjects and len(subjects) == 2,
                f"{observation_id} co-presence inputs need two distinct subjects",
            )
            _require(
                not any(
                    {relation.get("subject_ref"), relation.get("object_ref")} == subjects
                    for relation in indexes["relations"].values()
                ),
                f"{observation_id} must demonstrate co-presence without a stored Relation",
            )
            co_presence_observations.append(observation_id)
    _require(co_presence_observations, "fixture package needs spatial-temporal co-presence without Relation")

    for view_id, view in indexes["synchronized_views"].items():
        view_time = view.get("time_state", {})
        _validate_extent(
            view_time,
            context=view_id,
            dimension="temporal",
            claim_ids=claim_ids,
            fixture_mode=fixture_mode,
        )
        _require(view.get("local_context_refs"), f"{view_id} needs local context")
        _require(view.get("global_context_refs"), f"{view_id} needs global context")
        _require(view.get("active_layer_refs"), f"{view_id} needs active layers")
        _require(view.get("selected_object_refs"), f"{view_id} needs selected objects")
        camera = view.get("camera_state")
        _require(
            isinstance(camera, dict)
            and camera.get("kind") == "bounds"
            and isinstance(camera.get("bbox"), list)
            and len(camera["bbox"]) == 4
            and all(isinstance(value, (int, float)) for value in camera["bbox"])
            and camera.get("coordinate_reference") == "EPSG:4326",
            f"{view_id} needs a complete camera extent",
        )
        west, south, east, north = camera["bbox"]
        _require(
            -180 <= west < east <= 180 and -90 <= south < north <= 90,
            f"{view_id} camera bounds must be ordered EPSG:4326 coordinates",
        )
        comparison = view.get("comparison_scope")
        _require(
            isinstance(comparison, dict)
            and comparison.get("mode") in {"none", "local_global", "object_comparison"}
            and isinstance(comparison.get("reference_refs"), list),
            f"{view_id} needs an explicit comparison/reference scope",
        )
        context_by_scope = {
            "local": [context_objects.get(ref) for ref in view["local_context_refs"]],
            "global": [context_objects.get(ref) for ref in view["global_context_refs"]],
        }
        for scope_name, objects in context_by_scope.items():
            _require(
                all(isinstance(item, dict) for item in objects),
                f"{view_id} {scope_name} context contains an unresolved object",
            )
            for item in objects:
                extents = _object_temporal_extents(item)
                _require(
                    extents and any(_temporal_overlaps(view_time, extent) for extent in extents),
                    f"{view_id} {scope_name} context {item.get('id')} does not intersect view time",
                )
        if comparison.get("mode") == "local_global":
            reference_refs = set(comparison["reference_refs"])
            _require(reference_refs, f"{view_id} local_global comparison needs references")
            local_anchors = set().union(
                *(_object_spatial_anchor_refs(item) for item in context_by_scope["local"])
            )
            global_anchors = set().union(
                *(_object_spatial_anchor_refs(item) for item in context_by_scope["global"])
            )
            _require(
                reference_refs & local_anchors and reference_refs & global_anchors,
                f"{view_id} comparison references must bind both local and global spatial context",
            )
        uncertainty_display = view.get("uncertainty_display")
        _require(
            isinstance(uncertainty_display, dict)
            and all(
                isinstance(uncertainty_display.get(key), bool)
                for key in ("show_material", "show_alternatives", "show_corpus_limits")
            ),
            f"{view_id} needs explicit uncertainty display settings",
        )
        _require(
            set(view["local_context_refs"]).isdisjoint(view["global_context_refs"]),
            f"{view_id} local and global context must remain distinct",
        )
        _require(
            view.get("reconstruction_mode") in ALLOWED_RECONSTRUCTION_MODES,
            f"{view_id} has invalid reconstruction mode",
        )
        _require(
            view.get("dataset_identity") == package.get("world_slice", {}).get("dataset_identity"),
            f"{view_id} dataset identity must match the WorldSlice",
        )
        _require(
            _temporal_contains(world_slice["temporal_bounds"], view_time),
            f"{view_id} time state must remain within WorldSlice bounds",
        )

    _validate_coverage(package, indexes, registry, root)
    _validate_reviews(root, package, require_ready=require_ready)
    _validate_compatibility(root, require_ready=require_ready)

    return {
        expected_type: len(indexes[collection])
        for collection, expected_type in COLLECTION_TYPES.items()
        if collection != "derived_observations"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    try:
        counts = validate_package(args.root, require_ready=args.require_ready)
    except FixtureValidationError as exc:
        print(f"[FAIL] World-model fixtures: {exc}")
        return 1
    rendered = ", ".join(f"{key}={value}" for key, value in counts.items())
    mode = "READY" if args.require_ready else "STRUCTURAL"
    print(f"[PASS] World-model fixtures: mode={mode}; {rendered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
