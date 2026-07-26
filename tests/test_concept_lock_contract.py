from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_concept_lock_uses_one_human_research_core() -> None:
    concept = _read("docs/ARTEMIS_CONCEPT.md")
    thesis = _read("docs/PRODUCT_THESIS.md")

    assert "Миссия ARTEMIS — усиливать человеческое исследование" in concept
    assert "AI не является второй миссией проекта" in concept
    assert "Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved" in concept
    assert "Map/time are privileged lenses, not dogma" in concept
    assert "проверяемый Research Brief" in thesis
    assert "EvidenceLinks" in thesis


def test_research_work_target_is_distinct_from_current_mutable_runtime() -> None:
    contract = _read("docs/RESEARCH_SLICE_CONTRACT.md")
    spec = _read("docs/RESEARCH_SLICE_SPEC.md")
    truth = _read("docs/PROJECT_TRUTH.md")

    assert "Investigation → immutable Slice Revision → Research Brief" in contract
    assert "Research Brief = readable projection of one Slice Revision" in contract
    assert "current mutable runtime persistence envelope" in spec
    assert "content counter, а не immutable revision id" in spec
    assert "first-class Investigation" in truth
    assert "revision-pinned share" in truth


def test_epistemic_axes_and_claim_level_evidence_are_locked() -> None:
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

    assert "supports" in epistemic
    assert "challenges" in epistemic
    assert "contextualizes" in epistemic
    assert "Locator обязателен" in epistemic
    assert "First-class Claim schema ещё не реализована" in dictionary


def test_shared_classification_does_not_satisfy_relation_value() -> None:
    epistemic = _read("docs/EPISTEMIC_CONTRACT.md")
    dictionary = _read("docs/DATA_DICTIONARY.md")
    truth = _read("docs/PROJECT_TRUTH.md")
    legacy_corpus = _read("docs/work/2026-07-21_VALIDATION_CORPUS_PILOT_v1.md")

    assert "Pairwise `same_movement` является derived shared-classification view" in epistemic
    assert "`same_movement` is legacy documented shared-classification projection" in dictionary
    assert "10 из 12 current Relation records" in truth
    assert "не считаются substantive Relations" in legacy_corpus


def test_external_validation_requires_three_deep_modules_and_blind_briefs() -> None:
    modules = _read("docs/work/2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md")
    validation = _read("docs/PRODUCT_VALIDATION_PLAN.md")
    decision = _read("docs/VALIDATION_DECISION.md")

    assert modules.count("## 2. Module") == 1
    assert modules.count("## 3. Module") == 1
    assert modules.count("## 4. Module") == 1
    assert "External product validation запрещена" in modules
    assert "ровно 6 primary participants" in validation
    assert "same-content list/detail workflow" in validation
    assert "Два независимых evaluator" in validation
    assert "минимум у 4 из 6 ARTEMIS Brief" in validation
    assert "0/3 READY" in decision


def test_pre_lock_working_docs_are_explicitly_superseded() -> None:
    ai_strategy = _read("docs/work/ARTEMIS_AI_STRATEGY_v1_0.md")
    ui_plan = _read("docs/work/ARTEMIS_UI_UX_IMPLEMENTATION_PLAN_v1_0.md")
    relation_migration = _read("docs/work/2026-07-16_RELATIONS_SIMILARITY_MIGRATION_v1.md")

    assert "Superseded for active planning by Concept Lock v2" in ai_strategy
    assert "Concept Lock v2 supersession" in ui_plan
    assert "Concept Lock v2 supersession" in relation_migration
