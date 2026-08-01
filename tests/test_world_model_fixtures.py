import copy
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.validate_world_model_fixtures import (
    FixtureValidationError,
    REQUIRED_REVIEW_SCOPE,
    _claim_assertion_expression,
    _process_stage_premise_claims,
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
    reviewed_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    package = _read_package(root)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = reviewed_at
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
                    f"reviewed_at: {reviewed_at}",
                    "decision: READY",
                    "critical_findings: 0",
                    "unresolved_material_findings: 0",
                    "findings: []",
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
                "reviewed_at": reviewed_at,
                "decision": "READY",
                "critical_findings": 0,
                "unresolved_material_findings": 0,
                "findings": [],
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
    assert counts["DerivedObservation"] == 1
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


def test_validator_rejects_state_subject_and_value_substitution(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    state = next(
        item
        for item in package["states"]
        if item["id"] == "state-north-harbor-administration"
    )
    state["subject_ref"] = "entity-mara-vale"
    state["value"] = "administered_by_unattested_authority"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="lacks exact state_binding|lacks exact STATE_ASSERTION",
    ):
        validate_package(root)


def test_validator_rejects_duplicate_locator_state_rebinding(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    state = next(
        item
        for item in package["states"]
        if item["id"] == "state-north-harbor-administration"
    )
    state["subject_ref"] = "entity-mara-vale"
    state["value"] = "present"
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-administration-state"
    )
    claim["statement"] = "Mara Vale was present in Fixture Basin during 1498–1510."
    claim["state_bindings"] = [
        {
            "state_ref": state["id"],
            "subject_ref": state["subject_ref"],
            "state_kind": state["state_kind"],
            "value": state["value"],
        }
    ]
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_text = source_path.read_text(encoding="utf-8")
    locator = "LOCATOR[alpha-administration]"
    passage_start = source_text.index(locator)
    passage_end = source_text.index("LOCATOR[", passage_start + len(locator))
    injected = source_text[passage_start:passage_end].replace(
        'STATE_ASSERTION[{"state_kind":"administration",'
        '"state_ref":"state-north-harbor-administration",'
        '"subject_ref":"entity-fixture-basin",'
        '"value":"administered_by_north_harbor_council"}]',
        'STATE_ASSERTION[{"state_kind":"administration",'
        '"state_ref":"state-north-harbor-administration",'
        '"subject_ref":"entity-mara-vale","value":"present"}]',
    )
    source_path.write_text(injected + "\n" + source_text, encoding="utf-8")
    source = next(
        item for item in package["sources"] if item["id"] == "source-field-alpha"
    )
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="duplicate locator tokens|locator must occur exactly once",
    ):
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

    with pytest.raises(FixtureValidationError, match="closed v1 exclusion registry"):
        validate_package(root)


def test_validator_rejects_placeholder_coverage_exclusions(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["known_exclusions"] = [
        {
            "id": "placeholder",
            "assertion_kind": "corpus_exclusion",
            "description": "Placeholder",
        }
    ]
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="closed v1 exclusion registry"):
        validate_package(root)


def test_validator_rejects_erased_corpus_history_boundary(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["known_exclusions"] = [
        exclusion
        for exclusion in manifest["known_exclusions"]
        if exclusion["id"] != "no-historical-completeness-or-absence-claim"
    ]
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="closed v1 exclusion registry"):
        validate_package(root)


def test_validator_rejects_empty_required_scenario_registry(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["required_scenarios"] = {}
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="closed v1 scenario registry"):
        validate_package(root)


def test_validator_rejects_required_scenario_wrong_type(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["required_scenarios"]["point_event"] = "entity-mara-vale"
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="closed v1 scenario registry"):
        validate_package(root)


def test_validator_rejects_unexpected_coverage_manifest_field(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["temporal_bounds"] = "arbitrary prose outside the closed contract"
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="envelope must be closed"):
        validate_package(root)


def test_validator_rejects_coverage_layer_erasure(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "coverage_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["included_layers"] = []
    _write_json(path, manifest)

    with pytest.raises(FixtureValidationError, match="must exactly match WorldSlice"):
        validate_package(root)


def test_validator_rejects_documented_encounter_semantic_erasure(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-mara-ren-encounter"
    )
    relation["predicate"] = "interaction"
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-documented-encounter"
    )
    claim["relation_binding"]["predicate"] = "interaction"
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace(
            '"predicate":"documented_encounter"',
            '"predicate":"interaction"',
        ),
        encoding="utf-8",
    )
    source = next(
        item for item in package["sources"] if item["id"] == "source-field-alpha"
    )
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="documented_encounter must preserve its Relation predicate|lacks exact CLAIM_ASSERTION",
    ):
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

    with pytest.raises(
        FixtureValidationError,
        match="lacks exact EXTENT_ASSERTION|do not overlap in space",
    ):
        validate_package(root)


def test_validator_rejects_alternative_date_without_distinct_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    arrival = next(event for event in package["events"] if event["id"] == "event-workshop-arrival")
    arrival["temporal_extent"]["alternatives"][0]["basis_claim_refs"] = ["claim-arrival-event"]
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="basis_claim_refs must exactly match|alternative date needs a distinct supporting Claim",
    ):
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
    entity = next(item for item in package["entities"] if item["id"] == "place-far-observatory")
    entity["label"] = "Changed after review"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="does not match current reviewed content|identity registry drift",
    ):
        validate_package(root, require_ready=True)


def test_validator_rejects_world_slice_that_omits_modeled_region(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["world_slice"]["spatial_bounds"]["region_refs"].remove("region-south-coast")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="spatial bounds omit modeled Place or Region context|lacks exact EXTENT_ASSERTION",
    ):
        validate_package(root)


def test_validator_rejects_incomplete_alternative_date_uncertainty_basis(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item for item in package["uncertainties"] if item["id"] == "uncertainty-arrival-date"
    )
    uncertainty["basis_claim_refs"].remove("claim-arrival-event-1504")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="does not correspond|basis_claim_refs must exactly match|must bind every alternative-date Claim",
    ):
        validate_package(root)


def test_validator_rejects_uncertainty_subject_retarget(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-process-mechanism"
    )
    uncertainty["subject_or_claim_ref"] = "claim-mara-identity"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match=(
            "does not correspond|must link back|basis_claim_refs must exactly match|"
            "must be its system derivation Claim"
        ),
    ):
        validate_package(root)


def test_validator_rejects_foreign_uncertainty_backlink(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    event = next(
        item for item in package["events"] if item["id"] == "event-far-observation"
    )
    event["uncertainty_refs"].append("uncertainty-process-mechanism")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="does not correspond|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_missing_uncertainty_subject_backlink(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    claim["uncertainty_refs"] = []
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must link back|backlinks must exactly match",
    ):
        validate_package(root)


@pytest.mark.parametrize(
    ("claim_id", "uncertainty_id"),
    [
        ("claim-charter-event", "uncertainty-arrival-date"),
        ("claim-documented-encounter", "uncertainty-arrival-date"),
        ("claim-documented-encounter", "uncertainty-influence-ren-council"),
        ("claim-region-v1", "uncertainty-process-mechanism"),
        ("claim-process-north-stage", "uncertainty-region-alternative"),
        ("claim-trajectory-north", "uncertainty-trajectory-route"),
    ],
)
def test_validator_rejects_foreign_claim_uncertainty_backlink(
    tmp_path: Path,
    claim_id: str,
    uncertainty_id: str,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == claim_id)
    claim["uncertainty_refs"].append(uncertainty_id)
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="does not correspond|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_temporal_uncertainty_subject_swap(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-arrival-date"
    )
    uncertainty["subject_or_claim_ref"] = "claim-mara-identity"
    identity_claim = next(
        item for item in package["claims"] if item["id"] == "claim-mara-identity"
    )
    identity_claim["uncertainty_refs"].append("uncertainty-arrival-date")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="primary Event Claim"):
        validate_package(root)


def test_validator_rejects_process_uncertainty_stage_subject(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-process-mechanism"
    )
    uncertainty["subject_or_claim_ref"] = "claim-process-north-stage"
    uncertainty["basis_claim_refs"] = []
    grouping = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    grouping["uncertainty_refs"] = []
    north = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-north-stage"
    )
    north["uncertainty_refs"].append("uncertainty-process-mechanism")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="system derivation Claim"):
        validate_package(root)


def test_validator_rejects_missing_world_slice_uncertainty_backlink(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["world_slice"]["uncertainty_refs"] = []
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must link back|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_process_uncertainty_on_region_version(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v1"
    )
    version["uncertainty_refs"].append("uncertainty-process-mechanism")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="backlinks must exactly match"):
        validate_package(root)


def test_validator_rejects_trajectory_gap_uncertainty_on_documented_segment(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-trajectory-route"
    )
    uncertainty["basis_claim_refs"].append("claim-trajectory-north")
    trajectory = next(
        item for item in package["trajectories"] if item["id"] == "trajectory-mara-vale"
    )
    segment = next(
        item
        for item in trajectory["segments"]
        if item["id"] == "trajectory-segment-north"
    )
    segment["uncertainty_refs"].append("uncertainty-trajectory-route")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="basis_claim_refs must exactly match|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_geometry_uncertainty_propagated_to_old_version(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-region-alternative"
    )
    uncertainty["basis_claim_refs"].append("claim-region-v1")
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v1"
    )
    version["uncertainty_refs"].append("uncertainty-region-alternative")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="basis_claim_refs must exactly match|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_self_certified_geometry_uncertainty_version_set(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-region-alternative"
    )
    uncertainty["alternatives"].append("region-geometry-v1")
    uncertainty["basis_claim_refs"].append("claim-region-v1")
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v1"
    )
    version["uncertainty_refs"].append("uncertainty-region-alternative")
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-region-v1"
    )
    claim["uncertainty_refs"].append("uncertainty-region-alternative")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="disputed version set"):
        validate_package(root)


def test_validator_rejects_erased_overlapping_primary_from_geometry_uncertainty(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-region-alternative"
    )
    uncertainty["alternatives"].remove("region-geometry-v2")
    uncertainty["basis_claim_refs"].remove("claim-region-v2")
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v2"
    )
    version["uncertainty_refs"].remove("uncertainty-region-alternative")
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-region-v2"
    )
    claim["uncertainty_refs"].remove("uncertainty-region-alternative")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="disputed version set"):
        validate_package(root)


def test_validator_rejects_co_presence_claim_without_bound_premises(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-workshop-co-presence")
    claim["target_refs"] = ["event-far-observation"]
    claim["input_claim_refs"] = []
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must exclusively target its owner|target the observation and bind every input premise",
    ):
        validate_package(root)


def test_validator_rejects_unexecutable_similarity_observation(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["derived_observations"].append(
        {
            "id": "observation-unbound-similarity",
            "type": "DerivedObservation",
            "observation_kind": "similarity",
            "input_refs": [
                "event-north-harbor-charter",
                "event-far-observation",
            ],
            "claim_ref": "claim-process-analytical-grouping",
            "relation_created": False,
        }
    )
    grouping = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    grouping["target_refs"].append("observation-unbound-similarity")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
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
    package["processes"][0]["stages"][1]["claim_refs"] = ["claim-region-south"]
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target canonical owner|exactly bind its temporal and spatial premises",
    ):
        validate_package(root)


def test_validator_rejects_analytical_process_input_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    claim["input_claim_refs"] = ["claim-mara-identity"]
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="basis_claim_refs must exactly match|direct extent basis must be the system observation bound to every stage",
    ):
        validate_package(root)


def test_analytical_process_premises_include_spatial_only_claims() -> None:
    process = {
        "stages": [
            {
                "temporal_extent": {"basis_claim_refs": ["claim-temporal"]},
                "spatial_extent": {"basis_claim_refs": ["claim-spatial"]},
            }
        ]
    }

    assert _process_stage_premise_claims(process) == {
        "claim-temporal",
        "claim-spatial",
    }


def test_validator_rejects_claim_input_dependency_cycle(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    claim["input_claim_refs"] = ["claim-process-analytical-grouping"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="dependency cycle"):
        validate_package(root)


def test_validator_rejects_coordinated_process_derivation_bypass(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    grouping = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-process-analytical-grouping"
    )
    grouping["input_claim_refs"] = ["claim-mara-identity"]
    north = next(
        item for item in package["claims"] if item["id"] == "claim-process-north-stage"
    )
    north["claim_kind"] = "observation"
    north["origin"] = "system"
    north["evidence_state"] = "not_applicable"
    north["input_claim_refs"] = ["claim-process-north-stage", "claim-process-south-stage"]
    evidence = next(
        item
        for item in package["evidence_links"]
        if item["id"] == "evidence-process-north"
    )
    evidence["claim_id"] = "claim-mara-identity"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="dependency cycle|inputs must exactly match context premises|direct extent basis",
    ):
        validate_package(root)


def test_validator_rejects_misbound_top_level_claim_ref(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    place = next(item for item in package["entities"] if item["id"] == "place-south-port")
    place["claim_refs"] = ["claim-process-south-stage"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="claim_ref .* must target canonical owner"):
        validate_package(root)


def test_validator_rejects_misbound_layer_claim_ref(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["layers"][0]["claim_refs"] = ["claim-global-event"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="claim_ref .* must target canonical owner"):
        validate_package(root)


def test_validator_rejects_misbound_trajectory_segment_claim_ref(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["trajectories"][0]["segments"][0]["claim_refs"].append(
        "claim-mara-identity"
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="claim_ref .* must target canonical owner"):
        validate_package(root)


def test_validator_rejects_misbound_region_version_claim_ref(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["regions"][0]["geometry_versions"][0]["claim_refs"].append(
        "claim-mara-identity"
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="claim_ref .* must target canonical owner"):
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

    with pytest.raises(
        FixtureValidationError,
        match="immutable review scope|review registry envelope must be closed",
    ):
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

    with pytest.raises(FixtureValidationError, match="needs UTC ISO-8601 record_time.reviewed_at"):
        validate_package(root, require_ready=True)


def test_validator_rejects_invalid_created_at(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["record_time"]["created_at"] = "not-a-date"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="needs UTC ISO-8601 record_time.created_at",
    ):
        validate_package(root)


def test_ready_gate_rejects_invalid_reviewed_at(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package = _read_package(root)
    package["record_time"]["reviewed_at"] = "not-a-date"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match=(
            "needs UTC ISO-8601 record_time.reviewed_at|"
            "record_time.reviewed_at must be null or a UTC ISO-8601 timestamp"
        ),
    ):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_null_and_empty_reviewer_identities(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["reviews"][0]["review_id"] = None
    registry["reviews"][0]["reviewer_id"] = None
    registry["reviews"][0]["reviewer_instance_id"] = None
    registry["reviews"][1]["review_id"] = ""
    registry["reviews"][1]["reviewer_id"] = ""
    registry["reviews"][1]["reviewer_instance_id"] = ""
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="must be a non-empty stable identifier"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_boolean_finding_counts(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    for review in registry["reviews"]:
        review["critical_findings"] = False
        review["unresolved_material_findings"] = False
        artifact = root / review["artifact"]
        artifact.write_text(
            artifact.read_text(encoding="utf-8")
            .replace("critical_findings: 0", "critical_findings: false")
            .replace("unresolved_material_findings: 0", "unresolved_material_findings: false"),
            encoding="utf-8",
        )
        review["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(path, registry)

    with pytest.raises(FixtureValidationError, match="must be a non-negative integer"):
        validate_package(root, require_ready=True)


def test_schema_rejects_incomplete_temporal_alternative(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    arrival = next(event for event in package["events"] if event["id"] == "event-workshop-arrival")
    arrival["temporal_extent"]["alternatives"][0].pop("precision")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_schema_rejects_open_synchronized_view_shape(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0]["untyped_extra"] = True
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_schema_rejects_open_spatial_extent_shape(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["events"][0]["spatial_extent"]["untyped_extra"] = True
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_validator_rejects_reversed_process_stage_interval(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    stage = package["processes"][0]["stages"][1]
    stage["temporal_extent"]["start"] = "1505"
    stage["temporal_extent"]["end"] = "1504"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="start must not follow end"):
        validate_package(root)


def test_validator_rejects_context_outside_world_slice_time(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    event = next(item for item in package["events"] if item["id"] == "event-north-harbor-charter")
    event["temporal_extent"]["start"] = "1511"
    event["temporal_extent"]["end"] = "1511"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="lacks exact EXTENT_ASSERTION|temporal bounds omit modeled context",
    ):
        validate_package(root)


def test_validator_rejects_invented_compatibility_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    entity = projection["target_projection"]["entity"]
    claim = {
        "id": "compat-claim-villa-savoye-color",
        "type": "Claim",
        "statement": "Villa Savoye is blue.",
        "target_refs": [entity["id"]],
        "claim_kind": "factual",
        "origin": "imported",
        "review_state": "draft",
        "confidence": "unknown",
        "evidence_state": "missing",
        "evidence_link_refs": [],
        "uncertainty_refs": ["compat-uncertainty-villa-savoye-provenance"],
    }
    projection["target_projection"]["claims"].append(claim)
    entity["claim_refs"].append(claim["id"])
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="deterministic pinned mapping"):
        validate_package(root)


def test_validator_rejects_unmapped_compatibility_entity_field(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["target_projection"]["entity"]["color"] = "blue"
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="deterministic pinned mapping"):
        validate_package(root)


def test_schema_rejects_non_epsg4326_camera_reference(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0]["camera_state"]["coordinate_reference"] = "EPSG:3857"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="fails schema.json"):
        validate_package(root)


def test_validator_rejects_relation_time_missing_from_supporting_locator(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace("during 1504–1505 ", ""),
        encoding="utf-8",
    )
    package = _read_package(root)
    source = next(item for item in package["sources"] if item["id"] == "source-field-alpha")
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="temporal extent is not stated"):
        validate_package(root)


def test_validator_rejects_relation_endpoint_not_bound_by_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item for item in package["relations"] if item["id"] == "relation-mara-ren-encounter"
    )
    relation["object_ref"] = "entity-traveler-sol"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target (?:its|canonical) owner|target the Relation and both endpoints",
    ):
        validate_package(root)


def test_validator_rejects_reversed_directed_relation_roles(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["subject_ref"], relation["object_ref"] = relation["object_ref"], relation["subject_ref"]
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="directed endpoint roles|backlinks must exactly match",
    ):
        validate_package(root)


def test_validator_rejects_symmetric_influence_relation(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["directionality"] = "symmetric"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="requires directed directionality"):
        validate_package(root)


def test_validator_rejects_coordinated_label_role_bypass(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["subject_ref"], relation["object_ref"] = relation["object_ref"], relation["subject_ref"]
    council = next(
        item for item in package["entities"] if item["id"] == "entity-north-harbor-council"
    )
    council["label"] = "1504–1505"
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="relation_binding must exactly match|backlinks must exactly match",
    ):
        validate_package(root)


@pytest.mark.parametrize(
    ("relation_path", "replacement"),
    (
        (("temporal_extent", "precision"), "day"),
        (("temporal_extent", "certainty"), "certain"),
        (("mechanism",), "Telepathy determined the protocol."),
        (("scope",), "All council decisions worldwide"),
    ),
)
def test_validator_rejects_unbound_relation_semantic_drift(
    tmp_path: Path,
    relation_path: tuple[str, ...],
    replacement: str,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    target = relation
    for key in relation_path[:-1]:
        target = target[key]
    target[relation_path[-1]] = replacement
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="relation_binding must exactly match"):
        validate_package(root)


def test_validator_rejects_relation_binding_not_stated_by_locator(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-influence-ren-council"
    )
    relation["scope"] = "North Harbor protocol title only"
    claim["relation_binding"]["scope"] = relation["scope"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="supporting locator must state"):
        validate_package(root)


def test_validator_rejects_relation_missing_from_claim_targets(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-documented-encounter"
    )
    claim["target_refs"].remove("relation-mara-ren-encounter")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target (?:its|canonical) owner|target the Relation and both endpoints",
    ):
        validate_package(root)


def test_validator_rejects_unstated_relation_point_geometry(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item for item in package["relations"] if item["id"] == "relation-mara-ren-encounter"
    )
    relation["spatial_extent"] = {
        "kind": "point",
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
        "precision": "fixture_defined",
        "basis_claim_refs": ["claim-documented-encounter"],
    }
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target (?:its|canonical) owner|exact geometry must be stated",
    ):
        validate_package(root)


def test_validator_rejects_relation_geometry_hidden_in_temporal_digits(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["spatial_extent"] = {
        "kind": "point",
        "geometry": {"type": "Point", "coordinates": [15, 4]},
        "precision": "fixture_defined",
        "basis_claim_refs": ["claim-influence-ren-council"],
    }
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target (?:its|canonical) owner|exact geometry must be stated",
    ):
        validate_package(root)


def test_validator_rejects_invalid_geojson_shape_and_range(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    event = next(item for item in package["events"] if item["id"] == "event-north-harbor-charter")
    event["spatial_extent"]["geometry"] = {
        "type": "LineString",
        "coordinates": [[181, 95]],
    }
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must use GeoJSON Point|invalid GeoJSON"):
        validate_package(root)


def test_validator_rejects_narrowed_relation_interval(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["temporal_extent"]["end"] = "1504"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="temporal extent is not stated"):
        validate_package(root)


def test_validator_rejects_relation_interval_narrowed_to_instant(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    relation = next(
        item
        for item in package["relations"]
        if item["id"] == "relation-ren-influences-council-protocol"
    )
    relation["temporal_extent"].update(
        {
            "kind": "instant",
            "start": "1504",
            "end": "1504",
        }
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="temporal extent is not stated"):
        validate_package(root)


def test_validator_rejects_unsupported_event_participant(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-charter-event")
    claim["target_refs"].remove("entity-mara-vale")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="participant entity-mara-vale must be bound"):
        validate_package(root)


def test_validator_rejects_event_geometry_not_stated_by_source(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    event = next(item for item in package["events"] if item["id"] == "event-north-harbor-charter")
    event["spatial_extent"]["geometry"]["coordinates"] = [15, 4]
    claim = next(item for item in package["claims"] if item["id"] == "claim-charter-event")
    claim["statement"] = claim["statement"].replace(
        'GEOMETRY_ASSERTION[{"coordinates":[10.0,50.0],"type":"Point"}]',
        'GEOMETRY_ASSERTION[{"coordinates":[15,4],"type":"Point"}]',
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="exact geometry must be stated"):
        validate_package(root)


def test_validator_rejects_geometry_basis_claim_not_targeting_owner(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-global-event")
    claim["target_refs"].remove("event-far-observation")
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target (?:its|canonical) owner|exact geometry must be stated",
    ):
        validate_package(root)


def test_validator_rejects_geometry_transfer_between_region_versions(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version_a = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v1"
    )
    version_b = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v2"
    )
    version_a["spatial_extent"] = copy.deepcopy(version_b["spatial_extent"])
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="lacks exact EXTENT_ASSERTION"):
        validate_package(root)


def test_validator_rejects_geometry_transfer_between_events(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    charter = next(
        item for item in package["events"] if item["id"] == "event-north-harbor-charter"
    )
    distant = next(
        item for item in package["events"] if item["id"] == "event-far-observation"
    )
    charter["spatial_extent"] = copy.deepcopy(distant["spatial_extent"])
    claim = next(item for item in package["claims"] if item["id"] == "claim-global-event")
    claim["target_refs"].append("event-north-harbor-charter")
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="lacks exact EXTENT_ASSERTION"):
        validate_package(root)


def test_validator_rejects_state_spatial_basis_from_region_claims(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    state = next(
        item
        for item in package["states"]
        if item["id"] == "state-north-harbor-administration"
    )
    state["spatial_extent"]["basis_claim_refs"] = ["claim-region-v1", "claim-region-v2"]
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="must target owner|Claim refs must exactly bind State extents and value",
    ):
        validate_package(root)


def test_validator_rejects_hidden_trajectory_gap_interval(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    trajectory = next(
        item for item in package["trajectories"] if item["id"] == "trajectory-mara-vale"
    )
    gap = next(
        item for item in trajectory["segments"] if item["id"] == "trajectory-segment-gap"
    )
    gap["temporal_extent"]["start"] = "1502"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="lacks exact EXTENT_ASSERTION"):
        validate_package(root)


def test_validator_rejects_context_mode_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    version = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v1"
    )
    version["reconstruction_mode"] = "analytical_model"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="lacks exact EXTENT_ASSERTION"):
        validate_package(root)


def test_validator_rejects_geometry_identical_alternative(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    primary = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v2"
    )
    alternative = next(
        item
        for item in region["geometry_versions"]
        if item["id"] == "region-geometry-v2-alternative"
    )
    alternative["spatial_extent"]["geometry"] = copy.deepcopy(
        primary["spatial_extent"]["geometry"]
    )
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="alternative geometry must differ from overlapping primary reconstruction",
    ):
        validate_package(root)


def test_validator_rejects_z_only_alternative_geometry_difference(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    primary = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v2"
    )
    alternative = next(
        item
        for item in region["geometry_versions"]
        if item["id"] == "region-geometry-v2-alternative"
    )
    primary_ring = primary["spatial_extent"]["geometry"]["coordinates"][0]
    alternative["spatial_extent"]["geometry"]["coordinates"] = [
        [[*position, 7.0] for position in primary_ring]
    ]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="invalid GeoJSON Polygon coordinates"):
        validate_package(root)


def test_validator_rejects_compatibility_snapshot_field_erasure(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["input_snapshot"].pop("date_start")
    projection["input_snapshot"].pop("date_end")
    entity = projection["target_projection"]["entity"]
    entity["temporal_extent"]["start"] = None
    entity["temporal_extent"]["end"] = None
    projection["target_projection"]["claims"][0]["statement"] = (
        "The legacy record gives the interval None–None."
    )
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="must exactly mirror the pinned record fields"):
        validate_package(root)


def test_validator_rejects_compatibility_snapshot_coordinate_erasure(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["input_snapshot"].pop("latitude")
    projection["input_snapshot"].pop("longitude")
    entity = projection["target_projection"]["entity"]
    entity["spatial_extent"]["geometry"]["coordinates"] = [None, None]
    projection["target_projection"]["claims"][1]["statement"] = (
        "The legacy record gives the point [None, None]."
    )
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="must exactly mirror the pinned record fields"):
        validate_package(root)


def test_validator_rejects_compatibility_repository_spoof(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["source_dataset"]["repository"] = "attacker/forged-source"
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="source provenance drift"):
        validate_package(root)


def test_validator_rejects_compatibility_record_identity_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["source_dataset"]["record_id"] = "rec-forged"
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="Villa Savoye source identity drift"):
        validate_package(root)


def test_validator_rejects_blank_compatibility_losses(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["losses_and_unknowns"] = ["", "", "", ""]
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="preserve the exact material losses"):
        validate_package(root)


def test_validator_rejects_compatibility_determinism_rule_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["determinism_rule"] = "Trust the projection."
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="determinism rule drift"):
        validate_package(root)


def test_validator_rejects_extra_compatibility_envelope_field(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    projection["provenance_override"] = True
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="envelope must be closed"):
        validate_package(root)


def test_validator_rejects_compatibility_epistemic_promotion(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    claim = projection["target_projection"]["claims"][0]
    claim["review_state"] = "reviewed"
    claim["confidence"] = "high"
    claim["uncertainty_refs"] = []
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="deterministic pinned mapping"):
        validate_package(root)


def test_validator_rejects_compatibility_uncertainty_rewrite(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "compatibility" / "architecture_atlas_projection.json"
    projection = json.loads(path.read_text(encoding="utf-8"))
    uncertainty = projection["target_projection"]["uncertainties"][0]
    uncertainty["dimension"] = "none"
    uncertainty["description"] = "No uncertainty remains."
    uncertainty["effect"] = "Promote the record automatically."
    _write_json(path, projection)

    with pytest.raises(FixtureValidationError, match="deterministic pinned mapping"):
        validate_package(root)


def test_validator_rejects_trajectory_subject_swap(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    trajectory = package["trajectories"][0]
    trajectory["subject_ref"] = "entity-keeper-ren"
    trajectory["label"] = "Keeper Ren fixture trajectory"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="subject/label drift|must bind trajectory"):
        validate_package(root)


def test_validator_rejects_absent_state_as_co_presence_input(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    state = next(
        item
        for item in package["states"]
        if item["id"] == "state-traveler-workshop-presence"
    )
    claim = next(
        item
        for item in package["claims"]
        if item["id"] == "claim-traveler-workshop-presence"
    )
    old_assertion = _claim_assertion_expression(copy.deepcopy(claim))
    state["value"] = "absent"
    claim["state_bindings"][0]["value"] = "absent"
    new_assertion = _claim_assertion_expression(claim)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_text = source_path.read_text(encoding="utf-8")
    source_text = source_text.replace(old_assertion, new_assertion).replace(
        'STATE_ASSERTION[{"state_kind":"presence",'
        '"state_ref":"state-traveler-workshop-presence",'
        '"subject_ref":"entity-traveler-sol","value":"present"}]',
        'STATE_ASSERTION[{"state_kind":"presence",'
        '"state_ref":"state-traveler-workshop-presence",'
        '"subject_ref":"entity-traveler-sol","value":"absent"}]',
    )
    source_path.write_text(source_text, encoding="utf-8")
    source = next(
        item for item in package["sources"] if item["id"] == "source-field-alpha"
    )
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="positive presence States"):
        validate_package(root)


def test_validator_rejects_unbound_world_slice_bounds(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    bounds = package["world_slice"]["temporal_bounds"]
    bounds["start"] = "1000"
    bounds["end"] = "2000"
    bounds["basis_claim_refs"] = ["claim-mara-identity"]
    package["world_slice"]["spatial_bounds"]["basis_claim_refs"] = [
        "claim-mara-identity"
    ]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must target owner|lacks exact EXTENT_ASSERTION"):
        validate_package(root)


def test_validator_rejects_historical_completeness_rationale(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["world_slice"]["selection_rationale"] = (
        "This corpus is historically complete; missing people and events did not exist."
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="selection rationale contradicts"):
        validate_package(root)


def test_validator_rejects_background_only_supported_claim(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    evidence = next(
        item
        for item in package["evidence_links"]
        if item["id"] == "evidence-mara-identity"
    )
    evidence["evidence_strength"] = "background"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="evidence_state must be derived as missing"):
        validate_package(root)


def test_validator_rejects_uncertainty_semantic_inversion(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    uncertainty = next(
        item
        for item in package["uncertainties"]
        if item["id"] == "uncertainty-region-alternative"
    )
    uncertainty["description"] = "The primary reconstruction is exact."
    uncertainty["effect"] = "Hide the alternative geometry."
    uncertainty["effect_policy"] = "preserve_temporal_alternatives"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="semantic effect drift"):
        validate_package(root)


def test_validator_rejects_hidden_uncertainty_and_context_layers(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    view = package["synchronized_views"][0]
    view["uncertainty_display"] = {
        "show_material": False,
        "show_alternatives": False,
        "show_corpus_limits": False,
    }
    view["active_layer_refs"] = ["layer-biography"]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must display material"):
        validate_package(root)


def test_validator_rejects_reviewed_claim_statement_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-mara-identity"
    )
    claim["statement"] = "An unrelated ruler caused a distant war."
    _write_package(root, package)

    with pytest.raises(
        FixtureValidationError,
        match="statement drift|lacks exact CLAIM_ASSERTION",
    ):
        validate_package(root)


def test_validator_rejects_entity_subtype_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["entities"][0]["entity_kind"] = "Institution"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="identity registry drift"):
        validate_package(root)


def test_validator_rejects_topologically_identical_alternative_geometry(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    region = next(
        item for item in package["regions"] if item["id"] == "region-fixture-basin"
    )
    primary = next(
        item for item in region["geometry_versions"] if item["id"] == "region-geometry-v2"
    )
    alternative = next(
        item
        for item in region["geometry_versions"]
        if item["id"] == "region-geometry-v2-alternative"
    )
    ring = copy.deepcopy(primary["spatial_extent"]["geometry"]["coordinates"][0])
    core = ring[:-1]
    rotated = core[2:] + core[:2]
    rotated.append(rotated[0])
    alternative["spatial_extent"]["geometry"]["coordinates"] = [rotated]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must differ from overlapping primary"):
        validate_package(root)


def test_validator_rejects_noncanonical_coverage_manifest_ref(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["world_slice"]["coverage_manifest_ref"] = "attacker/empty.json"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="coverage_manifest.json|schema.json"):
        validate_package(root)


def test_validator_rejects_reviewed_at_before_ready(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["record_time"]["reviewed_at"] = "2999-01-01T00:00:00Z"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="must remain null"):
        validate_package(root)


def test_validator_rejects_truncated_locator_token(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["evidence_links"][0]["locator"] = "LOCATOR[alpha-ident"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="exact LOCATOR token|schema.json"):
        validate_package(root)


def test_ready_gate_rejects_contradictory_artifact_narrative(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    registry_path = root / PACKAGE / "review_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    artifact = root / registry["reviews"][0]["artifact"]
    artifact.write_text(
        artifact.read_text(encoding="utf-8")
        + "Finding: CRITICAL unresolved blocker\nCHANGES_REQUIRED\n",
        encoding="utf-8",
    )
    registry["reviews"][0]["artifact_sha256"] = hashlib.sha256(
        artifact.read_bytes()
    ).hexdigest()
    _write_json(registry_path, registry)

    with pytest.raises(
        FixtureValidationError,
        match="unknown field Finding|unstructured content",
    ):
        validate_package(root, require_ready=True)


def test_ready_gate_derives_decision_from_structured_findings(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    registry_path = root / PACKAGE / "review_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    review = registry["reviews"][0]
    review["findings"] = [
        {
            "finding_id": "semantic-blocker",
            "severity": "critical",
            "status": "unresolved",
            "summary": "A material semantic blocker remains.",
        }
    ]
    artifact = root / review["artifact"]
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace(
            "findings: []",
            'findings: [{"finding_id":"semantic-blocker","severity":"critical",'
            '"status":"unresolved","summary":"A material semantic blocker remains."}]',
        ),
        encoding="utf-8",
    )
    review["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(registry_path, registry)

    with pytest.raises(FixtureValidationError, match="derived from structured findings"):
        validate_package(root, require_ready=True)


def test_package_is_deterministic_under_deep_copy(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    _write_package(root, copy.deepcopy(package))

    assert validate_package(root) == validate_package(ROOT)


def test_validator_rejects_coordinated_claim_epistemic_self_certification(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-charter-event")
    old_assertion = _claim_assertion_expression(claim)
    claim.update(
        {
            "claim_kind": "counterfactual",
            "origin": "ai",
            "review_state": "rejected",
            "confidence": "low",
        }
    )
    new_assertion = _claim_assertion_expression(claim)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace(old_assertion, new_assertion),
        encoding="utf-8",
    )
    source = next(item for item in package["sources"] if item["id"] == "source-field-alpha")
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


def test_validator_rejects_coordinated_claim_target_and_backlink_expansion(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    claim = next(item for item in package["claims"] if item["id"] == "claim-charter-event")
    old_assertion = _claim_assertion_expression(claim)
    claim["target_refs"].append("entity-keeper-ren")
    keeper = next(
        item for item in package["entities"] if item["id"] == "entity-keeper-ren"
    )
    keeper["claim_refs"].append(claim["id"])
    new_assertion = _claim_assertion_expression(claim)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace(old_assertion, new_assertion),
        encoding="utf-8",
    )
    source = next(item for item in package["sources"] if item["id"] == "source-field-alpha")
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


def test_validator_rejects_coordinated_state_semantic_self_certification(
    tmp_path: Path,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    state = next(
        item
        for item in package["states"]
        if item["id"] == "state-north-harbor-administration"
    )
    claim = next(
        item for item in package["claims"] if item["id"] == "claim-administration-state"
    )
    old_binding = copy.deepcopy(claim["state_bindings"][0])
    old_state_assertion = "STATE_ASSERTION[" + json.dumps(
        old_binding, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "]"
    old_claim_assertion = _claim_assertion_expression(claim)
    state["state_kind"] = "presence"
    state["value"] = "present"
    new_binding = {
        "state_ref": state["id"],
        "subject_ref": state["subject_ref"],
        "state_kind": state["state_kind"],
        "value": state["value"],
    }
    claim["state_bindings"] = [new_binding]
    new_state_assertion = "STATE_ASSERTION[" + json.dumps(
        new_binding, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "]"
    new_claim_assertion = _claim_assertion_expression(claim)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8")
        .replace(old_state_assertion, new_state_assertion)
        .replace(old_claim_assertion, new_claim_assertion),
        encoding="utf-8",
    )
    source = next(item for item in package["sources"] if item["id"] == "source-field-alpha")
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


@pytest.mark.parametrize(
    ("collection", "item_id", "field", "replacement"),
    (
        ("events", "event-north-harbor-charter", "label", "Mara assassinated Keeper Ren"),
        ("layers", "layer-biography", "coverage_rule", "The layer proves complete historical absence."),
        ("regions", "region-fixture-basin", "region_kind", "imaginary_world_empire"),
    ),
)
def test_validator_rejects_unbound_closed_v1_display_semantics(
    tmp_path: Path,
    collection: str,
    item_id: str,
    field: str,
    replacement: str,
) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    item = next(record for record in package[collection] if record["id"] == item_id)
    item[field] = replacement
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


def test_validator_rejects_missing_event_participant_from_closed_graph(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    event = next(
        item
        for item in package["events"]
        if item["id"] == "event-documented-workshop-meeting"
    )
    event["participant_refs"] = []
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


def test_validator_rejects_local_global_context_role_swap(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    view = package["synchronized_views"][0]
    view["local_context_refs"], view["global_context_refs"] = (
        view["global_context_refs"],
        view["local_context_refs"],
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="closed reviewed v1 envelope"):
        validate_package(root)


def test_validator_rejects_selected_object_outside_visible_context(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    package["synchronized_views"][0]["selected_object_refs"] = [
        "event-north-harbor-charter"
    ]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="belong to or participate"):
        validate_package(root)


def test_validator_rejects_unclosed_source_locator_delimiter(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    source_path = root / PACKAGE / "sources" / "field-notebook-alpha.md"
    source_path.write_text(
        source_path.read_text(encoding="utf-8")
        + "\nLOCATOR[unclosed\nContradictory trailing fixture text.\n",
        encoding="utf-8",
    )
    source = next(item for item in package["sources"] if item["id"] == "source-field-alpha")
    source["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="malformed or nested locator"):
        validate_package(root)


def test_validator_rejects_collinear_backtracking_polygon_ring(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    version = next(
        version
        for region in package["regions"]
        for version in region["geometry_versions"]
        if version["id"] == "region-geometry-v2"
    )
    version["spatial_extent"]["geometry"]["coordinates"][0] = [
        [9.0, 49.0],
        [12.0, 49.0],
        [11.0, 49.0],
        [12.0, 51.0],
        [9.0, 51.0],
        [9.0, 49.0],
    ]
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="collinear backtracking"):
        validate_package(root)


def test_validator_rejects_polygon_hole_outside_exterior(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    version = next(
        version
        for region in package["regions"]
        for version in region["geometry_versions"]
        if version["id"] == "region-geometry-v2"
    )
    version["spatial_extent"]["geometry"]["coordinates"].append(
        [[20.0, 20.0], [21.0, 20.0], [21.0, 21.0], [20.0, 21.0], [20.0, 20.0]]
    )
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="strictly contained"):
        validate_package(root)


def test_validator_rejects_duplicate_semantic_evidence_link(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    duplicate = copy.deepcopy(package["evidence_links"][0])
    duplicate["id"] = "evidence-duplicate-reviewed-tuple"
    package["evidence_links"].append(duplicate)
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="duplicates an existing semantic EvidenceLink"):
        validate_package(root)


def test_ready_gate_rejects_future_reviewed_at(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package = _read_package(root)
    package["record_time"]["reviewed_at"] = "2999-01-01T00:00:00Z"
    _write_package(root, package)

    with pytest.raises(FixtureValidationError, match="reviewed_at must not be in the future"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_duplicate_semantic_package_key(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "package.json"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '"selection_rationale": "A deliberately fictional',
            '"selection_rationale": "The slice proves exhaustive historical completeness.",\n'
            '    "selection_rationale": "A deliberately fictional',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="duplicate key selection_rationale"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_duplicate_registry_status_key(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    path = root / PACKAGE / "review_registry.json"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '"status": "READY",',
            '"status": "REVIEW_REQUIRED",\n  "status": "READY",',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="duplicate key status"):
        validate_package(root, require_ready=True)


def test_validator_rejects_non_finite_json_number(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    path = root / PACKAGE / "package.json"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '"schema_version": "1.0.0",',
            '"schema_version": "1.0.0",\n  "nonfinite_probe": NaN,',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="non-finite number NaN"):
        validate_package(root)


def test_ready_gate_rejects_reviews_predating_frozen_commit(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    retroactive_time = "2026-07-30T00:00:00Z"
    package = _read_package(root)
    package["record_time"]["reviewed_at"] = retroactive_time
    _write_package(root, package)

    registry_path = root / PACKAGE / "review_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for review in registry["reviews"]:
        previous_time = review["reviewed_at"]
        review["reviewed_at"] = retroactive_time
        artifact = root / review["artifact"]
        artifact.write_text(
            artifact.read_text(encoding="utf-8").replace(
                f"reviewed_at: {previous_time}",
                f"reviewed_at: {retroactive_time}",
            ),
            encoding="utf-8",
        )
        review["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    _write_json(registry_path, registry)

    with pytest.raises(FixtureValidationError, match="must not predate the frozen commit"):
        validate_package(root, require_ready=True)


@pytest.mark.parametrize("overflow", ("1e999", "-1e999"))
def test_ready_gate_rejects_json_exponent_overflow(
    tmp_path: Path,
    overflow: str,
) -> None:
    root = _copy_fixture(tmp_path)
    schema_path = root / PACKAGE / "schema.json"
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace(
            '"$schema": "https://json-schema.org/draft/2020-12/schema",',
            '"$schema": "https://json-schema.org/draft/2020-12/schema",\n'
            f'  "x-nonfinite-probe": {overflow},',
            1,
        ),
        encoding="utf-8",
    )
    _make_ready_reviews(root)

    with pytest.raises(FixtureValidationError, match=f"non-finite number {overflow}"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_post_freeze_decimal_precision_drift(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package_path = root / PACKAGE / "package.json"
    package_path.write_text(
        package_path.read_text(encoding="utf-8").replace(
            "11.4",
            "11.4000000000000001",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="loses precision"):
        validate_package(root, require_ready=True)


@pytest.mark.parametrize("alias", ("11.40", "1.14e1", "114e-1"))
def test_ready_gate_rejects_post_freeze_decimal_lexical_alias(
    tmp_path: Path,
    alias: str,
) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    package_path = root / PACKAGE / "package.json"
    package_path.write_text(
        package_path.read_text(encoding="utf-8").replace("11.4", alias, 1),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="canonical binary64 spelling"):
        validate_package(root, require_ready=True)


def test_ready_gate_rejects_review_registry_numeric_lexical_alias(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _make_ready_reviews(root)
    registry_path = root / PACKAGE / "review_registry.json"
    registry_path.write_text(
        registry_path.read_text(encoding="utf-8").replace(
            '"required_review_count": 2,',
            '"required_review_count": 2e0,',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="canonical binary64 spelling"):
        validate_package(root, require_ready=True)


@pytest.mark.parametrize("value", ("1e-999", "-1e-999"))
def test_ready_gate_rejects_json_underflow_to_zero(
    tmp_path: Path,
    value: str,
) -> None:
    root = _copy_fixture(tmp_path)
    schema_path = root / PACKAGE / "schema.json"
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace(
            '"$schema": "https://json-schema.org/draft/2020-12/schema",',
            '"$schema": "https://json-schema.org/draft/2020-12/schema",\n'
            f'  "x-underflow-probe": {value},',
            1,
        ),
        encoding="utf-8",
    )
    _make_ready_reviews(root)

    with pytest.raises(FixtureValidationError, match="loses precision"):
        validate_package(root, require_ready=True)


@pytest.mark.parametrize("value", ("-0", "-0.0"))
def test_validator_rejects_ambiguous_signed_zero(
    tmp_path: Path,
    value: str,
) -> None:
    root = _copy_fixture(tmp_path)
    schema_path = root / PACKAGE / "schema.json"
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace(
            '"$schema": "https://json-schema.org/draft/2020-12/schema",',
            '"$schema": "https://json-schema.org/draft/2020-12/schema",\n'
            f'  "x-signed-zero-probe": {value},',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError, match="ambiguous signed zero"):
        validate_package(root)
