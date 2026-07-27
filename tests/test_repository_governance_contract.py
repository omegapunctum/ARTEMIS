from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_agent_and_documentation_routing_have_single_registries() -> None:
    agents = _read("AGENTS.md")
    foundation = _read("docs/FOUNDATION_INDEX.md")
    documentation = _read("docs/DOCUMENTATION_SYSTEM.md")
    structure = _read("docs/PROJECT_STRUCTURE.md")
    work_registry = _read("docs/work/README.md")

    assert "single entrypoint for agents" in agents
    assert "docs/FOUNDATION_INDEX.md" in agents
    assert "docs/work/README.md" in agents
    assert "canonical owner registry закреплён только в этом документе" in foundation
    assert "Текущий canonical layer зарегистрирован только" in documentation
    assert "Полный canonical set" in structure
    assert "working-layer lifecycle registry" in work_registry


def test_completed_concept_lock_is_not_the_next_execution_step() -> None:
    priorities = _read("docs/PRIORITIES.md")
    phases = _read("docs/PROJECT_PHASES.md")
    truth = _read("docs/PROJECT_TRUTH.md")
    master_prompt = _read("docs/ARTEMIS_MASTER_PROMPT.md")

    assert "### P0.1 Concept Lock v2 [current]" not in priorities
    assert "1. P0.2 three deep modules." in priorities
    assert "### Track A — Concept Lock v2 [completed]" in phases
    assert "1. Three deep research modules." in phases
    assert "1. подготовить три deep research modules" in truth
    assert "1. three deep research modules;" in master_prompt


def test_obsolete_plans_are_archived_and_cannot_open_scope() -> None:
    work_registry = _read("docs/work/README.md")

    for filename in (
        "ARTEMIS_AI_STRATEGY_v1_0.md",
        "COURSES_MVP_SCOPE.md",
        "FUNCTIONAL_EXPANSION_ROADMAP.md",
    ):
        assert not (ROOT / "docs" / "work" / filename).exists()
        archived = ROOT / "docs" / "archive" / filename
        assert archived.is_file()
        assert filename in work_registry


def test_web_storage_policy_matches_current_low_sensitivity_runtime_use() -> None:
    readme = _read("README.md")
    map_runtime = _read("js/map.js")
    ui_runtime = _read("js/ui.js")

    assert "Credentials, tokens, owner identity and private research content are never stored" in readme
    assert "Current low-sensitivity Web Storage use" in readme
    assert "window.localStorage" in map_runtime
    assert "window.sessionStorage" in ui_runtime
    assert "COURSE_PROGRESS_STORAGE_KEY" in ui_runtime


def test_proven_dead_repository_artifacts_do_not_return() -> None:
    for relative_path in (
        "api",
        "scripts/build_geojson.py",
        "analysis_failures.log",
        "failures.log",
    ):
        assert not (ROOT / relative_path).exists(), relative_path


def test_migration_plan_preserves_target_dependency_order() -> None:
    plan = _read("docs/work/2026-07-27_CONCEPT_LOCK_MIGRATION_PLAN_v1.md")

    positions = [
        plan.index("### Gate A — Deep research modules"),
        plan.index("### Gate B — Claim/Evidence and classification migration"),
        plan.index("### Gate C — Investigation, revision and Brief migration"),
        plan.index("### Gate D — Research interface and public target E2E"),
        plan.index("### Gate E — Controlled and field validation"),
    ]
    assert positions == sorted(positions)
    assert "`#309` Pages/API E2E | rewrite" in plan
    assert "closed `#316` | historical compatibility evidence" in plan
