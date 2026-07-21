#!/usr/bin/env python3
"""Build and verify the approved Architecture Atlas comparison-pilot profile."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


PROFILE_SCHEMA_VERSION = 1
PROFILE_ID = "architecture-atlas-comparison-pilot-v1"
PROFILE_PATH = Path("data/content_profile.json")

PILOT_TARGETS = {
    "features": {"minimum": 30, "maximum": 40},
    "comparison_cohorts": {
        "minimum": 6,
        "maximum": 8,
        "minimum_features_per_cohort": 3,
    },
    "reviewed_relations": {"minimum": 12, "maximum": 20},
    "feature_source_coverage": {"minimum_ratio": 1.0},
    "primary_media_coverage": {"minimum_ratio": 0.9},
    "relation_evidence_coverage": {"minimum_ratio": 1.0},
    "published_empty_layers": {"maximum": 0},
}

MATURITY_REFERENCE = {
    "features": "100-150",
    "populated_layers": "15-20",
    "reviewed_relations": "50+",
    "curated_stories": 3,
    "reference_research_slices": "5-10",
}


class ContentProfileError(ValueError):
    """Raised when the checked-in content profile is missing or stale."""


def _read_json(root: Path, relative_path: str, expected_type: type) -> Any:
    path = root / relative_path
    if not path.exists():
        raise ContentProfileError(f"{relative_path} is missing")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContentProfileError(f"{relative_path} is invalid JSON: {exc}") from exc
    if not isinstance(payload, expected_type):
        raise ContentProfileError(f"{relative_path} must be {expected_type.__name__}")
    return payload


def _properties(feature: dict[str, Any]) -> dict[str, Any]:
    properties = feature.get("properties")
    return properties if isinstance(properties, dict) else feature


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _coverage(numerator: int, denominator: int) -> dict[str, int | float]:
    return {
        "covered": numerator,
        "total": denominator,
        "ratio": _ratio(numerator, denominator),
    }


def build_content_profile(
    *,
    features: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    media: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    semantic_status: str,
) -> dict[str, Any]:
    """Return a deterministic readiness snapshot for the bounded pilot."""
    feature_count = len(features)
    layer_counts = Counter(
        str(_properties(feature).get("layer_id") or "").strip()
        for feature in features
    )
    layer_counts.pop("", None)
    minimum_per_cohort = PILOT_TARGETS["comparison_cohorts"]["minimum_features_per_cohort"]
    cohorts = [
        {"layer_id": layer_id, "feature_count": count}
        for layer_id, count in sorted(layer_counts.items())
        if count >= minimum_per_cohort
    ]
    singleton_layers = sum(count == 1 for count in layer_counts.values())

    features_with_source = sum(
        bool(_properties(feature).get("source_ids")) for feature in features
    )
    features_with_primary_media = sum(
        any(
            isinstance(ref, dict) and ref.get("display_role") == "primary"
            for ref in (_properties(feature).get("media_refs") or [])
        )
        for feature in features
    )
    relations_with_evidence = sum(
        bool(relation.get("source_ids")) and bool(relation.get("source_refs"))
        for relation in relations
    )
    connected_feature_ids = {
        str(relation.get(endpoint) or "").strip()
        for relation in relations
        for endpoint in ("source_feature_id", "target_feature_id")
        if str(relation.get(endpoint) or "").strip()
    }
    published_layer_ids = {
        str(layer.get("layer_id") or "").strip()
        for layer in layers
        if str(layer.get("layer_id") or "").strip()
    }
    populated_layer_ids = set(layer_counts)
    empty_published_layers = sorted(published_layer_ids - populated_layer_ids)

    actual = {
        "features": feature_count,
        "published_layers": len(layers),
        "comparison_cohorts": len(cohorts),
        "cohorts": cohorts,
        "singleton_layers": singleton_layers,
        "reviewed_sources": len(sources),
        "reviewed_media": len(media),
        "reviewed_relations": len(relations),
        "relation_connected_features": len(connected_feature_ids),
        "relation_connected_feature_ratio": _ratio(len(connected_feature_ids), feature_count),
        "feature_source_coverage": _coverage(features_with_source, feature_count),
        "primary_media_coverage": _coverage(features_with_primary_media, feature_count),
        "relation_evidence_coverage": _coverage(relations_with_evidence, len(relations)),
        "published_empty_layers": len(empty_published_layers),
        "empty_published_layer_ids": empty_published_layers,
        "semantic_status": semantic_status,
    }

    checks = [
        {
            "id": "features",
            "passed": PILOT_TARGETS["features"]["minimum"] <= feature_count <= PILOT_TARGETS["features"]["maximum"],
            "current": feature_count,
            "requirement": "30-40",
        },
        {
            "id": "comparison_cohorts",
            "passed": PILOT_TARGETS["comparison_cohorts"]["minimum"] <= len(cohorts) <= PILOT_TARGETS["comparison_cohorts"]["maximum"],
            "current": len(cohorts),
            "requirement": "6-8 layers with at least 3 Features each",
        },
        {
            "id": "reviewed_relations",
            "passed": PILOT_TARGETS["reviewed_relations"]["minimum"] <= len(relations) <= PILOT_TARGETS["reviewed_relations"]["maximum"],
            "current": len(relations),
            "requirement": "12-20",
        },
        {
            "id": "feature_source_coverage",
            "passed": actual["feature_source_coverage"]["ratio"] >= PILOT_TARGETS["feature_source_coverage"]["minimum_ratio"],
            "current": actual["feature_source_coverage"]["ratio"],
            "requirement": "100%",
        },
        {
            "id": "primary_media_coverage",
            "passed": actual["primary_media_coverage"]["ratio"] >= PILOT_TARGETS["primary_media_coverage"]["minimum_ratio"],
            "current": actual["primary_media_coverage"]["ratio"],
            "requirement": ">=90%",
        },
        {
            "id": "relation_evidence_coverage",
            "passed": actual["relation_evidence_coverage"]["ratio"] >= PILOT_TARGETS["relation_evidence_coverage"]["minimum_ratio"],
            "current": actual["relation_evidence_coverage"]["ratio"],
            "requirement": "100%",
        },
        {
            "id": "published_empty_layers",
            "passed": actual["published_empty_layers"] <= PILOT_TARGETS["published_empty_layers"]["maximum"],
            "current": actual["published_empty_layers"],
            "requirement": "0",
        },
        {
            "id": "semantic_gate",
            "passed": semantic_status in {"ready", "ready_with_warnings"},
            "current": semantic_status,
            "requirement": "ready or ready_with_warnings",
        },
    ]
    failed_check_ids = [check["id"] for check in checks if not check["passed"]]

    feature_gap = max(0, PILOT_TARGETS["features"]["minimum"] - feature_count)
    cohort_gap = max(0, PILOT_TARGETS["comparison_cohorts"]["minimum"] - len(cohorts))
    relation_gap = max(0, PILOT_TARGETS["reviewed_relations"]["minimum"] - len(relations))
    media_required = math.ceil(feature_count * PILOT_TARGETS["primary_media_coverage"]["minimum_ratio"])
    media_gap = max(0, media_required - features_with_primary_media)
    gaps = {
        "features_to_minimum": feature_gap,
        "comparison_cohorts_to_minimum": cohort_gap,
        "reviewed_relations_to_minimum": relation_gap,
        "primary_media_records_to_current_minimum": media_gap,
    }

    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_id": PROFILE_ID,
        "scope": "comparison-first Round 0 validation corpus",
        "decision": {
            "status": "approved_narrower_pilot",
            "purpose": "validate comparison, provenance, and Relation/Similarity literacy before corpus scaling",
            "does_not_claim": "full MVP content maturity or public Slice workflow readiness",
        },
        "targets": PILOT_TARGETS,
        "maturity_reference": MATURITY_REFERENCE,
        "actual": actual,
        "readiness": {
            "status": "comparison_ready" if not failed_check_ids else "building",
            "passed": not failed_check_ids,
            "failed_check_ids": failed_check_ids,
            "checks": checks,
            "gaps": gaps,
        },
    }


def build_content_profile_from_root(root: Path) -> dict[str, Any]:
    feature_collection = _read_json(root, "data/features.geojson", dict)
    features = feature_collection.get("features")
    if not isinstance(features, list):
        raise ContentProfileError("data/features.geojson features must be an array")
    report = _read_json(root, "data/validation_report.json", dict)
    return build_content_profile(
        features=features,
        layers=_read_json(root, "data/layers.json", list),
        sources=_read_json(root, "data/sources.json", list),
        media=_read_json(root, "data/media.json", list),
        relations=_read_json(root, "data/relations.json", list),
        semantic_status=str(report.get("status") or "unknown"),
    )


def validate_checked_in_profile(root: Path) -> dict[str, Any]:
    checked_in = _read_json(root, PROFILE_PATH.as_posix(), dict)
    expected = build_content_profile_from_root(root)
    if checked_in != expected:
        raise ContentProfileError(
            "data/content_profile.json is stale; run python scripts/content_profile.py --write"
        )
    return checked_in


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--write", action="store_true", help="write data/content_profile.json")
    args = parser.parse_args()
    root = args.root.resolve()
    profile = build_content_profile_from_root(root)
    serialized = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        path = root / PROFILE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized, encoding="utf-8")
        print(path.relative_to(root).as_posix())
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
