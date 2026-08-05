from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts import validate_relation_fixtures as validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path("fixtures/world_model/relations/v1/package.json")
REGISTRY_REL = Path("fixtures/world_model/relations/v1/review_registry.json")
README_REL = Path("fixtures/world_model/relations/v1/README.md")
OWNER_REL = Path("docs/RELATION_LADDER_CONTRACT.md")
WORK_REL = Path("docs/work/2026-08-05_RELATION_LADDER_REVIEW.md")
COMPAT_REL = Path("fixtures/world_model/relations/v1/compatibility/architecture_atlas_projection.json")


def _load(root: Path, relative: Path) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write(root: Path, relative: Path, value: dict) -> None:
    (root / relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"))
    package = _load(target, PACKAGE_REL)
    package["status"] = "REVIEW_REQUIRED"
    package["record_time"]["reviewed_at"] = None
    _write(target, PACKAGE_REL, package)
    registry = _load(target, REGISTRY_REL)
    registry.update(status="REVIEW_REQUIRED", frozen_commit=None, reviewed_content_sha256=None, reviews=[])
    _write(target, REGISTRY_REL, registry)
    for relative in (README_REL, OWNER_REL):
        path = target / relative
        path.write_text(path.read_text(encoding="utf-8").replace("Status: `READY`", "Status: `REVIEW_REQUIRED`", 1), encoding="utf-8")
    work = target / WORK_REL
    text = work.read_text(encoding="utf-8")
    text = text.replace("- State: `READY`.", "- State: `REVIEW_REQUIRED`.", 1)
    text = validator.re.sub(r"- Frozen commit: `[^`]+`\.", "- Frozen commit: `PENDING`.", text, count=1)
    text = validator.re.sub(r"- Reviewed digest: `[^`]+`\.", "- Reviewed digest: `PENDING`.", text, count=1)
    work.write_text(text, encoding="utf-8")
    return target


def _case(package: dict, case_id: str) -> dict:
    return next(item for item in package["cases"] if item["id"] == case_id)


def _claim(package: dict, claim_id: str) -> dict:
    return next(item for item in package["claims"] if item["id"] == claim_id)


def _run_git(root: Path, *args: str, when: datetime | None = None) -> str:
    env = None
    if when is not None:
        import os
        env = {**os.environ, "GIT_AUTHOR_DATE": when.isoformat(), "GIT_COMMITTER_DATE": when.isoformat()}
    return subprocess.run(("git", "-C", str(root), *args), check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).stdout.strip()


def _prepare_ready(root: Path) -> tuple[str, str]:
    now = datetime.now(UTC).replace(microsecond=0)
    frozen_time = now - timedelta(minutes=5)
    ready_time = now - timedelta(minutes=1)
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "ARTEMIS Test")
    _run_git(root, "config", "user.email", "artemis-test@example.invalid")
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "frozen relation candidate", when=frozen_time)
    frozen = _run_git(root, "rev-parse", "HEAD")
    digest = validator.compute_review_digest(root)

    reviews = []
    artifact_dir = root / "docs/work/reviews"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for index, track in enumerate(("semantic-model", "validator-integrity")):
        review = {
            "review_id": f"relation-v1-{track}", "reviewer_id": f"test-{track}-reviewer",
            "reviewer_instance_id": f"test-{track}-instance", "track": track,
            "independence_method": "separate_agent_task", "artifact": f"docs/work/reviews/relation-v1-{track}.json",
            "artifact_sha256": "", "frozen_commit": frozen, "reviewed_content_sha256": digest,
            "reviewed_at": (now - timedelta(minutes=3-index)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "decision": "READY", "finding_counts": {"critical": 0, "material": 0, "minor": 0},
            "findings": [], "independence_attestation": True,
        }
        artifact = {"artifact_format": "artemis-review-attestation-v1", **{key: value for key, value in review.items() if key not in {"artifact", "artifact_sha256"}}}
        artifact_path = root / review["artifact"]
        _write(root, Path(review["artifact"]), artifact)
        review["artifact_sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        reviews.append(review)

    package = _load(root, PACKAGE_REL)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = ready_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    _write(root, PACKAGE_REL, package)
    for relative in (README_REL, OWNER_REL):
        path = root / relative
        path.write_text(path.read_text(encoding="utf-8").replace("Status: `REVIEW_REQUIRED`", "Status: `READY`", 1), encoding="utf-8")
    work = root / WORK_REL
    text = work.read_text(encoding="utf-8").replace("- State: `REVIEW_REQUIRED`.", "- State: `READY`.", 1)
    text = text.replace("- Frozen commit: `PENDING`.", f"- Frozen commit: `{frozen}`.", 1)
    text = text.replace("- Reviewed digest: `PENDING`.", f"- Reviewed digest: `{digest}`.", 1)
    work.write_text(text, encoding="utf-8")
    _write(root, REGISTRY_REL, {"schema_version": "1.0.0", "package_id": "artemis-relation-ladder-v1", "status": "READY", "frozen_commit": frozen, "reviewed_content_sha256": digest, "required_review_count": 2, "review_scope_id": "relation-ladder-v1-canonical", "reviews": reviews})
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "finalize relation READY", when=ready_time)
    return frozen, digest


def test_relation_fixture_package_validates(tmp_path: Path) -> None:
    assert validator.validate_repository(_copy_repo(tmp_path)) == []


def test_require_ready_rejects_review_required_package(tmp_path: Path) -> None:
    assert any("relation package is not READY" in item for item in validator.validate_repository(_copy_repo(tmp_path), require_ready=True))


def test_deterministic_co_presence_distinguishes_same_and_different_place() -> None:
    package = _load(ROOT, PACKAGE_REL)
    assert validator.is_co_present(_case(package, "case-same-city-no-contact")) is True
    assert validator.is_co_present(_case(package, "case-disjoint-place")) is False


@pytest.mark.parametrize(
    ("case_id", "mutation", "needle"),
    [
        ("case-plausible-workshop", lambda case: case.update(assumptions=[]), "requires explicit assumptions"),
        ("case-plausible-workshop", lambda case: case.update(asserted_level="documented_encounter"), "predicate does not support asserted level"),
        ("case-documented-encounter", lambda case: case.update(asserted_level="interaction"), "predicate does not support asserted level"),
        ("case-documented-interaction", lambda case: case.update(asserted_level="influence"), "predicate does not support asserted level"),
        ("case-supported-influence", lambda case: case.update(asserted_level="causal"), "predicate does not support asserted level"),
    ],
)
def test_validator_rejects_every_adjacent_overpromotion(tmp_path: Path, case_id: str, mutation, needle: str) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    mutation(_case(package, case_id))
    _write(root, PACKAGE_REL, package)
    assert any(needle in item for item in validator.validate_repository(root))


def test_computed_co_presence_never_creates_historical_relation(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-same-city-no-contact")
    case["level_claim_ref"] = "claim-documented-encounter"
    _write(root, PACKAGE_REL, package)
    assert any("computed co-presence must not create" in item for item in validator.validate_repository(root))


def test_validator_rejects_swapped_case_claim_binding(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _case(package, "case-documented-encounter")["level_claim_ref"] = "claim-interaction"
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("Claim target binding mismatch" in item or "Claim predicate" in item for item in errors)


def test_validator_rejects_claim_assertion_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _claim(package, "claim-influence")["qualifiers"]["scope"] = "all later work"
    _write(root, PACKAGE_REL, package)
    assert any("assertion digest mismatch" in item for item in validator.validate_repository(root))


def test_validator_rejects_locator_digest_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    source = root / "fixtures/world_model/relations/v1/sources/relation-profile.md"
    source.write_text(source.read_text(encoding="utf-8").replace("SHA256[c2df", "SHA256[0000", 1), encoding="utf-8")
    assert any("locator does not bind" in item for item in validator.validate_repository(root))


def test_possible_encounter_cannot_gain_supporting_evidence_silently(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["evidence_links"].append(copy.deepcopy(package["evidence_links"][0]))
    link = package["evidence_links"][-1]
    link.update(id="evidence-possible-workshop", claim_id="claim-possible-workshop", locator="LOCATOR[claim-documented-encounter]")
    _write(root, PACKAGE_REL, package)
    assert any("non-supported Claim claim-possible-workshop" in item for item in validator.validate_repository(root))


def test_influence_requires_direction_mechanism_and_scope(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    claim = _claim(package, "claim-influence")
    claim["qualifiers"].pop("mechanism")
    claim["assertion_sha256"] = validator.claim_digest(claim)
    _write(root, PACKAGE_REL, package)
    assert any("influence requires direction, mechanism and scope" in item for item in validator.validate_repository(root))


def test_causal_requires_distinct_basis_and_policy(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-explicit-causal")
    case["causal_basis_claim_ref"] = "claim-causal"
    case["causal_policy_ref"] = None
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("distinct Claim" in item for item in errors)
    assert any("causal policy reference" in item for item in errors)


def test_classification_and_similarity_never_create_relation(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["non_relation_cases"][0]["creates_relation"] = True
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("classification and Similarity" in item or "False was expected" in item for item in errors)


def test_legacy_influence_cannot_be_promoted_by_compatibility(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["influenced"]["ladder_level"] = "influence"
    _write(root, COMPAT_REL, compatibility)
    assert any("legacy influenced must remain unresolved" in item for item in validator.validate_repository(root))


def test_validator_rejects_base_package_binding_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["base_packages"][1]["reviewed_content_sha256"] = "0" * 64
    _write(root, PACKAGE_REL, package)
    assert any("base package binding mismatch" in item for item in validator.validate_repository(root))


def test_ready_transition_validates(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    assert validator.validate_repository(root, require_ready=True) == []


def test_ready_rejects_current_semantic_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    package = _load(root, PACKAGE_REL)
    package["ladder_levels"][0]["definition"] = "Drifted after review and no longer trustworthy."
    _write(root, PACKAGE_REL, package)
    assert any("digest" in item for item in validator.validate_repository(root, require_ready=True))


def test_strict_json_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"status":"READY","status":"REVIEW_REQUIRED"}', encoding="utf-8")
    with pytest.raises(validator.DuplicateKeyError):
        validator.load_json(path)
