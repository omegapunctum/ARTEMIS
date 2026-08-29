import copy
import json

import pytest

from scripts.validate_leonardo_major_life_package import (
    PACKAGE_PATH,
    MajorLifePackageError,
    validate_package,
)


def _package():
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def test_source_audited_candidate_package_passes_fail_closed_validation() -> None:
    assert validate_package() == {
        "package_id": "leonardo-major-life-presence-candidates-v1",
        "status": "CANDIDATE_SOURCE_AUDITED",
        "place_count": 5,
        "macro_period_count": 6,
        "new_presence_count": 7,
        "referenced_romagna_presence_count": 4,
        "composed_anchor_count": 11,
        "new_unknown_transition_count": 7,
        "source_count": 11,
        "claim_count": 7,
        "evidence_link_count": 14,
        "uncertainty_count": 8,
        "runtime_authorized": False,
        "canonical_review_status": "pending_independent_review",
    }


def test_candidate_package_cannot_authorize_runtime() -> None:
    package = _package()
    package["runtime_authorized"] = True

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_presence_cannot_gain_unreviewed_geometry() -> None:
    package = _package()
    package["presences"][0]["geometry"] = {
        "type": "Point",
        "coordinates": [10.923, 43.787],
    }

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_presence_must_resolve_to_a_named_place_identity() -> None:
    package = _package()
    package["presences"][0]["place_ref"] = "place-does-not-exist"

    with pytest.raises(MajorLifePackageError, match="missing Place"):
        validate_package(package)


def test_place_cannot_gain_unreviewed_geometry() -> None:
    package = _package()
    package["places"][0]["geometry"] = {
        "type": "Point",
        "coordinates": [10.923, 43.787],
    }

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_unknown_transition_cannot_gain_line_or_route_evidence() -> None:
    package = _package()
    transition = package["transitions"][0]
    transition["source_refs"] = ["source-museo-leonardiano-places"]

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_florence_year_precision_cannot_be_inflated_to_day() -> None:
    package = _package()
    presence = next(
        row
        for row in package["presences"]
        if row["presence_id"] == "presence-leonardo-florence-st-luke-1472"
    )
    presence["temporal"].update(
        {"start": "1472-01-01", "end": "1472-01-01", "precision": "day"}
    )

    with pytest.raises(MajorLifePackageError, match="temporal precision drifted"):
        validate_package(package)


def test_romagna_segment_must_remain_an_identity_preserving_reference() -> None:
    package = _package()
    external = package["trajectory"]["external_segments"][0]
    external["identity_policy"] = "copied_into_major_life_package"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_evidence_link_must_resolve_to_registered_source() -> None:
    package = _package()
    package["evidence_links"][0]["source_id"] = "source-does-not-exist"

    with pytest.raises(MajorLifePackageError, match="missing Source"):
        validate_package(package)


def test_evidence_link_cannot_escape_its_atomic_claim() -> None:
    package = _package()
    package["evidence_links"][0]["claim_id"] = package["claims"][1]["claim_id"]

    with pytest.raises(MajorLifePackageError, match="escaped its atomic Claim"):
        validate_package(package)


def test_macro_period_cannot_become_world_model_entity() -> None:
    package = _package()
    package["macro_periods"][0]["presentation_only"] = False

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_candidate_package_cannot_self_assert_canonical_review() -> None:
    package = _package()
    package["audit"]["canonical_review_status"] = "ready"
    package["audit"]["current_decision"] = "FREEZE_FOR_REVIEW"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_historical_drive_cost_cannot_be_retroactively_estimated() -> None:
    package = _package()
    package["audit"]["curation_cost"]["duration_minutes"] = 30

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_missing_presence_uncertainty_is_rejected() -> None:
    package = _package()
    target = package["presences"][0]["uncertainty_refs"][0]
    package["uncertainties"] = [
        row for row in package["uncertainties"] if row["uncertainty_id"] != target
    ]

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)
