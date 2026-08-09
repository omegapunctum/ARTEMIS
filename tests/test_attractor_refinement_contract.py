import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_concept_owns_the_long_term_attractor_and_knowledge_model_boundary() -> None:
    concept = _read("docs/ARTEMIS_CONCEPT.md")
    foundation = _read("docs/FOUNDATION_INDEX.md")
    decision = _read("docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md")

    assert "модель знания о мире" in concept
    assert "Долгосрочный аттрактор ARTEMIS" in concept
    assert "World Model` — это source-aware representation" in concept
    assert "не объективный digital twin" in concept
    assert "Attractor guides architecture; it does not authorize implementation scope" in concept
    assert "one semantic core supports many domains" in foundation
    assert "many interfaces" in foundation
    assert "There must not be a second canonical `ATTRACTOR.md`, `NORTH_STAR.md`" in foundation
    assert "The attractor constrains direction, not schedule" in decision


def test_reviewed_world_model_contract_is_preserved_instead_of_silently_redeclared_ready() -> None:
    model = _read("docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md")
    foundation = _read("docs/FOUNDATION_INDEX.md")
    decision = _read("docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md")

    assert "Версия: 1.0" in model
    assert "Статус: active; accepted in PR `#328`" in model
    assert "Source/EvidenceLink относятся к конкретным Claims" in model
    assert "Corpus coverage отделяется от historical absence" in model
    assert "immutable #329" in foundation
    assert "review scope" in foundation
    assert "remains **byte-preserved v1.0**" in decision
    assert "requires a separate semantic-contract revision with new independent review evidence" in decision


def test_ai_can_change_future_view_state_but_not_canonical_knowledge() -> None:
    policy = _read("docs/AI_POLICY.md")
    master = _read("docs/ARTEMIS_MASTER_PROMPT.md")

    assert "Knowledge Exploration Interface" in policy
    assert "AI may control the VIEW. AI may propose KNOWLEDGE. AI may not silently rewrite TRUTH" in policy
    assert "view_action" in policy
    assert "exploration_plan" in policy
    assert "action must be inspectable and reversible" in policy
    assert "action must not mutate underlying Claims, Sources, EvidenceLinks, Uncertainty" in policy
    assert "AI generation/runtime: gated" in _read("docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md")
    assert "AI-controlled view/query runtime until a separate command/state contract is approved" in master
    assert "Do not implement AI behavior merely because it appears in the long-term attractor" in master


def test_attractor_refinement_does_not_advance_product_gate_or_capability() -> None:
    state = json.loads(_read("docs/project_state.json"))
    foundation = _read("docs/FOUNDATION_INDEX.md")
    master = _read("docs/ARTEMIS_MASTER_PROMPT.md")
    truth = _read("docs/PROJECT_TRUTH.md")

    assert state["gate"]["id"] == "C"
    assert state["gate"]["status"] == "completed"
    assert state["gate"]["decision"] == "FREEZE"
    assert state["next_transition"]["gate"] == "D"
    assert state["capability"]["globe"] == "non_public_r_and_d"
    assert state["github"]["active_issues"] == [355]

    assert "Issue `#363` / PR `#364`: Foundation v3.1 Attractor refinement — **COMPLETED**" in foundation
    assert "Gate D — source-aware Globe experience — is the next product gate, but it is **not currently opened/in progress**" in master
    assert "Foundation v3.1 / #363 / PR #364 is completed" in truth
    assert "Gate D is still only the next product gate" in truth


def test_personal_knowledge_remains_future_and_does_not_change_entity_model() -> None:
    concept = _read("docs/ARTEMIS_CONCEPT.md")
    entity_model = _read("docs/ENTITY_MODEL.md")

    assert "Персональный контекст знания — future branch" in concept
    assert "**не** добавляет `UserKnowledgeState`, `KnowledgeGap`, `ConceptMastery`" in concept
    assert "UserKnowledgeState" not in entity_model
    assert "ConceptMastery" not in entity_model
