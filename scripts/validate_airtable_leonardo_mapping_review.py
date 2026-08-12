#!/usr/bin/env python3
"""Validate the independent mapping-review lifecycle for #371.

At the pre-write stage REVIEW_REQUIRED is a valid state and historical writes remain forbidden.
A later controlled-write revision may require `--require-ready`, which only passes when one
separate read-only agent review is bound to the exact frozen row-plan digest and reports no open
critical/material findings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "fixtures" / "airtable_curation" / "v2" / "review_registry.json"
ARTIFACT_SCHEMA = ROOT / "fixtures" / "airtable_curation" / "v2" / "review_artifact.schema.json"
ROW_PLAN_LOCK = ROOT / "fixtures" / "airtable_curation" / "v2" / "row_plan_lock.json"
REVIEWS_DIR = ROOT / "fixtures" / "airtable_curation" / "v2" / "reviews"


class MappingReviewError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MappingReviewError(message)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise MappingReviewError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    _require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def _artifact_path(ref: str) -> Path:
    _require(ref.startswith("fixtures/airtable_curation/v2/reviews/"), "review artifact must live under v2/reviews")
    path = (ROOT / ref).resolve()
    _require(REVIEWS_DIR.resolve() in path.parents, "review artifact path escapes reviews directory")
    return path


def validate(*, require_ready: bool = False) -> dict[str, Any]:
    registry = _load(REGISTRY)
    lock = _load(ROW_PLAN_LOCK)
    schema = _load(ARTIFACT_SCHEMA)

    _require(registry.get("schema_version") == "1.0.0", "unexpected review registry version")
    _require(registry.get("issue") == 371, "review registry issue drift")
    _require(registry.get("row_plan_sha256") == lock.get("row_plan", {}).get("sha256"), "review registry row-plan digest drift")
    _require(registry.get("row_plan_lock_ref") == "fixtures/airtable_curation/v2/row_plan_lock.json", "row-plan lock ref drift")
    _require(registry.get("required_review_count") == 1, "exactly one independent mapping review is required")
    _require(registry.get("required_track") == "mapping-integrity", "required review track drift")
    _require(registry.get("required_independence_method") == "separate_agent_task_read_only", "independence method drift")

    write_gate = registry.get("write_gate", {})
    _require(write_gate.get("ready_required_before_historical_write") is True, "READY must remain required before historical write")
    _require(write_gate.get("historical_rows_authorized") is False, "this pre-write registry must not authorize historical rows")
    _require(write_gate.get("gate_d_opened") is False, "mapping review must not open Gate D")

    reviews = registry.get("reviews")
    _require(isinstance(reviews, list), "reviews must be a list")
    _require(len(reviews) <= registry["required_review_count"], "too many mapping reviews registered")

    if not reviews:
        _require(registry.get("status") == "REVIEW_REQUIRED", "empty registry must be REVIEW_REQUIRED")
        if require_ready:
            raise MappingReviewError("independent mapping review is still required")
        return {
            "status": "REVIEW_REQUIRED",
            "reviews": 0,
            "row_plan_sha256": registry["row_plan_sha256"],
            "historical_rows_authorized": False,
        }

    _require(len(reviews) == registry["required_review_count"], "incomplete review registry")
    review = reviews[0]
    _require(isinstance(review, dict), "review registry entry must be an object")
    for key in ("review_id", "reviewer_id", "reviewer_instance_id", "artifact_ref"):
        _require(isinstance(review.get(key), str) and review.get(key), f"review registry missing {key}")
    _require(review.get("track") == registry["required_track"], "review track drift")
    _require(review.get("independence_method") == registry["required_independence_method"], "review independence drift")
    _require(review.get("reviewed_row_plan_sha256") == registry["row_plan_sha256"], "reviewed digest drift")

    artifact = _load(_artifact_path(review["artifact_ref"]))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(artifact),
        key=lambda err: list(err.path),
    )
    _require(not errors, "invalid mapping review artifact: " + "; ".join(error.message for error in errors[:5]))

    for key in ("review_id", "reviewer_id", "reviewer_instance_id", "track", "independence_method", "reviewed_row_plan_sha256"):
        _require(artifact.get(key) == review.get(key), f"review artifact/registry mismatch: {key}")

    open_critical = sum(1 for finding in artifact["findings"] if finding["severity"] == "critical" and finding["status"] == "open")
    open_material = sum(1 for finding in artifact["findings"] if finding["severity"] == "material" and finding["status"] == "open")
    ready = artifact.get("decision") == "READY" and open_critical == 0 and open_material == 0

    if ready:
        _require(registry.get("status") == "READY", "READY artifact requires READY registry status")
    else:
        _require(registry.get("status") == "CHANGES_REQUIRED", "non-READY artifact requires CHANGES_REQUIRED registry status")

    if require_ready and not ready:
        raise MappingReviewError("mapping review is not READY")

    return {
        "status": registry["status"],
        "reviews": 1,
        "row_plan_sha256": registry["row_plan_sha256"],
        "open_critical": open_critical,
        "open_material": open_material,
        "historical_rows_authorized": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Leonardo Airtable mapping review lifecycle")
    parser.add_argument("--require-ready", action="store_true", help="Fail unless independent mapping review is READY")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = validate(require_ready=args.require_ready)
    except MappingReviewError as exc:
        print(f"Leonardo Airtable mapping review: FAIL — {exc}", file=sys.stderr)
        return 1
    print(
        "Leonardo Airtable mapping review: "
        f"{result['status']} — reviews={result['reviews']} row_plan_sha256={result['row_plan_sha256']} "
        "historical rows remain unauthorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
