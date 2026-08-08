import copy
import json
from pathlib import Path

from scripts.validate_geospatial_assets import (
    semantic_asset_signature,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "manifest.json"
SCHEMA_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "schema.json"
WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs():
    return _load(MANIFEST_PATH), _load(SCHEMA_PATH), _load(WORLD_PATH)


def _errors(manifest):
    _, schema, world = _inputs()
    return validate_manifest(manifest, schema=schema, world=world)


def _asset(manifest, asset_id):
    return next(asset for asset in manifest["assets"] if asset["asset_id"] == asset_id)


def test_synthetic_manifest_is_valid_and_not_historical_truth() -> None:
    manifest, schema, world = _inputs()
    assert validate_manifest(manifest, schema=schema, world=world) == []
    assert manifest["manifest_mode"] == "synthetic_contract_fixture"
    assert all(
        asset["semantic_role"] == "present_day_context"
        for asset in manifest["assets"]
    )
    assert all(
        asset["temporal_semantics"]["world_model_claim_refs"] == []
        for asset in manifest["assets"]
    )


def test_duplicate_asset_identity_is_rejected() -> None:
    manifest, _, _ = _inputs()
    manifest["assets"].append(copy.deepcopy(manifest["assets"][0]))
    assert any("duplicate asset_id" in error for error in _errors(manifest))


def test_provider_swap_does_not_change_semantic_asset_signature() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    swapped = copy.deepcopy(terrain)
    swapped["provider"] = {
        "provider_id": "provider-synthetic-alternative-terrain",
        "adapter_kind": "static_local",
        "endpoint_template": "fixture://terrain/alternative-global",
        "credential_mode": "none",
        "credential_env": None,
    }
    assert semantic_asset_signature(terrain) == semantic_asset_signature(swapped)


def test_terrain_requires_explicit_vertical_reference() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    terrain["spatial_reference"]["vertical_reference"] = {
        "mode": "not_applicable",
        "datum": None,
        "unit": None,
        "positive_direction": None,
    }
    assert any("height-bearing asset requires" in error for error in _errors(manifest))


def test_not_applicable_vertical_reference_cannot_hide_vertical_metadata() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["spatial_reference"]["vertical_reference"]["datum"] = "WGS84"
    assert any("not_applicable vertical reference" in error for error in _errors(manifest))


def test_present_day_context_cannot_claim_historical_validity() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    terrain["temporal_semantics"].update(
        {
            "mode": "historical_validity",
            "valid_from": "1500",
            "valid_to": "1510",
            "world_model_claim_refs": ["claim-region-v2"],
            "uncertainty_refs": ["uncertainty-region-alternative"],
            "reconstruction_method": "synthetic_method",
        }
    )
    errors = _errors(manifest)
    assert any("present_day_context must use" in error for error in errors)
    assert any("cannot declare historical validity" in error for error in errors)
    assert any("cannot carry historical Claim" in error for error in errors)


def test_historical_reconstruction_requires_validity_claims_and_method() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["semantic_role"] = "historical_reconstruction"
    imagery["temporal_semantics"]["mode"] = "historical_validity"
    errors = _errors(manifest)
    assert any("requires valid_from and valid_to" in error for error in errors)
    assert any("requires World Model Claim bindings" in error for error in errors)
    assert any("requires reconstruction_method" in error for error in errors)


def test_historical_reconstruction_can_bind_known_world_model_claims() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["semantic_role"] = "historical_reconstruction"
    imagery["temporal_semantics"] = {
        "mode": "historical_validity",
        "reference_date": None,
        "valid_from": "1504",
        "valid_to": "1510",
        "world_model_claim_refs": ["claim-region-v2"],
        "uncertainty_refs": ["uncertainty-region-alternative"],
        "reconstruction_method": "synthetic_fixture_reconstruction",
    }
    assert _errors(manifest) == []


def test_unknown_historical_claim_binding_is_rejected() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["semantic_role"] = "historical_reconstruction"
    imagery["temporal_semantics"] = {
        "mode": "historical_validity",
        "reference_date": None,
        "valid_from": "1504",
        "valid_to": "1510",
        "world_model_claim_refs": ["claim-does-not-exist"],
        "uncertainty_refs": [],
        "reconstruction_method": "synthetic_fixture_reconstruction",
    }
    assert any("unknown World Model Claim refs" in error for error in _errors(manifest))


def test_credential_like_query_parameter_is_rejected() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["provider"]["endpoint_template"] = (
        "https://tiles.example.invalid/{z}/{x}/{y}?access_token=literal-secret"
    )
    imagery["runtime_policy"]["network_required"] = True
    assert any("credential-like query parameter" in error for error in _errors(manifest))


def test_runtime_secret_requires_env_and_blocks_public_pages() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["provider"]["credential_mode"] = "runtime_secret"
    imagery["provider"]["credential_env"] = "ARTEMIS_TEST_TILE_TOKEN"
    imagery["runtime_policy"]["secret_required"] = True
    imagery["runtime_policy"]["public_pages_allowed"] = False
    assert _errors(manifest) == []

    imagery["runtime_policy"]["public_pages_allowed"] = True
    assert any("cannot be exposed to public Pages" in error for error in _errors(manifest))


def test_restricted_redistribution_forbids_cached_byte_redistribution() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["licensing"]["redistribution"] = "restricted"
    assert any("forbids cached byte redistribution" in error for error in _errors(manifest))


def test_prohibited_redistribution_forbids_offline_cache() -> None:
    manifest, _, _ = _inputs()
    imagery = _asset(manifest, "asset-synthetic-present-imagery")
    imagery["licensing"]["redistribution"] = "prohibited"
    imagery["cache_policy"]["cached_bytes_redistribution_allowed"] = False
    assert any("forbids offline cache" in error for error in _errors(manifest))


def test_fallback_policy_requires_existing_nonself_asset() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    terrain["runtime_policy"]["failure_mode"] = "fallback_allowed"
    terrain["runtime_policy"]["fallback_asset_ref"] = "asset-missing"
    assert any("fallback asset does not exist" in error for error in _errors(manifest))

    terrain["runtime_policy"]["fallback_asset_ref"] = terrain["asset_id"]
    assert any("cannot fall back to itself" in error for error in _errors(manifest))


def test_wgs84_coverage_bounds_are_validated() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    terrain["coverage"]["bbox_wgs84"] = [20.0, 50.0, 10.0, 40.0]
    errors = _errors(manifest)
    assert any("west must be less than east" in error for error in errors)
    assert any("south must be less than north" in error for error in errors)


def test_resolution_and_lod_order_are_validated() -> None:
    manifest, _, _ = _inputs()
    terrain = _asset(manifest, "asset-synthetic-present-terrain")
    terrain["coverage"]["min_resolution_m"] = 1000.0
    terrain["coverage"]["max_resolution_m"] = 30.0
    terrain["coverage"]["min_lod"] = 12
    terrain["coverage"]["max_lod"] = 2
    errors = _errors(manifest)
    assert any("min_resolution_m must be <=" in error for error in errors)
    assert any("min_lod must be <=" in error for error in errors)
