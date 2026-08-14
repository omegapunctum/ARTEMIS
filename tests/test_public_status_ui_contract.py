import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_pwa_banner_actions_receive_pointer_events_and_dismiss_for_session() -> None:
    css = _read("css/style.css")
    pwa = _read("js/pwa.js")

    assert re.search(
        r"\.app-system-message,\s*\.app-system-banner\s*\{\s*pointer-events:\s*auto;",
        css,
    )
    assert "INSTALL_HINT_DISMISSED_SESSION_KEY" in pwa
    assert "window.sessionStorage.setItem(INSTALL_HINT_DISMISSED_SESSION_KEY, '1')" in pwa
    assert "{ label: 'Закрыть', onClick: dismissInstallHint }" in pwa


def test_ready_status_panel_is_hidden_outside_debug_mode() -> None:
    index = _read("index.html")
    ui = _read("js/ui.js")

    assert "if (statusPanel) statusPanel.hidden = !visible;" in index
    assert "visible: DEBUG_TELEMETRY_STATUS" in index
    assert "DEBUG_TELEMETRY_STATUS ? runtimeReadiness.readyMessage : ''" in index
    assert "if (!isDebugTelemetryMode()) {" in ui
    assert "elements.statusMessage.textContent = '';" in ui
