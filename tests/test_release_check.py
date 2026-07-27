import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import release_check
from scripts.content_profile import build_content_profile_from_root


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "release_check.py"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_fixture(
    root: Path,
    *,
    empty_features: bool = False,
    frontend_fallback: bool = False,
    include_sw: bool = True,
    unsafe_sw: bool = False,
    expected_fallback_warnings: int = 0,
    data_quality_warnings: int = 0,
    records_total_source: int | None = None,
    records_rejected: int | None = None,
    rejected_items: list[dict] | None = None,
) -> None:
    canonical_id = "550e8400-e29b-41d4-a716-446655440000"
    source_id = "src_fixture"
    media_id = "media_fixture"
    media_asset_url = "https://example.com/fixture.jpg"
    features = [] if empty_features else [
        {
            "type": "Feature",
            "id": canonical_id,
            "geometry": {"type": "Point", "coordinates": [10.0, 20.0]},
            "properties": {
                "id": canonical_id,
                "canonical_publish_id": canonical_id,
                "source_record_id": "recFixture",
                "legacy_ids": ["recFixture"],
                "layer_id": "fixture_layer",
                "layer_type": "architecture",
                "date_start": "2000",
                "date_end": "2001",
                "image_url": media_asset_url,
                "source_ids": [source_id],
                "source_refs": [
                    {"source_id": source_id, "roles": ["general_reference"], "is_primary": True}
                ],
                "media_ids": [media_id],
                "media_refs": [
                    {"media_id": media_id, "display_role": "primary", "sort_order": 1}
                ],
                "relation_ids": [],
                "coordinates_confidence": "approximate",
                "tags": ["fixture"],
                "validated": True,
            },
        }
    ]
    rejected_payload = rejected_items or []
    resolved_records_rejected = len(rejected_payload) if records_rejected is None else records_rejected
    resolved_records_total_source = (
        len(features) + resolved_records_rejected
        if records_total_source is None
        else records_total_source
    )
    _write(
        root / "data" / "features.geojson",
        json.dumps({"type": "FeatureCollection", "features": features}),
    )
    _write(
        root / "data" / "features.json",
        json.dumps([{"id": "recFixture", "fields": {"id": canonical_id, "validated": True}} for _ in features]),
    )
    _write(
        root / "data" / "id_aliases.json",
        json.dumps(
            {
                "schema_version": 1,
                "canonical_format": "uuid_v4",
                "aliases": {} if empty_features else {"recFixture": canonical_id},
            }
        ),
    )
    _write(
        root / "data" / "layers.json",
        json.dumps(
            [] if empty_features else [
                {
                    "layer_id": "fixture_layer",
                    "name_ru": "Тестовый слой",
                    "name_en": "Fixture layer",
                    "color_hex": "#112233",
                    "icon": "fixture",
                    "is_enabled": True,
                }
            ]
        ),
    )
    _write(
        root / "data" / "sources.json",
        json.dumps(
            [] if empty_features else [
                {
                    "id": source_id,
                    "source_record_id": "recSourceFixture",
                    "url": "https://example.com/source",
                    "bibliographic_locator": None,
                    "title": "Fixture source",
                    "author_or_organization": "Fixture organization",
                    "source_type": "institutional",
                    "review_status": "reviewed",
                }
            ]
        ),
    )
    _write(
        root / "data" / "media.json",
        json.dumps(
            [] if empty_features else [
                {
                    "id": media_id,
                    "source_record_id": "recMediaFixture",
                    "asset_url": media_asset_url,
                    "source_page_url": "https://example.com/media",
                    "creator": "Fixture creator",
                    "license": "CC BY",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution_text": "Fixture creator, CC BY 4.0",
                    "media_type": "image",
                    "review_status": "reviewed",
                }
            ]
        ),
    )
    _write(root / "data" / "relations.json", "[]")
    _write(
        root / "data" / "validation_report.json",
        json.dumps(
            {
                "schema_version": 2,
                "status": "ready",
                "total_records": len(features),
                "valid_records": len(features),
                "skipped_records": resolved_records_rejected,
                "blocking_errors_count": 0,
                "warnings_count": 0,
                "blocking_errors": [],
                "errors_count": 0,
                "warnings": [],
                "errors": [],
            }
        ),
    )
    _write(
        root / "data" / "export_meta.json",
        json.dumps(
            {
                "records_exported": len(features),
                "records_rejected": resolved_records_rejected,
                "records_total_source": resolved_records_total_source,
                "layers_total_source": 0 if empty_features else 1,
                "layers_published": 0 if empty_features else 1,
                "enabled_empty_layers_excluded": 0,
                "sources_total_source": len(features),
                "sources_reviewed": len(features),
                "media_total_source": len(features),
                "media_reviewed": len(features),
                "relations_total_source": 0,
                "relations_reviewed": 0,
                "errors": 0,
                "warnings": 0,
                "warning_stats": {},
                "warning_categories": {
                    "expected_fallback": expected_fallback_warnings,
                    "data_quality": data_quality_warnings,
                },
                "semantic_gate": {"status": "ready", "blocking_errors": 0, "warnings": 0},
            }
        ),
    )
    _write(root / "data" / "rejected.json", json.dumps(rejected_payload))
    _write(
        root / "data" / "content_profile.json",
        json.dumps(build_content_profile_from_root(root)),
    )

    if frontend_fallback:
        data_js = """
const primary = 'data/features.geojson';
function fallbackToMapFeed() {
  return fetch('/api/map/feed');
}
""".strip()
    else:
        data_js = """
const primary = 'data/features.geojson';
const auxiliary = '/api/map/feed';
export async function loadPrimary() {
  return fetch(primary);
}
""".strip()
    _write(root / "js" / "data.js", data_js)

    if include_sw:
        if unsafe_sw:
            _write(
                root / "sw.js",
                """
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/auth')) {
    event.respondWith(caches.open('runtime').then((cache) => cache.match(event.request)));
    return;
  }
  event.respondWith(fetch(event.request));
});
""".strip()
                + "\n",
            )
        else:
            _write(
                root / "sw.js",
                """
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  const isPrivateApiRequest = url.pathname.startsWith('/api/');
  if (isPrivateApiRequest) {
    event.respondWith(fetch(request));
    return;
  }
  event.respondWith(fetch(request));
});
""".strip()
                + "\n",
            )

    _write(root / "app" / "__init__.py", "")
    _write(root / "app" / "main.py", "app = object()\n")
    _write(root / "scripts" / "export_airtable.py", "# fixture export script\n")
    _write(
        root / "index.html",
        """
<!doctype html>
<html>
  <head>
    <link rel="stylesheet" href="css/tokens.css" />
    <link rel="stylesheet" href="css/base.css" />
    <link rel="stylesheet" href="css/components/controls.css" />
    <link rel="stylesheet" href="css/components/surfaces.css" />
    <link rel="stylesheet" href="css/style.css" />
    <link rel="stylesheet" href="./css/main-screen.css" />
  </head>
  <body>
    <script src="js/data.js"></script>
  </body>
</html>
""".strip()
        + "\n",
    )
    _write(root / "css" / "tokens.css", ":root { --color: #000; }\n")
    _write(root / "css" / "base.css", "body { color: var(--color); }\n")
    _write(root / "css" / "components" / "controls.css", "button { color: inherit; }\n")
    _write(root / "css" / "components" / "surfaces.css", ".panel { display: block; }\n")
    _write(root / "css" / "style.css", ".feature { display: block; }\n")
    _write(root / "css" / "main-screen.css", ".main-screen { display: block; }\n")
    _write(
        root / ".github" / "workflows" / "pages.yml",
        """
name: pages
jobs:
  deploy:
    steps:
      - name: Prepare pages artifact
        run: |
          required_files=(
            "index.html"
            "css/tokens.css"
            "css/base.css"
            "css/components/controls.css"
            "css/components/surfaces.css"
            "css/style.css"
            "css/main-screen.css"
            "js/data.js"
            "data/features.geojson"
            "data/layers.json"
            "data/relations.json"
          )
""".strip()
        + "\n",
    )
    _write(
        root / "docs" / "CONTROLLED_RELEASE_DECISION.md",
        """
# Controlled release decision

## Статус документа
- Статус: active

Актуальные артефакты указаны в текущем release пакете.
""".strip()
        + "\n",
    )
    _write(
        root / "docs" / "archive" / "old.md",
        """
# old
- Статус: archived
Историческая ссылка: docs/MANUAL_SMOKE_EVIDENCE_2026-04-11.md
""".strip()
        + "\n",
    )
    _write(
        root / "docs" / "reference" / "info.md",
        """
# info
- Статус: reference
""".strip()
        + "\n",
    )
    _write(
        root / "docs" / "audits" / "note.md",
        """
# note
Историческая ссылка: docs/MANUAL_SMOKE_EVIDENCE_2026-04-11.md
""".strip()
        + "\n",
    )


def _run_release_check(
    root: Path,
    *,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["RELEASE_CHECK_ROOT"] = str(root)
    env.pop("PYTHONPATH", None)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_release_check_happy_path(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] Data layer" in result.stdout
    assert "[PASS] Semantic data" in result.stdout
    assert "[PASS] Content profile" in result.stdout
    assert "[PASS] Backend" in result.stdout
    assert "[PASS] Frontend" in result.stdout
    assert "[PASS] PWA" in result.stdout
    assert "[PASS] Governance" in result.stdout
    assert "[PASS] Release/docs drift" in result.stdout


def test_release_check_fails_on_empty_geojson(tmp_path: Path) -> None:
    _build_fixture(tmp_path, empty_features=True)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: features.geojson is empty" in result.stdout


def test_release_check_fails_when_features_json_missing(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    (tmp_path / "data" / "features.json").unlink()
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: data/features.json is missing" in result.stdout


def test_release_check_fails_when_id_aliases_missing(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    (tmp_path / "data" / "id_aliases.json").unlink()
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: data/id_aliases.json is missing" in result.stdout


def test_release_check_fails_when_canonical_id_is_not_uuid_v4(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "data" / "features.geojson",
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "recFixture",
                        "geometry": None,
                        "properties": {
                            "id": "recFixture",
                            "canonical_publish_id": "recFixture",
                            "source_record_id": "recFixture",
                            "legacy_ids": [],
                        },
                    }
                ],
            }
        ),
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "feature[0].id must be UUID v4" in result.stdout


def test_release_check_fails_on_blocking_semantic_error(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    report_path = tmp_path / "data" / "validation_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    error = {
        "id": "recFixture",
        "record_id": "recFixture",
        "field": "validated",
        "reason": "unreviewed_active_feature",
        "severity": "critical",
        "error": "unreviewed_active_feature",
    }
    report.update(
        {
            "status": "blocked",
            "blocking_errors_count": 1,
            "blocking_errors": [error],
            "errors_count": 1,
            "errors": [error],
        }
    )
    _write(report_path, json.dumps(report))

    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Semantic data: semantic validation has 1 blocking error(s)" in result.stdout


def test_release_check_fails_on_html_page_used_as_media_asset(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    media_path = tmp_path / "data" / "media.json"
    media = json.loads(media_path.read_text(encoding="utf-8"))
    media[0]["asset_url"] = "https://commons.wikimedia.org/wiki/File:Fixture.jpg"
    _write(media_path, json.dumps(media))

    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Semantic data: Media media_fixture has invalid direct asset_url" in result.stdout


def test_release_check_fails_on_published_enabled_empty_layer(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    layers_path = tmp_path / "data" / "layers.json"
    layers = json.loads(layers_path.read_text(encoding="utf-8"))
    layers.append(
        {
            "layer_id": "empty_layer",
            "name_ru": "Пустой слой",
            "name_en": "Empty layer",
            "color_hex": "#445566",
            "icon": "empty",
            "is_enabled": True,
        }
    )
    _write(layers_path, json.dumps(layers))

    meta_path = tmp_path / "data" / "export_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["layers_total_source"] = 2
    meta["layers_published"] = 2
    _write(meta_path, json.dumps(meta))

    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Semantic data: published enabled Layer empty_layer is empty" in result.stdout


def test_release_check_fails_on_frontend_fallback_pattern(tmp_path: Path) -> None:
    _build_fixture(tmp_path, frontend_fallback=True)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Frontend:" in result.stdout
    assert "js/data.js contains fallback marker" in result.stdout
    assert '"fallbacktomapfeed"' in result.stdout


def test_release_check_fails_when_sw_missing(tmp_path: Path) -> None:
    _build_fixture(tmp_path, include_sw=False)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] PWA: sw.js is missing" in result.stdout


def test_release_check_fails_when_private_requests_are_cache_eligible(tmp_path: Path) -> None:
    _build_fixture(tmp_path, unsafe_sw=True)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] PWA:" in result.stdout


def test_release_check_fails_when_expected_fallback_exceeds_threshold(tmp_path: Path) -> None:
    _build_fixture(tmp_path, expected_fallback_warnings=11)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: expected_fallback warnings exceed threshold (11 > 0)" in result.stdout


def test_release_check_fails_when_data_quality_exceeds_threshold(tmp_path: Path) -> None:
    _build_fixture(tmp_path, data_quality_warnings=15)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: data_quality warnings exceed threshold (15 > 14)" in result.stdout


def test_release_check_fails_on_legacy_upload_path_assumption(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "js" / "uploads.js",
        "const legacy = `/api/uploads/${filename}`;\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Frontend: js/uploads.js contains legacy /api/uploads/{filename} assumption" in result.stdout


def test_release_check_fails_on_runtime_publish_call_outside_moderation_python(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "app" / "drafts" / "routes.py",
        "def run_publish():\n    publish()\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert '[FAIL] Governance: direct runtime publish found outside moderation: "app/drafts/routes.py"' in result.stdout


def test_release_check_ignores_publish_tokens_inside_comments_and_strings(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "app" / "drafts" / "routes.py",
        "def no_call():\n    note = 'publish() in string'\n    # publish() in comment\n    return note\n",
    )
    _write(
        tmp_path / "js" / "runtime.js",
        "const a = 'publish()';\n// publish()\nconst b = `publish()`;\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] Governance" in result.stdout


def test_release_check_fails_on_runtime_publish_call_outside_moderation_js(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "js" / "runtime.js",
        "const gate = { publish: () => {} };\ngate.publish();\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert '[FAIL] Governance: direct runtime publish found outside moderation: "js/runtime.js"' in result.stdout


def test_release_check_fails_when_records_rejected_mismatches_rejected_json(tmp_path: Path) -> None:
    _build_fixture(tmp_path, records_rejected=2, rejected_items=[{"id": "r1"}])
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: records mismatch:" in result.stdout
    assert "records_rejected=2, rejected_json=1" in result.stdout


def test_release_check_fails_when_records_total_source_arithmetic_mismatch(tmp_path: Path) -> None:
    _build_fixture(tmp_path, records_total_source=99)
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Data layer: records mismatch:" in result.stdout
    assert "records_total_source=99, records_exported_plus_rejected=1" in result.stdout


def test_release_check_fails_without_auth_secret_key_outside_dev_test(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "APP_ENV": "prod",
            "AUTH_SECRET_KEY": "",
        },
    )

    assert result.returncode == 1
    assert "[FAIL] Runtime/deployment: AUTH_SECRET_KEY is required outside development/testing/local aliases" in result.stdout


def test_release_check_allows_development_alias_without_auth_secret_key(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "APP_ENV": "development",
            "AUTH_SECRET_KEY": "",
        },
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] Runtime/deployment" in result.stdout


def test_release_check_fails_when_redis_backend_without_redis_url(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "APP_ENV": "prod",
            "AUTH_SECRET_KEY": "super-secret",
            "AUTH_SESSION_BACKEND": "redis",
            "REDIS_URL": "",
        },
    )

    assert result.returncode == 1
    assert "[FAIL] Runtime/deployment: REDIS_URL is required when AUTH_SESSION_BACKEND=redis" in result.stdout


def test_release_check_fails_when_session_backend_invalid(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "AUTH_SESSION_BACKEND": "sqlite",
        },
    )

    assert result.returncode == 1
    assert '[FAIL] Runtime/deployment: AUTH_SESSION_BACKEND must be "memory" or "redis"' in result.stdout


def test_release_check_passes_with_valid_runtime_deployment_config(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "APP_ENV": "prod",
            "AUTH_SECRET_KEY": "super-secret",
            "AUTH_SESSION_BACKEND": "redis",
            "REDIS_URL": "redis://localhost:6379/0",
        },
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] Runtime/deployment" in result.stdout


def test_release_check_warns_for_memory_backend(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "AUTH_SESSION_BACKEND": "memory",
        },
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[WARN] Runtime/deployment: memory session backend -> single-node baseline only" in result.stdout


def test_release_check_fails_for_memory_backend_outside_dev_like_envs(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(
        tmp_path,
        env_overrides={
            "APP_ENV": "prod",
            "AUTH_SECRET_KEY": "super-secret",
            "AUTH_SESSION_BACKEND": "memory",
        },
    )

    assert result.returncode == 1
    assert (
        "[FAIL] Runtime/deployment: AUTH_SESSION_BACKEND=memory is allowed only in development/testing/local aliases"
        in result.stdout
    )


def test_release_check_invokes_pwa_behavioral_pytest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    behavioral_test = tmp_path / "tests" / "test_sw_fetch_behavior.py"
    _write(behavioral_test, "def test_placeholder():\n    assert True\n")
    monkeypatch.setattr(release_check, "BEHAVIORAL_PWA_TEST_PATH", behavioral_test)

    calls: list[tuple[list[str], str]] = []

    def _fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs.get("cwd", "")))
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(release_check.subprocess, "run", _fake_run)

    release_check.check_pwa_behavioral()

    assert calls, "behavioral PWA subprocess must be invoked"
    cmd, cwd = calls[0]
    assert cmd[0] == sys.executable
    assert cmd[1:3] == ["-m", "pytest"]
    assert str(behavioral_test) in cmd
    assert cwd == str(REPO_ROOT)


def test_release_check_fails_when_behavioral_pwa_verification_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    behavioral_test = tmp_path / "tests" / "test_sw_fetch_behavior.py"
    _write(behavioral_test, "def test_placeholder():\n    assert True\n")
    monkeypatch.setattr(release_check, "BEHAVIORAL_PWA_TEST_PATH", behavioral_test)

    def _fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(cmd, 1, stdout="failure", stderr="")

    monkeypatch.setattr(release_check.subprocess, "run", _fake_run)

    with pytest.raises(release_check.CheckFailed, match="PWA behavioral verification failed"):
        release_check.check_pwa_behavioral()


def test_check_backend_uses_safe_env_and_restores(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MIGRATION_STARTUP_ROLE", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("AUTH_SECRET_KEY", raising=False)

    captured: dict[str, str] = {}

    class _Module:
        app = object()

    def _fake_import(module_name: str):
        captured["module_name"] = module_name
        captured["migration_role"] = os.environ.get("MIGRATION_STARTUP_ROLE", "")
        captured["app_env"] = os.environ.get("APP_ENV", "")
        captured["auth_secret_key"] = os.environ.get("AUTH_SECRET_KEY", "")
        return _Module()

    monkeypatch.setattr(release_check.importlib, "import_module", _fake_import)

    release_check.check_backend()

    assert captured["module_name"] == "app.main"
    assert captured["migration_role"] == "non-owner"
    assert captured["app_env"] == "testing"
    assert captured["auth_secret_key"] == "release-check-dummy-secret"
    assert "MIGRATION_STARTUP_ROLE" not in os.environ
    assert "APP_ENV" not in os.environ
    assert "AUTH_SECRET_KEY" not in os.environ


def test_release_docs_drift_flags_main_screen_css_missing_from_pages_required_files(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / ".github" / "workflows" / "pages.yml",
        """
name: pages
jobs:
  deploy:
    steps:
      - name: Prepare pages artifact
        run: |
          required_files=(
            "index.html"
            "css/tokens.css"
            "css/base.css"
            "css/components/controls.css"
            "css/components/surfaces.css"
            "css/style.css"
            "js/data.js"
          )
""".strip()
        + "\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert '[FAIL] Release/docs drift: pages artifact required_files missing referenced asset: "css/main-screen.css"' in result.stdout


def test_release_docs_drift_flags_referenced_js_missing_from_pages_required_files(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "index.html",
        """
<!doctype html>
<html>
  <head><link rel="stylesheet" href="css/style.css" /></head>
  <body>
    <script src="js/data.js"></script>
    <script src="./js/map.js"></script>
  </body>
</html>
""".strip()
        + "\n",
    )
    _write(tmp_path / "js" / "map.js", "console.log('map');\n")
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert '[FAIL] Release/docs drift: pages artifact required_files missing referenced asset: "js/map.js"' in result.stdout


def test_release_docs_drift_flags_runtime_relations_missing_from_pages_artifact(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    workflow_path = tmp_path / ".github" / "workflows" / "pages.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace('            "data/relations.json"\n', ""),
        encoding="utf-8",
    )

    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert (
        '[FAIL] Release/docs drift: pages artifact required_files missing runtime data asset: '
        '"data/relations.json"'
    ) in result.stdout


def test_release_docs_drift_fails_when_archive_or_reference_marked_active(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    _write(
        tmp_path / "docs" / "archive" / "old.md",
        """
# old
- Статус: active
""".strip()
        + "\n",
    )
    result = _run_release_check(tmp_path)

    assert result.returncode == 1
    assert '[FAIL] Release/docs drift: archive/reference document cannot be active: "docs/archive/old.md"' in result.stdout


def test_release_docs_drift_allows_historical_mentions_inside_archive_and_audits(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    result = _run_release_check(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] Release/docs drift" in result.stdout
