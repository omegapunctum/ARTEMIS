from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT = ROOT / "docs" / "work" / "2026-08-10_AIRTABLE_PRE_GATE_D_ALIGNMENT_v1.md"
AUDIT_SCRIPT = ROOT / "scripts" / "audit_airtable.py"
PROJECT_STATE = ROOT / "docs" / "project_state.json"
WORLD_MODEL_CONTRACT = ROOT / "docs" / "SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md"
CURATION_PLAN = ROOT / "docs" / "work" / "airtable" / "2026-08-10_AIRTABLE_CURATION_SCHEMA_PLAN_v1.json"
STALE_FIXTURE_PLAN = ROOT / "fixtures" / "airtable_curation" / "v1" / "plan.json"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("artemis_audit_airtable", AUDIT_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_alignment_document_preserves_storage_and_gate_boundaries() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")

    assert "Architecture Atlas compatibility/public projection" in text
    assert "Airtable is useful to ARTEMIS as an editorial and curation surface" in text
    assert "does **not** open Gate D" in text
    assert "No Gate C record is imported" in text
    assert "Issue #331 remains paused" in text
    assert "`WorldSlices`" in text
    assert "`KnowledgeObjects`" in text
    assert "`ObjectParts`" in text
    assert "`Claims`" in text
    assert "`EvidenceLinks`" in text
    assert "`Uncertainties`" in text
    assert "reverse direction is prohibited" in text


def test_project_state_remains_gate_c_freeze_with_gate_d_only_next() -> None:
    state = json.loads(PROJECT_STATE.read_text(encoding="utf-8"))

    assert state["gate"]["id"] == "C"
    assert state["gate"]["status"] == "completed"
    assert state["gate"]["decision"] == "FREEZE"
    assert state["next_transition"]["gate"] == "D"
    assert state["capability"]["globe"] == "non_public_r_and_d"
    assert state["github"]["paused_issues"] == [331]


def test_legacy_audit_entrypoint_uses_canonical_semantic_gate() -> None:
    text = AUDIT_SCRIPT.read_text(encoding="utf-8")
    module = _load_audit_module()
    public_args = module.parse_args([])

    assert "validate_semantic_release" in text
    assert "export_airtable.py" in text
    assert "fetch_airtable_records" not in text
    assert "ALLOWED_LICENSES" not in text
    assert "validate_feature(" not in text
    assert "validate_layer(" not in text
    # The wrapper may pass a fixed --out-dir=data to the canonical exporter internally,
    # but callers must not be able to select a competing output/audit path.
    assert not hasattr(public_args, "out_dir")


def test_legacy_audit_validates_current_checked_in_artifacts() -> None:
    module = _load_audit_module()
    assert module.main(["--root", str(ROOT)]) == 0


def test_curation_plan_is_working_proposal_not_executable_fixture() -> None:
    assert CURATION_PLAN.exists()
    assert not STALE_FIXTURE_PLAN.exists()

    plan = json.loads(CURATION_PLAN.read_text(encoding="utf-8"))

    assert plan["schema_version"] == "1.0.0"
    assert plan["status"] == "proposal_only"
    assert plan["issue"] == 366
    assert plan["gate_boundary"] == {
        "current_gate": "C",
        "current_status": "completed",
        "current_decision": "FREEZE",
        "next_gate": "D",
        "next_gate_opened": False,
    }
    assert plan["authority"]["airtable_role"] == "editorial_curation_surface_not_semantic_owner"

    legacy_names = {table["name"] for table in plan["legacy_tables"]}
    assert legacy_names == {
        "Features",
        "Layers",
        "Sources",
        "Media",
        "FeatureSources",
        "FeatureMedia",
        "Relations",
        "RelationSources",
    }

    proposed_names = [table["name"] for table in plan["proposed_tables"]]
    assert proposed_names == [
        "WorldSlices",
        "KnowledgeObjects",
        "ObjectParts",
        "Claims",
        "EvidenceLinks",
        "Uncertainties",
    ]

    evidence_links = next(table for table in plan["proposed_tables"] if table["name"] == "EvidenceLinks")
    evidence_field_names = {field["name"] for field in evidence_links["fields"]}
    assert {"claim", "source", "locator", "relation_to_claim", "evidence_strength"} <= evidence_field_names

    prohibited = set(plan["prohibited"])
    assert "opening Gate D by implication" in prohibited
    assert "creating a second World Model ontology in Airtable" in prohibited
    assert "modifying the frozen Gate C package during shadow import" in prohibited


def test_reviewed_world_model_contract_is_not_redeclared_by_alignment() -> None:
    world_model = WORLD_MODEL_CONTRACT.read_text(encoding="utf-8")
    alignment = ALIGNMENT.read_text(encoding="utf-8")

    assert "Версия: 1.0." in world_model
    assert "schema proposal only" in alignment
    assert "Airtable convenience may not redefine" in alignment
