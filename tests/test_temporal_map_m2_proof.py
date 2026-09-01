import json
from pathlib import Path

import pytest

from scripts.build_temporal_map_m2_proof import (
    M2ProofError,
    SNAPSHOT_PATH,
    build_m2_inputs,
    build_m2_projection,
)


def _snapshot(tmp_path: Path, mutate) -> Path:
    value = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    mutate(value)
    path = tmp_path / "source_snapshot.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_m2_routes_one_wikidata_fact_through_existing_globe_adapter() -> None:
    world, state, projection, globe = build_m2_projection()
    assert world["status"] == "m2_one_source_proof"
    assert world["promotion_allowed"] is False
    assert world["m2_proof"]["provider_count"] == 1
    assert world["m2_proof"]["external_source_refs"] == [
        "source-wikidata-m2-one-source-proof"
    ]
    assert world["m2_proof"]["normalized_fact_count"] == 1
    assert world["m2_proof"]["inherited_gate_d_source_refs"]
    assert world["m2_proof"]["inherited_sources_are_m2_inputs"] is False
    assert state["temporal_selection"]["start"] == "1452-04-15"
    event = next(row for row in world["events"] if row["id"] == "event-leonardo-birth-wikidata-m2")
    assert event["source_refs"] == ["source-wikidata-m2-one-source-proof"]
    source = next(row for row in world["sources"] if row["id"] == event["source_refs"][0])
    assert source["rights"]["license"] == "CC0-1.0"
    item = next(row for row in projection["items"] if row.get("object_ref") == event["id"])
    assert item["temporal_membership"] == "active"
    assert item["spatial_status"] == "resolved"
    geometry = next(row for row in projection["geometries"] if row.get("owner_ref") == "place-anchiano-wikidata-m2")
    assert geometry["origin_kind"] == "place_reference_anchor"
    assert geometry["spatial_precision"] == "named_settlement"
    assert geometry["geometry"] == {"type": "Point", "coordinates": [10.938133333333, 43.799166666667]}
    assert any(row.get("object_ref") == event["id"] for row in globe["primitives"])


def test_m2_keeps_exact_position_and_routes_unknown() -> None:
    world, _state = build_m2_inputs()
    anchor = next(row for row in world["place_anchors"] if row["place_ref"] == "place-anchiano-wikidata-m2")
    trajectory = next(row for row in world["trajectories"] if row["id"] == "trajectory-leonardo-birth-wikidata-m2")
    assert anchor["historical_location_precision"] == "exact_position_within_named_settlement_unknown"
    assert [row["segment_kind"] for row in trajectory["segments"]] == ["presence"]
    assert all("geometry" not in row["spatial_extent"] for row in trajectory["segments"])


@pytest.mark.parametrize("mutate,message", [
    (lambda value: value["entities"]["Q762"]["statements"]["P569"][0].update({"rank": "normal"}), "P569 lost"),
    (lambda value: value["entities"]["Q762"]["statements"]["P19"][0]["value"].update({"entity_id": "Q999"}), "P19 does not resolve"),
    (lambda value: value["entities"]["Q154184"]["statements"]["P625"][0]["value"].update({"latitude": 999}), "outside WGS84"),
    (lambda value: value["entities"]["Q762"].update({"raw_entity_json_sha256": "0" * 64}), "raw_entity_json_sha256 drifted"),
    (lambda value: value["entities"]["Q762"].update({"revision_url": "https://example.com/revision"}), "revision_url drifted"),
    (lambda value: value["entities"]["Q762"]["statements"]["P569"][0].update({"statement_id": "fabricated"}), "P569 statement identity drifted"),
    (lambda value: value["entities"]["Q154184"]["statements"]["P625"][0].update({"reference_hashes": ["fabricated"]}), "P625 reference identity drifted"),
    (lambda value: value["provider"].update({"id": "second-provider"}), "one CC0 Wikidata provider"),
])
def test_m2_snapshot_drift_fails_closed(tmp_path: Path, mutate, message: str) -> None:
    with pytest.raises(M2ProofError, match=message):
        build_m2_inputs(snapshot_path=_snapshot(tmp_path, mutate))
