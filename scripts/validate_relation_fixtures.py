#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = Path("fixtures/world_model/relations/v1/package.json")
SCHEMA_PATH = Path("fixtures/world_model/relations/v1/schema.json")
REGISTRY_PATH = Path("fixtures/world_model/relations/v1/review_registry.json")
README_PATH = Path("fixtures/world_model/relations/v1/README.md")
COMPATIBILITY_PATH = Path("fixtures/world_model/relations/v1/compatibility/architecture_atlas_projection.json")
OWNER_PATH = Path("docs/RELATION_LADDER_CONTRACT.md")
WORK_PATH = Path("docs/work/2026-08-05_RELATION_LADDER_REVIEW.md")
REVIEW_SCOPE = (
    PACKAGE_PATH,
    SCHEMA_PATH,
    README_PATH,
    COMPATIBILITY_PATH,
    Path("fixtures/world_model/relations/v1/sources/relation-profile.md"),
    OWNER_PATH,
    WORK_PATH,
    Path("scripts/validate_relation_fixtures.py"),
    Path("tests/test_relation_fixtures.py"),
)
LEVELS = ("co_present", "possible_encounter", "documented_encounter", "interaction", "influence", "causal")
DOCUMENTED = {"documented_encounter", "interaction", "influence", "causal"}
CLAIM_DIGEST_KEYS = (
    "target_ref", "subject_ref", "predicate", "object_ref", "statement", "qualifiers",
    "claim_kind", "origin", "review_state", "confidence", "evidence_state",
)


class DuplicateKeyError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def claim_digest(claim: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical({key: claim[key] for key in CLAIM_DIGEST_KEYS})).hexdigest()


def _normalized_bytes(path: Path, data: bytes) -> bytes:
    if path == PACKAGE_PATH:
        value = json.loads(data, object_pairs_hook=_strict_object)
        value["status"] = "REVIEW_REQUIRED"
        value["record_time"]["reviewed_at"] = None
        return _canonical(value) + b"\n"
    text = data.decode("utf-8")
    if path in {README_PATH, OWNER_PATH}:
        text = text.replace("Status: `READY`", "Status: `REVIEW_REQUIRED`", 1)
    if path == WORK_PATH:
        text = re.sub(r"- State: `(?:REVIEW_REQUIRED|READY)`\.", "- State: `REVIEW_REQUIRED`.", text, count=1)
        text = re.sub(r"- Frozen commit: `[^`]+`\.", "- Frozen commit: `PENDING`.", text, count=1)
        text = re.sub(r"- Reviewed digest: `[^`]+`\.", "- Reviewed digest: `PENDING`.", text, count=1)
    return text.encode("utf-8")


def compute_review_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in REVIEW_SCOPE:
        path = root / relative
        data = _normalized_bytes(relative, path.read_bytes())
        digest.update(str(relative).encode("utf-8") + b"\0" + data + b"\0")
    return digest.hexdigest()


def _git_output(root: Path, *args: str) -> bytes:
    env = {key: value for key, value in os.environ.items() if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_REPLACE_REF_BASE"}}
    return subprocess.run(("git", "-C", str(root), *args), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).stdout


def _ids(items: list[dict[str, Any]]) -> list[str]:
    return [item["id"] for item in items]


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def is_co_present(case: dict[str, Any]) -> bool:
    subject = [p for p in case["presences"] if p["entity_ref"] == case["subject_ref"]]
    obj = [p for p in case["presences"] if p["entity_ref"] == case["object_ref"]]
    for left in subject:
        for right in obj:
            if left["place_ref"] != right["place_ref"]:
                continue
            if max(date.fromisoformat(left["start"]), date.fromisoformat(right["start"])) <= min(date.fromisoformat(left["end"]), date.fromisoformat(right["end"])):
                return True
    return False


def _validate_base_packages(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    for declared in package["base_packages"]:
        registry_path = root / declared["registry_path"]
        try:
            actual = load_json(registry_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"base registry load failed: {exc}")
            continue
        for key in ("package_id", "status", "frozen_commit", "reviewed_content_sha256"):
            _require(declared[key] == actual.get(key), f"base package binding mismatch for {declared['package_id']}: {key}", errors)


def _validate_ladder(package: dict[str, Any], errors: list[str]) -> None:
    levels = package["ladder_levels"]
    _require([item["id"] for item in levels] == list(LEVELS), "ladder levels must use the canonical closed order", errors)
    _require([item["rank"] for item in levels] == list(range(1, 7)), "ladder ranks must be exactly 1..6", errors)
    _require(levels[0]["storage_kind"] == "computed_observation", "co_present must remain a computed observation", errors)
    _require(levels[1]["storage_kind"] == "explicit_inference", "possible_encounter must remain an explicit inference", errors)
    _require(all(item["storage_kind"] == "relation_claim" for item in levels[2:]), "documented levels must be RelationClaims", errors)

    expected_pairs = list(zip(LEVELS, LEVELS[1:]))
    rules = package["promotion_rules"]
    _require([(item["from"], item["to"]) for item in rules] == expected_pairs, "promotion rules must cover every adjacent boundary exactly once", errors)
    _require(all(item["automatic"] is False for item in rules), "automatic ladder promotion is forbidden", errors)


def _validate_provenance(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    claims = {item["id"]: item for item in package["claims"]}
    sources = {item["id"]: item for item in package["sources"]}
    evidence = package["evidence_links"]
    _require(len(claims) == len(package["claims"]), "claim IDs must be unique", errors)
    _require(len(sources) == len(package["sources"]), "source IDs must be unique", errors)
    _require(len(_ids(evidence)) == len(set(_ids(evidence))), "EvidenceLink IDs must be unique", errors)

    for claim in claims.values():
        _require(claim["assertion_sha256"] == claim_digest(claim), f"claim {claim['id']} assertion digest mismatch", errors)

    for link in evidence:
        claim = claims.get(link["claim_id"])
        source = sources.get(link["source_id"])
        _require(claim is not None, f"EvidenceLink {link['id']} has dangling claim", errors)
        _require(source is not None, f"EvidenceLink {link['id']} has dangling source", errors)
        if claim is None or source is None:
            continue
        try:
            source_text = (root / source["path"]).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"source file load failed for {source['id']}: {exc}")
            continue
        expected = f"{link['locator']} SHA256[{claim['assertion_sha256']}]"
        _require(expected in source_text, f"EvidenceLink {link['id']} locator does not bind its exact Claim digest", errors)

    for claim in claims.values():
        supporting = [link for link in evidence if link["claim_id"] == claim["id"] and link["relation_to_claim"] == "supports" and link["review_state"] == "reviewed"]
        if claim["evidence_state"] == "supported":
            _require(bool(supporting), f"supported Claim {claim['id']} requires reviewed supporting evidence", errors)
        else:
            _require(not supporting, f"non-supported Claim {claim['id']} must not have supporting evidence", errors)


def _validate_case(case: dict[str, Any], claims: dict[str, dict[str, Any]], evidence: list[dict[str, Any]], uncertainties: dict[str, dict[str, Any]], errors: list[str]) -> None:
    level = case["asserted_level"]
    co_present = is_co_present(case)
    claim = claims.get(case["level_claim_ref"]) if case["level_claim_ref"] else None
    if level == "none":
        _require(not co_present, f"case {case['id']} expects none but is co-present", errors)
        _require(claim is None, f"case {case['id']} none must not create a Claim", errors)
        return
    _require(co_present, f"case {case['id']} level {level} lacks deterministic co-presence", errors)
    if level == "co_present":
        _require(claim is None, f"case {case['id']} computed co-presence must not create a historical Relation", errors)
        return

    _require(claim is not None, f"case {case['id']} level {level} requires an item-bound Claim", errors)
    if claim is None:
        return
    _require(claim["target_ref"] == case["id"], f"case {case['id']} Claim target binding mismatch", errors)
    _require(claim["subject_ref"] == case["subject_ref"] and claim["object_ref"] == case["object_ref"], f"case {case['id']} Claim endpoint binding mismatch", errors)
    _require(claim["predicate"] == level, f"case {case['id']} Claim predicate does not support asserted level", errors)

    if level == "possible_encounter":
        _require(bool(case["assumptions"]), f"case {case['id']} possible encounter requires explicit assumptions", errors)
        _require(bool(case["uncertainty_refs"]), f"case {case['id']} possible encounter requires relation uncertainty", errors)
        _require(claim["claim_kind"] == "inference" and claim["evidence_state"] == "missing", f"case {case['id']} possible encounter must remain an unsupported inference", errors)
        claim_assumptions = set(claim["qualifiers"].get("assumption_refs", []))
        _require(claim_assumptions == {item["id"] for item in case["assumptions"]}, f"case {case['id']} assumption binding mismatch", errors)
        for ref in case["uncertainty_refs"]:
            uncertainty = uncertainties.get(ref)
            _require(uncertainty is not None and uncertainty["subject_claim_ref"] == claim["id"], f"case {case['id']} uncertainty binding mismatch", errors)
        return

    _require(level in DOCUMENTED, f"case {case['id']} uses unknown documented level", errors)
    _require(claim["review_state"] == "reviewed" and claim["evidence_state"] == "supported", f"case {case['id']} documented level requires reviewed supported Claim", errors)
    supporting = [link for link in evidence if link["claim_id"] == claim["id"] and link["relation_to_claim"] == "supports" and link["review_state"] == "reviewed"]
    _require(bool(supporting), f"case {case['id']} documented level requires a supporting locator", errors)
    qualifiers = claim["qualifiers"]
    if level == "documented_encounter":
        _require(bool(qualifiers.get("contact_kind")), f"case {case['id']} encounter evidence must name contact kind", errors)
    elif level == "interaction":
        _require(bool(qualifiers.get("action")), f"case {case['id']} interaction requires a specific action or exchange", errors)
    elif level == "influence":
        _require(qualifiers.get("direction") == "subject_to_object" and bool(qualifiers.get("mechanism")) and bool(qualifiers.get("scope")), f"case {case['id']} influence requires direction, mechanism and scope", errors)
    elif level == "causal":
        _require(qualifiers.get("direction") == "subject_to_object" and bool(qualifiers.get("mechanism")) and bool(qualifiers.get("scope")) and bool(qualifiers.get("counterfactual_basis")), f"case {case['id']} causal Claim requires direction, mechanism, scope and counterfactual basis", errors)
        basis = claims.get(case["causal_basis_claim_ref"])
        _require(case["causal_basis_claim_ref"] != claim["id"] and basis is not None, f"case {case['id']} causal basis must be a distinct Claim", errors)
        if basis is not None:
            _require(basis["target_ref"] == case["id"] and basis["predicate"] == "causal_basis", f"case {case['id']} causal basis binding mismatch", errors)
            _require(any(link["claim_id"] == basis["id"] and link["relation_to_claim"] == "supports" for link in evidence), f"case {case['id']} causal basis requires supporting evidence", errors)
        _require(case["causal_policy_ref"] == "causal-policy-explicit-basis-v1", f"case {case['id']} causal policy reference is missing", errors)


def _validate_cases(package: dict[str, Any], errors: list[str]) -> None:
    claims = {item["id"]: item for item in package["claims"]}
    uncertainties = {item["id"]: item for item in package["uncertainties"]}
    case_ids = _ids(package["cases"])
    _require(len(case_ids) == len(set(case_ids)), "case IDs must be unique", errors)
    roles = {item["fixture_role"] for item in package["cases"]}
    _require(roles == {"positive", "negative", "ambiguous"}, "fixtures must include positive, negative and ambiguous roles", errors)
    expected = {"none", *LEVELS}
    _require({item["asserted_level"] for item in package["cases"]} == expected, "fixtures must cover none and every ladder level", errors)
    for case in package["cases"]:
        try:
            for presence in case["presences"]:
                _require(date.fromisoformat(presence["start"]) <= date.fromisoformat(presence["end"]), f"case {case['id']} has reversed presence interval", errors)
            _validate_case(case, claims, package["evidence_links"], uncertainties, errors)
        except (ValueError, KeyError) as exc:
            errors.append(f"case {case.get('id', '<unknown>')} invalid: {exc}")


def _validate_separation(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    expected_non_relations = {("classification", False), ("similarity", False)}
    _require({(item["signal_kind"], item["creates_relation"]) for item in package["non_relation_cases"]} == expected_non_relations, "classification and Similarity must remain separate non-Relations", errors)
    compatibility = load_json(root / COMPATIBILITY_PATH)
    _require(compatibility.get("migration_performed") is False, "relation compatibility must not claim migration", errors)
    _require(compatibility.get("same_movement", {}).get("target_kind") == "classification_projection" and compatibility["same_movement"].get("ladder_level") is None, "same_movement must project only to classification", errors)
    _require(compatibility.get("similarity", {}).get("creates_relation") is False and compatibility["similarity"].get("ladder_level") is None, "Similarity must not create a Relation", errors)
    for legacy in ("influenced", "inspired_by"):
        item = compatibility.get(legacy, {})
        _require(item.get("target_kind") == "unresolved_relation_candidate" and item.get("ladder_level") is None, f"legacy {legacy} must remain unresolved", errors)
        _require(set(item.get("required_before_promotion", [])) == {"atomic Claim", "locator", "direction", "mechanism", "scope"}, f"legacy {legacy} compatibility losses must be closed", errors)


def _validate_owner(root: Path, package: dict[str, Any], errors: list[str]) -> None:
    owner = (root / OWNER_PATH).read_text(encoding="utf-8")
    statuses = re.findall(r"^- Status: `(REVIEW_REQUIRED|READY)`\.$", owner, flags=re.MULTILINE)
    _require(statuses == [package["status"]], "relation owner status must agree with package", errors)
    for term in (*LEVELS, "same_movement", "Similarity", "five explicit negative regression classes"):
        _require(term in owner or term in (root / WORK_PATH).read_text(encoding="utf-8"), f"relation owner/record missing {term}", errors)


def _validate_ready(root: Path, package: dict[str, Any], registry: dict[str, Any], require_ready: bool, errors: list[str]) -> None:
    _require(registry.get("status") == package["status"], "relation package/registry status drift", errors)
    if package["status"] != "READY":
        if require_ready:
            errors.append("relation package is not READY")
        return
    frozen = registry.get("frozen_commit")
    reviewed_digest = registry.get("reviewed_content_sha256")
    reviews = registry.get("reviews", [])
    _require(isinstance(frozen, str) and bool(re.fullmatch(r"[0-9a-f]{40}", frozen or "")), "READY registry requires frozen commit", errors)
    _require(isinstance(reviewed_digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", reviewed_digest or "")), "READY registry requires reviewed digest", errors)
    _require(len(reviews) == 2 and {item.get("track") for item in reviews} == {"semantic-model", "validator-integrity"}, "READY requires two distinct review tracks", errors)
    _require(len({item.get("reviewer_instance_id") for item in reviews}) == 2, "READY review instances must be distinct", errors)
    for review in reviews:
        _require(review.get("decision") == "READY" and review.get("independence_attestation") is True, f"review {review.get('review_id')} is not independently READY", errors)
        counts = review.get("finding_counts", {})
        _require(counts.get("critical") == 0 and counts.get("material") == 0, f"review {review.get('review_id')} has unresolved blocker", errors)
        _require(review.get("frozen_commit") == frozen and review.get("reviewed_content_sha256") == reviewed_digest, f"review {review.get('review_id')} frozen binding mismatch", errors)
        artifact = root / review.get("artifact", "")
        try:
            _require(artifact.is_file() and not artifact.is_symlink(), f"review artifact {artifact} must be a regular non-symlink file", errors)
            _require(hashlib.sha256(artifact.read_bytes()).hexdigest() == review.get("artifact_sha256"), f"review artifact {artifact} checksum mismatch", errors)
        except OSError as exc:
            errors.append(f"review artifact load failed: {exc}")
    if not frozen or not reviewed_digest:
        return
    try:
        head = _git_output(root, "rev-parse", "HEAD").decode().strip()
        _git_output(root, "merge-base", "--is-ancestor", frozen, head)
        _require(compute_review_digest(root) == reviewed_digest, "current normalized relation digest differs from reviewed digest", errors)
        for relative in REVIEW_SCOPE:
            _git_output(root, "cat-file", "-e", f"{frozen}:{relative}")
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"review gate: Git ancestry/tree validation failed: {exc}")


def validate_repository(root: Path, require_ready: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json(root / SCHEMA_PATH)
        package = load_json(root / PACKAGE_PATH)
        registry = load_json(root / REGISTRY_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"fixture JSON load failed: {exc}"]
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"schema {location}: {error.message}")
    if errors:
        return errors
    _validate_base_packages(root, package, errors)
    _validate_ladder(package, errors)
    _validate_provenance(root, package, errors)
    _validate_cases(package, errors)
    _validate_separation(root, package, errors)
    _validate_owner(root, package, errors)
    _validate_ready(root, package, registry, require_ready, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = validate_repository(args.root.resolve(), require_ready=args.require_ready)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    package = load_json(args.root.resolve() / PACKAGE_PATH)
    print(f"relation fixtures valid: {len(package['cases'])} ladder cases, {len(package['non_relation_cases'])} separate signals; status={package['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
