import json
from pathlib import Path

from scripts.build_globe_spike import (
    CAPABILITY_PATH,
    ENGINE_EVALUATION_PATH,
    EXPECTED_ENGINE,
    ROOT,
    build_spike,
)


RUNTIME_JS = ROOT / "scripts" / "globe_spike" / "runtime.js"
HTML_TEMPLATE = ROOT / "scripts" / "globe_spike" / "index.html.template"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_engine_evaluation_selects_maplibre_with_all_required_criteria_pass() -> None:
    evaluation = _load(ENGINE_EVALUATION_PATH)
    assert evaluation["selected_engine_id"] == EXPECTED_ENGINE
    required = {
        item["id"] for item in evaluation["criteria"] if item["required"] is True
    }
    selected = next(
        candidate
        for candidate in evaluation["candidates"]
        if candidate["engine_id"] == EXPECTED_ENGINE
    )
    assert all(selected["criteria"][criterion] == "pass" for criterion in required)
    assert selected["decision"] == "selected_for_spike"


def test_builder_creates_isolated_static_artifact(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output)

    expected = {
        "index.html",
        "runtime.js",
        "style.css",
        "projection.json",
        "globe-projection.json",
        "explorer-state.json",
        "geospatial-assets.json",
        "synthetic-earth-context.geojson",
        "capability-path.geojson",
        "engine-evaluation.json",
        "build-meta.json",
        "README.txt",
    }
    assert {path.name for path in output.iterdir() if path.is_file()} == expected
    assert metadata["engine_id"] == EXPECTED_ENGINE
    assert metadata["backend_required"] is False
    assert metadata["public_pages_entrypoint"] is False
    assert metadata["capability_path_is_semantic"] is False


def test_generated_runtime_uses_shared_world_slice_state_and_projection(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)

    meta = _load(output / "build-meta.json")
    state = _load(output / "explorer-state.json")
    projection = _load(output / "projection.json")
    globe = _load(output / "globe-projection.json")

    assert meta["world_slice_ref"] == state["world_slice_ref"]
    assert meta["explorer_state_ref"] == state["state_id"]
    assert meta["projection_id"] == projection["projection_id"]
    assert globe["projection_id"] == projection["projection_id"]
    assert globe["source"]["explorer_state_ref"] == state["state_id"]
    assert globe["vertical_semantics"] == "not_modeled"


def test_globe_payload_contains_explicit_point_and_region_alternatives(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    globe = _load(output / "globe-projection.json")

    primitives = globe["primitives"]
    assert any(
        item["object_ref"] == "event-far-observation"
        and item["primitive_kind"] == "cartographic_point"
        for item in primitives
    )
    assert any(
        item["object_ref"] == "region-fixture-basin"
        and item["subobject_ref"] == "region-geometry-v2"
        and item["geometry_is_primary"] is True
        for item in primitives
    )
    assert any(
        item["object_ref"] == "region-fixture-basin"
        and item["subobject_ref"] == "region-geometry-v2-alternative"
        and item["geometry_is_primary"] is False
        for item in primitives
    )


def test_reviewed_trajectory_gap_remains_unresolved_and_uncertain(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output)
    projection = _load(output / "projection.json")

    gap = next(
        item
        for item in projection["items"]
        if item["object_ref"] == "trajectory-mara-vale"
        and item["subobject_ref"] == "trajectory-segment-gap"
    )
    assert gap["spatial_status"] == "unresolved"
    assert gap["geometry_refs"] == []
    assert "uncertainty-trajectory-route" in gap["uncertainty_refs"]
    assert metadata["trajectory_gap"]["geometry_refs"] == []


def test_capability_path_cannot_be_mistaken_for_world_model_knowledge() -> None:
    fixture = _load(CAPABILITY_PATH)
    feature = fixture["features"][0]
    properties = feature["properties"]
    assert feature["geometry"]["type"] == "LineString"
    assert properties["capability_only"] is True
    assert properties["semantic_role"] == "renderer_capability_path"
    assert properties["world_model_object_ref"] is None
    assert properties["pick_as_knowledge"] is False
    assert "object_ref" not in properties


def test_spike_source_does_not_read_public_compatibility_data_or_backend() -> None:
    runtime_source = RUNTIME_JS.read_text(encoding="utf-8")
    html_source = HTML_TEMPLATE.read_text(encoding="utf-8")
    combined = runtime_source + "\n" + html_source

    assert "features.geojson" not in combined
    assert "/api/" not in combined
    assert "globe-projection.json" in runtime_source
    assert "explorer-state.json" in runtime_source
    assert "geospatial-assets.json" in runtime_source
    assert "queryRenderedFeatures" in runtime_source
    assert "setProjection({ type: 'globe' })" in runtime_source


def test_maplibre_v5_semantic_layers_use_expression_geometry_type_filters() -> None:
    runtime_source = RUNTIME_JS.read_text(encoding="utf-8")

    assert "'$type'" not in runtime_source
    assert '"$type"' not in runtime_source
    assert runtime_source.count("['geometry-type']") >= 6
    assert "['==', ['geometry-type'], 'Polygon']" in runtime_source
    assert "['==', ['geometry-type'], 'LineString']" in runtime_source
    assert "['==', ['geometry-type'], 'Point']" in runtime_source


def test_spike_pins_maplibre_5_without_upgrading_public_runtime() -> None:
    html_source = HTML_TEMPLATE.read_text(encoding="utf-8")
    public_index = (ROOT / "index.html").read_text(encoding="utf-8")

    assert "maplibre-gl@5.24.0" in html_source
    assert "maplibre-gl@4.7.1" in public_index
    assert "maplibre-gl@5.24.0" not in public_index


def test_runtime_contains_terrain_capability_path_but_no_live_provider_is_selected(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output)
    runtime_source = RUNTIME_JS.read_text(encoding="utf-8")

    assert "raster-dem" in runtime_source
    assert "map.setTerrain" in runtime_source
    assert metadata["terrain"]["asset_ref"] == "asset-synthetic-present-terrain"
    assert metadata["terrain"]["live_provider_selected"] is False
    assert metadata["terrain"]["status"] == "synthetic_or_nonlive_provider"


def test_synthetic_context_has_attribution_and_no_world_model_identity(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    context = _load(output / "synthetic-earth-context.geojson")
    manifest = _load(output / "geospatial-assets.json")

    assert all(
        feature["properties"].get("capability_only") is True
        for feature in context["features"]
    )
    assert all(
        "object_ref" not in feature["properties"]
        for feature in context["features"]
    )
    assert all(
        asset["licensing"]["attribution_text"]
        for asset in manifest["assets"]
    )


def test_build_metadata_is_semantically_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    build_spike(first)
    build_spike(second)

    first_meta = _load(first / "build-meta.json")
    second_meta = _load(second / "build-meta.json")
    assert first_meta == second_meta
    assert _load(first / "projection.json") == _load(second / "projection.json")
    assert _load(first / "globe-projection.json") == _load(second / "globe-projection.json")
