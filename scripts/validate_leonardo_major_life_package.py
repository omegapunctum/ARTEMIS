#!/usr/bin/env python3
"""Validate the non-public Leonardo major-life Presence candidate package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

try:
    from scripts.validate_project_state import ProjectStateError, _validate_frozen_git_revision
except ModuleNotFoundError:  # direct script execution from scripts/
    from validate_project_state import ProjectStateError, _validate_frozen_git_revision


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "fixtures" / "world_slices" / "leonardo_major_life" / "v1"
PACKAGE_PATH = PACKAGE_ROOT / "package.json"
SCHEMA_PATH = PACKAGE_ROOT / "package.schema.json"
EXPECTED_CANDIDATE_CONTENT_DIGEST = (
    "45d3bafc17be34c461f3745d50f688682d113ac463ad69118bdbccaa3071aaa9"
)
EXPECTED_REVIEW_PREFIX_DIGEST = (
    "9fcf0d6b8c1278146367b83924f7c39f725e0a2de7282c2df49fc5ab1c8842d0"
)

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
EXPECTED_EVIDENCE_SOURCES = {
    "presence-leonardo-vinci-birth-1452": (
        "source-museo-leonardiano-places", "source-nga-leonardo-biography"
    ),
    "presence-leonardo-florence-st-luke-1472": (
        "source-museo-leonardiano-biography", "source-nga-leonardo-biography"
    ),
    "presence-leonardo-milan-altarpiece-contract-1483": (
        "source-national-gallery-lost-altarpiece", "source-national-gallery-virgin-rocks"
    ),
    "presence-leonardo-florence-second-period-1503": (
        "source-uffizi-leonardo-room", "source-louvre-leonardo-biography"
    ),
    "presence-leonardo-milan-ms-f-1508-09-12": (
        "source-museo-galileo-leonardo-chronology", "source-institut-france-carnet-f"
    ),
    "presence-leonardo-rome-belvedere-1513-1516": (
        "source-museo-galileo-leonardo-chronology", "source-museo-galileo-atl-0426-1"
    ),
    "presence-leonardo-amboise-clos-luce-1516-1519": (
        "source-clos-luce-leonardo-biography", "source-louvre-leonardo-biography"
    ),
}
EXPECTED_SOURCE_IDS = {
    source_id
    for pair in EXPECTED_EVIDENCE_SOURCES.values()
    for source_id in pair
}
EXPECTED_PRESENCE_SEMANTICS = {
    "presence-leonardo-vinci-birth-1452": (
        "documented_presence_anchor", "named_settlement", ("uncertainty-vinci-exact-birthplace",)
    ),
    "presence-leonardo-florence-st-luke-1472": (
        "documented_presence_anchor", "named_city", ("uncertainty-florence-1472-address",)
    ),
    "presence-leonardo-milan-altarpiece-contract-1483": (
        "documentary_context_anchor", "named_city_with_institutional_context",
        ("uncertainty-milan-1483-body-position",),
    ),
    "presence-leonardo-florence-second-period-1503": (
        "documented_presence_anchor", "named_city",
        ("uncertainty-florence-1500-1506-continuity",),
    ),
    "presence-leonardo-milan-ms-f-1508-09-12": (
        "source_native_manuscript_anchor", "named_city_with_parish_context",
        ("uncertainty-milan-1506-1513-continuity",),
    ),
    "presence-leonardo-rome-belvedere-1513-1516": (
        "residence_range_not_continuous_position", "named_complex",
        ("uncertainty-rome-daily-position",),
    ),
    "presence-leonardo-amboise-clos-luce-1516-1519": (
        "residence_range_not_continuous_position", "named_residence",
        ("uncertainty-amboise-continuous-position",),
    ),
}
EXPECTED_UNCERTAINTY_PROFILES = {
    "uncertainty-vinci-exact-birthplace": (
        ("presence-leonardo-vinci-birth-1452",), "spatial_precision",
        ("claim-vinci-1452-place",), "explicit_missing_exactness_evidence",
        "prohibit_geometry", None,
    ),
    "uncertainty-florence-1472-address": (
        ("presence-leonardo-florence-st-luke-1472",), "spatial_precision",
        ("claim-florence-1472-place",), "explicit_missing_exactness_evidence",
        "prohibit_geometry", None,
    ),
    "uncertainty-milan-1483-body-position": (
        ("presence-leonardo-milan-altarpiece-contract-1483",), "spatial_precision",
        ("claim-milan-contract-1483-place",), "explicit_missing_exactness_evidence",
        "prohibit_geometry", None,
    ),
    "uncertainty-florence-1500-1506-continuity": (
        ("presence-leonardo-florence-second-period-1503",), "temporal_coverage",
        ("claim-florence-1503-time",), "explicit_missing_exactness_evidence",
        "show_unknown", None,
    ),
    "uncertainty-milan-1506-1513-continuity": (
        ("presence-leonardo-milan-ms-f-1508-09-12",), "temporal_coverage",
        ("claim-milan-ms-f-1508-time",), "explicit_missing_exactness_evidence",
        "show_unknown", None,
    ),
    "uncertainty-rome-daily-position": (
        ("presence-leonardo-rome-belvedere-1513-1516",), "spatiotemporal_coverage",
        ("claim-rome-belvedere-1513-1516-time", "claim-rome-belvedere-1513-1516-place"),
        "explicit_missing_exactness_evidence", "show_possible",
        {"not_before": "1513", "not_after": "1516", "start_inclusive": True, "end_inclusive": True},
    ),
    "uncertainty-amboise-continuous-position": (
        ("presence-leonardo-amboise-clos-luce-1516-1519",), "spatiotemporal_coverage",
        ("claim-clos-luce-1516-1519-time", "claim-clos-luce-1516-1519-place"),
        "explicit_missing_exactness_evidence", "show_possible",
        {"not_before": "1516-09", "not_after": "1516-11", "start_inclusive": True, "end_inclusive": True},
    ),
    "uncertainty-major-life-route-and-coverage": (
        ("trajectory-leonardo-major-life-v1",), "trajectory_and_corpus_coverage",
        tuple(
            f"claim-{slug}-selection-significance"
            for slug in EXPECTED_CLAIM_SLUGS.values()
        ),
        "explicit_missing_route_evidence", "prohibit_geometry", None,
    ),
}
EXPECTED_ROMAGNA_SEGMENTS = (
    ("segment-rimini-presence", "presence", "place-rimini", "named_place", None,
     ("source-visit-romagna-leonardo-borgia", "source-uniurb-volpe-chronology")),
    ("segment-rimini-cesena-gap", "inferred_gap", None, "unknown_route", None, ()),
    ("segment-cesena-presence", "presence", "place-cesena", "named_place", None,
     ("source-visit-romagna-leonardo-borgia", "source-museo-galileo-ms-l", "source-uniurb-volpe-chronology")),
    ("segment-cesena-cesenatico-gap", "inferred_gap", None, "unknown_route", None, ()),
    ("segment-cesenatico-presence", "presence", "place-cesenatico", "named_place", None,
     ("source-visit-romagna-leonardo-borgia", "source-museo-galileo-ms-l", "source-uniurb-volpe-chronology")),
    ("segment-cesenatico-imola-gap", "inferred_gap", None, "unknown_route", None, ()),
    ("segment-imola-presence", "presence", "place-imola", "named_place", None,
     ("source-rct-imola-map", "source-imola-civic-museums-rocca")),
)
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


def _temporal_key(value: str, *, upper: bool = False) -> tuple[int, int, int]:
    parts = [int(part) for part in value.split("-")]
    year = parts[0]
    month = parts[1] if len(parts) > 1 else (12 if upper else 1)
    day = parts[2] if len(parts) > 2 else (31 if upper else 1)
    return year, month, day


def _expected_claim_uncertainties(claim_id: str) -> tuple[str, ...]:
    return tuple(
        uncertainty_id
        for uncertainty_id, profile in EXPECTED_UNCERTAINTY_PROFILES.items()
        if claim_id in profile[2]
    )


def _expected_evidence_profiles() -> dict[str, tuple[str, str, str, str]]:
    profiles: dict[str, tuple[str, str, str, str]] = {}
    for presence_id, slug in EXPECTED_CLAIM_SLUGS.items():
        primary_source, secondary_source = EXPECTED_EVIDENCE_SOURCES[presence_id]
        for dimension in CLAIM_DIMENSIONS:
            dimension_slug = dimension.replace("_", "-")
            claim_id = f"claim-{slug}-{dimension_slug}"
            profiles[f"evidence-{slug}-{dimension_slug}-primary"] = (
                claim_id,
                primary_source,
                "supports",
                "indirect" if dimension == "selection_significance" else "direct",
            )
        profiles[f"evidence-{slug}-identity-secondary"] = (
            f"claim-{slug}-identity", secondary_source, "contextualizes", "background"
        )
    return profiles


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


def _validate_candidate_content_digest(package: dict[str, Any]) -> None:
    reviewed_content = {
        key: value
        for key, value in package.items()
        if key != "candidate_content_digest_sha256"
    }
    reviewed_content["audit"] = {
        key: value
        for key, value in package["audit"].items()
        if key not in {"canonical_review_status", "current_decision", "prior_reviews"}
    }
    canonical = json.dumps(
        reviewed_content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    actual = hashlib.sha256(canonical).hexdigest()
    if package["candidate_content_digest_sha256"] != EXPECTED_CANDIDATE_CONTENT_DIGEST:
        raise MajorLifePackageError("candidate reviewed-content digest identity drifted")
    if actual != EXPECTED_CANDIDATE_CONTENT_DIGEST:
        raise MajorLifePackageError("candidate reviewed semantic content drifted")


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
    if set(sources) != EXPECTED_SOURCE_IDS:
        raise MajorLifePackageError("the reviewed Source identity set drifted")
    expected_evidence_profiles = _expected_evidence_profiles()
    if set(evidence) != set(expected_evidence_profiles):
        raise MajorLifePackageError("the reviewed EvidenceLink identity set drifted")
    if set(uncertainties) != set(EXPECTED_UNCERTAINTY_PROFILES):
        raise MajorLifePackageError("the reviewed Uncertainty identity set drifted")

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
        if not presence["temporal"]["start_inclusive"] or not presence["temporal"]["end_inclusive"]:
            raise MajorLifePackageError(f"Presence {presence_id} temporal bounds must remain inclusive")
        expected_semantics = EXPECTED_PRESENCE_SEMANTICS[presence_id]
        actual_semantics = (
            presence["temporal"]["extent_semantics"],
            presence["spatial_precision"],
            tuple(presence["uncertainty_refs"]),
        )
        if actual_semantics != expected_semantics:
            raise MajorLifePackageError(f"Presence {presence_id} reviewed semantic profile drifted")
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
    try:
        _validate_frozen_git_revision(
            external["frozen_commit"],
            external["frozen_tree"],
            external["reviewed_content_digest"],
        )
    except ProjectStateError as exc:
        raise MajorLifePackageError(f"frozen Romagna Git evidence is invalid: {exc}") from exc
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
    frozen_segments = tuple(
        (
            segment["segment_id"],
            segment["segment_kind"],
            segment["place_ref"],
            segment["spatial_mode"],
            segment["geometry"],
            tuple(segment["source_refs"]),
        )
        for segment in trajectory_rows[0]["segments"]
    )
    if frozen_segments != EXPECTED_ROMAGNA_SEGMENTS:
        raise MajorLifePackageError("frozen Romagna segment and gap semantics drifted")
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
        if claim["review_state"] != "reviewed" or claim["evidence_state"] != "supported":
            raise MajorLifePackageError(f"Claim {claim_id} must use canonical reviewed/supported states")
        expected_uncertainties = _expected_claim_uncertainties(claim_id)
        if tuple(claim["uncertainty_refs"]) != expected_uncertainties:
            raise MajorLifePackageError(f"Claim {claim_id} reviewed Uncertainty ownership drifted")
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
        actual_profile = (
            link["claim_id"],
            link["source_id"],
            link["relation_to_claim"],
            link["evidence_strength"],
        )
        if actual_profile != expected_evidence_profiles[evidence_id]:
            raise MajorLifePackageError(f"EvidenceLink {evidence_id} reviewed binding drifted")
        if link["review_state"] != "reviewed":
            raise MajorLifePackageError(f"EvidenceLink {evidence_id} must remain reviewed")
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
        if bounds is not None:
            if not bounds["start_inclusive"] or not bounds["end_inclusive"]:
                raise MajorLifePackageError(f"Uncertainty {uncertainty_id} bounds must remain inclusive")
            lower = _temporal_key(bounds["not_before"])
            upper = _temporal_key(bounds["not_after"], upper=True)
            if lower > upper:
                raise MajorLifePackageError(f"Uncertainty {uncertainty_id} has inverted bounds")
            presence_targets = [ref for ref in uncertainty["target_refs"] if ref in presences]
            if len(presence_targets) != 1:
                raise MajorLifePackageError(
                    f"bounded Uncertainty {uncertainty_id} must target exactly one Presence"
                )
            target_temporal = presences[presence_targets[0]]["temporal"]
            if lower < _temporal_key(target_temporal["start"]):
                raise MajorLifePackageError(f"Uncertainty {uncertainty_id} starts outside its target")
            if upper > _temporal_key(target_temporal["end"], upper=True):
                raise MajorLifePackageError(f"Uncertainty {uncertainty_id} ends outside its target")
        expected_profile = EXPECTED_UNCERTAINTY_PROFILES[uncertainty_id]
        actual_profile = (
            tuple(uncertainty["target_refs"]),
            uncertainty["dimension"],
            tuple(uncertainty["basis_claim_refs"]),
            uncertainty["evidence_condition"],
            uncertainty["projection_effect"],
            bounds,
        )
        if actual_profile != expected_profile:
            raise MajorLifePackageError(f"Uncertainty {uncertainty_id} reviewed profile drifted")
        if uncertainty["review_state"] != "reviewed":
            raise MajorLifePackageError(f"Uncertainty {uncertainty_id} must remain reviewed")

    if set(package["relation_policy"]["prohibited_predicates"]) != EXPECTED_PROHIBITED_RELATIONS:
        raise MajorLifePackageError("deferred #331 Relation boundary drifted")
    if package["relation_policy"]["stored_relations"]:
        raise MajorLifePackageError("candidate package cannot store Relations while #331 is deferred")

    _validate_candidate_content_digest(package)

    audit = package["audit"]
    if audit["curation_cost"]["duration_minutes"] is not None:
        raise MajorLifePackageError("historical Drive work cannot receive a retrospective estimate")
    reviews = audit["prior_reviews"]
    prefix_canonical = json.dumps(
        reviews[:5], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    if hashlib.sha256(prefix_canonical).hexdigest() != EXPECTED_REVIEW_PREFIX_DIGEST:
        raise MajorLifePackageError("immutable rounds 1 through 3 review prefix drifted")

    suffix = reviews[5:]
    rounds: dict[int, list[dict[str, Any]]] = {}
    for row in suffix:
        rounds.setdefault(row["round"], []).append(row)
        if row["decision"] == "FREEZE_FOR_REVIEW" and (
            row["unresolved_major"] != 0 or row["unresolved_medium"] != 0
        ):
            raise MajorLifePackageError("FREEZE_FOR_REVIEW cannot retain unresolved findings")
        if row["decision"] == "NARROW" and (
            row["unresolved_major"] == 0 and row["unresolved_medium"] == 0
        ):
            raise MajorLifePackageError("NARROW review must identify an unresolved finding")
    if sorted(rounds) != list(range(4, 4 + len(rounds))):
        raise MajorLifePackageError("review rounds must append contiguously from round 4")
    for round_number, rows in rounds.items():
        if [row["track"] for row in rows] != ["semantic_content", "validator_integrity"]:
            raise MajorLifePackageError(
                f"review round {round_number} must append semantic and validator tracks in order"
            )
        if len({row["reviewed_head"] for row in rows}) != 1:
            raise MajorLifePackageError(f"review round {round_number} tracks must inspect one SHA")
        if len({row["github_comment_id"] for row in rows}) != 1:
            raise MajorLifePackageError(f"review round {round_number} tracks must share one record")

    decision = audit["current_decision"]
    status = audit["canonical_review_status"]
    if decision is None:
        if status != "pending_independent_rereview":
            raise MajorLifePackageError("pending review requires pending lifecycle status")
    else:
        if status != "independent_review_complete" or not rounds:
            raise MajorLifePackageError("a package decision requires a completed appended review")
        latest = rounds[max(rounds)]
        latest_decisions = [row["decision"] for row in latest]
        if decision == "FREEZE_FOR_REVIEW" and latest_decisions != [
            "FREEZE_FOR_REVIEW", "FREEZE_FOR_REVIEW"
        ]:
            raise MajorLifePackageError("FREEZE_FOR_REVIEW requires two positive latest tracks")
        if decision in {"NARROW", "STOP"} and decision not in latest_decisions:
            raise MajorLifePackageError("package decision must be supported by the latest review")

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
        "current_decision": audit["current_decision"],
        "prior_review_decisions": [row["decision"] for row in audit["prior_reviews"]],
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
