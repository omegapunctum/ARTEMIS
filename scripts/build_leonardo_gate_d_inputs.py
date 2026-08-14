#!/usr/bin/env python3
"""Build read-only Gate D inputs from the frozen Leonardo Gate C package.

The adapter is deliberately lossy and fail-closed. It preserves canonical IDs,
draft/rejected review states, source locators, withheld geometry, unresolved
routes, and the non-public/non-promotable Gate C lifecycle. It does not mutate
the frozen package or claim that candidate content is reviewed historical truth.
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SLICE_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1"
SELECTION_PATH = SLICE_ROOT / "selection_manifest.json"
CLAIMS_PATH = SLICE_ROOT / "claims_manifest.json"
SOURCES_PATH = SLICE_ROOT / "source_registry.json"
COVERAGE_PATH = SLICE_ROOT / "coverage_manifest.json"
DECISION_PATH = SLICE_ROOT / "gate_c_decision.json"
PLACE_ANCHOR_PATH = (
    ROOT / "fixtures" / "globe_runtime" / "v1" / "leonardo_place_anchors.json"
)
PLACE_ANCHOR_SCHEMA_PATH = (
    ROOT / "fixtures" / "globe_runtime" / "v1" / "place_anchor_schema.json"
)

CALENDAR = "proleptic_gregorian"
LOCAL_OBJECT_IDS = {
    "entity-leonardo-da-vinci",
    "entity-cesare-borgia",
    "place-rimini",
    "place-cesena",
    "place-cesenatico",
    "place-imola",
    "event-leonardo-rimini-note",
    "event-leonardo-cesena-survey",
    "event-leonardo-borgia-patent",
    "event-leonardo-cesenatico-port-note",
    "event-leonardo-imola-map-context",
    "state-leonardo-in-borgia-service",
    "process-leonardo-romagna-surveying",
    "trajectory-leonardo-romagna-1502",
    "region-duchy-romagna-context",
}
GLOBAL_OBJECT_IDS = {
    "event-ottoman-turkmen-displacement-1502",
    "state-safavid-isma-il-i",
}
TYPE_COLLECTIONS = {
    "Entity": "entities",
    "Event": "events",
    "State": "states",
    "Process": "processes",
    "Trajectory": "trajectories",
    "Region": "regions",
}
TEMPORAL_VALUE_RE = re.compile(r"^-?\d{1,6}(?:-\d{2}(?:-\d{2})?)?$")


class GateDInputError(ValueError):
    """Raised when the frozen package cannot be adapted without invention."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateDInputError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateDInputError(f"{path} must contain a JSON object")
    return value


def _load_place_anchor_registry() -> dict[str, Any]:
    registry = _load(PLACE_ANCHOR_PATH)
    schema = _load(PLACE_ANCHOR_SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(registry),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise GateDInputError(f"invalid Gate D place anchor registry: {details}")

    anchors = registry["anchors"]
    expected_places = {"place-rimini", "place-cesena", "place-cesenatico", "place-imola"}
    place_refs = [str(anchor["place_ref"]) for anchor in anchors]
    if set(place_refs) != expected_places or len(place_refs) != len(set(place_refs)):
        raise GateDInputError(
            "Gate D place anchor registry must close exactly the four reviewed settlements"
        )

    source_id = registry["source"]["source_id"]
    uncertainty_id = registry["uncertainty"]["uncertainty_id"]
    identities: set[str] = set()
    for anchor in anchors:
        for key in ("anchor_id", "claim_id", "evidence_link_id"):
            identity = str(anchor[key])
            if identity in identities:
                raise GateDInputError(f"duplicate Gate D place anchor identity: {identity}")
            identities.add(identity)
        if anchor["source_id"] != source_id:
            raise GateDInputError(f"{anchor['anchor_id']}: source_id escapes registry source")
        if anchor["uncertainty_ref"] != uncertainty_id:
            raise GateDInputError(
                f"{anchor['anchor_id']}: uncertainty_ref escapes registry uncertainty"
            )
        if not str(anchor["source_uri"]).endswith("/" + str(anchor["source_entity_id"])):
            raise GateDInputError(
                f"{anchor['anchor_id']}: source URI does not close its Wikidata entity ID"
            )
    return registry


def _adapt_place_anchor_overlay(
    registry: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    source = registry["source"]
    uncertainty = registry["uncertainty"]
    anchors = sorted(registry["anchors"], key=lambda item: item["place_ref"])
    claims: list[dict[str, Any]] = []
    evidence_links: list[dict[str, Any]] = []
    target_refs: list[str] = []

    for anchor in anchors:
        longitude, latitude = anchor["geometry"]["coordinates"]
        target_refs.append(anchor["claim_id"])
        claims.append(
            {
                "id": anchor["claim_id"],
                "type": "Claim",
                "statement": (
                    f"Wikidata P625 supplies the present-day named-settlement reference "
                    f"point for {anchor['label']} at {latitude}, {longitude} (WGS84). "
                    "This is not an exact historical location."
                ),
                "target_refs": [anchor["place_ref"]],
                "claim_kind": "contextual_reference",
                "origin": "gate_d_reference_overlay",
                "review_state": "draft",
                "confidence": "source_bound",
                "confidence_basis": (
                    "The coordinate is bound to a specific Wikidata entity and may be "
                    "used only at named-settlement precision."
                ),
                "evidence_state": "linked_open_data",
                "evidence_link_refs": [anchor["evidence_link_id"]],
                "uncertainty_refs": [anchor["uncertainty_ref"]],
            }
        )
        evidence_links.append(
            {
                "id": anchor["evidence_link_id"],
                "type": "EvidenceLink",
                "claim_id": anchor["claim_id"],
                "source_id": anchor["source_id"],
                "locator": (
                    f"{anchor['source_entity_id']} · P625 coordinate location · "
                    f"{anchor['source_uri']}"
                ),
                "relation_to_claim": "supports_contextual_reference",
                "evidence_strength": "direct_structured_value",
                "review_state": "verified_contextual_reference",
                "reviewer": None,
            }
        )

    adapted_source = {
        "id": source["source_id"],
        "type": "Source",
        "title": source["title"],
        "source_type": source["source_type"],
        "uri": source["url"],
        "review_state": source["curation_state"],
        "registry_locator": source["locator"],
        "organization": source["organization"],
        "relation_to_claim": "supports_contextual_reference",
        "intended_claims": [anchor["claim_id"] for anchor in anchors],
        "retrieved_at": source["retrieved_at"],
        "rights": copy.deepcopy(source["rights"]),
    }
    adapted_uncertainty = {
        "id": uncertainty["uncertainty_id"],
        "type": "Uncertainty",
        "dimension": uncertainty["dimension"],
        "description": uncertainty["description"],
        "effect": uncertainty["effect"],
        "basis_kind": "gate_d_place_anchor_registry",
        "basis": registry["registry_id"],
        "basis_claim_refs": sorted(target_refs),
        "review_state": "draft",
        "target_refs": sorted(target_refs),
        "subject_or_claim_ref": sorted(target_refs)[0],
        "alternatives": [],
    }
    return claims, evidence_links, adapted_source, adapted_uncertainty


def _index(rows: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise GateDInputError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str):
            raise GateDInputError(f"{label} rows must contain string {key}")
        identity = row[key]
        if identity in result:
            raise GateDInputError(f"duplicate {label} identity: {identity}")
        result[identity] = row
    return result


def _temporal_extent(hint: dict[str, Any] | None) -> dict[str, Any] | None:
    if not hint or hint.get("value") is None:
        return None
    value = str(hint["value"])
    parts = value.split("/", 1)
    start = parts[0] if parts[0] != "unknown" else None
    end = parts[1] if len(parts) == 2 and parts[1] != "unknown" else start
    for candidate in (start, end):
        if candidate is not None and not TEMPORAL_VALUE_RE.fullmatch(candidate):
            raise GateDInputError(f"unsupported frozen temporal value: {value!r}")
    extent = {
        "kind": "instant" if start is not None and start == end else "closed_interval",
        "start": start,
        "end": end,
        "precision": hint.get("precision") or "range",
        "calendar": CALENDAR,
        "certainty": "candidate_requires_claim_binding",
        "basis_claim_refs": [],
    }
    return extent


def _spatial_extent(
    *, mode: str | None, place_ref: str | None, claim_refs: list[str]
) -> dict[str, Any]:
    if mode == "named_place" and place_ref:
        kind = "named_place"
    else:
        kind = "unknown"
    return {
        "kind": kind,
        "place_ref": place_ref,
        "precision": "withheld_no_reviewed_geometry",
        "basis_claim_refs": list(claim_refs),
    }


def _claim_refs_by_target(claims: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for claim_id, claim in claims.items():
        target = str(claim.get("target_object_ref") or "")
        if target:
            result.setdefault(target, []).append(claim_id)
    return {key: sorted(values) for key, values in result.items()}


def _uncertainty_refs_by_target(
    uncertainties: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for uncertainty_id, uncertainty in uncertainties.items():
        for target in uncertainty.get("target_refs") or []:
            result.setdefault(str(target), []).append(uncertainty_id)
    return {key: sorted(set(values)) for key, values in result.items()}


def _object_uncertainties(
    object_id: str,
    claim_refs: list[str],
    by_target: dict[str, list[str]],
) -> list[str]:
    values = set(by_target.get(object_id, []))
    for claim_ref in claim_refs:
        values.update(by_target.get(claim_ref, []))
    return sorted(values)


def _base_object(
    candidate: dict[str, Any],
    *,
    claim_refs: list[str],
    uncertainty_refs: list[str],
) -> dict[str, Any]:
    return {
        "id": candidate["object_id"],
        "type": candidate["object_type"],
        "label": candidate["label"],
        "claim_refs": list(claim_refs),
        "uncertainty_refs": list(uncertainty_refs),
        "layer_refs": list(candidate["layer_refs"]),
        "source_refs": list(candidate["source_refs"]),
        "gate_c_curation_state": candidate["curation_state"],
        "gate_c_spatial_mode": candidate["spatial_mode"],
        "gate_c_notes": candidate["notes"],
    }


def _adapt_candidate(
    candidate: dict[str, Any],
    *,
    claims_by_target: dict[str, list[str]],
    uncertainties_by_target: dict[str, list[str]],
) -> dict[str, Any]:
    object_id = candidate["object_id"]
    object_type = candidate["object_type"]
    claim_refs = claims_by_target.get(object_id, [])
    uncertainty_refs = _object_uncertainties(
        object_id, claim_refs, uncertainties_by_target
    )
    result = _base_object(
        candidate, claim_refs=claim_refs, uncertainty_refs=uncertainty_refs
    )
    temporal_extent = _temporal_extent(candidate.get("temporal_hint"))

    if object_type == "Entity":
        result["entity_kind"] = "Place" if object_id.startswith("place-") else "Person"
        return result

    if temporal_extent is not None:
        temporal_extent["basis_claim_refs"] = list(claim_refs)
        result["temporal_extent"] = temporal_extent

    if object_type in {"Event", "State", "Process"}:
        result["spatial_extent"] = _spatial_extent(
            mode=candidate.get("spatial_mode"),
            place_ref=None,
            claim_refs=claim_refs,
        )
    if object_type == "Process":
        result["process_mode"] = "analytical_model"
        result["stages"] = []
    elif object_type == "State":
        result["state_kind"] = "source_bound_context"
        result["value"] = "candidate_not_ready"
    elif object_type == "Trajectory":
        parent_extent = copy.deepcopy(temporal_extent)
        result["coverage"] = candidate["notes"]
        result["segments"] = []
        for segment in candidate.get("segments") or []:
            segment_extent = copy.deepcopy(parent_extent)
            if segment_extent is not None:
                segment_extent["basis_claim_refs"] = list(claim_refs)
                segment_extent["certainty"] = "inherited_parent_candidate_extent"
            result["segments"].append(
                {
                    "id": segment["segment_id"],
                    "segment_kind": segment["segment_kind"],
                    "temporal_extent": segment_extent,
                    "spatial_extent": _spatial_extent(
                        mode=segment.get("spatial_mode"),
                        place_ref=segment.get("place_ref"),
                        claim_refs=claim_refs,
                    ),
                    "claim_refs": list(claim_refs),
                    "uncertainty_refs": list(uncertainty_refs),
                    "source_refs": list(segment.get("source_refs") or []),
                }
            )
    elif object_type == "Region":
        result["region_kind"] = "source_bound_political_context"
        result["temporal_states"] = copy.deepcopy(candidate.get("temporal_states") or [])
        result["geometry_versions"] = []
        version_claims = {
            "title_based_context": "claim-romagna-title-based-context",
            "documented_place_only_context": "claim-romagna-documented-place-only-alternative",
        }
        region_context_claims = sorted(set(claim_refs) - set(version_claims.values()))
        for version in candidate.get("versions") or []:
            version_claim = version_claims.get(version["alternative_kind"])
            if version_claim not in claim_refs:
                raise GateDInputError(
                    f"Region version {version['version_id']} lacks its frozen Claim binding"
                )
            projected_claim_refs = sorted([version_claim, *region_context_claims])
            version_uncertainties = _object_uncertainties(
                object_id, projected_claim_refs, uncertainties_by_target
            )
            result["geometry_versions"].append(
                {
                    "id": version["version_id"],
                    "reconstruction_mode": version["reconstruction_mode"],
                    "is_primary": False,
                    "temporal_extent": _temporal_extent(version["temporal_hint"]),
                    "spatial_extent": {
                        "kind": "unknown",
                        "precision": version["geometry_status"],
                        "basis_claim_refs": projected_claim_refs,
                    },
                    "claim_refs": projected_claim_refs,
                    "uncertainty_refs": version_uncertainties,
                    "alternative_group_id": version["alternative_group_id"],
                    "alternative_kind": version["alternative_kind"],
                    "interpretation": version["interpretation"],
                    "source_refs": list(version["source_refs"]),
                }
            )
    return result


def _adapt_claim(claim: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(claim)
    result["id"] = result.pop("claim_id")
    result["type"] = "Claim"
    result["target_refs"] = [result.pop("target_object_ref")]
    return result


def _adapt_evidence(link: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(link)
    result["id"] = result.pop("evidence_link_id")
    result["type"] = "EvidenceLink"
    return result


def _adapt_source(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": source["source_id"],
        "type": "Source",
        "title": source["title"],
        "source_type": source["source_type"],
        "uri": source["url"],
        "review_state": source["curation_state"],
        "registry_locator": source["locator"],
        "organization": source["organization"],
        "relation_to_claim": source["relation_to_claim"],
        "intended_claims": list(source["intended_claims"]),
        "rights": copy.deepcopy(source["rights"]),
    }


def _adapt_uncertainty(uncertainty: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(uncertainty)
    result["id"] = result.pop("uncertainty_id")
    result["type"] = "Uncertainty"
    result["subject_or_claim_ref"] = result["target_refs"][0]
    result["alternatives"] = []
    return result


def _assert_frozen_boundary(
    selection: dict[str, Any], claims: dict[str, Any], decision: dict[str, Any]
) -> None:
    if decision.get("status") != "GATE_C_COMPLETED" or decision.get("decision") != "FREEZE":
        raise GateDInputError("Gate C decision must remain completed/FREEZE")
    if decision.get("promotion_allowed") is not False or decision.get("next_gate") != "D":
        raise GateDInputError("Gate C package must remain non-promotable input to Gate D")
    if selection.get("publication_status") != "non_public_curation":
        raise GateDInputError("Leonardo package must remain non-public")
    readiness = selection.get("readiness") or {}
    if readiness.get("historical_objects_ready") is not False:
        raise GateDInputError("Gate D adapter cannot promote candidate historical objects")
    if selection.get("relation_policy", {}).get("stored_relations") != []:
        raise GateDInputError("Relation semantics remain deferred")
    if any(item.get("geometry") is not None for item in selection.get("candidate_objects", [])):
        raise GateDInputError("Gate D adapter refuses candidate geometry")
    review_states = {item.get("review_state") for item in claims.get("claims", [])}
    if not review_states.issubset({"draft", "rejected"}):
        raise GateDInputError("Gate D adapter refuses promoted Claim review states")


def build_gate_d_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    """Return deterministic World Model-compatible and Explorer State inputs."""

    from scripts.validate_leonardo_world_slice import validate_package

    validate_package()
    selection = _load(SELECTION_PATH)
    claims_package = _load(CLAIMS_PATH)
    sources_package = _load(SOURCES_PATH)
    coverage = _load(COVERAGE_PATH)
    decision = _load(DECISION_PATH)
    place_anchor_registry = _load_place_anchor_registry()
    _assert_frozen_boundary(selection, claims_package, decision)

    candidates = _index(selection["candidate_objects"], "object_id", "candidate objects")
    claims = _index(claims_package["claims"], "claim_id", "Claims")
    uncertainties = _index(
        claims_package["uncertainties"], "uncertainty_id", "Uncertainties"
    )
    claims_by_target = _claim_refs_by_target(claims)
    uncertainties_by_target = _uncertainty_refs_by_target(uncertainties)

    adapted: dict[str, list[dict[str, Any]]] = {
        collection: [] for collection in TYPE_COLLECTIONS.values()
    }
    for candidate in candidates.values():
        adapted[TYPE_COLLECTIONS[candidate["object_type"]]].append(
            _adapt_candidate(
                candidate,
                claims_by_target=claims_by_target,
                uncertainties_by_target=uncertainties_by_target,
            )
        )
    for collection in adapted.values():
        collection.sort(key=lambda item: item["id"])

    anchor_by_place = {
        str(anchor["place_ref"]): anchor
        for anchor in place_anchor_registry["anchors"]
    }
    for entity in adapted["entities"]:
        if entity.get("entity_kind") != "Place":
            continue
        anchor = anchor_by_place.get(str(entity["id"]))
        if anchor is None:
            raise GateDInputError(f"Place lacks Gate D reference anchor: {entity['id']}")
        if entity.get("label") != anchor.get("label"):
            raise GateDInputError(
                f"Place anchor label drift for {entity['id']}: "
                f"{anchor.get('label')!r} != {entity.get('label')!r}"
            )
        entity["spatial_extent"] = {
            "kind": "named_place",
            "place_ref": entity["id"],
            "precision": anchor["spatial_precision"],
            "basis_claim_refs": [anchor["claim_id"]],
        }

    anchor_claims, anchor_evidence, anchor_source, anchor_uncertainty = (
        _adapt_place_anchor_overlay(place_anchor_registry)
    )

    identity = {
        "kind": "frozen_gate_c_repository_package",
        "value": f"{selection['slice_id']}@{decision['reviewed_content_digest']}",
    }
    layer_rows = [
        {
            "id": layer["layer_id"],
            "type": "Layer",
            "label": layer["label"],
            "role": layer["role"],
            "coverage_rule": coverage["coverage_statement"],
            "claim_refs": [],
            "uncertainty_refs": [],
        }
        for layer in selection["layers"]
    ]
    temporal_scope = selection["temporal_scope"]
    place_refs = sorted(
        object_id for object_id in candidates if object_id.startswith("place-")
    )
    world: dict[str, Any] = {
        "schema_version": "1.0.0",
        "package_id": f"gate-d-read-only:{selection['slice_id']}",
        "status": "gate_d_read_only_adapter",
        "fixture_mode": "frozen_gate_c_candidate_package",
        "historical_corpus_ready": False,
        "corpus_status_label": "frozen Gate C candidate package · non-public · draft/rejected Claims",
        "promotion_allowed": False,
        "record_time": decision["decided_at"],
        "world_slice": {
            "id": selection["slice_id"],
            "type": "WorldSlice",
            "label": selection["title"],
            "version": 1,
            "selection_rationale": coverage["coverage_statement"],
            "temporal_bounds": {
                "kind": "closed_interval",
                "start": temporal_scope["start"],
                "end": temporal_scope["end"],
                "precision": "day",
                "calendar": CALENDAR,
                "certainty": "analytical_closed_interval",
                "basis_claim_refs": [],
            },
            "spatial_bounds": {
                "kind": "composite_scope",
                "region_refs": ["region-duchy-romagna-context"],
                "place_refs": place_refs,
                "precision": "named_places_with_present_day_reference_anchors",
                "basis_claim_refs": [],
            },
            "included_layer_refs": [layer["id"] for layer in layer_rows],
            "uncertainty_refs": sorted(uncertainties),
            "dataset_identity": identity,
            "coverage_manifest_ref": str(COVERAGE_PATH.relative_to(ROOT)),
            "coverage_policy": {
                "corpus_completeness": "explicitly_incomplete",
                "absence_semantics": "not_historical_absence",
                "source_scope": "frozen_gate_c_repository_package",
                "known_exclusion_ids": sorted(
                    gap["gap_id"] for gap in coverage["known_gaps"]
                ),
            },
        },
        "layers": layer_rows,
        **adapted,
        "place_anchors": copy.deepcopy(place_anchor_registry["anchors"]),
        "gate_d_context_overlay_ref": place_anchor_registry["registry_id"],
        "relations": [],
        "derived_observations": [],
        "claims": sorted(
            [
                *(_adapt_claim(claim) for claim in claims_package["claims"]),
                *anchor_claims,
            ],
            key=lambda item: item["id"],
        ),
        "evidence_links": sorted(
            [
                *(
                    _adapt_evidence(link)
                    for link in claims_package["evidence_links"]
                ),
                *anchor_evidence,
            ],
            key=lambda item: item["id"],
        ),
        "sources": sorted(
            [
                *(_adapt_source(source) for source in sources_package["sources"]),
                anchor_source,
            ],
            key=lambda item: item["id"],
        ),
        "uncertainties": sorted(
            [
                *(
                    _adapt_uncertainty(value)
                    for value in claims_package["uncertainties"]
                ),
                anchor_uncertainty,
            ],
            key=lambda item: item["id"],
        ),
        "synchronized_views": [],
        "gate_c_decision": copy.deepcopy(decision),
    }

    local_refs = sorted(LOCAL_OBJECT_IDS)
    global_refs = sorted(GLOBAL_OBJECT_IDS)
    if set(candidates) != LOCAL_OBJECT_IDS | GLOBAL_OBJECT_IDS:
        raise GateDInputError("frozen candidate object set drifted from the Gate D adapter")
    state = {
        "schema_version": "1.0.0",
        "state_id": "explorer-state-leonardo-romagna-1502-gate-d",
        "world_slice_ref": selection["slice_id"],
        "dataset_identity": identity,
        "temporal_selection": {
            "mode": "interval",
            "start": temporal_scope["start"],
            "end": temporal_scope["end"],
            "precision": "day",
            "calendar": CALENDAR,
        },
        "active_layer_refs": [layer["id"] for layer in layer_rows],
        "selection": {
            "primary_object_ref": "event-leonardo-rimini-note",
            "selected_object_refs": [
                "entity-leonardo-da-vinci",
                "event-leonardo-rimini-note",
            ],
            "comparison_object_refs": [],
        },
        "context": {
            "local_context_refs": local_refs,
            "global_context_refs": global_refs,
            "derived_observation_refs": [],
        },
        "active_focus": {
            "trajectory_ref": "trajectory-leonardo-romagna-1502",
            "trajectory_segment_ref": "segment-rimini-presence",
            "region_ref": "region-duchy-romagna-context",
            "region_geometry_ref": None,
            "reconstruction_ref": None,
        },
        "comparison_scope": {
            "mode": "local_global",
            "reference_refs": [
                "place-rimini",
                "event-ottoman-turkmen-displacement-1502",
            ],
        },
        "epistemic_display": {
            "show_material_uncertainty": True,
            "show_alternatives": True,
            "show_corpus_limits": True,
        },
        "view_intent": {
            "kind": "global",
            "target_ref": None,
            "coordinate_reference": "EPSG:4326",
        },
    }
    return world, state


if __name__ == "__main__":
    model, explorer = build_gate_d_inputs()
    print(
        json.dumps(
            {
                "package_id": model["package_id"],
                "state_id": explorer["state_id"],
                "objects": sum(len(model[name]) for name in TYPE_COLLECTIONS.values()),
                "claims": len(model["claims"]),
                "evidence_links": len(model["evidence_links"]),
                "sources": len(model["sources"]),
                "uncertainties": len(model["uncertainties"]),
                "historical_corpus_ready": model["historical_corpus_ready"],
                "promotion_allowed": model["promotion_allowed"],
            },
            sort_keys=True,
        )
    )
