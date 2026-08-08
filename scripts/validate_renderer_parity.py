#!/usr/bin/env python3
"""Validate ARTEMIS 2D/Globe semantic parity for issue #344."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_render_projection_fixtures import build_all  # noqa: E402


WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
PROJECTION_SCHEMA_PATH = ROOT / "fixtures" / "render_projection" / "v1" / "schema.json"
EXPECTED_PATH = ROOT / "fixtures" / "render_parity" / "v1" / "expected.json"
EXPECTED_SCHEMA_PATH = ROOT / "fixtures" / "render_parity" / "v1" / "schema.json"
NEGATIVE_CASES_PATH = ROOT / "fixtures" / "render_parity" / "v1" / "negative_cases.json"

GEOMETRY_KIND_MAP = {
    "cartographic_point": "Point",
    "cartographic_polyline": "LineString",
    "cartographic_polygon": "Polygon",
    "cartographic_multipolygon": "MultiPolygon",
}

ITEM_FIELDS = (
    "item_id",
    "object_ref",
    "object_type",
    "subobject_ref",
    "render_role",
    "temporal_membership",
    "spatial_status",
    "geometry_refs",
    "place_ref",
    "layer_refs",
    "claim_refs",
    "uncertainty_refs",
    "evidence_link_refs",
    "source_refs",
    "semantic_flags",
)

RENDERED_FIELDS = (
    "item_id",
    "object_ref",
    "object_type",
    "subobject_ref",
    "render_role",
    "temporal_membership",
    "layer_refs",
    "claim_refs",
    "uncertainty_refs",
    "evidence_link_refs",
    "source_refs",
    "geometry_ref",
    "geometry_claim_refs",
    "geometry_uncertainty_refs",
    "geometry_reconstruction_mode",
    "geometry_is_primary",
    "semantic_flags",
)


class ParityError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParityError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ParityError(f"{path} must contain a JSON object")
    return value


def _schema_errors(value: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _stable(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_stable(item) for item in value]
    return value


def _item_fingerprint(item: dict[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(item.get(field)) for field in ITEM_FIELDS}


def _projection_item_index(projection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in projection.get("items", []):
        item_id = str(item.get("item_id") or "")
        if not item_id:
            raise ParityError("projection item without item_id")
        if item_id in index:
            raise ParityError(f"duplicate projection item_id: {item_id}")
        index[item_id] = item
    return index


def _normalize_maplibre(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for feature in adapter.get("features", []):
        instance_id = str(feature.get("id") or "")
        if not instance_id:
            raise ParityError("MapLibre feature without instance id")
        if instance_id in seen:
            raise ParityError(f"duplicate MapLibre instance id: {instance_id}")
        seen.add(instance_id)
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        row = {
            "instance_id": instance_id,
            "geometry_type": geometry.get("type"),
        }
        row.update({field: copy.deepcopy(properties.get(field)) for field in RENDERED_FIELDS})
        rows.append(row)
    return sorted(rows, key=lambda row: row["instance_id"])


def _normalize_globe(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for primitive in adapter.get("primitives", []):
        instance_id = str(primitive.get("primitive_id") or "")
        if not instance_id:
            raise ParityError("Globe primitive without instance id")
        if instance_id in seen:
            raise ParityError(f"duplicate Globe instance id: {instance_id}")
        seen.add(instance_id)
        primitive_kind = primitive.get("primitive_kind")
        if primitive_kind not in GEOMETRY_KIND_MAP:
            raise ParityError(f"unknown Globe primitive kind: {primitive_kind!r}")
        row = {
            "instance_id": instance_id,
            "geometry_type": GEOMETRY_KIND_MAP[primitive_kind],
        }
        row.update({field: copy.deepcopy(primitive.get(field)) for field in RENDERED_FIELDS})
        rows.append(row)
    return sorted(rows, key=lambda row: row["instance_id"])


def _validate_unrendered_rows(
    adapter: dict[str, Any],
    projection: dict[str, Any],
    key: str,
    expected_status: str,
) -> list[dict[str, Any]]:
    item_index = _projection_item_index(projection)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in adapter.get(key, []):
        item_id = str(row.get("item_id") or "")
        if not item_id:
            raise ParityError(f"{key} row without item_id")
        if item_id in seen:
            raise ParityError(f"duplicate {key} item_id: {item_id}")
        seen.add(item_id)
        item = item_index.get(item_id)
        if item is None:
            raise ParityError(f"{key} references missing projection item: {item_id}")
        if item.get("spatial_status") != expected_status:
            raise ParityError(
                f"{key} status drift for {item_id}: projection={item.get('spatial_status')!r}, expected={expected_status!r}"
            )
        if row.get("object_ref") != item.get("object_ref"):
            raise ParityError(f"{key} object_ref drift for {item_id}")
        if row.get("subobject_ref") != item.get("subobject_ref"):
            raise ParityError(f"{key} subobject_ref drift for {item_id}")
        if row.get("spatial_status") != expected_status:
            raise ParityError(f"{key} row status drift for {item_id}")
        rows.append(_item_fingerprint(item))
    return sorted(rows, key=lambda value: value["item_id"])


def renderer_envelope(
    *,
    renderer: str,
    projection: dict[str, Any],
    adapter: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    if renderer not in {"maplibre", "globe"}:
        raise ParityError(f"unknown renderer: {renderer}")

    source = adapter.get("source")
    if source != projection.get("source"):
        raise ParityError(f"{renderer}: adapter source does not match neutral projection")
    if adapter.get("projection_id") != projection.get("projection_id"):
        raise ParityError(f"{renderer}: projection_id drift")

    rendered = _normalize_maplibre(adapter) if renderer == "maplibre" else _normalize_globe(adapter)
    unresolved = _validate_unrendered_rows(
        adapter, projection, "unresolved_items", "unresolved"
    )
    non_spatial = _validate_unrendered_rows(
        adapter, projection, "non_spatial_items", "not_spatial"
    )

    all_items = sorted(
        (_item_fingerprint(item) for item in projection.get("items", [])),
        key=lambda value: value["item_id"],
    )

    selection = state.get("selection") or {}
    focus = state.get("active_focus") or {}
    return {
        "source": copy.deepcopy(projection.get("source")),
        "projection_id": projection.get("projection_id"),
        "selection": {
            "primary_object_ref": selection.get("primary_object_ref"),
            "selected_object_refs": sorted(selection.get("selected_object_refs") or []),
            "active_focus": {
                "trajectory_ref": focus.get("trajectory_ref"),
                "trajectory_segment_ref": focus.get("trajectory_segment_ref"),
                "region_ref": focus.get("region_ref"),
                "region_geometry_ref": focus.get("region_geometry_ref"),
            },
        },
        "semantic_state": {
            "active_object_refs": sorted(projection.get("active_object_refs") or []),
            "possible_active_object_refs": sorted(
                projection.get("possible_active_object_refs") or []
            ),
            "context_object_refs": sorted(projection.get("context_object_refs") or []),
            "deferred_object_types": sorted(projection.get("deferred_object_types") or []),
        },
        "items": all_items,
        "rendered_instances": rendered,
        "unresolved_items": unresolved,
        "non_spatial_items": non_spatial,
        "losses": sorted(
            (copy.deepcopy(loss) for loss in projection.get("losses", [])),
            key=lambda value: value["loss_id"],
        ),
    }


def assert_parity(
    *,
    map_projection: dict[str, Any],
    maplibre: dict[str, Any],
    globe_projection: dict[str, Any],
    globe: dict[str, Any],
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    left = renderer_envelope(
        renderer="maplibre", projection=map_projection, adapter=maplibre, state=state
    )
    right = renderer_envelope(
        renderer="globe", projection=globe_projection, adapter=globe, state=state
    )
    if _stable(left) != _stable(right):
        raise ParityError("2D/Globe semantic parity mismatch")
    return left, right


def _validate_expected(
    *,
    expected: dict[str, Any],
    envelope: dict[str, Any],
    state: dict[str, Any],
) -> None:
    if envelope["source"] != expected["source"]:
        raise ParityError("expected fixture source identity mismatch")

    selection_expected = expected["selection"]
    if envelope["selection"] != selection_expected:
        raise ParityError("selected object / active focus parity fixture mismatch")

    expected_state = expected["expected_semantic_state"]
    if envelope["semantic_state"] != expected_state:
        raise ParityError("active/possible/context/deferred semantic state mismatch")

    item_index = {item["item_id"]: item for item in envelope["items"]}
    for anchor in expected["anchors"]:
        item = item_index.get(anchor["item_id"])
        if item is None:
            raise ParityError(f"expected anchor missing: {anchor['item_id']}")
        for field, expected_value in anchor.items():
            if field == "item_id":
                continue
            if item.get(field) != expected_value:
                raise ParityError(
                    f"anchor {anchor['item_id']} field {field} mismatch: "
                    f"expected={expected_value!r}, actual={item.get(field)!r}"
                )

    primary_ref = state["selection"]["primary_object_ref"]
    selected_items = [
        item for item in envelope["items"] if item.get("object_ref") == primary_ref
    ]
    if not selected_items:
        raise ParityError("primary selected object is absent from renderer semantic envelope")
    if primary_ref == "event-documented-workshop-meeting" and not any(
        item.get("spatial_status") == "unresolved" for item in selected_items
    ):
        raise ParityError("selected workshop meeting must remain unresolved, not invented")


def _validate_relation_distinction(
    *, world: dict[str, Any], expected: dict[str, Any], envelope: dict[str, Any]
) -> None:
    rule = expected["relation_distinction"]
    derived = next(
        (
            item
            for item in world.get("derived_observations", [])
            if item.get("id") == rule["derived_observation_ref"]
        ),
        None,
    )
    if derived is None:
        raise ParityError("expected DerivedObservation is missing")
    if bool(derived.get("relation_created")) is not rule["relation_created"]:
        raise ParityError("DerivedObservation relation_created semantics drifted")

    relation_ids = {str(item.get("id")) for item in world.get("relations", [])}
    for relation_ref in rule["documented_relation_refs"]:
        if relation_ref not in relation_ids:
            raise ParityError(f"documented Relation missing: {relation_ref}")

    if "Relation" not in envelope["semantic_state"]["deferred_object_types"]:
        raise ParityError("Relation must remain explicitly deferred in projection v1")
    if any(
        item.get("object_type") == "Relation" for item in envelope.get("items", [])
    ):
        raise ParityError("Relation unexpectedly entered projection v1")
    if any(
        item.get("object_ref") == rule["derived_observation_ref"]
        for item in envelope.get("items", [])
    ):
        raise ParityError("DerivedObservation was promoted into renderer object semantics")


def _boundary_state(
    base_state: dict[str, Any], case: dict[str, Any]
) -> dict[str, Any]:
    state = copy.deepcopy(base_state)
    state["state_id"] = f"{base_state['state_id']}:{case['case_id']}"
    state["temporal_selection"] = copy.deepcopy(case["temporal_selection"])
    state["active_focus"] = copy.deepcopy(case["active_focus"])
    return state


def _validate_boundary_cases(
    *,
    world: dict[str, Any],
    base_state: dict[str, Any],
    projection_schema: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    for case in expected["boundary_cases"]:
        state = _boundary_state(base_state, case)
        projection, maplibre, globe = build_all(world, state, projection_schema)
        envelope, _ = assert_parity(
            map_projection=projection,
            maplibre=maplibre,
            globe_projection=projection,
            globe=globe,
            state=state,
        )
        present_subobjects = {
            str(item["subobject_ref"])
            for item in envelope["items"]
            if item.get("subobject_ref") is not None
        }
        missing = sorted(
            set(case["expected_present_subobject_refs"]) - present_subobjects
        )
        forbidden = sorted(
            set(case["expected_absent_subobject_refs"]) & present_subobjects
        )
        if missing:
            raise ParityError(f"boundary {case['case_id']} missing expected subobjects: {missing}")
        if forbidden:
            raise ParityError(
                f"boundary {case['case_id']} contains forbidden subobjects: {forbidden}"
            )


def apply_negative_case(
    case: dict[str, Any],
    *,
    map_projection: dict[str, Any],
    maplibre: dict[str, Any],
    globe_projection: dict[str, Any],
    globe: dict[str, Any],
) -> None:
    target = case["target"]
    mutation = case["mutation"]

    if target in {"maplibre_adapter", "globe_adapter"}:
        adapter = maplibre if target == "maplibre_adapter" else globe
        collection_key = "features" if target == "maplibre_adapter" else "primitives"
        id_key = "id" if target == "maplibre_adapter" else "primitive_id"
        rows = adapter[collection_key]
        instance_id = case["instance_id"]
        if mutation == "remove_rendered_instance":
            before = len(rows)
            adapter[collection_key] = [
                row for row in rows if row.get(id_key) != instance_id
            ]
            if len(adapter[collection_key]) == before:
                raise ParityError(f"negative case target instance missing: {instance_id}")
            return
        if mutation == "replace_rendered_field":
            row = next((row for row in rows if row.get(id_key) == instance_id), None)
            if row is None:
                raise ParityError(f"negative case target instance missing: {instance_id}")
            if target == "maplibre_adapter":
                row.setdefault("properties", {})[case["field"]] = copy.deepcopy(
                    case["value"]
                )
            else:
                row[case["field"]] = copy.deepcopy(case["value"])
            return
        raise ParityError(f"unsupported adapter mutation: {mutation}")

    if target == "globe_projection":
        item = next(
            (
                item
                for item in globe_projection.get("items", [])
                if item.get("item_id") == case["item_id"]
            ),
            None,
        )
        if item is None:
            raise ParityError(f"negative projection item missing: {case['item_id']}")
        if mutation == "replace_item_semantic_flag":
            item.setdefault("semantic_flags", {})[case["field"]] = copy.deepcopy(
                case["value"]
            )
            return
        if mutation == "replace_item_field":
            item[case["field"]] = copy.deepcopy(case["value"])
            return
        raise ParityError(f"unsupported projection mutation: {mutation}")

    raise ParityError(f"unsupported negative target: {target}")


def build_baseline() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    world = _load(WORLD_PATH)
    state = _load(STATE_PATH)
    projection_schema = _load(PROJECTION_SCHEMA_PATH)
    projection, maplibre, globe = build_all(world, state, projection_schema)
    return world, state, projection_schema, projection, maplibre, globe


def validate_all() -> dict[str, Any]:
    expected = _load(EXPECTED_PATH)
    expected_schema = _load(EXPECTED_SCHEMA_PATH)
    schema_errors = _schema_errors(expected, expected_schema)
    if schema_errors:
        raise ParityError("expected parity fixture schema failed: " + "; ".join(schema_errors))

    world, state, projection_schema, projection, maplibre, globe = build_baseline()
    envelope, _ = assert_parity(
        map_projection=projection,
        maplibre=maplibre,
        globe_projection=projection,
        globe=globe,
        state=state,
    )
    _validate_expected(expected=expected, envelope=envelope, state=state)
    _validate_relation_distinction(world=world, expected=expected, envelope=envelope)
    _validate_boundary_cases(
        world=world,
        base_state=state,
        projection_schema=projection_schema,
        expected=expected,
    )

    return {
        "fixture_id": expected["fixture_id"],
        "projection_id": projection["projection_id"],
        "item_count": len(envelope["items"]),
        "rendered_instance_count": len(envelope["rendered_instances"]),
        "unresolved_count": len(envelope["unresolved_items"]),
        "boundary_case_count": len(expected["boundary_cases"]),
    }


def main() -> int:
    try:
        summary = validate_all()
        print(
            "[PASS] Cross-renderer semantic parity v1: "
            f"fixture={summary['fixture_id']}; projection={summary['projection_id']}; "
            f"items={summary['item_count']}; rendered={summary['rendered_instance_count']}; "
            f"unresolved={summary['unresolved_count']}; boundaries={summary['boundary_case_count']}"
        )
        return 0
    except (ParityError, KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
