"""Input identity and fail-closed composition tests for one shared Explorer."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts import build_globe_spike as spike
from scripts import build_unified_explorer as unified


def test_shared_query_url_history_and_native_ui_behavior(bundle, tmp_path):
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_bytes(unified._bytes(bundle))
    subprocess.run(["node", "tests/unified_explorer_behavior.cjs", str(bundle_path)], cwd=unified.ROOT, check=True)


@pytest.fixture(scope="module")
def native_builds(tmp_path_factory):
    base = tmp_path_factory.mktemp("native-unified-inputs")
    spike.build_spike(base / "leonardo", public_preview=True)
    spike.build_spike(base / "roman", dataset=spike.REGION_DATASET, public_preview=True)
    return base


@pytest.fixture(scope="module")
def bundle(native_builds):
    return unified._compose(native_builds / "leonardo", native_builds / "roman")


def test_m5_native_identity_dates_epistemic_records_and_null_routes(bundle, native_builds):
    native = json.loads((native_builds / "leonardo" / "life-path.json").read_text())
    views = native.pop("views")
    composed = copy.deepcopy(bundle["leonardo"]["lifePath"])
    omitted = composed.pop("omitted_precomputed_views")
    assert composed == native
    assert omitted == {"count": len(views), "sha256": unified._digest(views), "role": "duplicate_presentation_views_replaced_by_one_shared_query"}
    assert len(composed["presences"]) == 11
    assert composed["route_policy"]["geometry"] is None
    assert all(row["route_geometry"] is None for row in composed["transitions"])
    assert bundle["leonardo"]["knowledge"] == json.loads((native_builds / "leonardo" / "knowledge-index.json").read_text())
    state = json.loads((native_builds / "leonardo" / "explorer-state.json").read_text())
    assert bundle["leonardo"]["explorerState"] == state
    assert bundle["leonardo"]["projection"]["source"]["explorer_state_ref"] == state["state_id"]
    assert bundle["leonardo"]["globe"]["source"]["explorer_state_ref"] == state["state_id"]
    assert bundle["source_native_state_role"] == "preserved_canonical_inputs_orchestrated_by_application_workspace_state_not_a_canonical_state_migration"
    for filename, key in [("projection.json", "projection"), ("globe-projection.json", "globe")]:
        assert bundle["leonardo"][key] == json.loads((native_builds / "leonardo" / filename).read_text())
    assert bundle["leonardo"]["sourcePackage"] == json.loads(spike.MAJOR_LIFE_PACKAGE_PATH.read_text())
    assert bundle["leonardo"]["runtimeAnchors"] == json.loads(spike.MAJOR_LIFE_RUNTIME_ANCHORS_PATH.read_text())


def test_roman_native_intervals_geometry_and_epistemic_statuses(bundle, native_builds):
    world, _, presets = spike.build_region_inputs()
    assert bundle["roman"]["worldInput"] == world
    assert bundle["roman"]["knowledge"] == json.loads((native_builds / "roman" / "knowledge-index.json").read_text())
    manifest = json.loads((spike.REGION_PACKAGE_ROOT / "source_manifest.json").read_text())
    excerpt = json.loads((spike.REGION_PACKAGE_ROOT / "sources" / "cliopatria-excerpt.json").read_text())
    assert bundle["roman"]["sourceManifest"] == manifest
    assert [(v["interval"]["start"], v["interval"]["end"]) for v in bundle["roman"]["versions"]] == [(91, 105), (106, 113), (114, 116)]
    for row, version, source_feature, preset in zip(bundle["roman"]["versions"], world["regions"][0]["geometry_versions"], excerpt["features"], presets):
        assert row["geometry_version"] == version
        assert row["geometry_version"]["spatial_extent"]["geometry"] == source_feature["geometry"]
        assert row["temporal_selection"] == preset["temporal_selection"]
        assert row["state"] == next(v["state"] for v in json.loads((native_builds / "roman" / "explorer-views.json").read_text())["views"] if v["temporal_preset_id"] == preset["preset_id"] and v["active_layer_refs"])
        assert row["projection"]["source"]["explorer_state_ref"] == row["state"]["state_id"]
        assert row["globe"]["source"]["explorer_state_ref"] == row["state"]["state_id"]
        primitives = [p for p in row["globe"]["primitives"] if p["item_id"] == row["item_id"]]
        assert len(primitives) == 1
        assert primitives[0]["coordinates"] == source_feature["geometry"]["coordinates"]
        assert primitives[0]["geometry_reconstruction_mode"] == "scholarly_reconstruction"
    # Claims remain native draft supported interpretations; no new acceptance.
    assert {c["review_state"] for c in world["claims"]} == {"draft"}
    assert {s["review_state"] for s in world["sources"]} == {"draft"}


def test_all_31_atemporal_references_preserve_coordinates_dates_aliases_and_sources(bundle):
    raw_features = json.loads(unified.FEATURES_PATH.read_text())["features"]
    raw_sources = json.loads(unified.SOURCES_PATH.read_text())
    by_source = {source["id"]: source for source in raw_sources}
    assert bundle["architecture"]["sources"] == raw_sources
    assert len(bundle["architecture"]["references"]) == len(raw_features) == 31
    assert bundle["architecture"]["time_filtering"] == "excluded"
    assert any(str(f["properties"]["date_start"]).startswith("-") for f in raw_features)
    for reference, feature in zip(bundle["architecture"]["references"], raw_features):
        assert reference["raw_feature"] == feature
        assert reference["geometry"] == feature["geometry"]
        assert reference["item_id"] == f"architecture:reference:{feature['id']}"
        assert reference["original_id"] == feature["id"]
        assert reference["aliases"] == feature["properties"]["legacy_ids"]
        assert reference["source_ids"] == feature["properties"]["source_ids"]
        assert reference["sources"] == [by_source[s] for s in reference["source_ids"]]
        assert reference["temporal_extent"] is None
        assert reference["historical_position"] is None
        assert reference["historical_applicability"] == reference["historical_precision"] == "unknown"
        assert reference["claim_refs"] == reference["evidence_link_refs"] == []
        assert reference["input_pointer_role"] == "export_provenance_not_historical_evidence"
    park_hill = next(r for r in bundle["architecture"]["references"] if "Park Hill" in (r["raw_feature"]["properties"].get("name_en") or ""))
    assert park_hill["geometry"]["coordinates"] == [-1.4582, 53.38163]
    pyramid = bundle["architecture"]["references"][0]
    assert pyramid["raw_feature"]["properties"]["date_start"] == "-2589"
    assert pyramid["raw_feature"]["properties"]["date_end"] == "-2566"
    assert pyramid["raw_feature"]["properties"]["coordinates_confidence"] == "exact"
    assert pyramid["historical_precision"] == "unknown"


def test_shared_registry_is_one_stable_collection_and_architecture_never_defines_coverage(bundle):
    registry = bundle["registry"]
    assert len(registry) == len({r["item_id"] for r in registry}) == 45
    assert {kind: sum(r["kind"] == kind for r in registry) for kind in ("presence", "region", "reference")} == {"presence": 11, "region": 3, "reference": 31}
    assert bundle["calendar"] == {"calendar": "proleptic_gregorian", "era": "CE", "min_year": 91, "max_year": 1519, "coverage_complete": False, "architecture_dates_define_coverage": False}
    assert all(r["interval"] is None for r in registry if r["layer_id"] == "architecture")
    assert [r["item_id"] for r in registry if r["layer_id"] == "leonardo"] == [p["presence_item_id"] for p in bundle["leonardo"]["lifePath"]["presences"]]
    assert [r["item_id"] for r in registry if r["layer_id"] == "roman"] == [v["item_id"] for v in bundle["roman"]["versions"]]


def test_source_ledger_and_content_digest_bind_exact_checked_in_bytes(bundle):
    rows = bundle["input_ledger"]
    assert len(rows) == len({row["path"] for row in rows}) == len(unified._input_paths())
    paths = {row["path"] for row in rows}
    assert {
        "data/features.geojson", "data/sources.json",
        "fixtures/world_slices/leonardo_major_life/v1/package.json",
        "fixtures/globe_runtime/v1/leonardo_major_life_runtime_anchors.json",
        "fixtures/world_slices/leonardo_romagna_1502/v1/claims_manifest.json",
        "fixtures/world_slices/leonardo_romagna_1502/v1/source_registry.json",
        "fixtures/world_slices/leonardo_romagna_1502/v1/review_registry.json",
        "fixtures/world_slices/roman_empire_region/v1/source_manifest.json",
        "fixtures/world_slices/roman_empire_region/v1/sources/cliopatria-excerpt.json",
    } <= paths
    for row in rows:
        payload = (unified.ROOT / row["path"]).read_bytes()
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
        assert row["bytes"] == len(payload)
        assert row["artifact_uri"] == f"./inputs/{row['path']}"
    expected = copy.deepcopy(bundle)
    digest = expected.pop("content_sha256")
    assert digest == unified._digest(expected)
    changed = copy.deepcopy(expected)
    changed["architecture"]["references"][0]["geometry"]["coordinates"][0] += 1
    assert unified._digest(changed) != digest


@pytest.mark.parametrize("problem", ["missing_source", "duplicate_id", "invalid_geometry", "source_link", "count"])
def test_bad_reference_input_fails_without_silent_loss_or_promotion(problem):
    features, sources = json.loads(unified.FEATURES_PATH.read_text()), json.loads(unified.SOURCES_PATH.read_text())
    first = features["features"][0]
    if problem == "missing_source":
        first["properties"]["source_ids"] = ["missing-source"]
    elif problem == "duplicate_id":
        features["features"][1]["id"] = first["id"]
    elif problem == "invalid_geometry":
        first["geometry"]["coordinates"] = [181, 0]
    elif problem == "source_link":
        first["properties"]["source_refs"][0]["source_id"] = "missing-source"
    elif problem == "count":
        features["features"].pop()
    before = copy.deepcopy(features)
    with pytest.raises(unified.UnifiedBuildError):
        unified.adapt_architecture(features, sources)
    assert features == before


def test_raw_dates_and_legacy_flags_never_create_temporal_applicability_or_claims():
    features, sources = json.loads(unified.FEATURES_PATH.read_text()), json.loads(unified.SOURCES_PATH.read_text())
    properties = features["features"][0]["properties"]
    properties.update({"date_start": "-99999", "date_end": "unresolved-associated-date", "validated": True, "date_valid": True, "reviewed": True, "coordinates_confidence": "exact"})
    references = unified.adapt_architecture(features, sources)["references"]
    assert references[0]["raw_feature"]["properties"] == properties
    assert references[0]["temporal_extent"] is None
    assert references[0]["historical_applicability"] == "unknown"
    assert references[0]["historical_precision"] == "unknown"
    assert references[0]["claim_refs"] == references[0]["evidence_link_refs"] == []


def test_entry_profiles_are_only_initial_presentation_and_share_bundle_bytes(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "index.html.template").write_text('<body data-entry-profile="{{ENTRY_PROFILE}}"></body>')
    (templates / "runtime.js").write_text("// Runtime is owned and tested separately.\n")
    (templates / "style.css").write_text("body { color: white; }\n")
    monkeypatch.setattr(unified, "TEMPLATE_DIR", templates)
    metadata = [unified.build_unified_explorer(tmp_path / profile, entry_profile=profile) for profile in ("leonardo", "roman")]
    assert (tmp_path / "leonardo" / "unified-bundle.json").read_bytes() == (tmp_path / "roman" / "unified-bundle.json").read_bytes()
    assert metadata[0]["bundle_sha256"] == metadata[1]["bundle_sha256"]
    assert metadata[0]["bundle_content_sha256"] == metadata[1]["bundle_content_sha256"]
    assert 'data-entry-profile="globe"' in (tmp_path / "leonardo" / "index.html").read_text()
    assert 'data-entry-profile="region"' in (tmp_path / "roman" / "index.html").read_text()
    for profile, meta in zip(("leonardo", "roman"), metadata):
        assert meta["entry_profile"] == profile
        assert meta["semantic_dataset"] == "unified_explorer"
        assert meta["deployment_mode"] == "public_r_and_d_preview"
        assert meta["public_pages_entrypoint"] is True
        assert meta["backend_required"] is False
        assert meta["engine_id"] == "maplibre-gl-js-5.24.0"
        assert meta["terrain"] == {"asset_ref": None, "runtime_enabled": False, "live_provider_selected": False, "status": "not_enabled_in_unified_runtime"}
        assert meta["value_validation"] == "UNVALIDATED"
        assert meta["source_native_state_role"] == "preserved_canonical_inputs_orchestrated_by_application_workspace_state_not_a_canonical_state_migration"
        for row in json.loads((tmp_path / profile / "unified-bundle.json").read_text())["input_ledger"]:
            assert hashlib.sha256((tmp_path / profile / "inputs" / row["path"]).read_bytes()).hexdigest() == row["sha256"]
        assert (tmp_path / profile / "sources" / "cliopatria-excerpt.json").read_bytes() == (spike.REGION_PACKAGE_ROOT / "sources" / "cliopatria-excerpt.json").read_bytes()


def test_invalid_profile_does_not_remove_existing_output(tmp_path):
    output = tmp_path / "already-built"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("existing artifact")
    with pytest.raises(unified.UnifiedBuildError):
        unified.build_unified_explorer(output, entry_profile="invented")
    assert sentinel.read_text() == "existing artifact"


def test_bad_input_does_not_partially_replace_published_build(tmp_path, monkeypatch):
    output = tmp_path / "already-built"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("existing artifact")
    features = json.loads(unified.FEATURES_PATH.read_text())
    features["features"][0]["properties"]["source_ids"] = ["unknown-source"]
    bad_input = tmp_path / "bad-features.geojson"
    bad_input.write_text(json.dumps(features))
    monkeypatch.setattr(unified, "FEATURES_PATH", bad_input)
    with pytest.raises(unified.UnifiedBuildError, match="unresolved source IDs"):
        unified.build_unified_explorer(output, entry_profile="leonardo")
    assert list(output.iterdir()) == [sentinel]
    assert sentinel.read_text() == "existing artifact"
