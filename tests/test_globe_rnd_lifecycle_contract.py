from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_355_owns_one_core_reset_product_loop() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")
    scope = _text("docs/ARTEMIS_PRODUCT_SCOPE.md")

    assert "Active cycle: Core Reset inside the Globe MVP vertical" in priorities
    assert "Active primary issue: GitHub issue `#355`" in priorities
    assert "4.8R — Core Reset / one Leonardo Globe product loop" in phases
    assert "Core Reset inside Gate D" in scope


def test_core_path_preserves_world_model_and_frozen_slice_truth() -> None:
    priorities = _text("docs/PRIORITIES.md")
    truth = _text("docs/PROJECT_TRUTH.md")

    assert (
        "Leonardo sources/manifests → World Model → Explorer State → "
        "Render Projection → Globe + inspector"
    ) in priorities
    assert "Gate C `FREEZE` evidence" in priorities
    assert "historical Claims remain draft/rejected" in priorities
    assert "no route or Region geometry is invented" in priorities
    assert "Gate C is completed/FREEZE" in truth


def test_public_surfaces_have_one_primary_product_and_one_compatibility_path() -> None:
    priorities = _text("docs/PRIORITIES.md")
    truth = _text("docs/PROJECT_TRUTH.md")
    structure = _text("docs/PROJECT_STRUCTURE.md")

    for text in (priorities, truth, structure):
        assert "/globe/" in text
        assert "/atlas/" in text

    assert "Leonardo Globe is the primary" in priorities
    assert "Architecture Atlas is preserved at `/atlas/` as a compatibility baseline" in priorities
    assert "public `/` is generated from" in structure


def test_legacy_and_premature_infrastructure_is_outside_core() -> None:
    priorities = _text("docs/PRIORITIES.md")

    assert "frozen compatibility code" in priorities
    assert "outside the Core critical path" in priorities
    assert "#371/#373 Airtable historical import/review" in priorities
    assert "editable Progressive Refinement runtime" in priorities
    assert "#392" in priorities


def test_early_value_decision_precedes_new_infrastructure() -> None:
    priorities = _text("docs/PRIORITIES.md")
    phases = _text("docs/PROJECT_PHASES.md")

    for decision in ("ITERATE", "NARROW", "STOP/RETHINK"):
        assert decision in priorities
        assert decision in phases
    assert "This decision occurs before new backend/storage infrastructure" in phases
