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
    "presence-leonardo-vinci-birth-1452": ("1452-04-15", "1452-04-15", "day"),
    "presence-leonardo-florence-st-luke-1472": ("1472", "1472", "year"),
    "presence-leonardo-milan-altarpiece-contract-1483": (
        "1483-04-25",
        "1483-04-25",
        "day",
    ),
    "presence-leonardo-florence-second-period-1503": ("1503", "1503", "year"),
    "presence-leonardo-milan-ms-f-1508-09-12": (
        "1508-09-12",
        "1508-09-12",
        "day",
    ),
    "presence-leonardo-rome-belvedere-1513-1516": (
        "1513",
        "1516",
        "year_range_with_approximate_year_locator",
    ),
    "presence-leonardo-amboise-clos-luce-1516-1519": (
        "1516",
        "1519-05-02",
        "season_year_start_and_day_end",
    ),
}
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
EXTERNAL_TRAJECTORY_REF = "trajectory-leonardo-romagna-1502"


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

    period_presence_refs: set[str] = set()
    for period_id, period in periods.items():
        if not period["presentation_only"]:
            raise MajorLifePackageError(f"macro-period {period_id} cannot become a World Model entity")
        for presence_ref in period["presence_refs"]:
            if presence_ref not in presences:
                raise MajorLifePackageError(
                    f"macro-period {period_id} references missing Presence {presence_ref}"
                )
            period_presence_refs.add(presence_ref)
    if period_presence_refs != set(presences):
        raise MajorLifePackageError("every Presence must belong to exactly the bounded period set")

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
            presence["temporal"]["start"],
            presence["temporal"]["end"],
            presence["temporal"]["precision"],
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

    trajectory = package["trajectory"]
    if trajectory["geometry"] is not None or trajectory["route_status"] != "unknown_route":
        raise MajorLifePackageError("candidate whole-life Trajectory must remain geometry-free")
    external = trajectory["external_segments"][0]
    if external["trajectory_ref"] != EXTERNAL_TRAJECTORY_REF:
        raise MajorLifePackageError("frozen Romagna segment identity drifted")
    if external["identity_policy"] != "reference_only_do_not_copy_or_rewrite":
        raise MajorLifePackageError("frozen Romagna identities must be referenced, not copied")

    allowed_transition_refs = set(presences) | {EXTERNAL_TRAJECTORY_REF}
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
        for evidence_ref in claim["evidence_link_refs"]:
            if evidence[evidence_ref]["claim_id"] != claim_id:
                raise MajorLifePackageError(
                    f"EvidenceLink {evidence_ref} escaped its atomic Claim {claim_id}"
                )

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

    valid_uncertainty_targets = set(presences) | {trajectory["trajectory_id"]}
    for uncertainty_id, uncertainty in uncertainties.items():
        missing_targets = set(uncertainty["target_refs"]) - valid_uncertainty_targets
        if missing_targets:
            raise MajorLifePackageError(
                f"Uncertainty {uncertainty_id} references missing targets: {sorted(missing_targets)}"
            )

    if set(package["relation_policy"]["prohibited_predicates"]) != EXPECTED_PROHIBITED_RELATIONS:
        raise MajorLifePackageError("deferred #331 Relation boundary drifted")
    if package["relation_policy"]["stored_relations"]:
        raise MajorLifePackageError("candidate package cannot store Relations while #331 is deferred")

    audit = package["audit"]
    if audit["canonical_review_status"] != "pending_independent_review":
        raise MajorLifePackageError("candidate package cannot self-assert canonical review completion")
    if audit["current_decision"] is not None:
        raise MajorLifePackageError("candidate package decision requires a later reviewed revision")
    if audit["curation_cost"]["duration_minutes"] is not None:
        raise MajorLifePackageError("historical Drive work cannot receive a retrospective estimate")

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
