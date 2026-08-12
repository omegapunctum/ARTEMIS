#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "world_model" / "refinement" / "v1"
PACKAGE_PATH = FIXTURE_DIR / "package.json"
SCHEMA_PATH = FIXTURE_DIR / "schema.json"
REVIEW_REQUEST_PATH = FIXTURE_DIR / "review_request.json"
REVIEW_REQUEST_SCHEMA_PATH = FIXTURE_DIR / "review_request.schema.json"
REVIEW_REGISTRY_PATH = FIXTURE_DIR / "review_registry.json"
REVIEW_REGISTRY_SCHEMA_PATH = FIXTURE_DIR / "review_registry.schema.json"
REVIEW_ARTIFACT_SCHEMA_PATH = FIXTURE_DIR / "review_artifact.schema.json"
ACCEPTANCE_DECISION_PATH = FIXTURE_DIR / "acceptance_decision.json"
ACCEPTANCE_DECISION_SCHEMA_PATH = FIXTURE_DIR / "acceptance_decision.schema.json"

EXPECTED_SERIES = {
    "series-leo-time",
    "series-leo-place",
    "series-leo-route",
    "series-range-1900",
    "series-range-2000",
    "series-stop-correction",
    "series-region-alternatives",
    "series-label-withdrawal",
}

EXPECTED_REVISIONS = {
    "revision-leo-time-coarse",
    "revision-leo-time-refined",
    "revision-leo-place-coarse",
    "revision-leo-place-refined",
    "revision-leo-route-unknown",
    "revision-range-1900-coarse",
    "revision-range-1900-refined",
    "revision-range-2000-state",
    "revision-stop-initial",
    "revision-stop-corrected",
    "revision-region-primary",
    "revision-region-alternative",
    "revision-label-initial",
    "revision-label-withdrawn",
}

EXPECTED_SOURCES = {"source-synthetic-travel-notebook", "source-synthetic-range-atlas"}
EXPECTED_CLAIMS = {f"claim-{value.removeprefix('revision-')}" for value in EXPECTED_REVISIONS}
EXPECTED_EVIDENCE_LINKS = {f"evidence-{value.removeprefix('revision-')}" for value in EXPECTED_REVISIONS}
EXPECTED_UNCERTAINTIES = {
    "uncertainty-leo-time-coarse",
    "uncertainty-leo-place-coarse",
    "uncertainty-leo-route-unknown",
    "uncertainty-range-1900-coarse",
    "uncertainty-region-alternatives",
}

PRECISION_FAMILIES = {
    "temporal": ["unknown", "century", "decade", "year", "month", "day"],
    "spatial": ["unknown", "region", "subregion", "locality", "point"],
    "route": ["route_unknown", "corridor", "documented_path"],
    "literal": ["categorical"],
}


class RefinementValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise RefinementValidationError(message)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")


def parse_utc(value: str, label: str) -> datetime:
    if not value.endswith("Z"):
        fail(f"{label} must use UTC Z notation")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        fail(f"{label} is not an ISO-8601 timestamp: {exc}")
    if parsed.tzinfo != timezone.utc:
        fail(f"{label} must be UTC")
    return parsed


def parse_day(value: str | None, label: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        fail(f"{label} must use YYYY-MM-DD: {exc}")


def index_unique(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item["id"]
        if item_id in result:
            fail(f"duplicate {label} id: {item_id}")
        result[item_id] = item
    return result


def validate_schema(package: dict[str, Any], schema: dict[str, Any]) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        fail(f"fixture schema is invalid: {exc.message}")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(package), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = ".".join(str(value) for value in first.absolute_path) or "<root>"
        fail(f"schema validation failed at {location}: {first.message}")


def validate_time_extent(extent: dict[str, Any], label: str) -> tuple[datetime | None, datetime | None]:
    if extent["calendar"] not in {"proleptic_gregorian", "source_native_unresolved"}:
        fail(f"{label}.calendar is unsupported")
    precision = extent["precision"]
    if precision not in PRECISION_FAMILIES["temporal"]:
        fail(f"{label}.precision must be temporal")
    start = parse_day(extent["start"], f"{label}.start")
    end = parse_day(extent["end"], f"{label}.end")
    if start is not None and end is not None and start > end:
        fail(f"{label} start must not follow end")
    kind = extent["kind"]
    expected_presence = {
        "instant": (True, True),
        "closed_interval": (True, True),
        "open_start_interval": (False, True),
        "open_end_interval": (True, False),
        "unknown": (False, False),
    }[kind]
    if (start is not None, end is not None) != expected_presence:
        fail(f"{label} bounds do not match kind {kind}")
    if kind == "instant" and start != end:
        fail(f"{label} instant bounds must be equal")
    if kind == "closed_interval" and start == end:
        fail(f"{label} closed interval must span more than one instant")
    for side, bound in (("start", start), ("end", end)):
        inclusive = extent[f"{side}_inclusive"]
        qualifier = extent[f"{side}_qualifier"]
        if bound is None and (inclusive is not None or qualifier != "unknown"):
            fail(f"{label}.{side} open bound must use inclusive=null and qualifier=unknown")
        if bound is not None and (not isinstance(inclusive, bool) or qualifier == "unknown"):
            fail(f"{label}.{side} finite bound requires inclusivity and a non-unknown qualifier")
    if start is not None and end is not None:
        lower = start.toordinal() + (0 if extent["start_inclusive"] else 1)
        upper = end.toordinal() - (0 if extent["end_inclusive"] else 1)
        if lower > upper:
            fail(f"{label} must represent a non-empty temporal possible set")
    if extent["certainty"] == "unknown" and kind != "unknown":
        fail(f"{label} unknown certainty requires unknown kind")
    if kind == "unknown" and extent["certainty"] != "unknown":
        fail(f"{label} unknown kind requires unknown certainty")
    if extent["normalization_state"] == "unresolved" and extent["calendar"] != "source_native_unresolved":
        fail(f"{label} unresolved normalization must retain source-native calendar state")
    if not extent["basis_claim_refs"]:
        fail(f"{label} requires at least one basis Claim")
    alternative_ids: set[str] = set()
    for index, alternative in enumerate(extent["alternatives"]):
        alternative_label = f"{label}.alternatives[{index}]"
        if alternative["id"] in alternative_ids:
            fail(f"{label} alternative ids must be unique")
        alternative_ids.add(alternative["id"])
        validate_time_extent({
            "calendar": extent["calendar"],
            "kind": alternative["kind"],
            "start": alternative["start"],
            "end": alternative["end"],
            "start_inclusive": alternative["start_inclusive"],
            "end_inclusive": alternative["end_inclusive"],
            "start_qualifier": alternative["start_qualifier"],
            "end_qualifier": alternative["end_qualifier"],
            "precision": alternative["precision"],
            "certainty": "unknown" if alternative["kind"] == "unknown" else "disputed",
            "normalization_state": extent["normalization_state"],
            "basis_claim_refs": alternative["basis_claim_refs"],
            "alternatives": [],
        }, alternative_label)
    return start, end


def precision_rank(value: str, dimension: str, label: str) -> int:
    family = PRECISION_FAMILIES[dimension]
    if value not in family:
        fail(f"{label} precision {value!r} is incompatible with {dimension}")
    return family.index(value)


def bbox(value: dict[str, Any], label: str) -> tuple[float, float, float, float]:
    values = value["bbox"]
    west, south, east, north = (float(item) for item in values)
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        fail(f"{label} bbox is invalid")
    return west, south, east, north


def strict_bbox_subset(child: tuple[float, float, float, float], parent: tuple[float, float, float, float]) -> bool:
    contained = child[0] >= parent[0] and child[1] >= parent[1] and child[2] <= parent[2] and child[3] <= parent[3]
    return contained and child != parent


def temporal_semantic_envelope(extent: dict[str, Any]) -> dict[str, Any]:
    """Return temporal meaning while excluding revision-local provenance links."""
    return {
        key: (
            [
                {item_key: item_value for item_key, item_value in alternative.items() if item_key != "basis_claim_refs"}
                for alternative in value
            ]
            if key == "alternatives"
            else value
        )
        for key, value in extent.items()
        if key != "basis_claim_refs"
    }


def temporal_members(extent: dict[str, Any]) -> list[dict[str, Any]]:
    primary = {
        key: value
        for key, value in extent.items()
        if key not in {"alternatives", "basis_claim_refs", "certainty", "normalization_state", "calendar"}
    }
    return [primary, *extent["alternatives"]]


def temporal_member_subset(child: dict[str, Any], parent: dict[str, Any]) -> bool:
    child_start = parse_day(child["start"], "temporal subset child.start")
    child_end = parse_day(child["end"], "temporal subset child.end")
    parent_start = parse_day(parent["start"], "temporal subset parent.start")
    parent_end = parse_day(parent["end"], "temporal subset parent.end")
    if parent_start is not None:
        if child_start is None or child_start < parent_start:
            return False
        if child_start == parent_start and child["start_inclusive"] and not parent["start_inclusive"]:
            return False
    if parent_end is not None:
        if child_end is None or child_end > parent_end:
            return False
        if child_end == parent_end and child["end_inclusive"] and not parent["end_inclusive"]:
            return False
    qualifier_narrowing = {
        "exact": {"exact"},
        "approximate": {"approximate", "exact"},
        "not_before": {"not_before", "exact"},
        "not_after": {"not_after", "exact"},
        "unknown": {"unknown"},
    }
    start_qualifier_subset = (
        parent_start is None
        or child["start_qualifier"] in qualifier_narrowing[parent["start_qualifier"]]
    )
    end_qualifier_subset = (
        parent_end is None
        or child["end_qualifier"] in qualifier_narrowing[parent["end_qualifier"]]
    )
    return start_qualifier_subset and end_qualifier_subset


def temporal_union_segments(members: list[dict[str, Any]]) -> list[tuple[int | None, int | None]]:
    segments: list[tuple[int | None, int | None]] = []
    for member in members:
        start = parse_day(member["start"], "temporal union start")
        end = parse_day(member["end"], "temporal union end")
        lower = None if start is None else start.toordinal() + (0 if member["start_inclusive"] else 1)
        upper = None if end is None else end.toordinal() - (0 if member["end_inclusive"] else 1)
        if lower is not None and upper is not None and lower > upper:
            continue
        segments.append((lower, upper))
    segments.sort(key=lambda item: (float("-inf") if item[0] is None else item[0], float("inf") if item[1] is None else item[1]))
    merged: list[tuple[int | None, int | None]] = []
    for lower, upper in segments:
        if not merged:
            merged.append((lower, upper))
            continue
        previous_lower, previous_upper = merged[-1]
        touches = previous_upper is None or lower is None or lower <= previous_upper + 1
        if not touches:
            merged.append((lower, upper))
            continue
        merged[-1] = (
            previous_lower,
            None if previous_upper is None or upper is None else max(previous_upper, upper),
        )
    return merged


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


PACKAGE_LOCK_COLLECTIONS = ("sources", "claims", "evidence_links", "uncertainties", "series", "revisions")


def package_semantic_payload(package: dict[str, Any]) -> dict[str, Any]:
    return {key: package[key] for key in PACKAGE_LOCK_COLLECTIONS}


def normalized_review_bytes(raw_path: str, content: bytes) -> bytes:
    if raw_path == "fixtures/world_model/refinement/v1/package.json":
        package = json.loads(content.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs)
        package["status"] = "REVIEW_REQUIRED"
        return json.dumps(package, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if raw_path == "docs/PROGRESSIVE_REFINEMENT_CONTRACT.md":
        text = content.decode("utf-8")
        approved_headers = {
            "version": {
                "- Version: 1.0-draft.",
                "- Version: 1.0.",
            },
            "status": {
                "- Status: `REVIEW_REQUIRED` under issue `#377`.",
                "- Status: `READY` under issue `#377`.",
            },
        }
        lines = text.splitlines(keepends=True)
        for label, prefix, replacement in (
            ("version", "- Version: ", "- Version: 1.0-review-candidate."),
            ("status", "- Status: ", "- Status: `REVIEW_REQUIRED` under issue `#377`."),
        ):
            matches = [index for index, line in enumerate(lines) if line.rstrip("\r\n").startswith(prefix)]
            if len(matches) != 1:
                fail(f"progressive refinement contract must contain exactly one {label} header")
            index = matches[0]
            raw_line = lines[index].rstrip("\r\n")
            if raw_line not in approved_headers[label]:
                fail(f"progressive refinement contract has an unauthorized {label} header")
            newline = lines[index][len(raw_line):]
            lines[index] = replacement + newline
        text = "".join(lines)
        return text.encode("utf-8")
    return content


def reviewed_content_sha256(
    request: dict[str, Any],
    content_loader: Any | None = None,
) -> str:
    digest = hashlib.sha256()
    scope = request.get("review_scope")
    if not isinstance(scope, list) or not scope or len(scope) != len(set(scope)):
        fail("review_request.review_scope must be a non-empty unique list")
    forbidden = {
        "fixtures/world_model/refinement/v1/review_request.json",
        "fixtures/world_model/refinement/v1/review_registry.json",
    }
    for raw_path in scope:
        if not isinstance(raw_path, str) or not raw_path or raw_path.startswith("/") or ".." in Path(raw_path).parts:
            fail("review scope contains an unsafe path")
        if raw_path in forbidden or raw_path.endswith("review_artifact.schema.json"):
            fail("review metadata cannot be part of the reviewed content digest")
        if content_loader is None:
            path = ROOT / raw_path
            if not path.is_file() or path.is_symlink():
                fail(f"review scope path is not a regular file: {raw_path}")
            content = path.read_bytes()
        else:
            content = content_loader(raw_path)
        digest.update(raw_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(normalized_review_bytes(raw_path, content))
        digest.update(b"\0")
    return digest.hexdigest()


def safe_metadata_path(raw_path: str, directory: Path, label: str) -> Path:
    path_value = Path(raw_path)
    if path_value.is_absolute() or ".." in path_value.parts:
        fail(f"{label} contains an unsafe path")
    path = ROOT / path_value
    directory_resolved = directory.resolve()
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(directory_resolved):
        fail(f"{label} is not a regular in-scope file: {raw_path}")
    return path


def require_regular_repo_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        fail(f"{label} must be a regular in-repository file")


def git_output(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=False
    )
    if result.returncode != 0:
        fail(f"git {' '.join(args)} failed")
    return result.stdout


def validate_clean_state(status_output: str, all_other_files: str) -> None:
    if status_output.strip() or all_other_files.strip():
        fail("READY validation requires a clean index/worktree with no untracked or ignored files")


def validate_index_visibility(index_entries: bytes) -> None:
    hidden_entries = [
        entry for entry in index_entries.split(b"\0")
        if entry and not entry.startswith(b"H ")
    ]
    if hidden_entries:
        fail("READY validation rejects assume-unchanged, skip-worktree or nonstandard index entries")


def validate_clean_checkout() -> None:
    validate_index_visibility(git_output("ls-files", "-v", "-z"))
    git_output("update-index", "--really-refresh")
    validate_clean_state(
        git_output("status", "--porcelain=v1", "--untracked-files=all").decode(),
        git_output("ls-files", "--others").decode(),
    )


def validate_git_blob_entry(raw_path: str, entry: str) -> None:
    parts = entry.strip().split(None, 3)
    if len(parts) != 4 or parts[0] != "100644" or parts[1] != "blob" or parts[3] != raw_path:
        fail(f"READY metadata path must be a committed regular 100644 blob: {raw_path}")


def require_head_regular_blob(raw_path: str) -> None:
    path = ROOT / raw_path
    require_regular_repo_file(path, raw_path)
    validate_git_blob_entry(raw_path, git_output("ls-tree", "HEAD", "--", raw_path).decode())


def validate_review_artifact(
    artifact: dict[str, Any],
    artifact_schema: dict[str, Any],
    label: str,
) -> None:
    validate_schema(artifact, artifact_schema)
    open_critical = sum(
        item["severity"] == "critical" and item["status"] == "open"
        for item in artifact["findings"]
    )
    open_material = sum(
        item["severity"] == "material" and item["status"] == "open"
        for item in artifact["findings"]
    )
    if artifact["open_critical"] != open_critical or artifact["open_material"] != open_material:
        fail(f"{label} finding counters do not match findings[]")
    finding_ids = [item["finding_id"] for item in artifact["findings"]]
    if len(finding_ids) != len(set(finding_ids)):
        fail(f"{label} finding_id values must be unique")
    if artifact["decision"] == "READY" and (open_critical or open_material):
        fail(f"{label} READY decision retains open critical/material findings")


def validate_review_entry(
    entry: dict[str, Any],
    artifact_schema: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    artifact_path = safe_metadata_path(
        entry["artifact_ref"], FIXTURE_DIR / "reviews", f"{label}.artifact_ref"
    )
    artifact_bytes = artifact_path.read_bytes()
    if hashlib.sha256(artifact_bytes).hexdigest() != entry["artifact_sha256"]:
        fail(f"{label} artifact digest drift")
    artifact = read_json(artifact_path)
    validate_review_artifact(artifact, artifact_schema, label)
    for field in (
        "review_round", "review_id", "reviewer_id", "reviewer_instance_id", "review_task_path",
        "track", "independence_method", "frozen_commit", "frozen_tree",
        "reviewed_content_sha256", "decision",
    ):
        if entry[field] != artifact[field]:
            fail(f"{label} registry/artifact mismatch for {field}")
    return artifact


def validate_acceptance_binding(
    decision: dict[str, Any],
    registry_status: str,
    frozen_commit: str | None,
    frozen_tree: str | None,
) -> None:
    if registry_status == "REVIEW_REQUIRED":
        if decision["status"] != "PENDING" or decision["decision"] is not None:
            fail("REVIEW_REQUIRED registry requires a pending acceptance decision")
        if decision["frozen_commit"] is not None or decision["frozen_tree"] is not None:
            fail("pending acceptance decision cannot claim a frozen revision")
        return
    if decision["status"] == "DECIDED":
        if decision["decision"] is None:
            fail("DECIDED acceptance artifact requires ACCEPT, NARROW or REJECT")
        if (decision["frozen_commit"], decision["frozen_tree"]) != (frozen_commit, frozen_tree):
            fail("acceptance decision does not bind the frozen revision")
    elif decision["decision"] is not None or decision["frozen_commit"] is not None or decision["frozen_tree"] is not None:
        fail("pending acceptance decision cannot claim a decision or frozen revision")


def validate_capability_prohibitions(decision: dict[str, Any]) -> None:
    prohibited = (
        "runtime_migration_authorized",
        "airtable_historical_write_authorized",
        "public_capability_change",
    )
    if any(decision.get(field) is not False for field in prohibited):
        fail("progressive refinement decision cannot authorize runtime, Airtable or public capability changes")


def validate_ready_descendant_paths(changed_paths: list[str], allowed_paths: set[str]) -> None:
    unauthorized = sorted(set(changed_paths) - allowed_paths)
    if unauthorized:
        fail(f"READY descendant contains non-metadata changes: {', '.join(unauthorized)}")


def validate_lifecycle_consistency(package_status: str, registry_status: str) -> None:
    contract = (ROOT / "docs" / "PROGRESSIVE_REFINEMENT_CONTRACT.md").read_text(encoding="utf-8")
    version_lines = [line for line in contract.splitlines() if line.startswith("- Version: ")]
    status_lines = [line for line in contract.splitlines() if line.startswith("- Status: ")]
    if len(version_lines) != 1 or len(status_lines) != 1:
        fail("progressive refinement contract lifecycle headers are ambiguous")
    ready = registry_status == "READY"
    expected_package = "READY" if ready else "REVIEW_REQUIRED"
    expected_version = "- Version: 1.0." if ready else "- Version: 1.0-draft."
    expected_status = (
        "- Status: `READY` under issue `#377`."
        if ready
        else "- Status: `REVIEW_REQUIRED` under issue `#377`."
    )
    if (
        package_status != expected_package
        or version_lines[0] != expected_version
        or status_lines[0] != expected_status
    ):
        fail("package, registry and contract lifecycle states are inconsistent")


def validate_review_envelope() -> dict[str, Any]:
    for path, label in (
        (REVIEW_REQUEST_PATH, "review request"),
        (REVIEW_REQUEST_SCHEMA_PATH, "review request schema"),
        (REVIEW_REGISTRY_PATH, "review registry"),
        (REVIEW_REGISTRY_SCHEMA_PATH, "review registry schema"),
        (REVIEW_ARTIFACT_SCHEMA_PATH, "review artifact schema"),
        (ACCEPTANCE_DECISION_PATH, "acceptance decision"),
        (ACCEPTANCE_DECISION_SCHEMA_PATH, "acceptance decision schema"),
    ):
        require_regular_repo_file(path, label)
    request = read_json(REVIEW_REQUEST_PATH)
    registry = read_json(REVIEW_REGISTRY_PATH)
    artifact_schema = read_json(REVIEW_ARTIFACT_SCHEMA_PATH)
    validate_schema(request, read_json(REVIEW_REQUEST_SCHEMA_PATH))
    validate_schema(registry, read_json(REVIEW_REGISTRY_SCHEMA_PATH))
    decision = read_json(ACCEPTANCE_DECISION_PATH)
    validate_schema(decision, read_json(ACCEPTANCE_DECISION_SCHEMA_PATH))
    validate_capability_prohibitions(decision)
    tracks = request["required_tracks"]

    digest = reviewed_content_sha256(request)
    if registry.get("reviewed_content_sha256") != digest:
        fail("review registry content digest does not match exact review scope")
    if registry.get("required_review_count") != 2 or registry.get("required_tracks") != tracks:
        fail("review registry must require exactly the two declared tracks")
    if registry.get("required_independence_method") != request["independence_method"]:
        fail("review registry independence method drift")
    if decision["reviewed_content_sha256"] != digest:
        fail("acceptance decision content digest drift")

    prior_artifacts = [
        validate_review_entry(entry, artifact_schema, f"prior_reviews[{index}]")
        for index, entry in enumerate(registry["prior_reviews"])
    ]
    if {artifact["track"] for artifact in prior_artifacts} != set(tracks):
        fail("prior review history must preserve both independent tracks")

    all_review_entries = [*registry["prior_reviews"], *registry["reviews"]]
    review_ids = [entry["review_id"] for entry in all_review_entries]
    if len(review_ids) != len(set(review_ids)):
        fail("review_id values must be unique across review history")

    status = registry.get("status")
    reviews = registry.get("reviews")
    if status == "REVIEW_REQUIRED":
        if registry.get("frozen_commit") is not None or registry.get("frozen_tree") is not None or reviews:
            fail("REVIEW_REQUIRED registry cannot claim a frozen review or completed reviews")
        validate_acceptance_binding(decision, status, None, None)
        return {
            "review_status": status,
            "reviewed_content_sha256": digest,
            "review_count": 0,
            "acceptance_decision": None,
        }
    if status not in {"REVIEWS_COMPLETE", "READY"}:
        fail("unsupported review registry status")
    frozen_commit = registry.get("frozen_commit")
    frozen_tree = registry.get("frozen_tree")
    if not isinstance(frozen_commit, str) or len(frozen_commit) != 40 or any(c not in "0123456789abcdef" for c in frozen_commit):
        fail("completed reviews require one exact frozen commit")
    if not isinstance(frozen_tree, str) or len(frozen_tree) != 40 or any(c not in "0123456789abcdef" for c in frozen_tree):
        fail("completed reviews require one exact frozen tree")
    if len(reviews) != 2:
        fail("completed review registry requires exactly two reviews")

    git_output("cat-file", "-e", f"{frozen_commit}^{{commit}}")
    actual_tree = git_output("show", "-s", "--format=%T", frozen_commit).decode().strip()
    if actual_tree != frozen_tree:
        fail("frozen tree does not match frozen commit")
    git_output("merge-base", "--is-ancestor", frozen_commit, "HEAD")

    def frozen_loader(raw_path: str) -> bytes:
        return git_output("show", f"{frozen_commit}:{raw_path}")

    request_ref = REVIEW_REQUEST_PATH.relative_to(ROOT).as_posix()
    if frozen_loader(request_ref) != REVIEW_REQUEST_PATH.read_bytes():
        fail("review request identity/scope does not match the frozen commit")
    for control_schema_path in (
        REVIEW_REQUEST_SCHEMA_PATH,
        REVIEW_REGISTRY_SCHEMA_PATH,
        REVIEW_ARTIFACT_SCHEMA_PATH,
        ACCEPTANCE_DECISION_SCHEMA_PATH,
    ):
        control_schema_ref = control_schema_path.relative_to(ROOT).as_posix()
        if frozen_loader(control_schema_ref) != control_schema_path.read_bytes():
            fail(f"review control schema does not match the frozen commit: {control_schema_ref}")
    registry_ref = REVIEW_REGISTRY_PATH.relative_to(ROOT).as_posix()
    frozen_registry = json.loads(
        frozen_loader(registry_ref).decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs
    )
    if registry["prior_reviews"] != frozen_registry.get("prior_reviews"):
        fail("prior review audit history does not match the frozen commit")
    if reviewed_content_sha256(request, frozen_loader) != digest:
        fail("frozen commit does not contain the reviewed content digest")

    allowed_descendant_paths = {
        PACKAGE_PATH.relative_to(ROOT).as_posix(),
        (ROOT / "docs" / "PROGRESSIVE_REFINEMENT_CONTRACT.md").relative_to(ROOT).as_posix(),
        REVIEW_REGISTRY_PATH.relative_to(ROOT).as_posix(),
        ACCEPTANCE_DECISION_PATH.relative_to(ROOT).as_posix(),
        *(review["artifact_ref"] for review in reviews),
    }
    changed_paths = git_output("diff", "--name-only", f"{frozen_commit}..HEAD").decode().splitlines()
    validate_ready_descendant_paths(changed_paths, allowed_descendant_paths)
    validate_clean_checkout()
    for raw_path in sorted(allowed_descendant_paths):
        require_head_regular_blob(raw_path)

    seen_tracks: set[str] = set()
    reviewer_ids: set[str] = set()
    reviewer_instances: set[str] = set()
    slots = {slot["track"]: slot for slot in request["review_slots"]}
    if set(slots) != set(tracks) or len({slot["reviewer_instance_id"] for slot in slots.values()}) != 2:
        fail("review request must pre-issue two distinct track slots")
    for index, review in enumerate(reviews):
        artifact = validate_review_entry(review, artifact_schema, f"reviews[{index}]")
        if artifact["review_round"] != request["review_round"]:
            fail("current review artifact uses the wrong review round")
        if artifact["frozen_commit"] != frozen_commit or artifact["frozen_tree"] != frozen_tree or artifact["reviewed_content_sha256"] != digest:
            fail("both reviews must bind the same frozen commit and reviewed content digest")
        slot = slots.get(artifact["track"])
        if slot is None or any(artifact[field] != slot[field] for field in ("reviewer_id", "reviewer_instance_id", "review_task_path", "track")):
            fail("review artifact does not match its pre-issued independent review slot")
        seen_tracks.add(artifact["track"])
        reviewer_ids.add(artifact["reviewer_id"])
        reviewer_instances.add(artifact["reviewer_instance_id"])
    if seen_tracks != set(tracks) or len(reviewer_ids) != 2 or len(reviewer_instances) != 2:
        fail("reviews must use distinct reviewers/instances and cover both required tracks")
    if status == "READY" and any(review["decision"] != "READY" for review in reviews):
        fail("READY registry requires two READY decisions")
    validate_acceptance_binding(decision, status, frozen_commit, frozen_tree)
    if status == "READY":
        if decision["status"] != "DECIDED" or decision["decision"] != "ACCEPT":
            fail("READY registry requires an explicit ACCEPT decision")
    elif decision["status"] == "DECIDED" and decision["decision"] == "ACCEPT":
        fail("ACCEPT decision requires READY registry status")
    return {
        "review_status": status,
        "reviewed_content_sha256": digest,
        "review_count": 2,
        "acceptance_decision": decision["decision"],
    }


def calculate_frontier(
    revisions: list[dict[str, Any]],
    series_ids: set[str],
    through: datetime | None = None,
) -> dict[str, list[str]]:
    frontier: dict[str, set[str]] = {series_id: set() for series_id in series_ids}
    seen: dict[str, dict[str, Any]] = {}
    ordered = sorted(revisions, key=lambda item: (parse_utc(item["recorded_at"], f"{item['id']}.recorded_at"), item["id"]))
    for revision in ordered:
        recorded_at = parse_utc(revision["recorded_at"], f"{revision['id']}.recorded_at")
        if through is not None and recorded_at > through:
            continue
        revision_id = revision["id"]
        series_ref = revision["series_ref"]
        predecessors = revision["predecessor_refs"]
        for predecessor_id in predecessors:
            predecessor = seen.get(predecessor_id)
            if predecessor is None:
                fail(f"{revision_id} has orphan or future predecessor {predecessor_id}")
            if predecessor["series_ref"] != series_ref:
                fail(f"{revision_id} has cross-series predecessor {predecessor_id}")
            if predecessor_id not in frontier[series_ref]:
                fail(f"{revision_id} predecessor {predecessor_id} is not on the active frontier")

        operation = revision["operation"]
        if operation == "initial":
            if predecessors:
                fail(f"{revision_id} initial revision cannot name predecessors")
            if frontier[series_ref]:
                fail(f"{revision_id} cannot add a second initial frontier")
            frontier[series_ref].add(revision_id)
        elif operation in {"refine", "correct"}:
            if len(predecessors) != 1:
                fail(f"{revision_id} {operation} requires exactly one predecessor")
            frontier[series_ref].difference_update(predecessors)
            frontier[series_ref].add(revision_id)
        elif operation == "add_alternative":
            if len(predecessors) != 1:
                fail(f"{revision_id} add_alternative requires exactly one active predecessor")
            frontier[series_ref].add(revision_id)
        elif operation == "withdraw":
            if len(predecessors) != 1:
                fail(f"{revision_id} withdraw requires exactly one predecessor")
            frontier[series_ref].difference_update(predecessors)
        else:  # pragma: no cover - schema already closes this set
            fail(f"unsupported operation: {operation}")
        seen[revision_id] = revision
    return {series_id: sorted(values) for series_id, values in sorted(frontier.items())}


def validate_revision_semantics(
    revisions: dict[str, dict[str, Any]],
    series: dict[str, dict[str, Any]],
    created_at: datetime,
) -> None:
    for revision in revisions.values():
        revision_id = revision["id"]
        series_item = series.get(revision["series_ref"])
        if series_item is None:
            fail(f"{revision_id} references unknown series {revision['series_ref']}")
        recorded_at = parse_utc(revision["recorded_at"], f"{revision_id}.recorded_at")
        if recorded_at < created_at:
            fail(f"{revision_id}.recorded_at predates package creation")

        operation = revision["operation"]
        assertion = revision["normalized_assertion"]
        if operation == "withdraw":
            if assertion is not None:
                fail(f"{revision_id} withdraw must have normalized_assertion=null")
            continue
        if assertion is None:
            fail(f"{revision_id} {operation} requires a normalized assertion")

        dimension = series_item["dimension"]
        source_precision = revision["source_value"]["precision"]
        normalized_precision = assertion["precision"]
        source_rank = precision_rank(source_precision, dimension, f"{revision_id}.source_value")
        normalized_rank = precision_rank(normalized_precision, dimension, f"{revision_id}.normalized_assertion")
        if normalized_rank > source_rank:
            fail(f"{revision_id} normalized precision is finer than source-native precision")

        validate_time_extent(assertion["valid_time"], f"{revision_id}.valid_time")
        if dimension == "temporal" and normalized_precision != assertion["valid_time"]["precision"]:
            fail(f"{revision_id} temporal precision representations must agree")
        if dimension == "temporal":
            for alternative in assertion["valid_time"]["alternatives"]:
                alternative_rank = precision_rank(
                    alternative["precision"], dimension, f"{revision_id}.valid_time alternative"
                )
                if alternative_rank > source_rank or alternative_rank > normalized_rank:
                    fail(f"{revision_id} temporal alternative precision exceeds source/top-level support")
        value = assertion["value"]
        expected_kind = {
            "temporal": "temporal_extent",
            "spatial": "bbox",
            "route": "route",
            "literal": "literal",
        }[dimension]
        if value["kind"] != expected_kind:
            fail(f"{revision_id} value kind {value['kind']} is incompatible with {dimension}")
        if value["kind"] == "bbox":
            bbox(value, f"{revision_id}.value")
        elif value["kind"] == "temporal_extent":
            value_start = parse_day(value["start"], f"{revision_id}.value.start")
            value_end = parse_day(value["end"], f"{revision_id}.value.end")
            valid_start, valid_end = validate_time_extent(assertion["valid_time"], f"{revision_id}.valid_time")
            if (value_start, value_end) != (valid_start, valid_end):
                fail(f"{revision_id} temporal value must equal its valid_time bounds")
        elif value["kind"] == "route":
            mode = value["mode"]
            geometry = value["geometry"]
            if mode == "unknown_route" and geometry is not None:
                fail(f"{revision_id} unknown_route must have geometry=null")
            if mode != "unknown_route" and geometry is None:
                fail(f"{revision_id} {mode} requires explicit geometry")

        predecessor_assertion = None
        if operation in {"refine", "correct", "add_alternative"}:
            predecessor = revisions[revision["predecessor_refs"][0]]
            predecessor_assertion = predecessor["normalized_assertion"]
            if predecessor_assertion is None:
                fail(f"{revision_id} cannot follow a withdrawn/null predecessor")
            if (
                dimension != "temporal"
                and temporal_semantic_envelope(assertion["valid_time"])
                != temporal_semantic_envelope(predecessor_assertion["valid_time"])
            ):
                fail(f"{revision_id} {dimension} {operation} cannot change the valid_time envelope")

        if operation != "refine":
            continue
        assert predecessor_assertion is not None
        old_start, old_end = validate_time_extent(predecessor_assertion["valid_time"], f"{predecessor['id']}.valid_time")
        new_start, new_end = validate_time_extent(assertion["valid_time"], f"{revision_id}.valid_time")
        if dimension == "temporal":
            if (
                assertion["valid_time"]["calendar"],
                assertion["valid_time"]["normalization_state"],
            ) != (
                predecessor_assertion["valid_time"]["calendar"],
                predecessor_assertion["valid_time"]["normalization_state"],
            ):
                fail(f"{revision_id} temporal refinement must keep the predecessor calendar profile")
            parent_members = temporal_members(predecessor_assertion["valid_time"])
            child_members = temporal_members(assertion["valid_time"])
            for child_member in child_members:
                if not any(temporal_member_subset(child_member, parent_member) for parent_member in parent_members):
                    fail(f"{revision_id} temporal possible set is not contained by its predecessor")
            union_is_equal = temporal_union_segments(parent_members) == temporal_union_segments(child_members)
            old_rank = precision_rank(
                predecessor_assertion["precision"], dimension, f"{predecessor['id']}.normalized_assertion"
            )
            precision_only_refinement = (
                len(parent_members) == len(child_members) == 1
                and union_is_equal
                and normalized_rank > old_rank
            )
            if union_is_equal and not precision_only_refinement:
                fail(f"{revision_id} false refine: temporal possible set is not strictly narrower")
        elif dimension == "spatial":
            child = bbox(assertion["value"], f"{revision_id}.value")
            parent = bbox(predecessor_assertion["value"], f"{predecessor['id']}.value")
            if not strict_bbox_subset(child, parent):
                fail(f"{revision_id} false refine: spatial possible set is not strictly narrower")
        else:
            fail(f"{revision_id} refine is unsupported for {dimension}; use correct or add_alternative")
        old_rank = precision_rank(predecessor_assertion["precision"], dimension, f"{predecessor['id']}.normalized_assertion")
        if normalized_rank < old_rank:
            fail(f"{revision_id} refinement cannot reduce declared precision")


def validate_package(package_path: Path = PACKAGE_PATH, schema_path: Path = SCHEMA_PATH) -> dict[str, Any]:
    package = read_json(package_path)
    schema = read_json(schema_path)
    validate_schema(package, schema)

    sources = index_unique(package["sources"], "Source")
    claims = index_unique(package["claims"], "Claim")
    evidence_links = index_unique(package["evidence_links"], "EvidenceLink")
    uncertainties = index_unique(package["uncertainties"], "Uncertainty")
    series = index_unique(package["series"], "series")
    revisions = index_unique(package["revisions"], "revision")

    all_ids: list[str] = []
    for collection in (sources, claims, evidence_links, uncertainties, series, revisions):
        all_ids.extend(collection)
    if len(all_ids) != len(set(all_ids)):
        fail("ids must be globally unique across the refinement package")

    if set(series) != EXPECTED_SERIES:
        fail("fixture series coverage does not match the closed v1 scenario set")
    if set(revisions) != EXPECTED_REVISIONS:
        fail("fixture revision coverage does not match the closed v1 scenario set")
    if set(sources) != EXPECTED_SOURCES:
        fail("fixture Source coverage does not match the closed v1 scenario set")
    if set(claims) != EXPECTED_CLAIMS:
        fail("fixture Claim coverage does not match the closed v1 scenario set")
    if set(evidence_links) != EXPECTED_EVIDENCE_LINKS:
        fail("fixture EvidenceLink coverage does not match the closed v1 scenario set")
    if set(uncertainties) != EXPECTED_UNCERTAINTIES:
        fail("fixture Uncertainty coverage does not match the closed v1 scenario set")

    target_series: dict[tuple[str, str], str] = {}
    dimension_suffixes = {
        "temporal": (".temporal",),
        "spatial": (".spatial", ".geometry"),
        "route": (".geometry",),
        "literal": (".label", ".provisional"),
    }
    for series_item in series.values():
        atomic_target = (series_item["subject_ref"], series_item["target_key"])
        if atomic_target in target_series:
            fail(f"atomic target has more than one revision series: {atomic_target}")
        target_series[atomic_target] = series_item["id"]
        if not series_item["target_key"].endswith(dimension_suffixes[series_item["dimension"]]):
            fail(f"{series_item['id']} target_key is inconsistent with its dimension")
        if series_item["dimension"] == "route" and not series_item["target_key"].startswith("route-"):
            fail(f"{series_item['id']} route target_key must identify a route target")

    lock = package["ledger_lock"]
    revision_order = [item["id"] for item in package["revisions"]]
    if lock["revision_ids"] != revision_order:
        fail("ledger_lock.revision_ids must exactly preserve revision order")
    actual_digest = canonical_sha256(package["revisions"])
    if lock["revisions_sha256"] != actual_digest:
        fail("ledger_lock revisions_sha256 does not match immutable revision payload")

    package_lock = package["package_lock"]
    expected_collection_ids = {
        key: [item["id"] for item in package[key]] for key in PACKAGE_LOCK_COLLECTIONS
    }
    if package_lock["collection_ids"] != expected_collection_ids:
        fail("package_lock collection_ids must preserve every semantic collection and order")
    semantic_digest = canonical_sha256(package_semantic_payload(package))
    if package_lock["semantic_sha256"] != semantic_digest:
        fail("package_lock semantic_sha256 does not match the complete semantic payload")

    created_at = parse_utc(package["created_at"], "created_at")
    computed = calculate_frontier(package["revisions"], set(series))
    validate_revision_semantics(revisions, series, created_at)

    claim_by_revision: dict[str, dict[str, Any]] = {}
    for claim in claims.values():
        revision_ref = claim["revision_ref"]
        if revision_ref not in revisions:
            fail(f"{claim['id']} references unknown revision {revision_ref}")
        if revision_ref in claim_by_revision:
            fail(f"revision {revision_ref} has more than one atomic Claim")
        claim_by_revision[revision_ref] = claim
        for evidence_ref in claim["evidence_link_refs"]:
            evidence = evidence_links.get(evidence_ref)
            if evidence is None or evidence["claim_ref"] != claim["id"]:
                fail(f"{claim['id']} has invalid EvidenceLink {evidence_ref}")
        for uncertainty_ref in claim["uncertainty_refs"]:
            if uncertainty_ref not in uncertainties:
                fail(f"{claim['id']} references unknown Uncertainty {uncertainty_ref}")
        reviewed_supports = [
            evidence_links[ref]
            for ref in claim["evidence_link_refs"]
            if evidence_links[ref]["review_state"] == "reviewed" and evidence_links[ref]["relation_to_claim"] == "supports"
        ]
        if claim["evidence_state"] == "supported" and not reviewed_supports:
            fail(f"{claim['id']} supported state requires reviewed supporting evidence")

    if set(claim_by_revision) != set(revisions):
        fail("every revision must have exactly one atomic Claim")

    for revision in revisions.values():
        assertion = revision["normalized_assertion"]
        if assertion is None:
            continue
        valid_time = assertion["valid_time"]
        if revision["claim_ref"] not in valid_time["basis_claim_refs"]:
            fail(f"{revision['id']} valid_time must bind its atomic Claim")
        for basis_ref in valid_time["basis_claim_refs"]:
            if basis_ref not in claims:
                fail(f"{revision['id']} valid_time has unknown basis Claim")
        for alternative in valid_time["alternatives"]:
            if any(basis_ref not in claims for basis_ref in alternative["basis_claim_refs"]):
                fail(f"{revision['id']} temporal alternative has unknown basis Claim")

    for evidence in evidence_links.values():
        if evidence["claim_ref"] not in claims:
            fail(f"{evidence['id']} references unknown Claim")
        if evidence["source_ref"] not in sources:
            fail(f"{evidence['id']} references unknown Source")
        if evidence["id"] not in claims[evidence["claim_ref"]]["evidence_link_refs"]:
            fail(f"{evidence['id']} is detached from its Claim")

    source_texts: dict[str, str] = {}
    for source in sources.values():
        artifact_ref = source["artifact_ref"]
        if artifact_ref.startswith("/") or ".." in Path(artifact_ref).parts:
            fail(f"{source['id']} has unsafe source artifact path")
        artifact_path = ROOT / artifact_ref
        expected_parent = (FIXTURE_DIR / "sources").resolve()
        if not artifact_path.is_file() or artifact_path.is_symlink() or not artifact_path.resolve().is_relative_to(expected_parent):
            fail(f"{source['id']} source artifact is not a regular in-scope file")
        content = artifact_path.read_bytes()
        if hashlib.sha256(content).hexdigest() != source["artifact_sha256"]:
            fail(f"{source['id']} source artifact digest drift")
        source_texts[source["id"]] = content.decode("utf-8")

    for evidence in evidence_links.values():
        claim_item = claims[evidence["claim_ref"]]
        revision = revisions[claim_item["revision_ref"]]
        base_marker = (
            f"## {evidence['locator']}\n\n"
            f"raw: `{revision['source_value']['raw']}`\n\n"
            f"claim: {claim_item['statement']}\n"
        )
        source_text = source_texts[evidence["source_ref"]]
        if source_text.count(f"## {evidence['locator']}\n") != 1 or base_marker not in source_text:
            fail(f"{evidence['id']} locator does not reproduce its source-native value and Claim")
        reviewed_support = (
            evidence["review_state"] == "reviewed"
            and evidence["relation_to_claim"] == "supports"
        )
        full_marker = (
            f"{base_marker}\n"
            f"source_value_sha256: `{canonical_sha256(revision['source_value'])}`\n\n"
            f"normalized_assertion_sha256: `{canonical_sha256(revision['normalized_assertion'])}`\n"
        )
        if reviewed_support and full_marker not in source_text:
            fail(f"{evidence['id']} locator does not bind the exact source value and normalized assertion")

    for uncertainty in uncertainties.values():
        if uncertainty["revision_ref"] not in revisions:
            fail(f"{uncertainty['id']} references unknown revision")
        uncertainty_revision = revisions[uncertainty["revision_ref"]]
        uncertainty_claim = claims[uncertainty_revision["claim_ref"]]
        if uncertainty["id"] not in uncertainty_revision["uncertainty_refs"] or uncertainty["id"] not in uncertainty_claim["uncertainty_refs"]:
            fail(f"{uncertainty['id']} is detached from its revision/Claim")

    for revision in revisions.values():
        claim = claims.get(revision["claim_ref"])
        if claim is None or claim["revision_ref"] != revision["id"]:
            fail(f"{revision['id']} claim_ref is not bidirectionally closed")
        if sorted(revision["evidence_link_refs"]) != sorted(claim["evidence_link_refs"]):
            fail(f"{revision['id']} and its Claim must have identical EvidenceLink refs")
        if sorted(revision["uncertainty_refs"]) != sorted(claim["uncertainty_refs"]):
            fail(f"{revision['id']} and its Claim must have identical Uncertainty refs")
        for uncertainty_ref in revision["uncertainty_refs"]:
            uncertainty = uncertainties[uncertainty_ref]
            if uncertainty["revision_ref"] != revision["id"]:
                fail(f"{revision['id']} has non-local Uncertainty {uncertainty_ref}")

    expected = {key: sorted(value) for key, value in sorted(package["expected_current_frontier"].items())}
    if set(expected) != set(series) or computed != expected:
        fail("expected_current_frontier does not match deterministic ledger replay")
    alternatives = computed["series-region-alternatives"]
    if alternatives != ["revision-region-alternative", "revision-region-primary"]:
        fail("competing reconstruction frontier must preserve both alternatives without a winner")

    checkpoint_times: list[datetime] = []
    for index, checkpoint in enumerate(package["replay_checkpoints"]):
        through = parse_utc(checkpoint["recorded_through"], f"replay_checkpoints[{index}].recorded_through")
        checkpoint_times.append(through)
        replay = calculate_frontier(package["revisions"], set(series), through=through)
        checkpoint_expected = {key: sorted(value) for key, value in sorted(checkpoint["expected_frontier"].items())}
        if set(checkpoint_expected) != set(series) or replay != checkpoint_expected:
            fail(f"replay checkpoint {checkpoint['recorded_through']} does not match ledger history")
    if checkpoint_times != sorted(set(checkpoint_times)):
        fail("replay checkpoints must be strictly increasing")
    if package["replay_checkpoints"][-1]["expected_frontier"] != package["expected_current_frontier"]:
        fail("last replay checkpoint must equal expected_current_frontier")

    # Closed scenario assertions that prevent semantically plausible fixture drift.
    if revisions["revision-leo-route-unknown"]["normalized_assertion"]["value"] != {
        "kind": "route", "mode": "unknown_route", "geometry": None
    }:
        fail("Leonardo-like route scenario must remain unknown and geometry-null")
    range_1900 = series["series-range-1900"]
    range_2000 = series["series-range-2000"]
    if range_1900["subject_ref"] != range_2000["subject_ref"] or range_1900["target_key"] == range_2000["target_key"]:
        fail("ecological range states must share subject but use distinct valid-time targets")
    if revisions["revision-range-2000-state"]["predecessor_refs"]:
        fail("later ecological world state must not refine the 1900 knowledge series")
    if revisions["revision-stop-corrected"]["operation"] != "correct":
        fail("contradicting stop scenario must remain a correction")
    if revisions["revision-label-withdrawn"]["normalized_assertion"] is not None:
        fail("withdrawal scenario must not remain in the current value frontier")

    review = validate_review_envelope()
    validate_lifecycle_consistency(package["status"], review["review_status"])
    return {
        "status": package["status"],
        "series": len(series),
        "revisions": len(revisions),
        "claims": len(claims),
        "evidence_links": len(evidence_links),
        "uncertainties": len(uncertainties),
        "ledger_sha256": actual_digest,
        "semantic_sha256": semantic_digest,
        **review,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ARTEMIS progressive refinement fixtures")
    parser.add_argument("--package", type=Path, default=PACKAGE_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    try:
        if args.require_ready and (args.package.resolve() != PACKAGE_PATH.resolve() or args.schema.resolve() != SCHEMA_PATH.resolve()):
            fail("--require-ready is restricted to the canonical reviewed package and schema")
        summary = validate_package(args.package, args.schema)
        if args.require_ready and (
            summary["status"] != "READY"
            or summary["review_status"] != "READY"
            or summary["acceptance_decision"] != "ACCEPT"
        ):
            fail("package, independent reviews and ACCEPT decision are not READY")
    except RefinementValidationError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
