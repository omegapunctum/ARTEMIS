from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_INDEX = ROOT / "index.html"
PUBLIC_MANIFEST = ROOT / "manifest.json"
PUBLIC_SERVICE_WORKER = ROOT / "sw.js"
GLOBE_TEMPLATE = ROOT / "scripts" / "globe_spike" / "index.html.template"
GLOBE_RUNTIME = ROOT / "scripts" / "globe_spike" / "runtime.js"
GLOBE_BUILDER = ROOT / "scripts" / "build_globe_spike.py"
GLOBE_WORKFLOW = ROOT / ".github" / "workflows" / "globe-runtime-spike.yml"
BOUNDARY_DOC = ROOT / "docs" / "work" / "2026-08-08_GLOBE_REPOSITORY_RUNTIME_BOUNDARY_v1.md"
PROJECT_STRUCTURE = ROOT / "docs" / "PROJECT_STRUCTURE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_current_public_entrypoint_stays_single_and_on_maplibre_4() -> None:
    index = _text(PUBLIC_INDEX)
    assert "maplibre-gl@4.7.1" in index
    assert "maplibre-gl@5.24.0" not in index
    assert "globe-runtime-spike" not in index
    assert "scripts/globe_spike" not in index
    assert "build/globe-spike" not in index


def test_globe_engine_version_is_isolated_to_experimental_template() -> None:
    template = _text(GLOBE_TEMPLATE)
    assert "maplibre-gl@5.24.0" in template
    assert "ARTEMIS Globe R&D Spike" in template
    assert "Experimental renderer" in template


def test_public_pwa_surfaces_do_not_advertise_or_cache_globe_spike() -> None:
    public_text = _text(PUBLIC_MANIFEST) + "\n" + _text(PUBLIC_SERVICE_WORKER)
    forbidden = (
        "globe-runtime-spike",
        "scripts/globe_spike",
        "build/globe-spike",
        "maplibre-gl@5.24.0",
    )
    assert all(token not in public_text for token in forbidden)


def test_globe_runtime_does_not_fall_back_to_public_compatibility_or_backend() -> None:
    runtime = _text(GLOBE_RUNTIME)
    template = _text(GLOBE_TEMPLATE)
    builder = _text(GLOBE_BUILDER)
    combined = runtime + "\n" + template + "\n" + builder

    assert "data/features.geojson" not in combined
    assert "features.geojson" not in combined
    assert "/api/" not in combined
    assert "globe-projection.json" in runtime
    assert "explorer-state.json" in runtime
    assert "geospatial-assets.json" in runtime


def test_generated_artifact_is_explicitly_nonpublic_and_backend_free() -> None:
    builder = _text(GLOBE_BUILDER)
    assert '"public_pages_entrypoint": False' in builder
    assert '"backend_required": False' in builder
    assert '"capability_path_is_semantic": False' in builder
    assert '"build" / "globe-spike"' in builder


def test_globe_workflow_uploads_review_artifact_but_never_deploys_pages() -> None:
    workflow = _text(GLOBE_WORKFLOW).lower()
    assert "actions/upload-artifact@" in workflow
    forbidden = (
        "actions/deploy-pages",
        "actions/upload-pages-artifact",
        "peaceiris/actions-gh-pages",
        "gh-pages",
    )
    assert all(token not in workflow for token in forbidden)


def test_boundary_decision_rejects_premature_apps_or_framework_migration() -> None:
    decision = _text(BOUNDARY_DOC)
    assert "will **not** perform a repository-wide `apps/*`" in decision
    assert "index.html` remains the only public frontend entrypoint" in decision
    assert "Moving Globe source out of `scripts/globe_spike/`" in decision
    assert "React/Vue/Angular/TypeScript/npm workspace/bundler migration is not implied" in decision
    assert "Production-scale 3D/dynamic Earth remains gated" in decision


def test_existing_canonical_structure_already_prohibits_renderer_semantic_forks() -> None:
    structure = _text(PROJECT_STRUCTURE)
    lowered = structure.lower()
    assert "current `index.html`" in lowered
    assert "experimental globe runtime" in lowered
    assert "second semantic core" not in lowered  # English shortcut must not become an alternate owner label.
    assert "renderer-specific historical data forks" in lowered


def test_no_checked_in_generated_globe_build_exists() -> None:
    assert not (ROOT / "build" / "globe-spike").exists()
