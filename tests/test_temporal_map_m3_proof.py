import json
from pathlib import Path

import pytest

from scripts.build_temporal_map_m3_proof import (
    EVENT_ID,
    M2_SOURCE_ID,
    M3ProofError,
    MUSEO_CLAIM_ID,
    MUSEO_SOURCE_ID,
    MUSEO_UNCERTAINTY_ID,
    SNAPSHOT_PATH,
    build_m3_inputs,
    build_m3_projection,
)


def _snapshot(tmp_path: Path, mutate) -> Path:
    value = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    mutate(value)
    path = tmp_path / "source_snapshot.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_m3_preserves_two_providers_one_presence_through_projection() -> None:
    world, _state, projection, globe = build_m3_projection()
    proof = world["m3_proof"]
    assert proof["provider_count"] == 2
    assert proof["provider_ids"] == ["wikidata", "museo_leonardiano_vinci"]
    assert proof["provider_independence"] == "independent_publisher_identity_only"
    assert proof["shared_upstream_evidence_unknown"] is True
    assert proof["external_source_refs"] == [M2_SOURCE_ID, MUSEO_SOURCE_ID]
    assert proof["normalized_presence_count"] == 1
    assert len(proof["inherited_gate_d_source_refs"]) == 11
    assert proof["inherited_sources_are_m3_inputs"] is False
    assert proof["world_source_record_count"] == 13
    assert proof["public_runtime_authorized"] is False
    assert proof["generic_federation_authorized"] is False
    assert proof["m4_authorized"] is False
    assert world["m2_proof"]["m3_authorized"] is False

    event = next(row for row in world["events"] if row["id"] == EVENT_ID)
    assert MUSEO_CLAIM_ID in event["claim_refs"]
    assert MUSEO_CLAIM_ID in event["temporal_extent"]["basis_claim_refs"]
    assert MUSEO_CLAIM_ID not in event["spatial_extent"]["basis_claim_refs"]
    assert MUSEO_UNCERTAINTY_ID in event["uncertainty_refs"]

    item = next(row for row in projection["items"] if row.get("object_ref") == EVENT_ID)
    assert item["source_refs"] == [MUSEO_SOURCE_ID, M2_SOURCE_ID]
    assert MUSEO_UNCERTAINTY_ID in item["uncertainty_refs"]
    assert any(row.get("object_ref") == EVENT_ID for row in globe["primitives"])


def test_m3_classifies_agreement_and_spatial_refinement_without_geometry() -> None:
    world, _state = build_m3_inputs()
    comparison = world["m3_proof"]["source_comparison"]
    assert comparison == {
        "temporal_relation": "exact_agreement",
        "temporal_value": "1452-04-15",
        "spatial_relation": "granularity_refinement_not_direct_conflict",
        "wikidata_place_assertion": "Anchiano",
        "museo_birth_locality_assertion": "Vinci",
        "museo_anchiano_house_status": "traditional_attribution",
        "exact_birth_house_supported": False,
        "museum_geometry_contribution": False,
    }
    source = next(row for row in world["sources"] if row["id"] == MUSEO_SOURCE_ID)
    assert source["rights"]["data_use_permitted"] is True
    assert source["rights"]["derived_geometry_use_permitted"] is False
    assert source["rights"]["media_reuse_permitted"] is False


@pytest.mark.parametrize(
    "mutate,message",
    [
        (
            lambda value: value["provider"].update({"id": "wikidata"}),
            "second-provider identity drifted",
        ),
        (
            lambda value: value.update({"retrieved_at": "unknown"}),
            "retrieval identity drifted",
        ),
        (
            lambda value: value["rights"].update({"media_reuse": "permitted"}),
            "rights boundary drifted",
        ),
        (
            lambda value: value["pages"]["places"].update(
                {"url": "https://example.com"}
            ),
            "page URL, locator or reviewed excerpt drifted",
        ),
        (
            lambda value: value["pages"]["places"]["excerpts"][0].update(
                {"text": "invented"}
            ),
            "page URL, locator or reviewed excerpt drifted",
        ),
        (
            lambda value: value["reviewed_claims"].update(
                {"exact_birth_house_supported": True}
            ),
            "reviewed claims drifted",
        ),
    ],
)
def test_m3_snapshot_drift_fails_closed(tmp_path: Path, mutate, message: str) -> None:
    with pytest.raises(M3ProofError, match=message):
        build_m3_inputs(snapshot_path=_snapshot(tmp_path, mutate))
