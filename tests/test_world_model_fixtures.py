import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.validate_world_model_fixtures import (
    FixtureValidationError,
    REQUIRED_REVIEW_SCOPE,
    compute_review_scope_digest,
    validate_package,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("fixtures/world_model/v1")


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / PACKAGE, root / PACKAGE)
    for relative_path in REQUIRED_REVIEW_SCOPE:
        source = ROOT / relative_path
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    data_source = ROOT / "data" / "features.json"
    if data_source.is_file():
        (root / "data").mkdir(parents=True)
        shutil.copy2(data_source, root / "data" / "features.json")
    return root


def _read_package(root: Path) -> dict:
    return json.loads((root / PACKAGE / "package.json").read_text(encoding="utf-8"))


def _write_package(root: Path, package: dict) -> None:
    _write_json(root / PACKAGE / "package.json", package)


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def _make_ready_reviews(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "fixture-tests@example.invalid")
    _git(root, "config", "user.name", "Fixture test")
    _git(root, "add", "data/features.json")
    _git(root, "commit", "-m", "test: pin compatibility source")
    compatibility_commit = _git(root, "rev-parse", "HEAD")
    compatibility_path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    compatibility = json.loads(compatibility_path.read_text(encoding="utf-8"))
    compatibility["source_dataset"]["commit"] = compatibility_commit
    compatibility["source_dataset"]["source_file_sha256"] = hashlib.sha256(
        (root / "data/features.json").read_bytes()
    ).hexdigest()
    _write_json(compatibility_path, compatibility)
    _git(root, "add", *REQUIRED_REVIEW_SCOPE)
    _git(root, "commit", "-m", "test: freeze semantic review scope")
    frozen_commit = _git(root, "rev-parse", "HEAD")

    package = _read_package(root)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = "2026-07-30T00:00:00Z"
    _write_package(root, package)

    registry_path = root / PACKAGE / "review_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    content_digest = compute_review_scope_digest(root, registry)
    reviews = []
    review_specs = (
        ("review-semantic", "reviewer-semantic", "invocation-semantic", "semantic-model"),
        ("review-validator", "reviewer-validator", "invocation-validator", "validator-integrity"),
    )
    for review_id, reviewer_id, reviewer_instance_id, review_track in review_specs:
        artifact_path = Path("docs/work/reviews") / f"{review_id}.md"
        artifact = root / artifact_path
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            "\n".join(
                (
                    f"review_id: {review_id}",
                    f"reviewer_id: {reviewer_id}",
                    f"reviewer_instance_id: {reviewer_instance_id}",
                    f"review_track: {review_track}",
                    "independence_method: separate_agent_task",
                    f"frozen_commit: {frozen_commit}",
                    f"reviewed_content_sha256: {content_digest}",
                    "decision: READY",
                    "critical_findings: 0",
                    "unresolved_material_findings: 0",
                    "independence_attestation: true",
                    "artifact_format: artemis-review-attestation-v1",
                    "",
                )
            ),
            encoding="utf-8",
        )
        reviews.append(
            {
                "review_id": review_id,
                "reviewer_id": reviewer_id,
                "reviewer_instance_id": reviewer_instance_id,
                "review_track": review_track,
                "independence_method": "separate_agent_task",
                "artifact": str(artifact_path),
                "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "frozen_commit": frozen_commit,
                "reviewed_content_sha256": content_digest,
                "decision": "READY",
                "critical_findings": 0,
                "unresolved_material_findings": 0,
                "independence_attestation": True,
            }
        )
    registry["status"] = "READY"
    registry["frozen_commit"] = frozen_commit
    registry["reviewed_content_sha256"] = content_digest
    registry["reviews"] = reviews
    _write_json(registry_path, registry)


def test_world_model_fixture_package_passes_structural_validation() -> None:
    counts = validate_package(ROOT)

    assert counts["Entity"] == 9
    assert counts["Event"] == 4
    assert counts["State"] == 3
    assert counts["Process"] == 1
    assert counts["Trajectory"] == 1
    assert counts["Region"] == 2
    assert counts["Relation"] == 2
    assert counts["Claim"] == 20
    assert counts["EvidenceLink"] == 21


def test_ready_mode_fails_until_two_independent_reviews_exist() -> None:
    with pytest.raises(FixtureValidationError, match="two independent READY reviews"):
        validate_package(ROOT, require_ready=True)


def test_validator_rejects_semantic_collapse(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["states"][0]["type"] = "Event"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must have type State"):
        validate_package(root)


def test_validator_rejects_orphan_references(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["events"][0]["claim_refs"] = ["claim-does-not-exist"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="orphan reference"):
        validate_package(root)


def test_validator_rejects_precision_without_basis_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["events"][0]["temporal_extent"]["basis_claim_refs"] = []
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="without a basis Claim"):
        validate_package(root)


def test_validator_rejects_derived_overlap_stored_as_relation(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["relations"][0]["predicate"] = "co_present"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="stores derived co_present as Relation"):
        validate_package(root)


def test_validator_rejects_unreproducible_locator(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["evidence_links"][0]["locator"] = "LOCATOR[missing]"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="locator is not reproducible"):
        validate_package(root)


def test_validator_rejects_invented_compatibility_evidence(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["target_projection"]["claims"][0]["evidence_state"] = "supported"
    path.write_text(json.dumps(projection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="must expose missing evidence"):
        validate_package(root)


def test_validator_rejects_historical_absence_semantics(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["known_exclusions"][0]["assertion_kind"] = "historical_absence"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="corpus exclusion"):
        validate_package(root)


def test_package_is_validated_against_json_schema(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["status"] = "APPROVED_BY_PROSE"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_validator_rejects_reference_to_wrong_object_type(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["events"][0]["participant_refs"] = ["claim-charter-event"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="participant_refs must reference"):
        validate_package(root)


def test_validator_rejects_temporal_only_overlap_as_co_presence(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    traveler_state = next(
        state for state in package["states"] if state["id"] == "state-traveler-workshop-presence"
    )
    traveler_state["spatial_extent"]["place_ref"] = "place-far-observatory"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="do not overlap in space"):
        validate_package(root)


def test_validator_rejects_alternative_date_without_distinct_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    arrival = next(event for event in package["events"] if event["id"] == "event-workshop-arrival")
    arrival["temporal_extent"]["alternatives"][0]["basis_claim_refs"] = ["claim-arrival-event"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="alternative date needs a distinct supporting Claim"):
        validate_package(root)


def test_validator_rejects_contradictory_evidence_state(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    influence = next(
        claim for claim in package["claims"] if claim["id"] == "claim-influence-ren-council"
    )
    influence["evidence_state"] = "supported"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must be derived as mixed"):
        validate_package(root)


def test_validator_rejects_process_that_does_not_span_regions(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    process = package["processes"][0]
    process["stages"][1]["spatial_extent"]["region_ref"] = "region-fixture-basin"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must target its Region|must span more than one Region"):
        validate_package(root)


def test_validator_rejects_incomplete_synchronized_view(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0].pop("camera_state")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_validator_rejects_compatibility_source_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    data_path = root / "data" / "features.json"
    records = json.loads(data_path.read_text(encoding="utf-8"))
    record = next(item for item in records if item["id"] == "rec1GDGqssFGehzEx")
    record["fields"]["date_start"] = "1930"
    _write_json(data_path, records)

    with pytest.raises(FixtureValidationError, match="record checksum drift"):
        validate_package(root)


def test_validator_rejects_dangling_compatibility_target_reference(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["target_projection"]["layers"] = []
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="explicit target Layers"):
        validate_package(root)


def test_ready_gate_accepts_two_bound_distinct_review_artifacts(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)

    counts = validate_package(root, require_ready=True)

    assert counts["Claim"] == 20


def test_ready_gate_rejects_duplicate_reviewer_invocation(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["reviews"][1]["reviewer_instance_id"] = registry["reviews"][0]["reviewer_instance_id"]
    artifact = root / registry["reviews"][1]["artifact"]
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace(
            "invocation-validator",
            "invocation-semantic",
        ),
        encoding="utf-8",
    )
    registry["reviews"][1]["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="reviewer invocation identities must be distinct"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_semantic_content_drift_after_review(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package = _read_package(root)
    package["entities"][0]["label"] = "Changed after review"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="does not match current reviewed content"):
        validate_package(root, require_ready=True)


def test_validator_rejects_world_slice_that_omits_modeled_region(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["world_slice"]["spatial_bounds"]["region_refs"].remove("region-south-coast")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="spatial bounds omit modeled Place or Region context"):
        validate_package(root)


def test_validator_rejects_incomplete_alternative_date_uncertainty_basis(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item for item in package["uncertainties"] if item["id"] == "uncertainty-arrival-date"
    )
    uncertainty["basis_claim_refs"].remove("claim-arrival-event-1504")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must bind every alternative-date Claim"):
        validate_package(root)


def test_validator_rejects_co_presence_claim_without_bound_premises(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-workshop-co-presence")
    claim["target_refs"] = ["event-far-observation"]
    claim["input_claim_refs"] = []
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="target the observation and bind every input premise"):
        validate_package(root)


def test_validator_rejects_process_stage_outside_process_time(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["processes"][0]["stages"][1]["temporal_extent"]["end"] = "1511"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must remain within"):
        validate_package(root)


def test_validator_rejects_process_stage_claim_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["processes"][0]["stages"][1]["claim_refs"] = ["claim-process-south-stage"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="exactly bind its temporal and spatial premises"):
        validate_package(root)


def test_validator_rejects_view_context_outside_view_time(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    view = package["synchronized_views"][0]
    view["local_context_refs"][0] = "event-north-harbor-charter"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="does not intersect view time"):
        validate_package(root)


def test_validator_rejects_empty_local_global_comparison(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0]["comparison_scope"]["reference_refs"] = []
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="local_global comparison needs references"):
        validate_package(root)


def test_validator_rejects_unordered_camera_bounds(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0]["camera_state"]["bbox"] = [20.0, -10.0, 10.0, 10.0]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="camera bounds must be ordered"):
        validate_package(root)


def test_schema_rejects_open_source_shape(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["sources"][0]["untyped_extra"] = {"anything": True}
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_schema_rejects_open_entity_and_process_stage_shapes(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["entities"][0]["untyped_extra"] = True
    package["processes"][0]["stages"][0]["untyped_extra"] = True
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_validator_rejects_dangling_compatibility_extent_basis(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["target_projection"]["entity"]["spatial_extent"]["basis_claim_refs"] = [
        "compat-claim-does-not-exist"
    ]
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="dangling reference"):
        validate_package(root)


def test_ready_gate_rejects_mutable_review_scope(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["review_scope"] = ["fixtures/world_model/v1/package.json"]
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="immutable review scope"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_artifact_registry_finding_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    artifact = root / registry["reviews"][0]["artifact"]
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace("critical_findings: 0", "critical_findings: 1"),
        encoding="utf-8",
    )
    registry["reviews"][0]["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="artifact/registry drift"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_unresolvable_frozen_commit(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    fake_commit = "b" * 40
    registry["frozen_commit"] = fake_commit
    for review in registry["reviews"]:
        old_commit = review["frozen_commit"]
        review["frozen_commit"] = fake_commit
        artifact = root / review["artifact"]
        artifact.write_text(
            artifact.read_text(encoding="utf-8").replace(old_commit, fake_commit),
            encoding="utf-8",
        )
        review["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="git verification failed"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_null_reviewed_at(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package = _read_package(root)
    package["record_time"]["reviewed_at"] = None
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="needs record_time.reviewed_at"):
        validate_package(root, require_ready=True)


def test_package_is_deterministic_under_deep_copy(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    _write_package(root, copy.deepcopy(package))

    assert validate_package(root) == validate_package(ROOT)
