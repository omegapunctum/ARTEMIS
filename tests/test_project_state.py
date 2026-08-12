import copy
import json
from datetime import datetime, timezone

import pytest

from scripts.validate_project_state import (
    GATE_C_FINALIZATION_COMMIT,
    GATE_C_FINALIZATION_TREE,
    ProjectStateError,
    STATE_PATH,
    _frozen_commit_time,
    _resolve_gate_c_finalization_ref,
    _reviewed_content_digest,
    _validate_completed_gate_transition,
    _validate_frozen_git_revision,
    _validate_review_chronology,
    validate_project_state,
)


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _historical_gate_c_payload() -> dict:
    state = _state()
    state["gate"] = copy.deepcopy(state["completed_gates"][0])
    state["next_transition"] = {"gate": "D", "condition": "Recorded Gate C transition."}
    return state


def test_current_project_state_opens_one_gate_d_vertical() -> None:
    state = _state()
    assert validate_project_state() == {
        "gate": "D",
        "gate_status": "in_progress",
        "active_issue_count": len(state["github"]["active_issues"]),
        "blocker_count": 0,
    }


def test_gate_c_finalization_evidence_ref_is_pinned() -> None:
    import subprocess

    assert _resolve_gate_c_finalization_ref() == GATE_C_FINALIZATION_COMMIT
    actual_tree = subprocess.check_output(
        ["git", "rev-parse", f"{GATE_C_FINALIZATION_COMMIT}^{{tree}}"], text=True
    ).strip()
    assert actual_tree == GATE_C_FINALIZATION_TREE


def test_completed_gate_c_history_cannot_be_dropped() -> None:
    state = _state()
    state["completed_gates"] = []
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_completed_gate_c_history_cannot_drop_evidence() -> None:
    state = _state()
    state["completed_gates"][0].pop("evidence")
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_issue_lifecycle_sets_cannot_overlap() -> None:
    state = _state()
    state["github"]["deferred_issues"].append(355)
    with pytest.raises(ProjectStateError, match="active/deferred overlap"):
        validate_project_state(state)


def test_relation_issue_must_be_deferred_before_relations() -> None:
    state = _state()
    state["github"]["deferred_issues"].remove(331)
    with pytest.raises(ProjectStateError, match="relation issue #331 must remain deferred"):
        validate_project_state(state)


def test_gate_d_decision_set_cannot_drift() -> None:
    state = _state()
    state["gate"]["allowed_decisions"] = ["FREEZE", "NARROW", "REJECT"]
    with pytest.raises(ProjectStateError, match="Gate D decision set drift"):
        validate_project_state(state)


def test_gate_e_cannot_open_before_gate_d_decision() -> None:
    state = _state()
    state["next_transition"]["gate"] = "E"
    with pytest.raises(ProjectStateError, match="Gate E cannot open"):
        validate_project_state(state)


def test_blocked_gate_d_requires_named_blocker() -> None:
    state = _state()
    state["gate"]["status"] = "blocked"
    with pytest.raises(ProjectStateError, match="must name at least one blocker"):
        validate_project_state(state)


def test_public_globe_promotion_is_rejected() -> None:
    state = _state()
    state["capability"]["globe"] = "public"
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state(state)


def test_empty_payload_is_validated_instead_of_reloading_current_state() -> None:
    with pytest.raises(ProjectStateError, match="schema validation failed"):
        validate_project_state({})


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


def test_historical_narrow_cannot_close_the_old_frozen_scope() -> None:
    state = _historical_gate_c_payload()
    state["gate"]["decision"] = "NARROW"
    with pytest.raises(ProjectStateError, match="new in-progress Gate C revision"):
        _validate_completed_gate_transition(state)


def test_historical_reject_cannot_advance_to_gate_d() -> None:
    state = _historical_gate_c_payload()
    state["gate"]["decision"] = "REJECT"
    state["capability"]["world_slice"] = "gate_c_rejected_non_public"
    with pytest.raises(ProjectStateError, match="transition to STOP"):
        _validate_completed_gate_transition(state)
