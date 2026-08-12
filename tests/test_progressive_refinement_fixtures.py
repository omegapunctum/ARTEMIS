from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validate_progressive_refinement_fixtures import (
    PACKAGE_PATH,
    SCHEMA_PATH,
    RefinementValidationError,
    validate_package,
)

ROOT = PACKAGE_PATH.parents[4]


def load_package() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def revision(package: dict, revision_id: str) -> dict:
    return next(item for item in package["revisions"] if item["id"] == revision_id)


def claim(package: dict, claim_id: str) -> dict:
    return next(item for item in package["claims"] if item["id"] == claim_id)


def refresh_lock(package: dict) -> None:
    package["ledger_lock"]["revision_ids"] = [item["id"] for item in package["revisions"]]
    raw = json.dumps(
        package["revisions"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    package["ledger_lock"]["revisions_sha256"] = hashlib.sha256(raw).hexdigest()


def write_package(tmp_path: Path, package: dict, *, refresh: bool = True) -> Path:
    payload = copy.deepcopy(package)
    if refresh:
        refresh_lock(payload)
    path = tmp_path / "package.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def assert_rejected(tmp_path: Path, package: dict, match: str, *, refresh: bool = True) -> None:
    path = write_package(tmp_path, package, refresh=refresh)
    with pytest.raises(RefinementValidationError, match=match):
        validate_package(path, SCHEMA_PATH)


def test_fixture_validates() -> None:
    summary = validate_package()
    assert summary == {
        "status": "REVIEW_REQUIRED",
        "series": 8,
        "revisions": 14,
        "claims": 14,
        "evidence_links": 14,
        "uncertainties": 5,
        "ledger_sha256": "b11cbbf47c8318b39dea1e131472feacb94bca09d48fb396cec28bd218355c8e",
    }


def test_require_ready_fails_closed() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_progressive_refinement_fixtures.py", "--require-ready"],
        cwd=PACKAGE_PATH.parents[4],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "package is not READY" in result.stdout


def test_rejects_in_place_mutation_without_lock_update(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-coarse")["source_value"]["raw"] = "September 1502"
    assert_rejected(tmp_path, package, "ledger_lock revisions_sha256", refresh=False)


def test_rejects_erased_history_even_with_recomputed_lock(tmp_path: Path) -> None:
    package = load_package()
    package["revisions"] = [
        item for item in package["revisions"] if item["id"] != "revision-leo-time-coarse"
    ]
    assert_rejected(tmp_path, package, "fixture revision coverage")


def test_rejects_false_temporal_refinement(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-leo-time-refined")
    item["normalized_assertion"]["valid_time"]["start"] = "1502-07-31"
    item["normalized_assertion"]["value"]["start"] = "1502-07-31"
    assert_rejected(tmp_path, package, "temporal possible set is not strictly narrower")


def test_rejects_false_spatial_refinement(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-range-1900-refined")["normalized_assertion"]["value"]["bbox"] = [
        3.0, 44.0, 18.0, 53.0
    ]
    assert_rejected(tmp_path, package, "spatial possible set is not strictly narrower")


def test_rejects_orphan_predecessor(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["predecessor_refs"] = ["revision-missing"]
    assert_rejected(tmp_path, package, "orphan or future predecessor")


def test_rejects_cross_series_predecessor(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["predecessor_refs"] = [
        "revision-leo-place-coarse"
    ]
    assert_rejected(tmp_path, package, "cross-series predecessor")


def test_rejects_predecessor_that_is_not_yet_recorded(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["recorded_at"] = "2026-08-11T00:30:00Z"
    assert_rejected(tmp_path, package, "orphan or future predecessor")


def test_rejects_normalized_precision_finer_than_source(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["source_value"]["precision"] = "month"
    assert_rejected(tmp_path, package, "finer than source-native precision")


def test_rejects_invented_unknown_route_geometry(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-route-unknown")["normalized_assertion"]["value"]["geometry"] = {
        "type": "LineString",
        "coordinates": [[12.0, 44.0], [12.5, 44.5]],
    }
    assert_rejected(tmp_path, package, "unknown_route must have geometry=null")


def test_rejects_automatic_alternative_winner(tmp_path: Path) -> None:
    package = load_package()
    package["expected_current_frontier"]["series-region-alternatives"] = [
        "revision-region-alternative"
    ]
    package["replay_checkpoints"][-1]["expected_frontier"]["series-region-alternatives"] = [
        "revision-region-alternative"
    ]
    assert_rejected(tmp_path, package, "expected_current_frontier")


def test_rejects_withdrawal_with_current_value(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-label-withdrawn")
    item["normalized_assertion"] = copy.deepcopy(
        revision(package, "revision-label-initial")["normalized_assertion"]
    )
    assert_rejected(tmp_path, package, "withdraw must have normalized_assertion=null")


def test_rejects_record_time_collapsed_into_historical_valid_time(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-coarse")["recorded_at"] = "1502-08-01T00:00:00Z"
    assert_rejected(tmp_path, package, "predates package creation")


def test_rejects_later_world_state_as_cross_series_refinement(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-range-2000-state")
    item["operation"] = "refine"
    item["predecessor_refs"] = ["revision-range-1900-refined"]
    item["recorded_at"] = "2026-08-11T12:30:00Z"
    assert_rejected(tmp_path, package, "cross-series predecessor")


def test_rejects_contradiction_disguised_as_literal_refinement(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-stop-corrected")["operation"] = "refine"
    assert_rejected(tmp_path, package, "refine is unsupported for literal")


def test_rejects_claim_evidence_lineage_drift(tmp_path: Path) -> None:
    package = load_package()
    claim(package, "claim-leo-time-refined")["evidence_link_refs"] = [
        "evidence-leo-time-coarse"
    ]
    assert_rejected(tmp_path, package, "invalid EvidenceLink")


def test_rejects_non_local_uncertainty(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-leo-time-refined")
    item["uncertainty_refs"] = ["uncertainty-leo-time-coarse"]
    claim(package, "claim-leo-time-refined")["uncertainty_refs"] = [
        "uncertainty-leo-time-coarse"
    ]
    assert_rejected(tmp_path, package, "non-local Uncertainty")


def test_rejects_tampered_record_time_replay(tmp_path: Path) -> None:
    package = load_package()
    package["replay_checkpoints"][1]["expected_frontier"]["series-stop-correction"] = [
        "revision-stop-initial"
    ]
    assert_rejected(tmp_path, package, "replay checkpoint")


def test_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    text = PACKAGE_PATH.read_text(encoding="utf-8")
    path = tmp_path / "package.json"
    path.write_text(text.replace('"schema_version": "1.0.0",', '"schema_version": "1.0.0",\n  "schema_version": "1.0.0",', 1), encoding="utf-8")
    with pytest.raises(RefinementValidationError, match="duplicate JSON key"):
        validate_package(path, SCHEMA_PATH)


def test_foundation_candidate_does_not_change_product_gate_state() -> None:
    state = json.loads((ROOT / "docs" / "project_state.json").read_text(encoding="utf-8"))
    assert state["gate"] == {
        "id": "D",
        "label": "Source-aware Globe experience",
        "status": "in_progress",
        "allowed_decisions": ["ADVANCE_TO_GATE_E", "NARROW", "REJECT"],
    }
    assert state["github"]["active_issues"] == [355]
    issue_sets = [
        value
        for key, value in state["github"].items()
        if key.endswith("_issues") and isinstance(value, list)
    ]
    assert all(377 not in values for values in issue_sets)


def test_candidate_is_routed_as_review_required_not_capability() -> None:
    contract = (ROOT / "docs" / "PROGRESSIVE_REFINEMENT_CONTRACT.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs" / "FOUNDATION_INDEX.md").read_text(encoding="utf-8")
    truth = (ROOT / "docs" / "PROJECT_TRUTH.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    decision = (
        ROOT / "docs" / "work" / "2026-08-12_PROGRESSIVE_REFINEMENT_DECISION_v1.md"
    ).read_text(encoding="utf-8")
    assert "Status: `REVIEW_REQUIRED` under issue `#377`" in contract
    assert "docs/PROGRESSIVE_REFINEMENT_CONTRACT.md" in foundation
    assert "Issue #377 is active foundation maintenance with `REVIEW_REQUIRED` fixtures" in truth
    assert "#377 as active foundation maintenance" in agents
    assert "Public capability impact: none" in decision


def test_required_ci_guards_are_wired() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "progressive-refinement.yml"
    ).read_text(encoding="utf-8")
    assert "python scripts/validate_progressive_refinement_fixtures.py" in workflow
    assert "pytest -q tests/test_progressive_refinement_fixtures.py" in workflow
