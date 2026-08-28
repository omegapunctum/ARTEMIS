import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "scripts" / "globe_spike" / "i18n.js"
RUNTIME = ROOT / "scripts" / "globe_spike" / "runtime.js"
TEMPLATE = ROOT / "scripts" / "globe_spike" / "index.html.template"
LANDING = ROOT / "scripts" / "globe_spike" / "root-index.html"


def _catalog() -> dict:
    result = subprocess.run(
        [
            "node",
            "-e",
            (
                "global.window = {};"
                "require('./scripts/globe_spike/i18n.js');"
                "process.stdout.write(JSON.stringify(window.__ARTEMIS_I18N));"
            ),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _placeholders(value: str) -> set[str]:
    return set(re.findall(r"\{([a-zA-Z0-9_]+)\}", value))


def test_catalog_has_complete_deterministic_english_and_russian_messages() -> None:
    catalog = _catalog()
    assert catalog["defaultLocale"] == "en"
    assert catalog["supportedLocales"] == ["en", "ru"]

    english = catalog["messages"]["en"]
    russian = catalog["messages"]["ru"]
    assert set(english) == set(russian)
    assert len(english) >= 80
    assert any("а" <= character.lower() <= "я" for value in russian.values() for character in value)
    for key in english:
        assert _placeholders(english[key]) == _placeholders(russian[key]), key


def test_all_template_and_runtime_translation_keys_exist() -> None:
    catalog = _catalog()
    keys = set(catalog["messages"]["en"])
    template = TEMPLATE.read_text(encoding="utf-8")
    runtime = RUNTIME.read_text(encoding="utf-8")

    template_keys = {
        key
        for key in re.findall(r'data-i18n(?:-aria-label|-title)?="([^"]+)"', template)
        if "{{" not in key
    }
    runtime_keys = set(re.findall(r"\bt\('([^']+)'", runtime))
    assert template_keys <= keys
    assert runtime_keys <= keys
    assert {"previewPublic", "previewGenerated"} <= keys


def test_locale_is_shareable_presentation_state_not_semantic_data() -> None:
    runtime = RUNTIME.read_text(encoding="utf-8")
    landing = LANDING.read_text(encoding="utf-8")
    locale_source = I18N.read_text(encoding="utf-8")

    assert "url.searchParams.set('lang', locale)" in runtime
    assert "url.searchParams.set('time'" in runtime
    assert "url.searchParams.set('layers'" in runtime
    assert "url.searchParams.set('item'" in runtime
    assert 'href="./globe/?lang=ru"' in landing
    assert 'href="./globe/?lang=en"' in landing
    assert "Claims & evidence · original evidence language" in locale_source
    assert "Утверждения и свидетельства · исходный язык материалов" in locale_source
    assert "fixtures/world_slices" not in locale_source
