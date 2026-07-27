#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import ast
import subprocess
import sys
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("RELEASE_CHECK_ROOT", REPO_ROOT)).resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    from scripts.semantic_data_gate import (  # noqa: E402
        SEMANTIC_WARNING_BUDGETS,
        SemanticGateError,
        validate_semantic_release,
    )
except ModuleNotFoundError:  # Direct execution with RELEASE_CHECK_ROOT fixture.
    from semantic_data_gate import (  # type: ignore[no-redef]  # noqa: E402
        SEMANTIC_WARNING_BUDGETS,
        SemanticGateError,
        validate_semantic_release,
    )
try:
    from scripts.content_profile import ContentProfileError, validate_checked_in_profile  # noqa: E402
except ModuleNotFoundError:  # Direct execution with RELEASE_CHECK_ROOT fixture.
    from content_profile import ContentProfileError, validate_checked_in_profile  # type: ignore[no-redef]  # noqa: E402
BEHAVIORAL_PWA_TEST_PATH = REPO_ROOT / "tests" / "test_sw_fetch_behavior.py"
DEV_LIKE_ENVS = {"development", "dev", "testing", "test", "local"}
PUBLIC_RUNTIME_DATA_ASSETS = {
    "data/features.geojson",
    "data/layers.json",
    "data/relations.json",
}

MAX_EXPECTED_FALLBACK_WARNINGS = 0
MAX_DATA_QUALITY_WARNINGS = sum(SEMANTIC_WARNING_BUDGETS.values())


class CheckFailed(Exception):
    pass


def fail(message: str) -> None:
    raise CheckFailed(message)


def _normalized_runtime_env() -> str:
    return (os.environ.get("APP_ENV") or os.environ.get("ENV") or "development").strip().lower()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.as_posix()} is invalid JSON: {exc}")


def _is_uuid_v4(value: object) -> bool:
    try:
        parsed = uuid.UUID(str(value).strip())
    except (ValueError, TypeError, AttributeError):
        return False
    return parsed.version == 4 and parsed.variant == uuid.RFC_4122


def check_data_layer() -> None:
    features_json_path = ROOT / "data/features.json"
    if not features_json_path.exists():
        fail("data/features.json is missing")
    features_json_payload = read_json(features_json_path)
    if not isinstance(features_json_payload, list):
        fail("data/features.json must be an array")

    features_path = ROOT / "data/features.geojson"
    if not features_path.exists():
        fail("data/features.geojson is missing")

    features_payload = read_json(features_path)
    features = features_payload.get("features") if isinstance(features_payload, dict) else None
    if not isinstance(features, list):
        fail("data/features.geojson has invalid features array")
    if len(features) == 0:
        fail("features.geojson is empty")
    if len(features_json_payload) != len(features):
        fail(
            "records mismatch: "
            f"records_features_json={len(features_json_payload)}, records_geojson={len(features)}"
        )

    canonical_ids: set[str] = set()
    source_record_aliases: dict[str, str] = {}
    feature_legacy_ids: dict[str, set[str]] = {}
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            fail(f"features.geojson feature[{index}] must be an object")
        canonical_id = str(feature.get("id") or "").strip()
        if not _is_uuid_v4(canonical_id):
            fail(f"features.geojson feature[{index}].id must be UUID v4")
        if canonical_id in canonical_ids:
            fail(f"features.geojson contains duplicate canonical id: {canonical_id}")
        canonical_ids.add(canonical_id)

        properties = feature.get("properties")
        if not isinstance(properties, dict):
            fail(f"features.geojson feature[{index}].properties must be an object")
        if properties.get("id") != canonical_id or properties.get("canonical_publish_id") != canonical_id:
            fail(f"features.geojson feature[{index}] identity fields must match Feature.id")
        source_record_id = str(properties.get("source_record_id") or "").strip()
        if not source_record_id:
            fail(f"features.geojson feature[{index}].properties.source_record_id is required")
        source_record_aliases[source_record_id] = canonical_id
        legacy_ids = properties.get("legacy_ids")
        if not isinstance(legacy_ids, list) or not all(isinstance(value, str) and value.strip() for value in legacy_ids):
            fail(f"features.geojson feature[{index}].properties.legacy_ids must be a string array")
        feature_legacy_ids[canonical_id] = set(legacy_ids)

    raw_canonical_ids: set[str] = set()
    for index, record in enumerate(features_json_payload):
        if not isinstance(record, dict):
            fail(f"data/features.json record[{index}] must be an object")
        fields = record.get("fields")
        raw_id = fields.get("id") if isinstance(fields, dict) else record.get("id")
        canonical_id = str(raw_id or "").strip()
        if not _is_uuid_v4(canonical_id):
            fail(f"data/features.json record[{index}] canonical id must be UUID v4")
        raw_canonical_ids.add(canonical_id)
    if raw_canonical_ids != canonical_ids:
        fail("data/features.json canonical ids must match features.geojson Feature.id values")

    id_aliases_path = ROOT / "data/id_aliases.json"
    if not id_aliases_path.exists():
        fail("data/id_aliases.json is missing")
    id_aliases_payload = read_json(id_aliases_path)
    if not isinstance(id_aliases_payload, dict) or id_aliases_payload.get("schema_version") != 1:
        fail("data/id_aliases.json must use schema_version 1")
    if id_aliases_payload.get("canonical_format") != "uuid_v4":
        fail("data/id_aliases.json canonical_format must be uuid_v4")
    aliases = id_aliases_payload.get("aliases")
    if not isinstance(aliases, dict):
        fail("data/id_aliases.json aliases must be an object")
    for legacy_id, canonical_id in aliases.items():
        if not isinstance(legacy_id, str) or not legacy_id.strip() or legacy_id == canonical_id:
            fail("data/id_aliases.json contains an invalid legacy id")
        if not _is_uuid_v4(canonical_id) or canonical_id not in canonical_ids:
            fail(f"data/id_aliases.json alias target is not a published UUID v4: {canonical_id}")
        if legacy_id not in feature_legacy_ids.get(canonical_id, set()):
            fail(f"features.geojson legacy_ids missing alias {legacy_id}")
    for source_record_id, canonical_id in source_record_aliases.items():
        if aliases.get(source_record_id) != canonical_id:
            fail(f"data/id_aliases.json missing source record alias {source_record_id}")

    export_meta_path = ROOT / "data/export_meta.json"
    if not export_meta_path.exists():
        fail("data/export_meta.json is missing")

    export_meta = read_json(export_meta_path)
    records_exported = export_meta.get("records_exported") if isinstance(export_meta, dict) else None
    if not isinstance(records_exported, int):
        fail("data/export_meta.json missing integer records_exported")

    if records_exported != len(features):
        fail(
            "records mismatch: "
            f"records_exported={records_exported}, records_geojson={len(features)}"
        )
    if records_exported != len(features_json_payload):
        fail(
            "records mismatch: "
            f"records_exported={records_exported}, records_features_json={len(features_json_payload)}"
        )

    warning_categories = export_meta.get("warning_categories") if isinstance(export_meta, dict) else None
    if not isinstance(warning_categories, dict):
        fail("data/export_meta.json missing warning_categories object")

    expected_fallback = warning_categories.get("expected_fallback", 0)
    data_quality = warning_categories.get("data_quality", 0)
    if not isinstance(expected_fallback, int):
        fail("data/export_meta.json warning_categories.expected_fallback must be integer")
    if not isinstance(data_quality, int):
        fail("data/export_meta.json warning_categories.data_quality must be integer")

    if expected_fallback > MAX_EXPECTED_FALLBACK_WARNINGS:
        fail(
            "expected_fallback warnings exceed threshold "
            f"({expected_fallback} > {MAX_EXPECTED_FALLBACK_WARNINGS})"
        )
    if data_quality > MAX_DATA_QUALITY_WARNINGS:
        fail(
            "data_quality warnings exceed threshold "
            f"({data_quality} > {MAX_DATA_QUALITY_WARNINGS})"
        )

    rejected_path = ROOT / "data/rejected.json"
    if not rejected_path.exists():
        fail("data/rejected.json is missing")
    rejected_payload = read_json(rejected_path)
    if not isinstance(rejected_payload, list):
        fail("data/rejected.json must be an array")

    records_rejected = export_meta.get("records_rejected") if isinstance(export_meta, dict) else None
    if records_rejected is not None:
        if not isinstance(records_rejected, int):
            fail("data/export_meta.json records_rejected must be integer")
        if records_rejected != len(rejected_payload):
            fail(
                "records mismatch: "
                f"records_rejected={records_rejected}, rejected_json={len(rejected_payload)}"
            )

    records_total_source = export_meta.get("records_total_source") if isinstance(export_meta, dict) else None
    if records_total_source is not None:
        if not isinstance(records_total_source, int):
            fail("data/export_meta.json records_total_source must be integer")
        expected_total_source = records_exported + (records_rejected if isinstance(records_rejected, int) else len(rejected_payload))
        if records_total_source != expected_total_source:
            fail(
                "records mismatch: "
                f"records_total_source={records_total_source}, records_exported_plus_rejected={expected_total_source}"
            )


def check_backend() -> None:
    env_overrides = {
        "MIGRATION_STARTUP_ROLE": "non-owner",
        "APP_ENV": "testing",
        "AUTH_SECRET_KEY": "release-check-dummy-secret",
    }
    previous_values = {key: os.environ.get(key) for key in env_overrides}
    try:
        for key, value in env_overrides.items():
            os.environ[key] = value
        module = importlib.import_module("app.main")
    except Exception as exc:
        fail(f"failed to import app.main: {exc}")
    finally:
        for key, previous in previous_values.items():
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous

    app = getattr(module, "app", None)
    if app is None:
        fail("app.main:app is missing")


def check_semantic_data() -> None:
    try:
        summary = validate_semantic_release(ROOT)
    except SemanticGateError as exc:
        fail(str(exc))
    print(
        "[INFO] Semantic data: "
        f"status={summary['status']} features={summary['features']} "
        f"layers={summary['layers']} sources={summary['sources']} "
        f"media={summary['media']} relations={summary['relations']} "
        f"warnings={summary['warnings']}"
    )


def check_content_profile() -> None:
    try:
        profile = validate_checked_in_profile(ROOT)
    except ContentProfileError as exc:
        fail(str(exc))
    actual = profile["actual"]
    readiness = profile["readiness"]
    print(
        "[INFO] Content profile: "
        f"status={readiness['status']} "
        f"features={actual['features']} "
        f"cohorts={actual['comparison_cohorts']} "
        f"relations={actual['reviewed_relations']} "
        f"media={actual['primary_media_coverage']['ratio']}"
    )


def check_frontend() -> None:
    data_js = ROOT / "js/data.js"
    if not data_js.exists():
        fail("js/data.js is missing")

    text = data_js.read_text(encoding="utf-8").lower()
    has_canonical_data_ref = "/data/" in text or "data/" in text
    if not has_canonical_data_ref:
        fail('js/data.js must reference canonical "/data/" source')

    if "/api/map/feed" not in text:
        return

    explicit_substitution_markers = (
        "fallbacktomapfeed",
        "loadmapfeedonerror",
        "retrywithruntimefeed",
    )
    for marker in explicit_substitution_markers:
        if marker in text:
            fail(f'js/data.js contains fallback marker: "{marker}"')

    substitution_words = (
        "fallback",
        "onerror",
        "catch",
        "retry",
        "alternate",
        "backup",
        "if fail",
        "if error",
    )

    for match in re.finditer(r"/api/map/feed", text):
        start = max(0, match.start() - 240)
        end = min(len(text), match.end() + 240)
        window = text[start:end]
        has_data_ref_in_window = "/data/" in window or "data/" in window
        if has_data_ref_in_window and any(word in window for word in substitution_words):
            fail("js/data.js contains suspicious /data/* -> /api/map/feed fallback pattern")
        if has_data_ref_in_window and re.search(r"(\|\||\?\?|:).{0,80}/api/map/feed|/api/map/feed.{0,80}(\|\||\?\?|:)", window):
            fail("js/data.js contains interchangeable source pattern with /api/map/feed")

    uploads_js = ROOT / "js/uploads.js"
    if uploads_js.exists():
        uploads_text = uploads_js.read_text(encoding="utf-8")
        if re.search(r"/api/uploads/[\"'`$]", uploads_text):
            fail("js/uploads.js contains legacy /api/uploads/{filename} assumption")


def check_pwa() -> None:
    sw_path = ROOT / "sw.js"
    if not sw_path.exists():
        fail("sw.js is missing")

    sw_text = sw_path.read_text(encoding="utf-8")
    sw_text_lower = sw_text.lower()

    has_private_scope = (
        "startswith('api/')" in sw_text_lower
        or 'startswith("api/")' in sw_text_lower
        or "startswith('/api/')" in sw_text_lower
        or 'startswith("/api/")' in sw_text_lower
    )
    if not has_private_scope:
        private_tokens = ("api/auth", "api/drafts", "api/me", "api/uploads", "api/moderation")
        has_private_scope = any(token in sw_text_lower for token in private_tokens)
    if not has_private_scope:
        fail("sw.js missing private/api request scope in bypass classifier")

    private_guard = re.search(
        r"if\s*\(\s*isprivateapirequest\s*\)\s*\{[\s\S]{0,500}?event\.respondwith\(fetch\(request\)\)[\s\S]{0,200}?return\s*;",
        sw_text,
        flags=re.IGNORECASE,
    )
    if private_guard is None:
        fail("sw.js missing explicit network-only bypass for private/auth requests")

    forbidden_cache_patterns = [
        r"cache\.put\([^)]*/api/auth",
        r"cache\.put\([^)]*/api/drafts",
    ]
    for pattern in forbidden_cache_patterns:
        if re.search(pattern, sw_text_lower):
            fail("sw.js contains explicit cache.put for private/auth route")


def check_pwa_behavioral() -> None:
    if not BEHAVIORAL_PWA_TEST_PATH.exists():
        fail("missing behavioral PWA verification test: tests/test_sw_fetch_behavior.py")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(BEHAVIORAL_PWA_TEST_PATH), "-q"],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        details: list[str] = [
            "PWA behavioral verification failed (tests/test_sw_fetch_behavior.py). Release is blocked."
        ]
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if stdout:
            details.append(f"--- subprocess stdout ---\n{stdout}")
        if stderr:
            details.append(f"--- subprocess stderr ---\n{stderr}")
        fail("\n".join(details))


def check_governance() -> None:
    export_script = ROOT / "scripts/export_airtable.py"
    if not export_script.exists():
        fail("scripts/export_airtable.py is missing")

    runtime_roots = [ROOT / "app", ROOT / "js"]
    for runtime_root in runtime_roots:
        if not runtime_root.exists():
            continue
        for path in runtime_root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".js"}:
                continue
            rel = path.relative_to(ROOT)
            if "moderation" in rel.parts:
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")
            has_publish_call = False
            if path.suffix == ".py":
                has_publish_call = _python_has_publish_call(text)
            elif path.suffix == ".js":
                has_publish_call = _js_has_publish_call(text)
            if has_publish_call:
                fail(f'direct runtime publish found outside moderation: "{rel.as_posix()}"')


def check_release_docs_drift() -> None:
    index_path = ROOT / "index.html"
    if not index_path.exists():
        fail("index.html is missing")

    pages_workflow_path = ROOT / ".github" / "workflows" / "pages.yml"
    if not pages_workflow_path.exists():
        fail(".github/workflows/pages.yml is missing")

    referenced_assets = _extract_local_index_assets(index_path.read_text(encoding="utf-8"))
    required_files = _parse_pages_required_files(pages_workflow_path.read_text(encoding="utf-8"))

    for asset in sorted(referenced_assets):
        if not (ROOT / asset).exists():
            fail(f'index.html references missing local asset: "{asset}"')
        if asset not in required_files:
            fail(f'pages artifact required_files missing referenced asset: "{asset}"')

    for asset in sorted(PUBLIC_RUNTIME_DATA_ASSETS):
        if not (ROOT / asset).exists():
            fail(f'public runtime data asset is missing: "{asset}"')
        if asset not in required_files:
            fail(f'pages artifact required_files missing runtime data asset: "{asset}"')

    _check_archive_reference_status_headers()
    _check_canonical_smoke_evidence_references()


def _extract_local_index_assets(index_html: str) -> set[str]:
    refs: set[str] = set()
    pattern = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", flags=re.IGNORECASE)
    for raw_ref in pattern.findall(index_html):
        ref = raw_ref.strip()
        if not ref:
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", ref):
            continue
        normalized = ref[2:] if ref.startswith("./") else ref
        if normalized.startswith("/"):
            continue
        if normalized.startswith("css/") or normalized.startswith("js/"):
            refs.add(normalized)
    return refs


def _parse_pages_required_files(workflow_text: str) -> set[str]:
    block = re.search(r"required_files=\(\s*([\s\S]*?)\s*\)", workflow_text)
    if block is None:
        fail(".github/workflows/pages.yml missing required_files=(...) block")
    entries = re.findall(r'"([^"]+)"', block.group(1))
    if not entries:
        fail(".github/workflows/pages.yml required_files list is empty")
    return set(entries)


def _check_archive_reference_status_headers() -> None:
    targets = [ROOT / "docs" / "archive", ROOT / "docs" / "reference"]
    for root in targets:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:80]
            for line in lines:
                normalized = re.sub(r"[*_`]", "", line).strip().lower()
                if normalized.startswith("- статус:") and "active" in normalized:
                    rel = path.relative_to(ROOT).as_posix()
                    fail(f'archive/reference document cannot be active: "{rel}"')


def _check_canonical_smoke_evidence_references() -> None:
    deprecated_path = "docs/MANUAL_SMOKE_EVIDENCE_2026-04-11.md"
    docs_root = ROOT / "docs"
    if not docs_root.exists():
        return
    for path in docs_root.rglob("*.md"):
        rel = path.relative_to(ROOT)
        if "archive" in rel.parts or "audits" in rel.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if deprecated_path in text:
            fail(f'canonical docs reference deprecated smoke evidence path: "{rel.as_posix()}"')


def _python_has_publish_call(text: str) -> bool:
    try:
        parsed = ast.parse(text)
    except SyntaxError:
        return bool(re.search(r"\bpublish\s*\(", text))

    for node in ast.walk(parsed):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "publish":
            return True
        if isinstance(func, ast.Attribute) and func.attr == "publish":
            return True
    return False


def _js_has_publish_call(text: str) -> bool:
    sanitized = _strip_js_comments_and_strings(text)
    return bool(re.search(r"\bpublish\s*\(", sanitized))


def _strip_js_comments_and_strings(text: str) -> str:
    without_block_comments = re.sub(r"/\*[\s\S]*?\*/", "", text)
    without_line_comments = re.sub(r"(^|[^:])//.*?$", r"\1", without_block_comments, flags=re.MULTILINE)
    without_double_quotes = re.sub(r'"(?:\\.|[^"\\])*"', '""', without_line_comments)
    without_single_quotes = re.sub(r"'(?:\\.|[^'\\])*'", "''", without_double_quotes)
    without_template_strings = re.sub(r"`(?:\\.|[^`\\])*`", "``", without_single_quotes)
    return without_template_strings


def check_runtime_deployment() -> None:
    app_env = _normalized_runtime_env()
    auth_secret_key = os.environ.get("AUTH_SECRET_KEY", "").strip()
    session_backend = os.environ.get("AUTH_SESSION_BACKEND", "memory").strip().lower()

    if app_env not in DEV_LIKE_ENVS and not auth_secret_key:
        fail("AUTH_SECRET_KEY is required outside development/testing/local aliases")

    if session_backend not in {"memory", "redis"}:
        fail('AUTH_SESSION_BACKEND must be "memory" or "redis"')

    if session_backend == "redis" and not os.environ.get("REDIS_URL", "").strip():
        fail("REDIS_URL is required when AUTH_SESSION_BACKEND=redis")

    if session_backend == "memory":
        if app_env not in DEV_LIKE_ENVS:
            fail("AUTH_SESSION_BACKEND=memory is allowed only in development/testing/local aliases")
        print("[WARN] Runtime/deployment: memory session backend -> single-node baseline only")


def run_check(name: str, func) -> None:
    try:
        func()
    except CheckFailed as exc:
        print(f"[FAIL] {name}: {exc}")
        sys.exit(1)
    print(f"[PASS] {name}")


def main() -> None:
    run_check("Data layer", check_data_layer)
    run_check("Semantic data", check_semantic_data)
    run_check("Content profile", check_content_profile)
    run_check("Backend", check_backend)
    run_check("Runtime/deployment", check_runtime_deployment)
    run_check("Frontend", check_frontend)
    run_check("PWA", check_pwa)
    run_check("PWA behavioral", check_pwa_behavioral)
    run_check("Governance", check_governance)
    run_check("Release/docs drift", check_release_docs_drift)


if __name__ == "__main__":
    main()
