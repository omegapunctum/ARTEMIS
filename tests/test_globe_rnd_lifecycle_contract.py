from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIORITIES = ROOT / "docs" / "PRIORITIES.md"
PHASES = ROOT / "docs" / "PROJECT_PHASES.md"
TRUTH = ROOT / "docs" / "PROJECT_TRUTH.md"
MASTER = ROOT / "docs" / "ARTEMIS_MASTER_PROMPT.md"
WORK_REGISTRY = ROOT / "docs" / "work" / "README.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_primary_foundation_path_remains_331_to_334() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    master = _text(MASTER)

    for text in (priorities, phases, master):
        assert "#331" in text
        assert "#332" in text
        assert "#333" in text
        assert "#334" in text

    assert "Active primary issue: GitHub issue `#331`" in priorities
    assert "Active primary dependency: issue `#331`" in phases
    assert "Active primary dependency: issue `#331`" in master
    assert "#331 → #332 → #333 → #334" in priorities


def test_globe_339_345_is_completed_evidence_not_active_product_track() -> None:
    priorities = _text(PRIORITIES)
    phases = _text(PHASES)
    truth = _text(TRUTH)
    master = _text(MASTER)
    registry = _text(WORK_REGISTRY)

    assert "Completed renderer R&D: issues `#339–#345`" in priorities
    assert "Completed bounded renderer R&D: issues `#339–#345`" in phases
    assert "The Globe R&D track `#339–#345` is complete" in truth
    assert "Issues `#339–#345` are **completed architecture/R&D evidence**" in master
    assert "#339–#345 Globe renderer R&D track is **completed architecture/R&D evidence**" in registry

    stale_active_phrases = (
        "Parallel non-blocking R&D: 3D Globe / renderer architecture, parent issue `#339`",
        "Parallel non-blocking R&D:",
        "Active parallel issue: `#339`",
        "Active: Globe",
    )
    combined = "\n".join((priorities, phases, truth, master, registry))
    assert all(phrase not in combined for phrase in stale_active_phrases)


def test_public_globe_is_still_not_current_capability() -> None:
    priorities = _text(PRIORITIES)
    truth = _text(TRUTH)
    master = _text(MASTER)

    assert "публичный Globe" in priorities
    assert "there is no public ARTEMIS Globe product surface" in truth
    assert "it is not a public capability" in master
    assert "Production-scale 3D/dynamic Earth remains gated" in priorities
    assert "Production-scale 3D/dynamic Earth remains gated" in truth


def test_project_truth_acknowledges_executable_globe_without_promoting_it() -> None:
    truth = _text(TRUTH)

    assert "A real executable 3D Globe R&D artifact now exists" in truth
    assert "MapLibre GL JS `5.24.0`" in truth
    assert "MapLibre GL JS `4.7.1`" in truth
    assert "generated Globe spike may remain executable evidence" not in truth  # wording belongs to governance, not capability ownership.
    assert "R&D EVIDENCE, NOT PUBLIC CAPABILITY" in truth


def test_master_prompt_preserves_one_semantic_core_renderer_rule() -> None:
    master = _text(MASTER)

    assert "Renderer engines do not own domain semantics" in master
    assert "Renderer payloads are projections of one World Model / World Slice" in master
    assert "Screenshot equality is not semantic parity" in master
    assert "creating separate 2D/3D historical truth datasets" in master
    assert "generated R&D artifacts" in master


def test_completed_globe_pr_chain_is_traceable() -> None:
    priorities = _text(PRIORITIES)
    expected = {
        "#339 / PR #346",
        "#340 / PR #347",
        "#341 / PR #348",
        "#342 / PR #349",
        "#343 / PR #350",
        "#344 / PR #351",
        "#345 / PR #352",
    }
    assert all(token in priorities for token in expected)
