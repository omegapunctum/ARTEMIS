import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts.build_globe_spike import build_spike
from scripts.build_render_projection_fixtures import build_all
from scripts.build_temporal_region_inputs import (
    PACKAGE,
    build_inputs,
    verify,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECTION_SCHEMA = json.loads(
    (ROOT / "fixtures/render_projection/v1/schema.json").read_text(encoding="utf-8")
)


def test_pinned_excerpt_is_reproducibly_verified() -> None:
    subprocess.run(
        ["python", "scripts/build_temporal_region_inputs.py", "--verify-excerpt"],
        cwd=ROOT,
        check=True,
    )


def test_source_audit_has_three_comparable_native_intervals() -> None:
    world, state, presets = build_inputs()
    region = world["regions"][0]
    versions = region["geometry_versions"]
    assert len(versions) == 3
    assert world["entities"][0]["label"] == "Roman Empire"
    assert state["dataset_identity"] == world["world_slice"]["dataset_identity"]
    assert [
        (v["temporal_extent"]["start"], v["temporal_extent"]["end"])
        for v in versions
    ] == [("0091", "0105"), ("0106", "0113"), ("0114", "0116")]
    assert [p["temporal_selection"]["start"] for p in presets] == ["0091", "0106", "0114"]
    assert all(v["reconstruction_mode"] == "scholarly_reconstruction" for v in versions)
    assert world["sources"][0]["provenance"]["license"] == "CC-BY-4.0"
    manifest = json.loads((PACKAGE / "source_manifest.json").read_text())
    assert manifest["comparability"]["territorial_concept"] == "political polity territory"
    assert manifest["comparability"]["temporal_precision"] == "native inclusive CE year intervals"


def test_comparability_rule_rejects_identity_drift() -> None:
    world, _state, _presets = build_inputs()
    # The verifier operates on source features, before World Model mapping.
    manifest = json.loads((PACKAGE / "source_manifest.json").read_text())
    excerpt = json.loads((PACKAGE / "sources/cliopatria-excerpt.json").read_text())
    changed = copy.deepcopy(excerpt["features"])
    changed[1]["properties"]["Name"] = "Roman Republic"
    with pytest.raises(ValueError, match="checksum|identity/comparability"):
        verify(changed, manifest)
    assert world["regions"][0]["label"].startswith("Roman Empire")


def test_each_canonical_time_projects_one_region_geometry_without_interpolation() -> None:
    world, state, presets = build_inputs()
    geometries = []
    for preset in presets:
        next_state = copy.deepcopy(state)
        next_state["temporal_selection"] = preset["temporal_selection"]
        projection, _maplibre, globe = build_all(world, next_state, PROJECTION_SCHEMA)
        item = next(
            candidate
            for candidate in projection["items"]
            if candidate["object_ref"] == "region-roman-empire"
        )
        assert item["object_type"] == "Region"
        assert item["temporal_membership"] == "active"
        assert item["spatial_status"] == "resolved"
        assert len(item["geometry_refs"]) == 1
        geometry = next(
            record for record in projection["geometries"]
            if record["geometry_ref"] == item["geometry_refs"][0]
        )
        geometries.append(geometry["geometry"])
        primitive = next(p for p in globe["primitives"] if p["item_id"] == item["item_id"])
        assert primitive["primitive_kind"] == "cartographic_multipolygon"
    assert len({json.dumps(value, sort_keys=True) for value in geometries}) == 3


def test_region_artifact_uses_shared_runtime_and_is_not_leonardo_publication(tmp_path: Path) -> None:
    output = tmp_path / "roman-region"
    metadata = build_spike(output, dataset="roman_region_proof")
    html = (output / "index.html").read_text(encoding="utf-8")
    readme = (output / "README.txt").read_text(encoding="utf-8")
    views = json.loads((output / "explorer-views.json").read_text(encoding="utf-8"))

    assert metadata["semantic_dataset"] == "roman_region_proof"
    assert metadata["temporal_preset_count"] == 3
    assert metadata["life_path_available"] is False
    assert metadata["public_pages_entrypoint"] is False
    assert "Roman Empire" in html
    assert "temporal-preset" in html
    assert "Leonardo Life Path" not in html
    assert "not a publication or user-value result" in readme
    assert (output / "source_manifest.json").exists()
    assert (output / "coverage_manifest.json").exists()
    assert len(views["views"]) == 6  # 3 times × 1-layer on/off subsets
    assert all(view["projection"]["source"]["explorer_state_ref"] for view in views["views"])
