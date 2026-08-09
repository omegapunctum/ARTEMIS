import hashlib
import json
from pathlib import Path

from scripts.build_globe_spike import (
    CAPABILITY_PATH,
    ENGINE_EVALUATION_PATH,
    EXPECTED_ENGINE,
    ROOT,
    WORLD_PATH,
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
        "knowledge-index.json",
        "build-meta.json",
        "README.txt",
    }
    assert {path.name for path in output.iterdir() if path.is_file()} == expected
    assert metadata["engine_id"] == EXPECTED_ENGINE
    assert metadata["backend_required"] is False
    assert metadata["public_pages_entrypoint"] is False
    assert metadata["capability_path_is_semantic"] is False
    assert metadata["knowledge_record_count"] == metadata["semantic_item_count"]
    assert (output / "sources").is_dir()


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
    assert "knowledge-index.json" in runtime_source
    assert "queryRenderedFeatures" in runtime_source
    assert "setProjection({ type: 'globe' })" in runtime_source


def test_knowledge_index_closes_projection_refs_without_fabrication(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    projection = _load(output / "projection.json")
    knowledge = _load(output / "knowledge-index.json")

    assert knowledge["fixture_mode"] == "synthetic_contract_fixture"
    assert knowledge["historical_corpus_ready"] is False
    assert "Relation" in knowledge["deferred_object_types"]
    assert {record["item_id"] for record in knowledge["records"]} == {
        item["item_id"] for item in projection["items"]
    }

    projected = {item["item_id"]: item for item in projection["items"]}
    for record in knowledge["records"]:
        item = projected[record["item_id"]]
        assert record["object_ref"] == item["object_ref"]
        assert record["subobject_ref"] == item["subobject_ref"]
        assert {claim["id"] for claim in record["claims"]} == set(item["claim_refs"])
        assert {link["id"] for link in record["evidence_links"]} == set(
            item["evidence_link_refs"]
        )
        assert {source["id"] for source in record["sources"]} == set(
            item["source_refs"]
        )
        assert {value["id"] for value in record["uncertainties"]} == set(
            item["uncertainty_refs"]
        )
        for link in record["evidence_links"]:
            assert link["claim_id"] in record["claim_refs"]
            assert link["source_id"] in record["source_refs"]
            assert link["locator"].strip()


def test_primary_selection_exposes_claim_source_and_repeatable_locator(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    knowledge = _load(output / "knowledge-index.json")
    record = next(
        item
        for item in knowledge["records"]
        if item["object_ref"] == "event-documented-workshop-meeting"
    )

    assert record["label"] == "Workshop meeting"
    assert record["claims"][0]["statement"].startswith("The synthetic register records")
    assert record["evidence_links"][0]["locator"] == "LOCATOR[alpha-encounter]"
    assert record["sources"][0]["title"] == "Synthetic field notebook alpha"
    assert record["sources"][0]["artifact_uri"] == "./sources/field-notebook-alpha.md"
    assert record["projection_losses"][0]["reason"] == "named_place_without_resolved_geometry"


def test_local_source_artifacts_are_copied_with_reviewed_checksums(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output)
    world = _load(WORLD_PATH)

    expected_checksums = {}
    for source in world["sources"]:
        copied = output / source["uri"]
        assert copied.is_file()
        digest = hashlib.sha256(copied.read_bytes()).hexdigest()
        assert digest == source["sha256"]
        expected_checksums[source["id"]] = digest
    assert metadata["input_sha256"]["source_documents"] == expected_checksums


def test_unresolved_items_are_keyboard_inspectable_through_knowledge_index() -> None:
    runtime_source = RUNTIME_JS.read_text(encoding="utf-8")
    html_source = HTML_TEMPLATE.read_text(encoding="utf-8")

    assert "row.type = 'button'" in runtime_source
    assert "selectKnowledgeItem(item.item_id, { focus: true })" in runtime_source
    assert "renderKnowledgeRecord" in runtime_source
    assert "evidence.locator" in runtime_source
    assert 'id="selection-card"' in html_source
    assert 'tabindex="-1"' in html_source
    assert 'aria-live="polite"' in html_source


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
    assert _load(first / "knowledge-index.json") == _load(second / "knowledge-index.json")
