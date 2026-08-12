#!/usr/bin/env python3
"""Validate the frozen semantic row plan for #371 before any live historical write.

This command is offline/read-only. It recomputes the candidate row plan from the frozen Gate C
package and fails if its canonical digest, counts, source binding or write authorization differs
from row_plan_lock.json.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_airtable_leonardo_shadow_plan.py"
LOCK = ROOT / "fixtures" / "airtable_curation" / "v2" / "row_plan_lock.json"
MAPPING = ROOT / "fixtures" / "airtable_curation" / "v2" / "mapping_contract.json"
PROJECT_STATE = ROOT / "docs" / "project_state.json"


class RowPlanLockError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RowPlanLockError(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RowPlanLockError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    _require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def _load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("artemis_airtable_leonardo_plan", BUILDER)
    _require(spec is not None and spec.loader is not None, "cannot load row-plan builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate() -> dict[str, Any]:
    builder = _load_builder()
    lock = _load_json(LOCK)
    mapping = _load_json(MAPPING)
    project_state = _load_json(PROJECT_STATE)

    _require(lock.get("schema_version") == "1.0.0", "unexpected row-plan lock version")
    _require(lock.get("status") == "ROW_PLAN_FROZEN", "row-plan lock must remain frozen")
    _require(lock.get("authoritative") is False, "row-plan lock cannot become knowledge authority")
    _require(lock.get("issue") == 371, "row-plan lock issue drift")
    _require(mapping.get("row_plan_lock") == "fixtures/airtable_curation/v2/row_plan_lock.json", "mapping must bind the row-plan lock")

    gate = project_state.get("gate", {})
    next_transition = project_state.get("next_transition", {})
    _require(gate.get("id") == "C" and gate.get("status") == "completed" and gate.get("decision") == "FREEZE", "Gate C boundary drift")
    _require(next_transition.get("gate") == "D", "Gate D must remain only the next transition")

    plan = builder.build_plan()
    digest = builder._digest(plan)
    locked_plan = lock.get("row_plan", {})
    _require(digest == locked_plan.get("sha256"), f"row-plan digest drift: {digest}")
    _require(sum(plan["counts"].values()) == locked_plan.get("total_rows"), "locked total row count drift")
    _require(plan["counts"] == locked_plan.get("counts"), "locked per-table counts drift")

    source = plan.get("source", {})
    frozen = lock.get("frozen_gate_c", {})
    _require(source.get("frozen_commit") == frozen.get("commit"), "frozen Gate C commit drift")
    _require(source.get("frozen_tree") == frozen.get("tree"), "frozen Gate C tree drift")
    _require(source.get("reviewed_content_digest") == frozen.get("reviewed_content_digest"), "frozen Gate C digest drift")

    expected = mapping.get("expected_counts", {})
    _require(expected.get("world_slices") == plan["counts"]["WorldSlices"], "WorldSlices count contract drift")
    _require(expected.get("slice_layers") == plan["counts"]["SliceLayers"], "SliceLayers count contract drift")
    _require(expected.get("world_sources") == plan["counts"]["WorldSources"], "WorldSources count contract drift")
    _require(expected.get("knowledge_objects") == plan["counts"]["KnowledgeObjects"], "KnowledgeObjects count contract drift")
    _require(expected.get("object_parts") == plan["counts"]["ObjectParts"], "ObjectParts count contract drift")
    _require(expected.get("claims") == plan["counts"]["Claims"], "Claims count contract drift")
    _require(expected.get("evidence_links") == plan["counts"]["EvidenceLinks"], "EvidenceLinks count contract drift")
    _require(expected.get("uncertainties") == plan["counts"]["Uncertainties"], "Uncertainties count contract drift")
    _require(expected.get("uncertainty_targets") == plan["counts"]["UncertaintyTargets"], "UncertaintyTargets count contract drift")

    authorization = lock.get("write_authorization", {})
    _require(authorization.get("historical_rows_authorized") is False, "historical rows must remain unauthorized at lock stage")
    _require(authorization.get("independent_mapping_review_required") is True, "independent mapping review must remain required")
    _require(authorization.get("round_trip_parity_required_after_write") is True, "round-trip parity requirement missing")
    _require(authorization.get("gate_d_opened") is False, "row-plan lock must not open Gate D")

    isolation = lock.get("legacy_isolation", {})
    _require(isolation.get("KnowledgeObjects.layers") == "must_remain_empty", "legacy Layers isolation drift")
    _require(isolation.get("EvidenceLinks.source") == "must_remain_empty", "legacy Sources isolation drift")
    for row in plan["rows"]["KnowledgeObjects"]:
        _require(row["fields"]["layers"] == [], f"{row['stable_id']}: legacy layers must remain empty")
    for row in plan["rows"]["EvidenceLinks"]:
        _require(row["fields"]["source"] == [], f"{row['stable_id']}: legacy source must remain empty")

    return {
        "sha256": digest,
        "total_rows": sum(plan["counts"].values()),
        "counts": plan["counts"],
        "historical_rows_authorized": False,
    }


def main() -> int:
    try:
        result = validate()
    except RowPlanLockError as exc:
        print(f"Leonardo Airtable row-plan lock: FAIL — {exc}", file=sys.stderr)
        return 1
    print(
        "Leonardo Airtable row-plan lock: PASS — "
        f"{result['total_rows']} rows; sha256={result['sha256']}; historical rows remain unauthorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
