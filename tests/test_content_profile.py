import json
from pathlib import Path

import pytest

from scripts.content_profile import (
    ContentProfileError,
    build_content_profile,
    validate_checked_in_profile,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _feature(index: int, layer_id: str, *, primary_media: bool = True) -> dict:
    media_refs = [
        {"media_id": f"media-{index}", "display_role": "primary"}
    ] if primary_media else []
    return {
        "id": f"feature-{index}",
        "properties": {
            "layer_id": layer_id,
            "source_ids": [f"source-{index}"],
            "media_refs": media_refs,
        },
    }


def _ready_payload() -> dict:
    features = [
        _feature(index, f"cohort-{index // 5}")
        for index in range(30)
    ]
    layers = [
        {"layer_id": f"cohort-{index}", "is_enabled": True}
        for index in range(6)
    ]
    sources = [{"id": f"source-{index}"} for index in range(30)]
    media = [{"id": f"media-{index}"} for index in range(30)]
    relations = [
        {
            "id": f"relation-{index}",
            "source_feature_id": f"feature-{index}",
            "target_feature_id": f"feature-{index + 1}",
            "source_ids": [f"source-{index}"],
            "source_refs": [{"source_id": f"source-{index}"}],
        }
        for index in range(12)
    ]
    return build_content_profile(
        features=features,
        layers=layers,
        sources=sources,
        media=media,
        relations=relations,
        semantic_status="ready",
    )


def test_checked_in_content_profile_matches_public_artifacts() -> None:
    profile = validate_checked_in_profile(REPO_ROOT)

    assert profile["profile_id"] == "architecture-atlas-comparison-pilot-v1"
    assert profile["actual"]["features"] == 31
    assert profile["actual"]["comparison_cohorts"] == 6
    assert profile["actual"]["primary_media_coverage"]["ratio"] == 0.9032
    assert profile["readiness"]["status"] == "building"
    assert profile["readiness"]["failed_check_ids"] == ["reviewed_relations"]
    assert profile["readiness"]["gaps"]["features_to_minimum"] == 0
    assert profile["readiness"]["gaps"]["reviewed_relations_to_minimum"] == 10


def test_profile_becomes_ready_at_approved_pilot_thresholds() -> None:
    profile = _ready_payload()

    assert profile["readiness"]["passed"] is True
    assert profile["readiness"]["status"] == "comparison_ready"
    assert profile["actual"]["comparison_cohorts"] == 6
    assert profile["actual"]["relation_evidence_coverage"]["ratio"] == 1.0


def test_profile_reports_media_gap_without_weakening_release_truth() -> None:
    features = [
        _feature(index, f"cohort-{index // 5}", primary_media=index < 26)
        for index in range(30)
    ]
    profile = build_content_profile(
        features=features,
        layers=[{"layer_id": f"cohort-{index}"} for index in range(6)],
        sources=[{"id": f"source-{index}"} for index in range(30)],
        media=[{"id": f"media-{index}"} for index in range(26)],
        relations=_ready_payload()["readiness"]["checks"][:0],
        semantic_status="ready_with_warnings",
    )

    assert profile["actual"]["primary_media_coverage"]["ratio"] == 0.8667
    assert profile["readiness"]["gaps"]["primary_media_records_to_current_minimum"] == 1
    assert "primary_media_coverage" in profile["readiness"]["failed_check_ids"]


def test_stale_checked_in_profile_is_rejected(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for name in (
        "features.geojson",
        "layers.json",
        "sources.json",
        "media.json",
        "relations.json",
        "validation_report.json",
        "content_profile.json",
    ):
        payload = json.loads((REPO_ROOT / "data" / name).read_text(encoding="utf-8"))
        (data_dir / name).write_text(json.dumps(payload), encoding="utf-8")
    stale = json.loads((data_dir / "content_profile.json").read_text(encoding="utf-8"))
    stale["actual"]["features"] = 999
    (data_dir / "content_profile.json").write_text(json.dumps(stale), encoding="utf-8")

    with pytest.raises(ContentProfileError, match="is stale"):
        validate_checked_in_profile(tmp_path)
