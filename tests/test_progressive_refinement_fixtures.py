from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import scripts.validate_progressive_refinement_fixtures as refinement_validator

from scripts.validate_progressive_refinement_fixtures import (
    PACKAGE_PATH,
    PACKAGE_LOCK_COLLECTIONS,
    REVIEW_ARTIFACT_SCHEMA_PATH,
    REVIEW_REGISTRY_PATH,
    REVIEW_REQUEST_PATH,
    SCHEMA_PATH,
    RefinementValidationError,
    canonical_sha256,
    package_semantic_payload,
    safe_metadata_path,
    validate_acceptance_binding,
    validate_capability_prohibitions,
    validate_clean_state,
    validate_git_blob_entry,
    validate_index_visibility,
    validate_lifecycle_consistency,
    validate_package,
    validate_ready_descendant_paths,
    validate_review_artifact,
    validate_time_extent,
    reviewed_content_sha256,
)

ROOT = PACKAGE_PATH.parents[4]


def load_package() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def revision(package: dict, revision_id: str) -> dict:
    return next(item for item in package["revisions"] if item["id"] == revision_id)


def claim(package: dict, claim_id: str) -> dict:
    return next(item for item in package["claims"] if item["id"] == claim_id)


def mark_revision_evidence_unreviewed(package: dict, revision_id: str) -> None:
    item = revision(package, revision_id)
    claim_item = claim(package, item["claim_ref"])
    claim_item["evidence_state"] = "missing"
    for evidence_ref in item["evidence_link_refs"]:
        evidence = next(value for value in package["evidence_links"] if value["id"] == evidence_ref)
        evidence["review_state"] = "draft"


def refresh_lock(package: dict) -> None:
    package["ledger_lock"]["revision_ids"] = [item["id"] for item in package["revisions"]]
    raw = json.dumps(
        package["revisions"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    package["ledger_lock"]["revisions_sha256"] = hashlib.sha256(raw).hexdigest()
    package["package_lock"]["collection_ids"] = {
        key: [item["id"] for item in package[key]] for key in PACKAGE_LOCK_COLLECTIONS
    }
    package["package_lock"]["semantic_sha256"] = canonical_sha256(
        package_semantic_payload(package)
    )


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
    assert summary["status"] == "REVIEW_REQUIRED"
    assert summary["review_status"] == "REVIEW_REQUIRED"
    assert summary["review_count"] == 0
    assert summary["reviewed_content_sha256"] == json.loads(
        REVIEW_REGISTRY_PATH.read_text(encoding="utf-8")
    )["reviewed_content_sha256"]
    assert summary["series"] == 8
    assert summary["revisions"] == 14
    assert summary["claims"] == 14
    assert summary["evidence_links"] == 14
    assert summary["uncertainties"] == 5
    assert summary["ledger_sha256"] == "bc134ee6566eab73e8741f749652418ed847c0cb7245713d9f649a4532a640ab"
    assert summary["semantic_sha256"] == "742dd8007da20fe558a7e3422641281c47f0aae6e4c4821ee4ccd28587b923a7"


def test_require_ready_fails_closed() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_progressive_refinement_fixtures.py", "--require-ready"],
        cwd=PACKAGE_PATH.parents[4],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "package, independent reviews and ACCEPT decision are not READY" in result.stdout


def test_review_registry_is_fail_closed_before_two_independent_reviews() -> None:
    registry = json.loads(REVIEW_REGISTRY_PATH.read_text(encoding="utf-8"))
    assert registry["status"] == "REVIEW_REQUIRED"
    assert registry["frozen_commit"] is None
    assert registry["reviews"] == []
    assert registry["required_tracks"] == ["semantic-model", "validator-integrity"]
    assert registry["required_independence_method"] == "separate_agent_task_read_only"


def test_review_scope_rejects_review_metadata() -> None:
    request = json.loads(REVIEW_REQUEST_PATH.read_text(encoding="utf-8"))
    request["review_scope"].append("fixtures/world_model/refinement/v1/review_registry.json")
    with pytest.raises(RefinementValidationError, match="review metadata"):
        reviewed_content_sha256(request)


def test_review_request_identity_and_scope_are_frozen_by_exact_bytes() -> None:
    validator_source = (
        ROOT / "scripts" / "validate_progressive_refinement_fixtures.py"
    ).read_text(encoding="utf-8")
    assert 'frozen_loader(request_ref) != REVIEW_REQUEST_PATH.read_bytes()' in validator_source
    assert "review request identity/scope does not match the frozen commit" in validator_source
    assert "REVIEW_REQUEST_SCHEMA_PATH," in validator_source
    assert "REVIEW_REGISTRY_SCHEMA_PATH," in validator_source
    assert "REVIEW_ARTIFACT_SCHEMA_PATH," in validator_source
    assert "ACCEPTANCE_DECISION_SCHEMA_PATH," in validator_source
    assert "review control schema does not match the frozen commit" in validator_source
    assert 'registry["prior_reviews"] != frozen_registry.get("prior_reviews")' in validator_source
    assert "prior review audit history does not match the frozen commit" in validator_source


@pytest.mark.parametrize(
    "field",
    ["runtime_migration_authorized", "airtable_historical_write_authorized", "public_capability_change"],
)
def test_capability_prohibitions_are_enforced_by_reviewed_validator(field: str) -> None:
    decision = {
        "runtime_migration_authorized": False,
        "airtable_historical_write_authorized": False,
        "public_capability_change": False,
    }
    decision[field] = True
    with pytest.raises(RefinementValidationError, match="cannot authorize runtime, Airtable or public"):
        validate_capability_prohibitions(decision)


def test_review_registry_rejects_content_digest_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registry = json.loads(REVIEW_REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["reviewed_content_sha256"] = "0" * 64
    path = tmp_path / "review_registry.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    monkeypatch.setattr(refinement_validator, "REVIEW_REGISTRY_PATH", path)
    monkeypatch.setattr(refinement_validator, "require_regular_repo_file", lambda *_: None)
    with pytest.raises(RefinementValidationError, match="content digest"):
        refinement_validator.validate_review_envelope()


def test_ready_artifact_rejects_open_findings_even_when_counters_are_zero() -> None:
    schema = json.loads(REVIEW_ARTIFACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    artifact = json.loads(
        (ROOT / "fixtures/world_model/refinement/v1/reviews/round1_validator_integrity.json").read_text(
            encoding="utf-8"
        )
    )
    artifact["decision"] = "READY"
    artifact["open_critical"] = 0
    artifact["open_material"] = 0
    with pytest.raises(RefinementValidationError, match="finding counters"):
        validate_review_artifact(artifact, schema, "adversarial")


def test_review_artifact_rejects_duplicate_finding_ids() -> None:
    schema = json.loads(REVIEW_ARTIFACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    artifact = json.loads(
        (ROOT / "fixtures/world_model/refinement/v1/reviews/round5_validator_integrity.json").read_text(
            encoding="utf-8"
        )
    )
    artifact["findings"][1]["finding_id"] = artifact["findings"][0]["finding_id"]
    with pytest.raises(RefinementValidationError, match="finding_id values must be unique"):
        validate_review_artifact(artifact, schema, "adversarial")


def test_review_artifact_path_rejects_traversal() -> None:
    with pytest.raises(RefinementValidationError, match="unsafe path"):
        safe_metadata_path(
            "fixtures/world_model/refinement/v1/reviews/../../../../outside.json",
            ROOT / "fixtures/world_model/refinement/v1/reviews",
            "artifact_ref",
        )


@pytest.mark.parametrize("outcome", ["NARROW", "REJECT"])
def test_decided_non_accept_outcome_must_bind_frozen_revision(outcome: str) -> None:
    decision = {
        "status": "DECIDED",
        "decision": outcome,
        "frozen_commit": None,
        "frozen_tree": None,
    }
    with pytest.raises(RefinementValidationError, match="does not bind the frozen revision"):
        validate_acceptance_binding(decision, "REVIEWS_COMPLETE", "a" * 40, "b" * 40)


def test_review_digest_allows_only_normalized_lifecycle_status_transition() -> None:
    request = json.loads(REVIEW_REQUEST_PATH.read_text(encoding="utf-8"))
    baseline = reviewed_content_sha256(request)

    def loader(raw_path: str) -> bytes:
        content = (ROOT / raw_path).read_bytes()
        if raw_path == "fixtures/world_model/refinement/v1/package.json":
            package = json.loads(content)
            package["status"] = "READY"
            return json.dumps(package).encode("utf-8")
        if raw_path == "docs/PROGRESSIVE_REFINEMENT_CONTRACT.md":
            text = content.decode("utf-8").replace("1.0-draft", "1.0", 1).replace(
                "`REVIEW_REQUIRED` under issue `#377`", "`READY` under issue `#377`", 1
            )
            return text.encode("utf-8")
        return content

    assert reviewed_content_sha256(request, loader) == baseline


def test_review_digest_rejects_semantic_text_appended_to_lifecycle_header() -> None:
    request = json.loads(REVIEW_REQUEST_PATH.read_text(encoding="utf-8"))

    def loader(raw_path: str) -> bytes:
        content = (ROOT / raw_path).read_bytes()
        if raw_path == "docs/PROGRESSIVE_REFINEMENT_CONTRACT.md":
            return content.replace(
                b"- Status: `REVIEW_REQUIRED` under issue `#377`.",
                b"- Status: `REVIEW_REQUIRED` under issue `#377`; runtime export authorized.",
                1,
            )
        return content

    with pytest.raises(RefinementValidationError, match="unauthorized status header"):
        reviewed_content_sha256(request, loader)


def test_source_locator_reproduces_raw_value_and_claim(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["source_value"]["raw"] = "9 August 1502"
    refresh_lock(package)
    path = write_package(tmp_path, package)
    with pytest.raises(RefinementValidationError, match="locator does not reproduce"):
        validate_package(path, SCHEMA_PATH)


def test_source_locator_binds_exact_normalized_assertion(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-leo-time-refined")["normalized_assertion"]
    item["valid_time"]["start"] = "1502-08-09"
    item["valid_time"]["end"] = "1502-08-09"
    item["value"]["start"] = "1502-08-09"
    item["value"]["end"] = "1502-08-09"
    assert_rejected(tmp_path, package, "locator does not bind the exact source value and normalized assertion")


def test_temporal_precision_representations_must_agree(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]["precision"] = "month"
    assert_rejected(tmp_path, package, "temporal precision representations must agree")


def test_source_locator_binds_complete_source_value(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-coarse")["source_value"]["precision"] = "day"
    assert_rejected(tmp_path, package, "locator does not bind the exact source value and normalized assertion")


def test_temporal_alternative_precision_cannot_exceed_source_or_top_level(tmp_path: Path) -> None:
    package = load_package()
    extent = revision(package, "revision-leo-time-coarse")["normalized_assertion"]["valid_time"]
    extent["alternatives"] = [{
        "id": "alternative-unsupported-day",
        "kind": "instant",
        "start": "1502-08-08",
        "end": "1502-08-08",
        "start_inclusive": True,
        "end_inclusive": True,
        "start_qualifier": "exact",
        "end_qualifier": "exact",
        "precision": "day",
        "basis_claim_refs": ["claim-leo-time-coarse"],
    }]
    assert_rejected(tmp_path, package, "alternative precision exceeds source/top-level support")


def test_temporal_envelope_supports_open_bounds_and_alternatives() -> None:
    basis = ["claim-leo-time-coarse"]
    start, end = validate_time_extent(
        {
            "calendar": "proleptic_gregorian",
            "kind": "open_end_interval",
            "start": "1502-08-01",
            "end": None,
            "start_inclusive": True,
            "end_inclusive": None,
            "start_qualifier": "not_before",
            "end_qualifier": "unknown",
            "precision": "day",
            "certainty": "approximate",
            "normalization_state": "normalized",
            "basis_claim_refs": basis,
            "alternatives": [
                {
                    "id": "alternative-open-start",
                    "kind": "open_start_interval",
                    "start": None,
                    "end": "1502-08-31",
                    "start_inclusive": None,
                    "end_inclusive": False,
                    "start_qualifier": "unknown",
                    "end_qualifier": "not_after",
                    "precision": "day",
                    "basis_claim_refs": basis,
                }
            ],
        },
        "temporal-test",
    )
    assert start is not None and end is None


def test_temporal_extent_rejects_empty_exclusive_instant() -> None:
    extent = copy.deepcopy(
        revision(load_package(), "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    )
    extent["start_inclusive"] = False
    extent["end_inclusive"] = False
    with pytest.raises(RefinementValidationError, match="non-empty temporal possible set"):
        validate_time_extent(extent, "exclusive-instant")


def test_rejects_duplicate_atomic_target_series(tmp_path: Path) -> None:
    package = load_package()
    duplicate = copy.deepcopy(package["series"][0])
    duplicate["id"] = "series-leo-time-duplicate"
    package["series"].append(duplicate)
    refresh_lock(package)
    path = write_package(tmp_path, package)
    with pytest.raises(RefinementValidationError, match="series coverage|more than one revision series"):
        validate_package(path, SCHEMA_PATH)


def test_rejects_evidence_history_erasure_even_with_recomputed_locks(tmp_path: Path) -> None:
    package = load_package()
    package["evidence_links"] = [
        item for item in package["evidence_links"] if item["id"] != "evidence-leo-route-unknown"
    ]
    revision(package, "revision-leo-route-unknown")["evidence_link_refs"] = []
    claim(package, "claim-leo-route-unknown")["evidence_link_refs"] = []
    claim(package, "claim-leo-route-unknown")["evidence_state"] = "missing"
    refresh_lock(package)
    path = write_package(tmp_path, package)
    with pytest.raises(RefinementValidationError, match="EvidenceLink coverage"):
        validate_package(path, SCHEMA_PATH)


def test_rejects_detached_evidence_even_with_recomputed_locks(tmp_path: Path) -> None:
    package = load_package()
    claim(package, "claim-leo-route-unknown")["evidence_link_refs"] = []
    revision(package, "revision-leo-route-unknown")["evidence_link_refs"] = []
    claim(package, "claim-leo-route-unknown")["evidence_state"] = "missing"
    assert_rejected(tmp_path, package, "detached from its Claim")


def test_rejects_detached_uncertainty_even_with_recomputed_locks(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-coarse")["uncertainty_refs"] = []
    claim(package, "claim-leo-time-coarse")["uncertainty_refs"] = []
    assert_rejected(tmp_path, package, "detached from its revision/Claim")


def test_require_ready_rejects_custom_package(tmp_path: Path) -> None:
    path = write_package(tmp_path, load_package())
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_progressive_refinement_fixtures.py",
            "--package",
            str(path),
            "--require-ready",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "restricted to the canonical reviewed package" in result.stdout


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
    item["normalized_assertion"]["valid_time"]["end"] = "1502-07-31"
    item["normalized_assertion"]["value"]["start"] = "1502-07-31"
    item["normalized_assertion"]["value"]["end"] = "1502-07-31"
    assert_rejected(tmp_path, package, "temporal possible set")


def test_temporal_refinement_cannot_change_calendar_profile(tmp_path: Path) -> None:
    package = load_package()
    extent = revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    extent["calendar"] = "source_native_unresolved"
    extent["normalization_state"] = "unresolved"
    assert_rejected(tmp_path, package, "must keep the predecessor calendar profile")


def test_temporal_refinement_alternatives_must_stay_in_predecessor_possible_set(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]["alternatives"] = [{
        "id": "alternative-outside-predecessor",
        "kind": "instant",
        "start": "1600-01-01",
        "end": "1600-01-01",
        "start_inclusive": True,
        "end_inclusive": True,
        "start_qualifier": "exact",
        "end_qualifier": "exact",
        "precision": "day",
        "basis_claim_refs": ["claim-leo-time-refined"],
    }]
    assert_rejected(tmp_path, package, "possible set is not contained by its predecessor")


def test_temporal_refinement_rejects_unchanged_universal_alternative(tmp_path: Path) -> None:
    package = load_package()
    universal = {
        "id": "alternative-unknown-universal",
        "kind": "unknown",
        "start": None,
        "end": None,
        "start_inclusive": None,
        "end_inclusive": None,
        "start_qualifier": "unknown",
        "end_qualifier": "unknown",
        "precision": "unknown",
        "basis_claim_refs": ["claim-leo-time-coarse"],
    }
    coarse = revision(package, "revision-leo-time-coarse")["normalized_assertion"]["valid_time"]
    refined = revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    coarse["alternatives"] = [copy.deepcopy(universal)]
    universal["basis_claim_refs"] = ["claim-leo-time-refined"]
    refined["alternatives"] = [universal]
    assert_rejected(tmp_path, package, "possible set is not strictly narrower")


def test_temporal_refinement_rejects_split_members_with_unchanged_union(tmp_path: Path) -> None:
    package = load_package()
    refined = revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    refined.update({
        "kind": "closed_interval",
        "start": "1502-08-01",
        "end": "1502-08-08",
        "start_inclusive": True,
        "end_inclusive": True,
        "start_qualifier": "approximate",
        "end_qualifier": "approximate",
        "alternatives": [{
            "id": "alternative-restores-predecessor-union",
            "kind": "closed_interval",
            "start": "1502-08-08",
            "end": "1502-08-31",
            "start_inclusive": True,
            "end_inclusive": True,
            "start_qualifier": "approximate",
            "end_qualifier": "approximate",
            "precision": "day",
            "basis_claim_refs": ["claim-leo-time-refined"],
        }],
    })
    value = revision(package, "revision-leo-time-refined")["normalized_assertion"]["value"]
    value["start"], value["end"] = refined["start"], refined["end"]
    assert_rejected(tmp_path, package, "possible set is not strictly narrower")


def test_temporal_refinement_allows_open_start_to_finite_narrowing(tmp_path: Path) -> None:
    package = load_package()
    coarse = revision(package, "revision-leo-time-coarse")["normalized_assertion"]["valid_time"]
    coarse.update({
        "kind": "open_start_interval",
        "start": None,
        "start_inclusive": None,
        "start_qualifier": "unknown",
    })
    revision(package, "revision-leo-time-coarse")["normalized_assertion"]["value"]["start"] = None
    mark_revision_evidence_unreviewed(package, "revision-leo-time-coarse")
    path = write_package(tmp_path, package)
    validate_package(path, SCHEMA_PATH)


def test_temporal_refinement_allows_equal_single_interval_with_finer_precision(tmp_path: Path) -> None:
    package = load_package()
    coarse = revision(package, "revision-leo-time-coarse")["normalized_assertion"]["valid_time"]
    refined = revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    for field in (
        "kind", "start", "end", "start_inclusive", "end_inclusive",
        "start_qualifier", "end_qualifier",
    ):
        refined[field] = coarse[field]
    value = revision(package, "revision-leo-time-refined")["normalized_assertion"]["value"]
    value["start"], value["end"] = refined["start"], refined["end"]
    mark_revision_evidence_unreviewed(package, "revision-leo-time-refined")
    path = write_package(tmp_path, package)
    validate_package(path, SCHEMA_PATH)


def test_temporal_refinement_allows_same_bounds_with_narrower_inclusivity(tmp_path: Path) -> None:
    package = load_package()
    coarse = revision(package, "revision-leo-time-coarse")["normalized_assertion"]["valid_time"]
    refined = revision(package, "revision-leo-time-refined")["normalized_assertion"]["valid_time"]
    refined.update({
        "kind": "closed_interval",
        "start": coarse["start"],
        "end": coarse["end"],
        "start_inclusive": False,
        "end_inclusive": coarse["end_inclusive"],
        "start_qualifier": coarse["start_qualifier"],
        "end_qualifier": coarse["end_qualifier"],
    })
    value = revision(package, "revision-leo-time-refined")["normalized_assertion"]["value"]
    value["start"], value["end"] = refined["start"], refined["end"]
    mark_revision_evidence_unreviewed(package, "revision-leo-time-refined")
    path = write_package(tmp_path, package)
    validate_package(path, SCHEMA_PATH)


def test_rejects_false_spatial_refinement(tmp_path: Path) -> None:
    package = load_package()
    revision(package, "revision-range-1900-refined")["normalized_assertion"]["value"]["bbox"] = [
        3.0, 44.0, 18.0, 53.0
    ]
    assert_rejected(tmp_path, package, "spatial possible set is not strictly narrower")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("start_inclusive", False),
        ("start_qualifier", "not_before"),
        ("calendar", "source_native_unresolved"),
        ("alternatives", [{
            "id": "alternative-material-temporal-envelope",
            "kind": "closed_interval",
            "start": "1900-01-01",
            "end": "1900-12-31",
            "start_inclusive": True,
            "end_inclusive": True,
            "start_qualifier": "exact",
            "end_qualifier": "exact",
            "precision": "day",
            "basis_claim_refs": ["claim-range-1900-refined"],
        }]),
    ],
)
def test_spatial_refinement_cannot_mutate_temporal_envelope(
    tmp_path: Path, field: str, value: object
) -> None:
    package = load_package()
    extent = revision(package, "revision-range-1900-refined")["normalized_assertion"]["valid_time"]
    extent[field] = value
    if field == "calendar":
        extent["normalization_state"] = "unresolved"
    assert_rejected(tmp_path, package, "cannot change the valid_time envelope")


def test_non_temporal_correction_cannot_move_to_another_valid_time(tmp_path: Path) -> None:
    package = load_package()
    item = revision(package, "revision-range-1900-refined")
    item["operation"] = "correct"
    extent = item["normalized_assertion"]["valid_time"]
    extent["start"] = "1901-01-01"
    extent["end"] = "1901-12-31"
    assert_rejected(tmp_path, package, "spatial correct cannot change the valid_time envelope")


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


def test_progressive_intake_and_promotion_are_routed_without_competing_truth_owner() -> None:
    contract = (ROOT / "docs" / "PROGRESSIVE_REFINEMENT_CONTRACT.md").read_text(encoding="utf-8")
    governance = (ROOT / "docs" / "CONTENT_GOVERNANCE.md").read_text(encoding="utf-8")
    operating_system = (ROOT / "docs" / "DEVELOPMENT_OPERATING_SYSTEM.md").read_text(encoding="utf-8")
    for text in (contract, governance):
        assert "candidate intake → atomic Claim/revision" in text
        assert "deterministic current frontier" in text
        assert "separately authorized export/publication" in text
    assert "Drive research originals → authorized curated corpus intake" in operating_system
    assert "No Drive file, Airtable row, AI output or runtime edit becomes canonical" in operating_system


def test_required_ci_guards_are_wired() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "progressive-refinement.yml"
    ).read_text(encoding="utf-8")
    assert "python scripts/validate_progressive_refinement_fixtures.py" in workflow
    assert "pytest -q tests/test_progressive_refinement_fixtures.py" in workflow
    assert 'fetch-depth: 0' in workflow
    assert 'requirements.txt' in workflow


def test_ready_descendant_rejects_any_path_outside_exact_metadata_allowlist() -> None:
    allowed = {
        "fixtures/world_model/refinement/v1/review_registry.json",
        "fixtures/world_model/refinement/v1/acceptance_decision.json",
    }
    validate_ready_descendant_paths(sorted(allowed), allowed)
    with pytest.raises(RefinementValidationError, match="non-metadata changes"):
        validate_ready_descendant_paths(
            [*sorted(allowed), "docs/PROJECT_TRUTH.md"], allowed
        )


@pytest.mark.parametrize(
    ("status_output", "other_files"),
    [
        (" M docs/PROJECT_TRUTH.md\n", ""),
        ("M  docs/PROJECT_TRUTH.md\n", ""),
        ("?? docs/UNREVIEWED_CAPABILITY.md\n", "docs/UNREVIEWED_CAPABILITY.md\n"),
        ("", "ignored/unreviewed-capability.md\n"),
    ],
)
def test_ready_checkout_rejects_staged_unstaged_untracked_and_ignored_files(
    status_output: str, other_files: str
) -> None:
    with pytest.raises(RefinementValidationError, match="clean index/worktree"):
        validate_clean_state(status_output, other_files)


@pytest.mark.parametrize(
    "index_entry",
    [b"h docs/PROJECT_TRUTH.md\0", b"S docs/PROJECT_TRUTH.md\0", b"s docs/PROJECT_TRUTH.md\0"],
)
def test_ready_checkout_rejects_hidden_index_visibility_flags(index_entry: bytes) -> None:
    validate_index_visibility(b"H README.md\0H path with newline\ninside.md\0")
    with pytest.raises(RefinementValidationError, match="nonstandard index entries"):
        validate_index_visibility(index_entry)


def test_ready_metadata_requires_regular_git_blob_mode() -> None:
    validate_git_blob_entry(
        "fixtures/world_model/refinement/v1/review_registry.json",
        "100644 blob abcdef\tfixtures/world_model/refinement/v1/review_registry.json\n",
    )
    with pytest.raises(RefinementValidationError, match="committed regular 100644 blob"):
        validate_git_blob_entry(
            "fixtures/world_model/refinement/v1/review_registry.json",
            "120000 blob abcdef\tfixtures/world_model/refinement/v1/review_registry.json\n",
        )


def test_lifecycle_consistency_rejects_package_registry_contradiction() -> None:
    validate_lifecycle_consistency("REVIEW_REQUIRED", "REVIEW_REQUIRED")
    with pytest.raises(RefinementValidationError, match="lifecycle states are inconsistent"):
        validate_lifecycle_consistency("READY", "REVIEW_REQUIRED")


def test_review_registry_rejects_duplicate_review_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = json.loads(REVIEW_REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["prior_reviews"].append(copy.deepcopy(registry["prior_reviews"][0]))
    path = tmp_path / "review_registry.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    monkeypatch.setattr(refinement_validator, "REVIEW_REGISTRY_PATH", path)
    monkeypatch.setattr(refinement_validator, "require_regular_repo_file", lambda *_: None)
    with pytest.raises(RefinementValidationError, match="review_id values must be unique"):
        refinement_validator.validate_review_envelope()
