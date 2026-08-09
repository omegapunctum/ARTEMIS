#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "project_state.json"
SCHEMA_PATH = ROOT / "docs" / "project_state.schema.json"
GATE_C_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1"
REVIEW_REGISTRY_SCHEMA_PATH = GATE_C_ROOT / "review_registry.schema.json"
GATE_C_DECISION_SCHEMA_PATH = GATE_C_ROOT / "gate_c_decision.schema.json"


class ProjectStateError(ValueError):
    pass


def _load(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectStateError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProjectStateError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def validate_project_state(state: dict | None = None) -> dict:
    payload = _load(STATE_PATH) if state is None else state
    schema = _load(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ProjectStateError(f"project state schema validation failed: {details}")

    gate = payload["gate"]
    active = set(payload["github"]["active_issues"])
    paused = set(payload["github"]["paused_issues"])
    completed = set(payload["github"]["completed_issues"])
    if active & paused or active & completed or paused & completed:
        raise ProjectStateError("an issue cannot be active and paused or completed at the same time")
    if payload["active_vertical"]["issue"] not in active:
        raise ProjectStateError("active vertical issue must be present in active_issues")
    if 331 not in paused:
        raise ProjectStateError("relation issue #331 must remain paused before documented Relations")
    if gate["id"] == "C" and gate["status"] != "completed" and not {332, 360}.issubset(active):
        raise ProjectStateError("Gate C requires active delivery issues #332 and #360")
    if gate["status"] != "completed" and ({"decision", "evidence"} & set(gate)):
        raise ProjectStateError("an unfinished gate cannot publish a decision or completion evidence")
    if payload["capability"]["globe"] != "non_public_r_and_d":
        raise ProjectStateError("the current Globe must remain non-public R&D")

    if gate["status"] == "completed":
        if gate["id"] != "C":
            raise ProjectStateError("this transition validator currently closes only Gate C")
        if not {332, 360}.issubset(completed) or {332, 360} & active:
            raise ProjectStateError("completed Gate C must move delivery issues #332 and #360 to completed_issues")
        if payload["capability"]["world_slice"] != "gate_c_frozen_non_public":
            raise ProjectStateError("completed Gate C must publish the frozen non-public capability")
        if payload["next_transition"]["gate"] not in {"D", "STOP"}:
            raise ProjectStateError("completed Gate C must advance to Gate D or STOP")
        _validate_gate_c_evidence(payload)

    for relative in payload["canonical_refs"]:
        if not (ROOT / relative).is_file():
            raise ProjectStateError(f"canonical reference does not exist: {relative}")

    return {
        "gate": gate["id"],
        "gate_status": gate["status"],
        "active_issue_count": len(active),
        "blocker_count": len(payload["blockers"]),
    }


def _validate_gate_c_evidence(payload: dict) -> None:
    gate = payload["gate"]
    evidence = gate["evidence"]
    review_registry = _load(ROOT / evidence["review_registry_ref"])
    gate_decision = _load(ROOT / evidence["gate_decision_ref"])
    cost = _load(ROOT / evidence["review_cost_ref"])
    _validate_against_schema(review_registry, REVIEW_REGISTRY_SCHEMA_PATH, "review registry")
    _validate_against_schema(gate_decision, GATE_C_DECISION_SCHEMA_PATH, "Gate C decision")

    frozen_identity = (evidence["frozen_commit"], evidence["frozen_tree"])
    if (review_registry.get("frozen_commit"), review_registry.get("frozen_tree")) != frozen_identity:
        raise ProjectStateError("review registry must bind the completed gate's frozen revision")
    reviews = review_registry.get("reviews") or []
    if len(reviews) != 2:
        raise ProjectStateError("completed Gate C requires exactly two independent reviews")
    identities = {row.get("reviewer_instance_id") for row in reviews}
    tracks = {row.get("track") for row in reviews}
    if len(identities) != 2 or tracks != {"semantic-content", "validator-integrity"}:
        raise ProjectStateError("Gate C reviews must be independent and cover both required tracks")
    for unique_field in ("review_id", "cost_activity_ref", "artifact_ref"):
        if len({row.get(unique_field) for row in reviews}) != 2:
            raise ProjectStateError(f"Gate C reviews require distinct {unique_field} values")
    for review in reviews:
        if (review.get("frozen_commit"), review.get("frozen_tree")) != frozen_identity:
            raise ProjectStateError("every Gate C review must inspect the same frozen revision")
        if review.get("decision") != "READY":
            raise ProjectStateError("completed Gate C requires READY review decisions")
        if review.get("unresolved_critical") != 0 or review.get("unresolved_material") != 0:
            raise ProjectStateError("completed Gate C cannot retain critical or material findings")
        artifact = ROOT / str(review.get("artifact_ref") or "")
        if not artifact.is_file():
            raise ProjectStateError(f"review artifact does not exist: {review.get('artifact_ref')}")

    if (gate_decision.get("frozen_commit"), gate_decision.get("frozen_tree")) != frozen_identity:
        raise ProjectStateError("Gate C decision must bind the reviewed frozen revision")
    if gate_decision.get("decision") != gate["decision"]:
        raise ProjectStateError("project state and Gate C decision disagree")
    expected_scope_outcome = {
        "FREEZE": "frozen",
        "NARROW": "narrowed",
        "REJECT": "rejected",
    }[gate["decision"]]
    if gate_decision.get("scope_outcome") != expected_scope_outcome:
        raise ProjectStateError("Gate C decision and scope outcome disagree")
    if gate_decision.get("unresolved_critical") != 0 or gate_decision.get("unresolved_material") != 0:
        raise ProjectStateError("Gate C decision cannot retain critical or material findings")

    review_durations = {
        row["activity_id"]: row["duration_minutes"]
        for row in cost.get("entries", [])
        if row.get("actor_kind") == "independent_reviewer"
        and row.get("measurement_state") == "recorded"
    }
    expected_cost_ids = {row.get("cost_activity_ref") for row in reviews}
    if None in expected_cost_ids or not expected_cost_ids.issubset(review_durations):
        raise ProjectStateError("each independent review must bind a recorded cost entry")
    for review in reviews:
        if review_durations[review["cost_activity_ref"]] != review.get("duration_minutes"):
            raise ProjectStateError("review duration must match its recorded cost entry")


def _validate_against_schema(payload: dict, schema_path: Path, label: str) -> None:
    errors = sorted(
        Draft202012Validator(
            _load(schema_path), format_checker=FormatChecker()
        ).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ProjectStateError(f"{label} schema validation failed: {details}")


if __name__ == "__main__":
    print(json.dumps(validate_project_state(), sort_keys=True))
