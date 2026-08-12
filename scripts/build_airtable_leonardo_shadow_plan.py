#!/usr/bin/env python3
"""Build the deterministic semantic-ID row plan for #371.

The plan contains no Airtable record IDs and performs no network access or writes. Linked-record
values are expressed as stable semantic IDs and are resolved only by the later controlled importer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SLICE_DIR = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1"
SELECTION = SLICE_DIR / "selection_manifest.json"
CLAIMS = SLICE_DIR / "claims_manifest.json"
SOURCES = SLICE_DIR / "source_registry.json"
PROJECT_STATE = ROOT / "docs" / "project_state.json"
MAPPING = ROOT / "fixtures" / "airtable_curation" / "v2" / "mapping_contract.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _temporal(hint: Any) -> dict[str, Any]:
    if not isinstance(hint, dict):
        return {
            "temporal_start": None,
            "temporal_end": None,
            "temporal_precision": None,
            "source_temporal_value": None,
            "source_temporal_precision": None,
            "temporal_assertion_status": None,
        }
    value = hint.get("value")
    source_precision = hint.get("precision")
    start = None
    end = None
    if isinstance(value, str) and value:
        if "/" in value:
            start, end = value.split("/", 1)
        else:
            start = value
    precision_map = {"range": "interval", "pending": "unresolved"}
    normalized_precision = precision_map.get(source_precision, source_precision)
    return {
        "temporal_start": start,
        "temporal_end": end,
        "temporal_precision": normalized_precision,
        "source_temporal_value": value,
        "source_temporal_precision": source_precision,
        "temporal_assertion_status": hint.get("assertion_status"),
    }


def _slice_layer_id(slice_id: str, layer_id: str) -> str:
    return f"slice-layer::{slice_id}::{layer_id}"


def _uncertainty_target_id(uncertainty_id: str, target_ref: str) -> str:
    return f"uncertainty-target::{uncertainty_id}::{target_ref}"


def _object_spatial_status(source_mode: Any) -> str:
    # The exact source token is retained separately. With no authorized geometry or explicit
    # object->place machine link in the frozen candidate envelope, the normalized curation status
    # must not invent one.
    if source_mode in {"named_place", "approximate_point", "historical_region_pending", "unknown_route"}:
        return "geometry_withheld"
    return "not_spatial"


def _row(table: str, stable_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    return {"table": table, "stable_id": stable_id, "fields": fields}


def build_plan() -> dict[str, Any]:
    selection = _load(SELECTION)
    claims_doc = _load(CLAIMS)
    sources_doc = _load(SOURCES)
    project_state = _load(PROJECT_STATE)
    mapping = _load(MAPPING)

    slice_id = selection["slice_id"]
    completed_gate_c = next(
        (
            gate
            for gate in project_state["completed_gates"]
            if gate.get("id") == "C" and gate.get("status") == "completed"
        ),
        None,
    )
    if completed_gate_c is None:
        raise ValueError("project_state must preserve completed Gate C evidence")
    gate_evidence = completed_gate_c["evidence"]
    source_registry = {source["source_id"]: source for source in sources_doc["sources"]}
    objects = {obj["object_id"]: obj for obj in selection["candidate_objects"]}
    claims = {claim["claim_id"]: claim for claim in claims_doc["claims"]}
    uncertainties = {item["uncertainty_id"]: item for item in claims_doc["uncertainties"]}

    rows: dict[str, list[dict[str, Any]]] = {
        "WorldSlices": [],
        "SliceLayers": [],
        "WorldSources": [],
        "KnowledgeObjects": [],
        "ObjectParts": [],
        "Claims": [],
        "EvidenceLinks": [],
        "Uncertainties": [],
        "UncertaintyTargets": [],
    }

    spatial_scope = selection["spatial_scope"]
    selection_rules = selection["selection_rules"]
    rows["WorldSlices"].append(
        _row(
            "WorldSlices",
            slice_id,
            {
                "id": slice_id,
                "label": selection["title"],
                "status": "frozen",
                "temporal_start": selection["temporal_scope"]["start"],
                "temporal_end": selection["temporal_scope"]["end"],
                "spatial_scope_note": _canonical_json(spatial_scope),
                "selection_rationale": "\n".join(selection_rules["include"]),
                "known_exclusions": "\n".join(selection_rules["exclude"]),
                "coverage_limitations": "\n".join(
                    [spatial_scope["global_context_policy"], selection_rules["absence_rule"]]
                ),
                "source_package_ref": "fixtures/world_slices/leonardo_romagna_1502/v1",
                "review_version": selection["schema_version"],
                "frozen_digest": gate_evidence["reviewed_content_digest"],
                "promotion_allowed": False,
                "notes": selection["temporal_scope"]["historical_precision_note"],
            },
        )
    )

    for layer in selection["layers"]:
        stable_id = _slice_layer_id(slice_id, layer["layer_id"])
        rows["SliceLayers"].append(
            _row(
                "SliceLayers",
                stable_id,
                {
                    "id": stable_id,
                    "world_slice": [slice_id],
                    "layer_id": layer["layer_id"],
                    "label": layer["label"],
                    "role": layer["role"],
                    "review_state": "draft",
                    "notes": None,
                },
            )
        )

    for source_id in sorted(source_registry):
        source = source_registry[source_id]
        rights = source["rights"]
        rows["WorldSources"].append(
            _row(
                "WorldSources",
                source_id,
                {
                    "id": source_id,
                    "title": source["title"],
                    "organization": source["organization"],
                    "source_type": source["source_type"],
                    "url": source["url"],
                    "locator": source["locator"],
                    "curation_state": source["curation_state"],
                    "access_status": rights.get("access_status"),
                    "data_or_text_use": rights.get("data_or_text_use"),
                    "media_reuse": rights.get("media_reuse"),
                    "derived_geometry_use": rights.get("derived_geometry_use"),
                    "license": rights.get("license"),
                    "attribution": rights.get("attribution"),
                    "review_state": "draft",
                    "notes": None,
                    "intended_claims": sorted(source["intended_claims"]),
                    "default_relation_to_claim": source["relation_to_claim"],
                },
            )
        )

    for object_id in sorted(objects):
        obj = objects[object_id]
        temporal = _temporal(obj.get("temporal_hint"))
        rows["KnowledgeObjects"].append(
            _row(
                "KnowledgeObjects",
                object_id,
                {
                    "id": object_id,
                    "object_type": obj["object_type"].lower(),
                    "label": obj["label"],
                    "world_slices": [slice_id],
                    "temporal_start": temporal["temporal_start"],
                    "temporal_end": temporal["temporal_end"],
                    "temporal_precision": temporal["temporal_precision"],
                    "temporal_certainty": None,
                    "spatial_status": _object_spatial_status(obj.get("spatial_mode")),
                    "place_ref": None,
                    "geometry_provenance_ref": None,
                    "reconstruction_mode": None,
                    "layers": [],
                    "review_state": "draft" if obj["curation_state"] == "candidate_not_ready" else obj["curation_state"],
                    "notes": obj.get("notes"),
                    "slice_layers": sorted(_slice_layer_id(slice_id, ref) for ref in obj["layer_refs"]),
                    "source_spatial_mode": obj.get("spatial_mode"),
                    "source_curation_state": obj.get("curation_state"),
                    "source_temporal_value": temporal["source_temporal_value"],
                    "source_temporal_precision": temporal["source_temporal_precision"],
                    "temporal_assertion_status": temporal["temporal_assertion_status"],
                    "world_sources": sorted(obj.get("source_refs", [])),
                },
            )
        )

    for object_id in sorted(objects):
        obj = objects[object_id]
        if obj["object_type"] == "Trajectory":
            for index, segment in enumerate(obj["segments"], start=1):
                source_kind = segment["segment_kind"]
                normalized_segment_kind = "unknown_route" if source_kind == "inferred_gap" else source_kind
                rows["ObjectParts"].append(
                    _row(
                        "ObjectParts",
                        segment["segment_id"],
                        {
                            "id": segment["segment_id"],
                            "knowledge_object": [object_id],
                            "part_kind": "trajectory_segment",
                            "sequence_order": index,
                            "temporal_start": None,
                            "temporal_end": None,
                            "temporal_precision": None,
                            "temporal_certainty": None,
                            "spatial_status": "unknown_route" if segment["spatial_mode"] == "unknown_route" else "place_ref",
                            "place_ref": segment.get("place_ref"),
                            "geometry_ref": None,
                            "segment_kind": normalized_segment_kind,
                            "reconstruction_mode": None,
                            "is_primary": False,
                            "review_state": "draft",
                            "notes": None,
                            "source_kind": source_kind,
                            "source_spatial_mode": segment.get("spatial_mode"),
                            "source_temporal_value": None,
                            "source_temporal_precision": None,
                            "temporal_assertion_status": None,
                            "geometry_status": None,
                            "alternative_group_id": None,
                            "alternative_kind": None,
                            "reconstruction_question": None,
                            "interpretation": None,
                            "world_sources": sorted(segment.get("source_refs", [])),
                        },
                    )
                )
        if obj["object_type"] == "Region":
            for index, state in enumerate(obj["temporal_states"], start=1):
                temporal = _temporal(state.get("temporal_hint"))
                rows["ObjectParts"].append(
                    _row(
                        "ObjectParts",
                        state["state_id"],
                        {
                            "id": state["state_id"],
                            "knowledge_object": [object_id],
                            "part_kind": "region_state",
                            "sequence_order": index,
                            "temporal_start": temporal["temporal_start"],
                            "temporal_end": temporal["temporal_end"],
                            "temporal_precision": temporal["temporal_precision"],
                            "temporal_certainty": None,
                            "spatial_status": "geometry_withheld",
                            "place_ref": None,
                            "geometry_ref": None,
                            "segment_kind": None,
                            "reconstruction_mode": None,
                            "is_primary": False,
                            "review_state": "draft",
                            "notes": None,
                            "source_kind": state["state_kind"],
                            "source_spatial_mode": None,
                            "source_temporal_value": temporal["source_temporal_value"],
                            "source_temporal_precision": temporal["source_temporal_precision"],
                            "temporal_assertion_status": temporal["temporal_assertion_status"],
                            "geometry_status": state["geometry_status"],
                            "alternative_group_id": None,
                            "alternative_kind": None,
                            "reconstruction_question": None,
                            "interpretation": state["interpretation"],
                            "world_sources": sorted(state.get("source_refs", [])),
                        },
                    )
                )
            for index, version in enumerate(obj["versions"], start=1):
                temporal = _temporal(version.get("temporal_hint"))
                rows["ObjectParts"].append(
                    _row(
                        "ObjectParts",
                        version["version_id"],
                        {
                            "id": version["version_id"],
                            "knowledge_object": [object_id],
                            "part_kind": "reconstruction_alternative",
                            "sequence_order": index,
                            "temporal_start": temporal["temporal_start"],
                            "temporal_end": temporal["temporal_end"],
                            "temporal_precision": temporal["temporal_precision"],
                            "temporal_certainty": None,
                            "spatial_status": "geometry_withheld",
                            "place_ref": None,
                            "geometry_ref": None,
                            "segment_kind": None,
                            "reconstruction_mode": version["reconstruction_mode"],
                            "is_primary": False,
                            "review_state": "draft",
                            "notes": None,
                            "source_kind": version["alternative_kind"],
                            "source_spatial_mode": None,
                            "source_temporal_value": temporal["source_temporal_value"],
                            "source_temporal_precision": temporal["source_temporal_precision"],
                            "temporal_assertion_status": temporal["temporal_assertion_status"],
                            "geometry_status": version["geometry_status"],
                            "alternative_group_id": version["alternative_group_id"],
                            "alternative_kind": version["alternative_kind"],
                            "reconstruction_question": version["reconstruction_question"],
                            "interpretation": version["interpretation"],
                            "world_sources": sorted(version.get("source_refs", [])),
                        },
                    )
                )

    for claim_id in sorted(claims):
        claim = claims[claim_id]
        rows["Claims"].append(
            _row(
                "Claims",
                claim_id,
                {
                    "id": claim_id,
                    "statement": claim["statement"],
                    "knowledge_object": [claim["target_object_ref"]],
                    "object_part": [],
                    "claim_kind": claim["claim_kind"],
                    "origin": claim["origin"],
                    "review_state": claim["review_state"],
                    "confidence": claim["confidence"],
                    "evidence_state": claim["evidence_state"],
                    "created_at": None,
                    "updated_at": None,
                    "confidence_basis": claim["confidence_basis"],
                },
            )
        )

    for link in sorted(claims_doc["evidence_links"], key=lambda item: item["evidence_link_id"]):
        link_id = link["evidence_link_id"]
        rows["EvidenceLinks"].append(
            _row(
                "EvidenceLinks",
                link_id,
                {
                    "id": link_id,
                    "claim": [link["claim_id"]],
                    "source": [],
                    "locator": link["locator"],
                    "relation_to_claim": link["relation_to_claim"],
                    "evidence_strength": link["evidence_strength"],
                    "review_state": link["review_state"],
                    "reviewer": link.get("reviewer"),
                    "reviewed_at": link.get("reviewed_at"),
                    "world_source": [link["source_id"]],
                },
            )
        )

    object_ids = set(objects)
    part_ids = {row["stable_id"] for row in rows["ObjectParts"]}
    claim_ids = set(claims)
    for uncertainty_id in sorted(uncertainties):
        uncertainty = uncertainties[uncertainty_id]
        rows["Uncertainties"].append(
            _row(
                "Uncertainties",
                uncertainty_id,
                {
                    "id": uncertainty_id,
                    "knowledge_object": [],
                    "object_part": [],
                    "claim": [],
                    "dimension": uncertainty["dimension"],
                    "description": uncertainty["description"],
                    "effect": uncertainty["effect"],
                    "range_or_alternatives": uncertainty.get("range_or_alternatives"),
                    "basis": uncertainty["basis"],
                    "review_state": uncertainty["review_state"],
                    "basis_kind": uncertainty["basis_kind"],
                    "basis_claims": sorted(uncertainty.get("basis_claim_refs", [])),
                },
            )
        )
        for target_ref in sorted(uncertainty["target_refs"]):
            fields = {
                "id": _uncertainty_target_id(uncertainty_id, target_ref),
                "uncertainty": [uncertainty_id],
                "knowledge_object": [target_ref] if target_ref in object_ids else [],
                "object_part": [target_ref] if target_ref in part_ids else [],
                "claim": [target_ref] if target_ref in claim_ids else [],
                "review_state": "draft",
                "notes": None,
            }
            rows["UncertaintyTargets"].append(
                _row("UncertaintyTargets", fields["id"], fields)
            )

    for table_rows in rows.values():
        table_rows.sort(key=lambda item: item["stable_id"])

    counts = {table: len(table_rows) for table, table_rows in rows.items()}
    expected = mapping["expected_counts"]
    expected_by_table = {
        "WorldSlices": expected["world_slices"],
        "SliceLayers": expected["slice_layers"],
        "WorldSources": expected["world_sources"],
        "KnowledgeObjects": expected["knowledge_objects"],
        "ObjectParts": expected["object_parts"],
        "Claims": expected["claims"],
        "EvidenceLinks": expected["evidence_links"],
        "Uncertainties": expected["uncertainties"],
    }
    for table, expected_count in expected_by_table.items():
        if counts[table] != expected_count:
            raise ValueError(f"{table}: expected {expected_count}, got {counts[table]}")
    if counts["UncertaintyTargets"] != 40:
        raise ValueError(f"UncertaintyTargets: expected 40, got {counts['UncertaintyTargets']}")

    plan = {
        "schema_version": "1.0.0",
        "status": "ROW_PLAN_CANDIDATE",
        "authoritative": False,
        "issue": 371,
        "source": {
            "slice_id": slice_id,
            "package_ref": "fixtures/world_slices/leonardo_romagna_1502/v1",
            "frozen_commit": gate_evidence["frozen_commit"],
            "frozen_tree": gate_evidence["frozen_tree"],
            "reviewed_content_digest": gate_evidence["reviewed_content_digest"],
        },
        "target": {
            "base_id": "appHmf8ubeUF9nfkO",
            "authority": "non_authoritative_shadow",
            "legacy_fields_required_empty": ["KnowledgeObjects.layers", "EvidenceLinks.source"],
            "gate_d_opened": False,
        },
        "write_phases": [
            ["WorldSlices", "SliceLayers", "WorldSources", "KnowledgeObjects", "ObjectParts"],
            ["Claims"],
            ["WorldSources.intended_claims", "EvidenceLinks", "Uncertainties", "UncertaintyTargets"],
        ],
        "counts": counts,
        "rows": rows,
    }
    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic Leonardo Airtable shadow row plan")
    parser.add_argument("--out", type=Path, help="Optional output JSON path")
    parser.add_argument("--digest-only", action="store_true", help="Print only the canonical SHA-256")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_plan()
    digest = _digest(plan)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.digest_only:
        print(digest)
    else:
        print(
            f"Leonardo shadow row plan: {sum(plan['counts'].values())} rows; "
            f"digest={digest}; counts={_canonical_json(plan['counts'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
