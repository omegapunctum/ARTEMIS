from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_airtable_leonardo_shadow_plan.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("artemis_leonardo_shadow_plan", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_row_plan_is_deterministic_and_complete() -> None:
    module = _load_builder()
    first = module.build_plan()
    second = module.build_plan()

    assert first == second
    assert module._digest(first) == module._digest(second)
    assert len(module._digest(first)) == 64
    assert first["status"] == "ROW_PLAN_CANDIDATE"
    assert first["authoritative"] is False
    assert first["target"]["gate_d_opened"] is False
    assert first["counts"] == {
        "WorldSlices": 1,
        "SliceLayers": 4,
        "WorldSources": 10,
        "KnowledgeObjects": 17,
        "ObjectParts": 11,
        "Claims": 22,
        "EvidenceLinks": 38,
        "Uncertainties": 11,
        "UncertaintyTargets": 40,
    }
    assert sum(first["counts"].values()) == 154


def test_row_plan_uses_semantic_ids_and_isolates_legacy_public_links() -> None:
    plan = _load_builder().build_plan()

    for table, rows in plan["rows"].items():
        ids = [row["stable_id"] for row in rows]
        assert len(ids) == len(set(ids)), table
        assert all(not stable_id.startswith("rec") for stable_id in ids)

    for row in plan["rows"]["KnowledgeObjects"]:
        assert row["fields"]["layers"] == []
        assert row["fields"]["slice_layers"]
    for row in plan["rows"]["EvidenceLinks"]:
        assert row["fields"]["source"] == []
        assert len(row["fields"]["world_source"]) == 1


def test_unknown_routes_and_region_geometry_remain_uninvented() -> None:
    plan = _load_builder().build_plan()
    parts = plan["rows"]["ObjectParts"]

    gaps = [row for row in parts if row["fields"]["spatial_status"] == "unknown_route"]
    assert len(gaps) == 3
    for row in gaps:
        fields = row["fields"]
        assert fields["source_kind"] == "inferred_gap"
        assert fields["source_spatial_mode"] == "unknown_route"
        assert fields["place_ref"] is None
        assert fields["geometry_ref"] is None
        assert fields["world_sources"] == []

    region_parts = [row for row in parts if row["fields"]["part_kind"] in {"region_state", "reconstruction_alternative"}]
    assert len(region_parts) == 4
    assert all(row["fields"]["spatial_status"] == "geometry_withheld" for row in region_parts)
    assert all(row["fields"]["geometry_ref"] is None for row in region_parts)


def test_source_temporal_precision_is_not_lost_by_normalization() -> None:
    plan = _load_builder().build_plan()
    objects = plan["rows"]["KnowledgeObjects"]
    parts = plan["rows"]["ObjectParts"]

    pending = [row for row in objects if row["fields"]["source_temporal_precision"] == "pending"]
    ranged = [row for row in objects if row["fields"]["source_temporal_precision"] == "range"]
    assert pending
    assert ranged
    assert all(row["fields"]["temporal_precision"] == "unresolved" for row in pending)
    assert all(row["fields"]["temporal_precision"] == "interval" for row in ranged)

    ranged_parts = [row for row in parts if row["fields"]["source_temporal_precision"] == "range"]
    assert ranged_parts
    assert all(row["fields"]["temporal_precision"] == "interval" for row in ranged_parts)


def test_rejected_claim_and_draft_sources_are_preserved_without_promotion() -> None:
    plan = _load_builder().build_plan()
    claims = {row["stable_id"]: row for row in plan["rows"]["Claims"]}

    assert claims["claim-cesena-survey-folios-9r-10r"]["fields"]["review_state"] == "rejected"
    assert all(row["fields"]["review_state"] == "draft" for row in plan["rows"]["WorldSources"])
    assert all(row["fields"]["review_state"] == "draft" for row in plan["rows"]["SliceLayers"])


def test_uncertainty_target_rows_preserve_identity_without_cloning() -> None:
    plan = _load_builder().build_plan()
    uncertainties = plan["rows"]["Uncertainties"]
    targets = plan["rows"]["UncertaintyTargets"]

    assert len(uncertainties) == 11
    assert len(targets) == 40
    uncertainty_ids = {row["stable_id"] for row in uncertainties}
    for row in targets:
        fields = row["fields"]
        assert len(fields["uncertainty"]) == 1
        assert fields["uncertainty"][0] in uncertainty_ids
        assert sum(bool(fields[key]) for key in ("knowledge_object", "object_part", "claim")) == 1
