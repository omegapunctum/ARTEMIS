#!/usr/bin/env python3
"""Build the bounded Temporal Map M2 one-source proof.

One pinned Wikidata snapshot becomes one Leonardo birth Presence and passes
through the existing World Model -> Explorer State -> Render Projection ->
Globe adapter. The result is proof-only and does not extend the public path.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_leonardo_gate_d_inputs import build_gate_d_inputs  # noqa: E402
from scripts.build_render_projection_fixtures import build_all  # noqa: E402


SNAPSHOT_PATH = ROOT / "fixtures/source_proofs/leonardo_wikidata_birth/v1/source_snapshot.json"
PROJECTION_SCHEMA_PATH = ROOT / "fixtures/render_projection/v1/schema.json"

EXPECTED_PROVIDER = {
    "id": "wikidata",
    "data_access": "https://www.wikidata.org/wiki/Wikidata:Data_access",
    "license": "CC0-1.0",
    "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
}
EXPECTED_ENTITIES = {
    "Q762": {
        "label": "Leonardo da Vinci",
        "revision": 2533380508,
        "revision_url": "https://www.wikidata.org/w/index.php?title=Q762&oldid=2533380508",
        "raw_entity_json_sha256": "109bf80f56e22ec4078ce7def6103fd54e600ac1dd4316f2ab572ff92c0e64cc",
    },
    "Q154184": {
        "label": "Anchiano",
        "revision": 2504702048,
        "revision_url": "https://www.wikidata.org/w/index.php?title=Q154184&oldid=2504702048",
        "raw_entity_json_sha256": "f4a2a87b8cf1824950a951b334cd204e0d2a9b9016c3ecc836e1ed75f47b206f",
    },
}
EXPECTED_STATEMENTS = {
    "P569": {
        "statement_id": "Q762$E556FF29-077E-47B3-995A-A5F6E5ABFDC9",
        "reference_hashes": [
            "72850ceb9f2401f4f45f57fbabe274e7a5218cc8",
            "22bd2579a39fff36a621589f559e9ac86976e97a",
            "e3d930e024c6a20f6b81f3cb078b99b1767d42bc",
            "fd38c16d153aa0df9c2885726011012b1fd81164",
        ],
    },
    "P19": {
        "statement_id": "q762$160C942C-22DB-4AE8-8F23-D1C5FE1F2EF6",
        "reference_hashes": [
            "22bd2579a39fff36a621589f559e9ac86976e97a",
            "e3d930e024c6a20f6b81f3cb078b99b1767d42bc",
            "642708de9c7676df694bfc92da8ff3ddd607436b",
        ],
    },
    "P625": {
        "statement_id": "q154184$5C9E0E15-0D1C-43D4-B822-397818D76C90",
        "reference_hashes": ["9a24f7c0208b05d6be97077d855671d1dfdbc0dd"],
    },
}


class M2ProofError(ValueError):
    """Raised when the one-source proof cannot be reproduced without invention."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise M2ProofError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise M2ProofError(f"{path} must contain a JSON object")
    return value


def _one_statement(entity: dict[str, Any], property_id: str, rank: str) -> dict[str, Any]:
    rows = (entity.get("statements") or {}).get(property_id)
    if not isinstance(rows, list) or len(rows) != 1:
        raise M2ProofError(f"{property_id} must contain exactly one proof statement")
    row = rows[0]
    if row.get("snaktype") != "value" or row.get("rank") != rank:
        raise M2ProofError(f"{property_id} lost its required value/rank semantics")
    if not row.get("statement_id") or not row.get("reference_hashes"):
        raise M2ProofError(f"{property_id} lacks statement/reference identity")
    return row


def _normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    provider = snapshot.get("provider") or {}
    if any(provider.get(key) != value for key, value in EXPECTED_PROVIDER.items()):
        raise M2ProofError("M2 is locked to one CC0 Wikidata provider")
    if snapshot.get("retrieved_at") != "2026-09-01":
        raise M2ProofError("M2 retrieval identity drifted")
    entities = snapshot.get("entities") or {}
    if set(entities) != {"Q762", "Q154184"}:
        raise M2ProofError("M2 snapshot must close exactly Q762 and its linked birth place")
    person, place = entities["Q762"], entities["Q154184"]
    for entity_id, expected in EXPECTED_ENTITIES.items():
        entity = entities[entity_id]
        for field, value in expected.items():
            if entity.get(field) != value:
                raise M2ProofError(f"M2 {entity_id} {field} drifted")

    birth = _one_statement(person, "P569", "preferred")
    birthplace = _one_statement(person, "P19", "normal")
    coordinate = _one_statement(place, "P625", "normal")
    for property_id, statement in (
        ("P569", birth), ("P19", birthplace), ("P625", coordinate)
    ):
        expected = EXPECTED_STATEMENTS[property_id]
        if statement.get("statement_id") != expected["statement_id"]:
            raise M2ProofError(f"{property_id} statement identity drifted")
        if statement.get("reference_hashes") != expected["reference_hashes"]:
            raise M2ProofError(f"{property_id} reference identity drifted")
    if birth["value"] != {
        "time": "+1452-04-15T00:00:00Z",
        "precision": 11,
        "calendar_entity": "Q1985786",
    }:
        raise M2ProofError("P569 is not the reviewed day-precision Gregorian value")
    if birthplace["value"].get("entity_id") != "Q154184":
        raise M2ProofError("P19 does not resolve to the included Anchiano entity")
    coordinate_value = coordinate["value"]
    if coordinate_value.get("globe_entity") != "Q2":
        raise M2ProofError("P625 must use the Earth globe entity")
    longitude = coordinate_value.get("longitude")
    latitude = coordinate_value.get("latitude")
    if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
        raise M2ProofError("P625 lacks numeric longitude/latitude")
    if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
        raise M2ProofError("P625 coordinate is outside WGS84 bounds")
    return {
        "date": "1452-04-15",
        "place_label": place["label"],
        "coordinates": [longitude, latitude],
        "statement_ids": [
            birth["statement_id"], birthplace["statement_id"], coordinate["statement_id"]
        ],
        "revision_urls": [person["revision_url"], place["revision_url"]],
    }


def build_m2_inputs(*, snapshot_path: Path = SNAPSHOT_PATH) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return proof-only World Model and Explorer State inputs."""

    data = _normalize_snapshot(_load(snapshot_path))
    world, state = build_gate_d_inputs()
    world, state = copy.deepcopy(world), copy.deepcopy(state)
    inherited_source_refs = sorted(source["id"] for source in world["sources"])

    source_id = "source-wikidata-m2-one-source-proof"
    place_id = "place-anchiano-wikidata-m2"
    event_id = "event-leonardo-birth-wikidata-m2"
    trajectory_id = "trajectory-leonardo-birth-wikidata-m2"
    segment_id = "segment-leonardo-birth-anchiano-wikidata-m2"
    claim_id = "claim-leonardo-birth-anchiano-wikidata-m2"
    anchor_claim_id = "claim-anchiano-coordinate-wikidata-m2"
    event_evidence_id = "evidence-leonardo-birth-wikidata-m2"
    anchor_evidence_id = "evidence-anchiano-coordinate-wikidata-m2"
    uncertainty_id = "uncertainty-anchiano-historical-position-wikidata-m2"
    layer_refs = ["layer-leonardo-trajectory"]

    temporal = {
        "kind": "instant", "start": data["date"], "end": data["date"],
        "precision": "day", "calendar": "proleptic_gregorian",
        "certainty": "source_bound_structured_value", "basis_claim_refs": [claim_id],
    }
    spatial = {
        "kind": "named_place", "place_ref": place_id,
        "precision": "named_settlement", "basis_claim_refs": [claim_id, anchor_claim_id],
    }
    world["entities"].append({
        "id": place_id, "type": "Entity", "label": data["place_label"],
        "entity_kind": "Place", "claim_refs": [anchor_claim_id],
        "uncertainty_refs": [uncertainty_id], "layer_refs": layer_refs,
        "source_refs": [source_id], "spatial_extent": copy.deepcopy(spatial),
        "proof_status": "m2_one_source_only",
    })
    world["events"].append({
        "id": event_id, "type": "Event",
        "label": "Leonardo da Vinci — birth (Wikidata M2 proof)",
        "claim_refs": [claim_id], "uncertainty_refs": [uncertainty_id],
        "layer_refs": layer_refs, "source_refs": [source_id],
        "temporal_extent": copy.deepcopy(temporal), "spatial_extent": copy.deepcopy(spatial),
        "proof_status": "m2_one_source_only",
    })
    world["trajectories"].append({
        "id": trajectory_id, "type": "Trajectory",
        "label": "Leonardo birth Presence — Wikidata M2 proof",
        "subject_ref": "entity-leonardo-da-vinci",
        "coverage": "One external fact from one provider; not a life trajectory.",
        "claim_refs": [claim_id], "uncertainty_refs": [uncertainty_id],
        "layer_refs": layer_refs, "source_refs": [source_id],
        "temporal_extent": copy.deepcopy(temporal),
        "segments": [{
            "id": segment_id, "segment_kind": "presence",
            "temporal_extent": copy.deepcopy(temporal), "spatial_extent": copy.deepcopy(spatial),
            "claim_refs": [claim_id], "uncertainty_refs": [uncertainty_id],
            "source_refs": [source_id],
        }],
        "proof_status": "m2_one_source_only",
    })
    world["place_anchors"].append({
        "anchor_id": "anchor-anchiano-wikidata-m2", "place_ref": place_id,
        "label": data["place_label"], "source_id": source_id,
        "source_entity_id": "Q154184", "source_uri": data["revision_urls"][1],
        "claim_id": anchor_claim_id, "evidence_link_id": anchor_evidence_id,
        "geometry": {"type": "Point", "coordinates": data["coordinates"]},
        "spatial_precision": "named_settlement",
        "historical_location_precision": "exact_position_within_named_settlement_unknown",
        "semantic_role": "present_day_settlement_reference", "uncertainty_ref": uncertainty_id,
    })
    world["claims"].extend([
        {
            "id": claim_id, "type": "Claim",
            "statement": "Wikidata Q762 states 15 April 1452 and links place of birth to Anchiano (Q154184).",
            "target_refs": [event_id, place_id], "claim_kind": "external_structured_fact",
            "origin": "m2_source_adapter", "review_state": "proof_only",
            "confidence": "source_bound", "confidence_basis": "Pinned P569 and P19 statements.",
            "evidence_state": "linked_open_data", "evidence_link_refs": [event_evidence_id],
            "uncertainty_refs": [uncertainty_id],
        },
        {
            "id": anchor_claim_id, "type": "Claim",
            "statement": "Wikidata Q154184 P625 is a present-day Anchiano reference, not an exact historical position.",
            "target_refs": [place_id], "claim_kind": "contextual_reference",
            "origin": "m2_source_adapter", "review_state": "proof_only",
            "confidence": "source_bound", "confidence_basis": "Pinned P625 statement.",
            "evidence_state": "linked_open_data", "evidence_link_refs": [anchor_evidence_id],
            "uncertainty_refs": [uncertainty_id],
        },
    ])
    world["evidence_links"].extend([
        {
            "id": event_evidence_id, "type": "EvidenceLink", "claim_id": claim_id,
            "source_id": source_id, "locator": " · ".join(data["statement_ids"][:2]),
            "relation_to_claim": "supports_external_structured_fact",
            "evidence_strength": "direct_structured_value",
            "review_state": "verified_for_m2_proof", "reviewer": None,
        },
        {
            "id": anchor_evidence_id, "type": "EvidenceLink", "claim_id": anchor_claim_id,
            "source_id": source_id, "locator": data["statement_ids"][2],
            "relation_to_claim": "supports_contextual_reference",
            "evidence_strength": "direct_structured_value",
            "review_state": "verified_for_m2_proof", "reviewer": None,
        },
    ])
    world["sources"].append({
        "id": source_id, "type": "Source", "title": "Wikidata M2 pinned one-source proof",
        "source_type": "structured_knowledge_graph", "uri": data["revision_urls"][0],
        "review_state": "proof_only", "registry_locator": str(snapshot_path.relative_to(ROOT)),
        "organization": "Wikimedia Foundation / Wikidata community",
        "relation_to_claim": "supplies_structured_values",
        "intended_claims": [claim_id, anchor_claim_id], "retrieved_at": "2026-09-01",
        "rights": {
            "license": "CC0-1.0", "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
            "data_use_permitted": True, "derived_geometry_use_permitted": True,
        },
    })
    world["uncertainties"].append({
        "id": uncertainty_id, "type": "Uncertainty", "dimension": "spatial_precision",
        "description": "Q154184 P625 is a modern named-settlement reference, not Leonardo's historical position or a birth house.",
        "effect": "render_at_named_settlement_precision_only",
        "basis_kind": "wikidata_m2_source_snapshot", "basis": data["statement_ids"][2],
        "basis_claim_refs": [claim_id, anchor_claim_id], "review_state": "proof_only",
        "target_refs": [event_id, place_id, claim_id, anchor_claim_id],
        "subject_or_claim_ref": claim_id, "alternatives": [],
    })

    for collection in ("entities", "events", "trajectories", "place_anchors", "claims", "evidence_links", "sources", "uncertainties"):
        key = "anchor_id" if collection == "place_anchors" else "id"
        world[collection] = sorted(world[collection], key=lambda row: row[key])
    world["package_id"] += ":m2-wikidata-birth-proof"
    world["status"] = "m2_one_source_proof"
    world["promotion_allowed"] = False
    world["m2_proof"] = {
        "provider_count": 1,
        "external_source_refs": [source_id],
        "normalized_fact_count": 1,
        "inherited_gate_d_source_refs": inherited_source_refs,
        "inherited_sources_are_m2_inputs": False,
        "public_runtime_authorized": False,
        "m3_authorized": False,
    }
    state["state_id"] = "explorer-state-leonardo-birth-wikidata-m2"
    state["temporal_selection"] = {
        "mode": "instant", "start": data["date"], "end": data["date"],
        "precision": "day", "calendar": "proleptic_gregorian",
    }
    state["selection"] = {
        "primary_object_ref": event_id,
        "selected_object_refs": ["entity-leonardo-da-vinci", event_id, place_id],
        "comparison_object_refs": [],
    }
    state["context"] = {
        "local_context_refs": ["entity-leonardo-da-vinci", event_id, place_id, trajectory_id],
        "global_context_refs": [], "derived_observation_refs": [],
    }
    state["active_focus"] = {
        "trajectory_ref": trajectory_id, "trajectory_segment_ref": segment_id,
        "region_ref": None, "region_geometry_ref": None, "reconstruction_ref": None,
    }
    state["comparison_scope"] = {"mode": "none", "reference_refs": []}
    return world, state


def build_m2_projection(*, snapshot_path: Path = SNAPSHOT_PATH):
    world, state = build_m2_inputs(snapshot_path=snapshot_path)
    projection, _maplibre, globe = build_all(world, state, _load(PROJECTION_SCHEMA_PATH))
    return world, state, projection, globe


if __name__ == "__main__":
    world, state, projection, globe = build_m2_projection()
    proof = world["m2_proof"]
    print(json.dumps({
        "milestone": "M2_ONE_SOURCE_PROOF",
        "provider_count": proof["provider_count"],
        "provider": "wikidata", "fact_count": proof["normalized_fact_count"],
        "inherited_gate_d_source_count": len(proof["inherited_gate_d_source_refs"]),
        "inherited_sources_are_m2_inputs": proof["inherited_sources_are_m2_inputs"],
        "world_package": world["package_id"], "explorer_state": state["state_id"],
        "projection_id": projection["projection_id"],
        "globe_primitive_count": len(globe["primitives"]),
        "runtime_authorized": False, "m3_authorized": False,
    }, ensure_ascii=False, indent=2))
