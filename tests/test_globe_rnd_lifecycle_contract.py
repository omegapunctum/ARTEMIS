from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIORITIES = ROOT / "docs" / "PRIORITIES.md"
PHASES = ROOT / "docs" / "PROJECT_PHASES.md"
TRUTH = ROOT / "docs" / "PROJECT_TRUTH.md"
MASTER = ROOT / "docs" / "ARTEMIS_MASTER_PROMPT.md"
SCOPE = ROOT / "docs" / "ARTEMIS_PRODUCT_SCOPE.md"
WORK_REGISTRY = ROOT / "docs" / "work" / "README.md"
DECISION = ROOT / "docs" / "work" / "2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md"


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
    assert "Active: Globe MVP / issue `#355`." in master
    assert "Globe MVP / issue `#355`" in scope


def test_parity_is_open_recovery_not_false_completed_evidence() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    decision = _text(DECISION)

    for text in (priorities, phases, truth, decision):
        assert "#344" in text
        assert "PR #351" in text

    assert "Recovery still open" in priorities
    assert "Open recovery" in phases
    assert "not accepted" in truth
    assert "issue #344 was closed while PR #351 remained open" in decision


def test_relation_semantics_are_paused_but_fail_closed() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    master = _text(MASTER)
    decision = _text(DECISION)

    for text in (priorities, phases, truth, master, decision):
        assert "#331" in text
        assert "paus" in text.lower()

    assert "documented Relation predicates" in priorities
    assert "only derived proximity/co-presence" in truth
    assert "only derived proximity/co-presence is allowed" in master


def test_globe_is_primary_development_surface_but_not_public_capability() -> None:
    priorities = _text(PRIORITIES)
    truth = _text(TRUTH)
    scope = _text(SCOPE)
    decision = _text(DECISION)

    assert "Globe is the primary interface-development surface" in priorities
    assert "there is no public ARTEMIS Globe product surface" in truth
    assert "R&D EVIDENCE, NOT PUBLIC CAPABILITY" in truth
    assert "The Globe is not public or product-validated" not in scope  # current truth owns runtime wording.
    assert "Public capability change: none" in decision


def test_one_semantic_core_and_2d_rollback_are_preserved() -> None:
    priorities = _text(PRIORITIES)
    master = _text(MASTER)
    decision = _text(DECISION)

    assert "one World Model → Explorer State → Render Projection path" in priorities
    assert "Renderer engines do not own domain semantics" in master
    assert "Screenshot equality is not semantic parity" in master
    assert "creating separate 2D/3D historical truth datasets" in master
    assert "same-content comparison surface and rollback path" in decision


def test_accepted_renderer_foundations_are_traceable_without_claiming_351() -> None:
    priorities = _text(PRIORITIES)
    accepted = {
        "#339 / PR #346",
        "#340 / PR #347",
        "#341 / PR #348",
        "#342 / PR #349",
        "#343 / PR #350",
        "#345 / PR #352",
    }
    assert all(token in priorities for token in accepted)
    assert "#344 / PR #351 — cross-renderer semantic parity" in priorities
    assert "Recovery still open" in priorities


def test_active_decision_is_registered_and_old_rnd_records_are_evidence() -> None:
    registry = _text(WORK_REGISTRY)

    assert "2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md" in registry
    assert "#355 active Globe MVP product/governance decision" in registry
    assert "2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md" in registry
    assert "Completed execution evidence" in registry
