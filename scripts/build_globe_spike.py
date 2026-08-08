#!/usr/bin/env python3
"""Build the isolated ARTEMIS #343 Globe runtime spike as a static artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_render_projection_fixtures import build_all  # noqa: E402
from scripts.validate_geospatial_assets import validate_manifest  # noqa: E402


WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
PROJECTION_SCHEMA_PATH = ROOT / "fixtures" / "render_projection" / "v1" / "schema.json"
ASSET_MANIFEST_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "manifest.json"
ASSET_SCHEMA_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "schema.json"
ENGINE_EVALUATION_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "engine_evaluation.json"
EARTH_CONTEXT_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "synthetic_earth_context.geojson"
CAPABILITY_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "capability_path.geojson"
TEMPLATE_DIR = ROOT / "scripts" / "globe_spike"

SPIKE_ID = "artemis-globe-runtime-spike-v1"
EXPECTED_ENGINE = "maplibre-gl-js-5.24.0"
REQUIRED_OUTPUT_FILES = {
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


class SpikeBuildError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpikeBuildError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SpikeBuildError(f"{path} must contain a JSON object")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _validate_engine_evaluation(evaluation: dict[str, Any]) -> dict[str, Any]:
    selected_id = evaluation.get("selected_engine_id")
    candidates = {
        str(candidate.get("engine_id")): candidate
        for candidate in evaluation.get("candidates", [])
        if candidate.get("engine_id")
    }
    selected = candidates.get(str(selected_id))
    if selected is None:
        raise SpikeBuildError("selected engine does not exist in engine evaluation")
    if selected_id != EXPECTED_ENGINE:
        raise SpikeBuildError(
            f"#343 expected {EXPECTED_ENGINE}, evaluation selected {selected_id!r}"
        )

    required = {
        str(criterion["id"])
        for criterion in evaluation.get("criteria", [])
        if criterion.get("required") is True
    }
    statuses = selected.get("criteria") or {}
    missing = sorted(required - set(statuses))
    if missing:
        raise SpikeBuildError(f"selected engine missing required criteria: {missing}")
    failures = sorted(
        criterion
        for criterion in required
        if statuses.get(criterion) != "pass"
    )
    if failures:
        raise SpikeBuildError(
            f"selected engine has non-pass required criteria: {failures}"
        )
    return selected


def _validate_capability_path(path_fixture: dict[str, Any]) -> None:
    features = path_fixture.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise SpikeBuildError("capability path must contain exactly one feature")
    feature = features[0]
    if feature.get("geometry", {}).get("type") != "LineString":
        raise SpikeBuildError("capability path must be a LineString")
    properties = feature.get("properties") or {}
    if properties.get("capability_only") is not True:
        raise SpikeBuildError("capability path must be explicitly capability_only")
    if properties.get("semantic_role") != "renderer_capability_path":
        raise SpikeBuildError("capability path semantic_role mismatch")
    if properties.get("world_model_object_ref") is not None:
        raise SpikeBuildError("capability path must not have a World Model object ref")
    if properties.get("pick_as_knowledge") is not False:
        raise SpikeBuildError("capability path must not be pickable as knowledge")
    if "object_ref" in properties:
        raise SpikeBuildError("capability path must not expose canonical object_ref")


def _validate_earth_context(context: dict[str, Any], manifest: dict[str, Any]) -> None:
    asset_ids = {str(asset["asset_id"]) for asset in manifest.get("assets", [])}
    features = context.get("features")
    if not isinstance(features, list) or not features:
        raise SpikeBuildError("synthetic Earth context must contain features")
    for feature in features:
        properties = feature.get("properties") or {}
        if properties.get("capability_only") is not True:
            raise SpikeBuildError("all synthetic Earth context features must be capability_only")
        if "object_ref" in properties or "world_model_object_ref" in properties:
            raise SpikeBuildError("Earth context must not carry World Model object identity")
        asset_ref = properties.get("asset_ref")
        if asset_ref and asset_ref not in asset_ids:
            raise SpikeBuildError(f"Earth context references unknown asset: {asset_ref}")


def _terrain_runtime_status(manifest: dict[str, Any]) -> dict[str, Any]:
    terrain = next(
        (asset for asset in manifest.get("assets", []) if asset.get("asset_kind") == "terrain_elevation"),
        None,
    )
    if terrain is None:
        return {
            "asset_ref": None,
            "live_provider_selected": False,
            "status": "no_terrain_asset",
        }
    provider = terrain["provider"]
    endpoint = str(provider.get("endpoint_template") or "")
    live = provider.get("adapter_kind") == "raster_url_template" and endpoint.startswith(
        ("http://", "https://")
    )
    return {
        "asset_ref": terrain["asset_id"],
        "live_provider_selected": bool(live),
        "status": "live_raster_dem" if live else "synthetic_or_nonlive_provider",
        "vertical_reference": terrain["spatial_reference"]["vertical_reference"],
    }


def build_spike(output: Path) -> dict[str, Any]:
    world = _load(WORLD_PATH)
    state = _load(STATE_PATH)
    projection_schema = _load(PROJECTION_SCHEMA_PATH)
    asset_manifest = _load(ASSET_MANIFEST_PATH)
    asset_schema = _load(ASSET_SCHEMA_PATH)
    evaluation = _load(ENGINE_EVALUATION_PATH)
    earth_context = _load(EARTH_CONTEXT_PATH)
    capability_path = _load(CAPABILITY_PATH)

    asset_errors = validate_manifest(asset_manifest, schema=asset_schema, world=world)
    if asset_errors:
        raise SpikeBuildError("invalid geospatial asset manifest: " + "; ".join(asset_errors))
    selected_engine = _validate_engine_evaluation(evaluation)
    _validate_capability_path(capability_path)
    _validate_earth_context(earth_context, asset_manifest)

    projection, _maplibre_adapter, globe_adapter = build_all(
        world, state, projection_schema
    )

    if "Relation" not in projection.get("deferred_object_types", []):
        raise SpikeBuildError("runtime spike requires Relation rendering to remain deferred")
    if globe_adapter.get("vertical_semantics") != "not_modeled":
        raise SpikeBuildError("#343 must not introduce World Model vertical history")

    trajectory_gap = next(
        (
            item
            for item in projection.get("items", [])
            if item.get("object_ref") == "trajectory-mara-vale"
            and item.get("subobject_ref") == "trajectory-segment-gap"
        ),
        None,
    )
    if trajectory_gap is None or trajectory_gap.get("spatial_status") != "unresolved":
        raise SpikeBuildError("reviewed trajectory gap must remain unresolved in the spike")
    if trajectory_gap.get("geometry_refs"):
        raise SpikeBuildError("reviewed trajectory gap must not acquire geometry")

    primary_region = any(
        primitive.get("object_ref") == "region-fixture-basin"
        and primitive.get("subobject_ref") == "region-geometry-v2"
        for primitive in globe_adapter.get("primitives", [])
    )
    alternative_region = any(
        primitive.get("object_ref") == "region-fixture-basin"
        and primitive.get("subobject_ref") == "region-geometry-v2-alternative"
        for primitive in globe_adapter.get("primitives", [])
    )
    explicit_point = any(
        primitive.get("object_ref") == "event-far-observation"
        and primitive.get("primitive_kind") == "cartographic_point"
        for primitive in globe_adapter.get("primitives", [])
    )
    if not (primary_region and alternative_region and explicit_point):
        raise SpikeBuildError(
            "Globe adapter lacks required explicit point + primary/alternative Region evidence"
        )

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(TEMPLATE_DIR / "index.html.template", output / "index.html")
    shutil.copyfile(TEMPLATE_DIR / "runtime.js", output / "runtime.js")
    shutil.copyfile(TEMPLATE_DIR / "style.css", output / "style.css")

    _write_json(output / "projection.json", projection)
    _write_json(output / "globe-projection.json", globe_adapter)
    _write_json(output / "explorer-state.json", state)
    _write_json(output / "geospatial-assets.json", asset_manifest)
    _write_json(output / "synthetic-earth-context.geojson", earth_context)
    _write_json(output / "capability-path.geojson", capability_path)
    _write_json(output / "engine-evaluation.json", evaluation)

    metadata = {
        "schema_version": "1.0.0",
        "spike_id": SPIKE_ID,
        "build_contract_date": "2026-08-08",
        "engine_id": selected_engine["engine_id"],
        "engine_family": selected_engine["engine_family"],
        "world_slice_ref": state["world_slice_ref"],
        "explorer_state_ref": state["state_id"],
        "projection_id": projection["projection_id"],
        "semantic_item_count": len(projection.get("items", [])),
        "globe_primitive_count": len(globe_adapter.get("primitives", [])),
        "unresolved_item_count": len(
            [item for item in projection.get("items", []) if item.get("spatial_status") == "unresolved"]
        ),
        "trajectory_gap": {
            "object_ref": trajectory_gap["object_ref"],
            "subobject_ref": trajectory_gap["subobject_ref"],
            "spatial_status": trajectory_gap["spatial_status"],
            "geometry_refs": trajectory_gap["geometry_refs"],
            "uncertainty_refs": trajectory_gap["uncertainty_refs"],
        },
        "terrain": _terrain_runtime_status(asset_manifest),
        "capability_path_is_semantic": False,
        "backend_required": False,
        "public_pages_entrypoint": False,
        "input_sha256": {
            "world_model": _sha(world),
            "explorer_state": _sha(state),
            "geospatial_assets": _sha(asset_manifest),
            "engine_evaluation": _sha(evaluation),
            "earth_context": _sha(earth_context),
            "capability_path": _sha(capability_path),
        },
        "generated_sha256": {
            "neutral_projection": _sha(projection),
            "globe_projection": _sha(globe_adapter),
        },
    }
    _write_json(output / "build-meta.json", metadata)

    (output / "README.txt").write_text(
        "ARTEMIS Globe R&D spike (issue #343)\n\n"
        "This directory is generated. It is not the public ARTEMIS runtime.\n"
        "Serve it with any static HTTP server, for example:\n\n"
        f"  python -m http.server 8080 --directory {output}\n\n"
        "Then open http://127.0.0.1:8080/ in a browser.\n"
        "Network access is required only to load the pinned MapLibre GL JS engine from unpkg.\n"
        "The default Earth context/terrain fixtures are synthetic and local.\n",
        encoding="utf-8",
    )

    present = {path.name for path in output.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_OUTPUT_FILES - present)
    if missing:
        raise SpikeBuildError(f"build missing required files: {missing}")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "build" / "globe-spike",
        help="generated artifact directory (default: build/globe-spike)",
    )
    args = parser.parse_args()

    try:
        metadata = build_spike(args.output.resolve())
        print(
            "[PASS] Globe runtime spike build: "
            f"engine={metadata['engine_id']}; "
            f"primitives={metadata['globe_primitive_count']}; "
            f"unresolved={metadata['unresolved_item_count']}; "
            f"output={args.output.resolve()}"
        )
        return 0
    except (SpikeBuildError, KeyError, TypeError, ValueError, OSError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
