from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_foundation_v3_restores_the_spatial_temporal_world_model() -> None:
    concept = _read("docs/ARTEMIS_CONCEPT.md")
    thesis = _read("docs/PRODUCT_THESIS.md")
    model = _read("docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md")

    assert "Миссия ARTEMIS — помогать человеку понимать мир как взаимосвязанную систему" in concept
    assert "Space and time are core coordinates" in concept
    assert "Evidence не является миссией ARTEMIS" in concept
    assert "Life in Context" in thesis
    assert "synchronized map/time/layers" in thesis

    for object_name in ("Entity", "Event", "State", "Process", "Trajectory", "Region", "Layer"):
        assert object_name in model

    assert "co_present" in model
    assert "documented_encounter" in model
    assert "causal" in model


def test_research_work_target_is_distinct_from_first_value_and_mutable_runtime() -> None:
    contract = _read("docs/RESEARCH_SLICE_CONTRACT.md")
    spec = _read("docs/RESEARCH_SLICE_SPEC.md")
    truth = _read("docs/PROJECT_TRUTH.md")

    assert "Investigation → immutable Slice Revision → Research Brief" in contract
    assert "Research Brief = readable projection of one Slice Revision" in contract
    assert "contextual spatial-temporal understanding" in contract
    assert "Не каждый synchronized exploration обязан создавать Investigation или Brief" in contract
    assert "current mutable runtime persistence envelope" in spec
    assert "content counter, а не immutable revision id" in spec
    assert "first-class Investigation" in truth
    assert "revision-pinned share" in truth


def test_epistemic_axes_and_model_assertions_are_locked() -> None:
    epistemic = _read("docs/EPISTEMIC_CONTRACT.md")
    dictionary = _read("docs/DATA_DICTIONARY.md")

    for dimension in (
        "Claim kind",
        "Origin",
        "Review state",
        "Confidence",
        "Evidence state",
        "Uncertainty",
    ):
        assert dimension in epistemic

    for claim_kind in ("`observation`", "`inference`", "`interpretation`", "`hypothesis`", "`counterfactual`"):
        assert claim_kind in epistemic

    assert "supports" in epistemic
    assert "challenges" in epistemic
    assert "contextualizes" in epistemic
    assert "Locator обязателен" in epistemic
    assert "Computed proximity, overlap, before/after and Similarity" in epistemic
    assert "First-class Claim schema ещё не реализована" in dictionary


def test_proximity_and_shared_classification_do_not_satisfy_relation_value() -> None:
    epistemic = _read("docs/EPISTEMIC_CONTRACT.md")
    model = _read("docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md")
    dictionary = _read("docs/DATA_DICTIONARY.md")
    truth = _read("docs/PROJECT_TRUTH.md")

    assert "Pairwise `same_movement` является derived shared-classification view" in epistemic
    assert "`same_movement` is legacy documented shared-classification projection" in dictionary
    assert "10 из 12 current Relation records" in truth
    assert "Co-presence вычисляется из модели и не создаёт Relation автоматически" in model
    assert "Система не повышает уровень автоматически" in model


def test_relation_ladder_extension_closes_promotion_boundaries() -> None:
    contract = _read("docs/RELATION_LADDER_CONTRACT.md")
    package = _read("fixtures/world_model/relations/v1/package.json")

    for level in (
        "co_present",
        "possible_encounter",
        "documented_encounter",
        "interaction",
        "influence",
        "causal",
    ):
        assert level in contract
        assert level in package

    assert "five explicit negative regression classes" in contract
    assert "same_movement" in contract
    assert "Similarity" in contract
    assert '"automatic": false' in package


def test_gate_a_is_preserved_as_ready_architecture_fixture_evidence() -> None:
    package = _read("docs/work/validation_modules/README.md")
    registry = _read("docs/work/validation_modules/review_registry.json")
    work_registry = _read("docs/work/README.md")
    decision = _read("docs/VALIDATION_DECISION.md")

    assert "Package status: `READY`" in package
    assert registry.count('"status": "READY"') == 3
    assert registry.count('"decision": "READY"') == 6
    assert "completed Gate A executable package" in work_registry
    assert "Gate A fixtures" in decision
    assert "not user-value evidence" in decision


def test_foundation_v3_validation_is_same_content_and_relation_safe() -> None:
    validation = _read("docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md")
    decision = _read("docs/VALIDATION_DECISION.md")

    assert "6–8 primary users" in validation
    assert "same-content baseline" in validation
    assert "two evaluators" in validation
    assert "co-presence or similarity stated as documented encounter/influence/causality" in validation
    assert "FOUNDATION V3 / PENDING USER EVIDENCE" in decision
    assert "Opened future branch | `NONE`" in decision


def test_concept_v2_is_preserved_but_cannot_authorize_execution() -> None:
    old_decision = _read("docs/work/2026-07-26_CONCEPT_LOCK_V2.md")
    new_decision = _read("docs/work/2026-07-28_FOUNDATION_V3_DECISION.md")
    migration = _read("docs/work/2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md")

    assert "SUPERSEDED BY FOUNDATION V3" in old_decision
    assert "must not authorize Gate B–E execution" in old_decision
    assert "Supersedes: `2026-07-26_CONCEPT_LOCK_V2.md`" in new_decision
    assert "No runtime or data record is migrated solely because this matrix exists" in migration
