#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

try:
    from scripts import validate_uncertainty_fixtures as uncertainty_validator
except ModuleNotFoundError:  # direct `python scripts/...` execution
    import validate_uncertainty_fixtures as uncertainty_validator


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = Path("fixtures/world_model/relations/v1/package.json")
SCHEMA_PATH = Path("fixtures/world_model/relations/v1/schema.json")
REGISTRY_PATH = Path("fixtures/world_model/relations/v1/review_registry.json")
README_PATH = Path("fixtures/world_model/relations/v1/README.md")
COMPATIBILITY_PATH = Path("fixtures/world_model/relations/v1/compatibility/architecture_atlas_projection.json")
OWNER_PATH = Path("docs/RELATION_LADDER_CONTRACT.md")
WORK_PATH = Path("docs/work/2026-08-05_RELATION_LADDER_REVIEW.md")
REVIEW_SCOPE = (
    PACKAGE_PATH,
    SCHEMA_PATH,
    README_PATH,
    COMPATIBILITY_PATH,
    Path("fixtures/world_model/relations/v1/sources/relation-profile.md"),
    OWNER_PATH,
    WORK_PATH,
    Path("scripts/validate_relation_fixtures.py"),
    Path("tests/test_relation_fixtures.py"),
    Path(".github/workflows/relation-contract.yml"),
)
PREDICATES = ("co_present", "possible_encounter", "documented_encounter", "interaction", "influence", "causal")
DOCUMENTED = {"documented_encounter", "interaction", "influence", "causal"}
OVERLAP_STATES = {"confirmed", "possible", "excluded", "unknown"}
EXPECTED_PREDICATE_PROFILE = {
    "co_present": {
        "family": "derived_proximity",
        "storage_kind": "computed_observation",
        "definition": "Declared temporal and spatial extents overlap with a visible confirmed or possible result.",
        "minimum_basis": [
            "reviewed #330 extent semantics",
            "deterministic overlap evaluation",
            "visible extent uncertainty",
        ],
        "directionality": "symmetric",
        "requires_co_presence": False,
    },
    "possible_encounter": {
        "family": "encounter_inference",
        "storage_kind": "explicit_inference",
        "definition": "An encounter is plausible under named assumptions after a co-presence signal is computed.",
        "minimum_basis": [
            "co-presence signal",
            "explicit assumptions",
            "relation uncertainty",
        ],
        "directionality": "symmetric",
        "requires_co_presence": True,
    },
    "documented_encounter": {
        "family": "documented_contact",
        "storage_kind": "relation_claim",
        "definition": "A reviewed source passage independently documents a meeting or contact.",
        "minimum_basis": [
            "atomic RelationClaim",
            "supporting EvidenceLink",
            "reproducible locator",
        ],
        "directionality": "directed_or_symmetric",
        "requires_co_presence": False,
    },
    "interaction": {
        "family": "documented_action",
        "storage_kind": "relation_claim",
        "definition": "A reviewed source independently documents an action or exchange, including distance channels.",
        "minimum_basis": [
            "interaction Claim",
            "specific action and channel",
            "supporting locator",
        ],
        "directionality": "directed_or_symmetric",
        "requires_co_presence": False,
    },
    "influence": {
        "family": "historical_effect",
        "storage_kind": "relation_claim",
        "definition": "A directional historical effect is asserted with mechanism, transmission mode and bounded scope.",
        "minimum_basis": [
            "direction",
            "mechanism",
            "transmission mode",
            "scope",
            "supporting evidence",
        ],
        "directionality": "directed",
        "requires_co_presence": False,
    },
    "causal": {
        "family": "causal_explanation",
        "storage_kind": "relation_claim",
        "definition": "A causal dependency between entities or processes is separately justified under an explicit policy.",
        "minimum_basis": [
            "causal RelationClaim",
            "distinct causal basis Claim",
            "policy reference",
        ],
        "directionality": "directed",
        "requires_co_presence": False,
    },
}
EXPECTED_RULES = {
    ("co_present", "possible_encounter"): "conditional_derivation",
    ("possible_encounter", "documented_encounter"): "independent_predicate_evidence",
    ("documented_encounter", "interaction"): "independent_predicate_evidence",
    ("interaction", "influence"): "independent_predicate_evidence",
    ("influence", "causal"): "independent_predicate_evidence",
}
EXPECTED_RULE_BASES = {
    ("co_present", "possible_encounter"): [
        "explicit assumptions",
        "relation uncertainty",
        "inference Claim",
    ],
    ("possible_encounter", "documented_encounter"): [
        "source-bound encounter Claim",
        "reviewed locator",
    ],
    ("documented_encounter", "interaction"): [
        "specific action and channel",
        "supporting locator",
    ],
    ("interaction", "influence"): [
        "direction",
        "mechanism",
        "transmission mode",
        "scope",
        "supporting evidence",
    ],
    ("influence", "causal"): [
        "distinct causal basis Claim",
        "causal policy reference",
    ],
}
EXPECTED_UI_RULES = {
    "co_present": {
        "required_label": "Present in overlapping declared extents",
        "forbidden_phrases": ["met", "knew", "interacted", "influenced", "caused"],
        "source_access_required": False,
    },
    "possible_encounter": {
        "required_label": "May have encountered, if the listed assumptions hold",
        "forbidden_phrases": ["met", "documented encounter", "interacted", "influenced", "caused"],
        "source_access_required": False,
    },
    "documented_encounter": {
        "required_label": "Documented meeting/contact",
        "forbidden_phrases": ["exchanged", "interacted", "influenced", "caused"],
        "source_access_required": True,
    },
    "interaction": {
        "required_label": "Documented action or exchange",
        "forbidden_phrases": ["influenced", "caused"],
        "source_access_required": True,
    },
    "influence": {
        "required_label": "Supported directional influence within the stated scope",
        "forbidden_phrases": ["caused", "necessarily caused"],
        "source_access_required": True,
    },
    "causal": {
        "required_label": "Separately justified causal claim",
        "forbidden_phrases": ["proven beyond the reviewed scope"],
        "source_access_required": True,
    },
}
CLAIM_DIGEST_KEYS = (
    "target_ref", "subject_ref", "predicate", "object_ref", "statement", "qualifiers",
    "claim_kind", "origin", "review_state", "confidence", "evidence_state",
)


class DuplicateKeyError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def claim_digest(claim: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical({key: claim[key] for key in CLAIM_DIGEST_KEYS})).hexdigest()


def _normalized_bytes(path: Path, data: bytes) -> bytes:
    if path == PACKAGE_PATH:
        value = json.loads(data, object_pairs_hook=_strict_object)
        value["status"] = "REVIEW_REQUIRED"
        value["record_time"]["reviewed_at"] = None
        return _canonical(value) + b"\n"
    text = data.decode("utf-8")
    if path in {README_PATH, OWNER_PATH}:
        text = text.replace("Status: `READY`", "Status: `REVIEW_REQUIRED`", 1)
    if path == WORK_PATH:
        text = re.sub(r"- State: `(?:REVIEW_REQUIRED|READY)`\.", "- State: `REVIEW_REQUIRED`.", text, count=1)
        text = re.sub(r"- Frozen commit: `[^`]+`\.", "- Frozen commit: `PENDING`.", text, count=1)
        text = re.sub(r"- Reviewed digest: `[^`]+`\.", "- Reviewed digest: `PENDING`.", text, count=1)
    return text.encode("utf-8")


def compute_review_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in REVIEW_SCOPE:
        path = root / relative
        data = _normalized_bytes(relative, path.read_bytes())
        digest.update(str(relative).encode("utf-8") + b"\0" + data + b"\0")
    return digest.hexdigest()


def _git_output(root: Path, *args: str) -> bytes:
    env = {key: value for key, value in os.environ.items() if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_REPLACE_REF_BASE"}}
    return subprocess.run(("git", "-C", str(root), *args), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).stdout


def _ids(items: list[dict[str, Any]]) -> list[str]:
    return [item["id"] for item in items]


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _intervals_disjoint(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_lower = uncertainty_validator.normalize_bound(left["lower"], "lower")
    left_upper = uncertainty_validator.normalize_bound(left["upper"], "upper")
    right_lower = uncertainty_validator.normalize_bound(right["lower"], "lower")
    right_upper = uncertainty_validator.normalize_bound(right["upper"], "upper")

    def before(upper: Any, lower: Any) -> bool:
        if upper is None or lower is None:
            return False
        return upper.ordinal < lower.ordinal or (
            upper.ordinal == lower.ordinal and not (upper.inclusive and lower.inclusive)
        )

    return before(left_upper, right_lower) or before(right_upper, left_lower)


def _temporal_pair_state(left: dict[str, Any], right: dict[str, Any]) -> str:
    if left["kind"] == "unknown" or right["kind"] == "unknown":
        return "unknown"
    if _intervals_disjoint(left, right):
        return "excluded"
    exact_kinds = {"instant", "closed_interval"}
    exact = left["kind"] in exact_kinds and right["kind"] in exact_kinds
    for candidate in (left, right):
        for side in ("lower", "upper"):
            bound = candidate[side]
            exact &= (
                bound is not None
                and bound["qualifier"] == "exact"
                and bound["precision"] == "day"
            )
    return "confirmed" if exact else "possible"


def _aggregate_states(states: list[str]) -> str:
    if states and all(state == "excluded" for state in states):
        return "excluded"
    if states and all(state == "confirmed" for state in states):
        return "confirmed"
    if any(state in {"confirmed", "possible"} for state in states):
        return "possible"
    return "unknown"


def _temporal_overlap(left: dict[str, Any], right: dict[str, Any]) -> str:
    return _aggregate_states(
        [
            _temporal_pair_state(a, b)
            for a in left["temporal_candidates"]
            for b in right["temporal_candidates"]
        ]
    )


def _place_ancestors(place_ref: str, parents: dict[str, str]) -> set[str]:
    result = {place_ref}
    while place_ref in parents:
        place_ref = parents[place_ref]
        if place_ref in result:
            break
        result.add(place_ref)
    return result


def _point(candidate: dict[str, Any]) -> tuple[float, float] | None:
    geometry = candidate.get("geometry")
    if geometry and geometry.get("type") == "Point":
        longitude, latitude = geometry["coordinates"]
        return float(longitude), float(latitude)
    return None


def _distance_m(left: tuple[float, float], right: tuple[float, float]) -> float:
    lon1, lat1 = (math.radians(value) for value in left)
    lon2, lat2 = (math.radians(value) for value in right)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _point_in_polygon(point: tuple[float, float], polygon: list[list[list[float]]]) -> bool:
    x, y = point
    ring = polygon[0]
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y):
            boundary_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < boundary_x:
                inside = not inside
        previous = current
    return inside


def _spatial_pair_state(left: dict[str, Any], right: dict[str, Any], parents: dict[str, str]) -> str:
    left_mode = left["mode"]
    right_mode = right["mode"]
    if left_mode in {"unknown", "unknown_route"} or right_mode in {"unknown", "unknown_route"}:
        return "unknown"
    if left_mode == right_mode == "named_place":
        left_place = left["place_ref"]
        right_place = right["place_ref"]
        related = (
            left_place in _place_ancestors(right_place, parents)
            or right_place in _place_ancestors(left_place, parents)
        )
        return "confirmed" if related else "excluded"

    left_point = _point(left)
    right_point = _point(right)
    if left_point is not None and right_point is not None:
        tolerance = float(left.get("tolerance_m", 0)) + float(right.get("tolerance_m", 0))
        distance = _distance_m(left_point, right_point)
        if tolerance == 0:
            return "confirmed" if distance < 0.01 else "excluded"
        return "possible" if distance <= tolerance else "excluded"

    for area, point_candidate in ((left, right), (right, left)):
        geometry = area.get("geometry")
        point_value = _point(point_candidate)
        if area["mode"] == "inferred_corridor" and geometry and point_value is not None:
            return "possible" if _point_in_polygon(point_value, geometry["coordinates"]) else "excluded"
    return "unknown"


def _spatial_overlap(left: dict[str, Any], right: dict[str, Any], parents: dict[str, str]) -> str:
    return _aggregate_states(
        [
            _spatial_pair_state(a, b, parents)
            for a in left["spatial_candidates"]
            for b in right["spatial_candidates"]
        ]
    )


def co_presence_state(case: dict[str, Any], parents: dict[str, str]) -> str:
    subject = next(
        presence for presence in case["presence_extents"]
        if presence["entity_ref"] == case["subject_ref"]
    )
    obj = next(
        presence for presence in case["presence_extents"]
        if presence["entity_ref"] == case["object_ref"]
    )
    temporal = _temporal_overlap(subject, obj)
    spatial = _spatial_overlap(subject, obj, parents)
    if "excluded" in {temporal, spatial}:
        return "excluded"
    if "unknown" in {temporal, spatial}:
        return "unknown"
    if temporal == spatial == "confirmed":
        return "confirmed"
    return "possible"


def is_co_present(case: dict[str, Any], parents: dict[str, str] | None = None) -> bool:
    return co_presence_state(case, parents or {}) in {"confirmed", "possible"}


def _validate_base_packages(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    for declared in package["base_packages"]:
        registry_path = root / declared["registry_path"]
        try:
            actual = load_json(registry_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"base registry load failed: {exc}")
            continue
        for key in ("package_id", "status", "frozen_commit", "reviewed_content_sha256"):
            _require(declared[key] == actual.get(key), f"base package binding mismatch for {declared['package_id']}: {key}", errors)


def _validate_spatial_candidate(candidate: dict[str, Any], errors: list[str], context: str) -> None:
    mode = candidate["mode"]
    geometry = candidate["geometry"]
    if not candidate["basis_claim_refs"]:
        errors.append(f"{context}: basis_claim_refs must not be empty")
    if geometry is not None:
        uncertainty_validator._validate_geometry(geometry, errors, context)
    if mode in {"named_place", "unknown", "unknown_route"} and geometry is not None:
        errors.append(f"{context}: {mode} must not contain geometry")
    if mode == "named_place" and not candidate.get("place_ref"):
        errors.append(f"{context}: named_place requires place_ref")
    if mode == "approximate_point" and (
        not candidate.get("tolerance_m")
        or not candidate["uncertainty_refs"]
        or not geometry
        or geometry.get("type") != "Point"
    ):
        errors.append(f"{context}: approximate_point requires Point, tolerance and uncertainty")
    if mode == "exact_point" and (not geometry or geometry.get("type") != "Point"):
        errors.append(f"{context}: exact_point requires Point geometry")
    if mode == "documented_path" and (not geometry or geometry.get("type") != "LineString"):
        errors.append(f"{context}: documented_path requires LineString geometry")
    if mode == "inferred_corridor" and (
        not geometry
        or geometry.get("type") != "Polygon"
        or not candidate["uncertainty_refs"]
    ):
        errors.append(f"{context}: inferred_corridor requires uncertain Polygon geometry")
    if mode == "unknown_route" and len(candidate.get("endpoint_refs", [])) != 2:
        errors.append(f"{context}: unknown_route requires exactly two endpoints")
    expected_policy = {
        "exact_point": "show_exact",
        "approximate_point": "show_possible",
        "named_place": "show_possible",
        "unknown": "show_unknown",
        "documented_path": "show_exact",
        "inferred_corridor": "show_inferred_geometry",
        "unknown_route": "prohibit_geometry",
    }[mode]
    if candidate["projection_policy"] != expected_policy:
        errors.append(f"{context}: {mode} requires projection_policy {expected_policy}")


def _validate_extent_semantics(
    root: Path, schema: dict[str, Any], package: dict[str, Any], errors: list[str]
) -> dict[str, str]:
    uncertainty_schema = load_json(
        root / "fixtures/world_model/uncertainty/v1/schema.json"
    )
    for definition in ("bound", "candidate", "spatialCase"):
        _require(
            schema["$defs"][definition] == uncertainty_schema["$defs"][definition],
            f"relation extent schema must consume the reviewed #330 {definition} definition exactly",
            errors,
        )

    uncertainty_package = load_json(
        root / "fixtures/world_model/uncertainty/v1/package.json"
    )
    claim_targets = {
        claim["id"]: claim["target_ref"] for claim in uncertainty_package["claims"]
    }
    temporal_target_kinds = {
        candidate["id"]: candidate["kind"]
        for case in uncertainty_package["temporal_cases"]
        for candidate in case["candidates"]
    }
    spatial_target_modes = {
        case["id"]: case["mode"] for case in uncertainty_package["spatial_cases"]
    }
    base_uncertainty_ids = {
        item["id"] for item in uncertainty_package["uncertainties"]
    }

    hierarchy = package["place_hierarchy"]
    parents = {item["child_ref"]: item["parent_ref"] for item in hierarchy}
    _require(
        len(parents) == len(hierarchy),
        "place hierarchy children must be unique",
        errors,
    )
    for child in parents:
        seen = {child}
        current = child
        while current in parents:
            current = parents[current]
            if current in seen:
                errors.append(f"place hierarchy cycle at {child}")
                break
            seen.add(current)

    presence_ids: list[str] = []
    for case in package["cases"]:
        entity_refs = [presence["entity_ref"] for presence in case["presence_extents"]]
        _require(
            entity_refs.count(case["subject_ref"]) == 1
            and entity_refs.count(case["object_ref"]) == 1,
            f"case {case['id']} must bind exactly one extent to each endpoint",
            errors,
        )
        for presence in case["presence_extents"]:
            presence_ids.append(presence["id"])
            temporal_ids = [item["id"] for item in presence["temporal_candidates"]]
            spatial_ids = [item["id"] for item in presence["spatial_candidates"]]
            _require(
                len(temporal_ids) == len(set(temporal_ids)),
                f"presence {presence['id']} temporal candidate IDs must be unique",
                errors,
            )
            _require(
                len(spatial_ids) == len(set(spatial_ids)),
                f"presence {presence['id']} spatial candidate IDs must be unique",
                errors,
            )
            for candidate in presence["temporal_candidates"]:
                uncertainty_validator._validate_candidate(
                    candidate, errors, f"{presence['id']}/{candidate['id']}"
                )
                for ref in candidate["basis_claim_refs"]:
                    _require(
                        temporal_target_kinds.get(claim_targets.get(ref))
                        == candidate["kind"],
                        f"{presence['id']}/{candidate['id']} must bind to a reviewed #330 temporal semantic profile",
                        errors,
                    )
            for candidate in presence["spatial_candidates"]:
                _validate_spatial_candidate(
                    candidate, errors, f"{presence['id']}/{candidate['id']}"
                )
                for ref in candidate["basis_claim_refs"]:
                    _require(
                        spatial_target_modes.get(claim_targets.get(ref))
                        == candidate["mode"],
                        f"{presence['id']}/{candidate['id']} must bind to a reviewed #330 spatial semantic profile",
                        errors,
                    )
                _require(
                    set(candidate["uncertainty_refs"]) <= base_uncertainty_ids,
                    f"{presence['id']}/{candidate['id']} has an uncertainty outside the reviewed #330 profile",
                    errors,
                )
            expected_uncertainties = {
                ref
                for candidate in presence["spatial_candidates"]
                for ref in candidate["uncertainty_refs"]
            }
            _require(
                set(presence["uncertainty_refs"]) == expected_uncertainties,
                f"presence {presence['id']} uncertainty binding mismatch",
                errors,
            )
    _require(
        len(presence_ids) == len(set(presence_ids)),
        "presence extent IDs must be globally unique",
        errors,
    )
    return parents


def _validate_predicate_profile(package: dict[str, Any], errors: list[str]) -> None:
    predicates = package["relation_predicates"]
    _require(
        {item["id"] for item in predicates} == set(PREDICATES)
        and len(predicates) == len(PREDICATES),
        "relation predicates must be unique and cover the closed profile",
        errors,
    )
    _require(
        all("rank" not in item for item in predicates),
        "relation predicates must not encode a global rank",
        errors,
    )
    indexed = {item["id"]: item for item in predicates}
    for predicate, expected in EXPECTED_PREDICATE_PROFILE.items():
        actual = indexed.get(predicate)
        if actual is None:
            continue
        _require(
            {key: actual[key] for key in expected} == expected,
            f"relation predicate {predicate} semantic profile drift",
            errors,
        )
    _require(
        indexed["co_present"]["storage_kind"] == "computed_observation",
        "co_present must remain a computed observation",
        errors,
    )
    _require(
        indexed["possible_encounter"]["storage_kind"] == "explicit_inference"
        and indexed["possible_encounter"]["requires_co_presence"] is True,
        "possible_encounter must remain an explicit co-presence-bound inference",
        errors,
    )
    _require(
        all(
            indexed[predicate]["storage_kind"] == "relation_claim"
            and indexed[predicate]["requires_co_presence"] is False
            for predicate in DOCUMENTED
        ),
        "documented predicates must be independent RelationClaims without a co-presence prerequisite",
        errors,
    )

    rules = package["promotion_rules"]
    actual_rules = {
        (item["from"], item["to"]): item["rule_kind"] for item in rules
    }
    _require(
        actual_rules == EXPECTED_RULES and len(rules) == len(EXPECTED_RULES),
        "promotion rules must cover the five regression boundaries without defining a total order",
        errors,
    )
    _require(
        all(item["automatic"] is False for item in rules),
        "automatic predicate promotion is forbidden",
        errors,
    )
    for rule in rules:
        pair = (rule["from"], rule["to"])
        _require(
            rule["required_basis"] == EXPECTED_RULE_BASES.get(pair),
            f"promotion boundary {pair[0]} -> {pair[1]} basis drift",
            errors,
        )


def _validate_ui_language(package: dict[str, Any], errors: list[str]) -> None:
    rules = package["ui_language_rules"]
    indexed = {item["predicate"]: item for item in rules}
    _require(
        len(indexed) == len(rules) == len(EXPECTED_UI_RULES)
        and set(indexed) == set(EXPECTED_UI_RULES),
        "UI language rules must uniquely cover every relation predicate",
        errors,
    )
    for predicate, expected in EXPECTED_UI_RULES.items():
        actual = indexed.get(predicate)
        if actual is None:
            continue
        _require(
            actual["required_label"] == expected["required_label"],
            f"UI rule {predicate} required label drift",
            errors,
        )
        _require(
            actual["forbidden_phrases"] == expected["forbidden_phrases"],
            f"UI rule {predicate} forbidden implication coverage drift",
            errors,
        )
        _require(
            actual["source_access_required"] is expected["source_access_required"],
            f"UI rule {predicate} source-access requirement drift",
            errors,
        )


def _validate_provenance(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    claims = {item["id"]: item for item in package["claims"]}
    sources = {item["id"]: item for item in package["sources"]}
    evidence = package["evidence_links"]
    _require(len(claims) == len(package["claims"]), "claim IDs must be unique", errors)
    _require(len(sources) == len(package["sources"]), "source IDs must be unique", errors)
    _require(len(_ids(evidence)) == len(set(_ids(evidence))), "EvidenceLink IDs must be unique", errors)

    for claim in claims.values():
        _require(claim["assertion_sha256"] == claim_digest(claim), f"claim {claim['id']} assertion digest mismatch", errors)

    for link in evidence:
        claim = claims.get(link["claim_id"])
        source = sources.get(link["source_id"])
        _require(claim is not None, f"EvidenceLink {link['id']} has dangling claim", errors)
        _require(source is not None, f"EvidenceLink {link['id']} has dangling source", errors)
        if claim is None or source is None:
            continue
        try:
            source_text = (root / source["path"]).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"source file load failed for {source['id']}: {exc}")
            continue
        expected = f"{link['locator']} SHA256[{claim['assertion_sha256']}]"
        _require(expected in source_text, f"EvidenceLink {link['id']} locator does not bind its exact Claim digest", errors)

    for claim in claims.values():
        supporting = [link for link in evidence if link["claim_id"] == claim["id"] and link["relation_to_claim"] == "supports" and link["review_state"] == "reviewed"]
        if claim["evidence_state"] == "supported":
            _require(bool(supporting), f"supported Claim {claim['id']} requires reviewed supporting evidence", errors)
        else:
            _require(not supporting, f"non-supported Claim {claim['id']} must not have supporting evidence", errors)


def _validate_case(
    case: dict[str, Any],
    claims: dict[str, dict[str, Any]],
    evidence: list[dict[str, Any]],
    uncertainties: dict[str, dict[str, Any]],
    parents: dict[str, str],
    errors: list[str],
) -> None:
    predicate = case["asserted_predicate"]
    observed = co_presence_state(case, parents)
    _require(
        observed == case["co_presence_result"],
        f"case {case['id']} co-presence result mismatch: expected {case['co_presence_result']}, got {observed}",
        errors,
    )
    claim = (
        claims.get(case["relation_claim_ref"])
        if case["relation_claim_ref"]
        else None
    )
    if predicate == "none":
        _require(
            observed == "excluded",
            f"case {case['id']} none requires an excluded co-presence result",
            errors,
        )
        _require(claim is None, f"case {case['id']} none must not create a Claim", errors)
        return
    if predicate == "co_present":
        _require(
            observed in {"confirmed", "possible"},
            f"case {case['id']} cannot assert co_present from {observed} extents",
            errors,
        )
        _require(
            claim is None,
            f"case {case['id']} computed co-presence must not create a historical Relation",
            errors,
        )
        return

    _require(
        claim is not None,
        f"case {case['id']} predicate {predicate} requires an item-bound Claim",
        errors,
    )
    if claim is None:
        return
    _require(claim["target_ref"] == case["id"], f"case {case['id']} Claim target binding mismatch", errors)
    _require(claim["subject_ref"] == case["subject_ref"] and claim["object_ref"] == case["object_ref"], f"case {case['id']} Claim endpoint binding mismatch", errors)
    _require(claim["predicate"] == predicate, f"case {case['id']} Claim predicate does not support asserted predicate", errors)

    if predicate == "possible_encounter":
        _require(
            observed in {"confirmed", "possible"},
            f"case {case['id']} possible encounter requires a co-presence signal",
            errors,
        )
        _require(bool(case["assumptions"]), f"case {case['id']} possible encounter requires explicit assumptions", errors)
        _require(bool(case["uncertainty_refs"]), f"case {case['id']} possible encounter requires relation uncertainty", errors)
        _require(claim["claim_kind"] == "inference" and claim["evidence_state"] == "missing", f"case {case['id']} possible encounter must remain an unsupported inference", errors)
        claim_assumptions = set(claim["qualifiers"].get("assumption_refs", []))
        _require(claim_assumptions == {item["id"] for item in case["assumptions"]}, f"case {case['id']} assumption binding mismatch", errors)
        for ref in case["uncertainty_refs"]:
            uncertainty = uncertainties.get(ref)
            _require(uncertainty is not None and uncertainty["subject_claim_ref"] == claim["id"], f"case {case['id']} uncertainty binding mismatch", errors)
        return

    _require(predicate in DOCUMENTED, f"case {case['id']} uses unknown documented predicate", errors)
    _require(claim["review_state"] == "reviewed" and claim["evidence_state"] == "supported", f"case {case['id']} documented predicate requires reviewed supported Claim", errors)
    supporting = [link for link in evidence if link["claim_id"] == claim["id"] and link["relation_to_claim"] == "supports" and link["review_state"] == "reviewed"]
    _require(bool(supporting), f"case {case['id']} documented predicate requires a supporting locator", errors)
    qualifiers = claim["qualifiers"]
    if predicate == "documented_encounter":
        _require(bool(qualifiers.get("contact_kind")), f"case {case['id']} encounter evidence must name contact kind", errors)
    elif predicate == "interaction":
        _require(
            bool(qualifiers.get("action"))
            and qualifiers.get("channel")
            in {"in_person", "correspondence", "intermediary", "institutional"},
            f"case {case['id']} interaction requires a specific action and channel",
            errors,
        )
    elif predicate == "influence":
        _require(
            qualifiers.get("direction") == "subject_to_object"
            and bool(qualifiers.get("mechanism"))
            and bool(qualifiers.get("scope"))
            and qualifiers.get("transmission_mode")
            in {"direct", "correspondence", "text", "intermediary", "institution"},
            f"case {case['id']} influence requires direction, mechanism, scope and transmission mode",
            errors,
        )
    elif predicate == "causal":
        _require(qualifiers.get("direction") == "subject_to_object" and bool(qualifiers.get("mechanism")) and bool(qualifiers.get("scope")) and bool(qualifiers.get("counterfactual_basis")), f"case {case['id']} causal Claim requires direction, mechanism, scope and counterfactual basis", errors)
        basis = claims.get(case["causal_basis_claim_ref"])
        _require(case["causal_basis_claim_ref"] != claim["id"] and basis is not None, f"case {case['id']} causal basis must be a distinct Claim", errors)
        if basis is not None:
            _require(basis["target_ref"] == case["id"] and basis["predicate"] == "causal_basis", f"case {case['id']} causal basis binding mismatch", errors)
            _require(any(link["claim_id"] == basis["id"] and link["relation_to_claim"] == "supports" for link in evidence), f"case {case['id']} causal basis requires supporting evidence", errors)
        _require(case["causal_policy_ref"] == "causal-policy-explicit-basis-v1", f"case {case['id']} causal policy reference is missing", errors)


def _validate_cases(
    package: dict[str, Any], parents: dict[str, str], errors: list[str]
) -> None:
    claims = {item["id"]: item for item in package["claims"]}
    uncertainties = {item["id"]: item for item in package["uncertainties"]}
    _require(
        len(claims) == len(package["claims"]),
        "Claim IDs must be unique",
        errors,
    )
    _require(
        len(uncertainties) == len(package["uncertainties"]),
        "relation uncertainty IDs must be unique",
        errors,
    )
    case_ids = _ids(package["cases"])
    _require(len(case_ids) == len(set(case_ids)), "case IDs must be unique", errors)
    roles = {item["fixture_role"] for item in package["cases"]}
    _require(roles == {"positive", "negative", "ambiguous"}, "fixtures must include positive, negative and ambiguous roles", errors)
    expected = {"none", *PREDICATES}
    _require(
        {item["asserted_predicate"] for item in package["cases"]} == expected,
        "fixtures must cover none and every relation predicate",
        errors,
    )
    _require(
        {item["co_presence_result"] for item in package["cases"]} == OVERLAP_STATES,
        "fixtures must cover confirmed, possible, excluded and unknown co-presence results",
        errors,
    )
    case_claim_refs = [
        ref
        for case in package["cases"]
        for ref in (case["relation_claim_ref"], case["causal_basis_claim_ref"])
        if ref is not None
    ]
    _require(
        len(case_claim_refs) == len(set(case_claim_refs))
        and set(case_claim_refs) == set(claims),
        "every relation Claim must bind to exactly one fixture case role",
        errors,
    )
    for uncertainty in uncertainties.values():
        _require(
            uncertainty["subject_claim_ref"] in claims,
            f"uncertainty {uncertainty['id']} has dangling Claim binding",
            errors,
        )
    for case in package["cases"]:
        try:
            for ref in case["uncertainty_refs"]:
                uncertainty = uncertainties.get(ref)
                _require(
                    uncertainty is not None
                    and uncertainty["subject_claim_ref"]
                    == case["relation_claim_ref"],
                    f"case {case['id']} relation uncertainty binding mismatch",
                    errors,
                )
            _validate_case(
                case,
                claims,
                package["evidence_links"],
                uncertainties,
                parents,
                errors,
            )
        except (ValueError, KeyError) as exc:
            errors.append(f"case {case.get('id', '<unknown>')} invalid: {exc}")


def _validate_separation(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    expected_non_relations = {("classification", False), ("similarity", False)}
    _require({(item["signal_kind"], item["creates_relation"]) for item in package["non_relation_cases"]} == expected_non_relations, "classification and Similarity must remain separate non-Relations", errors)
    compatibility = load_json(root / COMPATIBILITY_PATH)
    _require(
        set(compatibility)
        == {
            "schema_version",
            "source_artifact",
            "same_movement",
            "similarity",
            "influenced",
            "inspired_by",
            "part_of",
            "reconstructed_from",
            "migration_performed",
        },
        "relation compatibility envelope must remain closed",
        errors,
    )
    _require(compatibility.get("migration_performed") is False, "relation compatibility must not claim migration", errors)
    _require(
        set(compatibility.get("same_movement", {})) == {"target_kind", "relation_predicate", "loss"}
        and compatibility["same_movement"].get("target_kind") == "classification_projection"
        and compatibility["same_movement"].get("relation_predicate") is None,
        "same_movement must project only to classification",
        errors,
    )
    _require(
        set(compatibility.get("similarity", {})) == {"target_kind", "relation_predicate", "creates_relation"}
        and compatibility["similarity"].get("creates_relation") is False
        and compatibility["similarity"].get("relation_predicate") is None,
        "Similarity must not create a Relation",
        errors,
    )
    for legacy in ("influenced", "inspired_by"):
        item = compatibility.get(legacy, {})
        _require(
            set(item) == {"target_kind", "relation_predicate", "required_before_acceptance"}
            and item.get("target_kind") == "unresolved_relation_candidate"
            and item.get("relation_predicate") is None,
            f"legacy {legacy} must remain unresolved",
            errors,
        )
        _require(set(item.get("required_before_acceptance", [])) == {"atomic Claim", "locator", "direction", "mechanism", "transmission mode", "scope"}, f"legacy {legacy} compatibility losses must be closed", errors)
    _require(
        compatibility.get("part_of")
        == {"target_kind": "structural_relation_outside_profile", "relation_predicate": None}
        and compatibility.get("reconstructed_from")
        == {"target_kind": "reconstruction_relation_outside_profile", "relation_predicate": None},
        "structural and reconstruction compatibility predicates must stay outside the profile",
        errors,
    )


def _validate_owner(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    owner = (root / OWNER_PATH).read_text(encoding="utf-8")
    statuses = re.findall(r"^- Status: `(REVIEW_REQUIRED|READY)`\.$", owner, flags=re.MULTILINE)
    _require(statuses == [package["status"]], "relation owner status must agree with package", errors)
    for term in (
        *PREDICATES,
        "same_movement",
        "Similarity",
        "five explicit negative regression classes",
        "not a total order",
    ):
        _require(term in owner or term in (root / WORK_PATH).read_text(encoding="utf-8"), f"relation owner/record missing {term}", errors)


def _validate_ready(root: Path, package: dict[str, Any], registry: dict[str, Any], require_ready: bool, errors: list[str]) -> None:
    _require(registry.get("status") == package["status"], "relation package/registry status drift", errors)
    if package["status"] != "READY":
        if require_ready:
            errors.append("relation package is not READY")
        return
    frozen = registry.get("frozen_commit")
    reviewed_digest = registry.get("reviewed_content_sha256")
    reviews = registry.get("reviews", [])
    _require(isinstance(frozen, str) and bool(re.fullmatch(r"[0-9a-f]{40}", frozen or "")), "READY registry requires frozen commit", errors)
    _require(isinstance(reviewed_digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", reviewed_digest or "")), "READY registry requires reviewed digest", errors)
    _require(len(reviews) == 2 and {item.get("track") for item in reviews} == {"semantic-model", "validator-integrity"}, "READY requires two distinct review tracks", errors)
    _require(len({item.get("reviewer_instance_id") for item in reviews}) == 2, "READY review instances must be distinct", errors)
    for review in reviews:
        _require(review.get("decision") == "READY" and review.get("independence_attestation") is True, f"review {review.get('review_id')} is not independently READY", errors)
        counts = review.get("finding_counts", {})
        _require(counts.get("critical") == 0 and counts.get("material") == 0, f"review {review.get('review_id')} has unresolved blocker", errors)
        _require(review.get("frozen_commit") == frozen and review.get("reviewed_content_sha256") == reviewed_digest, f"review {review.get('review_id')} frozen binding mismatch", errors)
        artifact = root / review.get("artifact", "")
        try:
            _require(artifact.is_file() and not artifact.is_symlink(), f"review artifact {artifact} must be a regular non-symlink file", errors)
            _require(hashlib.sha256(artifact.read_bytes()).hexdigest() == review.get("artifact_sha256"), f"review artifact {artifact} checksum mismatch", errors)
        except OSError as exc:
            errors.append(f"review artifact load failed: {exc}")
    if not frozen or not reviewed_digest:
        return
    try:
        head = _git_output(root, "rev-parse", "HEAD").decode().strip()
        _git_output(root, "merge-base", "--is-ancestor", frozen, head)
        _require(compute_review_digest(root) == reviewed_digest, "current normalized relation digest differs from reviewed digest", errors)
        for relative in REVIEW_SCOPE:
            _git_output(root, "cat-file", "-e", f"{frozen}:{relative}")
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"review gate: Git ancestry/tree validation failed: {exc}")


def validate_repository(root: Path, require_ready: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json(root / SCHEMA_PATH)
        package = load_json(root / PACKAGE_PATH)
        registry = load_json(root / REGISTRY_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"fixture JSON load failed: {exc}"]
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"schema {location}: {error.message}")
    if errors:
        return errors
    _validate_base_packages(root, package, errors)
    _validate_predicate_profile(package, errors)
    _validate_ui_language(package, errors)
    parents = _validate_extent_semantics(root, schema, package, errors)
    _validate_provenance(root, package, errors)
    _validate_cases(package, parents, errors)
    _validate_separation(root, package, errors)
    _validate_owner(root, package, errors)
    _validate_ready(root, package, registry, require_ready, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = validate_repository(args.root.resolve(), require_ready=args.require_ready)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    package = load_json(args.root.resolve() / PACKAGE_PATH)
    print(f"relation fixtures valid: {len(package['cases'])} predicate cases, {len(package['non_relation_cases'])} separate signals; status={package['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
