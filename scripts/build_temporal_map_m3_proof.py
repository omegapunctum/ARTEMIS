#!/usr/bin/env python3
"""Build the bounded Temporal Map M3 two-provider proof.

The merged Wikidata M2 Presence is retained unchanged as evidence. One
publisher-independent institutional source is added for the same birth event,
so date agreement and spatial-granularity refinement remain explicit without
inventing an exact birth house or new geometry.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_render_projection_fixtures import build_all  # noqa: E402
from scripts.build_temporal_map_m2_proof import (  # noqa: E402
    PROJECTION_SCHEMA_PATH,
    build_m2_inputs,
)


SNAPSHOT_PATH = (
    ROOT
    / "fixtures/source_proofs/leonardo_museo_birth/v1/source_snapshot.json"
)
M2_SOURCE_ID = "source-wikidata-m2-one-source-proof"
MUSEO_SOURCE_ID = "source-museo-leonardiano-m3-birth"
EVENT_ID = "event-leonardo-birth-wikidata-m2"
MUSEO_CLAIM_ID = "claim-leonardo-birth-vinci-museo-m3"
MUSEO_EVIDENCE_ID = "evidence-leonardo-birth-vinci-museo-m3"
MUSEO_UNCERTAINTY_ID = "uncertainty-leonardo-birth-place-granularity-m3"

EXPECTED_PROVIDER = {
    "id": "museo_leonardiano_vinci",
    "label": "Museo Leonardiano di Vinci",
    "organization": "Comune di Vinci — Museo Leonardiano",
    "source_type": "institutional_web_reference",
    "independence_scope": "independent_publisher_identity_only",
    "shared_upstream_evidence": "unknown",
}
EXPECTED_RIGHTS = {
    "factual_claim_use": "citation_and_factual_claims_only",
    "media_reuse": "prohibited_without_permission",
    "derived_geometry_use": "not_permitted_from_site_media",
    "rights_url": "https://museoleonardiano.it/en/regulations-for-reproductions/",
}
EXPECTED_CLAIMS = {
    "birth_date": "1452-04-15",
    "birth_locality_label": "Vinci",
    "anchiano_house_status": "traditional_attribution",
    "exact_birth_house_supported": False,
}
EXPECTED_PAGES = {
    "places": {
        "title": "Leonardo’s places",
        "url": "https://museoleonardiano.it/en/leonardo-in-vinci/leonardos-places/",
        "locator": "The Places of Birth and Childhood — first paragraph",
        "revision_identity": "not_published",
        "excerpts": [
            {
                "role": "birth_date_and_locality",
                "text": "Leonardo was born in Vinci on April 15, 1452.",
            },
            {
                "role": "traditional_house_attribution",
                "text": (
                    "The house where Leonardo is traditionally believed to have been "
                    "born is located in Anchiano."
                ),
            },
        ],
        "excerpt_sha256": (
            "a62d0c514c713eb87dacaa76ecbffdb7484c66b93fbf128ae64b1e46bef61720"
        ),
    },
    "biography": {
        "title": "Leonardo da Vinci",
        "url": "https://museoleonardiano.it/en/leonardo-in-vinci/biografia/",
        "locator": "Leonardo's life — 15 April 1452 entry",
        "revision_identity": "not_published",
        "reviewed_claims_sha256": (
            "fc82711b636ede7f5a30c2f1fb5108574c3a95f5aa01d65e024d83163931226a"
        ),
    },
}


class M3ProofError(ValueError):
    """Raised when the two-provider proof cannot be reproduced honestly."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise M3ProofError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise M3ProofError(f"{path} must contain a JSON object")
    return value


def _claims_digest(claims: dict[str, Any]) -> str:
    encoded = json.dumps(
        claims, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("schema_version") != "1.0.0":
        raise M3ProofError("M3 source snapshot schema drifted")
    if snapshot.get("snapshot_id") != "museo-leonardiano-leonardo-birth-2026-09-01":
        raise M3ProofError("M3 source snapshot identity drifted")
    if snapshot.get("snapshot_kind") != "reviewed_web_claim_excerpt":
        raise M3ProofError("M3 source snapshot kind drifted")
    if snapshot.get("retrieved_at") != "2026-09-01":
        raise M3ProofError("M3 source retrieval identity drifted")
    if snapshot.get("provider") != EXPECTED_PROVIDER:
        raise M3ProofError("M3 second-provider identity drifted")
    if snapshot.get("rights") != EXPECTED_RIGHTS:
        raise M3ProofError("M3 source rights boundary drifted")
    claims = snapshot.get("reviewed_claims")
    if claims != EXPECTED_CLAIMS:
        raise M3ProofError("M3 reviewed claims drifted")
    pages = snapshot.get("pages")
    if pages != EXPECTED_PAGES:
        raise M3ProofError("M3 page URL, locator or reviewed excerpt drifted")

    excerpt_text = "\n".join(
        row["text"] for row in pages["places"]["excerpts"]
    )
    excerpt_digest = hashlib.sha256(excerpt_text.encode("utf-8")).hexdigest()
    if excerpt_digest != pages["places"]["excerpt_sha256"]:
        raise M3ProofError("M3 reviewed excerpt digest does not close")
    if _claims_digest(claims) != pages["biography"]["reviewed_claims_sha256"]:
        raise M3ProofError("M3 reviewed claims digest does not close")
    return {
        "date": claims["birth_date"],
        "birth_locality_label": claims["birth_locality_label"],
        "anchiano_house_status": claims["anchiano_house_status"],
        "places_url": pages["places"]["url"],
        "biography_url": pages["biography"]["url"],
        "rights_url": snapshot["rights"]["rights_url"],
    }


def build_m3_inputs(
    *, snapshot_path: Path = SNAPSHOT_PATH
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return proof-only M3 World Model and Explorer State inputs."""

    data = _normalize_snapshot(_load(snapshot_path))
    world, state = build_m2_inputs()
    world, state = copy.deepcopy(world), copy.deepcopy(state)

    event = next(row for row in world["events"] if row["id"] == EVENT_ID)
    event["label"] = "Leonardo da Vinci — birth (M3 two-provider proof)"
    event["claim_refs"] = sorted([*event["claim_refs"], MUSEO_CLAIM_ID])
    event["uncertainty_refs"] = sorted(
        [*event["uncertainty_refs"], MUSEO_UNCERTAINTY_ID]
    )
    event["source_refs"] = sorted([*event["source_refs"], MUSEO_SOURCE_ID])
    event["temporal_extent"]["basis_claim_refs"] = sorted(
        [*event["temporal_extent"]["basis_claim_refs"], MUSEO_CLAIM_ID]
    )

    world["claims"].append(
        {
            "id": MUSEO_CLAIM_ID,
            "type": "Claim",
            "statement": (
                "Museo Leonardiano states that Leonardo was born in Vinci on "
                "15 April 1452 and classifies the Anchiano house as a traditional "
                "birthplace attribution."
            ),
            "target_refs": [EVENT_ID, "place-anchiano-wikidata-m2"],
            "claim_kind": "external_institutional_fact",
            "origin": "m3_source_adapter",
            "review_state": "proof_only",
            "confidence": "source_bound",
            "confidence_basis": (
                "Two reviewed Museo Leonardiano page locators; no immutable page "
                "revision is published."
            ),
            "evidence_state": "linked_institutional_reference",
            "evidence_link_refs": [MUSEO_EVIDENCE_ID],
            "uncertainty_refs": [MUSEO_UNCERTAINTY_ID],
        }
    )
    world["evidence_links"].append(
        {
            "id": MUSEO_EVIDENCE_ID,
            "type": "EvidenceLink",
            "claim_id": MUSEO_CLAIM_ID,
            "source_id": MUSEO_SOURCE_ID,
            "locator": (
                "Leonardo’s places · The Places of Birth and Childhood · first "
                "paragraph; Leonardo da Vinci · Leonardo's life · 15 April 1452 entry"
            ),
            "relation_to_claim": "supports_date_and_refines_spatial_precision",
            "evidence_strength": "direct_institutional_page_statement",
            "review_state": "verified_for_m3_proof",
            "reviewer": None,
        }
    )
    world["sources"].append(
        {
            "id": MUSEO_SOURCE_ID,
            "type": "Source",
            "title": "Museo Leonardiano — Leonardo birth pages",
            "source_type": "institutional_web_reference",
            "uri": data["places_url"],
            "review_state": "proof_only",
            "registry_locator": str(snapshot_path.relative_to(ROOT)),
            "organization": EXPECTED_PROVIDER["organization"],
            "relation_to_claim": "supports_and_spatially_refines_birth_presence",
            "intended_claims": [MUSEO_CLAIM_ID],
            "retrieved_at": "2026-09-01",
            "secondary_uri": data["biography_url"],
            "rights": {
                "license": "citation-and-factual-claims-only",
                "license_url": data["rights_url"],
                "data_use_permitted": True,
                "derived_geometry_use_permitted": False,
                "media_reuse_permitted": False,
            },
        }
    )
    world["uncertainties"].append(
        {
            "id": MUSEO_UNCERTAINTY_ID,
            "type": "Uncertainty",
            "dimension": "source_spatial_granularity",
            "description": (
                "Wikidata names Anchiano as place of birth; Museo Leonardiano states "
                "birth in Vinci and treats the Anchiano house as traditional. This is "
                "a granularity and attribution refinement, not evidence for an exact house."
            ),
            "effect": "do_not_treat_anchiano_reference_point_as_exact_birth_site",
            "basis_kind": "m3_two_provider_comparison",
            "basis": "wikidata-q762-p19-vs-museo-leonardiano-birth-pages",
            "basis_claim_refs": [
                "claim-leonardo-birth-anchiano-wikidata-m2",
                MUSEO_CLAIM_ID,
            ],
            "review_state": "proof_only",
            "target_refs": [EVENT_ID, MUSEO_CLAIM_ID],
            "subject_or_claim_ref": MUSEO_CLAIM_ID,
            "alternatives": [],
        }
    )

    for collection in ("claims", "evidence_links", "sources", "uncertainties"):
        world[collection] = sorted(world[collection], key=lambda row: row["id"])
    world["package_id"] += ":m3-museo-birth-comparison"
    world["status"] = "m3_multi_source_proof"
    world["promotion_allowed"] = False
    world["m3_proof"] = {
        "authorized_by": "docs/work/2026-09-01_TEMPORAL_MAP_M2_EXIT_DECISION_v1.md",
        "provider_count": 2,
        "provider_ids": ["wikidata", EXPECTED_PROVIDER["id"]],
        "provider_independence": "independent_publisher_identity_only",
        "shared_upstream_evidence_unknown": True,
        "external_source_refs": [M2_SOURCE_ID, MUSEO_SOURCE_ID],
        "normalized_presence_count": 1,
        "inherited_gate_d_source_refs": copy.deepcopy(
            world["m2_proof"]["inherited_gate_d_source_refs"]
        ),
        "inherited_sources_are_m3_inputs": False,
        "world_source_record_count": len(world["sources"]),
        "source_comparison": {
            "temporal_relation": "exact_agreement",
            "temporal_value": data["date"],
            "spatial_relation": "granularity_refinement_not_direct_conflict",
            "wikidata_place_assertion": "Anchiano",
            "museo_birth_locality_assertion": data["birth_locality_label"],
            "museo_anchiano_house_status": data["anchiano_house_status"],
            "exact_birth_house_supported": False,
            "museum_geometry_contribution": False,
        },
        "public_runtime_authorized": False,
        "generic_federation_authorized": False,
        "m4_authorized": False,
    }
    state["state_id"] = "explorer-state-leonardo-birth-m3-two-provider"
    return world, state


def build_m3_projection(*, snapshot_path: Path = SNAPSHOT_PATH):
    world, state = build_m3_inputs(snapshot_path=snapshot_path)
    projection, _maplibre, globe = build_all(
        world, state, _load(PROJECTION_SCHEMA_PATH)
    )
    return world, state, projection, globe


if __name__ == "__main__":
    world, state, projection, globe = build_m3_projection()
    proof = world["m3_proof"]
    print(
        json.dumps(
            {
                "milestone": "M3_MULTI_SOURCE_PROOF",
                "provider_count": proof["provider_count"],
                "provider_ids": proof["provider_ids"],
                "provider_independence": proof["provider_independence"],
                "shared_upstream_evidence_unknown": proof[
                    "shared_upstream_evidence_unknown"
                ],
                "presence_count": proof["normalized_presence_count"],
                "inherited_gate_d_source_count": len(
                    proof["inherited_gate_d_source_refs"]
                ),
                "inherited_sources_are_m3_inputs": proof[
                    "inherited_sources_are_m3_inputs"
                ],
                "world_source_record_count": proof["world_source_record_count"],
                "temporal_relation": proof["source_comparison"]["temporal_relation"],
                "spatial_relation": proof["source_comparison"]["spatial_relation"],
                "projection_id": projection["projection_id"],
                "globe_primitive_count": len(globe["primitives"]),
                "runtime_authorized": False,
                "generic_federation_authorized": False,
                "m4_authorized": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
