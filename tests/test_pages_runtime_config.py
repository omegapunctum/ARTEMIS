import json
import subprocess
import textwrap
from pathlib import Path

import pytest

from scripts.generate_pages_runtime_config import normalize_api_base, render_config


ROOT = Path(__file__).resolve().parents[1]


def run_node_json(script: str) -> dict:
    result = subprocess.run(
        ["node", "--input-type=module", "-e", textwrap.dedent(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout.strip())


def test_generator_is_fail_closed_without_api() -> None:
    rendered = render_config("")
    assert "apiBase: \"\"" in rendered
    assert "account: false" in rendered
    assert "slices: false" in rendered


def test_generator_accepts_https_and_loopback_only() -> None:
    assert normalize_api_base("https://api.artemis.example/api/") == "https://api.artemis.example/api"
    assert normalize_api_base("http://127.0.0.1:8001/api") == "http://127.0.0.1:8001/api"
    with pytest.raises(ValueError, match="HTTPS"):
        normalize_api_base("http://api.artemis.example/api")
    with pytest.raises(ValueError, match="/api"):
        normalize_api_base("https://api.artemis.example")


def test_runtime_probe_enables_declared_capabilities_after_health_success() -> None:
    data = run_node_json(
        """
        globalThis.window = {
          ARTEMIS_DEPLOYMENT_CONFIG: {
            apiBase: 'https://api.artemis.example/api',
            capabilities: { account: true, slices: true, stories: false }
          },
          dispatchEvent: () => {},
          setTimeout,
          clearTimeout,
        };
        globalThis.CustomEvent = class { constructor(name, options) { this.name = name; this.detail = options?.detail; } };
        globalThis.fetch = async (url, options) => ({ ok: true, status: 200, url, options });
        await import('./js/runtime-config.js');
        await window.ARTEMIS_RUNTIME_READY;
        console.log(JSON.stringify({
          apiBase: window.ARTEMIS_API_BASE,
          status: window.ARTEMIS_RUNTIME_STATUS.status,
          capabilities: window.ARTEMIS_CAPABILITIES
        }));
        """
    )
    assert data["apiBase"] == "https://api.artemis.example/api"
    assert data["status"] == "available"
    assert data["capabilities"]["backend"] is True
    assert data["capabilities"]["account"] is True
    assert data["capabilities"]["slices"] is True
    assert data["capabilities"]["stories"] is False


def test_runtime_probe_fails_closed_when_api_is_unconfigured() -> None:
    data = run_node_json(
        """
        let fetchCount = 0;
        globalThis.window = {
          ARTEMIS_DEPLOYMENT_CONFIG: { apiBase: '', capabilities: { account: true, slices: true } },
          dispatchEvent: () => {},
          setTimeout,
          clearTimeout,
        };
        globalThis.CustomEvent = class { constructor(name, options) { this.name = name; this.detail = options?.detail; } };
        globalThis.fetch = async () => { fetchCount += 1; throw new Error('must not fetch'); };
        await import('./js/runtime-config.js');
        await window.ARTEMIS_RUNTIME_READY;
        console.log(JSON.stringify({
          fetchCount,
          status: window.ARTEMIS_RUNTIME_STATUS.status,
          capabilities: window.ARTEMIS_CAPABILITIES
        }));
        """
    )
    assert data["fetchCount"] == 0
    assert data["status"] == "unconfigured"
    assert data["capabilities"]["backend"] is False
    assert data["capabilities"]["slices"] is False


def test_auth_resolver_does_not_fall_back_to_static_origin() -> None:
    data = run_node_json(
        """
        globalThis.window = {
          ARTEMIS_API_BASE: '',
          dispatchEvent: () => {},
          setTimeout,
          clearTimeout,
        };
        globalThis.document = { querySelector: () => null };
        globalThis.CustomEvent = class { constructor(name, options) { this.name = name; this.detail = options?.detail; } };
        const { resolveApiUrl } = await import('./js/auth.js');
        let code = '';
        try { resolveApiUrl('/api/research-slices'); } catch (error) { code = error?.code || ''; }
        console.log(JSON.stringify({ code }));
        """
    )
    assert data["code"] == "API_UNAVAILABLE"


def test_pages_and_service_worker_runtime_contracts() -> None:
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")

    assert '"deployment-config.js"' in workflow
    assert '"js/runtime-config.js"' in workflow
    assert "vars.ARTEMIS_API_BASE" in workflow
    assert "generate_pages_runtime_config.py" in workflow
    assert '<script src="./deployment-config.js"></script>' in index
    assert '<script src="./js/runtime-config.js"></script>' in index
    assert "await Promise.resolve(window.ARTEMIS_RUNTIME_READY)" in index
    assert "isDeploymentConfigRequest(url)" in service_worker
    assert "fetch(request, { cache: 'no-store' })" in service_worker
