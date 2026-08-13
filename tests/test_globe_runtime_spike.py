import hashlib
import json
from pathlib import Path

from scripts.build_globe_spike import (
    CAPABILITY_PATH,
    DEFAULT_DATASET,
    ENGINE_EVALUATION_PATH,
    EXPECTED_ENGINE,
    ROOT,
    WORLD_PATH,
    build_spike,
)
from scripts.build_leonardo_gate_d_inputs import build_gate_d_inputs


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
        "explorer-views.json",
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
    assert metadata["explorer_view_count"] == 96
    assert metadata["temporal_preset_count"] == 6
    assert metadata["semantic_dataset"] == DEFAULT_DATASET
    assert not (output / "sources").exists()


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


def test_precomputed_views_use_source_native_time_and_projection_semantics(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    views = _load(output / "explorer-views.json")
    knowledge = _load(output / "knowledge-index.json")

    assert [preset["preset_id"] for preset in views["temporal_presets"]] == [
        "full-slice",
        "rimini-1502-08-08",
        "cesena-1502-08-10",
        "patent-1502-08-18",
        "cesenatico-1502-09-06",
        "imola-autumn-1502",
    ]
    assert views["temporal_presets"][-1]["temporal_selection"] == {
        "mode": "interval",
        "start": "1502-09",
        "end": "1502-11",
        "precision": "month",
        "calendar": "proleptic_gregorian",
    }
    assert len(views["layer_options"]) == 4
    assert len(views["views"]) == 6 * (2 ** 4)

    knowledge_ids = {record["item_id"] for record in knowledge["records"]}
    for view in views["views"]:
        state = view["state"]
        projection = view["projection"]
        globe = view["globe"]
        assert state["active_layer_refs"] == view["active_layer_refs"]
        assert projection["source"]["explorer_state_ref"] == state["state_id"]
        assert projection["temporal_selection"] == state["temporal_selection"]
        assert globe["source"]["explorer_state_ref"] == state["state_id"]
        assert projection["geometries"] == []
        assert globe["primitives"] == []
        assert {item["item_id"] for item in projection["items"]} <= knowledge_ids
        assert "Relation" in projection["deferred_object_types"]

    empty_layer_views = [view for view in views["views"] if not view["active_layer_refs"]]
    assert len(empty_layer_views) == 6
    assert all(view["projection"]["items"] == [] for view in empty_layer_views)


def test_temporal_views_change_membership_without_invented_intermediate_dates(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    views = _load(output / "explorer-views.json")
    all_layers = {option["layer_ref"] for option in views["layer_options"]}

    def object_refs(preset_id: str) -> set[str]:
        view = next(
            item for item in views["views"]
            if item["temporal_preset_id"] == preset_id
            and set(item["active_layer_refs"]) == all_layers
        )
        return {item["object_ref"] for item in view["projection"]["items"]}

    rimini = object_refs("rimini-1502-08-08")
    cesena = object_refs("cesena-1502-08-10")
    autumn = object_refs("imola-autumn-1502")
    assert "event-leonardo-rimini-note" in rimini
    assert "event-leonardo-rimini-note" not in cesena
    assert "event-leonardo-cesena-survey" in cesena
    assert "event-leonardo-imola-map-context" in autumn
    assert "event-leonardo-imola-map-context" not in rimini
    assert "event-ottoman-turkmen-displacement-1502" in rimini & cesena & autumn


def test_default_adapter_preserves_frozen_gate_c_boundary_without_geometry() -> None:
    world, state = build_gate_d_inputs()

    object_ids = {
        item["id"]
        for collection in ("entities", "events", "states", "processes", "trajectories", "regions")
        for item in world[collection]
    }
    assert len(object_ids) == 17
    assert len(world["claims"]) == 22
    assert len(world["evidence_links"]) == 38
    assert len(world["sources"]) == 10
    assert len(world["uncertainties"]) == 11
    assert {item["review_state"] for item in world["claims"]} == {"draft", "rejected"}
    assert world["relations"] == []
    assert world["derived_observations"] == []
    assert world["historical_corpus_ready"] is False
    assert world["promotion_allowed"] is False
    assert world["gate_c_decision"]["decision"] == "FREEZE"
    assert world["gate_c_decision"]["promotion_allowed"] is False
    assert state["world_slice_ref"] == "world-slice-leonardo-romagna-1502-v1"
    assert state["dataset_identity"] == world["world_slice"]["dataset_identity"]
    assert state["temporal_selection"] == {
        "mode": "interval",
        "start": "1502-08-08",
        "end": "1502-12-31",
        "precision": "day",
        "calendar": "proleptic_gregorian",
    }


def test_default_projection_keeps_real_slice_geometry_withheld(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output)
    projection = _load(output / "projection.json")
    globe = _load(output / "globe-projection.json")

    assert metadata["semantic_dataset"] == "leonardo_gate_c"
    assert metadata["semantic_item_count"] == 24
    assert metadata["globe_primitive_count"] == 0
    assert projection["geometries"] == []
    assert globe["primitives"] == []
    assert all(
        item["spatial_status"] != "resolved" for item in projection["items"]
    )
    assert any(
        item["object_ref"] == "process-leonardo-romagna-surveying"
        and item["subobject_ref"] is None
        and item["spatial_status"] == "unresolved"
        for item in projection["items"]
    )
    region_items = [
        item for item in projection["items"] if item["object_type"] == "Region"
    ]
    assert {item["subobject_ref"] for item in region_items} == {
        "region-version-borgia-romagna-1502",
        "region-version-documented-place-only-1502",
    }
    assert all(item["spatial_status"] == "unresolved" for item in region_items)


def test_globe_payload_contains_explicit_point_and_region_alternatives(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output, dataset="contract_fixture")
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
        if item["object_ref"] == "trajectory-leonardo-romagna-1502"
        and item["subobject_ref"] == "segment-rimini-cesena-gap"
    )
    assert gap["spatial_status"] == "unresolved"
    assert gap["geometry_refs"] == []
    assert "uncertainty-trajectory-route-gaps" in gap["uncertainty_refs"]
    assert len(metadata["trajectory_gaps"]) == 3
    assert all(item["geometry_refs"] == [] for item in metadata["trajectory_gaps"])


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
    assert "explorer-views.json" in runtime_source
    assert "geospatial-assets.json" in runtime_source
    assert "knowledge-index.json" in runtime_source
    assert "queryRenderedFeatures" in runtime_source
    assert "setProjection({ type: 'globe' })" in runtime_source


def test_knowledge_index_closes_projection_refs_without_fabrication(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    build_spike(output)
    projection = _load(output / "projection.json")
    knowledge = _load(output / "knowledge-index.json")

    assert knowledge["fixture_mode"] == "frozen_gate_c_candidate_package"
    assert knowledge["historical_corpus_ready"] is False
    assert knowledge["promotion_allowed"] is False
    assert "Relation" in knowledge["deferred_object_types"]
    assert {record["item_id"] for record in knowledge["records"]} == {
        item["item_id"] for item in projection["items"]
    }
    assert len({ref for record in knowledge["records"] for ref in record["claim_refs"]}) == 22
    assert len(
        {ref for record in knowledge["records"] for ref in record["evidence_link_refs"]}
    ) == 38

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
        if item["object_ref"] == "event-leonardo-rimini-note"
    )

    assert record["label"] == "Leonardo records the dated Rimini observation"
    assert record["claims"][0]["review_state"] == "draft"
    assert record["claims"][0]["statement"].startswith("Leonardo recorded an observation")
    assert "Manuscript L folio 78r" in record["evidence_links"][0]["locator"]
    assert record["sources"][0]["title"] == "Cronologia vinciana (1502–1503)"
    assert record["sources"][0]["artifact_uri"].startswith("https://press.uniurb.it/")
    assert record["projection_losses"][0]["reason"] == "unknown_spatial_extent"


def test_local_source_artifacts_are_copied_with_reviewed_checksums(tmp_path: Path) -> None:
    output = tmp_path / "globe-spike"
    metadata = build_spike(output, dataset="contract_fixture")
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


def test_timeline_layers_and_selection_share_precomputed_explorer_views() -> None:
    runtime_source = RUNTIME_JS.read_text(encoding="utf-8")
    html_source = HTML_TEMPLATE.read_text(encoding="utf-8")

    assert 'id="temporal-preset" type="range"' in html_source
    assert 'id="layer-controls"' in html_source
    assert 'role="status" aria-live="polite"' in html_source
    assert "applySemanticView" in runtime_source
    assert "runtime.viewByKey.get" in runtime_source
    assert "semanticSource.setData(globePrimitivesToGeoJson(next.globe))" in runtime_source
    assert "updateCanonicalSelection(projectionItem)" in runtime_source
    assert "Selection cleared: the object is outside the active time/layer projection." in runtime_source
    assert "prefers-reduced-motion: reduce" in runtime_source


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
    assert _load(first / "explorer-views.json") == _load(second / "explorer-views.json")
