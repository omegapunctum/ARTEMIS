#!/usr/bin/env python3
"""Validate ARTEMIS Relation semantics v1 against the reviewed World Model fixture."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"
REGISTRY_PATH = ROOT / "fixtures" / "world_model" / "relations" / "v1" / "predicate_registry.json"
REGISTRY_SCHEMA_PATH = ROOT / "fixtures" / "world_model" / "relations" / "v1" / "predicate_registry.schema.json"
CONTRACT_PATH = ROOT / "docs" / "RELATION_SEMANTICS_CONTRACT.md"


class DuplicateKeyError(ValueError):
    pass


class RelationValidationError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON number: {value}")
        ),
    )


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RelationValidationError(message)


def _index(items: list[dict[str, Any]], *, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        _require(isinstance(item_id, str) and item_id, f"{label}: item without id")
        _require(item_id not in result, f"{label}: duplicate id {item_id}")
        result[item_id] = item
    return result


def _typed_ids(world: dict[str, Any], type_name: str) -> set[str]:
    result: set[str] = set()
    for value in world.values():
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict) and item.get("type") == type_name and isinstance(item.get("id"), str):
                result.add(item["id"])
    return result


def _claim_targets_relation(claim: dict[str, Any], relation: dict[str, Any]) -> bool:
    relation_id = relation["id"]
    if relation_id in (claim.get("target_refs") or []):
        return True
    for binding in claim.get("relation_bindings") or []:
        if not isinstance(binding, dict):
            continue
        if binding.get("relation_ref") == relation_id:
            return True
    return False


def _validate_relation_binding(
    claim: dict[str, Any], relation: dict[str, Any], errors: list[str]
) -> None:
    relation_id = relation["id"]
    bindings = [
        binding
        for binding in (claim.get("relation_bindings") or [])
        if isinstance(binding, dict) and binding.get("relation_ref") == relation_id
    ]
    for binding in bindings:
        expected_equal = {
            "subject_ref": relation.get("subject_ref"),
            "predicate": relation.get("predicate"),
            "object_ref": relation.get("object_ref"),
            "directionality": relation.get("directionality"),
        }
        for field, expected in expected_equal.items():
            if field in binding and binding.get(field) != expected:
                errors.append(
                    f"{relation_id}: claim {claim['id']} relation_binding {field} "
                    f"does not match Relation ({binding.get(field)!r} != {expected!r})"
                )
        for field in ("mechanism", "scope"):
            if field in binding and field in relation and binding.get(field) != relation.get(field):
                errors.append(
                    f"{relation_id}: claim {claim['id']} relation_binding {field} "
                    "does not match Relation"
                )


def _reviewed_evidence_for_claim(
    claim_id: str, evidence_links: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [
        link
        for link in evidence_links
        if link.get("claim_id") == claim_id and link.get("review_state") == "reviewed"
    ]


def _support_meets_minimum(link: dict[str, Any], minimum: str) -> bool:
    if link.get("relation_to_claim") != "supports":
        return False
    if minimum == "any_reviewed":
        return True
    return link.get("evidence_strength") == minimum


def _is_contested(
    claim: dict[str, Any], reviewed_evidence: list[dict[str, Any]]
) -> bool:
    if claim.get("review_state") == "contested":
        return True
    if claim.get("evidence_state") == "mixed":
        return True
    return any(link.get("relation_to_claim") == "challenges" for link in reviewed_evidence)


def _validate_registry(registry: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(registry),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise RelationValidationError(f"predicate registry schema failed: {details}")

    predicate_ids = [item["predicate"] for item in registry["predicates"]]
    _require(len(predicate_ids) == len(set(predicate_ids)), "predicate registry contains duplicates")
    _require(
        registry["derived_observation_policy"]["automatic_relation_creation"] is False,
        "derived observation policy must prohibit automatic Relation creation",
    )


def validate_relation_semantics(
    world: dict[str, Any], registry: dict[str, Any], registry_schema: dict[str, Any]
) -> list[str]:
    _validate_registry(registry, registry_schema)

    errors: list[str] = []
    predicates = {item["predicate"]: item for item in registry["predicates"]}
    entities = _index(world.get("entities") or [], label="entities")
    claims = _index(world.get("claims") or [], label="claims")
    sources = _index(world.get("sources") or [], label="sources")
    evidence_links = list(world.get("evidence_links") or [])
    relations = list(world.get("relations") or [])
    derived_observations = list(world.get("derived_observations") or [])
    uncertainty_ids = _typed_ids(world, "Uncertainty")

    symmetric_signatures: dict[tuple[str, str, str, str, str], str] = {}

    for relation in relations:
        relation_id = relation.get("id") or "<missing-relation-id>"
        if relation.get("type") != "Relation":
            errors.append(f"{relation_id}: type must be Relation")
            continue

        predicate_id = relation.get("predicate")
        predicate = predicates.get(predicate_id)
        if predicate is None:
            errors.append(f"{relation_id}: unregistered predicate {predicate_id!r}")
            continue

        subject_ref = relation.get("subject_ref")
        object_ref = relation.get("object_ref")
        if subject_ref not in entities:
            errors.append(f"{relation_id}: subject_ref must resolve to Entity ({subject_ref!r})")
        if object_ref not in entities:
            errors.append(f"{relation_id}: object_ref must resolve to Entity ({object_ref!r})")
        if subject_ref == object_ref and not predicate["allow_self_relation"]:
            errors.append(f"{relation_id}: self relation is forbidden for {predicate_id}")

        if relation.get("directionality") != predicate["directionality"]:
            errors.append(
                f"{relation_id}: directionality must be {predicate['directionality']!r} "
                f"for {predicate_id}, got {relation.get('directionality')!r}"
            )

        mechanism_rule = predicate["mechanism"]
        mechanism = relation.get("mechanism")
        if mechanism_rule == "required" and not (
            isinstance(mechanism, str) and mechanism.strip()
        ):
            errors.append(f"{relation_id}: {predicate_id} requires non-empty mechanism")

        scope_rule = predicate["scope"]
        scope = relation.get("scope")
        if scope_rule == "required" and not (isinstance(scope, str) and scope.strip()):
            errors.append(f"{relation_id}: {predicate_id} requires non-empty scope")

        claim_refs = relation.get("claim_refs") or []
        if not claim_refs:
            errors.append(f"{relation_id}: Relation requires at least one principal claim_ref")
            continue

        relation_contested = False
        for claim_ref in claim_refs:
            claim = claims.get(claim_ref)
            if claim is None:
                errors.append(f"{relation_id}: missing Claim {claim_ref}")
                continue
            if not _claim_targets_relation(claim, relation):
                errors.append(
                    f"{relation_id}: Claim {claim_ref} does not explicitly target/bind the Relation"
                )
            _validate_relation_binding(claim, relation, errors)

            if claim.get("claim_kind") not in predicate["allowed_claim_kinds"]:
                errors.append(
                    f"{relation_id}: Claim {claim_ref} kind {claim.get('claim_kind')!r} "
                    f"not allowed for {predicate_id}"
                )

            reviewed = _reviewed_evidence_for_claim(claim_ref, evidence_links)
            support = [
                link
                for link in reviewed
                if _support_meets_minimum(
                    link, predicate["minimum_supporting_evidence_strength"]
                )
            ]
            if not support:
                errors.append(
                    f"{relation_id}: Claim {claim_ref} lacks reviewed supporting evidence "
                    f"meeting {predicate['minimum_supporting_evidence_strength']!r}"
                )

            for link in reviewed:
                source_id = link.get("source_id")
                source = sources.get(source_id)
                if source is None:
                    errors.append(
                        f"{relation_id}: EvidenceLink {link.get('id')} references missing Source {source_id!r}"
                    )
                elif source.get("review_state") != "reviewed":
                    errors.append(
                        f"{relation_id}: Source {source_id} for Relation evidence is not reviewed"
                    )

            contested = _is_contested(claim, reviewed)
            relation_contested = relation_contested or contested
            if contested:
                if not (claim.get("uncertainty_refs") or []):
                    errors.append(
                        f"{relation_id}: contested Claim {claim_ref} requires uncertainty_refs"
                    )
                if not (relation.get("uncertainty_refs") or []):
                    errors.append(
                        f"{relation_id}: contested/challenged Relation requires uncertainty_refs"
                    )

            if uncertainty_ids:
                for uncertainty_ref in claim.get("uncertainty_refs") or []:
                    if uncertainty_ref not in uncertainty_ids:
                        errors.append(
                            f"{relation_id}: Claim {claim_ref} references unknown Uncertainty {uncertainty_ref}"
                        )

        if relation_contested and predicate["contested_uncertainty_policy"] == "required_when_contested_or_challenged":
            if not relation.get("uncertainty_refs"):
                errors.append(
                    f"{relation_id}: {predicate_id} contested uncertainty policy is not satisfied"
                )

        if uncertainty_ids:
            for uncertainty_ref in relation.get("uncertainty_refs") or []:
                if uncertainty_ref not in uncertainty_ids:
                    errors.append(
                        f"{relation_id}: Relation references unknown Uncertainty {uncertainty_ref}"
                    )

        if predicate["directionality"] == "symmetric":
            endpoints = sorted([str(subject_ref), str(object_ref)])
            signature = (
                str(predicate_id),
                endpoints[0],
                endpoints[1],
                canonical_json(relation.get("temporal_extent")),
                canonical_json(relation.get("spatial_extent")),
            )
            previous = symmetric_signatures.get(signature)
            if previous is not None:
                errors.append(
                    f"{relation_id}: mirrored/duplicate symmetric Relation duplicates {previous}"
                )
            else:
                symmetric_signatures[signature] = relation_id

    derived_ids: set[str] = set()
    for observation in derived_observations:
        observation_id = observation.get("id") or "<missing-observation-id>"
        if observation_id in derived_ids:
            errors.append(f"DerivedObservation duplicate id: {observation_id}")
        derived_ids.add(str(observation_id))
        if observation.get("observation_kind") == "co_presence":
            if observation.get("relation_created") is not False:
                errors.append(
                    f"{observation_id}: co_presence DerivedObservation must keep relation_created=false"
                )

    if registry["derived_observation_policy"]["co_presence"] != "derived_observation_only":
        errors.append("registry must keep co_presence as derived_observation_only")
    if registry["derived_observation_policy"]["similarity"] != "analytical_result_only":
        errors.append("registry must keep similarity as analytical_result_only")
    if registry["derived_observation_policy"]["temporal_order"] != "insufficient_for_relation":
        errors.append("registry must reject temporal order as sufficient Relation evidence")

    return errors


def validate_paths(
    world_path: Path = WORLD_PATH,
    registry_path: Path = REGISTRY_PATH,
    registry_schema_path: Path = REGISTRY_SCHEMA_PATH,
) -> dict[str, Any]:
    world = load_json(world_path)
    registry = load_json(registry_path)
    registry_schema = load_json(registry_schema_path)
    if not isinstance(world, dict) or not isinstance(registry, dict) or not isinstance(registry_schema, dict):
        raise RelationValidationError("world/registry/schema must all be JSON objects")
    errors = validate_relation_semantics(world, registry, registry_schema)
    if errors:
        raise RelationValidationError("; ".join(errors))
    return {
        "registry_id": registry["registry_id"],
        "registry_status": registry["status"],
        "relation_count": len(world.get("relations") or []),
        "predicate_count": len(registry["predicates"]),
        "derived_observation_count": len(world.get("derived_observations") or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=WORLD_PATH)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=REGISTRY_SCHEMA_PATH)
    args = parser.parse_args()

    try:
        summary = validate_paths(args.world, args.registry, args.schema)
        print(
            "[PASS] Relation semantics v1: "
            f"registry={summary['registry_id']}; status={summary['registry_status']}; "
            f"relations={summary['relation_count']}; predicates={summary['predicate_count']}; "
            f"derived_observations={summary['derived_observation_count']}"
        )
        return 0
    except (RelationValidationError, DuplicateKeyError, KeyError, TypeError, ValueError, OSError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
