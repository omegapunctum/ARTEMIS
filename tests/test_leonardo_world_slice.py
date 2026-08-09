import copy
import json
from pathlib import Path

import pytest

from scripts.validate_leonardo_world_slice import (
    CLAIMS_PATH,
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


def _claims():
    return _load(CLAIMS_PATH)


def test_scope_frozen_package_passes_fail_closed_validation() -> None:
    summary = validate_package()
    assert summary == {
        "slice_id": "world-slice-leonardo-romagna-1502-v1",
        "status": "SCOPE_FROZEN",
        "candidate_object_count": 17,
        "source_count": 10,
        "known_gap_count": 6,
        "trajectory_gap_count": 3,
        "region_version_count": 2,
        "claim_count": 21,
        "evidence_link_count": 37,
        "uncertainty_count": 10,
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


def test_scope_cannot_silently_expand_back_to_florence_or_1504() -> None:
    selection, sources, coverage, cost = _baseline()
    selection["temporal_scope"]["end"] = "1504-12-31"
    selection["spatial_scope"]["focus_place_refs"].append("place-florence")

    with pytest.raises(WorldSliceScopeError, match="schema validation failed"):
        validate_package(selection, sources, coverage, cost)


def test_all_inter_place_gaps_are_explicit_and_evidence_free() -> None:
    selection, sources, coverage, cost = _baseline()
    trajectory = next(
        row for row in selection["candidate_objects"] if row["object_type"] == "Trajectory"
    )
    gaps = [row for row in trajectory["segments"] if row["segment_kind"] == "inferred_gap"]

    assert len(gaps) == 3
    assert all(row["spatial_mode"] == "unknown_route" for row in gaps)
    assert all(row["geometry"] is None for row in gaps)
    assert all(row["source_refs"] == [] for row in gaps)


def test_unknown_route_gap_cannot_claim_route_evidence() -> None:
    selection, sources, coverage, cost = _baseline()
    trajectory = next(
        row for row in selection["candidate_objects"] if row["object_type"] == "Trajectory"
    )
    gap = next(row for row in trajectory["segments"] if row["segment_kind"] == "inferred_gap")
    gap["source_refs"] = ["source-visit-romagna-leonardo-borgia"]

    with pytest.raises(WorldSliceScopeError, match="cannot pretend to have route evidence"):
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


def test_region_versions_require_temporal_claim_binding() -> None:
    selection, sources, coverage, cost = _baseline()
    region = next(
        row for row in selection["candidate_objects"] if row["object_type"] == "Region"
    )
    del region["versions"][0]["temporal_hint"]

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


def test_rct_rights_cannot_silently_allow_derived_geometry() -> None:
    selection, sources, coverage, cost = _baseline()
    rct = next(row for row in sources["sources"] if row["source_id"] == "source-rct-imola-map")
    rct["rights"]["derived_geometry_use"] = "permitted"

    with pytest.raises(WorldSliceScopeError, match="cannot authorize derived geometry"):
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


def test_draft_evidence_cannot_masquerade_as_supported() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["claims"][0]["evidence_state"] = "supported"

    with pytest.raises(WorldSliceScopeError, match="must derive from reviewed EvidenceLinks"):
        validate_package(selection, sources, coverage, cost, claims)


def test_evidence_link_cannot_escape_its_atomic_claim() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["evidence_links"][0]["claim_id"] = "claim-cesena-presence-1502-08-10"

    with pytest.raises(WorldSliceScopeError, match="bound to another Claim"):
        validate_package(selection, sources, coverage, cost, claims)


def test_reviewed_evidence_requires_named_reviewer() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    evidence = claims["evidence_links"][0]
    evidence["review_state"] = "reviewed"
    evidence["reviewer"] = None
    claims["claims"][0]["evidence_state"] = "supported"

    with pytest.raises(WorldSliceScopeError, match="requires a reviewer"):
        validate_package(selection, sources, coverage, cost, claims)


def test_dated_cesenatico_locator_cannot_regress_to_separate_folio_68r() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    evidence = next(
        row
        for row in claims["evidence_links"]
        if row["evidence_link_id"] == "evidence-cesenatico-folio-66v-uniurb"
    )
    evidence["locator"] = evidence["locator"].replace("66v", "68r")

    with pytest.raises(WorldSliceScopeError, match="critical locator text drifted"):
        validate_package(selection, sources, coverage, cost, claims)


def test_patent_critical_transcription_locator_cannot_be_removed() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["evidence_links"] = [
        row
        for row in claims["evidence_links"]
        if row["evidence_link_id"] != "evidence-patent-uniurb-p16-n26"
    ]
    patent_claim = next(
        row for row in claims["claims"] if row["claim_id"] == "claim-patent-date-1502-08-18"
    )
    patent_claim["evidence_link_refs"].remove("evidence-patent-uniurb-p16-n26")

    with pytest.raises(WorldSliceScopeError, match="critical locator EvidenceLink is missing"):
        validate_package(selection, sources, coverage, cost, claims)


def test_cesena_wall_folios_remain_traceable_but_rejected_from_supported_scope() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    wall_claim = next(
        row for row in claims["claims"] if row["claim_id"] == "claim-cesena-survey-folios-9r-10r"
    )

    assert wall_claim["review_state"] == "rejected"
    assert wall_claim["evidence_state"] == "missing"
    assert wall_claim["confidence"] == "low"

    wall_claim["confidence"] = "unknown"
    with pytest.raises(WorldSliceScopeError, match="must remain rejected and unsupported"):
        validate_package(selection, sources, coverage, cost, claims)


def test_claim_target_must_stay_inside_frozen_scope() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["claims"][0]["target_object_ref"] = "event-florence-outside-scope"

    with pytest.raises(WorldSliceScopeError, match="unknown candidate object"):
        validate_package(selection, sources, coverage, cost, claims)


def test_every_candidate_object_requires_an_atomic_claim_binding() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["claims"] = [
        row for row in claims["claims"] if row["target_object_ref"] != "process-leonardo-romagna-surveying"
    ]
    claims["evidence_links"] = [
        row
        for row in claims["evidence_links"]
        if row["claim_id"] != "claim-romagna-survey-process-analytical-grouping"
    ]
    claims["uncertainties"] = [
        row
        for row in claims["uncertainties"]
        if row["uncertainty_id"] != "uncertainty-process-analytical-grouping"
    ]
    uniurb = next(
        row for row in sources["sources"] if row["source_id"] == "source-uniurb-volpe-chronology"
    )
    uniurb["intended_claims"].remove("claim-romagna-survey-process-analytical-grouping")

    with pytest.raises(WorldSliceScopeError, match="requires an atomic Claim binding"):
        validate_package(selection, sources, coverage, cost, claims)


def test_uncertainty_requires_explicit_provenance_basis() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    uncertainty = claims["uncertainties"][0]
    uncertainty["basis_kind"] = "claim_refs"
    uncertainty["basis_claim_refs"] = []

    with pytest.raises(WorldSliceScopeError, match="requires at least one basis Claim"):
        validate_package(selection, sources, coverage, cost, claims)


def test_orphan_uncertainty_is_rejected() -> None:
    selection, sources, coverage, cost = _baseline()
    claims = _claims()
    claims["claims"] = [
        {
            **row,
            "uncertainty_refs": [
                ref
                for ref in row["uncertainty_refs"]
                if ref != "uncertainty-global-event-year-precision"
            ],
        }
        for row in claims["claims"]
    ]

    with pytest.raises(WorldSliceScopeError, match="not reciprocally bound"):
        validate_package(selection, sources, coverage, cost, claims)


def test_scope_requires_one_source_bound_global_event() -> None:
    selection, sources, coverage, cost = _baseline()
    event = next(
        row
        for row in selection["candidate_objects"]
        if row["object_id"] == "event-ottoman-turkmen-displacement-1502"
    )
    event["layer_refs"] = ["layer-local-context"]

    with pytest.raises(WorldSliceScopeError, match="exactly one source-bound global Event"):
        validate_package(selection, sources, coverage, cost)


def test_region_requires_both_explicit_reconstruction_alternatives() -> None:
    selection, sources, coverage, cost = _baseline()
    region = next(row for row in selection["candidate_objects"] if row["object_type"] == "Region")
    region["versions"][1]["reconstruction_mode"] = "title_based_context"

    with pytest.raises(WorldSliceScopeError, match="both explicit reconstruction alternatives"):
        validate_package(selection, sources, coverage, cost)
