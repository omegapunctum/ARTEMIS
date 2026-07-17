from __future__ import annotations

import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
UI_JS = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")
DATA_JS = (ROOT / "js" / "data.js").read_text(encoding="utf-8")
STYLE = (ROOT / "css" / "style.css").read_text(encoding="utf-8")


def _element_markup(element_id: str) -> str:
    match = re.search(
        rf"<button\b[^>]*\bid=[\"']{re.escape(element_id)}[\"'][^>]*>.*?</button>",
        INDEX,
        flags=re.DOTALL,
    )
    assert match, f"Missing button #{element_id}"
    return match.group(0)


def test_primary_navigation_is_functional_and_has_no_dead_hash_links() -> None:
    assert 'href="#" class="project-nav-link"' not in INDEX

    for target in ("workspace", "research", "stories", "courses", "saved"):
        assert INDEX.count(f'data-workspace-nav="{target}"') == 2

    assert "setActiveProjectNavigation" in UI_JS
    assert "openCoursesWorkspace" in UI_JS
    assert "focusZone: 'stories'" in UI_JS
    assert "focusZone: 'saved'" in UI_JS


def test_map_rail_uses_named_icons_and_does_not_mix_in_courses() -> None:
    for element_id in ("explore-workspace-trigger", "map-theme-toggle", "live-btn"):
        markup = _element_markup(element_id)
        assert 'class="workspace-tool-icon"' in markup
        assert 'class="sr-only"' in markup

    courses_markup = _element_markup("courses-btn")
    assert " hidden" in courses_markup


def test_first_run_state_exposes_direct_research_actions() -> None:
    assert 'id="onboarding-explore-btn"' in INDEX
    assert 'id="onboarding-slices-btn"' in INDEX
    assert "onboardingExploreBtn" in UI_JS
    assert "onboardingSlicesBtn" in UI_JS


def test_timeline_exposes_semantic_anchor_labels_on_desktop() -> None:
    assert 'role="list" aria-label="Исторические ориентиры"' in INDEX
    assert "node.setAttribute('role', 'listitem')" in UI_JS

    desktop_css = STYLE.split("@media (max-width: 1080px)", maxsplit=1)[0]
    label_rule = re.search(r"\.timeline-anchor-label\s*\{(?P<body>[^}]*)\}", desktop_css)
    assert label_rule, "Missing desktop timeline anchor label rule"
    assert "display: block" in label_rule.group("body")
    assert "--bottom-panel-height: 152px" in desktop_css


def test_documented_relations_are_separate_from_computed_similarity() -> None:
    assert "function getDocumentedRelations" in UI_JS
    assert "function getSimilarityResults" in UI_JS
    assert "getRelatedFeatures" not in UI_JS
    assert "relation: 'Документированные связи'" in UI_JS
    assert "similarity: 'Похожие объекты'" in UI_JS
    assert "same_layer" in UI_JS
    assert "date_overlap" in UI_JS
    assert "loadRelations" in DATA_JS
    assert "relations.json" in DATA_JS


def test_checked_in_relations_reference_public_features_and_evidence() -> None:
    relations = json.loads((ROOT / "data" / "relations.json").read_text(encoding="utf-8"))
    feature_collection = json.loads((ROOT / "data" / "features.geojson").read_text(encoding="utf-8"))
    features = {feature["id"]: feature for feature in feature_collection["features"]}
    relation_ids = {relation["id"] for relation in relations}

    assert len(relations) == 2
    for relation in relations:
        assert uuid.UUID(relation["id"]).version == 4
        assert relation["source_feature_id"] in features
        assert relation["target_feature_id"] in features
        assert relation["source_feature_id"] != relation["target_feature_id"]
        assert relation["source_ids"]
        assert relation["source_refs"]
        assert all(ref["url"].startswith("https://") for ref in relation["source_refs"])
        for feature_id in (relation["source_feature_id"], relation["target_feature_id"]):
            assert relation["id"] in features[feature_id]["properties"]["relation_ids"]

    projected_ids = {
        relation_id
        for feature in features.values()
        for relation_id in feature["properties"].get("relation_ids", [])
    }
    assert projected_ids == relation_ids
