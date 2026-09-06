import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _json(relative_path: str) -> dict:
    return json.loads(_text(relative_path))


def test_355_records_m4_adopt_and_current_m5_checkpoint() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")
    scope = _text("docs/ARTEMIS_PRODUCT_SCOPE.md")
    state = _json("docs/project_state.json")

    assert "Active primary issue: GitHub issue `#355`" in priorities
    assert "Core Reset was completed by PR `#393`" in priorities
    assert "PR `#395`" in priorities
    assert "PR `#396`" in priorities
    assert "M1 is complete" in priorities
    assert "PR #400 completed" in priorities

    assert "Core Reset [completed]" in phases
    assert "Leonardo Temporal Map loop, iteration 1 [completed]" in phases
    assert "Fresh user check of the published loop [completed]" in phases
    assert "Leonardo Major-Life Presence Scope v1 [completed]" in phases
    assert "M2 One-source proof [completed]" in phases
    assert "M3 Multi-source proof [completed]" in phases
    assert "M4 Architecture decision [completed]" in phases
    assert "M5 Whole-Life Runtime Proof [completed]" in phases

    assert "Current increment: `Gate E evidence preparation`" in scope
    assert state["active_vertical"]["issue"] == 355
    assert state["phase"]["id"] == "5.1"
    assert state["gate"]["id"] == "D"
    assert state["gate"]["status"] == "completed"
    assert state["gate"]["decision"] == "ADVANCE_TO_GATE_E"
    assert state["architecture_checkpoint"]["decision"] == "ADOPT"
    assert state["current_checkpoint"]["id"] == "M5"
    assert state["current_checkpoint"]["status"] == "completed"
    assert state["current_checkpoint"]["allowed_decisions"] == ["ITERATE", "NARROW", "STOP"]
    assert state["current_checkpoint"]["decision"] == "ITERATE"
    assert state["current_checkpoint"]["pre_start_decision_record"] is False


def test_core_path_preserves_world_model_and_frozen_slice_truth() -> None:
    priorities = _text("docs/PRIORITIES.md")
    truth = _text("docs/PROJECT_TRUTH.md")

    assert (
        "Leonardo sources/manifests → World Model → Explorer State → "
        "Render Projection → Globe + timeline + concise details"
    ) in priorities
    assert "Gate C `FREEZE` evidence" in priorities
    assert "historical Claims remain draft/rejected" in priorities
    assert "no route or Region geometry is invented" in priorities
    assert "Gate C is completed/FREEZE" in truth
    assert "four Romagna Presences" in priorities
    assert "source-bound reference anchors" in priorities


def test_temporal_map_interaction_contract_is_current() -> None:
    priorities = _text("docs/PRIORITIES.md")
    scope = _text("docs/ARTEMIS_PRODUCT_SCOPE.md")
    truth = _text("docs/PROJECT_TRUTH.md")

    combined = "\n".join((priorities, scope, truth))
    assert "full-width bottom" in combined
    assert "two-handle" in combined
    assert "one current-time cursor" in combined
    assert "popup" in combined
    assert "double-click" in combined
    assert "chronology only" in combined
    assert "historical route geometry" in combined

    assert "no map-camera movement on single click" in scope
    assert "Trajectory` remains the semantic authority" in scope


def test_public_surfaces_have_one_primary_product_and_one_compatibility_path() -> None:
    priorities = _text("docs/PRIORITIES.md")
    truth = _text("docs/PROJECT_TRUTH.md")
    structure = _text("docs/PROJECT_STRUCTURE.md")

    for text in (priorities, truth, structure):
        assert "/globe/" in text
        assert "/atlas/" in text

    assert "Leonardo Globe as the primary product-development/research surface" in priorities
    assert "Architecture Atlas at `/atlas/` as a compatibility baseline" in priorities
    assert "public `/` is generated from" in structure
    assert "public research prototype" in truth


def test_legacy_and_premature_infrastructure_is_outside_core() -> None:
    priorities = _text("docs/PRIORITIES.md")
    operating_system = _text("docs/DEVELOPMENT_OPERATING_SYSTEM.md")

    assert "frozen compatibility code" in priorities
    assert "outside the Core critical path" in priorities
    assert "#371/#373 Airtable historical import/review" in priorities
    assert "editable Progressive Refinement runtime" in priorities
    assert "#392" in operating_system
    assert "generic provider, federation, reconciliation, ingestion or storage infrastructure" in priorities
    assert "a third provider or second Presence before a separate bounded branch decision" in priorities
    assert "context/layers" in priorities


def test_m4_adopt_preserves_semantic_direction_during_m5() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")
    validation = _text("docs/VALIDATION_DECISION.md")
    m2 = _text("docs/work/2026-09-01_TEMPORAL_MAP_MILESTONES_AND_M2_PROOF_v1.md")
    m2_decision = _text("docs/work/2026-09-01_TEMPORAL_MAP_M2_EXIT_DECISION_v1.md")
    m3 = _text("docs/work/2026-09-01_TEMPORAL_MAP_M3_TWO_SOURCE_PROOF_v1.md")
    m3_decision = _text("docs/work/2026-09-01_TEMPORAL_MAP_M3_EXIT_DECISION_v1.md")
    decision_record = _text("docs/work/2026-09-01_TEMPORAL_MAP_M4_ARCHITECTURE_DECISION_v1.md")
    architecture = _text("docs/PLATFORM_ARCHITECTURE_DECISION.md")
    state = _json("docs/project_state.json")

    expected = ["ADOPT", "NARROW", "REJECT"]
    assert state["architecture_checkpoint"]["allowed_decisions"] == expected
    assert state["gate"]["allowed_decisions"] == ["ADVANCE_TO_GATE_E", "NARROW", "REJECT"]

    for decision in expected:
        assert decision in decision_record

    assert "No implementation branch is currently opened" in priorities
    assert "M5 bounded UX correction completed" in state["next_transition"]["condition"]
    assert state["gate"]["decision"] == "ADVANCE_TO_GATE_E"
    assert state["architecture_checkpoint"]["decision"] == "ADOPT"
    assert "PROCEED_TO_M3" in m2
    assert "Decision: `PROCEED_TO_M3`" in m2_decision
    assert "Recorded outcome: `PROCEED_TO_M4`" in m3
    assert "Decision: `PROCEED_TO_M4`" in m3_decision
    assert "Decision: `ADOPT`" in decision_record
    assert "Next implementation branch: not opened" in decision_record
    assert "Source-federated semantic boundary" in architecture
    assert "not authorization for live federation" in architecture
    assert "M5 direct product decision | `ITERATE / PR #408`" in validation
    assert "Completed correction | `Temporal Map M5 bounded UX correction v1`" in validation

    branch = _text("docs/work/2026-08-29_LEONARDO_MAJOR_LIFE_PRESENCE_SCOPE_v1.md")
    assert "6–10 major-life Presence anchors" in branch
    assert "1452–1519" in branch
    assert "route_geometry=null" in branch
    assert "Stage C — Runtime increment [not authorized]" in branch

    active_text = "\n".join((priorities, phases, decision_record, _text("docs/project_state.json")))
    assert "ADVANCE_TO_GATE_E" in active_text
    assert "EXPAND ONE BRANCH" not in active_text


def test_m5_governance_deviation_and_exit_are_explicit() -> None:
    alignment = _text("docs/work/2026-09-03_TEMPORAL_MAP_M5_GOVERNANCE_ALIGNMENT_v1.md")
    state = _json("docs/project_state.json")

    assert "no intervening repository decision record exists" in alignment
    assert "explicit owner instruction" in alignment
    assert "does not convert that later instruction into a retroactive pre-start decision" in alignment
    assert "ITERATE" in alignment
    assert "NARROW" in alignment
    assert "STOP" in alignment
    assert state["current_checkpoint"]["implementation_pr"] == 406
    assert state["current_checkpoint"]["entry_authority"] == "explicit_owner_instruction"

    exit_record = _text("docs/work/2026-09-04_TEMPORAL_MAP_M5_EXIT_DECISION_v1.md")
    assert "Decision: **`ITERATE`**" in exit_record
    assert "Next implementation branch: not opened" in exit_record
    assert "unknown_route" in exit_record
    assert "route_geometry=null" in exit_record
    assert "PR #394 remains closed and superseded" in exit_record


def test_m5_bounded_ux_scope_opens_one_non_route_correction() -> None:
    decision = _text("docs/work/2026-09-05_TEMPORAL_MAP_M5_BOUNDED_UX_SCOPE_v1.md")
    validation = _text("docs/VALIDATION_DECISION.md")
    state = _json("docs/project_state.json")

    assert "authorize exactly one bounded UX implementation branch" in decision
    assert "all seven recorded corrections" in decision
    assert "Do not connect Presence coordinates with a spatial path" in decision
    assert "unknown_route" in decision
    assert "route_geometry=null" in decision
    assert "PROCEED_TO_GATE_D_REVIEW" in decision
    assert "Export Airtable CI remains a separate technical maintenance PR" in decision
    assert "11 coarse Presence anchors / six periods / 1452–1519" in validation
    assert "Temporal Map M5 bounded UX correction v1" in validation
    assert state["ux_correction_checkpoint"]["decision"] == "PROCEED_TO_GATE_D_REVIEW"
    assert state["gate_review"]["recommendation"] == "ADVANCE_TO_GATE_E"
    amendment = _text("docs/work/2026-09-05_M5_POST_411_CORRECTION_v1.md")
    assert "ITERATE" in amendment
    assert "route_geometry=null" in amendment
    assert "supersedes" in amendment


def test_iteration_and_publication_do_not_equal_formal_user_validation() -> None:
    truth = _text("docs/PROJECT_TRUTH.md")
    validation = _text("docs/VALIDATION_DECISION.md")

    assert "formal user value not yet validated" in truth
    assert "FORMAL USER VALUE PENDING" in validation
    assert "R&D research prototype" in validation
    assert "do not by themselves prove user value" in validation
