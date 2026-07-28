#!/usr/bin/env python3
"""Validate and render the Gate A research-module package."""

from __future__ import annotations

import argparse
import json
import math
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "docs" / "work" / "validation_modules"
MODULE_IDS = ("A", "B", "C")
ALLOWED_PREDICATES = {
    "adapted_from",
    "contains",
    "derived_from",
    "influenced",
    "influenced_by",
    "inspired_by",
    "modelled_on",
    "part_of",
    "reconstructed_from",
}
ALLOWED_CLAIM_KINDS = {"factual", "interpretation", "hypothesis", "counterfactual"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unknown"}
ALLOWED_EVIDENCE_STATES = {"supported", "mixed", "challenged", "missing", "not_applicable"}
ALLOWED_EVIDENCE_RELATIONS = {"supports", "challenges", "contextualizes"}
ALLOWED_EVIDENCE_STRENGTH = {"direct", "indirect", "background"}
ALLOWED_REVIEW_STATES = {"draft", "reviewed", "contested", "rejected", "superseded"}


class ModuleValidationError(ValueError):
    """Raised when a Gate A artifact violates its executable contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ModuleValidationError(message)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ModuleValidationError(f"missing artifact: {path.relative_to(REPO_ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ModuleValidationError(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}") from exc


def _parse_timestamp(value: object, context: str) -> datetime:
    _require(isinstance(value, str) and value.endswith("Z"), f"{context} must be a UTC ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ModuleValidationError(f"{context} must be a valid UTC ISO timestamp") from exc
    _require(parsed.utcoffset() is not None, f"{context} must include a timezone")
    return parsed


def _is_uuid_v4(value: object) -> bool:
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return False
    return parsed.version == 4 and parsed.variant == uuid.RFC_4122


def _canonical_feature_ids(root: Path) -> set[str]:
    payload = _read_json(root / "data" / "features.json")
    _require(isinstance(payload, list), "data/features.json must be an array")
    result: set[str] = set()
    for record in payload:
        fields = record.get("fields") if isinstance(record, dict) else None
        feature_id = fields.get("id") if isinstance(fields, dict) else None
        if isinstance(feature_id, str):
            result.add(feature_id)
    return result


def _load_module(root: Path, module_id: str) -> dict[str, Any]:
    path = root / "docs" / "work" / "validation_modules" / "modules" / f"module_{module_id.lower()}.json"
    payload = _read_json(path)
    _require(isinstance(payload, dict), f"module {module_id} must be an object")
    return payload


def _indexed(items: object, key: str, context: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(items, list), f"{context} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        _require(isinstance(item, dict), f"{context} contains a non-object")
        item_id = item.get(key)
        _require(isinstance(item_id, str) and item_id, f"{context} item is missing {key}")
        _require(item_id not in result, f"{context} contains duplicate {key} {item_id}")
        result[item_id] = item
    return result


def _validate_module(
    module: dict[str, Any],
    canonical_feature_ids: set[str],
    *,
    require_ready: bool,
) -> dict[str, int]:
    module_id = module.get("module_id")
    prefix = f"module {module_id}"
    _require(module_id in MODULE_IDS, f"unknown module_id {module_id!r}")
    _require(module.get("schema_version") == 1, f"{prefix} must use schema_version 1")
    _require(module.get("status") in {"REVIEW_REQUIRED", "READY"}, f"{prefix} has invalid status")
    _require(isinstance(module.get("question"), str) and module["question"].strip(), f"{prefix} needs a question")
    _require(
        isinstance(module.get("selection_rationale"), str) and module["selection_rationale"].strip(),
        f"{prefix} needs selection rationale",
    )

    lenses = module.get("lenses")
    _require(isinstance(lenses, list) and 4 <= len(lenses) <= 6, f"{prefix} must have 4-6 lenses")
    _require(len(set(lenses)) == len(lenses), f"{prefix} lenses must be unique")

    features = _indexed(module.get("features"), "feature_id", f"{prefix} features")
    _require(4 <= len(features) <= 6, f"{prefix} must have 4-6 Features")
    for feature_id, feature in features.items():
        status = feature.get("corpus_status")
        _require(status in {"published", "module_candidate"}, f"{prefix} Feature {feature_id} has invalid corpus_status")
        if status == "published":
            _require(feature_id in canonical_feature_ids, f"{prefix} published Feature {feature_id} is absent from corpus")
        else:
            _require(_is_uuid_v4(feature_id), f"{prefix} candidate Feature {feature_id} must use UUID v4")
        _require(
            isinstance(feature.get("selection_rationale"), str) and feature["selection_rationale"].strip(),
            f"{prefix} Feature {feature_id} needs selection rationale",
        )

    saved_view = module.get("saved_view")
    _require(isinstance(saved_view, dict), f"{prefix} needs Saved View")
    _require(_is_uuid_v4(saved_view.get("id")), f"{prefix} Saved View id must use UUID v4")
    _require(saved_view.get("feature_ids") == list(features), f"{prefix} Saved View Feature order drift")
    _require(saved_view.get("lenses") == lenses, f"{prefix} Saved View lens drift")

    revision = module.get("reference_revision")
    _require(isinstance(revision, dict), f"{prefix} needs reference revision")
    _require(_is_uuid_v4(revision.get("id")), f"{prefix} revision id must use UUID v4")
    _require(_is_uuid_v4(revision.get("investigation_id")), f"{prefix} Investigation id must use UUID v4")
    _require(revision.get("revision_number") == 1, f"{prefix} reference revision_number must be 1")
    _require(revision.get("visibility") == "withheld_from_participants", f"{prefix} reference must be hidden")
    _require(revision.get("saved_view_id") == saved_view.get("id"), f"{prefix} revision Saved View drift")
    dataset = revision.get("dataset_identity")
    _require(
        isinstance(dataset, dict)
        and dataset.get("kind") == "git_commit"
        and isinstance(dataset.get("value"), str)
        and len(dataset["value"]) == 40,
        f"{prefix} needs a commit-pinned dataset identity",
    )

    sources = _indexed(module.get("sources"), "source_id", f"{prefix} sources")
    for source_id, source in sources.items():
        _require(
            isinstance(source.get("title"), str) and source["title"].strip(),
            f"{prefix} Source {source_id} needs a title",
        )
        _require(
            isinstance(source.get("publisher"), str) and source["publisher"].strip(),
            f"{prefix} Source {source_id} needs a publisher",
        )
        _require(
            isinstance(source.get("url"), str) and source["url"].startswith("https://"),
            f"{prefix} Source {source_id} needs an HTTPS URL",
        )

    claims = _indexed(module.get("claims"), "claim_id", f"{prefix} claims")
    _require(6 <= len(claims) <= 10, f"{prefix} must have 6-10 atomic Claims")
    relation_claims = 0
    medium_or_challenged = False
    for claim_id, claim in claims.items():
        _require(
            isinstance(claim.get("statement"), str) and claim["statement"].strip(),
            f"{prefix} Claim {claim_id} needs a statement",
        )
        _require(claim.get("claim_kind") in ALLOWED_CLAIM_KINDS, f"{prefix} Claim {claim_id} has invalid kind")
        _require(claim.get("origin") == "curator", f"{prefix} Claim {claim_id} must preserve curator origin")
        _require(
            claim.get("preparation_state") == "curator_checked",
            f"{prefix} Claim {claim_id} must preserve its curator preparation check separately",
        )
        _require(claim.get("review_state") in ALLOWED_REVIEW_STATES, f"{prefix} Claim {claim_id} has invalid review state")
        _require(claim.get("confidence") in ALLOWED_CONFIDENCE, f"{prefix} Claim {claim_id} has invalid confidence")
        _require(
            claim.get("evidence_state") in ALLOWED_EVIDENCE_STATES,
            f"{prefix} Claim {claim_id} has invalid evidence state",
        )
        _require(
            isinstance(claim.get("uncertainty"), str) and claim["uncertainty"].strip(),
            f"{prefix} Claim {claim_id} needs explicit uncertainty",
        )
        medium_or_challenged = medium_or_challenged or claim.get("confidence") in {"medium", "low"}
        relation = claim.get("relation")
        if relation is not None:
            _require(isinstance(relation, dict), f"{prefix} Claim {claim_id} relation must be an object")
            predicate = relation.get("predicate")
            _require(predicate in ALLOWED_PREDICATES, f"{prefix} Claim {claim_id} has invalid predicate")
            _require(predicate != "same_movement", f"{prefix} Claim {claim_id} cannot use same_movement")
            _require(
                relation.get("subject_feature_id") in features and relation.get("object_feature_id") in features,
                f"{prefix} Claim {claim_id} relation endpoints must be selected Features",
            )
            _require(
                relation.get("subject_feature_id") != relation.get("object_feature_id"),
                f"{prefix} Claim {claim_id} relation cannot be self-referential",
            )
            _require(
                isinstance(relation.get("qualifier"), str) and relation["qualifier"].strip(),
                f"{prefix} Claim {claim_id} relation needs a qualifier",
            )
            relation_claims += 1
        classification = claim.get("classification_assertion")
        if classification is not None:
            _require(
                isinstance(classification, dict),
                f"{prefix} Claim {claim_id} classification assertion must be an object",
            )
            _require(
                classification.get("feature_id") in features,
                f"{prefix} Claim {claim_id} classification Feature must be selected",
            )
            _require(
                isinstance(classification.get("classification"), str)
                and classification["classification"].strip(),
                f"{prefix} Claim {claim_id} classification must be explicit",
            )
            _require(
                isinstance(classification.get("qualifier"), str) and classification["qualifier"].strip(),
                f"{prefix} Claim {claim_id} classification needs a qualifier",
            )
    _require(relation_claims >= 2, f"{prefix} needs at least two substantive RelationClaims")

    evidence = _indexed(module.get("evidence_links"), "evidence_link_id", f"{prefix} EvidenceLinks")
    _require(len(evidence) >= 8, f"{prefix} needs at least eight EvidenceLinks")
    linked_claims: set[str] = set()
    for evidence_id, link in evidence.items():
        claim_id = link.get("claim_id")
        source_id = link.get("source_id")
        _require(claim_id in claims, f"{prefix} EvidenceLink {evidence_id} has missing Claim")
        _require(source_id in sources, f"{prefix} EvidenceLink {evidence_id} has missing Source")
        _require(
            isinstance(link.get("locator"), str) and len(link["locator"].strip()) >= 12,
            f"{prefix} EvidenceLink {evidence_id} needs a reproducible locator",
        )
        _require(
            link.get("relation_to_claim") in ALLOWED_EVIDENCE_RELATIONS,
            f"{prefix} EvidenceLink {evidence_id} has invalid relation_to_claim",
        )
        _require(
            link.get("evidence_strength") in ALLOWED_EVIDENCE_STRENGTH,
            f"{prefix} EvidenceLink {evidence_id} has invalid evidence strength",
        )
        _require(
            link.get("preparation_state") == "curator_checked",
            f"{prefix} EvidenceLink {evidence_id} must preserve its curator preparation check separately",
        )
        _require(
            link.get("review_state") in ALLOWED_REVIEW_STATES,
            f"{prefix} EvidenceLink {evidence_id} has invalid review state",
        )
        _require(
            isinstance(link.get("evidence_summary"), str) and link["evidence_summary"].strip(),
            f"{prefix} EvidenceLink {evidence_id} needs a summary",
        )
        medium_or_challenged = medium_or_challenged or link.get("relation_to_claim") == "challenges"
        linked_claims.add(claim_id)
    _require(linked_claims == set(claims), f"{prefix} every Claim must have at least one EvidenceLink")
    _require(medium_or_challenged, f"{prefix} needs a medium-confidence or challenging case")

    findings = module.get("findings")
    _require(isinstance(findings, list) and findings, f"{prefix} needs findings")
    _require(all(claim_id in claims for claim_id in findings), f"{prefix} findings must reference Claims")
    conclusion = module.get("conclusion")
    _require(isinstance(conclusion, dict), f"{prefix} needs a conclusion")
    _require(conclusion.get("status") in {"provisional", "unresolved"}, f"{prefix} conclusion status is invalid")
    _require(
        isinstance(conclusion.get("statement"), str) and conclusion["statement"].strip(),
        f"{prefix} conclusion needs a statement",
    )
    _require(
        isinstance(module.get("module_uncertainty"), list) and module["module_uncertainty"],
        f"{prefix} needs module-level uncertainty",
    )

    cost = module.get("cost")
    _require(isinstance(cost, dict), f"{prefix} needs cost tracking")
    _require(cost.get("currency") == "minutes", f"{prefix} cost unit must be minutes")
    if require_ready:
        _require(module.get("status") == "READY", f"{prefix} is not READY")
        _require(
            isinstance(cost.get("curation_elapsed"), int) and cost["curation_elapsed"] > 0,
            f"{prefix} READY status requires measured curation cost",
        )
        _require(
            all(claim.get("review_state") == "reviewed" for claim in claims.values()),
            f"{prefix} READY Claims must be reviewed",
        )
        _require(
            all(link.get("review_state") == "reviewed" for link in evidence.values()),
            f"{prefix} READY EvidenceLinks must be reviewed",
        )

    return {
        "features": len(features),
        "lenses": len(lenses),
        "claims": len(claims),
        "evidence_links": len(evidence),
        "relations": relation_claims,
    }


def _validate_reviews(root: Path, modules: dict[str, dict[str, Any]], *, require_ready: bool) -> None:
    registry_path = root / "docs" / "work" / "validation_modules" / "review_registry.json"
    registry = _read_json(registry_path)
    _require(isinstance(registry, dict) and registry.get("schema_version") == 1, "review registry must use schema 1")
    _require(registry.get("required_reviewers_per_module") == 2, "review registry must require exactly two reviewers")
    sessions = registry.get("review_sessions", {})
    _require(isinstance(sessions, dict), "review sessions must be an object")
    for session_id, session in sessions.items():
        _require(isinstance(session, dict), f"review session {session_id} must be an object")
        _require(
            isinstance(session.get("reviewer_id"), str) and session["reviewer_id"],
            f"review session {session_id} needs a reviewer",
        )
        _require(
            isinstance(session.get("independence_basis"), str) and session["independence_basis"].strip(),
            f"review session {session_id} needs an independence basis",
        )
        started_at = _parse_timestamp(session.get("started_at"), f"review session {session_id} start")
        ended_at = _parse_timestamp(session.get("ended_at"), f"review session {session_id} end")
        elapsed_seconds = int((ended_at - started_at).total_seconds())
        _require(elapsed_seconds > 0, f"review session {session_id} end must follow its start")
        _require(
            session.get("elapsed_seconds") == elapsed_seconds,
            f"review session {session_id} elapsed seconds do not match its timestamps",
        )
        _require(
            session.get("elapsed_minutes") == math.ceil(elapsed_seconds / 60),
            f"review session {session_id} minutes must be rounded up from elapsed seconds",
        )
        _require(
            isinstance(session.get("frozen_tree"), str) and len(session["frozen_tree"]) == 40,
            f"review session {session_id} needs a frozen Git tree",
        )
        _require(
            session.get("scope_modules") == list(MODULE_IDS),
            f"review session {session_id} must cover modules A, B and C",
        )
    entries = registry.get("modules")
    _require(isinstance(entries, dict) and set(entries) == set(MODULE_IDS), "review registry must cover A, B and C")
    for module_id in MODULE_IDS:
        entry = entries[module_id]
        _require(isinstance(entry, dict), f"review registry module {module_id} must be an object")
        reviews = entry.get("reviews")
        _require(isinstance(reviews, list), f"review registry module {module_id} reviews must be an array")
        reviewer_ids = [review.get("reviewer_id") for review in reviews if isinstance(review, dict)]
        _require(len(reviewer_ids) == len(set(reviewer_ids)), f"module {module_id} reviewers must be independent")
        for review in reviews:
            _require(isinstance(review, dict), f"module {module_id} review must be an object")
            session_id = review.get("session_id")
            _require(session_id in sessions, f"module {module_id} review has no measured session")
            session = sessions[session_id]
            _require(
                review.get("reviewer_id") == session.get("reviewer_id"),
                f"module {module_id} review identity does not match its session",
            )
            artifact = root / str(review.get("artifact"))
            _require(artifact.is_file(), f"module {module_id} review artifact is missing")
            artifact_text = artifact.read_text(encoding="utf-8")
            _require(
                f"Module {module_id}" in artifact_text
                and str(review.get("reviewer_id")) in artifact_text
                and str(session.get("frozen_tree")) in artifact_text
                and str(session.get("started_at")) in artifact_text
                and str(session.get("ended_at")) in artifact_text
                and f"`{review.get('decision')}`" in artifact_text,
                f"module {module_id} review artifact does not preserve its decision evidence",
            )
        expected_status = "READY" if len(reviews) == 2 and all(
            isinstance(review, dict) and review.get("decision") == "READY" for review in reviews
        ) else "REVIEW_REQUIRED"
        _require(entry.get("status") == expected_status, f"module {module_id} review status drift")
        _require(modules[module_id].get("status") == expected_status, f"module {module_id} artifact status drift")
        if require_ready:
            _require(len(reviews) == 2, f"module {module_id} needs exactly two independent reviews")
            for review in reviews:
                _require(review.get("decision") == "READY", f"module {module_id} has a non-READY review")


def _validate_recuration_checklists(
    root: Path,
    modules: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    path = root / "docs" / "work" / "validation_modules" / "recuration_checklists.json"
    payload = _read_json(path)
    _require(
        isinstance(payload, dict) and payload.get("schema_version") == 1,
        "re-curation checklists must use schema 1",
    )
    _require(
        isinstance(payload.get("method"), str) and payload["method"].strip(),
        "re-curation checklists need an audit method",
    )
    checklists = payload.get("modules")
    _require(
        isinstance(checklists, dict) and set(checklists) == set(MODULE_IDS),
        "re-curation checklists must cover modules A, B and C",
    )

    for module_id in MODULE_IDS:
        module = modules[module_id]
        checklist = checklists[module_id]
        _require(isinstance(checklist, dict), f"module {module_id} re-curation checklist must be an object")

        started_at = _parse_timestamp(checklist.get("started_at"), f"module {module_id} re-curation start")
        ended_at = _parse_timestamp(checklist.get("ended_at"), f"module {module_id} re-curation end")
        elapsed_seconds = int((ended_at - started_at).total_seconds())
        _require(elapsed_seconds > 0, f"module {module_id} re-curation end must follow its start")
        _require(
            checklist.get("elapsed_seconds") == elapsed_seconds,
            f"module {module_id} re-curation elapsed seconds do not match its timestamps",
        )
        _require(
            checklist.get("elapsed_minutes") == math.ceil(elapsed_seconds / 60),
            f"module {module_id} re-curation minutes must be rounded up from elapsed seconds",
        )

        expected_claim_ids = [claim["claim_id"] for claim in module["claims"]]
        expected_evidence_ids = [link["evidence_link_id"] for link in module["evidence_links"]]
        expected_relation_ids = [
            claim["claim_id"] for claim in module["claims"] if isinstance(claim.get("relation"), dict)
        ]
        expected_source_ids = [source["source_id"] for source in module["sources"]]
        _require(
            checklist.get("claim_ids") == expected_claim_ids,
            f"module {module_id} re-curation Claim coverage drift",
        )
        _require(
            checklist.get("evidence_link_ids") == expected_evidence_ids,
            f"module {module_id} re-curation EvidenceLink coverage drift",
        )
        _require(
            checklist.get("relation_claim_ids") == expected_relation_ids,
            f"module {module_id} re-curation Relation coverage drift",
        )
        _require(
            checklist.get("source_ids") == expected_source_ids,
            f"module {module_id} re-curation Source coverage drift",
        )

        source_coverage = checklist.get("source_locator_coverage")
        _require(
            isinstance(source_coverage, dict) and list(source_coverage) == expected_source_ids,
            f"module {module_id} re-curation source-locator coverage drift",
        )
        covered_evidence_ids: list[str] = []
        source_by_evidence = {
            link["evidence_link_id"]: link["source_id"] for link in module["evidence_links"]
        }
        for source_id, evidence_ids in source_coverage.items():
            _require(
                isinstance(evidence_ids, list) and evidence_ids,
                f"module {module_id} Source {source_id} needs checked locator IDs",
            )
            for evidence_id in evidence_ids:
                _require(
                    source_by_evidence.get(evidence_id) == source_id,
                    f"module {module_id} locator coverage maps {evidence_id} to the wrong Source",
                )
            covered_evidence_ids.extend(evidence_ids)
        _require(
            sorted(covered_evidence_ids) == sorted(expected_evidence_ids)
            and len(covered_evidence_ids) == len(set(covered_evidence_ids)),
            f"module {module_id} re-curation must cover every EvidenceLink locator exactly once",
        )

        expected_brief = f"docs/work/validation_modules/briefs/module_{module_id.lower()}_reference_brief.md"
        _require(
            checklist.get("brief_path") == expected_brief and checklist.get("brief_checked") is True,
            f"module {module_id} re-curation must check its deterministic Brief",
        )
        _require(checklist.get("result") == "PASS", f"module {module_id} re-curation did not pass")

    return checklists


def _validate_preparation_log(
    root: Path,
    modules: dict[str, dict[str, Any]],
    checklists: dict[str, dict[str, Any]],
    *,
    require_ready: bool,
) -> None:
    path = root / "docs" / "work" / "validation_modules" / "preparation_log.json"
    payload = _read_json(path)
    _require(isinstance(payload, dict) and payload.get("schema_version") == 1, "preparation log must use schema 1")
    _require(payload.get("measurement_status") in {"PARTIAL", "COMPLETE"}, "preparation log status is invalid")
    session = payload.get("timed_session")
    _require(isinstance(session, dict), "preparation log needs a timed session")
    _require(
        isinstance(session.get("elapsed_minutes"), int) and session["elapsed_minutes"] > 0,
        "preparation log needs positive measured minutes",
    )
    allocations = payload.get("per_module_curation_minutes")
    _require(
        isinstance(allocations, dict) and set(allocations) == set(MODULE_IDS),
        "preparation log must cover modules A, B and C",
    )
    full_sessions = payload.get("full_recuration_sessions")
    _require(
        isinstance(full_sessions, dict) and set(full_sessions) == set(MODULE_IDS),
        "preparation log must preserve a full re-curation session for modules A, B and C",
    )
    for module_id in MODULE_IDS:
        full_session = full_sessions[module_id]
        checklist = checklists[module_id]
        _require(isinstance(full_session, dict), f"module {module_id} full re-curation session must be an object")
        _require(
            full_session.get("started_at") == checklist["started_at"]
            and full_session.get("ended_at") == checklist["ended_at"]
            and full_session.get("elapsed_seconds") == checklist["elapsed_seconds"]
            and full_session.get("elapsed_minutes") == checklist["elapsed_minutes"],
            f"module {module_id} preparation session must match its executable re-curation checklist",
        )
        _require(
            allocations[module_id] == checklist["elapsed_minutes"]
            and modules[module_id].get("cost", {}).get("curation_elapsed") == checklist["elapsed_minutes"],
            f"module {module_id} curation cost must match its measured re-curation checklist",
        )
        _require(
            full_session.get("checklist_path")
            == "docs/work/validation_modules/recuration_checklists.json",
            f"module {module_id} full re-curation session must link its checklist",
        )
        scope = full_session.get("scope")
        _require(
            isinstance(scope, str)
            and all(term in scope for term in ("Claim", "EvidenceLink", "Relation", "Source", "Brief")),
            f"module {module_id} full re-curation scope must cover the complete research artifact",
        )
    if require_ready:
        _require(payload.get("measurement_status") == "COMPLETE", "READY requires complete preparation cost")
        _require(
            all(isinstance(value, int) and value > 0 for value in allocations.values()),
            "READY requires positive per-module preparation cost",
        )


def render_brief(module: dict[str, Any]) -> str:
    features = {item["feature_id"]: item for item in module["features"]}
    sources = {item["source_id"]: item for item in module["sources"]}
    evidence_by_claim: dict[str, list[dict[str, Any]]] = {}
    for link in module["evidence_links"]:
        evidence_by_claim.setdefault(link["claim_id"], []).append(link)

    lines = [
        f"# Reference Research Brief — Module {module['module_id']}",
        "",
        "> Hidden calibration artifact. Do not disclose to validation participants before blind scoring.",
        "",
        f"Status: `{module['status']}`",
        "",
        "## Question",
        "",
        module["question"],
        "",
        "## Compared Features",
        "",
    ]
    for feature in module["features"]:
        lines.append(f"- **{feature['name']}** — {feature['selection_rationale']}")
    lines.extend(["", "## Lenses", ""])
    lines.extend(f"- {lens}" for lens in module["lenses"])
    lines.extend(["", "## Claims and evidence", ""])
    for claim in module["claims"]:
        relation = claim.get("relation")
        relation_label = ""
        if relation:
            relation_label = (
                f" Relation: `{features[relation['subject_feature_id']]['name']} "
                f"→ {relation['predicate']} → {features[relation['object_feature_id']]['name']}`; "
                f"qualifier: {relation['qualifier']}."
            )
        lines.append(
            f"### {claim['claim_id']} · {claim['claim_kind']} · origin {claim['origin']} · "
            f"review {claim['review_state']} · {claim['confidence']} confidence · {claim['evidence_state']}"
        )
        lines.append("")
        lines.append(f"{claim['statement']}{relation_label}")
        lines.append("")
        lines.append(f"Uncertainty: {claim['uncertainty']}")
        lines.append("")
        for link in evidence_by_claim[claim["claim_id"]]:
            source = sources[link["source_id"]]
            citation_parts = [
                str(source[key])
                for key in ("author", "citation")
                if isinstance(source.get(key), str) and source[key].strip()
            ]
            if isinstance(source.get("publication_year"), int) and not source.get("citation"):
                citation_parts.append(str(source["publication_year"]))
            citation = f" ({'; '.join(citation_parts)})" if citation_parts else ""
            lines.append(
                f"- [{source['title']}]({source['url']}){citation} — {link['relation_to_claim']}; "
                f"{link['evidence_strength']}; review {link['review_state']}; "
                f"locator: {link['locator']}. {link['evidence_summary']}"
            )
        lines.append("")
    lines.extend(["## Findings", ""])
    claim_by_id = {claim["claim_id"]: claim for claim in module["claims"]}
    for claim_id in module["findings"]:
        lines.append(f"- **{claim_id}:** {claim_by_id[claim_id]['statement']}")
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            f"Status: `{module['conclusion']['status']}`",
            "",
            module["conclusion"]["statement"],
            "",
            "## Uncertainty",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in module["module_uncertainty"])
    revision = module["reference_revision"]
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            f"- Investigation: `{revision['investigation_id']}`",
            f"- Slice Revision: `{revision['id']}` / revision `{revision['revision_number']}`",
            f"- Saved View: `{module['saved_view']['id']}`",
            f"- Dataset commit: `{revision['dataset_identity']['value']}`",
            f"- Schema: `{revision['schema_version']}`",
            f"- Content version: `{revision['content_version']}`",
            "",
        ]
    )
    return "\n".join(lines)


def validate_package(
    root: Path = REPO_ROOT,
    *,
    require_ready: bool = False,
    check_briefs: bool = True,
) -> dict[str, dict[str, int]]:
    canonical_feature_ids = _canonical_feature_ids(root)
    modules = {module_id: _load_module(root, module_id) for module_id in MODULE_IDS}
    counts = {
        module_id: _validate_module(module, canonical_feature_ids, require_ready=require_ready)
        for module_id, module in modules.items()
    }
    _validate_reviews(root, modules, require_ready=require_ready)
    checklists = _validate_recuration_checklists(root, modules)
    _validate_preparation_log(root, modules, checklists, require_ready=require_ready)
    if check_briefs:
        briefs_root = root / "docs" / "work" / "validation_modules" / "briefs"
        for module_id, module in modules.items():
            brief_path = briefs_root / f"module_{module_id.lower()}_reference_brief.md"
            _require(brief_path.is_file(), f"module {module_id} reference Brief is missing")
            _require(
                brief_path.read_text(encoding="utf-8") == render_brief(module),
                f"module {module_id} reference Brief drift; run scripts/validation_modules.py --write-briefs",
            )
    return counts


def write_briefs(root: Path = REPO_ROOT) -> None:
    briefs_root = root / "docs" / "work" / "validation_modules" / "briefs"
    briefs_root.mkdir(parents=True, exist_ok=True)
    for module_id in MODULE_IDS:
        module = _load_module(root, module_id)
        (briefs_root / f"module_{module_id.lower()}_reference_brief.md").write_text(
            render_brief(module),
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true", help="Require two READY reviews per module")
    parser.add_argument("--write-briefs", action="store_true", help="Regenerate checked-in reference Briefs")
    args = parser.parse_args()
    if args.write_briefs:
        write_briefs()
    try:
        counts = validate_package(require_ready=args.require_ready)
    except ModuleValidationError as exc:
        print(f"[FAIL] Gate A research modules: {exc}")
        return 1
    for module_id, module_counts in counts.items():
        rendered = ", ".join(f"{key}={value}" for key, value in module_counts.items())
        print(f"[PASS] Module {module_id}: {rendered}")
    mode = "READY" if args.require_ready else "STRUCTURAL"
    print(f"[PASS] Gate A research modules: mode={mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
