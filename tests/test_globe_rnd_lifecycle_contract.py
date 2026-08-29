import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _json(relative_path: str) -> dict:
    return json.loads(_text(relative_path))


def test_355_owns_one_post_iteration_temporal_map_loop() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")
    scope = _text("docs/ARTEMIS_PRODUCT_SCOPE.md")
    state = _json("docs/project_state.json")

    assert "Active primary issue: GitHub issue `#355`" in priorities
    assert "Core Reset was completed by PR `#393`" in priorities
    assert "PR `#395`" in priorities
    assert "PR `#396`" in priorities
    assert "fresh user check" in priorities.lower()

    assert "Core Reset [completed]" in phases
    assert "Leonardo Temporal Map loop, iteration 1 [completed]" in phases
    assert "Fresh user check of the published loop [active]" in phases

    assert "Current increment: fresh user check of the published PR `#396` loop" in scope
    assert state["active_vertical"]["issue"] == 355
    assert state["gate"]["id"] == "D"
    assert state["gate"]["status"] == "in_progress"


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
    assert "four source-bound Romagna Presences" in priorities


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
    assert "broader Leonardo corpus" in priorities
    assert "default local/global context" in priorities


def test_next_decision_is_single_and_precedes_new_branches() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")
    validation = _text("docs/VALIDATION_DECISION.md")
    state = _json("docs/project_state.json")

    expected = ["ITERATE", "NARROW", "STOP/RETHINK"]
    assert state["gate"]["allowed_decisions"] == expected

    for decision in expected:
        assert decision in priorities
        assert decision in phases
        assert decision in validation

    assert "at most one evidence-backed next branch" in priorities
    assert "before opening at most one evidence-backed next branch" in state["next_transition"]["condition"]

    active_text = "\n".join((priorities, phases, validation, _text("docs/project_state.json")))
    assert "ADVANCE_TO_GATE_E" not in active_text
    assert "EXPAND ONE BRANCH" not in active_text


def test_publication_and_implementation_do_not_equal_user_validation() -> None:
    truth = _text("docs/PROJECT_TRUTH.md")
    validation = _text("docs/VALIDATION_DECISION.md")

    assert "user value not yet validated" in truth
    assert "PENDING USER EVIDENCE" in validation
    assert "public R&D access" in validation
    assert "do not by themselves prove user value" in validation
