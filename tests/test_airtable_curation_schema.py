from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_airtable_curation_schema.py"
CONTRACT = ROOT / "fixtures" / "airtable_curation" / "v1" / "schema_contract.json"
SNAPSHOT = ROOT / "fixtures" / "airtable_curation" / "v1" / "live_schema_snapshot.json"
PROJECT_STATE = ROOT / "docs" / "project_state.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("artemis_airtable_curation_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shadow_schema_validator_passes_with_empty_tables() -> None:
    module = _load_validator()
    assert module.validate(require_empty=True) == {"tables": 6, "fields": 75, "records": 0}


def test_shadow_schema_is_non_authoritative_and_pre_gate_d() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    state = json.loads(PROJECT_STATE.read_text(encoding="utf-8"))

    assert contract["status"] == "SHADOW_SCHEMA_V1"
    assert contract["authoritative"] is False
    assert contract["rules"]["real_gate_c_import_allowed"] is False
    assert contract["rules"]["public_export_authority"] is False
    assert contract["rules"]["legacy_architecture_atlas_authority_changed"] is False
    assert contract["gate_boundary"]["next_gate"] == "D"
    assert contract["gate_boundary"]["next_gate_opened"] is False
    assert contract["gate_boundary"]["paused_relation_issue"] == 331

    assert state["gate"]["id"] == "C"
    assert state["gate"]["status"] == "completed"
    assert state["gate"]["decision"] == "FREEZE"
    assert state["next_transition"]["gate"] == "D"
    assert state["github"]["paused_issues"] == [331]


def test_live_snapshot_contains_only_empty_shadow_tables() -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["authoritative"] is False
    assert snapshot["record_counts_verified_zero"] is True
    assert [table["name"] for table in snapshot["tables"]] == [
        "WorldSlices",
        "KnowledgeObjects",
        "ObjectParts",
        "Claims",
        "EvidenceLinks",
        "Uncertainties",
    ]
    assert all(table["record_count"] == 0 for table in snapshot["tables"])


def test_claim_evidence_uncertainty_boundaries_are_explicit() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    tables = {table["name"]: table for table in contract["tables"]}

    evidence_fields = {field["name"]: field for field in tables["EvidenceLinks"]["fields"]}
    assert evidence_fields["claim"]["cardinality"] == "exactly_one"
    assert evidence_fields["source"]["linked_table"] == "Sources"
    assert evidence_fields["source"]["cardinality"] == "exactly_one"
    assert evidence_fields["locator"]["type"] == "singleLineText"
    assert evidence_fields["relation_to_claim"]["choices"] == ["supports", "challenges", "contextualizes"]
    assert evidence_fields["evidence_strength"]["choices"] == ["direct", "indirect", "background"]

    uncertainty = tables["Uncertainties"]
    assert uncertainty["target_cardinality"] == "exactly_one_of_knowledge_object_object_part_claim"

    parts = {field["name"]: field for field in tables["ObjectParts"]["fields"]}
    assert "unknown_route" in parts["spatial_status"]["choices"]
    assert "unknown_route" in parts["segment_kind"]["choices"]


def test_reused_legacy_tables_keep_narrow_roles() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert set(contract["reused_tables"]) == {"Sources", "Layers", "Media"}
    assert snapshot["reused_table_ids"] == contract["reused_tables"]
    knowledge_fields = {
        field["name"]: field
        for table in contract["tables"]
        if table["name"] == "KnowledgeObjects"
        for field in table["fields"]
    }
    assert knowledge_fields["layers"]["linked_table"] == "Layers"
