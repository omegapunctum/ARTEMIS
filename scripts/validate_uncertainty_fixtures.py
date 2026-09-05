#!/usr/bin/env python3
"""Validate the additive ARTEMIS #330 uncertainty-semantics fixture package."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = Path("fixtures/world_model/uncertainty/v1")
PACKAGE_PATH = PACKAGE_DIR / "package.json"
SCHEMA_PATH = PACKAGE_DIR / "schema.json"
README_PATH = PACKAGE_DIR / "README.md"
REGISTRY_PATH = PACKAGE_DIR / "review_registry.json"
COMPATIBILITY_PATH = PACKAGE_DIR / "compatibility/architecture_atlas_projection.json"
BASE_PACKAGE_PATH = Path("fixtures/world_model/v1/package.json")
BASE_COMPATIBILITY_PATH = Path(
    "fixtures/world_model/v1/compatibility/architecture_atlas_projection.json"
)
BASE_REGISTRY_PATH = Path("fixtures/world_model/v1/review_registry.json")
OWNER_PATH = Path("docs/UNCERTAINTY_SEMANTICS_CONTRACT.md")
SOURCE_PATH = PACKAGE_DIR / "sources/uncertainty-profile.md"
REVIEW_SCOPE_ID = "uncertainty-semantics-v1-canonical"

SEMANTIC_SCOPE = (
    OWNER_PATH,
    README_PATH,
    SCHEMA_PATH,
    PACKAGE_PATH,
    COMPATIBILITY_PATH,
    SOURCE_PATH,
    Path("scripts/validate_uncertainty_fixtures.py"),
    Path("tests/test_uncertainty_fixtures.py"),
    Path(".github/workflows/etl.yml"),
)
# Accepted semantic bytes remain pinned while CI, validator and test harness
# maintenance evolve under ordinary repository review.
REVIEW_MAINTENANCE_PATHS = {
    Path("scripts/validate_uncertainty_fixtures.py"),
    Path("tests/test_uncertainty_fixtures.py"),
    Path(".github/workflows/etl.yml"),
}
READY_TRANSITION_PATHS = (OWNER_PATH, README_PATH, PACKAGE_PATH, REGISTRY_PATH)
GIT_ENVIRONMENT_OVERRIDES = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
    "GIT_DIR",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_REPLACE_REF_BASE",
    "GIT_WORK_TREE",
}
REVIEW_FIELDS = {
    "review_id",
    "reviewer_id",
    "reviewer_instance_id",
    "track",
    "independence_method",
    "artifact",
    "artifact_sha256",
    "frozen_commit",
    "reviewed_content_sha256",
    "reviewed_at",
    "decision",
    "finding_counts",
    "findings",
    "independence_attestation",
}
ARTIFACT_FIELDS = {"artifact_format", *(REVIEW_FIELDS - {"artifact", "artifact_sha256"})}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
LEXICAL_RE = {
    "year": re.compile(r"^\d{4}$"),
    "month": re.compile(r"^\d{4}-\d{2}$"),
    "day": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}


class DuplicateKeyError(ValueError):
    pass


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON number: {value}")
        ),
    )


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


@dataclass(frozen=True)
class Edge:
    ordinal: int
    inclusive: bool


def _parse_lexical(value: str, precision: str, side: str) -> int:
    if precision not in LEXICAL_RE or not LEXICAL_RE[precision].fullmatch(value):
        raise ValueError(f"non-canonical {precision} value: {value!r}")
    if precision == "year":
        year = int(value)
        parsed = date(year, 1, 1) if side == "lower" else date(year, 12, 31)
    elif precision == "month":
        year, month = (int(part) for part in value.split("-"))
        last_day = calendar.monthrange(year, month)[1]
        parsed = date(year, month, 1 if side == "lower" else last_day)
    else:
        parsed = date.fromisoformat(value)
    return parsed.toordinal()


def normalize_bound(bound: dict[str, Any] | None, side: str) -> Edge | None:
    if bound is None:
        return None
    return Edge(
        ordinal=_parse_lexical(bound["value"], bound["precision"], side),
        inclusive=bound["inclusive"],
    )


def _disjoint(
    lower: Edge | None,
    upper: Edge | None,
    query_lower: Edge,
    query_upper: Edge,
) -> bool:
    if upper is not None:
        if upper.ordinal < query_lower.ordinal:
            return True
        if upper.ordinal == query_lower.ordinal and not (
            upper.inclusive and query_lower.inclusive
        ):
            return True
    if lower is not None:
        if query_upper.ordinal < lower.ordinal:
            return True
        if query_upper.ordinal == lower.ordinal and not (
            query_upper.inclusive and lower.inclusive
        ):
            return True
    return False


def _contained(
    lower: Edge | None,
    upper: Edge | None,
    query_lower: Edge,
    query_upper: Edge,
) -> bool:
    if lower is None or upper is None:
        return False
    lower_inside = lower.ordinal > query_lower.ordinal or (
        lower.ordinal == query_lower.ordinal
        and (query_lower.inclusive or not lower.inclusive)
    )
    upper_inside = upper.ordinal < query_upper.ordinal or (
        upper.ordinal == query_upper.ordinal
        and (query_upper.inclusive or not upper.inclusive)
    )
    return lower_inside and upper_inside


def classify_window(case: dict[str, Any], query: dict[str, Any]) -> str:
    query_lower = Edge(date.fromisoformat(query["start"]).toordinal(), query["start_inclusive"])
    query_upper = Edge(date.fromisoformat(query["end"]).toordinal(), query["end_inclusive"])
    candidate_results: list[str] = []
    for candidate in case["candidates"]:
        lower = normalize_bound(candidate["lower"], "lower")
        upper = normalize_bound(candidate["upper"], "upper")
        if lower is None and upper is None:
            candidate_results.append("unknown")
        elif _disjoint(lower, upper, query_lower, query_upper):
            candidate_results.append("excluded")
        elif _contained(lower, upper, query_lower, query_upper):
            candidate_results.append("contained")
        else:
            candidate_results.append("possible_overlap")

    if candidate_results and all(result == "unknown" for result in candidate_results):
        return "unknown"
    if candidate_results and all(result == "excluded" for result in candidate_results):
        return "excluded"
    if candidate_results and all(result == "contained" for result in candidate_results):
        return "contained"
    return "possible_overlap"


def _validate_candidate(candidate: dict[str, Any], errors: list[str], context: str) -> None:
    kind = candidate["kind"]
    lower_raw = candidate["lower"]
    upper_raw = candidate["upper"]
    shape = {
        "instant": (True, True),
        "closed_interval": (True, True),
        "bounded_interval": (True, True),
        "open_start_interval": (False, True),
        "open_end_interval": (True, False),
        "approximate": (True, True),
        "unknown": (False, False),
    }[kind]
    if (lower_raw is not None, upper_raw is not None) != shape:
        errors.append(f"{context}: {kind} has invalid lower/upper shape")
        return
    if not candidate["basis_claim_refs"]:
        errors.append(f"{context}: basis_claim_refs must not be empty")

    if lower_raw is not None and lower_raw["qualifier"] in {"not_after", "approximate_end"}:
        errors.append(f"{context}: lower bound uses upper-bound qualifier")
    if upper_raw is not None and upper_raw["qualifier"] in {"not_before", "approximate_start"}:
        errors.append(f"{context}: upper bound uses lower-bound qualifier")
    if kind == "bounded_interval" and (
        lower_raw["qualifier"] != "not_before" or upper_raw["qualifier"] != "not_after"
    ):
        errors.append(f"{context}: bounded_interval must use not_before/not_after")
    if kind == "approximate" and (
        lower_raw["qualifier"] != "approximate_start"
        or upper_raw["qualifier"] != "approximate_end"
    ):
        errors.append(f"{context}: approximate must declare explicit approximate bounds")

    try:
        lower = normalize_bound(lower_raw, "lower")
        upper = normalize_bound(upper_raw, "upper")
    except (ValueError, TypeError) as exc:
        errors.append(f"{context}: {exc}")
        return
    if lower is not None and upper is not None:
        if lower.ordinal > upper.ordinal:
            errors.append(f"{context}: lower bound is after upper bound")
        if lower.ordinal == upper.ordinal and not (lower.inclusive and upper.inclusive):
            errors.append(f"{context}: empty interval at exclusive equal bounds")
    if kind == "instant" and lower_raw != upper_raw:
        errors.append(f"{context}: instant bounds must be identical")


def _validate_temporal(package: dict[str, Any], errors: list[str]) -> None:
    cases = package["temporal_cases"]
    case_ids = [case["id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("temporal case IDs must be unique")

    coverage: set[str] = set()
    has_alternatives = False
    has_exclusive = False
    for case in cases:
        candidate_ids = [candidate["id"] for candidate in case["candidates"]]
        if len(candidate_ids) != len(set(candidate_ids)):
            errors.append(f"{case['id']}: candidate IDs must be unique")
        has_alternatives |= len(candidate_ids) > 1
        normalized_candidates: set[bytes] = set()
        for candidate in case["candidates"]:
            context = f"{case['id']}/{candidate['id']}"
            _validate_candidate(candidate, errors, context)
            coverage.add(candidate["kind"])
            for side in ("lower", "upper"):
                bound = candidate[side]
                if bound:
                    coverage.add(bound["qualifier"])
                    has_exclusive |= not bound["inclusive"]
            normalized = canonical_json(
                {key: candidate[key] for key in ("kind", "lower", "upper")}
            )
            if normalized in normalized_candidates:
                errors.append(f"{case['id']}: duplicate semantic alternative")
            normalized_candidates.add(normalized)

        kinds = {candidate["kind"] for candidate in case["candidates"]}
        if len(case["candidates"]) > 1:
            expected_policy = "show_alternatives"
        elif kinds == {"unknown"}:
            expected_policy = "show_unknown"
        elif kinds & {"open_start_interval", "open_end_interval"}:
            expected_policy = "show_open_bound"
        elif kinds == {"instant"} and all(
            candidate["lower"] is not None
            and candidate["lower"]["qualifier"] == "exact"
            and candidate["upper"] == candidate["lower"]
            for candidate in case["candidates"]
        ):
            expected_policy = "show_exact"
        else:
            expected_policy = "show_possible"
        if case["projection_policy"] != expected_policy:
            errors.append(
                f"{case['id']}: temporal semantics require projection_policy {expected_policy}"
            )

        query_ids = [query["id"] for query in case["queries"]]
        if len(query_ids) != len(set(query_ids)):
            errors.append(f"{case['id']}: query IDs must be unique")
        for query in case["queries"]:
            try:
                start = date.fromisoformat(query["start"])
                end = date.fromisoformat(query["end"])
            except ValueError as exc:
                errors.append(f"{case['id']}/{query['id']}: invalid query date: {exc}")
                continue
            if start > end or (start == end and not (query["start_inclusive"] and query["end_inclusive"])):
                errors.append(f"{case['id']}/{query['id']}: empty or reversed query")
                continue
            try:
                actual = classify_window(case, query)
            except (ValueError, TypeError) as exc:
                errors.append(f"{case['id']}/{query['id']}: {exc}")
                continue
            if actual != query["expected"]:
                errors.append(
                    f"{case['id']}/{query['id']}: expected {query['expected']}, got {actual}"
                )

    required = {
        "instant",
        "bounded_interval",
        "open_start_interval",
        "open_end_interval",
        "approximate",
        "unknown",
        "not_before",
        "not_after",
    }
    missing = sorted(required - coverage)
    if missing:
        errors.append(f"temporal coverage missing: {', '.join(missing)}")
    if not has_alternatives:
        errors.append("temporal coverage requires competing alternatives")
    if not has_exclusive:
        errors.append("temporal coverage requires an exclusive boundary")


def _validate_geometry(geometry: dict[str, Any], errors: list[str], context: str) -> None:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if set(geometry) != {"type", "coordinates"}:
        errors.append(f"{context}: GeoJSON geometry envelope must be closed")
        return
    if geometry_type not in {"Point", "LineString", "Polygon"} or coordinates is None:
        errors.append(f"{context}: unsupported or incomplete GeoJSON geometry")
        return

    def valid_position(value: Any) -> bool:
        if not (
            isinstance(value, list)
            and len(value) == 2
            and all(
                isinstance(item, (int, float)) and not isinstance(item, bool)
                for item in value
            )
        ):
            return False
        longitude, latitude = value
        return -180 <= longitude <= 180 and -90 <= latitude <= 90

    if geometry_type == "Point":
        valid = valid_position(coordinates)
    elif geometry_type == "LineString":
        valid = (
            isinstance(coordinates, list)
            and len(coordinates) >= 2
            and all(valid_position(position) for position in coordinates)
        )
    else:
        valid = isinstance(coordinates, list) and bool(coordinates)
        if valid:
            for ring in coordinates:
                if not (
                    isinstance(ring, list)
                    and len(ring) >= 4
                    and all(valid_position(position) for position in ring)
                    and ring[0] == ring[-1]
                ):
                    valid = False
                    break
    if not valid:
        errors.append(f"{context}: invalid {geometry_type} coordinate shape or EPSG:4326 value")


def _validate_spatial(package: dict[str, Any], errors: list[str]) -> None:
    cases = package["spatial_cases"]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("spatial case IDs must be unique")
    modes = {case["mode"] for case in cases}
    required_modes = {
        "exact_point",
        "approximate_point",
        "named_place",
        "unknown",
        "documented_path",
        "inferred_corridor",
        "unknown_route",
    }
    if modes != required_modes:
        errors.append(f"spatial modes mismatch: {sorted(modes)}")

    for case in cases:
        mode = case["mode"]
        context = case["id"]
        geometry = case["geometry"]
        expected_policy = {
            "exact_point": "show_exact",
            "approximate_point": "show_possible",
            "named_place": "show_possible",
            "unknown": "show_unknown",
            "documented_path": "show_exact",
            "inferred_corridor": "show_inferred_geometry",
            "unknown_route": "prohibit_geometry",
        }[mode]
        if case["projection_policy"] != expected_policy:
            errors.append(
                f"{context}: {mode} requires projection_policy {expected_policy}"
            )
        if not case["basis_claim_refs"]:
            errors.append(f"{context}: basis_claim_refs must not be empty")
        if geometry is not None:
            _validate_geometry(geometry, errors, context)
        if mode in {"named_place", "unknown", "unknown_route"} and geometry is not None:
            errors.append(f"{context}: {mode} must not contain geometry")
        if mode == "named_place" and not case.get("place_ref"):
            errors.append(f"{context}: named_place requires place_ref")
        if mode == "approximate_point":
            if not case.get("tolerance_m") or not case["uncertainty_refs"]:
                errors.append(f"{context}: approximate_point requires tolerance and uncertainty")
            if not geometry or geometry.get("type") != "Point":
                errors.append(f"{context}: approximate_point requires Point geometry")
        if mode == "exact_point" and (not geometry or geometry.get("type") != "Point"):
            errors.append(f"{context}: exact_point requires Point geometry")
        if mode == "documented_path" and (not geometry or geometry.get("type") != "LineString"):
            errors.append(f"{context}: documented_path requires LineString geometry")
        if mode == "inferred_corridor":
            if not geometry or geometry.get("type") != "Polygon" or not case["uncertainty_refs"]:
                errors.append(f"{context}: inferred_corridor requires uncertain Polygon geometry")
            if case["projection_policy"] != "show_inferred_geometry":
                errors.append(f"{context}: inferred_corridor requires inferred disclosure")
        if mode == "unknown_route":
            if len(case.get("endpoint_refs", [])) != 2:
                errors.append(f"{context}: unknown_route requires exactly two endpoints")
            if case["projection_policy"] != "prohibit_geometry":
                errors.append(f"{context}: unknown_route must prohibit geometry")


def _semantic_assertions(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assertions: dict[str, dict[str, Any]] = {}
    for case in package["temporal_cases"]:
        for candidate in case["candidates"]:
            assertions[candidate["id"]] = {
                "dimension": "temporal",
                "target_ref": candidate["id"],
                "value": {
                    key: candidate[key]
                    for key in ("kind", "lower", "upper")
                },
            }
    for case in package["spatial_cases"]:
        assertions[case["id"]] = {
            "dimension": "spatial",
            "target_ref": case["id"],
            "value": {
                key: case[key]
                for key in ("mode", "geometry", "place_ref", "endpoint_refs", "tolerance_m")
                if key in case
            },
        }
    return assertions


def _semantic_items(package: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *(
            candidate
            for case in package["temporal_cases"]
            for candidate in case["candidates"]
        ),
        *package["spatial_cases"],
    ]


def _locator_passage(text: str, locator: str) -> str | None:
    start = text.find(locator)
    if start < 0:
        return None
    passage_start = start + len(locator)
    next_locator = text.find("LOCATOR[", passage_start)
    return text[passage_start:] if next_locator < 0 else text[passage_start:next_locator]


def _validate_provenance(
    root: Path,
    package: dict[str, Any],
    base_package: dict[str, Any],
    errors: list[str],
) -> None:
    collections = {
        name: package[name]
        for name in ("sources", "claims", "evidence_links", "uncertainties")
    }
    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    global_ids: set[str] = set()
    for name, values in collections.items():
        ids = [value["id"] for value in values]
        if len(ids) != len(set(ids)):
            errors.append(f"{name} IDs must be unique")
        if global_ids.intersection(ids):
            errors.append(f"{name} IDs collide with another epistemic collection")
        global_ids.update(ids)
        indexes[name] = {value["id"]: value for value in values}

    semantic_items = _semantic_items(package)
    semantic_target_ids = [item["id"] for item in semantic_items]
    if len(semantic_target_ids) != len(set(semantic_target_ids)):
        errors.append("semantic target IDs must be globally unique")
    assertions = _semantic_assertions(package)
    claims = indexes["claims"]
    links = indexes["evidence_links"]
    uncertainties = indexes["uncertainties"]
    sources = indexes["sources"]
    targets_to_claims: dict[str, list[str]] = {target: [] for target in assertions}

    for source_id, source in sources.items():
        relative = PACKAGE_DIR / source["uri"]
        try:
            source_path = _regular_repo_file(root, relative)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if _sha256(source_path) != source["sha256"]:
            errors.append(f"{source_id}: fixture source checksum mismatch")
        if source.get("historical_authority") is not False:
            errors.append(f"{source_id}: synthetic source cannot be historical authority")

    source_texts: dict[str, str] = {}
    for source_id, source in sources.items():
        path = root / PACKAGE_DIR / source["uri"]
        if path.is_file() and not path.is_symlink():
            source_texts[source_id] = path.read_text(encoding="utf-8")

    for claim_id, claim in claims.items():
        target_ref = claim["target_ref"]
        assertion = assertions.get(target_ref)
        if assertion is None:
            errors.append(f"{claim_id}: target_ref does not resolve")
            continue
        targets_to_claims[target_ref].append(claim_id)
        digest = hashlib.sha256(canonical_json(assertion)).hexdigest()
        if claim["assertion_sha256"] != digest:
            errors.append(f"{claim_id}: assertion digest does not match target semantics")
        evidence_refs = claim["evidence_link_refs"]
        if not evidence_refs:
            errors.append(f"{claim_id}: supported Claim needs a reviewed EvidenceLink")
        for evidence_ref in evidence_refs:
            link = links.get(evidence_ref)
            if link is None:
                errors.append(f"{claim_id}: unresolved EvidenceLink {evidence_ref}")
                continue
            if link["claim_id"] != claim_id:
                errors.append(f"{evidence_ref}: claim_id/back-reference mismatch")
            source_id = link["source_id"]
            passage = _locator_passage(source_texts.get(source_id, ""), link["locator"])
            if passage is None or f"ASSERTION_SHA256[{digest}]" not in passage:
                errors.append(f"{evidence_ref}: locator does not bind the exact assertion")

        for uncertainty_ref in claim["uncertainty_refs"]:
            uncertainty = uncertainties.get(uncertainty_ref)
            if uncertainty is None:
                errors.append(f"{claim_id}: unresolved Uncertainty {uncertainty_ref}")
            elif uncertainty["subject_claim_ref"] != claim_id:
                errors.append(f"{uncertainty_ref}: subject Claim mismatch")

    for target_ref, target_claims in targets_to_claims.items():
        if len(target_claims) != 1:
            errors.append(f"{target_ref}: requires exactly one bound Claim")

    for item in semantic_items:
        target_ref = item["id"]
        bound_claims = targets_to_claims.get(target_ref, [])
        if item["basis_claim_refs"] != bound_claims:
            errors.append(
                f"{target_ref}: basis_claim_refs must exactly match its target-bound Claim"
            )

        if "uncertainty_refs" in item:
            bound_uncertainties = [
                uncertainty_id
                for claim_id in bound_claims
                for uncertainty_id in claims.get(claim_id, {}).get("uncertainty_refs", [])
            ]
            if item["uncertainty_refs"] != bound_uncertainties:
                errors.append(
                    f"{target_ref}: uncertainty_refs must exactly match its bound Claim"
                )

    referenced_claims = {
        ref
        for family in (package["temporal_cases"], package["spatial_cases"])
        for case in family
        for item in (case["candidates"] if "candidates" in case else [case])
        for ref in item["basis_claim_refs"]
    }
    if referenced_claims != set(claims):
        errors.append("basis_claim_refs must resolve exactly to the extension Claim set")
    referenced_links = {
        ref for claim in claims.values() for ref in claim["evidence_link_refs"]
    }
    if referenced_links != set(links):
        errors.append("Claim evidence_link_refs must resolve exactly to the EvidenceLink set")
    referenced_sources = {link["source_id"] for link in links.values()}
    if referenced_sources != set(sources):
        errors.append("EvidenceLinks must resolve exactly to the Source set")
    for uncertainty_id, uncertainty in uncertainties.items():
        claim_id = uncertainty["subject_claim_ref"]
        claim = claims.get(claim_id)
        if claim is None:
            errors.append(f"{uncertainty_id}: subject Claim is unresolved")
            continue
        if uncertainty["basis_claim_refs"] != [claim_id]:
            errors.append(f"{uncertainty_id}: basis must exactly match its subject Claim")
        if uncertainty_id not in claim["uncertainty_refs"]:
            errors.append(f"{uncertainty_id}: Claim must link back to the Uncertainty")

    for claim_id, claim in claims.items():
        subject_uncertainties = [
            uncertainty_id
            for uncertainty_id, uncertainty in uncertainties.items()
            if uncertainty["subject_claim_ref"] == claim_id
        ]
        if claim["uncertainty_refs"] != subject_uncertainties:
            errors.append(
                f"{claim_id}: uncertainty_refs must exactly match subject-bound Uncertainties"
            )

    referenced_uncertainties = {
        ref for case in package["spatial_cases"] for ref in case["uncertainty_refs"]
    }
    if referenced_uncertainties != set(uncertainties):
        errors.append("spatial uncertainty_refs must resolve exactly to the Uncertainty set")

    base_entity_ids = {
        item.get("id") for item in base_package.get("entities", []) if isinstance(item, dict)
    }
    for case in package["spatial_cases"]:
        for ref in ([case["place_ref"]] if case.get("place_ref") else case.get("endpoint_refs", [])):
            if ref not in base_entity_ids:
                errors.append(f"{case['id']}: unresolved base place/entity ref {ref}")

    exact_targets = {"exact-point", "documented-path"}
    for target_ref in exact_targets:
        claim_id = targets_to_claims.get(target_ref, [None])[0]
        claim = claims.get(claim_id) if claim_id else None
        if not claim:
            continue
        direct = [
            links[ref]
            for ref in claim["evidence_link_refs"]
            if ref in links and links[ref]["evidence_strength"] == "direct"
        ]
        if not (
            claim["claim_kind"] == "factual"
            and claim["confidence"] == "high"
            and claim["evidence_state"] == "supported"
            and direct
        ):
            errors.append(f"{target_ref}: exact/documented projection needs direct high-confidence support")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_compatibility(root: Path, compatibility: dict[str, Any], errors: list[str]) -> None:
    base = root / BASE_COMPATIBILITY_PATH
    if not base.is_file():
        errors.append("base compatibility projection is missing")
        return
    try:
        base_projection = load_json(base)
        snapshot = base_projection["input_snapshot"]
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"base compatibility projection cannot be read: {exc}")
        return
    expected = {
        "schema_version": "1.0.0",
        "projection_id": "architecture-atlas-villa-savoye-uncertainty-v1",
        "base_projection": {
            "path": BASE_COMPATIBILITY_PATH.as_posix(),
            "sha256": _sha256(base),
        },
        "temporal_projection": {
            "input": {"date_start": snapshot["date_start"], "date_end": snapshot["date_end"]},
            "kind": "bounded_interval",
            "lower": {
                "value": snapshot["date_start"],
                "precision": "year",
                "qualifier": "not_before",
                "inclusive": True,
            },
            "upper": {
                "value": snapshot["date_end"],
                "precision": "year",
                "qualifier": "not_after",
                "inclusive": True,
            },
            "epistemic_state": "legacy_unverified",
            "projection_policy": "show_possible",
        },
        "spatial_projection": {
            "input": {
                "longitude": snapshot["longitude"],
                "latitude": snapshot["latitude"],
                "legacy_confidence": snapshot["coordinates_confidence"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [snapshot["longitude"], snapshot["latitude"]],
            },
            "target_precision": "unknown_precision",
            "epistemic_state": "missing_claim_level_locator",
            "projection_policy": "show_possible",
        },
        "losses_and_unknowns": [
            "Year fields do not establish day or month precision.",
            "The interval is queryable as a bounded possible extent, not as exact construction duration.",
            "Legacy coordinate confidence does not establish target exactness without Claim-level evidence.",
            "No locator is invented and no EvidenceLink is created by this projection.",
        ],
        "invented_fields": [],
    }
    if compatibility != expected:
        errors.append("compatibility projection must be a closed, value-bound, non-inventive projection")


def _normalized_scope_bytes(path: Path, value: bytes) -> bytes:
    if path == PACKAGE_PATH:
        package = json.loads(value.decode("utf-8"), object_pairs_hook=_strict_object)
        package["status"] = "REVIEW_REQUIRED"
        package["record_time"]["reviewed_at"] = None
        return canonical_json(package)
    if path == README_PATH:
        text = value.decode("utf-8")
        text = re.sub(
            r"^Status: `(?:REVIEW_REQUIRED|READY)`$",
            "Status: `REVIEW_REQUIRED`",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        return text.encode("utf-8")
    if path == Path("docs/UNCERTAINTY_SEMANTICS_CONTRACT.md"):
        text = value.decode("utf-8")
        text = re.sub(
            r"^- Status: `(REVIEW_REQUIRED|READY)`\.$",
            "- Status: `REVIEW_REQUIRED`.",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        return text.encode("utf-8")
    return value


def _regular_repo_file(root: Path, relative: Path | str) -> Path:
    relative_path = Path(relative)
    _require(
        not relative_path.is_absolute() and ".." not in relative_path.parts,
        f"review path must be canonical and relative: {relative_path.as_posix()}",
    )
    root_path = root.absolute()
    _require(
        root_path.is_dir() and not root_path.is_symlink(),
        "repository root must be a regular directory, not a symlink",
    )
    current = root_path
    for index, part in enumerate(relative_path.parts):
        current = current / part
        _require(not current.is_symlink(), f"review path must not contain symlinks: {relative_path}")
        if index < len(relative_path.parts) - 1:
            _require(current.is_dir(), f"review path parent must be a directory: {relative_path}")
    _require(current.is_file(), f"review artifact must be a regular file: {relative_path}")
    root_resolved = root_path.resolve(strict=True)
    current_resolved = current.resolve(strict=True)
    _require(
        current_resolved.is_relative_to(root_resolved),
        f"review artifact must resolve inside repository root: {relative_path}",
    )
    return current


def compute_review_digest(root: Path, *, maintenance_commit: str | None = None) -> str:
    digest = hashlib.sha256()
    for relative in SEMANTIC_SCOPE:
        if maintenance_commit is not None and relative in REVIEW_MAINTENANCE_PATHS:
            raw = _frozen_regular_blob(root, maintenance_commit, relative)
        else:
            raw = _regular_repo_file(root, relative).read_bytes()
        content = _normalized_scope_bytes(relative, raw)
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key in GIT_ENVIRONMENT_OVERRIDES or re.fullmatch(r"GIT_CONFIG_(KEY|VALUE)_\d+", key):
            environment.pop(key)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git_output(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", "--no-replace-objects", "-C", str(root), *args),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_git_environment(),
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip() if isinstance(exc, subprocess.CalledProcessError) else "git"
        raise ValidationError(f"git verification failed: {detail or args[0]}") from exc
    return result.stdout


def _require_git_toplevel(root: Path) -> None:
    inside = _git_output(root, "rev-parse", "--is-inside-work-tree").decode().strip()
    _require(inside == "true", "review root must be inside a Git working tree")
    top = Path(_git_output(root, "rev-parse", "--show-toplevel").decode().strip()).resolve(strict=True)
    _require(root.absolute().resolve(strict=True) == top, "review root must exactly match Git toplevel")
    graft = Path(
        _git_output(root, "rev-parse", "--path-format=absolute", "--git-path", "info/grafts")
        .decode()
        .strip()
    )
    _require(not graft.exists() and not graft.is_symlink(), "legacy Git grafts must be absent")


def _frozen_regular_blob(root: Path, commit: str, relative: Path | str) -> bytes:
    relative_path = Path(relative).as_posix()
    entry = _git_output(root, "ls-tree", commit, "--", relative_path).decode().strip()
    match = re.fullmatch(
        rf"(100644|100755) blob ([0-9a-f]{{40}})\t{re.escape(relative_path)}",
        entry,
    )
    _require(match is not None, f"review artifact must be one regular Git blob: {relative_path}")
    return _git_output(root, "cat-file", "blob", match.group(2))


def compute_review_digest_at_commit(
    root: Path,
    commit: str,
    *,
    maintenance_commit: str | None = None,
) -> str:
    _require_git_toplevel(root)
    _git_output(root, "cat-file", "-e", f"{commit}^{{commit}}")
    _git_output(root, "merge-base", "--is-ancestor", commit, "HEAD")
    digest = hashlib.sha256()
    for relative in SEMANTIC_SCOPE:
        source_commit = (
            maintenance_commit
            if maintenance_commit is not None and relative in REVIEW_MAINTENANCE_PATHS
            else commit
        )
        content = _normalized_scope_bytes(relative, _frozen_regular_blob(root, source_commit, relative))
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _utc_timestamp(value: Any) -> datetime:
    _require(
        isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value) is not None,
        "review timestamp must be UTC ISO-8601 to seconds",
    )
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise ValidationError("review timestamp is invalid") from exc


def _validate_review_state(
    root: Path,
    package: dict[str, Any],
    registry: dict[str, Any],
    *,
    require_ready: bool,
) -> None:
    _require(
        set(registry)
        == {
            "schema_version",
            "package_id",
            "status",
            "frozen_commit",
            "reviewed_content_sha256",
            "required_review_count",
            "review_scope_id",
            "reviews",
        },
        "review registry envelope must be closed",
    )
    _require(registry["schema_version"] == "1.0.0", "review registry schema version drift")
    _require(registry["package_id"] == package["package_id"], "review registry package drift")
    _require(type(registry["required_review_count"]) is int and registry["required_review_count"] == 2, "exactly two reviews are required")
    _require(registry["review_scope_id"] == REVIEW_SCOPE_ID, "review scope id drift")

    readme = _regular_repo_file(root, README_PATH).read_text(encoding="utf-8")
    owner = _regular_repo_file(root, OWNER_PATH).read_text(encoding="utf-8")
    readme_status = re.findall(r"^Status: `(REVIEW_REQUIRED|READY)`$", readme, flags=re.MULTILINE)
    owner_status = re.findall(r"^- Status: `(REVIEW_REQUIRED|READY)`\.$", owner, flags=re.MULTILINE)
    _require(readme_status == [package["status"]], "README status must match package")
    _require(owner_status == [package["status"]], "owner status must match package")

    reviews = registry["reviews"]
    _require(isinstance(reviews, list), "review registry reviews must be an array")
    identities: dict[str, list[str]] = {
        "review ids": [],
        "reviewers": [],
        "reviewer instances": [],
        "tracks": [],
        "artifacts": [],
    }
    parsed_reviews: list[dict[str, Any]] = []
    for review in reviews:
        _require(isinstance(review, dict) and set(review) == REVIEW_FIELDS, "review envelope must be closed")
        for field in ("review_id", "reviewer_id", "reviewer_instance_id"):
            _require(isinstance(review[field], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{2,}", review[field]) is not None, f"review {field} is invalid")
        _require(review["track"] in {"semantic-model", "validator-integrity"}, "review track is invalid")
        _require(review["independence_method"] == "separate_agent_task", "review independence method is invalid")
        _require(review["independence_attestation"] is True, "review independence must be attested")
        _utc_timestamp(review["reviewed_at"])
        _require(COMMIT_RE.fullmatch(review["frozen_commit"]) is not None, "review frozen_commit is invalid")
        _require(SHA_RE.fullmatch(review["reviewed_content_sha256"]) is not None, "review content digest is invalid")

        counts = review["finding_counts"]
        _require(
            isinstance(counts, dict)
            and set(counts) == {"critical", "material", "minor"}
            and all(type(counts[key]) is int and counts[key] >= 0 for key in counts),
            "review finding_counts must be a closed non-negative integer map",
        )
        findings = review["findings"]
        _require(isinstance(findings, list), "review findings must be an array")
        finding_ids: list[str] = []
        for finding in findings:
            _require(
                isinstance(finding, dict)
                and set(finding) == {"finding_id", "severity", "status", "summary"}
                and isinstance(finding["finding_id"], str)
                and finding["severity"] in {"critical", "material", "minor"}
                and finding["status"] in {"resolved", "unresolved"}
                and isinstance(finding["summary"], str)
                and finding["summary"].strip(),
                "review finding envelope is invalid",
            )
            finding_ids.append(finding["finding_id"])
        _require(len(finding_ids) == len(set(finding_ids)), "review finding ids must be unique")
        derived_counts = {
            severity: sum(finding["severity"] == severity for finding in findings)
            for severity in ("critical", "material", "minor")
        }
        unresolved_blockers = any(
            finding["severity"] in {"critical", "material"} and finding["status"] == "unresolved"
            for finding in findings
        )
        _require(counts == derived_counts, "review finding counts must be derived from findings")
        _require(review["decision"] == ("CHANGES_REQUIRED" if unresolved_blockers else "READY"), "review decision must be derived from findings")

        artifact_path = Path(review["artifact"])
        _require(
            not artifact_path.is_absolute()
            and ".." not in artifact_path.parts
            and artifact_path.parts[:3] == ("docs", "work", "reviews")
            and artifact_path.suffix == ".json",
            "review artifact path must be canonical JSON under docs/work/reviews",
        )
        artifact_file = _regular_repo_file(root, artifact_path)
        _require(SHA_RE.fullmatch(review["artifact_sha256"]) is not None and _sha256(artifact_file) == review["artifact_sha256"], "review artifact checksum drift")
        artifact = load_json(artifact_file)
        expected_artifact = {
            "artifact_format": "artemis-review-attestation-v1",
            **{key: review[key] for key in REVIEW_FIELDS if key not in {"artifact", "artifact_sha256"}},
        }
        _require(isinstance(artifact, dict) and set(artifact) == ARTIFACT_FIELDS and artifact == expected_artifact, "review artifact/registry semantic drift")

        identities["review ids"].append(review["review_id"])
        identities["reviewers"].append(review["reviewer_id"])
        identities["reviewer instances"].append(review["reviewer_instance_id"])
        identities["tracks"].append(review["track"])
        identities["artifacts"].append(review["artifact"])
        parsed_reviews.append(review)

    for label, values in identities.items():
        _require(len(values) == len(set(values)), f"{label} must be distinct")
    ready_records = (
        len(parsed_reviews) == 2
        and set(identities["tracks"]) == {"semantic-model", "validator-integrity"}
        and all(review["decision"] == "READY" for review in parsed_reviews)
    )
    expected_status = "READY" if ready_records else "REVIEW_REQUIRED"
    _require(package["status"] == registry["status"] == expected_status, "package/review registry status drift")

    created_at = _utc_timestamp(package["record_time"]["created_at"])
    reviewed_at_raw = package["record_time"]["reviewed_at"]
    if expected_status != "READY":
        _require(registry["frozen_commit"] is None and registry["reviewed_content_sha256"] is None, "REVIEW_REQUIRED registry cannot carry frozen READY metadata")
        _require(parsed_reviews == [] and reviewed_at_raw is None, "REVIEW_REQUIRED state cannot carry reviews or reviewed_at")
        _require(not require_ready, "uncertainty package is not READY")
        return

    frozen = registry["frozen_commit"]
    reviewed_digest = registry["reviewed_content_sha256"]
    _require(isinstance(frozen, str) and COMMIT_RE.fullmatch(frozen) is not None, "READY registry frozen_commit is invalid")
    _require(isinstance(reviewed_digest, str) and SHA_RE.fullmatch(reviewed_digest) is not None, "READY registry content digest is invalid")
    current_digest = compute_review_digest(root, maintenance_commit=frozen)
    _require(reviewed_digest == current_digest, "READY digest does not match current semantic scope")
    for dependency_commit in (
        package["base_package"]["merge_commit"],
        package["base_package"]["frozen_commit"],
    ):
        _git_output(root, "cat-file", "-e", f"{dependency_commit}^{{commit}}")
        _git_output(root, "merge-base", "--is-ancestor", dependency_commit, "HEAD")
    _require(
        compute_review_digest_at_commit(root, "HEAD", maintenance_commit=frozen)
        == current_digest,
        "current Git HEAD does not contain the reviewed semantic scope",
    )
    _require(compute_review_digest_at_commit(root, frozen) == current_digest, "frozen commit does not contain the reviewed semantic scope")

    artifact_paths = [Path(review["artifact"]) for review in parsed_reviews]
    for path in (*READY_TRANSITION_PATHS, *artifact_paths):
        _require(
            _regular_repo_file(root, path).read_bytes() == _frozen_regular_blob(root, "HEAD", path),
            f"READY transition artifact must exactly match Git HEAD: {path}",
        )
    for review in parsed_reviews:
        _require(review["frozen_commit"] == frozen, "reviews must bind the same frozen commit")
        _require(review["reviewed_content_sha256"] == current_digest, "review must bind the reviewed semantic digest")

    frozen_time = datetime.fromisoformat(_git_output(root, "show", "-s", "--format=%cI", frozen).decode().strip()).astimezone(UTC)
    reviewed_at = _utc_timestamp(reviewed_at_raw)
    review_times = [_utc_timestamp(review["reviewed_at"]) for review in parsed_reviews]
    now = datetime.now(UTC)
    _require(created_at <= reviewed_at <= now, "package review chronology is invalid")
    _require(all(frozen_time <= value <= reviewed_at for value in review_times), "review chronology is invalid")


def validate_repository(root: Path, require_ready: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json(root / SCHEMA_PATH)
        package = load_json(root / PACKAGE_PATH)
        registry = load_json(root / REGISTRY_PATH)
        compatibility = load_json(root / COMPATIBILITY_PATH)
        base_package = load_json(root / BASE_PACKAGE_PATH)
        base_registry = load_json(root / BASE_REGISTRY_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"fixture JSON load failed: {exc}"]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(package), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"schema {location}: {error.message}")

    if errors:
        return errors

    if base_package.get("status") != "READY":
        errors.append("base world-model package must remain READY")
    if package["base_package"]["status"] != base_package.get("status"):
        errors.append("declared base status does not match base package")
    if (
        base_registry.get("status") != "READY"
        or base_registry.get("frozen_commit") != package["base_package"]["frozen_commit"]
        or base_registry.get("reviewed_content_sha256")
        != package["base_package"]["reviewed_content_sha256"]
    ):
        errors.append("declared base package does not match the reviewed READY registry")
    _validate_temporal(package, errors)
    _validate_spatial(package, errors)
    _validate_provenance(root, package, base_package, errors)
    _validate_compatibility(root, compatibility, errors)

    owner = (root / OWNER_PATH).read_text(encoding="utf-8")
    owner_statuses = re.findall(
        r"^- Status: `(REVIEW_REQUIRED|READY)`\.$", owner, flags=re.MULTILINE
    )
    if owner_statuses != [package["status"]]:
        errors.append("uncertainty owner status must agree with package")
    for required_term in (
        "not_before",
        "not_after",
        "possible_overlap",
        "unknown_route",
        "unknown_precision",
    ):
        if required_term not in owner:
            errors.append(f"uncertainty owner contract missing {required_term}")

    policy_ids = [policy["id"] for policy in package["projection_policies"]]
    if len(policy_ids) != len(set(policy_ids)):
        errors.append("projection policy IDs must be unique")
    used_policies = {
        case["projection_policy"]
        for family in (package["temporal_cases"], package["spatial_cases"])
        for case in family
    }
    if not used_policies.issubset(set(policy_ids)):
        errors.append("case references unknown projection policy")

    try:
        _validate_review_state(root, package, registry, require_ready=require_ready)
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        errors.append(f"review gate: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_repository(root, require_ready=args.require_ready)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    package = load_json(root / PACKAGE_PATH)
    print(
        f"uncertainty fixtures valid: {len(package['temporal_cases'])} temporal, "
        f"{len(package['spatial_cases'])} spatial; status={package['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
