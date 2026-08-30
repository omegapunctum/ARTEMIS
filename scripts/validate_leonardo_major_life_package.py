#!/usr/bin/env python3
"""Validate the non-public Leonardo major-life Presence candidate package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_major_life" / "v1"
PACKAGE_PATH = PACKAGE_ROOT / "package.json"
SCHEMA_PATH = PACKAGE_ROOT / "package.schema.json"

EXPECTED_PRESENCE_PROFILES = {
    "presence-leonardo-vinci-birth-1452": (
        "15 April 1452", "1452-04-15", "1452-04-15", "day", "exact", "exact"
    ),
    "presence-leonardo-florence-st-luke-1472": (
        "1472", "1472", "1472", "year", "exact", "exact"
    ),
    "presence-leonardo-milan-altarpiece-contract-1483": (
        "surviving contract dated 25 April 1483",
        "1483",
        "1483",
        "year",
        "source_context_year",
        "source_context_year",
    ),
    "presence-leonardo-florence-second-period-1503": (
        "1503", "1503", "1503", "year", "exact", "exact"
    ),
    "presence-leonardo-milan-ms-f-1508-09-12": (
        "cominciato a Milano addì 12 settembre 1508",
        "1508-09-12",
        "1508-09-12",
        "day",
        "exact",
        "exact",
    ),
    "presence-leonardo-rome-belvedere-1513-1516": (
        "Roman stay 1513–1516; Belvedere work locator circa 1514",
        "1513",
        "1516",
        "year_range_with_approximate_year_locator",
        "not_before",
        "not_after",
    ),
    "presence-leonardo-amboise-clos-luce-1516-1519": (
        "settled in autumn 1516; died there 2 May 1519",
        "1516-09",
        "1519-05-02",
        "bounded_season_start_and_day_end",
        "not_before",
        "exact",
    ),
}
EXPECTED_CLAIM_SLUGS = {
    "presence-leonardo-vinci-birth-1452": "vinci-1452",
    "presence-leonardo-florence-st-luke-1472": "florence-1472",
    "presence-leonardo-milan-altarpiece-contract-1483": "milan-contract-1483",
    "presence-leonardo-florence-second-period-1503": "florence-1503",
    "presence-leonardo-milan-ms-f-1508-09-12": "milan-ms-f-1508",
    "presence-leonardo-rome-belvedere-1513-1516": "rome-belvedere-1513-1516",
    "presence-leonardo-amboise-clos-luce-1516-1519": "clos-luce-1516-1519",
}
CLAIM_DIMENSIONS = ("identity", "time", "place", "selection_significance")
EXPECTED_PROHIBITED_RELATIONS = {
    "possible_encounter",
    "documented_encounter",
    "interaction",
    "influence",
    "causal",
}
EXPECTED_PLACE_IDS = {
    "place-vinci",
    "place-florence",
    "place-milan",
    "place-vatican-belvedere",
    "place-clos-luce",
}
EXPECTED_PERIOD_MEMBERSHIP = {
    "period-leonardo-vinci-florence-formation": (
        "presence-leonardo-vinci-birth-1452",
        "presence-leonardo-florence-st-luke-1472",
    ),
    "period-leonardo-milan-i": ("presence-leonardo-milan-altarpiece-contract-1483",),
    "period-leonardo-florence-ii": ("presence-leonardo-florence-second-period-1503",),
    "period-leonardo-milan-ii": ("presence-leonardo-milan-ms-f-1508-09-12",),
    "period-leonardo-rome": ("presence-leonardo-rome-belvedere-1513-1516",),
    "period-leonardo-amboise-clos-luce": ("presence-leonardo-amboise-clos-luce-1516-1519",),
}
EXPECTED_TRANSITION_TOPOLOGY = (
    ("transition-vinci-to-florence-unknown", "presence-leonardo-vinci-birth-1452", "presence-leonardo-florence-st-luke-1472"),
    ("transition-florence-to-milan-i-unknown", "presence-leonardo-florence-st-luke-1472", "presence-leonardo-milan-altarpiece-contract-1483"),
    ("transition-milan-i-to-romagna-unknown", "presence-leonardo-milan-altarpiece-contract-1483", "trajectory-leonardo-romagna-1502"),
    ("transition-romagna-to-florence-ii-unknown", "trajectory-leonardo-romagna-1502", "presence-leonardo-florence-second-period-1503"),
    ("transition-florence-ii-to-milan-ii-unknown", "presence-leonardo-florence-second-period-1503", "presence-leonardo-milan-ms-f-1508-09-12"),
    ("transition-milan-ii-to-rome-unknown", "presence-leonardo-milan-ms-f-1508-09-12", "presence-leonardo-rome-belvedere-1513-1516"),
    ("transition-rome-to-amboise-unknown", "presence-leonardo-rome-belvedere-1513-1516", "presence-leonardo-amboise-clos-luce-1516-1519"),
)
EXTERNAL_TRAJECTORY_REF = "trajectory-leonardo-romagna-1502"
FROZEN_ROMAGNA = {
    "frozen_commit": "bd2e103cdeec615cb19f0a4293c708fe37a4ae52",
    "frozen_tree": "757fc3d0701e825e865ceeec401d233484f066b7",
    "reviewed_content_digest": "1323ca8f0e85e0d1287cdf8d78db8fcfd907551d7a7dbb37646725cbba72ddca",
    "review_registry_ref": "fixtures/world_slices/leonardo_romagna_1502/v1/review_registry.json",
    "gate_decision_ref": "fixtures/world_slices/leonardo_romagna_1502/v1/gate_c_decision.json",
    "presence_refs": [
        "segment-rimini-presence",
        "segment-cesena-presence",
        "segment-cesenatico-presence",
        "segment-imola-presence",
    ],
}


class MajorLifePackageError(ValueError):
    """Raised when the candidate package violates its fail-closed boundary."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MajorLifePackageError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MajorLifePackageError(f"{path} must contain a JSON object")
    return value


def _index(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get(key) or "")
        if not identity:
            raise MajorLifePackageError(f"{label} row missing {key}")
        if identity in result:
            raise MajorLifePackageError(f"duplicate {label} {key}: {identity}")
        result[identity] = row
    return result


def _validate_schema(package: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    if not errors:
        return
    messages = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]
    raise MajorLifePackageError(f"package schema validation failed: {'; '.join(messages)}")


def validate_package(package: dict[str, Any] | None = None) -> dict[str, Any]:
    package = _load(PACKAGE_PATH) if package is None else package
    _validate_schema(package)

    places = _index(package["places"], "place_id", "Place")
    periods = _index(package["macro_periods"], "period_id", "macro-period")
    presences = _index(package["presences"], "presence_id", "Presence")
    transitions = _index(package["transitions"], "transition_id", "transition")
    sources = _index(package["sources"], "source_id", "Source")
    claims = _index(package["claims"], "claim_id", "Claim")
    evidence = _index(package["evidence_links"], "evidence_link_id", "EvidenceLink")
    uncertainties = _index(package["uncertainties"], "uncertainty_id", "Uncertainty")

    if set(presences) != set(EXPECTED_PRESENCE_PROFILES):
        raise MajorLifePackageError("the seven reviewed Presence identities drifted")
    if set(places) != EXPECTED_PLACE_IDS:
        raise MajorLifePackageError("the five named Place identities drifted")

    if set(periods) != set(EXPECTED_PERIOD_MEMBERSHIP):
        raise MajorLifePackageError("the six reviewed macro-period identities drifted")
    membership_count = {presence_id: 0 for presence_id in presences}
    for period_id, period in periods.items():
        if not period["presentation_only"]:
            raise MajorLifePackageError(f"macro-period {period_id} cannot become a World Model entity")
        if tuple(period["presence_refs"]) != EXPECTED_PERIOD_MEMBERSHIP[period_id]:
            raise MajorLifePackageError(f"macro-period {period_id} membership or order drifted")
        for presence_ref in period["presence_refs"]:
            if presence_ref not in presences:
                raise MajorLifePackageError(
                    f"macro-period {period_id} references missing Presence {presence_ref}"
                )
            membership_count[presence_ref] += 1
    if set(membership_count.values()) != {1}:
        raise MajorLifePackageError("every Presence must belong to exactly one macro-period")

    for presence_id, presence in presences.items():
        if presence["period_ref"] not in periods:
            raise MajorLifePackageError(
                f"Presence {presence_id} references missing macro-period {presence['period_ref']}"
            )
        if presence_id not in periods[presence["period_ref"]]["presence_refs"]:
            raise MajorLifePackageError(
                f"Presence {presence_id} and macro-period {presence['period_ref']} are not reciprocal"
            )
        expected = EXPECTED_PRESENCE_PROFILES[presence_id]
        actual = (
            presence["temporal"]["source_native"],
            presence["temporal"]["start"],
            presence["temporal"]["end"],
            presence["temporal"]["precision"],
            presence["temporal"]["start_qualifier"],
            presence["temporal"]["end_qualifier"],
        )
        if actual != expected:
            raise MajorLifePackageError(
                f"Presence {presence_id} temporal precision drifted: expected {expected}, got {actual}"
            )
        if presence["geometry"] is not None:
            raise MajorLifePackageError(f"Presence {presence_id} cannot publish geometry before review")
        if presence["place_ref"] not in places:
            raise MajorLifePackageError(
                f"Presence {presence_id} references missing Place {presence['place_ref']}"
            )
        if presence["place_label"] != places[presence["place_ref"]]["label"]:
            raise MajorLifePackageError(
                f"Presence {presence_id} and Place {presence['place_ref']} labels drifted"
            )
        missing_claims = set(presence["claim_refs"]) - set(claims)
        if missing_claims:
            raise MajorLifePackageError(
                f"Presence {presence_id} references missing Claims: {sorted(missing_claims)}"
            )
        expected_claims = {
            f"claim-{EXPECTED_CLAIM_SLUGS[presence_id]}-{dimension.replace('_', '-')}"
            for dimension in CLAIM_DIMENSIONS
        }
        if set(presence["claim_refs"]) != expected_claims:
            raise MajorLifePackageError(
                f"Presence {presence_id} must own exactly its four atomic Claims"
            )
        missing_uncertainties = set(presence["uncertainty_refs"]) - set(uncertainties)
        if missing_uncertainties:
            raise MajorLifePackageError(
                f"Presence {presence_id} references missing Uncertainties: {sorted(missing_uncertainties)}"
            )

    for place_id, place in places.items():
        if place["geometry"] is not None:
            raise MajorLifePackageError(f"Place {place_id} cannot publish geometry before review")
        missing_claims = set(place["claim_refs"]) - set(claims)
        if missing_claims:
            raise MajorLifePackageError(
                f"Place {place_id} references missing Claims: {sorted(missing_claims)}"
            )
        for claim_ref in place["claim_refs"]:
            target_ref = claims[claim_ref]["target_ref"]
            if target_ref not in presences:
                raise MajorLifePackageError(
                    f"Place {place_id} Claim {claim_ref} references missing Presence {target_ref}"
                )
            target_presence = presences[target_ref]
            if target_presence["place_ref"] != place_id:
                raise MajorLifePackageError(
                    f"Place {place_id} Claim {claim_ref} targets a different Place"
                )
            if claims[claim_ref]["claim_dimension"] != "place":
                raise MajorLifePackageError(
                    f"Place {place_id} may own only place-dimension Claims"
                )
        expected_place_claims = {
            f"claim-{EXPECTED_CLAIM_SLUGS[presence_id]}-place"
            for presence_id, presence in presences.items()
            if presence["place_ref"] == place_id
        }
        if set(place["claim_refs"]) != expected_place_claims:
            raise MajorLifePackageError(f"Place {place_id} Claim ownership is incomplete")

    trajectory = package["trajectory"]
    if trajectory["geometry"] is not None or trajectory["route_status"] != "unknown_route":
        raise MajorLifePackageError("candidate whole-life Trajectory must remain geometry-free")
    external = trajectory["external_segments"][0]
    if external["trajectory_ref"] != EXTERNAL_TRAJECTORY_REF:
        raise MajorLifePackageError("frozen Romagna segment identity drifted")
    if external["identity_policy"] != "reference_only_do_not_copy_or_rewrite":
        raise MajorLifePackageError("frozen Romagna identities must be referenced, not copied")
    for field, expected in FROZEN_ROMAGNA.items():
        if external[field] != expected:
            raise MajorLifePackageError(f"frozen Romagna {field} drifted")
    gate_decision = _load(ROOT / external["gate_decision_ref"])
    review_registry = _load(ROOT / external["review_registry_ref"])
    for field in ("frozen_commit", "frozen_tree", "reviewed_content_digest"):
        if gate_decision[field] != external[field] or review_registry[field] != external[field]:
            raise MajorLifePackageError(f"frozen Romagna {field} does not match reviewed Gate C")
    selection = _load(ROOT / external["package_ref"] / "selection_manifest.json")
    trajectory_rows = [
        row for row in selection["candidate_objects"]
        if row.get("object_id") == EXTERNAL_TRAJECTORY_REF
    ]
    if len(trajectory_rows) != 1:
        raise MajorLifePackageError("frozen Romagna Trajectory cannot be resolved exactly once")
    frozen_presence_refs = [
        segment["segment_id"]
        for segment in trajectory_rows[0]["segments"]
        if segment["segment_kind"] == "presence"
    ]
    if frozen_presence_refs != external["presence_refs"]:
        raise MajorLifePackageError("frozen Romagna Presence identities drifted")

    allowed_transition_refs = set(presences) | {EXTERNAL_TRAJECTORY_REF}
    actual_topology = tuple(
        (row["transition_id"], row["from_ref"], row["to_ref"])
        for row in package["transitions"]
    )
    if actual_topology != EXPECTED_TRANSITION_TOPOLOGY:
        raise MajorLifePackageError("ordered major-life transition topology drifted")
    for transition_id, transition in transitions.items():
        if transition["from_ref"] not in allowed_transition_refs:
            raise MajorLifePackageError(
                f"transition {transition_id} has unknown from_ref {transition['from_ref']}"
            )
        if transition["to_ref"] not in allowed_transition_refs:
            raise MajorLifePackageError(
                f"transition {transition_id} has unknown to_ref {transition['to_ref']}"
            )
        if transition["route_status"] != "unknown_route" or transition["geometry"] is not None:
            raise MajorLifePackageError(
                f"transition {transition_id} cannot carry historical route geometry"
            )
        if transition["source_refs"]:
            raise MajorLifePackageError(
                f"unknown transition {transition_id} cannot pretend to have route evidence"
            )

    expected_claim_ids = {
        f"claim-{slug}-{dimension.replace('_', '-')}"
        for slug in EXPECTED_CLAIM_SLUGS.values()
        for dimension in CLAIM_DIMENSIONS
    }
    if set(claims) != expected_claim_ids:
        raise MajorLifePackageError("atomic Claim identity set drifted")

    used_evidence: set[str] = set()
    used_uncertainties: set[str] = set()
    for claim_id, claim in claims.items():
        if claim["target_ref"] not in presences:
            raise MajorLifePackageError(
                f"Claim {claim_id} references missing Presence {claim['target_ref']}"
            )
        missing_evidence = set(claim["evidence_link_refs"]) - set(evidence)
        if missing_evidence:
            raise MajorLifePackageError(
                f"Claim {claim_id} references missing EvidenceLinks: {sorted(missing_evidence)}"
            )
        missing_uncertainties = set(claim["uncertainty_refs"]) - set(uncertainties)
        if missing_uncertainties:
            raise MajorLifePackageError(
                f"Claim {claim_id} references missing Uncertainties: {sorted(missing_uncertainties)}"
            )
        target_presence = claim["target_ref"]
        expected_id = (
            f"claim-{EXPECTED_CLAIM_SLUGS[target_presence]}-"
            f"{claim['claim_dimension'].replace('_', '-')}"
        )
        if claim_id != expected_id:
            raise MajorLifePackageError(f"Claim {claim_id} target/dimension ownership drifted")
        if claim_id not in presences[target_presence]["claim_refs"]:
            raise MajorLifePackageError(f"Claim {claim_id} is not reciprocally owned by its Presence")
        supporting = [
            evidence[ref]
            for ref in claim["evidence_link_refs"]
            if evidence[ref]["relation_to_claim"] == "supports"
        ]
        if not supporting:
            raise MajorLifePackageError(f"Claim {claim_id} has no supporting EvidenceLink")
        for evidence_ref in claim["evidence_link_refs"]:
            if evidence[evidence_ref]["claim_id"] != claim_id:
                raise MajorLifePackageError(
                    f"EvidenceLink {evidence_ref} escaped its atomic Claim {claim_id}"
                )
            used_evidence.add(evidence_ref)
        used_uncertainties.update(claim["uncertainty_refs"])

    if used_evidence != set(evidence):
        raise MajorLifePackageError("orphan EvidenceLink detected")

    used_sources: set[str] = set()
    for evidence_id, link in evidence.items():
        if link["claim_id"] not in claims:
            raise MajorLifePackageError(
                f"EvidenceLink {evidence_id} references missing Claim {link['claim_id']}"
            )
        if link["source_id"] not in sources:
            raise MajorLifePackageError(
                f"EvidenceLink {evidence_id} references missing Source {link['source_id']}"
            )
        if evidence_id not in claims[link["claim_id"]]["evidence_link_refs"]:
            raise MajorLifePackageError(
                f"EvidenceLink {evidence_id} is not reciprocally registered on its Claim"
            )
        if link["relation_to_claim"] == "supports" and link["evidence_strength"] == "background":
            raise MajorLifePackageError(
                f"supporting EvidenceLink {evidence_id} cannot have background strength"
            )
        used_sources.add(link["source_id"])

    if used_sources != set(sources):
        raise MajorLifePackageError("orphan Source detected")

    valid_uncertainty_targets = set(presences) | {trajectory["trajectory_id"]}
    for uncertainty_id, uncertainty in uncertainties.items():
        missing_targets = set(uncertainty["target_refs"]) - valid_uncertainty_targets
        if missing_targets:
            raise MajorLifePackageError(
                f"Uncertainty {uncertainty_id} references missing targets: {sorted(missing_targets)}"
            )
        missing_basis = set(uncertainty["basis_claim_refs"]) - set(claims)
        if missing_basis:
            raise MajorLifePackageError(
                f"Uncertainty {uncertainty_id} references missing basis Claims: {sorted(missing_basis)}"
            )
        for claim_ref in uncertainty["basis_claim_refs"]:
            if uncertainty_id not in claims[claim_ref]["uncertainty_refs"]:
                raise MajorLifePackageError(
                    f"Uncertainty {uncertainty_id} is not reciprocal with Claim {claim_ref}"
                )
        if uncertainty_id not in used_uncertainties:
            raise MajorLifePackageError(f"orphan Uncertainty {uncertainty_id} detected")
        for target_ref in uncertainty["target_refs"]:
            target_uncertainties = (
                trajectory["uncertainty_refs"]
                if target_ref == trajectory["trajectory_id"]
                else presences[target_ref]["uncertainty_refs"]
            )
            if uncertainty_id not in target_uncertainties:
                raise MajorLifePackageError(
                    f"Uncertainty {uncertainty_id} is not reciprocally registered on {target_ref}"
                )
        bounds = uncertainty["possible_bounds"]
        if uncertainty["projection_effect"] == "show_possible" and bounds is None:
            raise MajorLifePackageError(
                f"Uncertainty {uncertainty_id} requires explicit possible bounds"
            )

    if set(package["relation_policy"]["prohibited_predicates"]) != EXPECTED_PROHIBITED_RELATIONS:
        raise MajorLifePackageError("deferred #331 Relation boundary drifted")
    if package["relation_policy"]["stored_relations"]:
        raise MajorLifePackageError("candidate package cannot store Relations while #331 is deferred")

    audit = package["audit"]
    if audit["canonical_review_status"] != "pending_independent_rereview":
        raise MajorLifePackageError("candidate package cannot self-assert canonical review completion")
    if audit["current_decision"] is not None:
        raise MajorLifePackageError("candidate package decision requires a later reviewed revision")
    if audit["curation_cost"]["duration_minutes"] is not None:
        raise MajorLifePackageError("historical Drive work cannot receive a retrospective estimate")
    if len(audit["prior_reviews"]) != 1 or audit["prior_reviews"][0]["decision"] != "NARROW":
        raise MajorLifePackageError("round-1 NARROW review history must remain preserved")

    coverage = package["coverage"]
    if coverage["new_presence_count"] != len(presences):
        raise MajorLifePackageError("new Presence coverage count drifted")
    if coverage["composed_anchor_count"] != len(presences) + external["presence_count"]:
        raise MajorLifePackageError("composed whole-life anchor count drifted")

    return {
        "package_id": package["package_id"],
        "status": package["status"],
        "place_count": len(places),
        "macro_period_count": len(periods),
        "new_presence_count": len(presences),
        "referenced_romagna_presence_count": external["presence_count"],
        "composed_anchor_count": coverage["composed_anchor_count"],
        "new_unknown_transition_count": len(transitions),
        "source_count": len(sources),
        "claim_count": len(claims),
        "evidence_link_count": len(evidence),
        "uncertainty_count": len(uncertainties),
        "runtime_authorized": package["runtime_authorized"],
        "canonical_review_status": audit["canonical_review_status"],
        "prior_review_decision": audit["prior_reviews"][0]["decision"],
    }


def main() -> int:
    try:
        summary = validate_package()
    except MajorLifePackageError as exc:
        print(f"Leonardo major-life package validation failed: {exc}")
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
