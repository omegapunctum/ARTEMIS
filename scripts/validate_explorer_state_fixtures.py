#!/usr/bin/env python3
"""Validate renderer-neutral ARTEMIS Explorer State fixtures.

The JSON Schema owns structural shape. This validator adds repository-specific
cross-reference and semantic checks against the reviewed World Model fixture.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "fixtures" / "explorer_state" / "v1" / "schema.json"
DEFAULT_STATE = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
DEFAULT_WORLD = ROOT / "fixtures" / "world_model" / "v1" / "package.json"

BANNED_SHARED_KEYS = {
    "zoom",
    "pitch",
    "bearing",
    "camera",
    "camera_state",
    "camera_matrix",
    "viewer",
    "scene",
    "maplibre",
    "cesium",
    "visible_object_ids",
    "filtered_features",
    "filtered_feature_ids",
}

TEMPORAL_RE = re.compile(r"^(?P<year>-?\d{1,6})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?$")


class ExplorerStateValidationError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExplorerStateValidationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExplorerStateValidationError(f"{path} must contain a JSON object")
    return payload


def _schema_errors(schema: dict[str, Any], state: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(state), key=lambda item: list(item.absolute_path))
    messages: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"schema:{path}: {error.message}")
    return messages


def _walk_banned_keys(value: Any, path: str = "<root>") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in BANNED_SHARED_KEYS:
                errors.append(f"renderer-owned key is forbidden in Explorer State: {child_path}")
            errors.extend(_walk_banned_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_banned_keys(child, f"{path}[{index}]"))
    return errors


def _temporal_key(value: str) -> tuple[int, int, int]:
    match = TEMPORAL_RE.match(value)
    if not match:
        raise ExplorerStateValidationError(
            f"temporal selection value {value!r} must use signed year, YYYY-MM or YYYY-MM-DD form"
        )
    year = int(match.group("year"))
    month = int(match.group("month") or 1)
    day = int(match.group("day") or 1)
    if not 1 <= month <= 12:
        raise ExplorerStateValidationError(f"invalid month in temporal selection: {value!r}")
    if not 1 <= day <= 31:
        raise ExplorerStateValidationError(f"invalid day in temporal selection: {value!r}")
    return year, month, day


def _id_index(world: dict[str, Any]) -> tuple[set[str], set[str], dict[str, set[str]], dict[str, set[str]], set[str]]:
    object_ids: set[str] = set()
    layer_ids = {str(item.get("id")) for item in world.get("layers", []) if item.get("id")}
    derived_ids = {
        str(item.get("id"))
        for item in world.get("derived_observations", [])
        if item.get("id")
    }

    for collection_name in (
        "entities",
        "events",
        "states",
        "processes",
        "trajectories",
        "regions",
        "relations",
    ):
        for item in world.get(collection_name, []):
            if item.get("id"):
                object_ids.add(str(item["id"]))

    trajectory_segments: dict[str, set[str]] = {}
    for trajectory in world.get("trajectories", []):
        trajectory_id = str(trajectory.get("id") or "")
        if not trajectory_id:
            continue
        trajectory_segments[trajectory_id] = {
            str(segment.get("id"))
            for segment in trajectory.get("segments", [])
            if segment.get("id")
        }

    region_geometries: dict[str, set[str]] = {}
    for region in world.get("regions", []):
        region_id = str(region.get("id") or "")
        if not region_id:
            continue
        region_geometries[region_id] = {
            str(geometry.get("id"))
            for geometry in region.get("geometry_versions", [])
            if geometry.get("id")
        }

    all_context_refs = object_ids | derived_ids
    return object_ids, layer_ids, trajectory_segments, region_geometries, all_context_refs


def _unknown_refs(values: list[Any], allowed: set[str]) -> list[str]:
    return sorted({str(value) for value in values if str(value) not in allowed})


def validate_state(
    state: dict[str, Any],
    *,
    schema: dict[str, Any],
    world: dict[str, Any],
) -> list[str]:
    errors = _schema_errors(schema, state)
    errors.extend(_walk_banned_keys(state))
    if errors:
        return errors

    world_slice = world.get("world_slice") or {}
    expected_slice_ref = str(world_slice.get("id") or "")
    if state.get("world_slice_ref") != expected_slice_ref:
        errors.append(
            f"world_slice_ref mismatch: expected {expected_slice_ref!r}, got {state.get('world_slice_ref')!r}"
        )

    expected_identity = world_slice.get("dataset_identity")
    if state.get("dataset_identity") != expected_identity:
        errors.append("dataset_identity must exactly match the pinned World Slice dataset identity")

    object_ids, layer_ids, trajectory_segments, region_geometries, context_refs = _id_index(world)

    unknown_layers = _unknown_refs(state.get("active_layer_refs", []), layer_ids)
    if unknown_layers:
        errors.append(f"unknown active_layer_refs: {unknown_layers}")

    selection = state.get("selection") or {}
    selected_refs = list(selection.get("selected_object_refs") or [])
    comparison_refs = list(selection.get("comparison_object_refs") or [])
    primary_ref = selection.get("primary_object_ref")
    unknown_selection = _unknown_refs(selected_refs + comparison_refs, object_ids)
    if unknown_selection:
        errors.append(f"unknown selection object refs: {unknown_selection}")
    if primary_ref is not None:
        if str(primary_ref) not in object_ids:
            errors.append(f"primary_object_ref does not resolve: {primary_ref!r}")
        if str(primary_ref) not in {str(item) for item in selected_refs}:
            errors.append("primary_object_ref must also be present in selected_object_refs")

    context = state.get("context") or {}
    local_refs = list(context.get("local_context_refs") or [])
    global_refs = list(context.get("global_context_refs") or [])
    derived_refs = list(context.get("derived_observation_refs") or [])
    unknown_context = _unknown_refs(local_refs + global_refs, context_refs)
    if unknown_context:
        errors.append(f"unknown local/global context refs: {unknown_context}")
    unknown_derived = _unknown_refs(derived_refs, {
        str(item.get("id"))
        for item in world.get("derived_observations", [])
        if item.get("id")
    })
    if unknown_derived:
        errors.append(f"unknown derived_observation_refs: {unknown_derived}")

    comparison_scope = state.get("comparison_scope") or {}
    unknown_comparison_scope = _unknown_refs(
        list(comparison_scope.get("reference_refs") or []),
        object_ids,
    )
    if unknown_comparison_scope:
        errors.append(f"unknown comparison_scope.reference_refs: {unknown_comparison_scope}")

    active_focus = state.get("active_focus") or {}
    trajectory_ref = active_focus.get("trajectory_ref")
    segment_ref = active_focus.get("trajectory_segment_ref")
    if segment_ref is not None:
        if trajectory_ref is None:
            errors.append("trajectory_segment_ref requires trajectory_ref")
        elif str(segment_ref) not in trajectory_segments.get(str(trajectory_ref), set()):
            errors.append(
                f"trajectory segment {segment_ref!r} does not belong to trajectory {trajectory_ref!r}"
            )
    if trajectory_ref is not None and str(trajectory_ref) not in trajectory_segments:
        errors.append(f"trajectory_ref does not resolve to a Trajectory: {trajectory_ref!r}")

    region_ref = active_focus.get("region_ref")
    geometry_ref = active_focus.get("region_geometry_ref")
    if geometry_ref is not None:
        if region_ref is None:
            errors.append("region_geometry_ref requires region_ref")
        elif str(geometry_ref) not in region_geometries.get(str(region_ref), set()):
            errors.append(
                f"Region geometry {geometry_ref!r} does not belong to Region {region_ref!r}"
            )
    if region_ref is not None and str(region_ref) not in region_geometries:
        errors.append(f"region_ref does not resolve to a Region: {region_ref!r}")

    reconstruction_ref = active_focus.get("reconstruction_ref")
    if reconstruction_ref is not None:
        geometry_union = set().union(*region_geometries.values()) if region_geometries else set()
        if str(reconstruction_ref) not in object_ids | geometry_union:
            errors.append(f"reconstruction_ref does not resolve: {reconstruction_ref!r}")

    temporal = state.get("temporal_selection") or {}
    start = str(temporal.get("start") or "")
    end = str(temporal.get("end") or "")
    try:
        start_key = _temporal_key(start)
        end_key = _temporal_key(end)
        if start_key > end_key:
            errors.append("temporal_selection.start must be <= temporal_selection.end")
    except ExplorerStateValidationError as exc:
        errors.append(str(exc))
    if temporal.get("mode") == "instant" and start != end:
        errors.append("temporal_selection mode=instant requires identical start and end")

    epistemic = state.get("epistemic_display") or {}
    if epistemic.get("show_material_uncertainty") is not True:
        errors.append("material uncertainty cannot be disabled")
    if epistemic.get("show_corpus_limits") is not True:
        errors.append("corpus limits cannot be disabled")

    view_intent = state.get("view_intent") or {}
    if view_intent.get("kind") == "focus_object":
        target_ref = view_intent.get("target_ref")
        if target_ref is None or str(target_ref) not in object_ids:
            errors.append("focus_object view_intent.target_ref must resolve to a World Model object")
    if view_intent.get("kind") == "bounds":
        bbox = view_intent.get("bbox") or []
        if len(bbox) == 4 and float(bbox[1]) > float(bbox[3]):
            errors.append("view_intent bbox south latitude must be <= north latitude")

    return errors


def validate_paths(schema_path: Path, state_path: Path, world_path: Path) -> list[str]:
    schema = _load_json(schema_path)
    state = _load_json(state_path)
    world = _load_json(world_path)
    return validate_state(state, schema=schema, world=world)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    args = parser.parse_args(argv)

    errors = validate_paths(args.schema, args.state, args.world)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    print(
        "[PASS] Explorer State fixture: "
        f"state={args.state.name}; world={args.world.name}; schema=1.0.0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
