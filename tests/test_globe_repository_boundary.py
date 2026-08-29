from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_INDEX = ROOT / "index.html"
PUBLIC_MANIFEST = ROOT / "manifest.json"
PUBLIC_SERVICE_WORKER = ROOT / "sw.js"
CORE_LANDING = ROOT / "scripts" / "globe_spike" / "root-index.html"
GLOBE_TEMPLATE = ROOT / "scripts" / "globe_spike" / "index.html.template"
GLOBE_RUNTIME = ROOT / "scripts" / "globe_spike" / "runtime.js"
GLOBE_BUILDER = ROOT / "scripts" / "build_globe_spike.py"
GLOBE_WORKFLOW = ROOT / ".github" / "workflows" / "globe-runtime-spike.yml"
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
BOUNDARY_DOC = ROOT / "docs" / "work" / "2026-08-08_GLOBE_REPOSITORY_RUNTIME_BOUNDARY_v1.md"
PROJECT_STRUCTURE = ROOT / "docs" / "PROJECT_STRUCTURE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_architecture_atlas_source_stays_on_maplibre_4_and_links_preview() -> None:
    index = _text(PUBLIC_INDEX)
    assert "maplibre-gl@4.7.1" in index
    assert "maplibre-gl@5.24.0" not in index
    assert 'href="./globe/"' in index
    assert "3D Globe · R&amp;D" in index
    assert "scripts/globe_spike" not in index
    assert "build/globe-spike" not in index


def test_public_root_landing_routes_globe_primary_and_atlas_compatibility() -> None:
    landing = _text(CORE_LANDING)
    assert 'href="./globe/"' in landing
    assert 'href="./atlas/"' in landing
    assert "Globe — активный продуктовый контур" in landing
    assert "исследовательский прототип" in landing
    assert "maplibre" not in landing.lower()


def test_globe_engine_version_is_isolated_to_experimental_template() -> None:
    template = _text(GLOBE_TEMPLATE)
    assert "maplibre-gl@5.24.0" in template
    assert "ARTEMIS · Leonardo Life Path" in template
    assert "{{PUBLIC_PREVIEW_STATUS}}" in template


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


def test_generated_artifact_supports_explicit_review_and_public_preview_modes() -> None:
    builder = _text(GLOBE_BUILDER)
    assert "public_preview: bool = False" in builder
    assert '"public_pages_entrypoint": public_preview' in builder
    assert '"public_r_and_d_preview" if public_preview' in builder
    assert '"isolated_review_artifact"' in builder
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


def test_pages_workflow_builds_bounded_public_globe_preview() -> None:
    workflow = _text(PAGES_WORKFLOW)
    assert "scripts/globe_spike/root-index.html pages_artifact/index.html" in workflow
    assert 'pages_artifact/atlas/$file' in workflow
    assert "python scripts/build_globe_spike.py" in workflow
    assert "--public-preview" in workflow
    assert "--output pages_artifact/globe" in workflow
    assert 'metadata["public_pages_entrypoint"] is True' in workflow
    assert "actions/upload-pages-artifact@" in workflow


def test_pages_core_path_has_no_backend_or_airtable_dependency() -> None:
    workflow = _text(PAGES_WORKFLOW)
    assert "pip install jsonschema==4.25.1 pytest" in workflow
    assert "pip install -r requirements.txt" not in workflow
    assert "scripts/release_check.py" not in workflow
    assert "validate_airtable" not in workflow
    assert "preflight_migration_check" not in workflow
    assert "app.main" not in workflow


def test_boundary_decision_rejects_premature_apps_or_framework_migration() -> None:
    decision = _text(BOUNDARY_DOC)
    assert "will **not** perform a repository-wide `apps/*`" in decision
    assert "public R&D preview" in decision
    assert "root 2D runtime remains the default and rollback entrypoint" in decision
    assert "Moving Globe source out of `scripts/globe_spike/`" in decision
    assert "React/Vue/Angular/TypeScript/npm workspace/bundler migration is not implied" in decision
    assert "Production-scale 3D/dynamic Earth remains gated" in decision


def test_existing_canonical_structure_prohibits_renderer_semantic_forks() -> None:
    structure = _text(PROJECT_STRUCTURE)
    lowered = structure.lower()
    assert "source `index.html`" in lowered
    assert "generated core landing" in lowered
    assert "primary leonardo globe/temporal map research prototype" in lowered
    assert "общий world model / explorer state / projection boundary" in lowered
    assert "renderer-specific historical data forks" in lowered
    assert "current leonardo globe historical input" in lowered
    assert "not `data/features.geojson`" in lowered


def test_no_checked_in_generated_globe_build_exists() -> None:
    assert not (ROOT / "build" / "globe-spike").exists()
