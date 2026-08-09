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
    operating_system = _read("docs/DEVELOPMENT_OPERATING_SYSTEM.md")

    assert "single entrypoint for agents" in agents
    assert "docs/FOUNDATION_INDEX.md" in agents
    assert "docs/work/README.md" in agents
    assert "единственный реестр canonical owner documents" in foundation
    assert "Текущий canonical layer зарегистрирован только" in documentation
    assert "Полный canonical set" in structure
    assert "working-layer lifecycle registry" in work_registry
    assert "SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md" in foundation
    assert "UNCERTAINTY_SEMANTICS_CONTRACT.md" in foundation
    assert "SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md" in structure
    assert "fixtures/" in structure
    assert "validate_world_model_fixtures.py" in structure
    assert "validate_uncertainty_fixtures.py" in structure
    assert "uncertainty/" in structure
    assert "One product vertical is active" in operating_system
    assert "docs/project_state.json" in operating_system
    assert (ROOT / "docs" / "project_state.schema.json").is_file()


def test_globe_mvp_is_active_and_relation_contract_is_paused() -> None:
    priorities = _read("docs/PRIORITIES.md")
    phases = _read("docs/PROJECT_PHASES.md")
    truth = _read("docs/PROJECT_TRUTH.md")
    master_prompt = _read("docs/ARTEMIS_MASTER_PROMPT.md")

    assert "Active cycle: Globe MVP" in priorities
    assert "Active primary issue: GitHub issue `#355`" in priorities
    assert "#330 uncertainty fixtures" in priorities
    assert "P0.2 Cross-renderer semantic parity — COMPLETED" in priorities
    assert "#331 relation predicates" in priorities

    assert "Активная фаза: **4.8 Globe MVP vertical / real World Slice**" in phases
    assert "Статус: **ACTIVE / ISSUE #355**" in phases
    assert "SUPERSEDED BEFORE GATES B–E" in phases
    assert "#330 / PR #337 — reviewed uncertainty semantics" in phases
    assert "Completed recovery foundation" in phases
    assert "#332/#360 / Leonardo-in-Romagna World Slice 1502" in phases

    assert "#330 / PR #337 uncertainty semantics — READY" in truth
    assert "Issue #331 is paused" in truth
    assert "issue #355 is the active product-facing MVP contour" in truth
    assert "#344 / PR #351 semantic parity is merged executable evidence" in truth

    assert "Active: Globe MVP / issue `#355`." in master_prompt
    assert "#344 / PR #351 semantic parity as a green renderer foundation" in master_prompt
    assert "Issue #331 is `PAUSED`" in master_prompt
    assert "superseded #323–#325 path and PR #314 are closed" in master_prompt


def test_globe_architecture_does_not_create_a_second_semantic_core() -> None:
    data_contract = _read("docs/DATA_CONTRACT.md")
    master_prompt = _read("docs/ARTEMIS_MASTER_PROMPT.md")
    work_registry = _read("docs/work/README.md")
    globe_record = _read("docs/work/2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md")

    assert "canonical public **2D map projection**" in data_contract
    assert "must not be promoted into the canonical representation" in data_contract
    assert "renderer-ready GeoJSON, engine primitives, meshes or tiles are derived projections" in data_contract
    assert "No competing semantic/world-model source of truth" in master_prompt
    assert "Renderer engines do not own domain semantics" in master_prompt
    assert "2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md" in work_registry
    assert "one spatial-temporal world model" in globe_record.lower()
    assert "Renderer payloads are projections" in globe_record
    assert "Semantic parity is not screenshot parity" in globe_record


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


def test_superseded_migration_plan_cannot_open_v2_execution() -> None:
    old_plan = _read("docs/work/2026-07-27_CONCEPT_LOCK_MIGRATION_PLAN_v1.md")
    work_registry = _read("docs/work/README.md")
    matrix = _read("docs/work/2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md")

    assert "### Gate A — Deep research modules" in old_plan
    assert "2026-07-27_CONCEPT_LOCK_MIGRATION_PLAN_v1.md" in work_registry
    assert "superseded execution plan" in work_registry
    assert "Must not authorize #323–#325" in work_registry
    assert "Old Concept v2 implementation issues were closed `not planned`" in matrix
    assert "Clean child issues were created for:" in matrix

    for child_scope in (
        "universal world-model contract and fixtures",
        "spatial-temporal uncertainty",
        "Leonardo World Slice",
        "synchronized explorer",
        "relation ladder",
        "contextual-learning validation",
        "source-bound AI reasoning contract",
    ):
        assert child_scope in matrix
