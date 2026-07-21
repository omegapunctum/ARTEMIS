#!/usr/bin/env python3
"""Semantic publish checks shared by Airtable export and the release gate."""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


BROAD_TEMPORAL_RANGE_YEARS = 500
MIN_CORPUS_FOR_DATASET_WARNINGS = 3

# These are temporary regression ceilings for the approved 19-Feature pilot.
# A new warning reason, or a count above its ceiling, blocks release until the
# data is corrected or governance explicitly changes the budget.
SEMANTIC_WARNING_BUDGETS = {
    "enabled_empty_layer_excluded": 7,
    "missing_primary_media": 3,
    "uniform_coordinates_confidence": 1,
    "missing_classification_depth": 1,
    "weak_source_depth": 1,
    "broad_temporal_range": 1,
}

ALLOWED_COORDINATES_CONFIDENCE = {"exact", "approximate", "conditional"}
ALLOWED_LAYER_TYPES = {"architecture", "route_point", "biogeography", "biography"}
ALLOWED_SOURCE_TYPES = {"primary", "official", "academic", "institutional", "reference", "other"}
ALLOWED_MEDIA_TYPES = {"image", "map", "drawing", "diagram", "document"}
ALLOWED_MEDIA_DISPLAY_ROLES = {"primary", "gallery", "context", "detail"}
ALLOWED_MEDIA_LICENSES = {"CC0", "CC BY", "CC BY-SA", "PD"}
ALLOWED_RELATION_TYPES = {"influenced", "inspired_by", "same_movement", "reconstructed_from", "part_of"}
SYMMETRIC_RELATION_TYPES = {"same_movement"}
ALLOWED_EPISTEMIC_STATUSES = {"fact", "interpretation", "hypothesis"}
ALLOWED_RELATION_CONFIDENCE = {"high", "medium", "low"}
YEAR_RE = re.compile(r"^(-?\d{4})(?:-\d{2}-\d{2})?$")


class SemanticGateError(ValueError):
    """Raised when checked-in artifacts are not semantically publishable."""


def _properties(feature: dict[str, Any]) -> dict[str, Any]:
    properties = feature.get("properties")
    return properties if isinstance(properties, dict) else feature


def _feature_id(feature: dict[str, Any]) -> str:
    properties = _properties(feature)
    return str(feature.get("id") or properties.get("id") or "<missing>").strip()


def _diagnostic_id(feature: dict[str, Any]) -> str:
    properties = _properties(feature)
    return str(properties.get("source_record_id") or _feature_id(feature)).strip()


def _warning(record_id: str, reason: str, field: str, value: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": record_id,
        "record_id": record_id,
        "field": field,
        "warning": reason,
        "reason": reason,
        "severity": "warning",
    }
    if value is not None:
        payload["value"] = value
    return payload


def _year(value: Any) -> int | None:
    if value in (None, ""):
        return None
    match = YEAR_RE.fullmatch(str(value).strip())
    return int(match.group(1)) if match else None


def _is_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_direct_media_asset(value: Any) -> bool:
    if not _is_url(value):
        return False
    parsed = urlparse(str(value).strip())
    return not (
        "commons.wikimedia.org" in parsed.netloc.lower()
        and "/wiki/file:" in parsed.path.lower()
    )


def _is_uuid_v4(value: Any) -> bool:
    try:
        parsed = uuid.UUID(str(value).strip())
    except (ValueError, TypeError, AttributeError):
        return False
    return parsed.version == 4 and parsed.variant == uuid.RFC_4122


def select_publishable_layers(
    layers: Iterable[dict[str, Any]],
    features: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Exclude disabled and enabled-empty Layers; report the latter truthfully."""
    populated_ids = {
        str(_properties(feature).get("layer_id") or "").strip()
        for feature in features
        if str(_properties(feature).get("layer_id") or "").strip()
    }
    published: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for layer in layers:
        if layer.get("is_enabled") is not True:
            continue
        layer_id = str(layer.get("layer_id") or "<missing>").strip()
        if layer_id not in populated_ids:
            warnings.append(_warning(layer_id, "enabled_empty_layer_excluded", "layer_id"))
            continue
        published.append(layer)
    return published, warnings


def collect_semantic_quality_warnings(features: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create non-blocking, actionable quality warnings for the pilot corpus."""
    materialized = list(features)
    warnings: list[dict[str, Any]] = []

    for feature in materialized:
        properties = _properties(feature)
        media_refs = properties.get("media_refs")
        primary_media = [
            ref for ref in media_refs
            if isinstance(ref, dict) and ref.get("display_role") == "primary"
        ] if isinstance(media_refs, list) else []
        if not primary_media:
            warnings.append(_warning(_diagnostic_id(feature), "missing_primary_media", "media_refs"))

        start = _year(properties.get("date_start"))
        end = _year(properties.get("date_end") or properties.get("date_construction_end"))
        if start is not None and end is not None and end - start > BROAD_TEMPORAL_RANGE_YEARS:
            warnings.append(
                _warning(
                    _diagnostic_id(feature),
                    "broad_temporal_range",
                    "date_start/date_end",
                    {"start": start, "end": end, "span_years": end - start},
                )
            )

    if len(materialized) >= MIN_CORPUS_FOR_DATASET_WARNINGS:
        confidences = {
            _properties(feature).get("coordinates_confidence")
            for feature in materialized
        }
        if confidences == {"exact"}:
            warnings.append(
                _warning(
                    "<dataset>",
                    "uniform_coordinates_confidence",
                    "coordinates_confidence",
                    {"confidence": "exact", "feature_count": len(materialized)},
                )
            )

        missing_tags = [
            _feature_id(feature)
            for feature in materialized
            if not _properties(feature).get("tags")
        ]
        if missing_tags:
            warnings.append(
                _warning(
                    "<dataset>",
                    "missing_classification_depth",
                    "tags",
                    {"feature_count": len(missing_tags)},
                )
            )

        shallow_sources = []
        for feature in materialized:
            source_refs = _properties(feature).get("source_refs")
            if isinstance(source_refs, list) and len(source_refs) <= 1:
                shallow_sources.append(_feature_id(feature))
        if shallow_sources:
            warnings.append(
                _warning(
                    "<dataset>",
                    "weak_source_depth",
                    "source_refs",
                    {"feature_count": len(shallow_sources), "threshold": "<=1 reviewed Source"},
                )
            )

    return warnings


def _load_json(root: Path, relative_path: str, expected_type: type) -> Any:
    path = root / relative_path
    if not path.exists():
        raise SemanticGateError(f"{relative_path} is missing")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SemanticGateError(f"{relative_path} is invalid JSON: {exc}") from exc
    if not isinstance(payload, expected_type):
        raise SemanticGateError(f"{relative_path} must be {expected_type.__name__}")
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SemanticGateError(message)


def _unique_index(items: list[dict[str, Any]], key: str, artifact: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        _require(isinstance(item, dict), f"{artifact}[{index}] must be an object")
        value = str(item.get(key) or "").strip()
        _require(bool(value), f"{artifact}[{index}].{key} is required")
        _require(value not in result, f"{artifact} contains duplicate {key}: {value}")
        result[value] = item
    return result


def validate_semantic_release(root: Path) -> dict[str, int | str]:
    """Validate cross-artifact semantic publish readiness for checked-in data."""
    feature_collection = _load_json(root, "data/features.geojson", dict)
    features = feature_collection.get("features")
    _require(isinstance(features, list) and bool(features), "data/features.geojson features must be non-empty")
    layers = _load_json(root, "data/layers.json", list)
    sources = _load_json(root, "data/sources.json", list)
    media = _load_json(root, "data/media.json", list)
    relations = _load_json(root, "data/relations.json", list)
    rejected = _load_json(root, "data/rejected.json", list)
    report = _load_json(root, "data/validation_report.json", dict)
    meta = _load_json(root, "data/export_meta.json", dict)

    _require(report.get("schema_version") == 2, "validation_report.json must use schema_version 2")
    blocking_errors = report.get("blocking_errors")
    warnings = report.get("warnings")
    _require(isinstance(blocking_errors, list), "validation_report.blocking_errors must be an array")
    _require(isinstance(warnings, list), "validation_report.warnings must be an array")
    _require(report.get("blocking_errors_count") == len(blocking_errors), "blocking error count mismatch")
    _require(report.get("warnings_count") == len(warnings), "warning count mismatch")
    _require(report.get("errors") == blocking_errors, "legacy validation_report.errors alias drift")
    _require(report.get("errors_count") == len(blocking_errors), "legacy validation_report.errors_count drift")
    _require(not blocking_errors, f"semantic validation has {len(blocking_errors)} blocking error(s)")
    _require(not rejected, "data/rejected.json contains release-blocking records")

    source_by_id = _unique_index(sources, "id", "data/sources.json")
    for source_id, source in source_by_id.items():
        _require(source.get("review_status") == "reviewed", f"Source {source_id} is not reviewed")
        _require(_is_url(source.get("url")) or bool(source.get("bibliographic_locator")), f"Source {source_id} has no locator")
        _require(bool(source.get("title")), f"Source {source_id} has no title")
        _require(bool(source.get("author_or_organization")), f"Source {source_id} has no author/organization")
        _require(source.get("source_type") in ALLOWED_SOURCE_TYPES, f"Source {source_id} has invalid source_type")

    media_by_id = _unique_index(media, "id", "data/media.json")
    for media_id, item in media_by_id.items():
        _require(item.get("review_status") == "reviewed", f"Media {media_id} is not reviewed")
        _require(_is_direct_media_asset(item.get("asset_url")), f"Media {media_id} has invalid direct asset_url")
        _require(_is_url(item.get("source_page_url")), f"Media {media_id} has invalid source_page_url")
        _require(bool(item.get("creator")), f"Media {media_id} has no creator")
        _require(item.get("license") in ALLOWED_MEDIA_LICENSES, f"Media {media_id} has invalid license")
        _require(bool(item.get("attribution_text")), f"Media {media_id} has no attribution")
        _require(item.get("media_type") in ALLOWED_MEDIA_TYPES, f"Media {media_id} has invalid media_type")

    layer_by_id = _unique_index(layers, "layer_id", "data/layers.json")
    feature_by_id: dict[str, dict[str, Any]] = {}
    feature_relation_projection: dict[str, set[str]] = {}
    for index, feature in enumerate(features):
        _require(isinstance(feature, dict), f"features.geojson feature[{index}] must be an object")
        feature_id = _feature_id(feature)
        _require(_is_uuid_v4(feature_id), f"Feature {feature_id} must use UUID v4")
        _require(feature_id not in feature_by_id, f"duplicate Feature id: {feature_id}")
        feature_by_id[feature_id] = feature
        properties = _properties(feature)
        _require(properties.get("validated") is True, f"Feature {feature_id} is not validated")
        _require(properties.get("layer_type") in ALLOWED_LAYER_TYPES, f"Feature {feature_id} has invalid layer_type")
        layer_id = str(properties.get("layer_id") or "").strip()
        _require(layer_id in layer_by_id, f"Feature {feature_id} references unpublished Layer {layer_id}")
        geometry = feature.get("geometry")
        coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
        _require(isinstance(coordinates, list) and len(coordinates) == 2, f"Feature {feature_id} has invalid geometry")
        longitude, latitude = coordinates
        _require(isinstance(longitude, (int, float)) and -180 <= longitude <= 180, f"Feature {feature_id} longitude out of range")
        _require(isinstance(latitude, (int, float)) and -90 <= latitude <= 90, f"Feature {feature_id} latitude out of range")
        _require(properties.get("coordinates_confidence") in ALLOWED_COORDINATES_CONFIDENCE, f"Feature {feature_id} has invalid coordinate confidence")

        start = _year(properties.get("date_start"))
        end = _year(properties.get("date_end") or properties.get("date_construction_end"))
        _require(start is not None, f"Feature {feature_id} has invalid date_start")
        _require(end is None or start <= end, f"Feature {feature_id} has inconsistent dates")

        source_ids = properties.get("source_ids")
        source_refs = properties.get("source_refs")
        _require(isinstance(source_ids, list) and bool(source_ids), f"Feature {feature_id} has no reviewed Source")
        _require(isinstance(source_refs, list), f"Feature {feature_id}.source_refs must be an array")
        _require(source_ids == [ref.get("source_id") for ref in source_refs if isinstance(ref, dict)], f"Feature {feature_id} source projection drift")
        _require(len(source_ids) == len(set(source_ids)), f"Feature {feature_id} has duplicate Source refs")
        _require(all(source_id in source_by_id for source_id in source_ids), f"Feature {feature_id} references missing Source")
        _require(sum(ref.get("is_primary") is True for ref in source_refs if isinstance(ref, dict)) == 1, f"Feature {feature_id} must have one primary Source")

        media_ids = properties.get("media_ids")
        media_refs = properties.get("media_refs")
        _require(isinstance(media_ids, list), f"Feature {feature_id}.media_ids must be an array")
        _require(isinstance(media_refs, list), f"Feature {feature_id}.media_refs must be an array")
        _require(media_ids == [ref.get("media_id") for ref in media_refs if isinstance(ref, dict)], f"Feature {feature_id} media projection drift")
        _require(len(media_ids) == len(set(media_ids)), f"Feature {feature_id} has duplicate Media refs")
        _require(all(media_id in media_by_id for media_id in media_ids), f"Feature {feature_id} references missing Media")
        primary_media_ids = [
            ref.get("media_id") for ref in media_refs
            if isinstance(ref, dict) and ref.get("display_role") == "primary"
        ]
        _require(len(primary_media_ids) <= 1, f"Feature {feature_id} has multiple primary Media")
        _require(all(ref.get("display_role") in ALLOWED_MEDIA_DISPLAY_ROLES for ref in media_refs if isinstance(ref, dict)), f"Feature {feature_id} has invalid Media role")
        if primary_media_ids:
            expected_asset = media_by_id[primary_media_ids[0]].get("asset_url")
            _require(properties.get("image_url") == expected_asset, f"Feature {feature_id} image_url is not the reviewed primary Media asset")
        else:
            _require(properties.get("image_url") in (None, ""), f"Feature {feature_id} exposes unreviewed legacy image_url")

        relation_ids = properties.get("relation_ids")
        _require(isinstance(relation_ids, list), f"Feature {feature_id}.relation_ids must be an array")
        feature_relation_projection[feature_id] = set(relation_ids)

    populated_layer_ids = {
        str(_properties(feature).get("layer_id")) for feature in features
    }
    for layer_id, layer in layer_by_id.items():
        _require(layer.get("is_enabled") is True, f"published Layer {layer_id} must be enabled")
        _require(layer_id in populated_layer_ids, f"published enabled Layer {layer_id} is empty")

    relation_by_id = _unique_index(relations, "id", "data/relations.json")
    seen_predicates: set[tuple[str, str, str]] = set()
    expected_projection: dict[str, set[str]] = {feature_id: set() for feature_id in feature_by_id}
    for relation_id, relation in relation_by_id.items():
        _require(_is_uuid_v4(relation_id), f"Relation {relation_id} must use UUID v4")
        source_feature_id = str(relation.get("source_feature_id") or "")
        target_feature_id = str(relation.get("target_feature_id") or "")
        relation_type = str(relation.get("relation_type") or "")
        _require(source_feature_id in feature_by_id and target_feature_id in feature_by_id, f"Relation {relation_id} has missing endpoint")
        _require(source_feature_id != target_feature_id, f"Relation {relation_id} is self-referential")
        _require(relation_type in ALLOWED_RELATION_TYPES, f"Relation {relation_id} has invalid type")
        _require(relation.get("epistemic_status") in ALLOWED_EPISTEMIC_STATUSES, f"Relation {relation_id} has invalid epistemic status")
        _require(relation.get("confidence") in ALLOWED_RELATION_CONFIDENCE, f"Relation {relation_id} has invalid confidence")
        if relation_type in SYMMETRIC_RELATION_TYPES:
            _require(source_feature_id < target_feature_id, f"Relation {relation_id} has unsorted symmetric endpoints")
        predicate = (source_feature_id, relation_type, target_feature_id)
        _require(predicate not in seen_predicates, f"duplicate Relation predicate: {predicate}")
        seen_predicates.add(predicate)
        source_ids = relation.get("source_ids")
        source_refs = relation.get("source_refs")
        _require(isinstance(source_ids, list) and bool(source_ids), f"Relation {relation_id} has no evidence")
        _require(isinstance(source_refs, list) and bool(source_refs), f"Relation {relation_id} has no evidence refs")
        _require(source_ids == [ref.get("source_id") for ref in source_refs if isinstance(ref, dict)], f"Relation {relation_id} evidence projection drift")
        _require(all(source_id in source_by_id for source_id in source_ids), f"Relation {relation_id} references missing Source")
        _require(all("relation_evidence" in (ref.get("roles") or []) and bool(ref.get("claim_note")) for ref in source_refs if isinstance(ref, dict)), f"Relation {relation_id} has invalid evidence semantics")
        expected_projection[source_feature_id].add(relation_id)
        expected_projection[target_feature_id].add(relation_id)

    _require(set(relation_by_id) == {relation_id for ids in feature_relation_projection.values() for relation_id in ids}, "Feature relation_ids contain missing or unprojected Relations")
    for feature_id, relation_ids in expected_projection.items():
        _require(feature_relation_projection[feature_id] == relation_ids, f"Feature {feature_id} relation projection drift")

    warning_keys = Counter((str(item.get("reason") or ""), str(item.get("id") or "")) for item in warnings if isinstance(item, dict))
    expected_warnings = collect_semantic_quality_warnings(features)
    expected_keys = Counter((item["reason"], item["id"]) for item in expected_warnings)
    empty_layer_warnings = [item for item in warnings if isinstance(item, dict) and item.get("reason") == "enabled_empty_layer_excluded"]
    non_layer_warning_keys = Counter({key: count for key, count in warning_keys.items() if key[0] != "enabled_empty_layer_excluded"})
    _require(non_layer_warning_keys == expected_keys, "validation_report semantic warnings do not match published Features")

    warning_stats = Counter(str(item.get("reason") or "") for item in warnings if isinstance(item, dict))
    for reason, count in warning_stats.items():
        _require(reason in SEMANTIC_WARNING_BUDGETS, f"unbudgeted semantic warning: {reason}")
        _require(count <= SEMANTIC_WARNING_BUDGETS[reason], f"semantic warning budget exceeded: {reason} ({count} > {SEMANTIC_WARNING_BUDGETS[reason]})")

    _require(meta.get("errors") == 0, "export_meta reports blocking errors")
    _require(meta.get("warnings") == len(warnings), "export_meta warning count mismatch")
    _require(meta.get("warning_stats") == dict(sorted(warning_stats.items())), "export_meta warning_stats drift")
    categories = meta.get("warning_categories")
    _require(categories == {"expected_fallback": 0, "data_quality": len(warnings)}, "export_meta warning_categories drift")
    _require(meta.get("layers_published") == len(layers), "export_meta layers_published mismatch")
    _require(meta.get("enabled_empty_layers_excluded") == len(empty_layer_warnings), "excluded empty Layer count mismatch")
    _require(meta.get("layers_total_source") == len(layers) + len(empty_layer_warnings), "source Layer count mismatch")
    semantic_gate = meta.get("semantic_gate")
    expected_status = "ready_with_warnings" if warnings else "ready"
    _require(report.get("status") == expected_status, "validation_report status drift")
    _require(
        semantic_gate == {"status": expected_status, "blocking_errors": 0, "warnings": len(warnings)},
        "export_meta semantic_gate drift",
    )

    return {
        "status": expected_status,
        "features": len(features),
        "layers": len(layers),
        "sources": len(sources),
        "media": len(media),
        "relations": len(relations),
        "warnings": len(warnings),
    }
