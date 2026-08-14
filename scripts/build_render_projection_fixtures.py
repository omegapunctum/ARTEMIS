#!/usr/bin/env python3
"""Build and validate deterministic ARTEMIS render-projection fixtures.

R&D contract tool for issue #341.

Inputs:
- reviewed Foundation v3 World Model fixture;
- renderer-neutral Explorer State fixture;
- neutral projection JSON Schema.

Outputs in memory:
- neutral Render Projection Package;
- future MapLibre/GeoJSON adapter payload;
- engine-neutral Globe cartographic adapter payload.

The builder intentionally never geocodes named places, interpolates unknown
trajectory routes, chooses a silent winner between active Region alternatives,
or adds altitude / terrain history.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_explorer_state_fixtures import validate_state  # noqa: E402


WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
PACKAGE_DIR = ROOT / "fixtures" / "render_projection" / "v1"
SCHEMA_PATH = PACKAGE_DIR / "schema.json"
PROJECTION_PATH = PACKAGE_DIR / "projection.json"
MAPLIBRE_PATH = PACKAGE_DIR / "maplibre.geojson"
GLOBE_PATH = PACKAGE_DIR / "globe.json"

SCHEMA_VERSION = "1.0.0"
SUPPORTED_GEOMETRIES = {"Point", "LineString", "Polygon", "MultiPolygon"}
INCLUDED_TYPES = ["Entity", "Event", "State", "Process", "Trajectory", "Region"]
DEFERRED_TYPES = ["Relation"]

YEAR_RE = re.compile(r"^-?\d{1,6}$")
MONTH_RE = re.compile(r"^(?P<year>-?\d{1,6})-(?P<month>\d{2})$")
DAY_RE = re.compile(r"^(?P<year>-?\d{1,6})-(?P<month>\d{2})-(?P<day>\d{2})$")


class ProjectionError(ValueError):
    """Raised when projection would violate the executable contract."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectionError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectionError(f"{path} must contain a JSON object")
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _uniq(values: Iterable[Any]) -> list[str]:
    return sorted({str(value) for value in values if value is not None and str(value)})


def _infer_precision(value: str, declared: str | None) -> str:
    if declared in {"day", "month", "year"}:
        return str(declared)
    if DAY_RE.fullmatch(value):
        return "day"
    if MONTH_RE.fullmatch(value):
        return "month"
    if YEAR_RE.fullmatch(value):
        return "year"
    raise ProjectionError(
        f"unsupported temporal lexical value/precision: {value!r} / {declared!r}"
    )


def _value_bounds(
    value: str, precision: str | None
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    resolved = _infer_precision(value, precision)
    if resolved == "year":
        year = int(value)
        return (year, 1, 1), (year, 12, 31)
    if resolved == "month":
        match = MONTH_RE.fullmatch(value)
        if not match:
            raise ProjectionError(f"invalid month value: {value!r}")
        year = int(match.group("year"))
        month = int(match.group("month"))
        if not 1 <= month <= 12:
            raise ProjectionError(f"invalid month in {value!r}")
        return (year, month, 1), (year, month, 31)
    match = DAY_RE.fullmatch(value)
    if not match:
        raise ProjectionError(f"invalid day value: {value!r}")
    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        raise ProjectionError(f"invalid day in {value!r}")
    point = (year, month, day)
    return point, point


def _selection_bounds(
    state: dict[str, Any],
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    temporal = state["temporal_selection"]
    lower, _ = _value_bounds(str(temporal["start"]), str(temporal["precision"]))
    _, upper = _value_bounds(str(temporal["end"]), str(temporal["precision"]))
    return lower, upper


def _candidate_bounds(
    candidate: dict[str, Any],
) -> tuple[tuple[int, int, int] | None, tuple[int, int, int] | None]:
    precision = candidate.get("precision")
    start = candidate.get("start")
    end = candidate.get("end")
    lower = _value_bounds(str(start), str(precision))[0] if start is not None else None
    upper = _value_bounds(str(end), str(precision))[1] if end is not None else None
    return lower, upper


def _overlaps(
    lower: tuple[int, int, int] | None,
    upper: tuple[int, int, int] | None,
    query_lower: tuple[int, int, int],
    query_upper: tuple[int, int, int],
) -> bool:
    if upper is not None and upper < query_lower:
        return False
    if lower is not None and lower > query_upper:
        return False
    return True


def temporal_membership(
    extent: dict[str, Any] | None, state: dict[str, Any]
) -> str | None:
    """Return active / possible_active / atemporal_context / None.

    Alternatives and approximate extents are never promoted to exact active facts.
    """
    if not extent:
        return "atemporal_context"

    query_lower, query_upper = _selection_bounds(state)
    candidates: list[tuple[dict[str, Any], bool]] = [(extent, False)]
    candidates.extend((alternative, True) for alternative in extent.get("alternatives") or [])

    matching: list[tuple[dict[str, Any], bool]] = []
    for candidate, is_alternative in candidates:
        lower, upper = _candidate_bounds(candidate)
        if lower is None and upper is None:
            continue
        if _overlaps(lower, upper, query_lower, query_upper):
            matching.append((candidate, is_alternative))

    if not matching:
        return None

    if str(extent.get("kind") or "").startswith("approximate"):
        return "possible_active"
    if any(is_alternative for _, is_alternative in matching):
        return "possible_active"
    if extent.get("alternatives"):
        return "possible_active"
    return "active"


def _claim_indexes(
    world: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    claims = {str(item["id"]): item for item in world.get("claims", [])}
    evidence: dict[str, list[dict[str, Any]]] = {}
    for link in world.get("evidence_links", []):
        evidence.setdefault(str(link.get("claim_id")), []).append(link)
    return claims, evidence


def _epistemic_refs(
    claim_refs: Iterable[Any],
    direct_uncertainty_refs: Iterable[Any],
    claims: dict[str, dict[str, Any]],
    evidence: dict[str, list[dict[str, Any]]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    normalized_claims = _uniq(claim_refs)
    uncertainty = set(_uniq(direct_uncertainty_refs))
    evidence_refs: set[str] = set()
    source_refs: set[str] = set()

    for claim_ref in normalized_claims:
        claim = claims.get(claim_ref)
        if claim:
            uncertainty.update(_uniq(claim.get("uncertainty_refs") or []))
        for link in evidence.get(claim_ref, []):
            if link.get("id"):
                evidence_refs.add(str(link["id"]))
            if link.get("source_id"):
                source_refs.add(str(link["source_id"]))

    return (
        normalized_claims,
        sorted(uncertainty),
        sorted(evidence_refs),
        sorted(source_refs),
    )


def _geometry_ref(owner_ref: str, owner_subobject_ref: str | None = None) -> str:
    if owner_subobject_ref is None:
        return f"geom:{owner_ref}"
    return f"geom:{owner_ref}:{owner_subobject_ref}"


def _item_id(role: str, object_ref: str, subobject_ref: str | None = None) -> str:
    if subobject_ref is None:
        return f"rp:{role}:{object_ref}"
    return f"rp:{role}:{object_ref}:{subobject_ref}"


def _validate_geometry(geometry: dict[str, Any]) -> None:
    geometry_type = geometry.get("type")
    if geometry_type not in SUPPORTED_GEOMETRIES:
        raise ProjectionError(
            f"unsupported neutral geometry type in v1: {geometry_type!r}"
        )
    if not isinstance(geometry.get("coordinates"), list):
        raise ProjectionError(
            f"geometry {geometry_type!r} must contain coordinates array"
        )


def _region_index(world: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(region["id"]): region for region in world.get("regions", [])}


def _place_anchor_index(world: dict[str, Any]) -> dict[str, dict[str, Any]]:
    anchors: dict[str, dict[str, Any]] = {}
    for anchor in world.get("place_anchors", []):
        place_ref = str(anchor.get("place_ref") or "")
        if not place_ref:
            raise ProjectionError("place anchor lacks place_ref")
        if place_ref in anchors:
            raise ProjectionError(f"duplicate place anchor for {place_ref}")
        anchors[place_ref] = anchor
    return anchors


def _ensure_geometry_record(
    geometry_records: dict[str, dict[str, Any]],
    *,
    owner_ref: str,
    owner_subobject_ref: str | None,
    spatial_extent: dict[str, Any],
    origin_kind: str,
    claim_refs: Iterable[Any],
    uncertainty_refs: Iterable[Any],
    reconstruction_mode: str | None = None,
    is_primary: bool | None = None,
) -> str:
    geometry = spatial_extent.get("geometry")
    if not isinstance(geometry, dict):
        raise ProjectionError(
            f"resolved spatial extent has no geometry for {owner_ref}/{owner_subobject_ref}"
        )
    _validate_geometry(geometry)

    ref = _geometry_ref(owner_ref, owner_subobject_ref)
    candidate = {
        "geometry_ref": ref,
        "geometry": copy.deepcopy(geometry),
        "owner_ref": owner_ref,
        "owner_subobject_ref": owner_subobject_ref,
        "origin_kind": origin_kind,
        "spatial_precision": str(spatial_extent.get("precision") or "unknown"),
        "reconstruction_mode": reconstruction_mode,
        "is_primary": is_primary,
        "claim_refs": _uniq(claim_refs),
        "uncertainty_refs": _uniq(uncertainty_refs),
    }

    existing = geometry_records.get(ref)
    if existing is not None and existing != candidate:
        raise ProjectionError(f"geometry identity collision with different payload: {ref}")
    geometry_records[ref] = candidate
    return ref


def _active_region_geometry_refs(
    region_ref: str,
    *,
    world: dict[str, Any],
    state: dict[str, Any],
    geometry_records: dict[str, dict[str, Any]],
) -> list[str]:
    region = _region_index(world).get(region_ref)
    if region is None:
        raise ProjectionError(f"region_ref does not resolve: {region_ref}")

    show_alternatives = bool(state["epistemic_display"].get("show_alternatives"))
    selected_geometry_ref = state.get("active_focus", {}).get("region_geometry_ref")
    refs: list[str] = []

    for version in region.get("geometry_versions", []):
        membership = temporal_membership(version.get("temporal_extent"), state)
        if membership is None:
            continue

        primary = bool(version.get("is_primary"))
        if (
            not primary
            and not show_alternatives
            and version.get("id") != selected_geometry_ref
        ):
            continue

        refs.append(
            _ensure_geometry_record(
                geometry_records,
                owner_ref=region_ref,
                owner_subobject_ref=str(version["id"]),
                spatial_extent=version["spatial_extent"],
                origin_kind="region_geometry_version",
                claim_refs=version.get("claim_refs")
                or version["spatial_extent"].get("basis_claim_refs")
                or [],
                uncertainty_refs=_uniq(
                    (region.get("uncertainty_refs") or [])
                    + (version.get("uncertainty_refs") or [])
                ),
                reconstruction_mode=str(
                    version.get("reconstruction_mode") or "unknown"
                ),
                is_primary=primary,
            )
        )

    return sorted(refs)


def _unresolved_loss(
    *, item_id: str, reason: str, place_ref: str | None
) -> dict[str, Any]:
    return {
        "loss_id": f"loss:{item_id}",
        "item_id": item_id,
        "loss_kind": "geometry_unresolved",
        "cause": "source_model_gap",
        "severity": "material",
        "reason": reason,
        "place_ref": place_ref,
    }


def _resolve_spatial_extent(
    spatial_extent: dict[str, Any] | None,
    *,
    object_ref: str,
    subobject_ref: str | None,
    item_id: str,
    world: dict[str, Any],
    state: dict[str, Any],
    geometry_records: dict[str, dict[str, Any]],
    claim_refs: Iterable[Any],
    uncertainty_refs: Iterable[Any],
) -> tuple[str, list[str], str | None, list[dict[str, Any]]]:
    if not spatial_extent:
        return "not_spatial", [], None, []

    kind = str(spatial_extent.get("kind") or "unknown")
    place_ref = (
        str(spatial_extent["place_ref"]) if spatial_extent.get("place_ref") else None
    )

    if isinstance(spatial_extent.get("geometry"), dict):
        ref = _ensure_geometry_record(
            geometry_records,
            owner_ref=object_ref,
            owner_subobject_ref=subobject_ref,
            spatial_extent=spatial_extent,
            origin_kind="explicit_spatial_extent",
            claim_refs=spatial_extent.get("basis_claim_refs") or claim_refs,
            uncertainty_refs=uncertainty_refs,
        )
        return "resolved", [ref], place_ref, []

    if kind == "region_ref" and spatial_extent.get("region_ref"):
        refs = _active_region_geometry_refs(
            str(spatial_extent["region_ref"]),
            world=world,
            state=state,
            geometry_records=geometry_records,
        )
        if refs:
            return "resolved", refs, None, []
        reason = "region_has_no_temporally_resolved_geometry"
    elif kind == "named_place" and place_ref:
        anchor = _place_anchor_index(world).get(place_ref)
        if anchor is None:
            reason = "named_place_without_resolved_geometry"
        else:
            anchor_extent = {
                "geometry": copy.deepcopy(anchor["geometry"]),
                "precision": anchor["spatial_precision"],
                "basis_claim_refs": [anchor["claim_id"]],
            }
            ref = _ensure_geometry_record(
                geometry_records,
                owner_ref=place_ref,
                owner_subobject_ref=None,
                spatial_extent=anchor_extent,
                origin_kind="place_reference_anchor",
                claim_refs=[anchor["claim_id"]],
                uncertainty_refs=[anchor["uncertainty_ref"]],
            )
            return "resolved", [ref], place_ref, []
    elif kind == "unknown":
        reason = "unknown_spatial_extent"
    elif kind in {"multiple_regions", "multiple_places", "composite_scope"}:
        reason = "composite_extent_requires_explicit_projection_rule"
    else:
        reason = f"unresolved_spatial_extent:{kind}"

    return (
        "unresolved",
        [],
        place_ref,
        [_unresolved_loss(item_id=item_id, reason=reason, place_ref=place_ref)],
    )


def _make_item(
    *,
    role: str,
    object_ref: str,
    object_type: str,
    subobject_ref: str | None,
    membership: str,
    layer_refs: Iterable[Any],
    claim_refs: Iterable[Any],
    uncertainty_refs: Iterable[Any],
    spatial_extent: dict[str, Any] | None,
    semantic_flags: dict[str, Any],
    world: dict[str, Any],
    state: dict[str, Any],
    geometry_records: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    evidence: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    item_id = _item_id(role, object_ref, subobject_ref)
    anchor_claim_refs: list[str] = []
    anchor_uncertainty_refs: list[str] = []
    if (
        spatial_extent
        and spatial_extent.get("kind") == "named_place"
        and spatial_extent.get("place_ref")
    ):
        anchor = _place_anchor_index(world).get(str(spatial_extent["place_ref"]))
        if anchor is not None:
            anchor_claim_refs = [str(anchor["claim_id"])]
            anchor_uncertainty_refs = [str(anchor["uncertainty_ref"])]
    normalized_claims, normalized_uncertainty, evidence_refs, source_refs = _epistemic_refs(
        [*claim_refs, *anchor_claim_refs],
        [*uncertainty_refs, *anchor_uncertainty_refs],
        claims,
        evidence,
    )
    spatial_status, geometry_refs, place_ref, losses = _resolve_spatial_extent(
        spatial_extent,
        object_ref=object_ref,
        subobject_ref=subobject_ref,
        item_id=item_id,
        world=world,
        state=state,
        geometry_records=geometry_records,
        claim_refs=normalized_claims,
        uncertainty_refs=normalized_uncertainty,
    )

    return {
        "item_id": item_id,
        "object_ref": object_ref,
        "object_type": object_type,
        "subobject_ref": subobject_ref,
        "render_role": role,
        "temporal_membership": membership,
        "spatial_status": spatial_status,
        "geometry_refs": geometry_refs,
        "place_ref": place_ref,
        "layer_refs": _uniq(layer_refs),
        "claim_refs": normalized_claims,
        "uncertainty_refs": normalized_uncertainty,
        "evidence_link_refs": evidence_refs,
        "source_refs": source_refs,
        "semantic_flags": semantic_flags,
    }, losses


def _referenced_entity_ids(state: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    selection = state.get("selection") or {}
    context = state.get("context") or {}
    comparison = state.get("comparison_scope") or {}

    for key in ("selected_object_refs", "comparison_object_refs"):
        refs.update(_uniq(selection.get(key) or []))
    if selection.get("primary_object_ref"):
        refs.add(str(selection["primary_object_ref"]))
    refs.update(_uniq(context.get("local_context_refs") or []))
    refs.update(_uniq(context.get("global_context_refs") or []))
    refs.update(_uniq(comparison.get("reference_refs") or []))
    return refs


def _semantic_flags(**overrides: Any) -> dict[str, Any]:
    flags: dict[str, Any] = {
        "segment_kind": None,
        "reconstruction_mode": None,
        "is_primary": None,
        "state_kind": None,
        "process_mode": None,
    }
    flags.update(overrides)
    return flags


def build_projection(
    world: dict[str, Any], state: dict[str, Any], schema: dict[str, Any]
) -> dict[str, Any]:
    explorer_errors = validate_state(
        state,
        schema=_load(ROOT / "fixtures" / "explorer_state" / "v1" / "schema.json"),
        world=world,
    )
    if explorer_errors:
        raise ProjectionError("invalid Explorer State: " + "; ".join(explorer_errors))

    world_slice = world.get("world_slice") or {}
    if (
        state["world_slice_ref"] != world_slice.get("id")
        or state["dataset_identity"] != world_slice.get("dataset_identity")
    ):
        raise ProjectionError("World Slice / Explorer State identity mismatch")

    active_layers = set(_uniq(state.get("active_layer_refs") or []))
    claims, evidence = _claim_indexes(world)
    geometry_records: dict[str, dict[str, Any]] = {}
    items: list[dict[str, Any]] = []
    losses: list[dict[str, Any]] = []
    active_refs: set[str] = set()
    possible_refs: set[str] = set()
    context_refs: set[str] = set()

    def add(item: dict[str, Any], item_losses: list[dict[str, Any]]) -> None:
        items.append(item)
        losses.extend(item_losses)
        membership = item["temporal_membership"]
        if membership == "active":
            active_refs.add(item["object_ref"])
        elif membership == "possible_active":
            possible_refs.add(item["object_ref"])
        else:
            context_refs.add(item["object_ref"])

    referenced = _referenced_entity_ids(state)
    for entity in world.get("entities", []):
        entity_id = str(entity["id"])
        if entity_id not in referenced:
            continue
        layers = set(_uniq(entity.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue

        item, item_losses = _make_item(
            role="entity_context",
            object_ref=entity_id,
            object_type="Entity",
            subobject_ref=None,
            membership="atemporal_context",
            layer_refs=entity.get("layer_refs") or [],
            claim_refs=entity.get("claim_refs") or [],
            uncertainty_refs=entity.get("uncertainty_refs") or [],
            spatial_extent=entity.get("spatial_extent"),
            semantic_flags=_semantic_flags(),
            world=world,
            state=state,
            geometry_records=geometry_records,
            claims=claims,
            evidence=evidence,
        )
        if (
            str(entity.get("entity_kind") or "") == "Place"
            and not entity.get("spatial_extent")
        ):
            item["spatial_status"] = "unresolved"
            item["place_ref"] = entity_id
            item_losses = [
                _unresolved_loss(
                    item_id=item["item_id"],
                    reason="place_entity_without_resolved_geometry",
                    place_ref=entity_id,
                )
            ]
        add(item, item_losses)

    for event in world.get("events", []):
        layers = set(_uniq(event.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue
        membership = temporal_membership(event.get("temporal_extent"), state)
        if membership is None:
            continue
        item, item_losses = _make_item(
            role="event",
            object_ref=str(event["id"]),
            object_type="Event",
            subobject_ref=None,
            membership=membership,
            layer_refs=event.get("layer_refs") or [],
            claim_refs=event.get("claim_refs") or [],
            uncertainty_refs=event.get("uncertainty_refs") or [],
            spatial_extent=event.get("spatial_extent"),
            semantic_flags=_semantic_flags(),
            world=world,
            state=state,
            geometry_records=geometry_records,
            claims=claims,
            evidence=evidence,
        )

        add(item, item_losses)

    for state_obj in world.get("states", []):
        layers = set(_uniq(state_obj.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue
        membership = temporal_membership(state_obj.get("temporal_extent"), state)
        if membership is None:
            continue
        item, item_losses = _make_item(
            role="state",
            object_ref=str(state_obj["id"]),
            object_type="State",
            subobject_ref=None,
            membership=membership,
            layer_refs=state_obj.get("layer_refs") or [],
            claim_refs=state_obj.get("claim_refs") or [],
            uncertainty_refs=state_obj.get("uncertainty_refs") or [],
            spatial_extent=state_obj.get("spatial_extent"),
            semantic_flags=_semantic_flags(
                state_kind=str(state_obj.get("state_kind") or "") or None
            ),
            world=world,
            state=state,
            geometry_records=geometry_records,
            claims=claims,
            evidence=evidence,
        )
        add(item, item_losses)

    for process in world.get("processes", []):
        layers = set(_uniq(process.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue
        process_membership = temporal_membership(process.get("temporal_extent"), state)
        if process_membership is None:
            continue
        stages = process.get("stages", [])
        if not stages:
            item, item_losses = _make_item(
                role="process_stage",
                object_ref=str(process["id"]),
                object_type="Process",
                subobject_ref=None,
                membership=process_membership,
                layer_refs=process.get("layer_refs") or [],
                claim_refs=process.get("claim_refs") or [],
                uncertainty_refs=process.get("uncertainty_refs") or [],
                spatial_extent=process.get("spatial_extent"),
                semantic_flags=_semantic_flags(
                    process_mode=str(process.get("process_mode") or "") or None
                ),
                world=world,
                state=state,
                geometry_records=geometry_records,
                claims=claims,
                evidence=evidence,
            )
            add(item, item_losses)
        for stage in stages:
            membership = temporal_membership(stage.get("temporal_extent"), state)
            if membership is None:
                continue
            item, item_losses = _make_item(
                role="process_stage",
                object_ref=str(process["id"]),
                object_type="Process",
                subobject_ref=str(stage["id"]),
                membership=membership,
                layer_refs=process.get("layer_refs") or [],
                claim_refs=stage.get("claim_refs") or [],
                uncertainty_refs=process.get("uncertainty_refs") or [],
                spatial_extent=stage.get("spatial_extent"),
                semantic_flags=_semantic_flags(
                    process_mode=str(process.get("process_mode") or "") or None
                ),
                world=world,
                state=state,
                geometry_records=geometry_records,
                claims=claims,
                evidence=evidence,
            )
            add(item, item_losses)

    for trajectory in world.get("trajectories", []):
        layers = set(_uniq(trajectory.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue
        for segment in trajectory.get("segments", []):
            membership = temporal_membership(segment.get("temporal_extent"), state)
            if membership is None:
                continue
            item, item_losses = _make_item(
                role="trajectory_segment",
                object_ref=str(trajectory["id"]),
                object_type="Trajectory",
                subobject_ref=str(segment["id"]),
                membership=membership,
                layer_refs=trajectory.get("layer_refs") or [],
                claim_refs=segment.get("claim_refs") or [],
                uncertainty_refs=_uniq(
                    (trajectory.get("uncertainty_refs") or [])
                    + (segment.get("uncertainty_refs") or [])
                ),
                spatial_extent=segment.get("spatial_extent"),
                semantic_flags=_semantic_flags(
                    segment_kind=str(segment.get("segment_kind") or "") or None
                ),
                world=world,
                state=state,
                geometry_records=geometry_records,
                claims=claims,
                evidence=evidence,
            )
            add(item, item_losses)

    for region in world.get("regions", []):
        layers = set(_uniq(region.get("layer_refs") or []))
        if layers and not layers.intersection(active_layers):
            continue
        for version in region.get("geometry_versions", []):
            membership = temporal_membership(version.get("temporal_extent"), state)
            if membership is None:
                continue
            if (
                not version.get("is_primary")
                and not state["epistemic_display"].get("show_alternatives")
                and version.get("id")
                != state.get("active_focus", {}).get("region_geometry_ref")
            ):
                continue

            spatial_extent = version.get("spatial_extent") or {}
            if not isinstance(spatial_extent.get("geometry"), dict):
                item, item_losses = _make_item(
                    role="region_geometry",
                    object_ref=str(region["id"]),
                    object_type="Region",
                    subobject_ref=str(version["id"]),
                    membership=membership,
                    layer_refs=region.get("layer_refs") or [],
                    claim_refs=version.get("claim_refs") or [],
                    uncertainty_refs=_uniq(
                        (region.get("uncertainty_refs") or [])
                        + (version.get("uncertainty_refs") or [])
                    ),
                    spatial_extent=spatial_extent,
                    semantic_flags=_semantic_flags(
                        reconstruction_mode=str(
                            version.get("reconstruction_mode") or "unknown"
                        ),
                        is_primary=bool(version.get("is_primary")),
                    ),
                    world=world,
                    state=state,
                    geometry_records=geometry_records,
                    claims=claims,
                    evidence=evidence,
                )
                add(item, item_losses)
                continue

            geometry_ref = _ensure_geometry_record(
                geometry_records,
                owner_ref=str(region["id"]),
                owner_subobject_ref=str(version["id"]),
                spatial_extent=spatial_extent,
                origin_kind="region_geometry_version",
                claim_refs=version.get("claim_refs") or [],
                uncertainty_refs=_uniq(
                    (region.get("uncertainty_refs") or [])
                    + (version.get("uncertainty_refs") or [])
                ),
                reconstruction_mode=str(
                    version.get("reconstruction_mode") or "unknown"
                ),
                is_primary=bool(version.get("is_primary")),
            )
            normalized_claims, normalized_uncertainty, evidence_refs, source_refs = (
                _epistemic_refs(
                    version.get("claim_refs") or [],
                    _uniq(
                        (region.get("uncertainty_refs") or [])
                        + (version.get("uncertainty_refs") or [])
                    ),
                    claims,
                    evidence,
                )
            )
            item = {
                "item_id": _item_id(
                    "region_geometry", str(region["id"]), str(version["id"])
                ),
                "object_ref": str(region["id"]),
                "object_type": "Region",
                "subobject_ref": str(version["id"]),
                "render_role": "region_geometry",
                "temporal_membership": membership,
                "spatial_status": "resolved",
                "geometry_refs": [geometry_ref],
                "place_ref": None,
                "layer_refs": _uniq(region.get("layer_refs") or []),
                "claim_refs": normalized_claims,
                "uncertainty_refs": normalized_uncertainty,
                "evidence_link_refs": evidence_refs,
                "source_refs": source_refs,
                "semantic_flags": _semantic_flags(
                    reconstruction_mode=str(
                        version.get("reconstruction_mode") or "unknown"
                    ),
                    is_primary=bool(version.get("is_primary")),
                ),
            }
            add(item, [])

    projection = {
        "schema_version": SCHEMA_VERSION,
        "projection_id": f"render-projection:{state['state_id']}",
        "source": {
            "world_slice_ref": state["world_slice_ref"],
            "dataset_identity": copy.deepcopy(state["dataset_identity"]),
            "explorer_state_ref": state["state_id"],
        },
        "temporal_selection": copy.deepcopy(state["temporal_selection"]),
        "coordinate_reference": "EPSG:4326",
        "vertical_semantics": "not_modeled",
        "included_object_types": INCLUDED_TYPES,
        "deferred_object_types": DEFERRED_TYPES,
        "active_object_refs": sorted(active_refs),
        "possible_active_object_refs": sorted(possible_refs - active_refs),
        "context_object_refs": sorted(context_refs),
        "geometries": sorted(
            geometry_records.values(), key=lambda item: item["geometry_ref"]
        ),
        "items": sorted(items, key=lambda item: item["item_id"]),
        "losses": sorted(losses, key=lambda item: item["loss_id"]),
        "coverage": {
            "coverage_manifest_ref": world_slice.get("coverage_manifest_ref"),
            "coverage_policy": copy.deepcopy(world_slice.get("coverage_policy") or {}),
        },
    }

    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(projection),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in schema_errors
        )
        raise ProjectionError(f"projection schema validation failed: {details}")

    return projection


def _geometry_lookup(projection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["geometry_ref"]): item for item in projection.get("geometries", [])
    }


def _adapter_instances(
    projection: dict[str, Any],
    *,
    supported_geometry_types: set[str],
) -> tuple[
    list[tuple[dict[str, Any], dict[str, Any], str]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    geometries = _geometry_lookup(projection)
    instances: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    unresolved: list[dict[str, Any]] = []
    non_spatial: list[dict[str, Any]] = []

    for item in projection.get("items", []):
        status = item["spatial_status"]
        if status != "resolved":
            row = {
                "item_id": item["item_id"],
                "object_ref": item["object_ref"],
                "subobject_ref": item["subobject_ref"],
                "spatial_status": status,
            }
            if status == "unresolved":
                unresolved.append(row)
            elif status == "not_spatial":
                non_spatial.append(row)
            else:
                raise ProjectionError(f"unknown spatial_status: {status!r}")
            continue

        for geometry_ref in item.get("geometry_refs", []):
            geometry_record = geometries.get(geometry_ref)
            if geometry_record is None:
                raise ProjectionError(
                    f"item references missing projection geometry: {geometry_ref}"
                )
            geometry_type = geometry_record["geometry"].get("type")
            if geometry_type not in supported_geometry_types:
                raise ProjectionError(
                    "renderer_capability: adapter cannot represent material geometry "
                    f"{geometry_type!r} for {item['item_id']}"
                )
            instance_id = (
                item["item_id"]
                if len(item.get("geometry_refs", [])) == 1
                else f"{item['item_id']}:{geometry_ref}"
            )
            instances.append((item, geometry_record, instance_id))

    instances.sort(key=lambda value: value[2])
    unresolved.sort(key=lambda value: value["item_id"])
    non_spatial.sort(key=lambda value: value["item_id"])
    return instances, unresolved, non_spatial


def _adapter_semantics(
    item: dict[str, Any], geometry_record: dict[str, Any]
) -> dict[str, Any]:
    return {
        "item_id": item["item_id"],
        "object_ref": item["object_ref"],
        "object_type": item["object_type"],
        "subobject_ref": item["subobject_ref"],
        "render_role": item["render_role"],
        "temporal_membership": item["temporal_membership"],
        "layer_refs": item["layer_refs"],
        "claim_refs": item["claim_refs"],
        "uncertainty_refs": item["uncertainty_refs"],
        "evidence_link_refs": item["evidence_link_refs"],
        "source_refs": item["source_refs"],
        "geometry_ref": geometry_record["geometry_ref"],
        "geometry_claim_refs": geometry_record["claim_refs"],
        "geometry_uncertainty_refs": geometry_record["uncertainty_refs"],
        "geometry_reconstruction_mode": geometry_record.get("reconstruction_mode"),
        "geometry_is_primary": geometry_record.get("is_primary"),
        "semantic_flags": item["semantic_flags"],
    }


def to_maplibre(
    projection: dict[str, Any],
    *,
    supported_geometry_types: set[str] | None = None,
) -> dict[str, Any]:
    supported = supported_geometry_types or set(SUPPORTED_GEOMETRIES)
    instances, unresolved, non_spatial = _adapter_instances(
        projection, supported_geometry_types=supported
    )

    features: list[dict[str, Any]] = []
    for item, geometry_record, instance_id in instances:
        features.append(
            {
                "type": "Feature",
                "id": instance_id,
                "geometry": copy.deepcopy(geometry_record["geometry"]),
                "properties": _adapter_semantics(item, geometry_record),
            }
        )

    return {
        "type": "FeatureCollection",
        "schema_version": SCHEMA_VERSION,
        "adapter_kind": "maplibre_geojson",
        "projection_id": projection["projection_id"],
        "source": copy.deepcopy(projection["source"]),
        "features": features,
        "unresolved_items": unresolved,
        "non_spatial_items": non_spatial,
    }


def to_globe(
    projection: dict[str, Any],
    *,
    supported_geometry_types: set[str] | None = None,
) -> dict[str, Any]:
    supported = supported_geometry_types or set(SUPPORTED_GEOMETRIES)
    instances, unresolved, non_spatial = _adapter_instances(
        projection, supported_geometry_types=supported
    )
    kind_map = {
        "Point": "cartographic_point",
        "LineString": "cartographic_polyline",
        "Polygon": "cartographic_polygon",
        "MultiPolygon": "cartographic_multipolygon",
    }

    primitives: list[dict[str, Any]] = []
    for item, geometry_record, instance_id in instances:
        geometry = geometry_record["geometry"]
        primitives.append(
            {
                "primitive_id": instance_id,
                "primitive_kind": kind_map[geometry["type"]],
                "coordinates": copy.deepcopy(geometry["coordinates"]),
                **_adapter_semantics(item, geometry_record),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "adapter_kind": "globe_cartographic",
        "projection_id": projection["projection_id"],
        "source": copy.deepcopy(projection["source"]),
        "coordinate_reference": projection["coordinate_reference"],
        "vertical_semantics": projection["vertical_semantics"],
        "primitives": primitives,
        "unresolved_items": unresolved,
        "non_spatial_items": non_spatial,
    }


def assert_adapter_preservation(
    maplibre: dict[str, Any], globe: dict[str, Any]
) -> None:
    map_rows = {
        str(feature["id"]): feature["properties"]
        for feature in maplibre.get("features", [])
    }
    globe_rows = {
        str(primitive["primitive_id"]): primitive
        for primitive in globe.get("primitives", [])
    }
    if set(map_rows) != set(globe_rows):
        raise ProjectionError("adapter identity drift: rendered instance IDs differ")

    fields = {
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
    }
    for instance_id in sorted(map_rows):
        for field in fields:
            if map_rows[instance_id].get(field) != globe_rows[instance_id].get(field):
                raise ProjectionError(
                    f"adapter semantic drift for {instance_id}: field {field} differs"
                )

    if maplibre.get("unresolved_items") != globe.get("unresolved_items"):
        raise ProjectionError("adapter semantic drift: unresolved item sets differ")
    if maplibre.get("non_spatial_items") != globe.get("non_spatial_items"):
        raise ProjectionError("adapter semantic drift: non-spatial item sets differ")


def build_all(
    world: dict[str, Any], state: dict[str, Any], schema: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    projection = build_projection(world, state, schema)
    maplibre = to_maplibre(projection)
    globe = to_globe(projection)
    assert_adapter_preservation(maplibre, globe)
    return projection, maplibre, globe


def _write(path: Path, value: Any) -> None:
    path.write_text(_canonical(value), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="write derived projection/adapters for local inspection only",
    )
    args = parser.parse_args()

    try:
        projection, maplibre, globe = build_all(
            _load(WORLD_PATH), _load(STATE_PATH), _load(SCHEMA_PATH)
        )
        if args.write:
            _write(PROJECTION_PATH, projection)
            _write(MAPLIBRE_PATH, maplibre)
            _write(GLOBE_PATH, globe)
        print(
            "[PASS] Render Projection v1: "
            f"items={len(projection['items'])}; "
            f"geometries={len(projection['geometries'])}; "
            f"losses={len(projection['losses'])}; "
            f"map_features={len(maplibre['features'])}; "
            f"globe_primitives={len(globe['primitives'])}"
        )
        return 0
    except (ProjectionError, KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
