from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIORITIES = ROOT / "docs" / "PRIORITIES.md"
PHASES = ROOT / "docs" / "PROJECT_PHASES.md"
TRUTH = ROOT / "docs" / "PROJECT_TRUTH.md"
MASTER = ROOT / "docs" / "ARTEMIS_MASTER_PROMPT.md"
SCOPE = ROOT / "docs" / "ARTEMIS_PRODUCT_SCOPE.md"
WORK_REGISTRY = ROOT / "docs" / "work" / "README.md"
DECISION = ROOT / "docs" / "work" / "2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md"
WORLD_SLICE_SCOPE = ROOT / "docs" / "work" / "2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_globe_mvp_355_is_the_single_active_product_contour() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    master = _text(MASTER)
    scope = _text(SCOPE)

    assert "Active cycle: Globe MVP" in priorities
    assert "Active primary issue: GitHub issue `#355`" in priorities
    assert "ACTIVE / ISSUE #355" in phases
    assert "Active product vertical: Globe MVP / issue `#355`" in master
    assert "Globe MVP / issue `#355`" in scope


def test_parity_is_completed_recovery_foundation() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    decision = _text(DECISION)

    for text in (priorities, phases, truth, decision):
        assert "#344" in text
        assert "PR #351" in text

    assert "COMPLETED / #344 / PR #351" in priorities
    assert "#344 / PR #351 — cross-renderer semantic parity" in phases
    assert "semantic parity is merged executable evidence" in truth
    assert "Completed recovery: issue `#344` / PR `#351`" in decision


def test_relation_semantics_are_deferred_but_fail_closed() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    master = _text(MASTER)
    decision = _text(DECISION)

    for text in (priorities, phases, truth, master, decision):
        assert "#331" in text
        assert "defer" in text.lower()

    assert "documented Relation predicates" in priorities
    assert "only derived proximity/co-presence" in truth
    assert "only derived proximity/co-presence is allowed" in master


def test_globe_is_primary_development_surface_with_bounded_public_review_only() -> None:
    priorities = _text(PRIORITIES)
    truth = _text(TRUTH)
    scope = _text(SCOPE)
    decision = _text(DECISION)

    assert "Globe is the primary interface-development surface" in priorities
    assert "public R&D preview" in truth
    assert "не является product-ready Globe" in truth
    assert "bounded public R&D preview" in scope
    assert "labelled generated R&D review preview" in decision


def test_one_semantic_core_and_2d_rollback_are_preserved() -> None:
    priorities = _text(PRIORITIES)
    master = _text(MASTER)
    decision = _text(DECISION)

    assert "one World Model → Explorer State → Render Projection path" in priorities
    assert "Renderer engines do not own domain semantics" in master
    assert "Screenshot equality is not semantic parity" in master
    assert "separate domain-specific or renderer-specific truth models" in master
    assert "same-content comparison surface and rollback path" in decision


def test_accepted_renderer_foundations_are_traceable_with_351() -> None:
    priorities = _text(PRIORITIES)
    accepted = {
        "#339 / PR #346",
        "#340 / PR #347",
        "#341 / PR #348",
        "#342 / PR #349",
        "#343 / PR #350",
        "#344 / PR #351",
        "#345 / PR #352",
    }
    assert all(token in priorities for token in accepted)
    assert "#344 / PR #351 — cross-renderer semantic parity" in priorities
    assert "Recovery still open" not in priorities


def test_active_decision_is_registered_and_old_rnd_records_are_evidence() -> None:
    registry = _text(WORK_REGISTRY)

    assert "2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md" in registry
    assert "2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md" in registry
    assert "#355 active Globe MVP product/governance decision" in registry
    assert "2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md" in registry
    assert "Completed execution evidence" in registry


def test_real_world_slice_gate_c_is_completed_but_not_historical_product_data() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    scope = _text(WORLD_SLICE_SCOPE)

    assert "Gate C is completed by a `FREEZE` decision" in priorities
    assert "Completed Gate C delivery" in phases
    assert "Gate C is completed/FREEZE" in truth
    assert "State: `SCOPE_FROZEN / GATE C REVIEWED / NON-PUBLIC`" in scope
    assert "Decision: `FREEZE`" in scope
    assert "Public capability change: none" in scope
    assert "No line connects the selected presence contexts" in scope
    assert "This is not a promotion to reviewed historical data" in scope
    assert "Gate D is the next permitted transition but is not started by this decision" in scope
