from __future__ import annotations

import copy
import json
import shutil
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
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".pytest_cache", "__pycache__"))
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


def test_uncertainty_fixture_package_validates() -> None:
    assert validator.validate_repository(ROOT) == []


def test_require_ready_rejects_review_required_package() -> None:
    errors = validator.validate_repository(ROOT, require_ready=True)
    assert "uncertainty package is not READY" in errors


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
    assert any("must not become target exactness" in error for error in validator.validate_repository(root))


def test_validator_rejects_invented_compatibility_fields(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["invented_fields"] = ["locator"]
    _write(root, COMPAT_REL, compatibility)
    assert any("must not invent fields" in error for error in validator.validate_repository(root))


def test_validator_rejects_base_projection_checksum_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["base_projection"]["sha256"] = "0" * 64
    _write(root, COMPAT_REL, compatibility)
    assert any("checksum mismatch" in error for error in validator.validate_repository(root))


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
    assert any("status must agree" in error for error in validator.validate_repository(root))


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
