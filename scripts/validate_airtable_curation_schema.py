#!/usr/bin/env python3
"""Validate the checked-in ARTEMIS Airtable shadow curation schema evidence.

The validator is intentionally offline and deterministic. It validates:

- the executable shadow schema contract against the accepted #366 working plan;
- the checked-in live Airtable metadata snapshot against that contract;
- table/field identity, types, controlled vocabularies and link targets;
- the pre-Gate-D lifecycle boundary from ``docs/project_state.json``;
- zero-record status when ``--require-empty`` is requested.

The snapshot records metadata evidence only. It is not a historical corpus and does
not make Airtable the canonical World Model authority.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "fixtures" / "airtable_curation" / "v1" / "schema_contract.json"
SNAPSHOT_PATH = ROOT / "fixtures" / "airtable_curation" / "v1" / "live_schema_snapshot.json"
PLAN_PATH = ROOT / "docs" / "work" / "airtable" / "2026-08-10_AIRTABLE_CURATION_SCHEMA_PLAN_v1.json"
PROJECT_STATE_PATH = ROOT / "docs" / "project_state.json"

TABLE_ID_RE = re.compile(r"^tbl[A-Za-z0-9]{14}$")
FIELD_ID_RE = re.compile(r"^fld[A-Za-z0-9]{14}$")
EXPECTED_TABLE_ORDER = [
    "WorldSlices",
    "KnowledgeObjects",
    "ObjectParts",
    "Claims",
    "EvidenceLinks",
    "Uncertainties",
]
EXPECTED_REUSED_TABLES = {"Sources", "Layers", "Media"}


class SchemaError(RuntimeError):
    """Raised when the shadow curation schema evidence is inconsistent."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SchemaError(f"missing required schema evidence: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SchemaError(f"expected JSON object in {path.relative_to(ROOT)}")
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _field_map(table: dict[str, Any], *, owner: str) -> dict[str, dict[str, Any]]:
    fields = table.get("fields")
    _require(isinstance(fields, list), f"{owner}.{table.get('name')}: fields must be a list")
    result: dict[str, dict[str, Any]] = {}
    for field in fields:
        _require(isinstance(field, dict), f"{owner}.{table.get('name')}: field must be an object")
        name = field.get("name")
        _require(isinstance(name, str) and name, f"{owner}.{table.get('name')}: field name missing")
        _require(name not in result, f"{owner}.{table.get('name')}: duplicate field {name}")
        result[name] = field
    return result


def _normalize_field_for_plan(field: dict[str, Any]) -> dict[str, Any]:
    keep = {"name", "type", "choices", "linked_table", "cardinality", "precision"}
    return {key: field[key] for key in keep if key in field}


def _validate_contract_against_plan(contract: dict[str, Any], plan: dict[str, Any]) -> None:
    _require(plan.get("status") == "proposal_only", "accepted Airtable plan must remain proposal_only")
    _require(plan.get("issue") == 366, "accepted Airtable plan must remain bound to #366")
    _require(contract.get("source_plan") == str(PLAN_PATH.relative_to(ROOT)), "contract source_plan drift")

    plan_tables = plan.get("proposed_tables")
    contract_tables = contract.get("tables")
    _require(isinstance(plan_tables, list) and isinstance(contract_tables, list), "plan/contract tables missing")
    _require([item.get("name") for item in plan_tables] == EXPECTED_TABLE_ORDER, "working plan table order drift")
    _require([item.get("name") for item in contract_tables] == EXPECTED_TABLE_ORDER, "contract table order drift")

    plan_by_name = {item["name"]: item for item in plan_tables}
    contract_by_name = {item["name"]: item for item in contract_tables}
    for table_name in EXPECTED_TABLE_ORDER:
        plan_fields = _field_map(plan_by_name[table_name], owner="plan")
        contract_fields = _field_map(contract_by_name[table_name], owner="contract")
        _require(set(plan_fields) == set(contract_fields), f"{table_name}: contract field names drift from accepted plan")
        for field_name, contract_field in contract_fields.items():
            plan_field = plan_fields[field_name]
            for key, value in _normalize_field_for_plan(contract_field).items():
                if key == "name":
                    continue
                if key in plan_field:
                    _require(plan_field[key] == value, f"{table_name}.{field_name}: {key} drift from accepted plan")


def _validate_gate_boundary(contract: dict[str, Any], project_state: dict[str, Any]) -> None:
    gate = project_state.get("gate", {})
    next_transition = project_state.get("next_transition", {})
    github = project_state.get("github", {})
    capability = project_state.get("capability", {})
    completed_gates = project_state.get("completed_gates", [])
    gate_c = next((item for item in completed_gates if item.get("id") == "C"), {})

    _require(gate_c.get("status") == "completed", "Gate C history must remain completed")
    _require(gate_c.get("decision") == "FREEZE", "Gate C history must retain FREEZE")
    _require(gate.get("id") == "D", "current project gate must be D")
    _require(gate.get("status") in {"in_progress", "blocked"}, "Gate D lifecycle drift")
    _require(next_transition.get("gate") == "D", "Gate E must remain unopened")
    _require(331 in github.get("deferred_issues", []), "Relation issue #331 must remain deferred")
    _require(capability.get("globe") == "non_public_r_and_d", "Globe must remain non-public R&D")

    boundary = contract.get("gate_boundary", {})
    _require(boundary.get("current_gate") == "C", "contract current_gate must be C")
    _require(boundary.get("current_status") == "completed", "contract Gate C status drift")
    _require(boundary.get("current_decision") == "FREEZE", "contract Gate C decision drift")
    _require(boundary.get("next_gate") == "D", "contract next_gate drift")
    _require(boundary.get("next_gate_opened") is False, "shadow schema contour must not be the action that opened Gate D")
    _require(boundary.get("paused_relation_issue") == 331, "contract must preserve the #331 Relation gate")


def _validate_snapshot(contract: dict[str, Any], snapshot: dict[str, Any], *, require_empty: bool) -> dict[str, int]:
    _require(contract.get("schema_version") == "1.0.0", "unexpected curation schema version")
    _require(contract.get("status") == "SHADOW_SCHEMA_V1", "unexpected curation schema status")
    _require(contract.get("authoritative") is False, "Airtable shadow schema cannot be authoritative")
    _require(snapshot.get("snapshot_version") == "1.0.0", "unexpected live snapshot version")
    _require(snapshot.get("authoritative") is False, "live Airtable snapshot cannot be authoritative")

    reused_contract = contract.get("reused_tables")
    reused_snapshot = snapshot.get("reused_table_ids")
    _require(isinstance(reused_contract, dict), "contract reused_tables missing")
    _require(isinstance(reused_snapshot, dict), "snapshot reused_table_ids missing")
    _require(set(reused_contract) == EXPECTED_REUSED_TABLES, "contract reused table set drift")
    _require(reused_snapshot == reused_contract, "snapshot reused table IDs drift from contract")
    for name, table_id in reused_snapshot.items():
        _require(bool(TABLE_ID_RE.fullmatch(str(table_id))), f"invalid reused table id for {name}: {table_id}")

    contract_tables = contract.get("tables")
    snapshot_tables = snapshot.get("tables")
    _require(isinstance(contract_tables, list) and isinstance(snapshot_tables, list), "contract/snapshot tables missing")
    _require([table.get("name") for table in contract_tables] == EXPECTED_TABLE_ORDER, "contract table order drift")
    _require([table.get("name") for table in snapshot_tables] == EXPECTED_TABLE_ORDER, "snapshot table order drift")

    contract_by_name = {table["name"]: table for table in contract_tables}
    snapshot_by_name = {table["name"]: table for table in snapshot_tables}
    table_ids = dict(reused_snapshot)
    for name, table in snapshot_by_name.items():
        table_id = table.get("id")
        _require(isinstance(table_id, str) and bool(TABLE_ID_RE.fullmatch(table_id)), f"{name}: invalid table id")
        _require(table_id not in table_ids.values(), f"{name}: duplicate table id {table_id}")
        table_ids[name] = table_id

    total_fields = 0
    total_records = 0
    seen_field_ids: set[str] = set()

    for table_name in EXPECTED_TABLE_ORDER:
        expected = contract_by_name[table_name]
        actual = snapshot_by_name[table_name]
        expected_fields = _field_map(expected, owner="contract")
        actual_fields = _field_map(actual, owner="snapshot")
        _require(set(expected_fields) == set(actual_fields), f"{table_name}: snapshot field set drift")

        record_count = actual.get("record_count")
        _require(isinstance(record_count, int) and record_count >= 0, f"{table_name}: invalid record_count")
        total_records += record_count
        if require_empty:
            _require(record_count == 0, f"{table_name}: shadow table must remain empty before import")

        for field_name, expected_field in expected_fields.items():
            actual_field = actual_fields[field_name]
            field_id = actual_field.get("id")
            _require(isinstance(field_id, str) and bool(FIELD_ID_RE.fullmatch(field_id)), f"{table_name}.{field_name}: invalid field id")
            _require(field_id not in seen_field_ids, f"duplicate field id in snapshot: {field_id}")
            seen_field_ids.add(field_id)
            total_fields += 1

            _require(actual_field.get("type") == expected_field.get("type"), f"{table_name}.{field_name}: type drift")

            if "choices" in expected_field:
                _require(actual_field.get("choices") == expected_field["choices"], f"{table_name}.{field_name}: select choices drift")
            if "precision" in expected_field:
                _require(actual_field.get("precision") == expected_field["precision"], f"{table_name}.{field_name}: precision drift")
            if "time_zone" in expected_field:
                _require(actual_field.get("time_zone") == expected_field["time_zone"], f"{table_name}.{field_name}: timezone drift")
            linked_table = expected_field.get("linked_table")
            if linked_table is not None:
                _require(linked_table in table_ids, f"{table_name}.{field_name}: unknown linked table {linked_table}")
                _require(
                    actual_field.get("linked_table_id") == table_ids[linked_table],
                    f"{table_name}.{field_name}: link target drift",
                )

    if require_empty:
        _require(snapshot.get("record_counts_verified_zero") is True, "snapshot must record zero-count verification")
        _require(contract.get("rules", {}).get("record_count_required") == 0, "contract must require empty shadow tables")
        _require(total_records == 0, "shadow schema contains records before import gate")

    rules = contract.get("rules", {})
    _require(rules.get("real_gate_c_import_allowed") is False, "contract must prohibit Gate C import")
    _require(rules.get("public_export_authority") is False, "shadow schema cannot own public export")
    _require(rules.get("legacy_architecture_atlas_authority_changed") is False, "legacy export authority must remain unchanged")

    return {"tables": len(snapshot_tables), "fields": total_fields, "records": total_records}


def validate(*, require_empty: bool = False) -> dict[str, int]:
    contract = _load_json(CONTRACT_PATH)
    snapshot = _load_json(SNAPSHOT_PATH)
    plan = _load_json(PLAN_PATH)
    project_state = _load_json(PROJECT_STATE_PATH)

    _validate_contract_against_plan(contract, plan)
    _validate_gate_boundary(contract, project_state)
    return _validate_snapshot(contract, snapshot, require_empty=require_empty)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ARTEMIS Airtable shadow curation schema evidence")
    parser.add_argument(
        "--require-empty",
        action="store_true",
        help="Fail unless all six shadow curation tables are recorded as empty.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate(require_empty=args.require_empty)
    except SchemaError as exc:
        print(f"Airtable curation schema: FAIL — {exc}", file=sys.stderr)
        return 1

    print(
        "Airtable curation schema: PASS — "
        f"{summary['tables']} shadow tables, {summary['fields']} declared fields, {summary['records']} records"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
