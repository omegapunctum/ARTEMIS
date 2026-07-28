import json
import math
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from scripts.validation_modules import ModuleValidationError, render_brief, validate_package


ROOT = Path(__file__).resolve().parents[1]


def test_gate_a_research_modules_pass_structural_contract() -> None:
    counts = validate_package(ROOT)

    assert set(counts) == {"A", "B", "C"}
    for module_counts in counts.values():
        assert 4 <= module_counts["features"] <= 6
        assert 4 <= module_counts["lenses"] <= 6
        assert 6 <= module_counts["claims"] <= 10
        assert module_counts["evidence_links"] >= 8
        assert module_counts["relations"] >= 2


def test_gate_a_passes_strict_ready_contract() -> None:
    counts = validate_package(ROOT, require_ready=True)

    assert set(counts) == {"A", "B", "C"}


def test_reference_briefs_are_deterministic() -> None:
    for module_id in ("a", "b", "c"):
        module_path = ROOT / "docs" / "work" / "validation_modules" / "modules" / f"module_{module_id}.json"
        brief_path = (
            ROOT
            / "docs"
            / "work"
            / "validation_modules"
            / "briefs"
            / f"module_{module_id}_reference_brief.md"
        )
        module = json.loads(module_path.read_text(encoding="utf-8"))
        assert brief_path.read_text(encoding="utf-8") == render_brief(module)


def test_gate_a_uses_canonical_epistemic_vocabulary() -> None:
    for module_id in ("a", "b", "c"):
        module_path = ROOT / "docs" / "work" / "validation_modules" / "modules" / f"module_{module_id}.json"
        module = json.loads(module_path.read_text(encoding="utf-8"))

        assert {claim["claim_kind"] for claim in module["claims"]} <= {
            "factual",
            "interpretation",
            "hypothesis",
            "counterfactual",
        }
        assert {claim["review_state"] for claim in module["claims"]} <= {
            "draft",
            "reviewed",
            "contested",
            "rejected",
            "superseded",
        }
        assert {link["evidence_strength"] for link in module["evidence_links"]} <= {
            "direct",
            "indirect",
            "background",
        }
        assert all(claim["preparation_state"] == "curator_checked" for claim in module["claims"])
        assert all(link["preparation_state"] == "curator_checked" for link in module["evidence_links"])


def test_reference_briefs_preserve_material_epistemic_axes_and_relation_qualifiers() -> None:
    for module_id in ("a", "b", "c"):
        module_path = ROOT / "docs" / "work" / "validation_modules" / "modules" / f"module_{module_id}.json"
        module = json.loads(module_path.read_text(encoding="utf-8"))
        brief = render_brief(module)

        for claim in module["claims"]:
            assert (
                f"{claim['claim_id']} · {claim['claim_kind']} · origin {claim['origin']} · "
                f"review {claim['review_state']}"
            ) in brief
        for link in module["evidence_links"]:
            assert f"{link['evidence_strength']}; review {link['review_state']}; locator:" in brief
        for claim in module["claims"]:
            if claim.get("relation"):
                assert f"qualifier: {claim['relation']['qualifier']}." in brief


def test_ready_cost_uses_full_audited_recuration_per_module() -> None:
    log_path = ROOT / "docs" / "work" / "validation_modules" / "preparation_log.json"
    checklist_path = ROOT / "docs" / "work" / "validation_modules" / "recuration_checklists.json"
    preparation_log = json.loads(log_path.read_text(encoding="utf-8"))
    checklists = json.loads(checklist_path.read_text(encoding="utf-8"))["modules"]

    assert preparation_log["measurement_status"] == "COMPLETE"
    assert set(preparation_log["full_recuration_sessions"]) == {"A", "B", "C"}
    for module_id in ("A", "B", "C"):
        session = preparation_log["full_recuration_sessions"][module_id]
        checklist = checklists[module_id]
        module_path = (
            ROOT
            / "docs"
            / "work"
            / "validation_modules"
            / "modules"
            / f"module_{module_id.lower()}.json"
        )
        module = json.loads(module_path.read_text(encoding="utf-8"))
        started_at = datetime.fromisoformat(checklist["started_at"].replace("Z", "+00:00"))
        ended_at = datetime.fromisoformat(checklist["ended_at"].replace("Z", "+00:00"))
        elapsed_seconds = int((ended_at - started_at).total_seconds())

        assert checklist["elapsed_seconds"] == elapsed_seconds
        assert checklist["elapsed_minutes"] == math.ceil(elapsed_seconds / 60)
        assert session["started_at"] == checklist["started_at"]
        assert session["ended_at"] == checklist["ended_at"]
        assert session["elapsed_seconds"] == checklist["elapsed_seconds"]
        assert session["elapsed_minutes"] == checklist["elapsed_minutes"]
        assert preparation_log["per_module_curation_minutes"][module_id] == session["elapsed_minutes"]
        assert module["cost"]["curation_elapsed"] == session["elapsed_minutes"]
        assert checklist["claim_ids"] == [claim["claim_id"] for claim in module["claims"]]
        assert checklist["evidence_link_ids"] == [
            link["evidence_link_id"] for link in module["evidence_links"]
        ]
        assert checklist["relation_claim_ids"] == [
            claim["claim_id"] for claim in module["claims"] if claim.get("relation")
        ]
        assert checklist["source_ids"] == [source["source_id"] for source in module["sources"]]
        covered_evidence = [
            evidence_id
            for evidence_ids in checklist["source_locator_coverage"].values()
            for evidence_id in evidence_ids
        ]
        assert sorted(covered_evidence) == sorted(checklist["evidence_link_ids"])
        assert len(covered_evidence) == len(set(covered_evidence))


def test_recuration_contract_rejects_timestamp_arithmetic_drift(tmp_path: Path) -> None:
    package_root = tmp_path / "docs" / "work" / "validation_modules"
    shutil.copytree(ROOT / "docs" / "work" / "validation_modules", package_root)
    (tmp_path / "data").mkdir()
    shutil.copy2(ROOT / "data" / "features.json", tmp_path / "data" / "features.json")

    checklist_path = package_root / "recuration_checklists.json"
    checklists = json.loads(checklist_path.read_text(encoding="utf-8"))
    checklists["modules"]["A"]["elapsed_seconds"] += 1
    checklist_path.write_text(json.dumps(checklists), encoding="utf-8")

    with pytest.raises(ModuleValidationError, match="elapsed seconds do not match"):
        validate_package(tmp_path)


def test_recuration_contract_rejects_incomplete_object_coverage(tmp_path: Path) -> None:
    package_root = tmp_path / "docs" / "work" / "validation_modules"
    shutil.copytree(ROOT / "docs" / "work" / "validation_modules", package_root)
    (tmp_path / "data").mkdir()
    shutil.copy2(ROOT / "data" / "features.json", tmp_path / "data" / "features.json")

    checklist_path = package_root / "recuration_checklists.json"
    checklists = json.loads(checklist_path.read_text(encoding="utf-8"))
    checklists["modules"]["B"]["evidence_link_ids"].pop()
    checklist_path.write_text(json.dumps(checklists), encoding="utf-8")

    with pytest.raises(ModuleValidationError, match="EvidenceLink coverage drift"):
        validate_package(tmp_path)


def test_review_contract_rejects_session_timestamp_drift(tmp_path: Path) -> None:
    package_root = tmp_path / "docs" / "work" / "validation_modules"
    shutil.copytree(ROOT / "docs" / "work" / "validation_modules", package_root)
    (tmp_path / "data").mkdir()
    shutil.copy2(ROOT / "data" / "features.json", tmp_path / "data" / "features.json")

    registry_path = package_root / "review_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["review_sessions"]["reviewer-1-final-cfab4dda"]["elapsed_seconds"] += 1
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ModuleValidationError, match="elapsed seconds do not match"):
        validate_package(tmp_path, require_ready=True)
