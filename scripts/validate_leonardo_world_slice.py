#!/usr/bin/env python3
"""Validate the scope-frozen, non-public Leonardo World Slice curation package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_romagna_1502" / "v1"
SELECTION_PATH = PACKAGE_ROOT / "selection_manifest.json"
SELECTION_SCHEMA_PATH = PACKAGE_ROOT / "selection_manifest.schema.json"
SOURCE_PATH = PACKAGE_ROOT / "source_registry.json"
SOURCE_SCHEMA_PATH = PACKAGE_ROOT / "source_registry.schema.json"
COVERAGE_PATH = PACKAGE_ROOT / "coverage_manifest.json"
COVERAGE_SCHEMA_PATH = PACKAGE_ROOT / "coverage_manifest.schema.json"
COST_PATH = PACKAGE_ROOT / "curation_cost.json"
COST_SCHEMA_PATH = PACKAGE_ROOT / "curation_cost.schema.json"
CLAIMS_PATH = PACKAGE_ROOT / "claims_manifest.json"
CLAIMS_SCHEMA_PATH = PACKAGE_ROOT / "claims_manifest.schema.json"
REVIEW_REGISTRY_PATH = PACKAGE_ROOT / "review_registry.json"
REVIEW_REGISTRY_SCHEMA_PATH = PACKAGE_ROOT / "review_registry.schema.json"

REQUIRED_OBJECT_TYPES = {"Entity", "Event", "State", "Process", "Trajectory", "Region"}
PROHIBITED_RELATION_PREDICATES = {
    "possible_encounter",
    "documented_encounter",
    "interaction",
    "influence",
    "causal",
}
CRITICAL_LOCATOR_BINDINGS = {
    "evidence-rimini-uniurb-f78r": {
        "claim_id": "claim-rimini-presence-1502-08-08",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "78r"),
    },
    "evidence-cesena-uniurb-f46v": {
        "claim_id": "claim-cesena-presence-1502-08-10",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "46v"),
    },
    "evidence-patent-uniurb-p16-n26": {
        "claim_id": "claim-patent-date-1502-08-18",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "note 26", "decimo octavo Augusti"),
    },
    "evidence-cesenatico-uniurb-f66v": {
        "claim_id": "claim-cesenatico-presence-1502-09-06",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "66v"),
    },
    "evidence-cesenatico-folio-66v-uniurb": {
        "claim_id": "claim-cesenatico-dated-folio-66v",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "66v"),
    },
    "evidence-service-uniurb-patent": {
        "claim_id": "claim-leonardo-borgia-service-1502",
        "source_id": "source-uniurb-volpe-chronology",
        "required_tokens": ("Printed p. 16", "note 26", "Architect and Engineer General"),
    },
}


class WorldSliceScopeError(ValueError):
    """Raised when the scope package violates its fail-closed boundary."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorldSliceScopeError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorldSliceScopeError(f"{path} must contain a JSON object")
    return value


def _validate_schema(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if not errors:
        return
    messages = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]
    raise WorldSliceScopeError(f"{label} schema validation failed: {'; '.join(messages)}")


def _index(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get(key) or "")
        if not identity:
            raise WorldSliceScopeError(f"{label} row missing {key}")
        if identity in result:
            raise WorldSliceScopeError(f"duplicate {label} {key}: {identity}")
        result[identity] = row
    return result


def validate_package(
    selection: dict[str, Any] | None = None,
    sources: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
    cost: dict[str, Any] | None = None,
    claims_package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selection = _load(SELECTION_PATH) if selection is None else selection
    sources = _load(SOURCE_PATH) if sources is None else sources
    coverage = _load(COVERAGE_PATH) if coverage is None else coverage
    cost = _load(COST_PATH) if cost is None else cost
    claims_package = _load(CLAIMS_PATH) if claims_package is None else claims_package

    _validate_schema(selection, _load(SELECTION_SCHEMA_PATH), "selection manifest")
    _validate_schema(sources, _load(SOURCE_SCHEMA_PATH), "source registry")
    _validate_schema(coverage, _load(COVERAGE_SCHEMA_PATH), "coverage manifest")
    _validate_schema(cost, _load(COST_SCHEMA_PATH), "curation cost log")
    _validate_schema(claims_package, _load(CLAIMS_SCHEMA_PATH), "claims manifest")

    layer_index = _index(selection["layers"], "layer_id", "layer")
    object_index = _index(selection["candidate_objects"], "object_id", "candidate object")
    source_index = _index(sources["sources"], "source_id", "source")
    gap_index = _index(coverage["known_gaps"], "gap_id", "known gap")
    _index(cost["entries"], "activity_id", "cost activity")
    claim_index = _index(claims_package["claims"], "claim_id", "Claim")
    evidence_index = _index(
        claims_package["evidence_links"], "evidence_link_id", "EvidenceLink"
    )
    uncertainty_index = _index(
        claims_package["uncertainties"], "uncertainty_id", "Uncertainty"
    )

    object_types = {row["object_type"] for row in object_index.values()}
    if not REQUIRED_OBJECT_TYPES.issubset(object_types):
        missing = sorted(REQUIRED_OBJECT_TYPES - object_types)
        raise WorldSliceScopeError(f"required World Model candidate types are missing: {missing}")

    used_source_refs: set[str] = set()
    for object_id, row in object_index.items():
        missing_layers = set(row["layer_refs"]) - set(layer_index)
        if missing_layers:
            raise WorldSliceScopeError(
                f"candidate object {object_id} references missing layers: {sorted(missing_layers)}"
            )
        missing_sources = set(row["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"candidate object {object_id} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(row["source_refs"])
        if row["geometry"] is not None:
            raise WorldSliceScopeError(
                f"scope-freeze candidate {object_id} cannot publish geometry before review"
            )

    if selection["relation_policy"]["stored_relations"]:
        raise WorldSliceScopeError("scope package cannot store Relations while #331 is paused")
    actual_prohibited = set(selection["relation_policy"]["prohibited_predicates"])
    if actual_prohibited != PROHIBITED_RELATION_PREDICATES:
        raise WorldSliceScopeError("prohibited Relation predicate set drifted from the paused #331 boundary")
    if selection["relation_policy"]["allowed_computed_observations"] != ["derived_co_presence"]:
        raise WorldSliceScopeError("only derived_co_presence is allowed before #331")

    trajectories = [row for row in object_index.values() if row["object_type"] == "Trajectory"]
    if len(trajectories) != 1:
        raise WorldSliceScopeError("scope must contain exactly one bounded candidate Trajectory")
    trajectory = trajectories[0]
    if trajectory["spatial_mode"] != "unknown_route" or trajectory["geometry"] is not None:
        raise WorldSliceScopeError("candidate Trajectory must remain an unknown route with null geometry")
    segments = trajectory.get("segments") or []
    gap_segments = [row for row in segments if row["segment_kind"] == "inferred_gap"]
    if not gap_segments:
        raise WorldSliceScopeError("candidate Trajectory must expose at least one inferred gap")
    for gap in gap_segments:
        if gap["spatial_mode"] != "unknown_route" or gap["geometry"] is not None:
            raise WorldSliceScopeError("inferred trajectory gap cannot carry route geometry")
        if gap["source_refs"]:
            raise WorldSliceScopeError("unknown route gap cannot pretend to have route evidence")
    for segment in segments:
        missing_sources = set(segment["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"trajectory segment {segment['segment_id']} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(segment["source_refs"])

    regions = [row for row in object_index.values() if row["object_type"] == "Region"]
    if len(regions) != 1:
        raise WorldSliceScopeError("scope must contain exactly one bounded candidate Region")
    versions = regions[0].get("versions") or []
    if len(versions) < 2:
        raise WorldSliceScopeError("candidate Region must preserve at least two source-bound versions")
    expected_reconstruction_modes = {"title_based_context", "documented_place_only_context"}
    actual_reconstruction_modes = {version["reconstruction_mode"] for version in versions}
    if actual_reconstruction_modes != expected_reconstruction_modes:
        raise WorldSliceScopeError("candidate Region must preserve both explicit reconstruction alternatives")
    if len({version["alternative_group_id"] for version in versions}) != 1:
        raise WorldSliceScopeError("candidate Region alternatives must answer one reconstruction question")
    for version in versions:
        if version["geometry_status"] != "pending_digitization_review" or version["geometry"] is not None:
            raise WorldSliceScopeError("candidate Region geometry must remain withheld pending review")
        missing_sources = set(version["source_refs"]) - set(source_index)
        if missing_sources:
            raise WorldSliceScopeError(
                f"Region version {version['version_id']} references missing sources: {sorted(missing_sources)}"
            )
        used_source_refs.update(version["source_refs"])

    for source_id, source in source_index.items():
        rights = source["rights"]
        intended_claims = set(source["intended_claims"])
        missing_intended_claims = intended_claims - set(claim_index)
        if missing_intended_claims:
            raise WorldSliceScopeError(
                f"source {source_id} references missing intended Claims: {sorted(missing_intended_claims)}"
            )
        if source_id.startswith("source-rct-"):
            if rights["data_or_text_use"] != "citation_and_factual_claims_only":
                raise WorldSliceScopeError(f"{source_id} must remain citation/factual-use only")
            if rights["media_reuse"] != "prohibited_without_permission":
                raise WorldSliceScopeError(f"{source_id} cannot authorize image reuse")
            if rights["derived_geometry_use"] != "prohibited":
                raise WorldSliceScopeError(f"{source_id} cannot authorize derived geometry")
        if source_id.startswith("source-getty-"):
            if rights["license"] != "ODC-By-1.0":
                raise WorldSliceScopeError(f"{source_id} must preserve Getty ODC-By 1.0 licensing")
            if not rights["attribution"].strip():
                raise WorldSliceScopeError(f"{source_id} must preserve Getty attribution")
        if source["source_type"] != "license_policy" and source_id not in used_source_refs:
            raise WorldSliceScopeError(f"unused candidate source is outside the frozen scope: {source_id}")
        if rights["access_status"] != "accessible":
            raise WorldSliceScopeError(f"frozen source must record verified access: {source_id}")

    manifest_gap_refs = set(selection["known_gap_refs"])
    if manifest_gap_refs != set(gap_index):
        raise WorldSliceScopeError("selection known_gap_refs must exactly match coverage_manifest gaps")

    for entry in cost["entries"]:
        if entry["measurement_state"] == "pending" and entry["duration_minutes"] is not None:
            raise WorldSliceScopeError("pending cost entries must not invent a duration")
        if entry["measurement_state"] == "recorded" and entry["duration_minutes"] is None:
            raise WorldSliceScopeError("recorded cost entries require an actual duration")

    used_evidence_refs: set[str] = set()
    used_uncertainty_refs: set[str] = set()
    claimed_object_refs: set[str] = set()
    for claim_id, claim in claim_index.items():
        if claim["target_object_ref"] not in object_index:
            raise WorldSliceScopeError(
                f"Claim {claim_id} references unknown candidate object {claim['target_object_ref']}"
            )
        missing_evidence = set(claim["evidence_link_refs"]) - set(evidence_index)
        if missing_evidence:
            raise WorldSliceScopeError(
                f"Claim {claim_id} references missing EvidenceLinks: {sorted(missing_evidence)}"
            )
        missing_uncertainty = set(claim["uncertainty_refs"]) - set(uncertainty_index)
        if missing_uncertainty:
            raise WorldSliceScopeError(
                f"Claim {claim_id} references missing Uncertainties: {sorted(missing_uncertainty)}"
            )
        used_evidence_refs.update(claim["evidence_link_refs"])
        used_uncertainty_refs.update(claim["uncertainty_refs"])
        claimed_object_refs.add(claim["target_object_ref"])

        linked = [evidence_index[ref] for ref in claim["evidence_link_refs"]]
        target_source_refs = set(object_index[claim["target_object_ref"]]["source_refs"])
        escaped_sources = [
            row["source_id"] for row in linked if row["source_id"] not in target_source_refs
        ]
        if escaped_sources:
            raise WorldSliceScopeError(
                f"Claim {claim_id} uses sources outside its target object's frozen scope: {escaped_sources}"
            )
        escaped = [row["evidence_link_id"] for row in linked if row["claim_id"] != claim_id]
        if escaped:
            raise WorldSliceScopeError(
                f"Claim {claim_id} includes EvidenceLinks bound to another Claim: {escaped}"
            )
        reviewed_relations = {
            row["relation_to_claim"] for row in linked if row["review_state"] == "reviewed"
        }
        if "supports" in reviewed_relations and "challenges" in reviewed_relations:
            derived_evidence_state = "mixed"
        elif "supports" in reviewed_relations:
            derived_evidence_state = "supported"
        elif "challenges" in reviewed_relations:
            derived_evidence_state = "challenged"
        else:
            derived_evidence_state = "missing"
        if claim["evidence_state"] != derived_evidence_state:
            raise WorldSliceScopeError(
                f"Claim {claim_id} evidence_state must derive from reviewed EvidenceLinks: "
                f"{claim['evidence_state']} != {derived_evidence_state}"
            )
        if claim["review_state"] == "reviewed" and not reviewed_relations:
            raise WorldSliceScopeError(
                f"Claim {claim_id} cannot be reviewed without reviewed EvidenceLinks"
            )

    if used_evidence_refs != set(evidence_index):
        raise WorldSliceScopeError("every EvidenceLink must be referenced by exactly its Claim scope")
    if claimed_object_refs != set(object_index):
        missing_claim_targets = sorted(set(object_index) - claimed_object_refs)
        raise WorldSliceScopeError(
            f"every frozen candidate object requires an atomic Claim binding: {missing_claim_targets}"
        )

    for evidence_id, evidence in evidence_index.items():
        if evidence["claim_id"] not in claim_index:
            raise WorldSliceScopeError(
                f"EvidenceLink {evidence_id} references missing Claim {evidence['claim_id']}"
            )
        if evidence["source_id"] not in source_index:
            raise WorldSliceScopeError(
                f"EvidenceLink {evidence_id} references missing Source {evidence['source_id']}"
            )
        if evidence["review_state"] == "draft" and evidence["reviewer"] is not None:
            raise WorldSliceScopeError(
                f"draft EvidenceLink {evidence_id} cannot claim a reviewer"
            )
        if evidence["review_state"] == "reviewed" and not str(evidence["reviewer"] or "").strip():
            raise WorldSliceScopeError(
                f"reviewed EvidenceLink {evidence_id} requires a reviewer"
            )

    for evidence_id, expected in CRITICAL_LOCATOR_BINDINGS.items():
        evidence = evidence_index.get(evidence_id)
        if evidence is None:
            raise WorldSliceScopeError(f"critical locator EvidenceLink is missing: {evidence_id}")
        if evidence["claim_id"] != expected["claim_id"] or evidence["source_id"] != expected["source_id"]:
            raise WorldSliceScopeError(f"critical locator binding drifted: {evidence_id}")
        if evidence["relation_to_claim"] != "supports" or evidence["evidence_strength"] != "direct":
            raise WorldSliceScopeError(f"critical locator strength drifted: {evidence_id}")
        missing_tokens = [
            token for token in expected["required_tokens"] if token not in evidence["locator"]
        ]
        if missing_tokens:
            raise WorldSliceScopeError(
                f"critical locator text drifted for {evidence_id}: missing {missing_tokens}"
            )

    for source_id, source in source_index.items():
        if source["source_type"] == "license_policy":
            continue
        linked_claims = {
            row["claim_id"] for row in evidence_index.values() if row["source_id"] == source_id
        }
        if set(source["intended_claims"]) != linked_claims:
            raise WorldSliceScopeError(
                f"source {source_id} intended Claim refs must match its EvidenceLinks"
            )

    cesenatico_folio_claim = claim_index.get("claim-cesenatico-dated-folio-66v")
    if cesenatico_folio_claim is None:
        raise WorldSliceScopeError("dated Cesenatico folio Claim is missing")
    if "66v" not in cesenatico_folio_claim["statement"] or "68r" in cesenatico_folio_claim["statement"]:
        raise WorldSliceScopeError("dated Cesenatico Claim must bind folio 66v, not folio 68r")

    cesena_wall_claim = claim_index.get("claim-cesena-survey-folios-9r-10r")
    if cesena_wall_claim is None:
        raise WorldSliceScopeError("Cesena wall-survey Claim must remain traceable")
    if (
        cesena_wall_claim["review_state"] != "rejected"
        or cesena_wall_claim["evidence_state"] != "missing"
        or cesena_wall_claim["confidence"] != "low"
    ):
        raise WorldSliceScopeError(
            "Cesena folios 9r–10r Claim must remain rejected and unsupported in Gate C"
        )
    if any(
        evidence_index[ref]["review_state"] == "reviewed"
        for ref in cesena_wall_claim["evidence_link_refs"]
    ):
        raise WorldSliceScopeError(
            "Cesena folios 9r–10r Claim cannot acquire reviewed evidence without a new gate"
        )

    known_uncertainty_targets = set(claim_index) | set(object_index)
    for uncertainty_id, uncertainty in uncertainty_index.items():
        missing_targets = set(uncertainty["target_refs"]) - known_uncertainty_targets
        if missing_targets:
            raise WorldSliceScopeError(
                f"Uncertainty {uncertainty_id} references missing targets: {sorted(missing_targets)}"
            )
        missing_basis_claims = set(uncertainty["basis_claim_refs"]) - set(claim_index)
        if missing_basis_claims:
            raise WorldSliceScopeError(
                f"Uncertainty {uncertainty_id} references missing basis Claims: {sorted(missing_basis_claims)}"
            )
        if uncertainty["basis_kind"] == "claim_refs" and not uncertainty["basis_claim_refs"]:
            raise WorldSliceScopeError(
                f"Uncertainty {uncertainty_id} requires at least one basis Claim"
            )
        if uncertainty["basis_kind"] != "claim_refs" and uncertainty["basis_claim_refs"]:
            raise WorldSliceScopeError(
                f"Uncertainty {uncertainty_id} cannot hide Claim refs behind {uncertainty['basis_kind']}"
            )
        for target_ref in uncertainty["target_refs"]:
            if target_ref in claim_index and uncertainty_id not in claim_index[target_ref]["uncertainty_refs"]:
                raise WorldSliceScopeError(
                    f"Uncertainty {uncertainty_id} is not reciprocally bound by Claim {target_ref}"
                )
    if used_uncertainty_refs != set(uncertainty_index):
        raise WorldSliceScopeError("every Uncertainty must be referenced by at least one atomic Claim")

    global_event_candidates = [
        row
        for row in object_index.values()
        if row["object_type"] == "Event" and "layer-global-simultaneity" in row["layer_refs"]
    ]
    if len(global_event_candidates) != 1:
        raise WorldSliceScopeError("scope must include exactly one source-bound global Event candidate")

    readiness = selection["readiness"]
    if (
        readiness["scope_frozen"] is not True
        or readiness["historical_objects_ready"] is not False
        or readiness["promotion_allowed"] is not False
        or readiness["independent_review_count"] not in {0, 2}
    ):
        raise WorldSliceScopeError("scope-freeze readiness must remain explicitly non-promotable")
    if readiness["independent_review_count"] == 2:
        review_registry = _load(REVIEW_REGISTRY_PATH)
        _validate_schema(
            review_registry, _load(REVIEW_REGISTRY_SCHEMA_PATH), "review registry"
        )
        if len(review_registry["reviews"]) != 2 or any(
            review["decision"] != "READY" for review in review_registry["reviews"]
        ):
            raise WorldSliceScopeError("review count requires two READY review records")

    return {
        "slice_id": selection["slice_id"],
        "status": selection["status"],
        "candidate_object_count": len(object_index),
        "source_count": len(source_index),
        "known_gap_count": len(gap_index),
        "trajectory_gap_count": len(gap_segments),
        "region_version_count": len(versions),
        "claim_count": len(claim_index),
        "evidence_link_count": len(evidence_index),
        "uncertainty_count": len(uncertainty_index),
        "promotion_allowed": readiness["promotion_allowed"],
    }


def main() -> int:
    try:
        summary = validate_package()
    except WorldSliceScopeError as exc:
        print(f"Leonardo World Slice scope: FAIL: {exc}")
        return 1
    print(
        "Leonardo World Slice scope: PASS "
        f"(objects={summary['candidate_object_count']}, sources={summary['source_count']}, "
        f"gaps={summary['known_gap_count']}, claims={summary['claim_count']}, "
        f"evidence_links={summary['evidence_link_count']}, "
        f"region_versions={summary['region_version_count']}, "
        f"promotion_allowed={summary['promotion_allowed']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
