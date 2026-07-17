from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLE_PATH = ROOT / "css" / "style.css"
WORKSPACE_STYLE_PATH = ROOT / "css" / "main-screen.css"


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
    "--workspace-strip-height",
    "--bottom-panel-height",
    "--map-rail-width",
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


def test_shared_style_system_is_substantive_and_balanced() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")
    without_comments = _strip_css_comments(css)

    # Prevent a missing file or minimal placeholder from passing the release gate.
    assert len(without_comments) > 20_000
    assert without_comments.count("{") == without_comments.count("}")


def test_shared_style_system_exposes_runtime_contract() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")

    missing_properties = sorted(prop for prop in REQUIRED_CUSTOM_PROPERTIES if prop not in css)
    missing_selectors = sorted(selector for selector in REQUIRED_SELECTOR_FRAGMENTS if selector not in css)

    assert not missing_properties, f"Missing required CSS properties: {missing_properties}"
    assert not missing_selectors, f"Missing required CSS selectors/states: {missing_selectors}"


def test_workspace_breakpoints_match_javascript_modes() -> None:
    workspace_css = WORKSPACE_STYLE_PATH.read_text(encoding="utf-8")
    ui_js = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")

    assert "@media (max-width: 1080px)" in workspace_css
    assert "@media (max-width: 720px)" in workspace_css
    assert "width <= 720 ? 'mobile'" in ui_js
    assert "width <= 1080 ? 'tablet'" in ui_js


def test_service_worker_precaches_both_style_layers() -> None:
    service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")

    assert "'css/style.css'" in service_worker
    assert "'css/main-screen.css'" in service_worker
    assert "2026-07-16-v9-relations" in service_worker
