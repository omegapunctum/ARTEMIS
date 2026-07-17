from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKENS_STYLE_PATH = ROOT / "css" / "tokens.css"
BASE_STYLE_PATH = ROOT / "css" / "base.css"
CONTROLS_STYLE_PATH = ROOT / "css" / "components" / "controls.css"
SURFACES_STYLE_PATH = ROOT / "css" / "components" / "surfaces.css"
STYLE_PATH = ROOT / "css" / "style.css"
WORKSPACE_STYLE_PATH = ROOT / "css" / "main-screen.css"

FOUNDATION_STYLE_PATHS = (
    TOKENS_STYLE_PATH,
    BASE_STYLE_PATH,
    CONTROLS_STYLE_PATH,
    SURFACES_STYLE_PATH,
)
RUNTIME_STYLE_PATHS = (*FOUNDATION_STYLE_PATHS, STYLE_PATH, WORKSPACE_STYLE_PATH)


REQUIRED_CUSTOM_PROPERTIES = {
    "--bg-root",
    "--bg-surface-1",
    "--border-soft",
    "--text-primary",
    "--accent-primary",
    "--state-success",
    "--state-warning",
    "--state-error",
    "--top-header-height",
    "--bottom-panel-height",
    "--z-map-controls",
    "--timeline-left",
    "--timeline-right",
}


REQUIRED_SELECTOR_FRAGMENTS = {
    "[hidden]",
    ":focus-visible",
    "#app-shell",
    "#workspace-frame",
    "#top-header",
    "#research-context-bar",
    "#map-container",
    "#map",
    "#bottom-panel",
    ".timeline-track-wrap",
    ".detail-panel",
    ".ui-button",
    ".top-panel",
    ".modal",
    ".ugc-panel",
    ".moderation-workspace",
    ".app-status-host",
    ".slice-workzone",
    ".story-mode-surface",
    ".course-mode-surface",
    "prefers-reduced-motion",
}


def _strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def test_owner_style_files_are_substantive_and_balanced() -> None:
    minimum_content = {
        TOKENS_STYLE_PATH: 1_500,
        BASE_STYLE_PATH: 1_500,
        CONTROLS_STYLE_PATH: 3_000,
        SURFACES_STYLE_PATH: 1_200,
        STYLE_PATH: 20_000,
        WORKSPACE_STYLE_PATH: 2_000,
    }

    for path in RUNTIME_STYLE_PATHS:
        css = path.read_text(encoding="utf-8")
        without_comments = _strip_css_comments(css)
        assert len(without_comments) > minimum_content[path], f"Owner stylesheet is too small: {path}"
        assert without_comments.count("{") == without_comments.count("}"), f"Unbalanced CSS: {path}"


def test_shared_style_system_exposes_runtime_contract() -> None:
    css = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_STYLE_PATHS)

    missing_properties = sorted(prop for prop in REQUIRED_CUSTOM_PROPERTIES if prop not in css)
    missing_selectors = sorted(selector for selector in REQUIRED_SELECTOR_FRAGMENTS if selector not in css)

    assert not missing_properties, f"Missing required CSS properties: {missing_properties}"
    assert not missing_selectors, f"Missing required CSS selectors/states: {missing_selectors}"


def test_foundation_selectors_have_explicit_owner_files() -> None:
    tokens = TOKENS_STYLE_PATH.read_text(encoding="utf-8")
    base = BASE_STYLE_PATH.read_text(encoding="utf-8")
    controls = CONTROLS_STYLE_PATH.read_text(encoding="utf-8")
    surfaces = SURFACES_STYLE_PATH.read_text(encoding="utf-8")

    assert ":root" in tokens and "--bg-root" in tokens
    assert "html," in base and "body" in base and "[hidden]" in base
    assert ".ui-button" in controls and "input:not(" in controls
    assert ".glass-panel" in surfaces and ".ui-badge" in surfaces


def test_foundation_styles_load_before_transitional_feature_layers() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    ordered_paths = (
        "./css/tokens.css",
        "./css/base.css",
        "./css/components/controls.css",
        "./css/components/surfaces.css",
        "./css/style.css",
        "./css/main-screen.css",
    )

    positions = [index.index(path) for path in ordered_paths]
    assert positions == sorted(positions)


def test_workspace_breakpoints_match_javascript_modes() -> None:
    workspace_css = WORKSPACE_STYLE_PATH.read_text(encoding="utf-8")
    ui_js = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")

    assert "@media (max-width: 1080px)" in workspace_css
    assert "@media (max-width: 720px)" in workspace_css
    assert "width <= 720 ? 'mobile'" in ui_js
    assert "width <= 1080 ? 'tablet'" in ui_js


def test_service_worker_precaches_all_runtime_style_layers() -> None:
    service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")

    for path in (
        "css/tokens.css",
        "css/base.css",
        "css/components/controls.css",
        "css/components/surfaces.css",
        "css/style.css",
        "css/main-screen.css",
    ):
        assert f"'{path}'" in service_worker
    assert "2026-07-17-v12-c2-compact-timeline" in service_worker
