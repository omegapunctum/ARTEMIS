import copy
import json
from pathlib import Path

import pytest

from scripts.validate_renderer_parity import (
    EXPECTED_PATH,
    NEGATIVE_CASES_PATH,
    ParityError,
    apply_negative_case,
    assert_parity,
    build_baseline,
    renderer_envelope,
    validate_all,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_baseline_cross_renderer_contract_passes() -> None:
    summary = validate_all()
    assert summary["fixture_id"] == "artemis-cross-renderer-parity-fixture-v1"
    assert summary["item_count"] > 0
    assert summary["rendered_instance_count"] > 0
    assert summary["unresolved_count"] > 0
    assert summary["boundary_case_count"] == 2


def test_2d_and_globe_semantic_envelopes_are_identical() -> None:
    _world, state, _schema, projection, maplibre, globe = build_baseline()
    left, right = assert_parity(
        map_projection=projection,
        maplibre=maplibre,
        globe_projection=projection,
        globe=globe,
        state=state,
    )
    assert left == right
    assert left["source"]["world_slice_ref"] == "world-slice-fixture-basin-v1"
    assert left["selection"]["primary_object_ref"] == "event-documented-workshop-meeting"
    assert left["selection"] == {
        "primary_object_ref": state["selection"]["primary_object_ref"],
        "selected_object_refs": sorted(state["selection"]["selected_object_refs"]),
        "active_focus": {
            "trajectory_ref": state["active_focus"]["trajectory_ref"],
            "trajectory_segment_ref": state["active_focus"]["trajectory_segment_ref"],
            "region_ref": state["active_focus"]["region_ref"],
            "region_geometry_ref": state["active_focus"]["region_geometry_ref"],
        },
    }


def test_selected_unresolved_object_has_same_identity_for_both_renderers() -> None:
    _world, state, _schema, projection, maplibre, globe = build_baseline()
    left = renderer_envelope(
        renderer="maplibre", projection=projection, adapter=maplibre, state=state
    )
    right = renderer_envelope(
        renderer="globe", projection=projection, adapter=globe, state=state
    )

    target = "rp:event:event-documented-workshop-meeting"
    left_item = next(item for item in left["unresolved_items"] if item["item_id"] == target)
    right_item = next(item for item in right["unresolved_items"] if item["item_id"] == target)
    assert left_item == right_item
    assert left_item["object_ref"] == "event-documented-workshop-meeting"
    assert left_item["spatial_status"] == "unresolved"
    assert left_item["geometry_refs"] == []


def test_region_primary_and_alternative_semantics_match() -> None:
    _world, state, _schema, projection, maplibre, globe = build_baseline()
    left, right = assert_parity(
        map_projection=projection,
        maplibre=maplibre,
        globe_projection=projection,
        globe=globe,
        state=state,
    )

    ids = {
        "rp:region_geometry:region-fixture-basin:region-geometry-v2",
        "rp:region_geometry:region-fixture-basin:region-geometry-v2-alternative",
    }
    left_rows = {
        row["item_id"]: row for row in left["rendered_instances"] if row["item_id"] in ids
    }
    right_rows = {
        row["item_id"]: row for row in right["rendered_instances"] if row["item_id"] in ids
    }
    assert left_rows == right_rows
    assert left_rows["rp:region_geometry:region-fixture-basin:region-geometry-v2"]["geometry_is_primary"] is True
    assert left_rows["rp:region_geometry:region-fixture-basin:region-geometry-v2-alternative"]["geometry_is_primary"] is False
    assert "uncertainty-region-alternative" in left_rows["rp:region_geometry:region-fixture-basin:region-geometry-v2"]["uncertainty_refs"]


def test_trajectory_gap_remains_unresolved_and_uncertain() -> None:
    _world, state, _schema, projection, maplibre, globe = build_baseline()
    left, right = assert_parity(
        map_projection=projection,
        maplibre=maplibre,
        globe_projection=projection,
        globe=globe,
        state=state,
    )
    target = "rp:trajectory_segment:trajectory-mara-vale:trajectory-segment-gap"
    left_gap = next(item for item in left["items"] if item["item_id"] == target)
    right_gap = next(item for item in right["items"] if item["item_id"] == target)
    assert left_gap == right_gap
    assert left_gap["spatial_status"] == "unresolved"
    assert left_gap["geometry_refs"] == []
    assert left_gap["semantic_flags"]["segment_kind"] == "inferred_gap"
    assert "uncertainty-trajectory-route" in left_gap["uncertainty_refs"]


def test_renderer_only_difference_allowlist_contains_no_semantic_owners() -> None:
    expected = _load(EXPECTED_PATH)
    allowed = set(expected["renderer_only_differences"])
    forbidden_tokens = {
        "object_ref",
        "subobject_ref",
        "claim",
        "evidence",
        "source",
        "uncertainty",
        "temporal_membership",
        "region_geometry",
        "trajectory_segment",
        "relation",
        "world_slice",
        "explorer_state",
    }
    normalized = " ".join(sorted(allowed)).lower()
    assert all(token not in normalized for token in forbidden_tokens)
    assert "camera_and_orientation" in allowed
    assert "screenshot_pixels" in allowed


NEGATIVE_CASES = _load(NEGATIVE_CASES_PATH)["cases"]


@pytest.mark.parametrize("case", NEGATIVE_CASES, ids=lambda case: case["case_id"])
def test_every_negative_semantic_corruption_is_rejected(case) -> None:
    _world, state, _schema, projection, maplibre, globe = build_baseline()
    map_projection = copy.deepcopy(projection)
    globe_projection = copy.deepcopy(projection)
    mutated_maplibre = copy.deepcopy(maplibre)
    mutated_globe = copy.deepcopy(globe)

    apply_negative_case(
        case,
        map_projection=map_projection,
        maplibre=mutated_maplibre,
        globe_projection=globe_projection,
        globe=mutated_globe,
    )

    with pytest.raises(ParityError):
        assert_parity(
            map_projection=map_projection,
            maplibre=mutated_maplibre,
            globe_projection=globe_projection,
            globe=mutated_globe,
            state=state,
        )
