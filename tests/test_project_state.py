import copy
import json

import pytest

from scripts.validate_project_state import ProjectStateError, STATE_PATH, validate_project_state


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_current_project_state_is_valid_and_single_gate() -> None:
    assert validate_project_state() == {
        "gate": "C",
        "gate_status": "in_progress",
        "active_issue_count": 3,
        "blocker_count": 3,
    }


def test_active_issue_cannot_also_be_paused() -> None:
    state = _state()
    state["github"]["paused_issues"].append(332)
    with pytest.raises(ProjectStateError, match="active and paused"):
        validate_project_state(state)


def test_gate_c_cannot_drop_delivery_issue() -> None:
    state = _state()
    state["github"]["active_issues"].remove(360)
    with pytest.raises(ProjectStateError, match="requires active delivery issues"):
        validate_project_state(state)


def test_unfinished_gate_cannot_claim_decision() -> None:
    state = _state()
    state["gate"]["decision"] = "FREEZE"
    with pytest.raises(ProjectStateError, match="unfinished gate"):
        validate_project_state(state)


def test_public_globe_promotion_is_rejected() -> None:
    state = copy.deepcopy(_state())
    state["capability"]["globe"] = "public"
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)
