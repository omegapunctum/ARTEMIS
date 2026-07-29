#!/usr/bin/env python3
"""Validate ARTEMIS world-model contract fixtures without runtime migration."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_RELATIVE = Path("fixtures/world_model/v1")
SCHEMA_VERSION = "1.0.0"

COLLECTION_TYPES = {
    "entities": "Entity",
    "events": "Event",
    "states": "State",
    "processes": "Process",
    "trajectories": "Trajectory",
    "regions": "Region",
    "relations": "Relation",
    "derived_observations": "DerivedObservation",
    "claims": "Claim",
    "evidence_links": "EvidenceLink",
    "uncertainties": "Uncertainty",
    "synchronized_views": "SynchronizedView",
    "sources": "Source",
    "layers": "Layer",
}

ALLOWED_CLAIM_KINDS = {
    "factual",
    "observation",
    "inference",
    "interpretation",
    "hypothesis",
    "counterfactual",
}
ALLOWED_ORIGINS = {"curator", "user", "ai", "system", "imported"}
ALLOWED_REVIEW_STATES = {"draft", "reviewed", "contested", "rejected", "superseded"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unknown"}
ALLOWED_EVIDENCE_STATES = {"supported", "mixed", "challenged", "missing", "not_applicable"}
ALLOWED_EVIDENCE_RELATIONS = {"supports", "challenges", "contextualizes"}
ALLOWED_EVIDENCE_STRENGTH = {"direct", "indirect", "background"}
ALLOWED_RECONSTRUCTION_MODES = {
    "historical_assertion",
    "scholarly_reconstruction",
    "alternative_reconstruction",
    "analytical_model",
    "hypothesis",
    "counterfactual",
}
DERIVED_ONLY_PREDICATES = {
    "co_present",
    "temporal_overlap",
    "spatial_overlap",
    "before",
    "after",
    "route_intersection",
    "similarity",
}
REFERENCE_KEYS = {
    "claim_refs",
    "uncertainty_refs",
    "layer_refs",
    "participant_refs",
    "basis_claim_refs",
    "target_refs",
    "place_refs",
    "input_refs",
    "local_context_refs",
    "global_context_refs",
    "derived_observation_refs",
    "active_layer_refs",
    "included_layer_refs",
}
SINGLE_REFERENCE_KEYS = {
    "subject_ref",
    "object_ref",
    "place_ref",
    "region_ref",
    "claim_ref",
    "claim_id",
    "source_id",
    "subject_or_claim_ref",
}


class FixtureValidationError(ValueError):
    """Raised when a fixture violates the executable world-model contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureValidationError(message)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FixtureValidationError(f"missing artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(f"invalid JSON in {path}: {exc}") from exc


def _index(items: object, expected_type: str, context: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(items, list) and items, f"{context} must be a non-empty array")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        _require(isinstance(item, dict), f"{context} contains a non-object")
        item_id = item.get("id")
        _require(isinstance(item_id, str) and item_id, f"{context} item is missing id")
        _require(item_id not in indexed, f"{context} contains duplicate id {item_id}")
        _require(item.get("type") == expected_type, f"{item_id} must have type {expected_type}")
        indexed[item_id] = item
    return indexed


def _walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _validate_extent(
    extent: object,
    *,
    context: str,
    dimension: str,
    claim_ids: set[str],
    fixture_mode: str,
) -> None:
    _require(isinstance(extent, dict), f"{context} {dimension} extent must be an object")
    kind = extent.get("kind")
    precision = extent.get("precision")
    basis = extent.get("basis_claim_refs")
    _require(isinstance(kind, str) and kind, f"{context} {dimension} extent needs kind")
    _require(isinstance(precision, str) and precision, f"{context} {dimension} extent needs precision")
    _require(isinstance(basis, list), f"{context} {dimension} extent needs basis_claim_refs")
    _require(len(basis) == len(set(basis)), f"{context} {dimension} extent has duplicate basis Claims")
    for claim_id in basis:
        _require(claim_id in claim_ids, f"{context} {dimension} extent has orphan basis Claim {claim_id}")

    if precision != "unknown":
        _require(basis, f"{context} cannot assert {dimension} precision {precision} without a basis Claim")
    if precision == "fixture_defined":
        _require(
            fixture_mode == "synthetic_contract_fixture",
            f"{context} may use fixture_defined precision only in a synthetic contract fixture",
        )

    if dimension == "temporal":
        _require("certainty" in extent, f"{context} temporal extent needs certainty")
        if kind == "instant":
            _require(extent.get("start") == extent.get("end"), f"{context} instant must have equal start/end")
        if kind == "closed_interval":
            _require(extent.get("start") is not None and extent.get("end") is not None, f"{context} interval is open")
        alternatives = extent.get("alternatives", [])
        _require(isinstance(alternatives, list), f"{context} alternatives must be an array")
        for alternative in alternatives:
            _require(isinstance(alternative, dict), f"{context} temporal alternative must be an object")
            alt_basis = alternative.get("basis_claim_refs")
            _require(isinstance(alt_basis, list) and alt_basis, f"{context} temporal alternative needs basis Claims")
            for claim_id in alt_basis:
                _require(claim_id in claim_ids, f"{context} temporal alternative has orphan Claim {claim_id}")

    if dimension == "spatial":
        if kind in {"point", "path", "polygon", "multipolygon"}:
            geometry = extent.get("geometry")
            _require(isinstance(geometry, dict), f"{context} {kind} needs geometry")
            _require(isinstance(geometry.get("type"), str), f"{context} geometry needs GeoJSON type")
            _require(isinstance(geometry.get("coordinates"), list), f"{context} geometry needs coordinates")
        elif kind == "named_place":
            _require(isinstance(extent.get("place_ref"), str), f"{context} named_place needs place_ref")
        elif kind == "region_ref":
            _require(isinstance(extent.get("region_ref"), str), f"{context} region_ref needs region_ref")
        elif kind == "multiple_places":
            _require(
                isinstance(extent.get("place_refs"), list) and len(extent["place_refs"]) >= 2,
                f"{context} multiple_places needs at least two place refs",
            )
        elif kind == "unknown":
            _require(precision == "unknown", f"{context} unknown space must use unknown precision")
            _require("geometry" not in extent, f"{context} unknown space must not invent geometry")


def _validate_claims(
    claims: dict[str, dict[str, Any]],
    evidence_links: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    package_root: Path,
) -> None:
    links_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link_id, link in evidence_links.items():
        claim_id = link.get("claim_id")
        source_id = link.get("source_id")
        _require(claim_id in claims, f"{link_id} has orphan Claim {claim_id}")
        _require(source_id in sources, f"{link_id} has orphan Source {source_id}")
        _require(link.get("relation_to_claim") in ALLOWED_EVIDENCE_RELATIONS, f"{link_id} has invalid relation")
        _require(link.get("evidence_strength") in ALLOWED_EVIDENCE_STRENGTH, f"{link_id} has invalid strength")
        _require(link.get("review_state") in ALLOWED_REVIEW_STATES, f"{link_id} has invalid review state")
        locator = link.get("locator")
        _require(isinstance(locator, str) and locator, f"{link_id} needs a locator")
        source_path = package_root / str(sources[source_id].get("uri"))
        _require(source_path.is_file(), f"{link_id} source artifact is missing: {source_path}")
        _require(locator in source_path.read_text(encoding="utf-8"), f"{link_id} locator is not reproducible")
        links_by_claim[claim_id].append(link)

    for claim_id, claim in claims.items():
        _require(
            isinstance(claim.get("statement"), str) and claim["statement"].strip(),
            f"{claim_id} needs an atomic statement",
        )
        _require(claim.get("claim_kind") in ALLOWED_CLAIM_KINDS, f"{claim_id} has invalid claim kind")
        _require(claim.get("origin") in ALLOWED_ORIGINS, f"{claim_id} has invalid origin")
        _require(claim.get("review_state") in ALLOWED_REVIEW_STATES, f"{claim_id} has invalid review state")
        _require(claim.get("confidence") in ALLOWED_CONFIDENCE, f"{claim_id} has invalid confidence")
        state = claim.get("evidence_state")
        _require(state in ALLOWED_EVIDENCE_STATES, f"{claim_id} has invalid evidence state")
        links = links_by_claim.get(claim_id, [])
        reviewed = [link for link in links if link.get("review_state") == "reviewed"]
        relations = {link.get("relation_to_claim") for link in reviewed}
        if state == "supported":
            _require("supports" in relations, f"{claim_id} says supported without reviewed supporting evidence")
        elif state == "mixed":
            _require(
                {"supports", "challenges"}.issubset(relations),
                f"{claim_id} says mixed without reviewed support and challenge",
            )
        elif state == "challenged":
            _require("challenges" in relations, f"{claim_id} says challenged without reviewed challenge")
        elif state in {"missing", "not_applicable"}:
            _require(not links, f"{claim_id} says {state} but has EvidenceLinks")


def _validate_sources(sources: dict[str, dict[str, Any]], package_root: Path) -> None:
    for source_id, source in sources.items():
        _require(source.get("source_type") == "fixture_document", f"{source_id} must be a fixture document")
        _require(source.get("review_state") == "reviewed", f"{source_id} must be reviewed")
        provenance = source.get("provenance")
        _require(isinstance(provenance, dict), f"{source_id} needs provenance")
        _require(
            provenance.get("historical_authority") is False,
            f"{source_id} must not masquerade as historical authority",
        )
        source_path = package_root / str(source.get("uri"))
        _require(source_path.is_file(), f"{source_id} file is missing")
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        _require(source.get("sha256") == digest, f"{source_id} checksum drift")


def _validate_references(package: dict[str, Any], registry: set[str]) -> None:
    for item in _walk(package):
        item_id = item.get("id", package.get("package_id", "package"))
        for key in REFERENCE_KEYS:
            if key not in item:
                continue
            refs = item[key]
            _require(isinstance(refs, list), f"{item_id}.{key} must be an array")
            _require(len(refs) == len(set(refs)), f"{item_id}.{key} contains duplicates")
            for ref in refs:
                _require(ref in registry, f"{item_id}.{key} has orphan reference {ref}")
        for key in SINGLE_REFERENCE_KEYS:
            if key in item:
                ref = item[key]
                _require(isinstance(ref, str) and ref in registry, f"{item_id}.{key} has orphan reference {ref}")


def _validate_compatibility(root: Path) -> None:
    path = root / PACKAGE_RELATIVE / "compatibility" / "architecture_atlas_projection.json"
    projection = _read_json(path)
    _require(projection.get("schema_version") == SCHEMA_VERSION, "compatibility projection version drift")
    source_dataset = projection.get("source_dataset")
    _require(isinstance(source_dataset, dict), "compatibility projection needs source_dataset")
    commit = source_dataset.get("commit")
    _require(
        isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
        "compatibility projection must pin a commit",
    )
    target = projection.get("target_projection")
    _require(isinstance(target, dict), "compatibility projection needs target_projection")
    _require(target.get("invented_fields") == [], "compatibility projection invented target fields")
    entity = target.get("entity")
    _require(isinstance(entity, dict), "compatibility projection needs target Entity")
    spatial = entity.get("spatial_extent")
    _require(
        isinstance(spatial, dict) and spatial.get("precision") == "unknown",
        "legacy coordinate confidence must not become target precision without evidence",
    )
    claims = target.get("claims")
    _require(isinstance(claims, list) and claims, "compatibility projection needs imported Claims")
    for claim in claims:
        _require(claim.get("origin") == "imported", "compatibility Claim must preserve imported origin")
        _require(claim.get("evidence_state") == "missing", "compatibility Claim must expose missing evidence")
        _require(claim.get("evidence_link_refs") == [], "compatibility projection must not invent EvidenceLinks")
    losses = projection.get("losses_and_unknowns")
    _require(isinstance(losses, list) and len(losses) >= 4, "compatibility projection must expose material losses")

    canonical_path = root / str(source_dataset.get("path"))
    if canonical_path.is_file():
        records = _read_json(canonical_path)
        record = next(
            (
                item
                for item in records
                if isinstance(item, dict) and item.get("id") == source_dataset.get("record_id")
            ),
            None,
        )
        _require(record is not None, "pinned Architecture Atlas compatibility record is absent")
        fields = record.get("fields")
        snapshot = projection.get("input_snapshot")
        _require(isinstance(fields, dict) and isinstance(snapshot, dict), "compatibility input is malformed")
        for key, expected in snapshot.items():
            _require(fields.get(key) == expected, f"compatibility input drift for {key}")


def _validate_coverage(
    package: dict[str, Any],
    indexes: dict[str, dict[str, dict[str, Any]]],
    registry: set[str],
    root: Path,
) -> None:
    manifest = _read_json(root / PACKAGE_RELATIVE / "coverage_manifest.json")
    _require(manifest.get("schema_version") == SCHEMA_VERSION, "coverage manifest version drift")
    _require(manifest.get("package_id") == package.get("package_id"), "coverage package id drift")
    counts = Counter()
    for collection, expected_type in COLLECTION_TYPES.items():
        if collection == "derived_observations":
            continue
        counts[expected_type] = len(indexes[collection])
    required = manifest.get("required_object_kinds")
    _require(isinstance(required, dict), "coverage manifest needs required_object_kinds")
    _require(dict(counts) == required, f"coverage counts drift: expected {required}, got {dict(counts)}")

    scenarios = manifest.get("required_scenarios")
    _require(isinstance(scenarios, dict), "coverage manifest needs scenarios")
    for scenario, ref in scenarios.items():
        if scenario == "compatibility_projection":
            _require(
                (root / PACKAGE_RELATIVE / str(ref)).is_file(),
                "coverage manifest compatibility projection is missing",
            )
        else:
            _require(ref in registry, f"coverage scenario {scenario} has orphan reference {ref}")

    exclusions = manifest.get("known_exclusions")
    _require(isinstance(exclusions, list) and exclusions, "coverage manifest needs known exclusions")
    for exclusion in exclusions:
        _require(
            isinstance(exclusion, dict) and exclusion.get("assertion_kind") == "corpus_exclusion",
            "fixture absence must be represented only as corpus exclusion",
        )


def _validate_reviews(root: Path, package: dict[str, Any], *, require_ready: bool) -> None:
    registry = _read_json(root / PACKAGE_RELATIVE / "review_registry.json")
    _require(registry.get("schema_version") == SCHEMA_VERSION, "review registry version drift")
    _require(registry.get("package_id") == package.get("package_id"), "review registry package drift")
    _require(registry.get("required_review_count") == 2, "fixture package requires two reviews")
    reviews = registry.get("reviews")
    _require(isinstance(reviews, list), "review registry reviews must be an array")
    reviewer_ids = [review.get("reviewer_id") for review in reviews if isinstance(review, dict)]
    _require(len(reviewer_ids) == len(set(reviewer_ids)), "fixture reviewers must be independent")
    for review in reviews:
        _require(isinstance(review, dict), "fixture review must be an object")
        artifact = root / str(review.get("artifact"))
        _require(artifact.is_file(), f"fixture review artifact is missing: {artifact}")
        text = artifact.read_text(encoding="utf-8")
        for value in (
            review.get("reviewer_id"),
            review.get("frozen_commit"),
            review.get("decision"),
        ):
            _require(isinstance(value, str) and value in text, "fixture review artifact/registry drift")
    expected_status = (
        "READY"
        if len(reviews) == 2 and all(review.get("decision") == "READY" for review in reviews)
        else "REVIEW_REQUIRED"
    )
    _require(registry.get("status") == expected_status, "review registry status drift")
    _require(package.get("status") == expected_status, "fixture package status drift")
    if require_ready:
        _require(expected_status == "READY", "two independent READY reviews are required")
        frozen = registry.get("frozen_commit")
        _require(
            isinstance(frozen, str) and re.fullmatch(r"[0-9a-f]{40}", frozen) is not None,
            "READY reviews need one frozen commit",
        )
        for review in reviews:
            _require(review.get("frozen_commit") == frozen, "reviews must inspect the same frozen commit")


def validate_package(root: Path = REPO_ROOT, *, require_ready: bool = False) -> dict[str, int]:
    package_root = root / PACKAGE_RELATIVE
    schema = _read_json(package_root / "schema.json")
    package = _read_json(package_root / "package.json")
    _require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema draft drift")
    _require(schema.get("$id", "").endswith(f"/{SCHEMA_VERSION}"), "schema id/version drift")
    _require(package.get("schema_version") == SCHEMA_VERSION, "package schema version drift")
    _require(package.get("fixture_mode") == "synthetic_contract_fixture", "v1 package must be synthetic")
    _require(package.get("world_slice", {}).get("type") == "WorldSlice", "package needs WorldSlice")

    indexes = {
        collection: _index(package.get(collection), expected_type, collection)
        for collection, expected_type in COLLECTION_TYPES.items()
    }
    claims = indexes["claims"]
    claim_ids = set(claims)
    fixture_mode = str(package.get("fixture_mode"))

    nested_ids: set[str] = set()
    for item in _walk(package):
        item_id = item.get("id")
        if isinstance(item_id, str):
            _require(item_id not in nested_ids, f"package contains duplicate global id {item_id}")
            nested_ids.add(item_id)
    nested_ids.add(str(package["world_slice"]["id"]))
    registry = nested_ids | {str(package["package_id"])}

    _validate_sources(indexes["sources"], package_root)
    _validate_claims(claims, indexes["evidence_links"], indexes["sources"], package_root)

    for collection in ("events", "states", "processes", "relations"):
        for item_id, item in indexes[collection].items():
            _validate_extent(
                item.get("temporal_extent"),
                context=item_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                item.get("spatial_extent"),
                context=item_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )

    for process_id, process in indexes["processes"].items():
        stages = process.get("stages")
        _require(isinstance(stages, list) and len(stages) >= 2, f"{process_id} needs at least two stages")
        place_signatures: set[str] = set()
        for stage in stages:
            stage_id = str(stage.get("id"))
            _validate_extent(
                stage.get("temporal_extent"),
                context=stage_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                stage.get("spatial_extent"),
                context=stage_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            place_signatures.add(json.dumps(stage.get("spatial_extent"), sort_keys=True))
        _require(len(place_signatures) >= 2, f"{process_id} must span more than one spatial stage")

    for trajectory_id, trajectory in indexes["trajectories"].items():
        segments = trajectory.get("segments")
        _require(isinstance(segments, list) and len(segments) >= 2, f"{trajectory_id} needs segments")
        inferred = []
        for segment in segments:
            segment_id = str(segment.get("id"))
            _require(
                segment.get("segment_kind") in {"presence", "movement", "inferred_gap"},
                f"{segment_id} has invalid segment kind",
            )
            _validate_extent(
                segment.get("temporal_extent"),
                context=segment_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                segment.get("spatial_extent"),
                context=segment_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            if segment.get("segment_kind") == "inferred_gap":
                inferred.append(segment)
                _require(segment.get("uncertainty_refs"), f"{segment_id} inferred gap needs uncertainty")
                _require(
                    segment.get("spatial_extent", {}).get("kind") == "unknown",
                    f"{segment_id} must not invent a route geometry",
                )
        _require(inferred, f"{trajectory_id} must exercise an inferred gap")

    for region_id, region in indexes["regions"].items():
        versions = region.get("geometry_versions")
        _require(isinstance(versions, list) and len(versions) >= 2, f"{region_id} needs geometry versions")
        geometries: set[str] = set()
        alternatives = []
        for version in versions:
            version_id = str(version.get("id"))
            _require(
                version.get("reconstruction_mode") in ALLOWED_RECONSTRUCTION_MODES,
                f"{version_id} has invalid reconstruction mode",
            )
            _validate_extent(
                version.get("temporal_extent"),
                context=version_id,
                dimension="temporal",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            _validate_extent(
                version.get("spatial_extent"),
                context=version_id,
                dimension="spatial",
                claim_ids=claim_ids,
                fixture_mode=fixture_mode,
            )
            geometries.add(json.dumps(version.get("spatial_extent", {}).get("geometry"), sort_keys=True))
            if version.get("reconstruction_mode") == "alternative_reconstruction":
                alternatives.append(version)
                _require(version.get("uncertainty_refs"), f"{version_id} alternative needs uncertainty")
        _require(len(geometries) >= 2, f"{region_id} geometry must change")
        _require(alternatives, f"{region_id} needs an alternative reconstruction")

    for relation_id, relation in indexes["relations"].items():
        predicate = relation.get("predicate")
        _require(predicate not in DERIVED_ONLY_PREDICATES, f"{relation_id} stores derived {predicate} as Relation")
        relation_claims = relation.get("claim_refs")
        _require(
            isinstance(relation_claims, list) and len(relation_claims) == 1,
            f"{relation_id} must bind exactly one Relation Claim",
        )
        claim = claims[relation_claims[0]]
        _require(
            claim.get("evidence_state") in {"supported", "mixed"},
            f"{relation_id} needs reviewed claim-level evidence",
        )

    for observation_id, observation in indexes["derived_observations"].items():
        _require(observation.get("relation_created") is False, f"{observation_id} must not create Relation")
        claim = claims.get(observation.get("claim_ref"))
        _require(isinstance(claim, dict), f"{observation_id} needs observation Claim")
        _require(
            claim.get("claim_kind") == "observation"
            and claim.get("origin") == "system"
            and claim.get("evidence_state") == "not_applicable",
            f"{observation_id} epistemic dimensions are collapsed",
        )

    for view_id, view in indexes["synchronized_views"].items():
        _validate_extent(
            view.get("time_state"),
            context=view_id,
            dimension="temporal",
            claim_ids=claim_ids,
            fixture_mode=fixture_mode,
        )
        _require(view.get("local_context_refs"), f"{view_id} needs local context")
        _require(view.get("global_context_refs"), f"{view_id} needs global context")
        _require(
            view.get("reconstruction_mode") in ALLOWED_RECONSTRUCTION_MODES,
            f"{view_id} has invalid reconstruction mode",
        )

    _validate_references(package, registry)
    _validate_coverage(package, indexes, registry, root)
    _validate_compatibility(root)
    _validate_reviews(root, package, require_ready=require_ready)

    return {
        expected_type: len(indexes[collection])
        for collection, expected_type in COLLECTION_TYPES.items()
        if collection != "derived_observations"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    try:
        counts = validate_package(args.root, require_ready=args.require_ready)
    except FixtureValidationError as exc:
        print(f"[FAIL] World-model fixtures: {exc}")
        return 1
    rendered = ", ".join(f"{key}={value}" for key, value in counts.items())
    mode = "READY" if args.require_ready else "STRUCTURAL"
    print(f"[PASS] World-model fixtures: mode={mode}; {rendered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

