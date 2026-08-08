import copy
import json
from pathlib import Path

import pytest

from scripts.build_render_projection_fixtures import (
    ProjectionError,
    assert_adapter_preservation,
    build_all,
    build_projection,
    to_globe,
    to_maplibre,
)


ROOT = Path(__file__).resolve().parents[1]
WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
SCHEMA_PATH = ROOT / "fixtures" / "render_projection" / "v1" / "schema.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _build():
    return build_all(_load(WORLD_PATH), _load(STATE_PATH), _load(SCHEMA_PATH))


def _item(projection, item_id):
    return next(item for item in projection["items"] if item["item_id"] == item_id)


def _geometry(projection, geometry_ref):
    return next(item for item in projection["geometries"] if item["geometry_ref"] == geometry_ref)


def test_same_inputs_build_neutral_maplibre_and_globe_payloads() -> None:
    projection, maplibre, globe = _build()

    assert projection["source"]["world_slice_ref"] == "world-slice-fixture-basin-v1"
    assert projection["source"]["explorer_state_ref"] == "explorer-state-1504-local-global"
    assert projection["vertical_semantics"] == "not_modeled"
    assert projection["deferred_object_types"] == ["Relation"]
    assert maplibre["adapter_kind"] == "maplibre_geojson"
    assert globe["adapter_kind"] == "globe_cartographic"
    assert globe["vertical_semantics"] == "not_modeled"

    assert_adapter_preservation(maplibre, globe)


def test_explicit_point_geometry_is_preserved_for_both_adapters() -> None:
    projection, maplibre, globe = _build()
    item = _item(projection, "rp:event:event-far-observation")

    assert item["spatial_status"] == "resolved"
    assert item["geometry_refs"] == ["geom:event-far-observation"]
    geometry = _geometry(projection, "geom:event-far-observation")
    assert geometry["geometry"] == {"type": "Point", "coordinates": [100.0, -20.0]}

    map_feature = next(
        feature for feature in maplibre["features"]
        if feature["properties"]["item_id"] == item["item_id"]
    )
    globe_primitive = next(
        primitive for primitive in globe["primitives"]
        if primitive["item_id"] == item["item_id"]
    )
    assert map_feature["geometry"] == geometry["geometry"]
    assert globe_primitive["primitive_kind"] == "cartographic_point"
    assert globe_primitive["coordinates"] == [100.0, -20.0]


def test_named_place_without_canonical_geometry_stays_unresolved() -> None:
    projection, maplibre, globe = _build()
    meeting = _item(projection, "rp:event:event-documented-workshop-meeting")

    assert meeting["place_ref"] == "place-inland-workshop"
    assert meeting["spatial_status"] == "unresolved"
    assert meeting["geometry_refs"] == []
    assert any(
        loss["item_id"] == meeting["item_id"]
        and loss["reason"] == "named_place_without_resolved_geometry"
        for loss in projection["losses"]
    )
    assert all(
        feature["properties"]["item_id"] != meeting["item_id"]
        for feature in maplibre["features"]
    )
    assert all(
        primitive["item_id"] != meeting["item_id"]
        for primitive in globe["primitives"]
    )
    assert any(row["item_id"] == meeting["item_id"] for row in maplibre["unresolved_items"])
    assert any(row["item_id"] == meeting["item_id"] for row in globe["unresolved_items"])


def test_unknown_trajectory_gap_never_becomes_a_line() -> None:
    projection, maplibre, globe = _build()
    gap = _item(projection, "rp:trajectory_segment:trajectory-mara-vale:trajectory-segment-gap")

    assert gap["semantic_flags"]["segment_kind"] == "inferred_gap"
    assert gap["spatial_status"] == "unresolved"
    assert gap["geometry_refs"] == []
    assert any(
        loss["item_id"] == gap["item_id"] and loss["reason"] == "unknown_spatial_extent"
        for loss in projection["losses"]
    )
    assert all(feature["properties"]["item_id"] != gap["item_id"] for feature in maplibre["features"])
    assert all(primitive["item_id"] != gap["item_id"] for primitive in globe["primitives"])


def test_region_primary_and_alternative_reconstructions_survive() -> None:
    projection, maplibre, globe = _build()
    primary = _geometry(projection, "geom:region-fixture-basin:region-geometry-v2")
    alternative = _geometry(projection, "geom:region-fixture-basin:region-geometry-v2-alt")

    assert primary["reconstruction_mode"] == "documented_reconstruction"
    assert primary["is_primary"] is True
    assert alternative["reconstruction_mode"] == "documented_alternative"
    assert alternative["is_primary"] is False
    assert primary["geometry"] != alternative["geometry"]

    state_item = _item(projection, "rp:state:state-north-harbor-administration")
    assert set(state_item["geometry_refs"]) >= {
        primary["geometry_ref"],
        alternative["geometry_ref"],
    }

    map_modes = {
        feature["properties"]["geometry_reconstruction_mode"]
        for feature in maplibre["features"]
        if feature["properties"]["item_id"] == state_item["item_id"]
    }
    globe_modes = {
        primitive["geometry_reconstruction_mode"]
        for primitive in globe["primitives"]
        if primitive["item_id"] == state_item["item_id"]
    }
    assert map_modes == {"documented_reconstruction", "documented_alternative"}
    assert globe_modes == map_modes


def test_evidence_sources_and_uncertainty_survive_projection() -> None:
    projection, maplibre, globe = _build()
    event_item = _item(projection, "rp:event:event-far-observation")

    assert event_item["claim_refs"] == ["claim-far-observation"]
    assert event_item["evidence_link_refs"] == ["evidence-far-observation"]
    assert event_item["source_refs"] == ["source-field-notebook-beta"]

    primary_region_item = _item(
        projection,
        "rp:region_geometry:region-fixture-basin:region-geometry-v2",
    )
    assert "uncertainty-region-boundary" in primary_region_item["uncertainty_refs"]

    map_row = next(
        feature["properties"] for feature in maplibre["features"]
        if feature["properties"]["item_id"] == primary_region_item["item_id"]
    )
    globe_row = next(
        primitive for primitive in globe["primitives"]
        if primitive["item_id"] == primary_region_item["item_id"]
    )
    assert map_row["source_refs"] == globe_row["source_refs"]
    assert map_row["uncertainty_refs"] == globe_row["uncertainty_refs"]
    assert map_row["geometry_claim_refs"] == globe_row["geometry_claim_refs"]


def test_approximate_temporal_alternative_is_not_promoted_to_active_fact() -> None:
    projection, _, _ = _build()
    arrival = _item(projection, "rp:event:event-workshop-arrival")
    assert arrival["temporal_membership"] == "possible_active"


def test_relation_objects_are_explicitly_deferred_from_projection_v1() -> None:
    projection, _, _ = _build()
    assert projection["deferred_object_types"] == ["Relation"]
    assert all(item["object_type"] != "Relation" for item in projection["items"])


def test_adapter_capability_loss_fails_closed() -> None:
    projection, _, _ = _build()
    with pytest.raises(ProjectionError, match="renderer_capability"):
        to_globe(projection, supported_geometry_types={"Point"})
    with pytest.raises(ProjectionError, match="renderer_capability"):
        to_maplibre(projection, supported_geometry_types={"Point"})


def test_explicit_path_is_supported_but_not_synthesized() -> None:
    world = _load(WORLD_PATH)
    state = _load(STATE_PATH)
    schema = _load(SCHEMA_PATH)
    world["events"].append(
        {
            "id": "event-explicit-path-fixture",
            "type": "Event",
            "label": "Explicit path fixture",
            "temporal_extent": {
                "kind": "instant",
                "start": "1504-03-01",
                "end": "1504-03-01",
                "precision": "day",
                "certainty": "documented",
                "basis_claim_refs": []
            },
            "spatial_extent": {
                "kind": "path",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[10.0, 20.0], [11.0, 21.0]]
                },
                "precision": "fixture_defined",
                "basis_claim_refs": []
            },
            "participant_refs": [],
            "claim_refs": [],
            "uncertainty_refs": [],
            "layer_refs": ["layer-exchange"]
        }
    )

    projection = build_projection(world, state, schema)
    item = _item(projection, "rp:event:event-explicit-path-fixture")
    assert item["geometry_refs"] == ["geom:event-explicit-path-fixture"]
    assert _geometry(projection, item["geometry_refs"][0])["geometry"]["type"] == "LineString"

    maplibre = to_maplibre(projection)
    globe = to_globe(projection)
    map_feature = next(
        feature for feature in maplibre["features"]
        if feature["properties"]["item_id"] == item["item_id"]
    )
    globe_primitive = next(
        primitive for primitive in globe["primitives"]
        if primitive["item_id"] == item["item_id"]
    )
    assert map_feature["geometry"]["type"] == "LineString"
    assert globe_primitive["primitive_kind"] == "cartographic_polyline"


def test_world_slice_identity_drift_is_rejected_before_projection() -> None:
    world = _load(WORLD_PATH)
    state = _load(STATE_PATH)
    state["dataset_identity"]["value"] = "wrong-dataset"

    with pytest.raises(ProjectionError, match="invalid Explorer State|identity mismatch"):
        build_projection(world, state, _load(SCHEMA_PATH))


def test_globe_v1_never_adds_vertical_history() -> None:
    _, _, globe = _build()
    assert globe["vertical_semantics"] == "not_modeled"
    payload = json.dumps(globe, sort_keys=True).lower()
    assert '"height"' not in payload
    assert '"altitude"' not in payload
    assert '"terrain_height"' not in payload
