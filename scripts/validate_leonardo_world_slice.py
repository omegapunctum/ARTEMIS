#!/usr/bin/env python3
"""Validate the scope-frozen, non-public Leonardo World Slice curation package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_1502_1504" / "v1"
SELECTION_PATH = PACKAGE_ROOT / "selection_manifest.json"
SELECTION_SCHEMA_PATH = PACKAGE_ROOT / "selection_manifest.schema.json"
SOURCE_PATH = PACKAGE_ROOT / "source_registry.json"
SOURCE_SCHEMA_PATH = PACKAGE_ROOT / "source_registry.schema.json"
COVERAGE_PATH = PACKAGE_ROOT / "coverage_manifest.json"
COVERAGE_SCHEMA_PATH = PACKAGE_ROOT / "coverage_manifest.schema.json"
COST_PATH = PACKAGE_ROOT / "curation_cost.json"
COST_SCHEMA_PATH = PACKAGE_ROOT / "curation_cost.schema.json"

REQUIRED_OBJECT_TYPES = {"Entity", "Event", "State", "Process", "Trajectory", "Region"}
PROHIBITED_RELATION_PREDICATES = {
    "possible_encounter",
    "documented_encounter",
    "interaction",
    "influence",
    "causal",
}


class WorldSliceScopeError(ValueError):
    """Raised when the scope package violates its fail-closed boundary."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorldSliceScopeError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorldSliceScopeError(f"{path} must contain a JSON object")
    return value


def _validate_schema(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if not errors:
        return
    messages = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]
    raise WorldSliceScopeError(f"{label} schema validation failed: {'; '.join(messages)}")


def _index(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get(key) or "")
        if not identity:
            raise WorldSliceScopeError(f"{label} row missing {key}")
        if identity in result:
            raise WorldSliceScopeError(f"duplicate {label} {key}: {identity}")
        result[identity] = row
    return result


def validate_package(
    selection: dict[str, Any] | None = None,
    sources: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
    cost: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selection = selection or _load(SELECTION_PATH)
    sources = sources or _load(SOURCE_PATH)
    coverage = coverage or _load(COVERAGE_PATH)
    cost = cost or _load(COST_PATH)

    _validate_schema(selection, _load(SELECTION_SCHEMA_PATH), "selection manifest")
    _validate_schema(sources, _load(SOURCE_SCHEMA_PATH), "source registry")
    _validate_schema(coverage, _load(COVERAGE_SCHEMA_PATH), "coverage manifest")
    _validate_schema(cost, _load(COST_SCHEMA_PATH), "curation cost log")

    layer_index = _index(selection["layers"], "layer_id", "layer")
    object_index = _index(selection["candidate_objects"], "object_id", "candidate object")
    source_index = _index(sources["sources"], "source_id", "source")
    gap_index = _index(coverage["known_gaps"], "gap_id", "known gap")
    _index(cost["entries"], "activity_id", "cost activity")

    object_types = {row["object_type"] for row in object_index.values()}
    if not REQUIRED_OBJECT_TYPES.issubset(object_types):
        missing = sorted(REQUIRED_OBJECT_TYPES - object_types)
        raise WorldSliceScopeError(f"required World Model candidate types are missing: {missing}")

    used_source_refs: set[str] = set()
    for object_id, row in object_index.items():
        missing_layers = set(row["layer_refs"]) - set(layer_index)
        if missing_layers:
            raise WorldSliceScopeError(
                f"candidate object {object_id} references missing layers: {sorted(missing_layers)}"
            )
        missing_sources = set(row["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"candidate object {object_id} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(row["source_refs"])
        if row["geometry"] is not None:
            raise WorldSliceScopeError(
                f"scope-freeze candidate {object_id} cannot publish geometry before review"
            )

    if selection["relation_policy"]["stored_relations"]:
        raise WorldSliceScopeError("scope package cannot store Relations while #331 is paused")
    actual_prohibited = set(selection["relation_policy"]["prohibited_predicates"])
    if actual_prohibited != PROHIBITED_RELATION_PREDICATES:
        raise WorldSliceScopeError("prohibited Relation predicate set drifted from the paused #331 boundary")
    if selection["relation_policy"]["allowed_computed_observations"] != ["derived_co_presence"]:
        raise WorldSliceScopeError("only derived_co_presence is allowed before #331")

    trajectories = [row for row in object_index.values() if row["object_type"] == "Trajectory"]
    if len(trajectories) != 1:
        raise WorldSliceScopeError("scope must contain exactly one bounded candidate Trajectory")
    trajectory = trajectories[0]
    if trajectory["spatial_mode"] != "unknown_route" or trajectory["geometry"] is not None:
        raise WorldSliceScopeError("candidate Trajectory must remain an unknown route with null geometry")
    segments = trajectory.get("segments") or []
    gap_segments = [row for row in segments if row["segment_kind"] == "inferred_gap"]
    if len(gap_segments) != 1:
        raise WorldSliceScopeError("candidate Trajectory must expose exactly one inferred gap")
    gap = gap_segments[0]
    if gap["spatial_mode"] != "unknown_route" or gap["geometry"] is not None:
        raise WorldSliceScopeError("inferred trajectory gap cannot carry route geometry")
    if gap["source_refs"]:
        raise WorldSliceScopeError("unknown route gap cannot pretend to have route evidence")
    for segment in segments:
        missing_sources = set(segment["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"trajectory segment {segment['segment_id']} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(segment["source_refs"])

    regions = [row for row in object_index.values() if row["object_type"] == "Region"]
    if len(regions) != 1:
        raise WorldSliceScopeError("scope must contain exactly one bounded candidate Region")
    versions = regions[0].get("versions") or []
    if len(versions) < 2:
        raise WorldSliceScopeError("candidate Region must preserve at least two source-bound versions")
    for version in versions:
        if version["reconstruction_mode"] != "analytical_model":
            raise WorldSliceScopeError("candidate Region version must remain an analytical model")
        if version["geometry_status"] != "pending_digitization_review" or version["geometry"] is not None:
            raise WorldSliceScopeError("candidate Region geometry must remain withheld pending review")
        missing_sources = set(version["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"Region version {version['version_id']} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(version["source_refs"])

    for source_id, source in source_index.items():
        rights = source["rights"]
        if source_id.startswith("source-rct-"):
            if rights["data_or_text_use"] != "citation_and_factual_claims_only":
                raise WorldSliceScopeError(f"{source_id} must remain citation/factual-use only")
            if rights["media_reuse"] != "prohibited_without_permission":
                raise WorldSliceScopeError(f"{source_id} cannot authorize image reuse")
        if source_id.startswith("source-getty-"):
            if rights["license"] != "ODC-By-1.0":
                raise WorldSliceScopeError(f"{source_id} must preserve Getty ODC-By 1.0 licensing")
            if not rights["attribution"].strip():
                raise WorldSliceScopeError(f"{source_id} must preserve Getty attribution")
        if source["source_type"] != "license_policy" and source_id not in used_source_refs:
            raise WorldSliceScopeError(f"unused candidate source is outside the frozen scope: {source_id}")

    manifest_gap_refs = set(selection["known_gap_refs"])
    if manifest_gap_refs != set(gap_index):
        raise WorldSliceScopeError("selection known_gap_refs must exactly match coverage_manifest gaps")

    for entry in cost["entries"]:
        if entry["measurement_state"] == "pending" and entry["duration_minutes"] is not None:
            raise WorldSliceScopeError("pending cost entries must not invent a duration")
        if entry["measurement_state"] == "recorded" and entry["duration_minutes"] is None:
            raise WorldSliceScopeError("recorded cost entries require an actual duration")

    readiness = selection["readiness"]
    if readiness != {
        "scope_frozen": True,
        "historical_objects_ready": False,
        "independent_review_count": 0,
        "promotion_allowed": False,
    }:
        raise WorldSliceScopeError("scope-freeze readiness must remain explicitly non-promotable")

    return {
        "slice_id": selection["slice_id"],
        "status": selection["status"],
        "candidate_object_count": len(object_index),
        "source_count": len(source_index),
        "known_gap_count": len(gap_index),
        "trajectory_gap_count": len(gap_segments),
        "region_version_count": len(versions),
        "promotion_allowed": readiness["promotion_allowed"],
    }


def main() -> int:
    try:
        summary = validate_package()
    except WorldSliceScopeError as exc:
        print(f"Leonardo World Slice scope: FAIL: {exc}")
        return 1
    print(
        "Leonardo World Slice scope: PASS "
        f"(objects={summary['candidate_object_count']}, sources={summary['source_count']}, "
        f"gaps={summary['known_gap_count']}, region_versions={summary['region_version_count']}, "
        f"promotion_allowed={summary['promotion_allowed']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
