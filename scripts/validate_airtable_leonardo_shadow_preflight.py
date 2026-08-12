#!/usr/bin/env python3
"""Fail-closed preflight for the frozen Leonardo Gate C -> Airtable shadow import.

This validator performs no network access and no Airtable writes. It proves that:

- the completed #368 v1 empty shadow schema remains valid;
- the #371 v2 live extension snapshot matches its executable contract;
- Gate C remains completed/FREEZE in history and this contour never opens Gate D;
- the frozen Leonardo package has the reviewed counts and closed reference graph;
- the package deterministically expands to 11 ObjectParts without geometry invention;
- four World Model layers are isolated from legacy Architecture Atlas Layers;
- ten frozen Sources are isolated from legacy public Sources;
- 11 Uncertainty identities expand to deterministic many-target junction rows;
- no stored Relation predicate, invented route, Region polygon or public promotion is authorized.

Passing this command is necessary but not sufficient to write historical records. The v2
contract intentionally remains PREFLIGHT_ONLY until a separate import revision captures the
actual row plan and live round-trip evidence.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V1_VALIDATOR = ROOT / "scripts" / "validate_airtable_curation_schema.py"
V1_SNAPSHOT = ROOT / "fixtures" / "airtable_curation" / "v1" / "live_schema_snapshot.json"
EXTENSION_CONTRACT = ROOT / "fixtures" / "airtable_curation" / "v2" / "extension_contract.json"
EXTENSION_SNAPSHOT = ROOT / "fixtures" / "airtable_curation" / "v2" / "live_extension_snapshot.json"
MAPPING_CONTRACT = ROOT / "fixtures" / "airtable_curation" / "v2" / "mapping_contract.json"
SELECTION = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1" / "selection_manifest.json"
CLAIMS = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1" / "claims_manifest.json"
SOURCES = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1" / "source_registry.json"
PROJECT_STATE = ROOT / "docs" / "project_state.json"

TABLE_ID_RE = re.compile(r"^tbl[A-Za-z0-9]{14}$")
FIELD_ID_RE = re.compile(r"^fld[A-Za-z0-9]{14}$")
ALLOWED_EVIDENCE_RELATIONS = {"supports", "challenges", "contextualizes"}
ALLOWED_EVIDENCE_STRENGTH = {"direct", "indirect", "background"}


class PreflightError(RuntimeError):
    """Raised when the shadow-import preflight is not closed and deterministic."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PreflightError(f"missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise PreflightError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    _require(isinstance(value, dict), f"expected JSON object: {path.relative_to(ROOT)}")
    return value


def _unique_map(items: Any, key: str, owner: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(items, list), f"{owner} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        _require(isinstance(item, dict), f"{owner} entries must be objects")
        value = item.get(key)
        _require(isinstance(value, str) and value, f"{owner}: missing {key}")
        _require(value not in result, f"{owner}: duplicate {key} {value}")
        result[value] = item
    return result


def _load_v1_validator() -> Any:
    spec = importlib.util.spec_from_file_location("artemis_airtable_curation_v1", V1_VALIDATOR)
    _require(spec is not None and spec.loader is not None, "cannot load v1 Airtable validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_project_boundary(project_state: dict[str, Any], extension: dict[str, Any], mapping: dict[str, Any]) -> None:
    gate = project_state.get("gate", {})
    next_transition = project_state.get("next_transition", {})
    github = project_state.get("github", {})
    capability = project_state.get("capability", {})
    completed_gates = project_state.get("completed_gates", [])
    gate_c = next((item for item in completed_gates if item.get("id") == "C"), {})

    _require(gate_c.get("status") == "completed", "Gate C history must remain completed")
    _require(gate_c.get("decision") == "FREEZE", "Gate C history must retain FREEZE")
    _require(gate.get("id") == "D", "current project gate must be D")
    _require(gate.get("status") in {"in_progress", "blocked"}, "Gate D lifecycle drift")
    _require(next_transition.get("gate") == "D", "Gate E must remain unopened")
    _require(331 in github.get("deferred_issues", []), "Relation issue #331 must remain deferred")
    _require(capability.get("globe") == "non_public_r_and_d", "Globe must remain non-public")
    _require(capability.get("world_slice") == "gate_c_frozen_non_public", "World Slice must remain frozen/non-public")

    boundary = extension.get("gate_boundary", {})
    _require(boundary.get("current_gate") == "C", "v2 current gate drift")
    _require(boundary.get("current_status") == "completed", "v2 Gate C status drift")
    _require(boundary.get("current_decision") == "FREEZE", "v2 Gate C decision drift")
    _require(boundary.get("next_gate") == "D", "v2 next gate drift")
    _require(boundary.get("next_gate_opened") is False, "v2 contour must not be the action that opened Gate D")
    _require(boundary.get("paused_relation_issue") == 331, "v2 must preserve the #331 Relation gate")

    rules = extension.get("rules", {})
    for key in (
        "historical_records_allowed",
        "airtable_authority",
        "public_export_authority",
        "legacy_layers_write_allowed",
        "legacy_sources_write_allowed",
        "relations_write_allowed",
        "geometry_invention_allowed",
    ):
        _require(rules.get(key) is False, f"v2 rule {key} must remain false during preflight")
    _require(rules.get("preflight_only") is True, "v2 must remain preflight-only")
    _require(mapping.get("status") == "PREFLIGHT_ONLY", "mapping contract must remain PREFLIGHT_ONLY")


def _validate_extension_schema(extension: dict[str, Any], snapshot: dict[str, Any], v1_snapshot: dict[str, Any]) -> dict[str, int]:
    _require(extension.get("schema_version") == "2.0.0", "unexpected extension schema version")
    _require(extension.get("status") == "SHADOW_IMPORT_PREFLIGHT_V2", "unexpected extension status")
    _require(extension.get("authoritative") is False, "Airtable extension cannot be authoritative")
    _require(snapshot.get("snapshot_version") == "2.0.0", "unexpected extension snapshot version")
    _require(snapshot.get("authoritative") is False, "extension snapshot cannot be authoritative")
    _require(snapshot.get("historical_records_present") is False, "historical records must not exist during preflight")
    _require(snapshot.get("record_counts_verified_zero") is True, "extension zero-record verification missing")

    v1_tables = v1_snapshot.get("tables")
    _require(isinstance(v1_tables, list), "v1 snapshot tables missing")
    table_ids: dict[str, str] = dict(v1_snapshot.get("reused_table_ids") or {})
    for table in v1_tables:
        name = table.get("name")
        table_id = table.get("id")
        _require(isinstance(name, str) and isinstance(table_id, str), "invalid v1 table identity")
        table_ids[name] = table_id

    expected_tables = _unique_map(extension.get("tables"), "name", "v2 contract tables")
    actual_tables = _unique_map(snapshot.get("tables"), "name", "v2 snapshot tables")
    _require(set(expected_tables) == set(actual_tables), "v2 table set drift")

    for name, table in actual_tables.items():
        table_id = table.get("id")
        _require(isinstance(table_id, str) and TABLE_ID_RE.fullmatch(table_id) is not None, f"{name}: invalid table id")
        table_ids[name] = table_id

    total_new_fields = 0
    seen_field_ids: set[str] = set()
    total_records = 0
    for name, expected in expected_tables.items():
        actual = actual_tables[name]
        record_count = actual.get("record_count")
        _require(isinstance(record_count, int) and record_count == 0, f"{name}: must remain empty during preflight")
        total_records += record_count
        expected_fields = _unique_map(expected.get("fields"), "name", f"contract {name}.fields")
        actual_fields = _unique_map(actual.get("fields"), "name", f"snapshot {name}.fields")
        _require(set(expected_fields) == set(actual_fields), f"{name}: field set drift")
        for field_name, expected_field in expected_fields.items():
            actual_field = actual_fields[field_name]
            field_id = actual_field.get("id")
            _require(isinstance(field_id, str) and FIELD_ID_RE.fullmatch(field_id) is not None, f"{name}.{field_name}: invalid field id")
            _require(field_id not in seen_field_ids, f"duplicate v2 field id {field_id}")
            seen_field_ids.add(field_id)
            total_new_fields += 1
            _require(actual_field.get("type") == expected_field.get("type"), f"{name}.{field_name}: type drift")
            if "choices" in expected_field:
                _require(actual_field.get("choices") == expected_field["choices"], f"{name}.{field_name}: select choices drift")
            linked_table = expected_field.get("linked_table")
            if linked_table is not None:
                _require(linked_table in table_ids, f"{name}.{field_name}: unknown linked table {linked_table}")
                _require(actual_field.get("linked_table_id") == table_ids[linked_table], f"{name}.{field_name}: link target drift")

    expected_extensions = {
        (item.get("table"), item.get("name")): item
        for item in extension.get("field_extensions", [])
        if isinstance(item, dict)
    }
    actual_extensions = {
        (item.get("table"), item.get("name")): item
        for item in snapshot.get("field_extensions", [])
        if isinstance(item, dict)
    }
    _require(len(expected_extensions) == len(extension.get("field_extensions", [])), "duplicate contract field extension")
    _require(len(actual_extensions) == len(snapshot.get("field_extensions", [])), "duplicate snapshot field extension")
    _require(set(expected_extensions) == set(actual_extensions), "v2 field-extension set drift")

    for key, expected in expected_extensions.items():
        actual = actual_extensions[key]
        table_name, field_name = key
        _require(table_name in table_ids, f"{table_name}.{field_name}: unknown owner table")
        _require(actual.get("table_id") == table_ids[table_name], f"{table_name}.{field_name}: owner table id drift")
        field_id = actual.get("id")
        _require(isinstance(field_id, str) and FIELD_ID_RE.fullmatch(field_id) is not None, f"{table_name}.{field_name}: invalid field id")
        _require(field_id not in seen_field_ids, f"duplicate field id across v2 snapshot: {field_id}")
        seen_field_ids.add(field_id)
        _require(actual.get("type") == expected.get("type"), f"{table_name}.{field_name}: type drift")
        linked_table = expected.get("linked_table")
        if linked_table is not None:
            _require(actual.get("linked_table_id") == table_ids[linked_table], f"{table_name}.{field_name}: link target drift")

    isolation = extension.get("legacy_isolation", {})
    _require(isolation.get("KnowledgeObjects.layers", {}).get("required_for_gate_c_import") == "empty", "legacy Layers isolation missing")
    _require(isolation.get("EvidenceLinks.source", {}).get("required_for_gate_c_import") == "empty", "legacy Sources isolation missing")

    return {
        "new_tables": len(actual_tables),
        "new_table_fields": total_new_fields,
        "field_extensions": len(actual_extensions),
        "records": total_records,
    }


def _derive_parts(selection: dict[str, Any], source_ids: set[str]) -> tuple[dict[str, dict[str, Any]], int]:
    objects = _unique_map(selection.get("candidate_objects"), "object_id", "candidate_objects")
    parts: dict[str, dict[str, Any]] = {}
    unknown_routes = 0

    for obj in objects.values():
        object_type = obj.get("object_type")
        _require(obj.get("geometry") is None, f"{obj['object_id']}: candidate geometry must remain null")
        source_refs = obj.get("source_refs", [])
        _require(isinstance(source_refs, list) and set(source_refs) <= source_ids, f"{obj['object_id']}: invalid source_refs")
        temporal_hint = obj.get("temporal_hint")
        _require(isinstance(temporal_hint, dict), f"{obj['object_id']}: temporal_hint missing")
        _require(isinstance(temporal_hint.get("precision"), str), f"{obj['object_id']}: temporal precision missing")
        _require(isinstance(temporal_hint.get("assertion_status"), str), f"{obj['object_id']}: temporal assertion status missing")

        if object_type == "Trajectory":
            segments = obj.get("segments")
            _require(isinstance(segments, list) and segments, f"{obj['object_id']}: trajectory segments missing")
            for order, segment in enumerate(segments, start=1):
                _require(isinstance(segment, dict), "trajectory segment must be object")
                part_id = segment.get("segment_id")
                _require(isinstance(part_id, str) and part_id, "trajectory segment id missing")
                _require(part_id not in parts, f"duplicate ObjectPart id {part_id}")
                _require(segment.get("geometry") is None, f"{part_id}: trajectory geometry must remain null")
                refs = segment.get("source_refs", [])
                _require(isinstance(refs, list) and set(refs) <= source_ids, f"{part_id}: invalid source refs")
                spatial_mode = segment.get("spatial_mode")
                source_kind = segment.get("segment_kind")
                if spatial_mode == "unknown_route":
                    unknown_routes += 1
                    _require(source_kind == "inferred_gap", f"{part_id}: unknown route must preserve inferred_gap source kind")
                    _require(refs == [], f"{part_id}: unknown route must not acquire source refs")
                    _require(segment.get("place_ref") is None, f"{part_id}: unknown route must not acquire a place_ref")
                else:
                    _require(source_kind == "presence", f"{part_id}: non-gap trajectory part must remain presence")
                    _require(isinstance(segment.get("place_ref"), str) and segment.get("place_ref"), f"{part_id}: presence place_ref missing")
                parts[part_id] = {"owner": obj["object_id"], "kind": "trajectory_segment", "order": order}

        if object_type == "Region":
            states = obj.get("temporal_states")
            versions = obj.get("versions")
            _require(isinstance(states, list) and len(states) == 2, f"{obj['object_id']}: expected two temporal states")
            _require(isinstance(versions, list) and len(versions) == 2, f"{obj['object_id']}: expected two reconstruction alternatives")
            for order, state in enumerate(states, start=1):
                part_id = state.get("state_id")
                _require(isinstance(part_id, str) and part_id, "Region state id missing")
                _require(part_id not in parts, f"duplicate ObjectPart id {part_id}")
                _require(state.get("geometry") is None, f"{part_id}: Region state geometry must remain null")
                _require(state.get("geometry_status") == "withheld_no_boundary_evidence", f"{part_id}: Region state geometry status drift")
                _require(isinstance(state.get("state_kind"), str) and state.get("state_kind"), f"{part_id}: state_kind missing")
                _require(isinstance(state.get("interpretation"), str) and state.get("interpretation"), f"{part_id}: interpretation missing")
                refs = state.get("source_refs", [])
                _require(isinstance(refs, list) and set(refs) <= source_ids, f"{part_id}: invalid source refs")
                parts[part_id] = {"owner": obj["object_id"], "kind": "region_state", "order": order}
            for order, version in enumerate(versions, start=1):
                part_id = version.get("version_id")
                _require(isinstance(part_id, str) and part_id, "Region version id missing")
                _require(part_id not in parts, f"duplicate ObjectPart id {part_id}")
                _require(version.get("geometry") is None, f"{part_id}: reconstruction geometry must remain null")
                _require(version.get("geometry_status") == "pending_digitization_review", f"{part_id}: reconstruction geometry status drift")
                for key in ("alternative_group_id", "reconstruction_mode", "alternative_kind", "reconstruction_question", "interpretation"):
                    _require(isinstance(version.get(key), str) and version.get(key), f"{part_id}: {key} missing")
                refs = version.get("source_refs", [])
                _require(isinstance(refs, list) and set(refs) <= source_ids, f"{part_id}: invalid source refs")
                parts[part_id] = {"owner": obj["object_id"], "kind": "reconstruction_alternative", "order": order}

    return parts, unknown_routes


def _validate_frozen_mapping(selection: dict[str, Any], claims_doc: dict[str, Any], sources_doc: dict[str, Any], mapping: dict[str, Any]) -> dict[str, int]:
    expected = mapping.get("expected_counts", {})
    _require(selection.get("slice_id") == mapping.get("slice_id"), "slice id drift")
    _require(selection.get("status") == "SCOPE_FROZEN", "Leonardo selection must remain SCOPE_FROZEN")
    _require(selection.get("publication_status") == "non_public_curation", "Leonardo selection must remain non-public")
    readiness = selection.get("readiness", {})
    _require(readiness.get("scope_frozen") is True, "scope_frozen must remain true")
    _require(readiness.get("historical_objects_ready") is False, "historical objects must remain not ready")
    _require(readiness.get("promotion_allowed") is False, "promotion must remain prohibited")

    relation_policy = selection.get("relation_policy", {})
    _require(relation_policy.get("stored_relations") == [], "stored Relations remain prohibited")
    prohibited = set(relation_policy.get("prohibited_predicates") or [])
    _require({"possible_encounter", "documented_encounter", "interaction", "influence", "causal"} <= prohibited, "Relation prohibition drift")

    layers = selection.get("layers")
    _require(isinstance(layers, list), "selection layers missing")
    actual_layers = [(item.get("layer_id"), item.get("role")) for item in layers if isinstance(item, dict)]
    expected_layers = [(item.get("layer_id"), item.get("role")) for item in mapping.get("layers", []) if isinstance(item, dict)]
    _require(actual_layers == expected_layers, "Gate C layer IDs/roles drift from mapping contract")
    layer_ids = {layer_id for layer_id, _ in actual_layers}

    sources = _unique_map(sources_doc.get("sources"), "source_id", "source_registry.sources")
    source_ids = set(sources)
    _require(len(sources) == expected.get("world_sources"), "WorldSource count drift")
    for source_id, source in sources.items():
        for key in ("title", "organization", "source_type", "locator", "curation_state"):
            _require(isinstance(source.get(key), str) and source.get(key), f"{source_id}: {key} missing")
        _require(isinstance(source.get("url"), str) and source.get("url"), f"{source_id}: url missing")
        rights = source.get("rights")
        _require(isinstance(rights, dict), f"{source_id}: rights envelope missing")
        for key in ("access_status", "data_or_text_use", "media_reuse", "derived_geometry_use", "attribution"):
            _require(key in rights, f"{source_id}: rights.{key} missing")

    objects = _unique_map(selection.get("candidate_objects"), "object_id", "candidate_objects")
    object_ids = set(objects)
    _require(len(objects) == expected.get("knowledge_objects"), "KnowledgeObject count drift")
    _require({item.get("object_type") for item in objects.values()} == set(selection.get("required_object_types") or []), "required object-type coverage drift")
    for object_id, obj in objects.items():
        refs = obj.get("layer_refs")
        _require(isinstance(refs, list) and set(refs) <= layer_ids, f"{object_id}: invalid layer_refs")

    parts, unknown_routes = _derive_parts(selection, source_ids)
    part_ids = set(parts)
    _require(len(parts) == expected.get("object_parts"), "ObjectPart count drift")
    _require(unknown_routes == expected.get("unknown_route_parts"), "unknown-route count drift")

    claims = _unique_map(claims_doc.get("claims"), "claim_id", "claims_manifest.claims")
    evidence = _unique_map(claims_doc.get("evidence_links"), "evidence_link_id", "claims_manifest.evidence_links")
    uncertainties = _unique_map(claims_doc.get("uncertainties"), "uncertainty_id", "claims_manifest.uncertainties")
    claim_ids = set(claims)
    uncertainty_ids = set(uncertainties)
    _require(len(claims) == expected.get("claims"), "Claim count drift")
    _require(len(evidence) == expected.get("evidence_links"), "EvidenceLink count drift")
    _require(len(uncertainties) == expected.get("uncertainties"), "Uncertainty count drift")

    evidence_by_claim: dict[str, set[str]] = {claim_id: set() for claim_id in claim_ids}
    for evidence_id, link in evidence.items():
        claim_id = link.get("claim_id")
        source_id = link.get("source_id")
        _require(claim_id in claims, f"{evidence_id}: unresolved claim_id {claim_id}")
        _require(source_id in sources, f"{evidence_id}: unresolved source_id {source_id}")
        _require(isinstance(link.get("locator"), str) and link.get("locator").strip(), f"{evidence_id}: blank locator")
        _require(link.get("relation_to_claim") in ALLOWED_EVIDENCE_RELATIONS, f"{evidence_id}: invalid relation_to_claim")
        _require(link.get("evidence_strength") in ALLOWED_EVIDENCE_STRENGTH, f"{evidence_id}: invalid evidence_strength")
        _require(link.get("review_state") in {"draft", "reviewed", "rejected"}, f"{evidence_id}: invalid review_state")
        evidence_by_claim[claim_id].add(evidence_id)

    for claim_id, claim in claims.items():
        _require(claim.get("target_object_ref") in objects, f"{claim_id}: unresolved target_object_ref")
        _require(isinstance(claim.get("statement"), str) and claim.get("statement").strip(), f"{claim_id}: blank statement")
        _require(isinstance(claim.get("confidence_basis"), str) and claim.get("confidence_basis").strip(), f"{claim_id}: confidence_basis missing")
        declared_evidence = claim.get("evidence_link_refs")
        declared_uncertainty = claim.get("uncertainty_refs")
        _require(isinstance(declared_evidence, list), f"{claim_id}: evidence_link_refs missing")
        _require(set(declared_evidence) == evidence_by_claim[claim_id], f"{claim_id}: EvidenceLink closure drift")
        _require(isinstance(declared_uncertainty, list) and set(declared_uncertainty) <= uncertainty_ids, f"{claim_id}: invalid uncertainty_refs")

    for source_id, source in sources.items():
        intended = source.get("intended_claims")
        _require(isinstance(intended, list) and set(intended) <= claim_ids, f"{source_id}: invalid intended_claims")
        _require(source.get("relation_to_claim") in ALLOWED_EVIDENCE_RELATIONS, f"{source_id}: invalid source relation_to_claim")

    target_bindings: set[tuple[str, str]] = set()
    for uncertainty_id, uncertainty in uncertainties.items():
        _require(isinstance(uncertainty.get("dimension"), str) and uncertainty.get("dimension"), f"{uncertainty_id}: dimension missing")
        _require(isinstance(uncertainty.get("description"), str) and uncertainty.get("description"), f"{uncertainty_id}: description missing")
        _require(isinstance(uncertainty.get("effect"), str) and uncertainty.get("effect"), f"{uncertainty_id}: effect missing")
        _require(isinstance(uncertainty.get("basis_kind"), str) and uncertainty.get("basis_kind"), f"{uncertainty_id}: basis_kind missing")
        basis_claims = uncertainty.get("basis_claim_refs")
        _require(isinstance(basis_claims, list) and set(basis_claims) <= claim_ids, f"{uncertainty_id}: invalid basis_claim_refs")
        targets = uncertainty.get("target_refs")
        _require(isinstance(targets, list) and targets, f"{uncertainty_id}: target_refs missing")
        _require(len(targets) == len(set(targets)), f"{uncertainty_id}: duplicate target_ref")
        for target_ref in targets:
            memberships = int(target_ref in object_ids) + int(target_ref in part_ids) + int(target_ref in claim_ids)
            _require(memberships == 1, f"{uncertainty_id}: target {target_ref} must resolve to exactly one object/part/claim")
            binding = (uncertainty_id, target_ref)
            _require(binding not in target_bindings, f"duplicate UncertaintyTarget binding {binding}")
            target_bindings.add(binding)

    if "uncertainty_targets" in expected:
        _require(len(target_bindings) == expected["uncertainty_targets"], "UncertaintyTarget derived count drift")

    return {
        "world_slices": 1,
        "knowledge_objects": len(objects),
        "object_parts": len(parts),
        "world_sources": len(sources),
        "claims": len(claims),
        "evidence_links": len(evidence),
        "uncertainties": len(uncertainties),
        "uncertainty_targets": len(target_bindings),
        "slice_layers": len(layers),
        "unknown_routes": unknown_routes,
    }


def validate() -> dict[str, int]:
    # Preserve the completed #368 evidence and fail if its six original tables cease to be empty.
    v1 = _load_v1_validator()
    try:
        v1_summary = v1.validate(require_empty=True)
    except Exception as exc:  # noqa: BLE001 - convert legacy validator exception into one preflight failure
        raise PreflightError(f"v1 Airtable shadow schema failed: {exc}") from exc
    _require(v1_summary == {"tables": 6, "fields": 75, "records": 0}, "unexpected v1 shadow-schema summary")

    extension = _load_json(EXTENSION_CONTRACT)
    snapshot = _load_json(EXTENSION_SNAPSHOT)
    mapping = _load_json(MAPPING_CONTRACT)
    selection = _load_json(SELECTION)
    claims_doc = _load_json(CLAIMS)
    sources_doc = _load_json(SOURCES)
    project_state = _load_json(PROJECT_STATE)
    v1_snapshot = _load_json(V1_SNAPSHOT)

    _validate_project_boundary(project_state, extension, mapping)
    schema_summary = _validate_extension_schema(extension, snapshot, v1_snapshot)
    mapping_summary = _validate_frozen_mapping(selection, claims_doc, sources_doc, mapping)

    return {
        **schema_summary,
        **mapping_summary,
    }


def main() -> int:
    try:
        summary = validate()
    except PreflightError as exc:
        print(f"Leonardo Airtable shadow preflight: FAIL — {exc}", file=sys.stderr)
        return 1

    print(
        "Leonardo Airtable shadow preflight: PASS — "
        f"{summary['knowledge_objects']} objects, {summary['object_parts']} parts, "
        f"{summary['world_sources']} sources, {summary['claims']} Claims, "
        f"{summary['evidence_links']} EvidenceLinks, {summary['uncertainties']} Uncertainties, "
        f"{summary['uncertainty_targets']} uncertainty targets, {summary['slice_layers']} slice layers; "
        "all v2 extension tables remain empty; this preflight did not open Gate D"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
