#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "project_state.json"
SCHEMA_PATH = ROOT / "docs" / "project_state.schema.json"


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
    payload = state or _load(STATE_PATH)
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
    if active & paused:
        raise ProjectStateError("an issue cannot be active and paused at the same time")
    if payload["active_vertical"]["issue"] not in active:
        raise ProjectStateError("active vertical issue must be present in active_issues")
    if 331 not in paused:
        raise ProjectStateError("relation issue #331 must remain paused before documented Relations")
    if gate["id"] == "C" and not {332, 360}.issubset(active):
        raise ProjectStateError("Gate C requires active delivery issues #332 and #360")
    if gate["status"] != "completed" and "decision" in gate:
        raise ProjectStateError("an unfinished gate cannot publish a decision")
    if payload["capability"]["globe"] != "non_public_r_and_d":
        raise ProjectStateError("the current Globe must remain non-public R&D")

    for relative in payload["canonical_refs"]:
        if not (ROOT / relative).is_file():
            raise ProjectStateError(f"canonical reference does not exist: {relative}")

    return {
        "gate": gate["id"],
        "gate_status": gate["status"],
        "active_issue_count": len(active),
        "blocker_count": len(payload["blockers"]),
    }


if __name__ == "__main__":
    print(json.dumps(validate_project_state(), sort_keys=True))
