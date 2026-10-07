#!/usr/bin/env python3
"""Compose the bounded, read-only shared Explorer from existing accepted inputs.

This is a render/input envelope, not an import into a new historical ontology.
The incumbent isolated builders remain independently reproducible.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import build_globe_spike as spike  # noqa: E402
from scripts import build_leonardo_gate_d_inputs as gate_d  # noqa: E402
from scripts import validate_leonardo_world_slice as gate_c_validation  # noqa: E402

TEMPLATE_DIR = ROOT / "scripts" / "unified_explorer"
FEATURES_PATH = ROOT / "data" / "features.geojson"
SOURCES_PATH = ROOT / "data" / "sources.json"
ENTRY_PROFILES = {"leonardo", "roman"}


class UnifiedBuildError(ValueError):
    """An existing input cannot be composed without inventing or dropping data."""


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UnifiedBuildError(f"cannot read input {path.name}: {exc}") from exc


def _bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_bytes(_bytes(value) + b"\n")


def adapt_architecture(features: Any, sources: Any) -> dict[str, Any]:
    """Retain raw metadata; never turn export flags/dates into historical support."""
    if not isinstance(features, dict) or features.get("type") != "FeatureCollection":
        raise UnifiedBuildError("architecture input must be a FeatureCollection")
    rows = features.get("features")
    if not isinstance(rows, list) or len(rows) != 31:
        raise UnifiedBuildError("bounded architecture input requires exactly 31 references")
    if not isinstance(sources, list):
        raise UnifiedBuildError("architecture sources must be an array")
    source_by_id = {}
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or source["id"] in source_by_id:
            raise UnifiedBuildError("architecture source identity is missing or duplicated")
        source_by_id[source["id"]] = source
    references, seen = [], set()
    for index, feature in enumerate(rows):
        if not isinstance(feature, dict):
            raise UnifiedBuildError("architecture reference must be a feature")
        identifier, properties = feature.get("id"), feature.get("properties")
        if not isinstance(identifier, str) or identifier in seen or not isinstance(properties, dict):
            raise UnifiedBuildError("architecture reference identity is missing or duplicated")
        seen.add(identifier)
        if properties.get("id") != identifier or properties.get("canonical_publish_id") != identifier:
            raise UnifiedBuildError("architecture reference identity mirrors disagree")
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if geometry.get("type") != "Point" or not isinstance(coords, list) or len(coords) != 2:
            raise UnifiedBuildError("architecture reference requires its original Point")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in coords) or not (-180 <= coords[0] <= 180 and -90 <= coords[1] <= 90):
            raise UnifiedBuildError("architecture reference coordinates are invalid")
        source_ids = properties.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids or any(not isinstance(s, str) or s not in source_by_id for s in source_ids):
            raise UnifiedBuildError("architecture reference has unresolved source IDs")
        links = properties.get("source_refs")
        if not isinstance(links, list) or any(not isinstance(link, dict) or link.get("source_id") not in source_ids for link in links):
            raise UnifiedBuildError("architecture reference has unresolved source links")
        aliases = properties.get("legacy_ids")
        if not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases):
            raise UnifiedBuildError("architecture reference aliases are invalid")
        references.append({
            "item_id": f"architecture:reference:{identifier}",
            "original_id": identifier,
            "aliases": copy.deepcopy(aliases),
            "layer_id": "architecture",
            "kind": "atemporal_reference",
            "historical_applicability": "unknown",
            "temporal_extent": None,
            "historical_position": None,
            "historical_precision": "unknown",
            "claim_refs": [],
            "evidence_link_refs": [],
            "input_pointer": f"data/features.geojson#/features/{index}",
            "input_pointer_role": "export_provenance_not_historical_evidence",
            "source_ids": copy.deepcopy(source_ids),
            "sources": [copy.deepcopy(source_by_id[s]) for s in source_ids],
            "geometry": copy.deepcopy(geometry),
            "raw_feature": copy.deepcopy(feature),
        })
    return {
        "role": "atemporal_reference_context",
        "historical_applicability": "unknown",
        "time_filtering": "excluded",
        "legacy_flags_role": "raw_export_metadata_not_historical_acceptance",
        "references": references,
        "sources": copy.deepcopy(sources),
    }


def _input_paths() -> list[Path]:
    """Explicit actual source/contract inputs used by the two incumbent builders."""
    return sorted({
        FEATURES_PATH, SOURCES_PATH,
        gate_d.SELECTION_PATH, gate_d.CLAIMS_PATH, gate_d.SOURCES_PATH,
        gate_d.CESENA_AMENDMENT_PATH,
        gate_d.COVERAGE_PATH, gate_d.DECISION_PATH, gate_d.PLACE_ANCHOR_PATH,
        gate_d.PLACE_ANCHOR_SCHEMA_PATH,
        gate_c_validation.SELECTION_SCHEMA_PATH, gate_c_validation.SOURCE_SCHEMA_PATH,
        gate_c_validation.COVERAGE_SCHEMA_PATH, gate_c_validation.COST_PATH,
        gate_c_validation.COST_SCHEMA_PATH, gate_c_validation.CLAIMS_SCHEMA_PATH,
        gate_c_validation.REVIEW_REGISTRY_PATH, gate_c_validation.REVIEW_REGISTRY_SCHEMA_PATH,
        ROOT / "fixtures" / "explorer_state" / "v1" / "schema.json",
        spike.PROJECTION_SCHEMA_PATH, spike.ASSET_MANIFEST_PATH, spike.ASSET_SCHEMA_PATH,
        spike.ENGINE_EVALUATION_PATH, spike.ACCEPTANCE_PROFILES_PATH,
        spike.EARTH_CONTEXT_PATH, spike.CAPABILITY_PATH, spike.LIFE_PATH_PRESENTATION_PATH,
        spike.MAJOR_LIFE_PACKAGE_PATH, spike.MAJOR_LIFE_RUNTIME_ANCHORS_PATH, spike.M5_CONTRACT_PATH,
        spike.REGION_PACKAGE_ROOT / "source_manifest.json",
        spike.REGION_PACKAGE_ROOT / "coverage_manifest.json",
        spike.REGION_PACKAGE_ROOT / "sources" / "cliopatria-excerpt.json",
    }, key=lambda p: str(p))


def _ledger(paths: list[Path]) -> list[dict[str, Any]]:
    result = []
    for path in paths:
        try:
            relative, payload = path.relative_to(ROOT).as_posix(), path.read_bytes()
        except (ValueError, OSError) as exc:
            raise UnifiedBuildError(f"input ledger cannot read repository input {path.name}") from exc
        result.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload), "artifact_uri": f"./inputs/{relative}"})
    return result


def _compose(leonardo_dir: Path, roman_dir: Path) -> dict[str, Any]:
    life_path = _read(leonardo_dir / "life-path.json")
    knowledge = _read(leonardo_dir / "knowledge-index.json")
    if len(life_path.get("presences", [])) != 11 or any(t.get("route_geometry") is not None for t in life_path.get("transitions", [])):
        raise UnifiedBuildError("accepted M5 Presence or null-route identity drift")
    omitted_views = life_path.pop("views")
    life_path["omitted_precomputed_views"] = {
        "count": len(omitted_views), "sha256": _digest(omitted_views),
        "role": "duplicate_presentation_views_replaced_by_one_shared_query",
    }
    roman_views = _read(roman_dir / "explorer-views.json")
    roman_knowledge = _read(roman_dir / "knowledge-index.json")
    roman_world, _, _ = spike.build_region_inputs()
    versions = []
    for geometry_version, preset in zip(roman_world["regions"][0]["geometry_versions"], roman_views["temporal_presets"]):
        matches = [v for v in roman_views["views"] if v["temporal_preset_id"] == preset["preset_id"] and v["active_layer_refs"]]
        if len(matches) != 1:
            raise UnifiedBuildError("Roman version must retain one native active-layer projection")
        view = matches[0]
        item = next((i for i in view["projection"]["items"] if i.get("subobject_ref") == geometry_version["id"]), None)
        if item is None:
            raise UnifiedBuildError("Roman native geometry item identity is missing")
        versions.append({
            "item_id": item["item_id"], "preset_id": preset["preset_id"],
            "interval": {"start": int(geometry_version["temporal_extent"]["start"]), "end": int(geometry_version["temporal_extent"]["end"])},
            "temporal_selection": copy.deepcopy(preset["temporal_selection"]),
            "geometry_version": copy.deepcopy(geometry_version),
            "projection": view["projection"], "globe": view["globe"],
            "state": view["state"],
        })
    if [(v["interval"]["start"], v["interval"]["end"]) for v in versions] != [(91, 105), (106, 113), (114, 116)]:
        raise UnifiedBuildError("Roman native intervals drifted")
    architecture = adapt_architecture(_read(FEATURES_PATH), _read(SOURCES_PATH))
    registry = []
    for presence in life_path["presences"]:
        registry.append({
            "item_id": presence["presence_item_id"], "layer_id": "leonardo", "kind": "presence",
            "presence_id": presence["presence_id"], "event_item_id": presence["event_item_id"],
            "label": presence["place_label"],
            "interval": {"start": int(presence["temporal"]["start"][:4]), "end": int(presence["temporal"]["end"][:4])},
            "original_ids": {"presence_id": presence["presence_id"], "presence_item_id": presence["presence_item_id"], "event_item_id": presence["event_item_id"], "place_ref": presence["place_ref"]},
            "source_pointer": f"lifePath#/presences/{presence['index']}",
        })
    registry += [{
        "item_id": v["item_id"], "canonical_item_id": v["item_id"], "layer_id": "roman", "kind": "region",
        "label": f"Roman Empire · {v['interval']['start']}–{v['interval']['end']} CE",
        "geometry_version_ref": v["geometry_version"]["id"], "preset_id": v["preset_id"],
        "interval": copy.deepcopy(v["interval"]),
        "original_ids": {"item_id": v["item_id"], "region_ref": "region-roman-empire", "geometry_version_ref": v["geometry_version"]["id"]},
        "source_pointer": f"roman#/versions/{index}",
    } for index, v in enumerate(versions)]
    registry += [{
        "item_id": r["item_id"], "layer_id": "architecture", "kind": "reference",
        "label": r["raw_feature"]["properties"].get("name_en") or r["raw_feature"]["properties"]["name_ru"],
        "interval": None, "original_id": r["original_id"], "aliases": r["aliases"],
        "original_ids": {"original_id": r["original_id"], "aliases": r["aliases"], "source_record_id": r["raw_feature"]["properties"].get("source_record_id")},
        "source_pointer": r["input_pointer"],
    } for r in architecture["references"]]
    if len({r["item_id"] for r in registry}) != len(registry):
        raise UnifiedBuildError("shared registry contains duplicate item identity")
    bundle = {
        "schema_version": "1.0.0", "bundle_id": "artemis-unified-layer-explorer-v1",
        "role": "read_only_input_and_projection_envelope", "historical_corpus_ready": False,
        "calendar": {"calendar": "proleptic_gregorian", "era": "CE", "min_year": 91, "max_year": 1519, "coverage_complete": False, "architecture_dates_define_coverage": False},
        "input_ledger": _ledger(_input_paths()), "registry": registry,
        "source_native_state_role": "preserved_canonical_inputs_orchestrated_by_application_workspace_state_not_a_canonical_state_migration",
        "leonardo": {"lifePath": life_path, "knowledge": knowledge, "explorerState": _read(leonardo_dir / "explorer-state.json"), "projection": _read(leonardo_dir / "projection.json"), "globe": _read(leonardo_dir / "globe-projection.json"), "sourcePackage": _read(spike.MAJOR_LIFE_PACKAGE_PATH), "runtimeAnchors": _read(spike.MAJOR_LIFE_RUNTIME_ANCHORS_PATH)},
        "roman": {"versions": versions, "knowledge": roman_knowledge, "sourceManifest": _read(spike.REGION_PACKAGE_ROOT / "source_manifest.json"), "worldInput": roman_world},
        "architecture": architecture,
    }
    bundle["content_sha256"] = _digest(bundle)
    return bundle


def compose_bundle() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="artemis-unified-inputs-") as temporary:
        base = Path(temporary)
        spike.build_spike(base / "leonardo", public_preview=True)
        spike.build_spike(base / "roman", dataset=spike.REGION_DATASET, public_preview=True)
        return _compose(base / "leonardo", base / "roman")


def build_unified_explorer(output: Path, *, entry_profile: str = "leonardo") -> dict[str, Any]:
    if entry_profile not in ENTRY_PROFILES:
        raise UnifiedBuildError("entry profile must be leonardo or roman")
    with tempfile.TemporaryDirectory(prefix="artemis-unified-build-") as temporary:
        base = Path(temporary)
        leonardo, roman = base / "leonardo", base / "roman"
        incumbent_meta = spike.build_spike(leonardo, public_preview=True)
        spike.build_spike(roman, dataset=spike.REGION_DATASET, public_preview=True)
        bundle = _compose(leonardo, roman)
        amendment_provenance = {
            **incumbent_meta["input_amendment"],
            "artifact_uri": "./inputs/" + gate_d.CESENA_AMENDMENT_PATH.relative_to(ROOT).as_posix(),
            "base_claims_artifact_uri": "./inputs/" + gate_d.CLAIMS_PATH.relative_to(ROOT).as_posix(),
        }
        ledger_by_path = {row["path"]: row for row in bundle["input_ledger"]}
        if ledger_by_path[amendment_provenance["path"]]["sha256"] != amendment_provenance["sha256"]:
            raise UnifiedBuildError("Cesena amendment input changed during composition")
        # Finish validating all input/template content before touching the output.
        template = (TEMPLATE_DIR / "index.html.template").read_text(encoding="utf-8")
        assets = {name: (TEMPLATE_DIR / name).read_bytes() for name in ("runtime.js", "style.css")}
        optional_locale = TEMPLATE_DIR / "localization.js"
        if optional_locale.exists():
            assets["localization.js"] = optional_locale.read_bytes()
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)
        public_profile = "globe" if entry_profile == "leonardo" else "region"
        for name, payload in assets.items():
            (output / name).write_bytes(payload)
        for name in ("geospatial-assets.json", "earth-context.geojson", "engine-evaluation.json", "acceptance-profiles.json"):
            shutil.copyfile(leonardo / name, output / name)
        for row in bundle["input_ledger"]:
            destination = output / "inputs" / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], destination)
            if hashlib.sha256(destination.read_bytes()).hexdigest() != row["sha256"]:
                raise UnifiedBuildError("copied input differs from its pinned ledger: " + row["path"])
        shutil.copyfile(roman / "source_manifest.json", output / "source_manifest.json")
        source_dir = roman / "sources"
        if source_dir.exists():
            shutil.copytree(source_dir, output / "sources")
        _write(output / "unified-bundle.json", bundle)
        bundle_sha = hashlib.sha256((output / "unified-bundle.json").read_bytes()).hexdigest()
        replacements = {
            "ENTRY_PROFILE": public_profile,
            "BUNDLE_SHA": bundle_sha,
            "CONTEXT_SHA": hashlib.sha256((output / "earth-context.geojson").read_bytes()).hexdigest(),
            "RUNTIME_SHA": hashlib.sha256(assets["runtime.js"]).hexdigest(),
            "STYLE_SHA": hashlib.sha256(assets["style.css"]).hexdigest(),
        }
        for key, value in replacements.items():
            template = template.replace("{{" + key + "}}", value)
        (output / "index.html").write_text(template, encoding="utf-8")
        metadata = {
            "schema_version": "1.0.0", "spike_id": "artemis-unified-layer-explorer-v1",
            "semantic_dataset": "unified_explorer", "entry_profile": entry_profile,
            "deployment_mode": "public_r_and_d_preview", "public_pages_entrypoint": True,
            "backend_required": False, "historical_corpus_ready": False,
            "engine_id": spike.EXPECTED_ENGINE, "engine_family": incumbent_meta["engine_family"],
            "bundle_id": bundle["bundle_id"], "bundle_sha256": bundle_sha,
            "bundle_content_sha256": bundle["content_sha256"],
            "leonardo_dataset_identity": bundle["leonardo"]["explorerState"]["dataset_identity"],
            "leonardo_input_amendment": amendment_provenance,
            "semantic_item_count": len(bundle["registry"]), "life_path_available": True,
            "life_path_presence_count": 11, "roman_version_count": 3, "architecture_reference_count": 31,
            "earth_context": incumbent_meta["earth_context"],
            "terrain": {"asset_ref": None, "runtime_enabled": False, "live_provider_selected": False, "status": "not_enabled_in_unified_runtime"},
            "input_sha256": {row["path"]: row["sha256"] for row in bundle["input_ledger"]},
            "generated_sha256": {"unified_bundle": bundle_sha},
            "value_validation": "UNVALIDATED",
            "source_native_state_role": bundle["source_native_state_role"],
        }
        _write(output / "build-meta.json", metadata)
        (output / "README.txt").write_text("ARTEMIS one persistent shared-layer Explorer. Public R&D preview; formal user value UNVALIDATED.\nLeonardo: 11 accepted presentation Presences, unknown/null historical routes.\nRoman Empire: three unchanged native interval reconstructions; no geometric union or interpolation.\nArchitecture: 31 atemporal imported reference points; historical applicability/position/precision unknown. Raw dates and legacy export flags are metadata only.\n", encoding="utf-8")
        return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--entry-profile", choices=sorted(ENTRY_PROFILES), default="leonardo")
    args = parser.parse_args()
    try:
        metadata = build_unified_explorer(args.output, entry_profile=args.entry_profile)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {metadata['semantic_item_count']} shared registry records; {metadata['bundle_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
