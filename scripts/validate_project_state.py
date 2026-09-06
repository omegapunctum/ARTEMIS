#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "project_state.json"
SCHEMA_PATH = ROOT / "docs" / "project_state.schema.json"
GATE_C_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1"
GATE_C_ROOT_RELATIVE = "fixtures/world_slices/leonardo_romagna_1502/v1"
REVIEW_REGISTRY_SCHEMA_PATH = GATE_C_ROOT / "review_registry.schema.json"
GATE_C_DECISION_SCHEMA_PATH = GATE_C_ROOT / "gate_c_decision.schema.json"
REVIEW_ARTIFACT_SCHEMA_PATH = GATE_C_ROOT / "review_artifact.schema.json"
COST_SCHEMA_PATH = GATE_C_ROOT / "curation_cost.schema.json"

# Gate C was independently reviewed on the frozen revision and finalized on this exact
# descendant before PR #362 was squash-merged. The squash commit intentionally is not a
# descendant of the reviewed branch history, so historical evidence is retained through
# immutable, commit-pinned evidence refs rather than by requiring every future HEAD to
# descend from the pre-squash review commit.
GATE_C_FINALIZATION_COMMIT = "c4879b793407d71f9a352a34ab9cd1b260b3e510"
GATE_C_FINALIZATION_TREE = "8246d6d5b7d3ad63d105ea934e539833e1a0c39f"
GATE_C_FINALIZATION_REFS = (
    "refs/remotes/origin/evidence/gate-c-leonardo-romagna-1502-finalization",
    "refs/heads/evidence/gate-c-leonardo-romagna-1502-finalization",
)

REVIEWED_CONTENT_PATHS = (
    ".github/workflows/release-gate.yml",
    "docs/DEVELOPMENT_OPERATING_SYSTEM.md",
    "docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md",
    "docs/project_state.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/claims_manifest.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/claims_manifest.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/coverage_manifest.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/coverage_manifest.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/curation_cost.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/gate_c_decision.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/review_artifact.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/review_registry.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/selection_manifest.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/selection_manifest.schema.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/source_registry.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/source_registry.schema.json",
    "scripts/validate_leonardo_world_slice.py",
    "scripts/validate_project_state.py",
    "tests/test_leonardo_world_slice.py",
    "tests/test_project_state.py",
)
GATE_C_FINALIZATION_PATHS = {
    "docs/PRIORITIES.md",
    "docs/PROJECT_PHASES.md",
    "docs/project_state.json",
    "docs/work/2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md",
    "docs/work/README.md",
    "fixtures/world_slices/leonardo_romagna_1502/v1/README.md",
    "fixtures/world_slices/leonardo_romagna_1502/v1/curation_cost.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/gate_c_decision.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/review_registry.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/reviews/gate_c_semantic_content_review.json",
    "fixtures/world_slices/leonardo_romagna_1502/v1/reviews/gate_c_validator_integrity_review.json",
}
REVIEW_ARTIFACT_RE = re.compile(
    r"^fixtures/world_slices/leonardo_romagna_1502/v1/reviews/"
    r"gate_c_(semantic_content|validator_integrity)_review\.json$"
)


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


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        output = getattr(exc, "output", "")
        raise ProjectStateError(f"Git verification failed for {' '.join(args)}: {output}") from exc


def _resolve_gate_c_finalization_ref() -> str:
    for ref in GATE_C_FINALIZATION_REFS:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            resolved = result.stdout.strip()
            if resolved != GATE_C_FINALIZATION_COMMIT:
                raise ProjectStateError(
                    "Gate C finalization evidence ref moved away from the pinned commit"
                )
            return resolved
    raise ProjectStateError(
        "Gate C finalization evidence ref is unavailable; fetch/retain "
        "evidence/gate-c-leonardo-romagna-1502-finalization"
    )


def _validate_gate_c_finalization_anchor(frozen_commit: str) -> str:
    finalization_commit = _resolve_gate_c_finalization_ref()
    actual_tree = _git("rev-parse", f"{finalization_commit}^{{tree}}")
    if actual_tree != GATE_C_FINALIZATION_TREE:
        raise ProjectStateError("Gate C finalization commit tree does not match its pinned tree")
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", frozen_commit, finalization_commit],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ProjectStateError(
            "frozen Gate C review commit must be an ancestor of the pinned finalization commit"
        ) from exc
    changed = set(
        filter(None, _git("diff", "--name-only", f"{frozen_commit}..{finalization_commit}").splitlines())
    )
    unexpected = changed - GATE_C_FINALIZATION_PATHS
    if unexpected:
        raise ProjectStateError(
            f"reviewed content changed during Gate C finalization: {sorted(unexpected)}"
        )
    return finalization_commit


def _validate_current_gate_c_evidence_subtree(finalization_commit: str) -> None:
    finalization_subtree = _git(
        "rev-parse", f"{finalization_commit}:{GATE_C_ROOT_RELATIVE}"
    )
    current_subtree = _git("rev-parse", f"HEAD:{GATE_C_ROOT_RELATIVE}")
    if current_subtree != finalization_subtree:
        raise ProjectStateError(
            "completed Gate C evidence subtree changed after its pinned finalization"
        )


def _validate_frozen_git_revision(commit: str, tree: str, digest: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9a-f]{40}", tree):
        raise ProjectStateError("frozen commit and tree must be full lowercase Git object ids")
    _git("rev-parse", "--verify", f"{commit}^{{commit}}")
    actual_tree = _git("rev-parse", f"{commit}^{{tree}}")
    if actual_tree != tree:
        raise ProjectStateError("frozen commit does not resolve to the recorded tree")
    finalization_commit = _validate_gate_c_finalization_anchor(commit)
    actual_digest = _reviewed_content_digest(commit)
    if actual_digest != digest:
        raise ProjectStateError("reviewed-content digest does not match the frozen Git revision")
    _validate_current_gate_c_evidence_subtree(finalization_commit)


def _reviewed_content_digest(commit: str) -> str:
    output = _git("ls-tree", "-r", commit, "--", *REVIEWED_CONTENT_PATHS)
    blobs: dict[str, str] = {}
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        _mode, object_type, object_id = metadata.split()
        if object_type != "blob":
            raise ProjectStateError(f"reviewed content path is not a Git blob: {path}")
        blobs[path] = object_id
    missing = set(REVIEWED_CONTENT_PATHS) - set(blobs)
    if missing:
        raise ProjectStateError(f"frozen revision lacks reviewed content paths: {sorted(missing)}")
    canonical = "".join(f"{path}\0{blobs[path]}\n" for path in sorted(blobs))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _parse_utc_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ProjectStateError(f"{label} must be an RFC 3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ProjectStateError(f"{label} must use UTC")
    return parsed.astimezone(timezone.utc)


def _frozen_commit_time(commit: str) -> datetime:
    value = _git("show", "-s", "--format=%cI", commit)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProjectStateError("frozen commit timestamp must be RFC 3339") from exc
    if parsed.tzinfo is None:
        raise ProjectStateError("frozen commit timestamp must include a timezone offset")
    return parsed.astimezone(timezone.utc)


def _validate_review_chronology(
    review: dict, now: datetime, not_before: datetime | None = None
) -> tuple[datetime, datetime]:
    started = _parse_utc_timestamp(review["started_at"], "review started_at")
    completed = _parse_utc_timestamp(review["completed_at"], "review completed_at")
    if completed < started:
        raise ProjectStateError("review completed_at cannot precede started_at")
    if not_before is not None and started < not_before:
        raise ProjectStateError("review cannot start before the frozen commit exists")
    if started > now or completed > now:
        raise ProjectStateError("review timestamps cannot be in the future")
    expected_duration = max(1, math.ceil((completed - started).total_seconds() / 60))
    if review["duration_minutes"] != expected_duration:
        raise ProjectStateError("review duration must equal rounded-up elapsed UTC time")
    return started, completed


def _validate_completed_gate_transition(payload: dict) -> None:
    decision = payload["gate"]["decision"]
    if decision == "NARROW":
        raise ProjectStateError("NARROW requires a new in-progress Gate C revision and re-review")
    if decision == "FREEZE":
        if payload["capability"]["world_slice"] != "gate_c_frozen_non_public":
            raise ProjectStateError("FREEZE must publish the frozen non-public capability")
        if payload["next_transition"]["gate"] not in {"D", "STOP"}:
            raise ProjectStateError("FREEZE must advance to Gate D or STOP")
    if decision == "REJECT":
        if payload["capability"]["world_slice"] != "gate_c_rejected_non_public":
            raise ProjectStateError("REJECT must publish a rejected non-public capability state")
        if payload["next_transition"]["gate"] != "STOP":
            raise ProjectStateError("REJECT must transition to STOP")


def _validate_cost_append_only(cost: dict, frozen_commit: str, reviews: list[dict]) -> None:
    try:
        frozen_cost = json.loads(
            _git(
                "show",
                f"{frozen_commit}:fixtures/world_slices/leonardo_romagna_1502/v1/curation_cost.json",
            )
        )
    except json.JSONDecodeError as exc:
        raise ProjectStateError("frozen curation cost is not valid JSON") from exc
    for field in ("schema_version", "slice_id", "status", "unit", "ready_rule"):
        if cost.get(field) != frozen_cost.get(field):
            raise ProjectStateError(f"curation cost field changed after review: {field}")
    final_cost_ids = {row["cost_activity_ref"] for row in reviews}
    frozen_entries = frozen_cost.get("entries") or []
    current_entries = cost.get("entries") or []
    retained_entries = [row for row in current_entries if row.get("activity_id") not in final_cost_ids]
    added_entries = [row for row in current_entries if row.get("activity_id") in final_cost_ids]
    if retained_entries != frozen_entries:
        raise ProjectStateError("pre-review curation costs changed after the frozen revision")
    if len(added_entries) != 2 or {row.get("activity_id") for row in added_entries} != final_cost_ids:
        raise ProjectStateError("final curation cost may append only the two bound review activities")


def _validate_completed_gate_history(payload: dict) -> None:
    completed_gates = payload["completed_gates"]
    if len(completed_gates) != 1 or completed_gates[0].get("id") != "C":
        raise ProjectStateError("completed gate history must retain exactly the accepted Gate C record")
    gate_c = completed_gates[0]
    historical_payload = {
        **payload,
        "gate": gate_c,
        "next_transition": {
            "gate": gate_c["next_gate"],
            "condition": "Recorded Gate C transition.",
        },
    }
    _validate_completed_gate_transition(historical_payload)
    _validate_gate_c_evidence(historical_payload)


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
    deferred = set(payload["github"]["deferred_issues"])
    superseded = set(payload["github"]["superseded_issues"])
    completed = set(payload["github"]["completed_issues"])
    lifecycle_sets = {
        "active": active,
        "paused": paused,
        "deferred": deferred,
        "superseded": superseded,
        "completed": completed,
    }
    lifecycle_names = tuple(lifecycle_sets)
    for index, left_name in enumerate(lifecycle_names):
        for right_name in lifecycle_names[index + 1 :]:
            overlap = lifecycle_sets[left_name] & lifecycle_sets[right_name]
            if overlap:
                raise ProjectStateError(
                    f"issue lifecycle sets {left_name}/{right_name} overlap: {sorted(overlap)}"
                )
    if payload["active_vertical"]["issue"] not in active:
        raise ProjectStateError("active vertical issue must be present in active_issues")
    if 331 not in deferred:
        raise ProjectStateError("relation issue #331 must remain deferred before documented Relations")
    if paused:
        raise ProjectStateError("the Gate D opening snapshot must not retain stale paused issues")
    if payload["capability"]["globe"] != "public_r_and_d_preview":
        raise ProjectStateError("the current Globe must remain a bounded public R&D preview")

    _validate_completed_gate_history(payload)
    if not {332, 360}.issubset(completed) or {332, 360} & active:
        raise ProjectStateError("completed Gate C must remain in completed issue history")

    if gate["id"] != "D":
        raise ProjectStateError("project_state v1.3 currently opens only Gate D")
    if gate["status"] not in {"in_progress", "blocked"}:
        raise ProjectStateError("Gate D must be in_progress or blocked")
    if gate["allowed_decisions"] != ["ADVANCE_TO_GATE_E", "NARROW", "REJECT"]:
        raise ProjectStateError("Gate D decision set drift")
    if "decision" in gate:
        raise ProjectStateError("Gate D exit remains pending; checkpoint acceptance is not a gate decision")
    if payload["gate_review"]["material_implementation_gaps"]:
        raise ProjectStateError("ADVANCE_TO_GATE_E recommendation cannot ignore material implementation gaps")
    checkpoint = payload["current_checkpoint"]
    if checkpoint["id"] != "M5":
        raise ProjectStateError("the current product checkpoint must remain M5")
    if checkpoint["status"] == "awaiting_manual_product_check" and "decision" in checkpoint:
        raise ProjectStateError("M5 cannot record a product decision before the manual check")
    if checkpoint["status"] == "completed" and "decision" not in checkpoint:
        raise ProjectStateError("completed M5 must record exactly one product decision")
    if checkpoint["pre_start_decision_record"] is not False:
        raise ProjectStateError("M5 governance history must not invent a pre-start decision record")
    if payload["next_transition"]["gate"] != "D":
        raise ProjectStateError("Gate E cannot open before a completed Gate D decision")
    if payload["capability"]["world_slice"] != "gate_c_frozen_non_public":
        raise ProjectStateError("Gate D must begin from the frozen non-public Gate C World Slice")
    if 333 not in superseded or 334 not in deferred:
        raise ProjectStateError("legacy #333/#334 lifecycle must be superseded/deferred under #355")
    if not {371, 373}.issubset(deferred):
        raise ProjectStateError("Airtable import/review must remain deferred outside Gate D")
    if gate["status"] == "blocked" and not payload["blockers"]:
        raise ProjectStateError("a blocked Gate D must name at least one blocker")

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
    _validate_against_schema(cost, COST_SCHEMA_PATH, "curation cost")

    frozen_identity = (evidence["frozen_commit"], evidence["frozen_tree"])
    digest = evidence["reviewed_content_digest"]
    _validate_frozen_git_revision(*frozen_identity, digest)
    frozen_commit_time = _frozen_commit_time(evidence["frozen_commit"])
    if (review_registry.get("frozen_commit"), review_registry.get("frozen_tree")) != frozen_identity:
        raise ProjectStateError("review registry must bind the completed gate's frozen revision")
    if review_registry.get("reviewed_content_digest") != digest:
        raise ProjectStateError("review registry must bind the reviewed-content digest")
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
    now = datetime.now(timezone.utc)
    review_completed_times: list[datetime] = []
    for review in reviews:
        if (review.get("frozen_commit"), review.get("frozen_tree")) != frozen_identity:
            raise ProjectStateError("every Gate C review must inspect the same frozen revision")
        if review.get("reviewed_content_digest") != digest:
            raise ProjectStateError("every Gate C review must bind the reviewed-content digest")
        if review.get("decision") != "READY":
            raise ProjectStateError("completed Gate C requires READY review decisions")
        if review.get("unresolved_critical") != 0 or review.get("unresolved_material") != 0:
            raise ProjectStateError("completed Gate C cannot retain critical or material findings")
        artifact_ref = str(review.get("artifact_ref") or "")
        if not REVIEW_ARTIFACT_RE.fullmatch(artifact_ref):
            raise ProjectStateError("review artifact must use the dedicated Gate C review directory")
        artifact = ROOT / artifact_ref
        if not artifact.is_file():
            raise ProjectStateError(f"review artifact does not exist: {review.get('artifact_ref')}")
        artifact_payload = _load(artifact)
        _validate_against_schema(artifact_payload, REVIEW_ARTIFACT_SCHEMA_PATH, "review artifact")
        identity_fields = (
            "review_id", "reviewer_id", "reviewer_instance_id", "track", "independence_method",
            "frozen_commit", "frozen_tree", "reviewed_content_digest", "started_at",
            "completed_at", "duration_minutes", "decision", "unresolved_critical",
            "unresolved_material", "cost_activity_ref",
        )
        if any(artifact_payload.get(field) != review.get(field) for field in identity_fields):
            raise ProjectStateError("review artifact identity disagrees with the review registry")
        _started, completed = _validate_review_chronology(
            review, now, not_before=frozen_commit_time
        )
        review_completed_times.append(completed)

    if (gate_decision.get("frozen_commit"), gate_decision.get("frozen_tree")) != frozen_identity:
        raise ProjectStateError("Gate C decision must bind the reviewed frozen revision")
    if gate_decision.get("reviewed_content_digest") != digest:
        raise ProjectStateError("Gate C decision must bind the reviewed-content digest")
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
    if gate_decision.get("next_gate") != payload["next_transition"]["gate"]:
        raise ProjectStateError("Gate C decision next_gate must match project_state next transition")
    decided_at = _parse_utc_timestamp(gate_decision["decided_at"], "Gate C decided_at")
    if decided_at > now:
        raise ProjectStateError("Gate C decision cannot be in the future")
    if review_completed_times and decided_at < max(review_completed_times):
        raise ProjectStateError("Gate C decision cannot predate either independent review")

    pending_costs = [
        row["activity_id"] for row in cost.get("entries", [])
        if row.get("measurement_state") == "pending"
    ]
    if pending_costs:
        raise ProjectStateError(f"completed Gate C cannot retain pending cost entries: {pending_costs}")
    _validate_cost_append_only(cost, evidence["frozen_commit"], reviews)
    recuration = next(
        (row for row in cost.get("entries", []) if row.get("activity_id") == "cost-gate-c-full-recuration"),
        None,
    )
    if (
        not recuration
        or recuration.get("measurement_state") != "recorded"
        or not isinstance(recuration.get("duration_minutes"), int)
        or recuration["duration_minutes"] < 1
    ):
        raise ProjectStateError("completed Gate C requires a recorded full recuration activity")

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
