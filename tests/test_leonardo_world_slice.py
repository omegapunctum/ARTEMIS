import copy
import json
from pathlib import Path

import pytest

from scripts.validate_leonardo_world_slice import (
    COST_PATH,
    COVERAGE_PATH,
    SELECTION_PATH,
    SOURCE_PATH,
    WorldSliceScopeError,
    validate_package,
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline():
    return _load(SELECTION_PATH), _load(SOURCE_PATH), _load(COVERAGE_PATH), _load(COST_PATH)


def test_scope_frozen_package_passes_fail_closed_validation() -> None:
    summary = validate_package()
    assert summary == {
        "slice_id": "world-slice-leonardo-1502-1504-v1",
        "status": "SCOPE_FROZEN",
        "candidate_object_count": 11,
        "source_count": 8,
        "known_gap_count": 6,
        "trajectory_gap_count": 1,
        "region_version_count": 2,
        "promotion_allowed": False,
    }


def test_scope_cannot_claim_historical_readiness_or_promotion() -> None:
    selection, sources, coverage, cost = _baseline()
    selection["readiness"]["historical_objects_ready"] = True
    selection["readiness"]["promotion_allowed"] = True

    with pytest.raises(WorldSliceScopeError, match="schema validation failed"):
        validate_package(selection, sources, coverage, cost)


def test_unknown_trajectory_gap_rejects_invented_line_geometry() -> None:
    selection, sources, coverage, cost = _baseline()
    trajectory = next(
        row for row in selection["candidate_objects"] if row["object_type"] == "Trajectory"
    )
    gap = next(row for row in trajectory["segments"] if row["segment_kind"] == "inferred_gap")
    gap["geometry"] = {
        "type": "LineString",
        "coordinates": [[11.7, 44.35], [11.25, 43.7667]],
    }

    with pytest.raises(WorldSliceScopeError, match="schema validation failed"):
        validate_package(selection, sources, coverage, cost)


def test_candidate_region_rejects_unreviewed_polygon() -> None:
    selection, sources, coverage, cost = _baseline()
    region = next(
        row for row in selection["candidate_objects"] if row["object_type"] == "Region"
    )
    region["versions"][0]["geometry"] = {
        "type": "Polygon",
        "coordinates": [[[11.0, 43.0], [12.0, 43.0], [12.0, 44.0], [11.0, 43.0]]],
    }

    with pytest.raises(WorldSliceScopeError, match="schema validation failed"):
        validate_package(selection, sources, coverage, cost)


def test_paused_relation_gate_rejects_stored_relation() -> None:
    selection, sources, coverage, cost = _baseline()
    selection["relation_policy"]["stored_relations"].append(
        {"predicate": "influence", "subject": "entity-leonardo-da-vinci"}
    )

    with pytest.raises(WorldSliceScopeError, match="schema validation failed"):
        validate_package(selection, sources, coverage, cost)


def test_candidate_object_rejects_missing_source_reference() -> None:
    selection, sources, coverage, cost = _baseline()
    selection["candidate_objects"][0]["source_refs"] = ["source-does-not-exist"]

    with pytest.raises(WorldSliceScopeError, match="references missing sources"):
        validate_package(selection, sources, coverage, cost)


def test_rct_rights_cannot_silently_allow_image_reuse() -> None:
    selection, sources, coverage, cost = _baseline()
    rct = next(row for row in sources["sources"] if row["source_id"] == "source-rct-imola-map")
    rct["rights"]["media_reuse"] = "not_applicable"

    with pytest.raises(WorldSliceScopeError, match="cannot authorize image reuse"):
        validate_package(selection, sources, coverage, cost)


def test_getty_reference_points_keep_odc_attribution() -> None:
    selection, sources, coverage, cost = _baseline()
    getty = next(row for row in sources["sources"] if row["source_id"] == "source-getty-tgn-imola")
    getty["rights"]["license"] = None

    with pytest.raises(WorldSliceScopeError, match="must preserve Getty ODC-By 1.0 licensing"):
        validate_package(selection, sources, coverage, cost)


def test_manifest_and_coverage_gap_registries_cannot_drift() -> None:
    selection, sources, coverage, cost = _baseline()
    coverage["known_gaps"][0]["gap_id"] = "gap-unregistered-replacement"

    with pytest.raises(WorldSliceScopeError, match="must exactly match"):
        validate_package(selection, sources, coverage, cost)


def test_cost_log_cannot_mark_unmeasured_work_as_recorded() -> None:
    selection, sources, coverage, cost = _baseline()
    cost["entries"][0]["measurement_state"] = "recorded"

    with pytest.raises(WorldSliceScopeError, match="require an actual duration"):
        validate_package(selection, sources, coverage, cost)
