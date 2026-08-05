from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts import validate_uncertainty_fixtures as validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path("fixtures/world_model/uncertainty/v1/package.json")
REGISTRY_REL = Path("fixtures/world_model/uncertainty/v1/review_registry.json")
README_REL = Path("fixtures/world_model/uncertainty/v1/README.md")
COMPAT_REL = Path(
    "fixtures/world_model/uncertainty/v1/compatibility/architecture_atlas_projection.json"
)


def _copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    base_path = target / "fixtures/world_model/v1/package.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    base["status"] = "READY"
    base_path.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base_registry_path = target / "fixtures/world_model/v1/review_registry.json"
    base_registry = json.loads(base_registry_path.read_text(encoding="utf-8"))
    base_registry["status"] = "READY"
    base_registry["frozen_commit"] = "2333a26ea48eb8a694354be625bcc2a5892d2fbb"
    base_registry["reviewed_content_sha256"] = "ebe6527ea8a41d8046918e37726d38b2a3898c1e496234630e718fa861632168"
    base_registry_path.write_text(
        json.dumps(base_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target


def _load(root: Path, relative: Path) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write(root: Path, relative: Path, value: dict) -> None:
    (root / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _case(package: dict, case_id: str) -> dict:
    return next(case for case in package["temporal_cases"] if case["id"] == case_id)


def _spatial(package: dict, case_id: str) -> dict:
    return next(case for case in package["spatial_cases"] if case["id"] == case_id)


def _run_git(root: Path, *args: str, when: datetime | None = None) -> str:
    env = None
    if when is not None:
        env = {
            "GIT_AUTHOR_DATE": when.isoformat(),
            "GIT_COMMITTER_DATE": when.isoformat(),
        }
        import os

        env = {**os.environ, **env}
    result = subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return result.stdout.strip()


def _prepare_ready(root: Path) -> tuple[str, str]:
    now = datetime.now(UTC).replace(microsecond=0)
    frozen_time = now - timedelta(minutes=5)
    review_times = [now - timedelta(minutes=3), now - timedelta(minutes=2)]
    ready_time = now - timedelta(minutes=1)
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "ARTEMIS Test")
    _run_git(root, "config", "user.email", "artemis-test@example.invalid")
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "frozen uncertainty candidate", when=frozen_time)
    frozen = _run_git(root, "rev-parse", "HEAD")
    digest = validator.compute_review_digest(root)

    artifact_dir = root / "docs/work/reviews"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    reviews = []
    for index, track in enumerate(("semantic-model", "validator-integrity")):
        review = {
            "review_id": f"uncertainty-v1-{track}",
            "reviewer_id": f"test-{track}-reviewer",
            "reviewer_instance_id": f"test-{track}-instance",
            "track": track,
            "independence_method": "separate_agent_task",
            "artifact": f"docs/work/reviews/uncertainty-v1-{track}.json",
            "artifact_sha256": "",
            "frozen_commit": frozen,
            "reviewed_content_sha256": digest,
            "reviewed_at": review_times[index].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "decision": "READY",
            "finding_counts": {"critical": 0, "material": 0, "minor": 0},
            "findings": [],
            "independence_attestation": True,
        }
        artifact = {
            "artifact_format": "artemis-review-attestation-v1",
            **{
                key: value
                for key, value in review.items()
                if key not in {"artifact", "artifact_sha256"}
            },
        }
        artifact_path = root / review["artifact"]
        _write(root, Path(review["artifact"]), artifact)
        review["artifact_sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        reviews.append(review)

    package = _load(root, PACKAGE_REL)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = ready_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    _write(root, PACKAGE_REL, package)
    for relative, old, new in (
        (README_REL, "Status: `REVIEW_REQUIRED`", "Status: `READY`"),
        (Path("docs/UNCERTAINTY_SEMANTICS_CONTRACT.md"), "- Status: `REVIEW_REQUIRED`.", "- Status: `READY`."),
    ):
        path = root / relative
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    registry = {
        "schema_version": "1.0.0",
        "package_id": "artemis-uncertainty-semantics-v1",
        "status": "READY",
        "frozen_commit": frozen,
        "reviewed_content_sha256": digest,
        "required_review_count": 2,
        "review_scope_id": "uncertainty-semantics-v1-canonical",
        "reviews": reviews,
    }
    _write(root, REGISTRY_REL, registry)
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "finalize uncertainty READY", when=ready_time)
    return frozen, digest


def _mock_external_base_history(monkeypatch: pytest.MonkeyPatch) -> None:
    real_git_output = validator._git_output
    dependency_commits = {
        "db60ffc89b93c8a3694b5f0b699e43e706786ba8",
        "2333a26ea48eb8a694354be625bcc2a5892d2fbb",
    }

    def proxy(root: Path, *args: str) -> bytes:
        if any(commit in " ".join(args) for commit in dependency_commits):
            return b""
        return real_git_output(root, *args)

    monkeypatch.setattr(validator, "_git_output", proxy)


def test_uncertainty_fixture_package_validates(tmp_path: Path) -> None:
    assert validator.validate_repository(_copy_repo(tmp_path)) == []


def test_require_ready_rejects_review_required_package(tmp_path: Path) -> None:
    errors = validator.validate_repository(_copy_repo(tmp_path), require_ready=True)
    assert any("uncertainty package is not READY" in error for error in errors)


def test_window_classification_covers_all_four_results() -> None:
    package = _load(ROOT, PACKAGE_REL)
    results = {
        validator.classify_window(case, query)
        for case in package["temporal_cases"]
        for query in case["queries"]
    }
    assert results == {"excluded", "possible_overlap", "contained", "unknown"}


def test_touching_exclusive_boundary_is_excluded() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = _case(package, "exclusive-touch")
    query = next(query for query in case["queries"] if query["id"] == "exclusive-touch-only")
    assert validator.classify_window(case, query) == "excluded"


def test_touching_inclusive_boundary_overlaps() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = copy.deepcopy(_case(package, "exclusive-touch"))
    case["candidates"][0]["lower"]["inclusive"] = True
    query = next(query for query in case["queries"] if query["id"] == "exclusive-touch-only")
    assert validator.classify_window(case, query) == "possible_overlap"


def test_alternatives_are_combined_without_first_winner() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = _case(package, "alternative-years")
    query = next(query for query in case["queries"] if query["id"] == "alternative-one")
    assert validator.classify_window(case, query) == "possible_overlap"
    reversed_case = copy.deepcopy(case)
    reversed_case["candidates"].reverse()
    assert validator.classify_window(reversed_case, query) == "possible_overlap"


@pytest.mark.parametrize(
    ("case_id", "mutation", "needle"),
    [
        (
            "bounded-not-before-not-after",
            lambda case: case["candidates"][0]["lower"].update(qualifier="exact"),
            "bounded_interval must use not_before/not_after",
        ),
        (
            "not-before-open-end",
            lambda case: case["candidates"][0].update(upper={"value": "1505", "precision": "year", "qualifier": "not_after", "inclusive": True}),
            "open_end_interval has invalid lower/upper shape",
        ),
        (
            "approximate-explicit-range",
            lambda case: case["candidates"][0]["lower"].update(value="1503-1"),
            "non-canonical year value",
        ),
    ],
)
def test_validator_rejects_invalid_temporal_semantics(
    tmp_path: Path, case_id: str, mutation, needle: str
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    mutation(_case(package, case_id))
    _write(root, PACKAGE_REL, package)
    assert any(needle in error for error in validator.validate_repository(root))


def test_validator_rejects_reversed_query(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    query = _case(package, "exact-day")["queries"][0]
    query["start"] = "1504-03-02"
    query["end"] = "1504-03-01"
    _write(root, PACKAGE_REL, package)
    assert any("empty or reversed query" in error for error in validator.validate_repository(root))


def test_validator_rejects_duplicate_semantic_alternative(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "alternative-years")
    duplicate = copy.deepcopy(case["candidates"][0])
    duplicate["id"] = "alternative-duplicate"
    case["candidates"][1] = duplicate
    _write(root, PACKAGE_REL, package)
    assert any("duplicate semantic alternative" in error for error in validator.validate_repository(root))


def test_validator_rejects_wrong_expected_window_result(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _case(package, "exact-day")["queries"][0]["expected"] = "excluded"
    _write(root, PACKAGE_REL, package)
    assert any("expected excluded, got contained" in error for error in validator.validate_repository(root))


def test_validator_rejects_approximate_point_without_tolerance(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _spatial(package, "approximate-point").pop("tolerance_m")
    _write(root, PACKAGE_REL, package)
    assert any("requires tolerance and uncertainty" in error for error in validator.validate_repository(root))


def test_validator_rejects_unknown_route_geometry(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _spatial(package, "unknown-route")["geometry"] = {
        "type": "LineString",
        "coordinates": [[10.0, 50.0], [11.0, 50.5]],
    }
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("unknown_route must not contain geometry" in error for error in errors)


def test_validator_rejects_inferred_corridor_without_uncertainty(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _spatial(package, "inferred-corridor")["uncertainty_refs"] = []
    _write(root, PACKAGE_REL, package)
    assert any("requires uncertain Polygon geometry" in error for error in validator.validate_repository(root))


def test_validator_rejects_legacy_exactness_promotion(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["spatial_projection"]["target_precision"] = "exact"
    _write(root, COMPAT_REL, compatibility)
    assert any("closed, value-bound" in error for error in validator.validate_repository(root))


def test_validator_rejects_invented_compatibility_fields(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["invented_fields"] = ["locator"]
    _write(root, COMPAT_REL, compatibility)
    assert any("closed, value-bound" in error for error in validator.validate_repository(root))


def test_validator_rejects_dangling_claim_reference(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _spatial(package, "documented-path")["basis_claim_refs"] = ["claim-does-not-exist"]
    _write(root, PACKAGE_REL, package)
    assert any("basis_claim_refs" in error for error in validator.validate_repository(root))


def test_validator_rejects_claim_assertion_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    next(claim for claim in package["claims"] if claim["id"] == "claim-exact-point")[
        "assertion_sha256"
    ] = "0" * 64
    _write(root, PACKAGE_REL, package)
    assert any("assertion digest" in error for error in validator.validate_repository(root))


@pytest.mark.parametrize(
    ("family", "case_id"),
    [
        ("temporal", "not-before-open-end"),
        ("spatial", "unknown-location"),
    ],
)
def test_validator_rejects_projection_promotion(
    tmp_path: Path, family: str, case_id: str
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    cases = package["temporal_cases"] if family == "temporal" else package["spatial_cases"]
    next(case for case in cases if case["id"] == case_id)["projection_policy"] = "show_exact"
    _write(root, PACKAGE_REL, package)
    assert any("projection_policy" in error for error in validator.validate_repository(root))


@pytest.mark.parametrize(
    ("case_id", "coordinates"),
    [
        ("exact-point", [[10.0, 50.0], [11.0, 51.0]]),
        ("documented-path", [[10.0, 50.0]]),
        ("inferred-corridor", [[[10.0, 50.0], [11.0, 50.0], [10.0, 50.0]]]),
    ],
)
def test_validator_rejects_invalid_geojson_shapes(
    tmp_path: Path, case_id: str, coordinates: list
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _spatial(package, case_id)["geometry"]["coordinates"] = coordinates
    _write(root, PACKAGE_REL, package)
    assert any("coordinate shape" in error for error in validator.validate_repository(root))


def test_validator_rejects_compatibility_value_drift_and_extra_fields(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["temporal_projection"]["lower"]["value"] = "0001"
    compatibility["spatial_projection"]["geometry"]["coordinates"] = [0.0, 0.0]
    compatibility["spatial_projection"]["locator"] = "invented"
    _write(root, COMPAT_REL, compatibility)
    assert any("closed, value-bound" in error for error in validator.validate_repository(root))


def test_committed_ready_transition_validates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    _mock_external_base_history(monkeypatch)
    assert validator.validate_repository(root, require_ready=True) == []


def test_ready_rejects_current_worktree_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    _mock_external_base_history(monkeypatch)
    package = _load(root, PACKAGE_REL)
    package["projection_policies"][0]["label"] = "Drifted after commit"
    _write(root, PACKAGE_REL, package)
    assert any("digest" in error or "Git HEAD" in error for error in validator.validate_repository(root, require_ready=True))


def test_ready_rejects_symlinked_review_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    _mock_external_base_history(monkeypatch)
    registry = _load(root, REGISTRY_REL)
    artifact_path = root / registry["reviews"][0]["artifact"]
    target = artifact_path.with_suffix(".target.json")
    artifact_path.rename(target)
    artifact_path.symlink_to(target.name)
    assert any("symlink" in error for error in validator.validate_repository(root, require_ready=True))


def test_validator_rejects_base_projection_checksum_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["base_projection"]["sha256"] = "0" * 64
    _write(root, COMPAT_REL, compatibility)
    assert any("closed, value-bound" in error for error in validator.validate_repository(root))


def test_validator_rejects_non_ready_base_package(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    base_path = Path("fixtures/world_model/v1/package.json")
    base = _load(root, base_path)
    base["status"] = "REVIEW_REQUIRED"
    _write(root, base_path, base)
    assert any("base world-model package must remain READY" in error for error in validator.validate_repository(root))


def test_validator_rejects_status_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    registry = _load(root, REGISTRY_REL)
    registry["status"] = "READY"
    _write(root, REGISTRY_REL, registry)
    assert any("status drift" in error for error in validator.validate_repository(root))


def test_review_digest_normalizes_metadata_only_status_transition(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    before = validator.compute_review_digest(root)
    package = _load(root, PACKAGE_REL)
    package["status"] = "READY"
    _write(root, PACKAGE_REL, package)
    readme_path = root / README_REL
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace(
            "Status: `REVIEW_REQUIRED`", "Status: `READY`", 1
        ),
        encoding="utf-8",
    )
    assert validator.compute_review_digest(root) == before


def test_strict_json_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"status":"READY","status":"REVIEW_REQUIRED"}', encoding="utf-8")
    with pytest.raises(validator.DuplicateKeyError):
        validator.load_json(path)
