import copy
import json
from datetime import datetime, timezone

import pytest

from scripts.validate_project_state import (
    ProjectStateError,
    STATE_PATH,
    _frozen_commit_time,
    _reviewed_content_digest,
    _validate_completed_gate_transition,
    _validate_frozen_git_revision,
    _validate_review_chronology,
    validate_project_state,
)


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _in_progress_state() -> dict:
    state = _state()
    state["gate"]["status"] = "in_progress"
    state["gate"].pop("decision", None)
    state["gate"].pop("evidence", None)
    state["github"]["active_issues"] = [332, 360, 355]
    state["github"]["completed_issues"] = [
        issue for issue in state["github"]["completed_issues"] if issue not in {332, 360}
    ]
    state["capability"]["world_slice"] = "scope_curation"
    state["blockers"] = ["Gate C review evidence is not complete"]
    state["next_transition"] = {"gate": "C", "condition": "Complete Gate C review."}
    return state


def _completed_state_without_evidence() -> dict:
    state = _in_progress_state()
    state["gate"]["status"] = "completed"
    state["gate"]["decision"] = "FREEZE"
    state["github"]["active_issues"] = [355]
    state["github"]["completed_issues"].extend([332, 360])
    state["capability"]["world_slice"] = "gate_c_frozen_non_public"
    state["blockers"] = []
    state["next_transition"] = {"gate": "D", "condition": "Begin Gate D."}
    return state


def test_current_project_state_is_valid_and_single_gate() -> None:
    state = _state()
    assert validate_project_state() == {
        "gate": "C",
        "gate_status": state["gate"]["status"],
        "active_issue_count": len(state["github"]["active_issues"]),
        "blocker_count": len(state["blockers"]),
    }


def test_active_issue_cannot_also_be_paused() -> None:
    state = _state()
    state["github"]["paused_issues"].append(332)
    with pytest.raises(ProjectStateError, match="active and paused"):
        validate_project_state(state)


def test_gate_c_cannot_drop_delivery_issue() -> None:
    state = _in_progress_state()
    state["github"]["active_issues"].remove(360)
    with pytest.raises(ProjectStateError, match="requires active delivery issues"):
        validate_project_state(state)


def test_unfinished_gate_cannot_claim_decision() -> None:
    state = _in_progress_state()
    state["gate"]["decision"] = "FREEZE"
    with pytest.raises(ProjectStateError, match="unfinished gate"):
        validate_project_state(state)


def test_public_globe_promotion_is_rejected() -> None:
    state = copy.deepcopy(_state())
    state["capability"]["globe"] = "public"
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_empty_payload_is_validated_instead_of_reloading_current_state() -> None:
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state({})


def test_completed_gate_c_cannot_bypass_frozen_review_evidence() -> None:
    state = _completed_state_without_evidence()

    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_completed_gate_c_cannot_keep_blockers() -> None:
    state = _state()
    state["gate"]["status"] = "completed"
    state["gate"]["decision"] = "FREEZE"
    state["gate"]["evidence"] = {
        "frozen_commit": "a" * 40,
        "frozen_tree": "b" * 40,
        "review_registry_ref": "fixtures/world_slices/leonardo_romagna_1502/v1/review_registry.json",
        "gate_decision_ref": "fixtures/world_slices/leonardo_romagna_1502/v1/gate_c_decision.json",
        "review_cost_ref": "fixtures/world_slices/leonardo_romagna_1502/v1/curation_cost.json",
    }

    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_nonexistent_frozen_commit_is_rejected_by_git() -> None:
    with pytest.raises(ProjectStateError, match="Git verification failed"):
        _validate_frozen_git_revision("a" * 40, "b" * 40, "c" * 64)


def test_frozen_commit_tree_mismatch_is_rejected() -> None:
    import subprocess

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    with pytest.raises(ProjectStateError, match="does not resolve to the recorded tree"):
        _validate_frozen_git_revision(commit, "b" * 40, "c" * 64)


def test_review_chronology_rejects_reversed_timestamps() -> None:
    review = {
        "started_at": "2026-08-09T09:10:00Z",
        "completed_at": "2026-08-09T09:09:00Z",
        "duration_minutes": 1,
    }
    with pytest.raises(ProjectStateError, match="cannot precede"):
        _validate_review_chronology(review, datetime(2026, 8, 9, 10, tzinfo=timezone.utc))


def test_review_duration_must_equal_rounded_elapsed_time() -> None:
    review = {
        "started_at": "2026-08-09T09:00:00Z",
        "completed_at": "2026-08-09T09:05:01Z",
        "duration_minutes": 999,
    }
    with pytest.raises(ProjectStateError, match="rounded-up elapsed"):
        _validate_review_chronology(review, datetime(2026, 8, 9, 10, tzinfo=timezone.utc))


def test_review_cannot_predate_the_frozen_commit() -> None:
    review = {
        "started_at": "2026-08-09T09:00:00Z",
        "completed_at": "2026-08-09T09:01:00Z",
        "duration_minutes": 1,
    }
    with pytest.raises(ProjectStateError, match="before the frozen commit exists"):
        _validate_review_chronology(
            review,
            datetime(2026, 8, 9, 10, tzinfo=timezone.utc),
            not_before=datetime(2026, 8, 9, 9, 57, 2, tzinfo=timezone.utc),
        )


def test_frozen_git_timestamp_with_non_utc_offset_is_normalized() -> None:
    import subprocess

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    parsed = _frozen_commit_time(commit)
    assert parsed.tzinfo is timezone.utc


def test_reviewed_content_digest_rejects_revision_without_scope_files() -> None:
    import subprocess

    empty_tree = subprocess.check_output(
        ["git", "hash-object", "-t", "tree", "/dev/null"], text=True
    ).strip()
    with pytest.raises(ProjectStateError, match="lacks reviewed content paths"):
        _reviewed_content_digest(empty_tree)


def test_narrow_cannot_close_the_old_frozen_scope() -> None:
    state = _state()
    state["gate"]["decision"] = "NARROW"
    with pytest.raises(ProjectStateError, match="new in-progress Gate C revision"):
        _validate_completed_gate_transition(state)


def test_reject_cannot_advance_to_gate_d() -> None:
    state = _state()
    state["gate"]["decision"] = "REJECT"
    state["capability"]["world_slice"] = "gate_c_rejected_non_public"
    state["next_transition"]["gate"] = "D"
    with pytest.raises(ProjectStateError, match="transition to STOP"):
        _validate_completed_gate_transition(state)
