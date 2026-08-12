#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
    precision = extent["precision"]
    if precision not in PRECISION_FAMILIES["temporal"]:
        fail(f"{label}.precision must be temporal")
    start = parse_day(extent["start"], f"{label}.start")
    end = parse_day(extent["end"], f"{label}.end")
    if (start is None) != (end is None):
        fail(f"{label} must have both bounds or neither")
    if start is not None and end is not None and start > end:
        fail(f"{label} start must not follow end")
    if extent["certainty"] == "unknown" and (start is not None or end is not None):
        fail(f"{label} unknown certainty cannot carry bounds")
    if extent["certainty"] != "unknown" and (start is None or end is None):
        fail(f"{label} non-unknown certainty requires bounds")
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


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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

        if operation != "refine":
            continue
        predecessor = revisions[revision["predecessor_refs"][0]]
        predecessor_assertion = predecessor["normalized_assertion"]
        if predecessor_assertion is None:
            fail(f"{revision_id} cannot refine a withdrawn/null predecessor")
        old_start, old_end = validate_time_extent(predecessor_assertion["valid_time"], f"{predecessor['id']}.valid_time")
        new_start, new_end = validate_time_extent(assertion["valid_time"], f"{revision_id}.valid_time")
        if dimension == "temporal":
            if None in {old_start, old_end, new_start, new_end}:
                fail(f"{revision_id} temporal refine requires finite bounds")
            assert old_start is not None and old_end is not None and new_start is not None and new_end is not None
            if not (new_start >= old_start and new_end <= old_end and (new_start, new_end) != (old_start, old_end)):
                fail(f"{revision_id} false refine: temporal possible set is not strictly narrower")
        elif dimension == "spatial":
            if (new_start, new_end) != (old_start, old_end):
                fail(f"{revision_id} spatial refinement cannot change valid_time")
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

    lock = package["ledger_lock"]
    revision_order = [item["id"] for item in package["revisions"]]
    if lock["revision_ids"] != revision_order:
        fail("ledger_lock.revision_ids must exactly preserve revision order")
    actual_digest = canonical_sha256(package["revisions"])
    if lock["revisions_sha256"] != actual_digest:
        fail("ledger_lock revisions_sha256 does not match immutable revision payload")

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

    for evidence in evidence_links.values():
        if evidence["claim_ref"] not in claims:
            fail(f"{evidence['id']} references unknown Claim")
        if evidence["source_ref"] not in sources:
            fail(f"{evidence['id']} references unknown Source")

    for uncertainty in uncertainties.values():
        if uncertainty["revision_ref"] not in revisions:
            fail(f"{uncertainty['id']} references unknown revision")

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

    return {
        "status": package["status"],
        "series": len(series),
        "revisions": len(revisions),
        "claims": len(claims),
        "evidence_links": len(evidence_links),
        "uncertainties": len(uncertainties),
        "ledger_sha256": actual_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ARTEMIS progressive refinement fixtures")
    parser.add_argument("--package", type=Path, default=PACKAGE_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    try:
        summary = validate_package(args.package, args.schema)
        if args.require_ready and summary["status"] != "READY":
            fail("package is not READY")
    except RefinementValidationError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
