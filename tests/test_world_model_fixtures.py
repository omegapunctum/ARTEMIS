import copy
import json
import shutil
from pathlib import Path

import pytest

from scripts.validate_world_model_fixtures import (
    FixtureValidationError,
    validate_package,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("fixtures/world_model/v1")


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / PACKAGE, root / PACKAGE)
    data_source = ROOT / "data" / "features.json"
    if data_source.is_file():
        (root / "data").mkdir(parents=True)
        shutil.copy2(data_source, root / "data" / "features.json")
    return root


def _read_package(root: Path) -> dict:
    return json.loads((root / PACKAGE / "package.json").read_text(encoding="utf-8"))


def _write_package(root: Path, package: dict) -> None:
    (root / PACKAGE / "package.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_world_model_fixture_package_passes_structural_validation() -> None:
    counts = validate_package(ROOT)

    assert counts["Entity"] == 7
    assert counts["Event"] == 4
    assert counts["State"] == 2
    assert counts["Process"] == 1
    assert counts["Trajectory"] == 1
    assert counts["Region"] == 1
    assert counts["Relation"] == 1
    assert counts["Claim"] == 15
    assert counts["EvidenceLink"] == 16


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


def test_package_is_deterministic_under_deep_copy(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    package = _read_package(root)
    _write_package(root, copy.deepcopy(package))

    assert validate_package(root) == validate_package(ROOT)
