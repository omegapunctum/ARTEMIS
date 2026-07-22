from __future__ import annotations

import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
UI_JS = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")
DATA_JS = (ROOT / "js" / "data.js").read_text(encoding="utf-8")
TOKENS = (ROOT / "css" / "tokens.css").read_text(encoding="utf-8")
STYLE = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
WORKSPACE_STYLE = (ROOT / "css" / "main-screen.css").read_text(encoding="utf-8")


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

    assert 'data-workspace-nav="workspace"' not in INDEX
    assert 'data-workspace-nav="courses"' not in INDEX
    for target in ("research", "stories", "saved"):
        assert INDEX.count(f'data-workspace-nav="{target}"') == 2

    for target, capability in (("stories", "stories"), ("saved", "slices")):
        matches = re.findall(
            rf'<button\b[^>]*data-workspace-nav="{target}"[^>]*>',
            INDEX,
        )
        assert len(matches) == 2
        assert all(f'data-requires-capability="{capability}"' in markup and " hidden" in markup for markup in matches)

    assert "resolvePublicCapabilities" in UI_JS
    assert "syncPublicCapabilityVisibility" in UI_JS
    assert "window.ARTEMIS_CAPABILITIES" in UI_JS
    assert "stories: normalizeCapabilityFlag(overrides.stories, false)" in UI_JS
    assert "setActiveProjectNavigation" in UI_JS
    assert "focusZone: 'stories'" in UI_JS
    assert "focusZone: 'saved'" in UI_JS


def test_map_tools_are_overlayed_without_a_structural_rail() -> None:
    for element_id in ("explore-workspace-trigger", "map-theme-toggle", "live-btn"):
        markup = _element_markup(element_id)
        assert 'class="workspace-tool-icon"' in markup
        assert 'class="sr-only"' in markup

    courses_markup = _element_markup("courses-btn")
    assert " hidden" in courses_markup
    assert "--map-rail-width" not in TOKENS
    assert "--map-rail-width" not in WORKSPACE_STYLE
    assert re.search(r"#workspace-main\s*\{[^}]*grid-template-columns:\s*minmax\(0, 1fr\)", WORKSPACE_STYLE, re.DOTALL)
    assert re.search(r"#explore-toolbar-shell\s*\{[^}]*position:\s*absolute", WORKSPACE_STYLE, re.DOTALL)
    assert re.search(r"#map-container\s*\{[^}]*grid-column:\s*1", WORKSPACE_STYLE, re.DOTALL)


def test_first_run_state_exposes_direct_research_actions() -> None:
    assert 'id="onboarding-explore-btn"' in INDEX
    assert 'id="onboarding-slices-btn"' in INDEX
    assert 'id="onboarding-slices-btn" class="ui-button ui-button-secondary" type="button" data-requires-capability="slices" hidden' in INDEX
    assert "Начните с объекта на карте" in INDEX
    assert "Начните с исследовательского среза" not in INDEX
    assert "onboardingExploreBtn" in UI_JS
    assert "onboardingSlicesBtn" in UI_JS


def test_shell_is_compact_and_context_is_inline() -> None:
    header_start = INDEX.index('<header id="top-header"')
    header_end = INDEX.index("</header>", header_start)
    context_position = INDEX.index('<section id="research-context-bar"', header_start)
    assert header_start < context_position < header_end
    assert "--workspace-strip-height" not in TOKENS
    assert "--workspace-strip-height" not in STYLE
    assert re.search(r"#workspace-frame\s*\{[^}]*border:\s*0;[^}]*border-radius:\s*0;[^}]*box-shadow:\s*none", STYLE, re.DOTALL)
    assert "function scheduleMapResize" in UI_JS
    assert "if (wasDesktopDock !== isDesktopDock) scheduleMapResize(map)" in UI_JS


def test_timeline_is_compact_without_hardcoded_semantic_anchors() -> None:
    assert "TIMELINE_SEMANTIC_ANCHORS" not in UI_JS
    assert "renderTimelineAxis" not in UI_JS
    assert "timeline-axis" not in INDEX
    assert "timeline-anchor" not in STYLE
    assert "--bottom-panel-height: 84px" in TOKENS
    assert re.search(r"\.timeline-track-wrap\s*\{[^}]*height:\s*24px", STYLE, re.DOTALL)
    assert re.search(r"@media \(max-width: 1080px\).*?--bottom-panel-height:\s*84px", STYLE, re.DOTALL)
    assert re.search(r"@media \(max-width: 720px\).*?--bottom-panel-height:\s*80px", STYLE, re.DOTALL)

    for element_id in ("timeline-mode-point", "timeline-mode-range", "timeline-start", "timeline-end"):
        assert f'id="{element_id}"' in INDEX
    assert 'id="timeline" class="timeline-row is-range-mode"' in INDEX
    assert 'id="timeline-mode-range" class="timeline-mode-btn is-active"' in INDEX
    assert "setupTimelinePointerInteractions" in UI_JS
    assert "applyTimelineModeUi" in UI_JS
    assert "updateTimelineLabel" in UI_JS


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

    assert len(relations) == 12
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
