#!/usr/bin/env python3
"""Validate the additive ARTEMIS #330 uncertainty-semantics fixture package."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
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

SEMANTIC_SCOPE = (
    Path("docs/UNCERTAINTY_SEMANTICS_CONTRACT.md"),
    README_PATH,
    SCHEMA_PATH,
    PACKAGE_PATH,
    COMPATIBILITY_PATH,
    Path("scripts/validate_uncertainty_fixtures.py"),
    Path("tests/test_uncertainty_fixtures.py"),
)

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
    if geometry_type not in {"Point", "LineString", "Polygon"} or coordinates is None:
        errors.append(f"{context}: unsupported or incomplete GeoJSON geometry")
        return

    def visit(value: Any) -> None:
        if isinstance(value, list) and len(value) == 2 and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
        ):
            longitude, latitude = value
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                errors.append(f"{context}: coordinate outside EPSG:4326")
        elif isinstance(value, list):
            for item in value:
                visit(item)
        else:
            errors.append(f"{context}: malformed coordinate array")

    visit(coordinates)


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_compatibility(root: Path, compatibility: dict[str, Any], errors: list[str]) -> None:
    base = root / BASE_COMPATIBILITY_PATH
    if not base.is_file():
        errors.append("base compatibility projection is missing")
        return
    expected = compatibility["base_projection"]["sha256"]
    actual = _sha256(base)
    if not SHA_RE.fullmatch(expected) or actual != expected:
        errors.append("base compatibility projection checksum mismatch")
    if compatibility["invented_fields"] != []:
        errors.append("compatibility projection must not invent fields")
    temporal = compatibility["temporal_projection"]
    if temporal["projection_policy"] != "show_possible":
        errors.append("legacy temporal projection must remain possible, not exact")
    if temporal["lower"]["precision"] != "year" or temporal["upper"]["precision"] != "year":
        errors.append("legacy year fields must preserve year precision")
    spatial = compatibility["spatial_projection"]
    if spatial["target_precision"] != "unknown_precision":
        errors.append("legacy coordinate confidence must not become target exactness")
    if not compatibility["losses_and_unknowns"]:
        errors.append("compatibility losses must be explicit")


def _normalized_scope_bytes(path: Path, value: bytes) -> bytes:
    if path == PACKAGE_PATH:
        package = json.loads(value.decode("utf-8"), object_pairs_hook=_strict_object)
        package["status"] = "REVIEW_REQUIRED"
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


def compute_review_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SEMANTIC_SCOPE:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(relative.as_posix())
        content = _normalized_scope_bytes(relative, path.read_bytes())
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _validate_ready(
    root: Path,
    package: dict[str, Any],
    registry: dict[str, Any],
    errors: list[str],
) -> None:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    if package["status"] != registry.get("status"):
        errors.append("package and review registry status disagree")
    readme_status = re.findall(r"^Status: `(REVIEW_REQUIRED|READY)`$", readme, flags=re.MULTILINE)
    if readme_status != [package["status"]]:
        errors.append("README must contain one status synchronized with package")
    if package["status"] != "READY":
        errors.append("uncertainty package is not READY")
        return
    frozen_commit = registry.get("frozen_commit")
    reviewed_digest = registry.get("reviewed_digest")
    if not isinstance(frozen_commit, str) or not COMMIT_RE.fullmatch(frozen_commit):
        errors.append("READY registry requires a full frozen_commit SHA")
    if not isinstance(reviewed_digest, str) or not SHA_RE.fullmatch(reviewed_digest):
        errors.append("READY registry requires a reviewed_digest")
    else:
        try:
            actual_digest = compute_review_digest(root)
        except FileNotFoundError as exc:
            errors.append(f"review scope file missing: {exc}")
        else:
            if actual_digest != reviewed_digest:
                errors.append("READY reviewed_digest does not match semantic scope")
    reviews = registry.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != 2:
        errors.append("READY registry requires exactly two reviews")
        return
    tracks = {review.get("track") for review in reviews if isinstance(review, dict)}
    if tracks != {"semantic-model", "validator-integrity"}:
        errors.append("READY reviews must use distinct semantic-model and validator-integrity tracks")
    for review in reviews:
        if not isinstance(review, dict):
            errors.append("review entry must be an object")
            continue
        if review.get("decision") != "READY":
            errors.append("every READY review must have decision READY")
        counts = review.get("finding_counts")
        if not isinstance(counts, dict) or any(
            not isinstance(counts.get(key), int) or isinstance(counts.get(key), bool)
            for key in ("critical", "material", "minor")
        ):
            errors.append("review finding_counts must be strict integers")
        elif counts["critical"] or counts["material"]:
            errors.append("READY review cannot contain critical or material findings")
        artifact = review.get("artifact")
        checksum = review.get("artifact_sha256")
        if not isinstance(artifact, str) or not isinstance(checksum, str) or not SHA_RE.fullmatch(checksum):
            errors.append("review artifact path/checksum is invalid")
            continue
        artifact_path = root / artifact
        if not artifact_path.is_file() or _sha256(artifact_path) != checksum:
            errors.append(f"review artifact missing or checksum mismatch: {artifact}")


def validate_repository(root: Path, require_ready: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json(root / SCHEMA_PATH)
        package = load_json(root / PACKAGE_PATH)
        registry = load_json(root / REGISTRY_PATH)
        compatibility = load_json(root / COMPATIBILITY_PATH)
        base_package = load_json(root / BASE_PACKAGE_PATH)
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
    _validate_temporal(package, errors)
    _validate_spatial(package, errors)
    _validate_compatibility(root, compatibility, errors)

    owner = (root / "docs/UNCERTAINTY_SEMANTICS_CONTRACT.md").read_text(encoding="utf-8")
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

    if require_ready:
        _validate_ready(root, package, registry, errors)
    else:
        readme = (root / README_PATH).read_text(encoding="utf-8")
        statuses = re.findall(r"^Status: `(REVIEW_REQUIRED|READY)`$", readme, flags=re.MULTILINE)
        if statuses != [package["status"]] or registry.get("status") != package["status"]:
            errors.append("package, registry and README status must agree")
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
