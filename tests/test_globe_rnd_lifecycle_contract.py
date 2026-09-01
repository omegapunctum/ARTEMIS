import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _json(relative_path: str) -> dict:
    return json.loads(_text(relative_path))


def test_355_records_m4_adopt_without_opening_implementation() -> None:
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
    assert "No post-M4 implementation phase is active" in phases

    assert "Current increment: `Post-M4 hold`" in scope
    assert state["active_vertical"]["issue"] == 355
    assert state["phase"]["id"] == "5.0"
    assert state["gate"]["id"] == "D"
    assert state["gate"]["status"] == "in_progress"
    assert state["gate"]["decision"] == "ADOPT"


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
    assert "public integration of the PR #400 candidate package" in priorities
    assert "a third provider or second Presence before a separate bounded branch decision" in priorities
    assert "context/layers" in priorities


def test_m4_adopt_preserves_semantic_direction_and_post_m4_hold() -> None:
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
    assert state["gate"]["allowed_decisions"] == expected

    for decision in expected:
        assert decision in decision_record

    assert "There is no active implementation branch" in priorities
    assert "before adding new sources" in state["next_transition"]["condition"]
    assert state["gate"]["decision"] == "ADOPT"
    assert "PROCEED_TO_M3" in m2
    assert "Decision: `PROCEED_TO_M3`" in m2_decision
    assert "Recorded outcome: `PROCEED_TO_M4`" in m3
    assert "Decision: `PROCEED_TO_M4`" in m3_decision
    assert "Decision: `ADOPT`" in decision_record
    assert "Next implementation branch: not opened" in decision_record
    assert "Source-federated semantic boundary" in architecture
    assert "not authorization for live federation" in architecture
    assert "Recorded product decision | `ITERATE`" in validation
    assert "Opened next branch | `Leonardo Major-Life Presence Scope v1`" in validation

    branch = _text("docs/work/2026-08-29_LEONARDO_MAJOR_LIFE_PRESENCE_SCOPE_v1.md")
    assert "6–10 major-life Presence anchors" in branch
    assert "1452–1519" in branch
    assert "route_geometry=null" in branch
    assert "Stage C — Runtime increment [not authorized]" in branch

    active_text = "\n".join((priorities, phases, decision_record, _text("docs/project_state.json")))
    assert "ADVANCE_TO_GATE_E" not in active_text
    assert "EXPAND ONE BRANCH" not in active_text


def test_iteration_and_publication_do_not_equal_formal_user_validation() -> None:
    truth = _text("docs/PROJECT_TRUTH.md")
    validation = _text("docs/VALIDATION_DECISION.md")

    assert "formal user value not yet validated" in truth
    assert "FORMAL USER VALUE PENDING" in validation
    assert "R&D research prototype" in validation
    assert "do not by themselves prove user value" in validation
