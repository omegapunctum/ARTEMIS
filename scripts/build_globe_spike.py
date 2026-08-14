#!/usr/bin/env python3
"""Build the isolated ARTEMIS #343 Globe runtime spike as a static artifact."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_leonardo_gate_d_inputs import (  # noqa: E402
    SLICE_ROOT as LEONARDO_SLICE_ROOT,
    build_gate_d_inputs,
)
from scripts.build_render_projection_fixtures import build_all  # noqa: E402
from scripts.validate_geospatial_assets import validate_manifest  # noqa: E402


WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
PROJECTION_SCHEMA_PATH = ROOT / "fixtures" / "render_projection" / "v1" / "schema.json"
ASSET_MANIFEST_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "gate_d_runtime.json"
ASSET_SCHEMA_PATH = ROOT / "fixtures" / "geospatial_assets" / "v1" / "schema.json"
ENGINE_EVALUATION_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "engine_evaluation.json"
ACCEPTANCE_PROFILES_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "gate_d_acceptance_profiles.json"
EARTH_CONTEXT_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "natural_earth_110m_land.geojson"
CAPABILITY_PATH = ROOT / "fixtures" / "globe_runtime" / "v1" / "capability_path.geojson"
TEMPLATE_DIR = ROOT / "scripts" / "globe_spike"

SPIKE_ID = "artemis-globe-gate-d-review-v1"
EXPECTED_ENGINE = "maplibre-gl-js-5.24.0"
DEFAULT_DATASET = "leonardo_gate_c"
DATASET_CHOICES = {DEFAULT_DATASET, "contract_fixture"}
REQUIRED_OUTPUT_FILES = {
    "index.html",
    "runtime.js",
    "style.css",
    "projection.json",
    "globe-projection.json",
    "explorer-state.json",
    "explorer-views.json",
    "geospatial-assets.json",
    "earth-context.geojson",
    "capability-path.geojson",
    "engine-evaluation.json",
    "acceptance-profiles.json",
    "knowledge-index.json",
    "build-meta.json",
    "README.txt",
}

LEONARDO_TEMPORAL_PRESETS = (
    {
        "preset_id": "full-slice",
        "label": "Full review interval · 8 Aug–31 Dec 1502",
        "temporal_selection": {
            "mode": "interval",
            "start": "1502-08-08",
            "end": "1502-12-31",
            "precision": "day",
            "calendar": "proleptic_gregorian",
        },
    },
    {
        "preset_id": "rimini-1502-08-08",
        "label": "Rimini source date · 8 Aug 1502",
        "temporal_selection": {
            "mode": "instant",
            "start": "1502-08-08",
            "end": "1502-08-08",
            "precision": "day",
            "calendar": "proleptic_gregorian",
        },
    },
    {
        "preset_id": "cesena-1502-08-10",
        "label": "Cesena source date · 10 Aug 1502",
        "temporal_selection": {
            "mode": "instant",
            "start": "1502-08-10",
            "end": "1502-08-10",
            "precision": "day",
            "calendar": "proleptic_gregorian",
        },
    },
    {
        "preset_id": "patent-1502-08-18",
        "label": "Borgia patent source date · 18 Aug 1502",
        "temporal_selection": {
            "mode": "instant",
            "start": "1502-08-18",
            "end": "1502-08-18",
            "precision": "day",
            "calendar": "proleptic_gregorian",
        },
    },
    {
        "preset_id": "cesenatico-1502-09-06",
        "label": "Cesenatico source date · 6 Sep 1502",
        "temporal_selection": {
            "mode": "instant",
            "start": "1502-09-06",
            "end": "1502-09-06",
            "precision": "day",
            "calendar": "proleptic_gregorian",
        },
    },
    {
        "preset_id": "imola-autumn-1502",
        "label": "Imola source interval · Sep–Nov 1502",
        "temporal_selection": {
            "mode": "interval",
            "start": "1502-09",
            "end": "1502-11",
            "precision": "month",
            "calendar": "proleptic_gregorian",
        },
    },
)


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


def _validate_acceptance_profiles(contract: dict[str, Any]) -> None:
    profiles = contract.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise SpikeBuildError("browser acceptance contract must contain profiles")
    profile_ids = [profile.get("profile_id") for profile in profiles]
    if profile_ids != ["desktop", "tablet", "mobile"]:
        raise SpikeBuildError(
            "browser acceptance profiles must remain ordered desktop/tablet/mobile"
        )
    if len(set(profile_ids)) != len(profile_ids):
        raise SpikeBuildError("browser acceptance profile ids must be unique")

    expected_layouts = {"desktop", "tablet", "mobile"}
    for profile in profiles:
        viewport = profile.get("viewport_css_px") or {}
        if not all(
            isinstance(viewport.get(axis), int) and viewport[axis] > 0
            for axis in ("width", "height")
        ):
            raise SpikeBuildError(
                f"browser profile {profile.get('profile_id')!r} has invalid viewport"
            )
        if profile.get("expected_layout_mode") not in expected_layouts:
            raise SpikeBuildError(
                f"browser profile {profile.get('profile_id')!r} has invalid layout mode"
            )
        if not isinstance(profile.get("prefers_reduced_motion"), bool):
            raise SpikeBuildError(
                f"browser profile {profile.get('profile_id')!r} lacks motion preference"
            )

    thresholds = contract.get("thresholds") or {}
    required_thresholds = {
        "max_horizontal_overflow_css_px",
        "min_interactive_target_css_px",
        "max_unnamed_interactive_controls",
        "min_globe_width_css_px",
        "min_globe_height_css_px",
    }
    if set(thresholds) != required_thresholds or any(
        not isinstance(value, int) or value < 0 for value in thresholds.values()
    ):
        raise SpikeBuildError("browser acceptance thresholds are incomplete or invalid")
    if profiles[-1]["prefers_reduced_motion"] is not True:
        raise SpikeBuildError("mobile browser profile must exercise reduced motion")
    if not contract.get("limitations"):
        raise SpikeBuildError("browser acceptance contract must disclose limitations")


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
    assets = {str(asset["asset_id"]): asset for asset in manifest.get("assets", [])}
    context_meta = context.get("artemis_context") or {}
    context_asset_ref = context_meta.get("asset_ref")
    if context_meta.get("capability_only") is not True:
        raise SpikeBuildError("Earth context collection must be capability_only")
    if context_meta.get("semantic_role") != "present_day_context":
        raise SpikeBuildError("Earth context collection must be present_day_context")
    if context_meta.get("historical_validity") is not None:
        raise SpikeBuildError("Earth context cannot declare historical validity")
    if context_asset_ref not in assets:
        raise SpikeBuildError(f"Earth context references unknown asset: {context_asset_ref}")
    context_asset = assets[context_asset_ref]
    if context_asset.get("semantic_role") != "present_day_context":
        raise SpikeBuildError("Earth context asset must remain present_day_context")
    if context_asset.get("provenance", {}).get("provenance_kind") == "synthetic_fixture":
        raise SpikeBuildError("Gate D Earth context must resolve to a real dataset")

    features = context.get("features")
    if not isinstance(features, list) or not features:
        raise SpikeBuildError("Earth context must contain features")
    for feature in features:
        properties = feature.get("properties") or {}
        if properties.get("capability_only") is not True:
            raise SpikeBuildError("all Earth context features must be capability_only")
        if properties.get("semantic_role") != "present_day_context":
            raise SpikeBuildError("all Earth context features must be present_day_context")
        if "object_ref" in properties or "world_model_object_ref" in properties:
            raise SpikeBuildError("Earth context must not carry World Model object identity")
        asset_ref = properties.get("asset_ref")
        if asset_ref != context_asset_ref:
            raise SpikeBuildError("Earth context feature asset_ref must match the collection")
        if asset_ref not in assets:
            raise SpikeBuildError(f"Earth context references unknown asset: {asset_ref}")


def _earth_context_runtime_status(
    context: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    asset_ref = context["artemis_context"]["asset_ref"]
    asset = next(asset for asset in manifest["assets"] if asset["asset_id"] == asset_ref)
    provider = asset["provider"]
    return {
        "asset_ref": asset_ref,
        "provider_id": provider["provider_id"],
        "real_dataset_selected": asset["provenance"]["provenance_kind"]
        != "synthetic_fixture",
        "status": "bundled_real_vector_context",
        "semantic_role": asset["semantic_role"],
        "network_required": asset["runtime_policy"]["network_required"],
        "secret_required": asset["runtime_policy"]["secret_required"],
    }


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


def _load_semantic_inputs(
    dataset: str,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if dataset == DEFAULT_DATASET:
        world, state = build_gate_d_inputs()
        return world, state, LEONARDO_SLICE_ROOT
    if dataset == "contract_fixture":
        return _load(WORLD_PATH), _load(STATE_PATH), WORLD_PATH.parent
    raise SpikeBuildError(f"unknown semantic dataset: {dataset!r}")


def _index_by_id(values: Any, *, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise SpikeBuildError(f"World Model {label} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get("id"), str):
            raise SpikeBuildError(f"World Model {label} must contain objects with string ids")
        item_id = value["id"]
        if item_id in indexed:
            raise SpikeBuildError(f"duplicate World Model {label} id: {item_id}")
        indexed[item_id] = value
    return indexed


def _build_knowledge_index(
    world: dict[str, Any], projection: dict[str, Any]
) -> dict[str, Any]:
    object_collections = {
        "Entity": "entities",
        "Event": "events",
        "State": "states",
        "Process": "processes",
        "Trajectory": "trajectories",
        "Region": "regions",
        "DerivedObservation": "derived_observations",
    }
    objects: dict[str, dict[str, Any]] = {}
    object_types: dict[str, str] = {}
    for object_type, collection in object_collections.items():
        for object_id, value in _index_by_id(
            world.get(collection, []), label=collection
        ).items():
            if object_id in objects:
                raise SpikeBuildError(f"duplicate canonical object id: {object_id}")
            objects[object_id] = value
            object_types[object_id] = object_type

    claims = _index_by_id(world.get("claims", []), label="claims")
    evidence_links = _index_by_id(
        world.get("evidence_links", []), label="evidence_links"
    )
    sources = _index_by_id(world.get("sources", []), label="sources")
    uncertainties = _index_by_id(
        world.get("uncertainties", []), label="uncertainties"
    )
    losses_by_item: dict[str, list[dict[str, Any]]] = {}
    for loss in projection.get("losses", []):
        if not isinstance(loss, dict) or not isinstance(loss.get("item_id"), str):
            raise SpikeBuildError("projection losses must reference item_id")
        losses_by_item.setdefault(loss["item_id"], []).append(loss)

    records: list[dict[str, Any]] = []
    for item in projection.get("items", []):
        item_id = item.get("item_id")
        object_ref = item.get("object_ref")
        object_type = item.get("object_type")
        if not isinstance(item_id, str) or not isinstance(object_ref, str):
            raise SpikeBuildError("projection item lacks canonical item/object identity")
        canonical_object = objects.get(object_ref)
        if canonical_object is None:
            raise SpikeBuildError(f"projection item references unknown object: {object_ref}")
        if object_types[object_ref] != object_type:
            raise SpikeBuildError(
                f"projection object type drift for {object_ref}: "
                f"{object_type!r} != {object_types[object_ref]!r}"
            )

        claim_refs = list(item.get("claim_refs") or [])
        evidence_refs = list(item.get("evidence_link_refs") or [])
        source_refs = list(item.get("source_refs") or [])
        uncertainty_refs = list(item.get("uncertainty_refs") or [])

        missing_claims = sorted(set(claim_refs) - set(claims))
        missing_evidence = sorted(set(evidence_refs) - set(evidence_links))
        missing_sources = sorted(set(source_refs) - set(sources))
        missing_uncertainties = sorted(set(uncertainty_refs) - set(uncertainties))
        if missing_claims or missing_evidence or missing_sources or missing_uncertainties:
            raise SpikeBuildError(
                f"knowledge closure failed for {item_id}: "
                f"claims={missing_claims}; evidence={missing_evidence}; "
                f"sources={missing_sources}; uncertainties={missing_uncertainties}"
            )

        embedded_evidence = [copy.deepcopy(evidence_links[ref]) for ref in evidence_refs]
        for evidence in embedded_evidence:
            if evidence.get("claim_id") not in claim_refs:
                raise SpikeBuildError(
                    f"evidence {evidence['id']} escapes projected claims for {item_id}"
                )
            if evidence.get("source_id") not in source_refs:
                raise SpikeBuildError(
                    f"evidence {evidence['id']} escapes projected sources for {item_id}"
                )
            if not str(evidence.get("locator") or "").strip():
                raise SpikeBuildError(f"evidence {evidence['id']} lacks a locator")

        embedded_sources: list[dict[str, Any]] = []
        for ref in source_refs:
            source = copy.deepcopy(sources[ref])
            uri = str(source.get("uri") or "")
            source["artifact_uri"] = uri if "://" in uri else f"./{uri}"
            embedded_sources.append(source)

        records.append(
            {
                "item_id": item_id,
                "object_ref": object_ref,
                "object_type": object_type,
                "subobject_ref": item.get("subobject_ref"),
                "label": canonical_object.get("label") or object_ref,
                "render_role": item.get("render_role"),
                "spatial_status": item.get("spatial_status"),
                "temporal_membership": item.get("temporal_membership"),
                "semantic_flags": copy.deepcopy(item.get("semantic_flags") or {}),
                "claim_refs": claim_refs,
                "evidence_link_refs": evidence_refs,
                "source_refs": source_refs,
                "uncertainty_refs": uncertainty_refs,
                "claims": [copy.deepcopy(claims[ref]) for ref in claim_refs],
                "evidence_links": embedded_evidence,
                "sources": embedded_sources,
                "uncertainties": [
                    copy.deepcopy(uncertainties[ref]) for ref in uncertainty_refs
                ],
                "projection_losses": copy.deepcopy(losses_by_item.get(item_id, [])),
            }
        )

    projection_item_ids = {item.get("item_id") for item in projection.get("items", [])}
    orphan_losses = sorted(set(losses_by_item) - projection_item_ids)
    if orphan_losses:
        raise SpikeBuildError(f"projection losses reference unknown items: {orphan_losses}")

    return {
        "schema_version": "1.0.0",
        "index_id": f"knowledge-index:{projection['projection_id']}",
        "package_id": world["package_id"],
        "world_slice_ref": world["world_slice"]["id"],
        "projection_id": projection["projection_id"],
        "fixture_mode": world.get("fixture_mode"),
        "historical_corpus_ready": world.get("historical_corpus_ready") is True,
        "corpus_status_label": world.get("corpus_status_label")
        or (
            "synthetic contract fixture · not historical evidence"
            if world.get("fixture_mode") == "synthetic_contract_fixture"
            else "candidate package · historical readiness not established"
        ),
        "promotion_allowed": world.get("promotion_allowed") is True,
        "deferred_object_types": copy.deepcopy(
            projection.get("deferred_object_types", [])
        ),
        "records": records,
    }


def _copy_local_sources(
    world: dict[str, Any], output: Path, *, source_root: Path
) -> dict[str, str]:
    source_root = source_root.resolve()
    copied: dict[str, str] = {}
    for source in world.get("sources", []):
        source_id = str(source.get("id") or "")
        uri = str(source.get("uri") or "")
        if not source_id or not uri or "://" in uri:
            continue
        relative = Path(uri)
        if relative.is_absolute() or ".." in relative.parts:
            raise SpikeBuildError(f"unsafe local source URI: {uri}")
        source_path = (source_root / relative).resolve()
        if source_root not in source_path.parents:
            raise SpikeBuildError(f"local source escapes package root: {uri}")
        try:
            payload = source_path.read_bytes()
        except OSError as exc:
            raise SpikeBuildError(f"cannot read local source {uri}: {exc}") from exc
        digest = hashlib.sha256(payload).hexdigest()
        if digest != source.get("sha256"):
            raise SpikeBuildError(f"local source checksum drift: {source_id}")
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        copied[source_id] = digest
    return copied


def _layer_subsets(layer_refs: list[str]) -> list[list[str]]:
    """Return every deterministic visibility combination for precomputed views."""

    return [
        list(combination)
        for size in range(len(layer_refs) + 1)
        for combination in itertools.combinations(layer_refs, size)
    ]


def _build_explorer_views(
    *,
    world: dict[str, Any],
    base_state: dict[str, Any],
    projection_schema: dict[str, Any],
    dataset: str,
) -> dict[str, Any]:
    """Precompute semantic views so the renderer never reinterprets time/layers."""

    layer_options = [
        {"layer_ref": layer["id"], "label": layer.get("label") or layer["id"]}
        for layer in world.get("layers", [])
    ]
    layer_refs = [option["layer_ref"] for option in layer_options]
    temporal_presets = (
        copy.deepcopy(list(LEONARDO_TEMPORAL_PRESETS))
        if dataset == DEFAULT_DATASET
        else [
            {
                "preset_id": "fixture-selection",
                "label": "Contract fixture selection",
                "temporal_selection": copy.deepcopy(
                    base_state["temporal_selection"]
                ),
            }
        ]
    )
    subsets = _layer_subsets(layer_refs)
    all_layers = sorted(layer_refs)
    views: list[dict[str, Any]] = []
    default_view_id: str | None = None

    for preset in temporal_presets:
        for active_layers in subsets:
            state = copy.deepcopy(base_state)
            sorted_layers = sorted(active_layers)
            layer_mask = "".join(
                "1" if layer_ref in sorted_layers else "0"
                for layer_ref in layer_refs
            )
            view_id = f"explorer-view-{preset['preset_id']}-layers-{layer_mask}"
            state["temporal_selection"] = copy.deepcopy(
                preset["temporal_selection"]
            )
            state["active_layer_refs"] = sorted_layers
            if not (
                preset["preset_id"] == temporal_presets[0]["preset_id"]
                and sorted_layers == all_layers
            ):
                state["state_id"] = f"{base_state['state_id']}--{preset['preset_id']}--{layer_mask}"

            projection, _maplibre, globe = build_all(
                world, state, projection_schema
            )
            if dataset == DEFAULT_DATASET and (
                projection.get("geometries") or globe.get("primitives")
            ):
                raise SpikeBuildError(
                    "precomputed Gate D views must preserve withheld geometry"
                )
            views.append(
                {
                    "view_id": view_id,
                    "temporal_preset_id": preset["preset_id"],
                    "active_layer_refs": sorted_layers,
                    "state": state,
                    "projection": projection,
                    "globe": globe,
                }
            )
            if (
                preset["preset_id"] == temporal_presets[0]["preset_id"]
                and sorted_layers == all_layers
            ):
                default_view_id = view_id

    if default_view_id is None:
        raise SpikeBuildError("explorer view index has no default view")
    return {
        "schema_version": "1.0.0",
        "index_id": f"explorer-view-index:{base_state['state_id']}",
        "default_view_id": default_view_id,
        "temporal_presets": temporal_presets,
        "layer_options": layer_options,
        "views": sorted(views, key=lambda value: value["view_id"]),
    }


def build_spike(output: Path, *, dataset: str = DEFAULT_DATASET) -> dict[str, Any]:
    world, state, source_root = _load_semantic_inputs(dataset)
    state = copy.deepcopy(state)
    state["active_layer_refs"] = sorted(state.get("active_layer_refs") or [])
    projection_schema = _load(PROJECTION_SCHEMA_PATH)
    asset_manifest = _load(ASSET_MANIFEST_PATH)
    asset_schema = _load(ASSET_SCHEMA_PATH)
    evaluation = _load(ENGINE_EVALUATION_PATH)
    acceptance_profiles = _load(ACCEPTANCE_PROFILES_PATH)
    earth_context = _load(EARTH_CONTEXT_PATH)
    capability_path = _load(CAPABILITY_PATH)

    asset_errors = validate_manifest(asset_manifest, schema=asset_schema, world=world)
    if asset_errors:
        raise SpikeBuildError("invalid geospatial asset manifest: " + "; ".join(asset_errors))
    selected_engine = _validate_engine_evaluation(evaluation)
    _validate_acceptance_profiles(acceptance_profiles)
    _validate_capability_path(capability_path)
    _validate_earth_context(earth_context, asset_manifest)

    projection, _maplibre_adapter, globe_adapter = build_all(
        world, state, projection_schema
    )
    explorer_views = _build_explorer_views(
        world=world,
        base_state=state,
        projection_schema=projection_schema,
        dataset=dataset,
    )

    if "Relation" not in projection.get("deferred_object_types", []):
        raise SpikeBuildError("runtime spike requires Relation rendering to remain deferred")
    if globe_adapter.get("vertical_semantics") != "not_modeled":
        raise SpikeBuildError("#343 must not introduce World Model vertical history")

    trajectory_gaps = [
        item
        for item in projection.get("items", [])
        if item.get("semantic_flags", {}).get("segment_kind") == "inferred_gap"
    ]
    if not trajectory_gaps:
        raise SpikeBuildError("runtime dataset must expose at least one trajectory gap")
    if any(
        item.get("spatial_status") != "unresolved" or item.get("geometry_refs")
        for item in trajectory_gaps
    ):
        raise SpikeBuildError("trajectory gaps must remain unresolved and geometry-free")

    if dataset == "contract_fixture":
        required_primitives = {
            ("event-far-observation", None),
            ("region-fixture-basin", "region-geometry-v2"),
            ("region-fixture-basin", "region-geometry-v2-alternative"),
        }
        actual_primitives = {
            (item.get("object_ref"), item.get("subobject_ref"))
            for item in globe_adapter.get("primitives", [])
        }
        if not required_primitives.issubset(actual_primitives):
            raise SpikeBuildError("contract fixture lost required renderer primitives")
    else:
        if world.get("historical_corpus_ready") is not False:
            raise SpikeBuildError("Gate D package must remain not historical-ready")
        if world.get("promotion_allowed") is not False:
            raise SpikeBuildError("Gate D package must remain non-promotable")
        if projection.get("geometries") or globe_adapter.get("primitives"):
            raise SpikeBuildError("frozen Gate C package must remain geometry-free")
        region_items = [
            item for item in projection.get("items", []) if item.get("object_type") == "Region"
        ]
        if {item.get("subobject_ref") for item in region_items} != {
            "region-version-borgia-romagna-1502",
            "region-version-documented-place-only-1502",
        }:
            raise SpikeBuildError("Gate C Region alternatives were not preserved")
        if any(item.get("spatial_status") != "unresolved" for item in region_items):
            raise SpikeBuildError("Gate C Region alternatives must remain unresolved")

    knowledge_index = _build_knowledge_index(world, projection)
    knowledge_item_ids = {
        record["item_id"] for record in knowledge_index["records"]
    }
    missing_view_records = sorted(
        {
            item["item_id"]
            for view in explorer_views["views"]
            for item in view["projection"].get("items", [])
        }
        - knowledge_item_ids
    )
    if missing_view_records:
        raise SpikeBuildError(
            f"precomputed views escape master knowledge closure: {missing_view_records}"
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
    _write_json(output / "explorer-views.json", explorer_views)
    _write_json(output / "geospatial-assets.json", asset_manifest)
    _write_json(output / "earth-context.geojson", earth_context)
    _write_json(output / "capability-path.geojson", capability_path)
    _write_json(output / "engine-evaluation.json", evaluation)
    _write_json(output / "acceptance-profiles.json", acceptance_profiles)
    _write_json(output / "knowledge-index.json", knowledge_index)
    copied_source_sha256 = _copy_local_sources(
        world, output, source_root=source_root
    )

    metadata = {
        "schema_version": "1.0.0",
        "spike_id": SPIKE_ID,
        "build_contract_date": "2026-08-13",
        "semantic_dataset": dataset,
        "engine_id": selected_engine["engine_id"],
        "engine_family": selected_engine["engine_family"],
        "world_slice_ref": state["world_slice_ref"],
        "explorer_state_ref": state["state_id"],
        "projection_id": projection["projection_id"],
        "semantic_item_count": len(projection.get("items", [])),
        "globe_primitive_count": len(globe_adapter.get("primitives", [])),
        "knowledge_record_count": len(knowledge_index["records"]),
        "explorer_view_count": len(explorer_views["views"]),
        "temporal_preset_count": len(explorer_views["temporal_presets"]),
        "unresolved_item_count": len(
            [item for item in projection.get("items", []) if item.get("spatial_status") == "unresolved"]
        ),
        "trajectory_gaps": [
            {
                "object_ref": item["object_ref"],
                "subobject_ref": item["subobject_ref"],
                "spatial_status": item["spatial_status"],
                "geometry_refs": item["geometry_refs"],
                "uncertainty_refs": item["uncertainty_refs"],
            }
            for item in trajectory_gaps
        ],
        "terrain": _terrain_runtime_status(asset_manifest),
        "earth_context": _earth_context_runtime_status(earth_context, asset_manifest),
        "capability_path_is_semantic": False,
        "backend_required": False,
        "public_pages_entrypoint": False,
        "browser_acceptance_profile_count": len(acceptance_profiles.get("profiles", [])),
        "input_sha256": {
            "world_model": _sha(world),
            "explorer_state": _sha(state),
            "geospatial_assets": _sha(asset_manifest),
            "engine_evaluation": _sha(evaluation),
            "acceptance_profiles": _sha(acceptance_profiles),
            "earth_context": _sha(earth_context),
            "capability_path": _sha(capability_path),
            "source_documents": copied_source_sha256,
        },
        "generated_sha256": {
            "neutral_projection": _sha(projection),
            "globe_projection": _sha(globe_adapter),
            "knowledge_index": _sha(knowledge_index),
            "explorer_views": _sha(explorer_views),
        },
    }
    _write_json(output / "build-meta.json", metadata)

    (output / "README.txt").write_text(
        "ARTEMIS source-aware Globe Gate D review artifact (#355)\n\n"
        "This directory is generated. It is not the public ARTEMIS runtime.\n"
        "Serve it with any static HTTP server, for example:\n\n"
        f"  python -m http.server 8080 --directory {output}\n\n"
        "Then open http://127.0.0.1:8080/ in a browser.\n"
        "Network access is required only to load the pinned MapLibre GL JS engine from unpkg.\n"
        "Earth context is the bundled Natural Earth 1:110m Land v4.0.0 present-day reference layer.\n"
        "It is real physical-geography context, not historical reconstruction; terrain remains synthetic/non-live.\n"
        "The default semantic input is the frozen, non-public Leonardo Gate C package.\n"
        "Its Claims remain draft/rejected, all historical geometry remains withheld, and promotion is not allowed.\n"
        "Time/layer controls switch only among precomputed Explorer State and Render Projection packages.\n"
        "The inspector resolves only package-derived canonical references, sources, locators and uncertainty.\n",
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
    parser.add_argument(
        "--dataset",
        choices=sorted(DATASET_CHOICES),
        default=DEFAULT_DATASET,
        help="semantic input package (default: frozen Leonardo Gate C package)",
    )
    args = parser.parse_args()

    try:
        metadata = build_spike(args.output.resolve(), dataset=args.dataset)
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
