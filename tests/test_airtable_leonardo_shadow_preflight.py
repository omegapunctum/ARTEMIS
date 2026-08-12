from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_airtable_leonardo_shadow_preflight.py"
EXTENSION = ROOT / "fixtures" / "airtable_curation" / "v2" / "extension_contract.json"
SNAPSHOT = ROOT / "fixtures" / "airtable_curation" / "v2" / "live_extension_snapshot.json"
MAPPING = ROOT / "fixtures" / "airtable_curation" / "v2" / "mapping_contract.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("artemis_leonardo_shadow_preflight", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_leonardo_shadow_preflight_passes_without_historical_rows() -> None:
    module = _load_validator()
    assert module.validate() == {
        "new_tables": 3,
        "new_table_fields": 31,
        "field_extensions": 22,
        "records": 0,
        "world_slices": 1,
        "knowledge_objects": 17,
        "object_parts": 11,
        "world_sources": 10,
        "claims": 22,
        "evidence_links": 38,
        "uncertainties": 11,
        "uncertainty_targets": 40,
        "slice_layers": 4,
        "unknown_routes": 3,
    }


def test_preflight_is_fail_closed_and_does_not_open_gate_d() -> None:
    extension = json.loads(EXTENSION.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))

    assert extension["status"] == "SHADOW_IMPORT_PREFLIGHT_V2"
    assert extension["authoritative"] is False
    assert extension["rules"]["historical_records_allowed"] is False
    assert extension["rules"]["preflight_only"] is True
    assert extension["rules"]["public_export_authority"] is False
    assert extension["rules"]["relations_write_allowed"] is False
    assert extension["rules"]["geometry_invention_allowed"] is False
    assert extension["gate_boundary"]["next_gate"] == "D"
    assert extension["gate_boundary"]["next_gate_opened"] is False
    assert mapping["status"] == "PREFLIGHT_ONLY"


def test_legacy_public_layers_and_sources_are_explicitly_isolated() -> None:
    extension = json.loads(EXTENSION.read_text(encoding="utf-8"))
    field_extensions = {(field["table"], field["name"]): field for field in extension["field_extensions"]}

    assert extension["legacy_isolation"]["KnowledgeObjects.layers"]["required_for_gate_c_import"] == "empty"
    assert extension["legacy_isolation"]["EvidenceLinks.source"]["required_for_gate_c_import"] == "empty"
    assert field_extensions[("KnowledgeObjects", "slice_layers")]["linked_table"] == "SliceLayers"
    assert field_extensions[("EvidenceLinks", "world_source")]["linked_table"] == "WorldSources"
    assert field_extensions[("KnowledgeObjects", "world_sources")]["linked_table"] == "WorldSources"
    assert field_extensions[("ObjectParts", "world_sources")]["linked_table"] == "WorldSources"


def test_source_temporal_tokens_are_preserved_separately_from_normalized_enums() -> None:
    extension = json.loads(EXTENSION.read_text(encoding="utf-8"))
    field_extensions = {(field["table"], field["name"]): field for field in extension["field_extensions"]}

    assert ("KnowledgeObjects", "source_temporal_value") in field_extensions
    assert ("KnowledgeObjects", "source_temporal_precision") in field_extensions
    assert ("ObjectParts", "source_temporal_value") in field_extensions
    assert ("ObjectParts", "source_temporal_precision") in field_extensions


def test_uncertainty_identity_is_preserved_via_target_junction() -> None:
    extension = json.loads(EXTENSION.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    tables = {table["name"]: table for table in extension["tables"]}

    assert tables["UncertaintyTargets"]["target_cardinality"] == "exactly_one_of_knowledge_object_object_part_claim"
    assert mapping["mapping"]["Uncertainties"]["identity_count"] == "preserve exactly 11 source identities"
    assert mapping["mapping"]["Uncertainties"]["targets"].startswith("expand target_refs[]")
    assert mapping["mapping"]["UncertaintyTargets"]["duplicates"] == "prohibited"


def test_live_extension_snapshot_contains_no_rows() -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert snapshot["record_counts_verified_zero"] is True
    assert snapshot["historical_records_present"] is False
    assert [table["name"] for table in snapshot["tables"]] == ["SliceLayers", "UncertaintyTargets", "WorldSources"]
    assert all(table["record_count"] == 0 for table in snapshot["tables"])
