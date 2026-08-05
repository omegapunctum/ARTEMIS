from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts import validate_relation_fixtures as validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path("fixtures/world_model/relations/v1/package.json")
REGISTRY_REL = Path("fixtures/world_model/relations/v1/review_registry.json")
README_REL = Path("fixtures/world_model/relations/v1/README.md")
OWNER_REL = Path("docs/RELATION_LADDER_CONTRACT.md")
WORK_REL = Path("docs/work/2026-08-05_RELATION_LADDER_REVIEW.md")
COMPAT_REL = Path(
    "fixtures/world_model/relations/v1/compatibility/architecture_atlas_projection.json"
)


def _load(root: Path, relative: Path) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write(root: Path, relative: Path, value: dict) -> None:
    (root / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    package = _load(target, PACKAGE_REL)
    package["status"] = "REVIEW_REQUIRED"
    package["record_time"]["reviewed_at"] = None
    _write(target, PACKAGE_REL, package)
    registry = _load(target, REGISTRY_REL)
    registry.update(
        status="REVIEW_REQUIRED",
        frozen_commit=None,
        reviewed_content_sha256=None,
        reviews=[],
    )
    _write(target, REGISTRY_REL, registry)
    for relative in (README_REL, OWNER_REL):
        path = target / relative
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Status: `READY`", "Status: `REVIEW_REQUIRED`", 1
            ),
            encoding="utf-8",
        )
    work = target / WORK_REL
    text = work.read_text(encoding="utf-8")
    text = text.replace("- State: `READY`.", "- State: `REVIEW_REQUIRED`.", 1)
    text = validator.re.sub(
        r"- Frozen commit: `[^`]+`\.", "- Frozen commit: `PENDING`.", text, count=1
    )
    text = validator.re.sub(
        r"- Reviewed digest: `[^`]+`\.",
        "- Reviewed digest: `PENDING`.",
        text,
        count=1,
    )
    text = validator.re.sub(
        r"- Reviews: .+", "- Reviews: `PENDING`.", text, count=1
    )
    work.write_text(text, encoding="utf-8")
    return target


def _case(package: dict, case_id: str) -> dict:
    return next(item for item in package["cases"] if item["id"] == case_id)


def _claim(package: dict, claim_id: str) -> dict:
    return next(item for item in package["claims"] if item["id"] == claim_id)


def _refresh_claim_locator(root: Path, package: dict, claim_id: str) -> None:
    claim = _claim(package, claim_id)
    old_digest = claim["assertion_sha256"]
    claim["assertion_sha256"] = validator.claim_digest(claim)
    source = root / "fixtures/world_model/relations/v1/sources/relation-profile.md"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            f"SHA256[{old_digest}]", f"SHA256[{claim['assertion_sha256']}]", 1
        ),
        encoding="utf-8",
    )


def _presence(case: dict, entity_ref: str) -> dict:
    return next(
        item for item in case["presence_extents"] if item["entity_ref"] == entity_ref
    )


def _run_git(root: Path, *args: str, when: datetime | None = None) -> str:
    env = None
    if when is not None:
        import os

        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": when.isoformat(),
            "GIT_COMMITTER_DATE": when.isoformat(),
        }
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    ).stdout.strip()


def _prepare_ready(root: Path) -> tuple[str, str]:
    now = datetime.now(UTC).replace(microsecond=0)
    frozen_time = now - timedelta(minutes=5)
    ready_time = now - timedelta(minutes=1)
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "ARTEMIS Test")
    _run_git(root, "config", "user.email", "artemis-test@example.invalid")
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "frozen relation candidate", when=frozen_time)
    frozen = _run_git(root, "rev-parse", "HEAD")
    digest = validator.compute_review_digest(root)

    reviews = []
    artifact_dir = root / "docs/work/reviews"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for index, track in enumerate(("semantic-model", "validator-integrity")):
        review = {
            "review_id": f"relation-v1-{track}",
            "reviewer_id": f"test-{track}-reviewer",
            "reviewer_instance_id": f"test-{track}-instance",
            "track": track,
            "independence_method": "separate_agent_task",
            "artifact": f"docs/work/reviews/relation-v1-{track}.json",
            "artifact_sha256": "",
            "frozen_commit": frozen,
            "reviewed_content_sha256": digest,
            "reviewed_at": (now - timedelta(minutes=3 - index)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "decision": "READY",
            "finding_counts": {"critical": 0, "material": 0, "minor": 0},
            "findings": [],
            "independence_attestation": True,
        }
        artifact = {
            "artifact_format": "artemis-review-attestation-v1",
            **{
                key: value
                for key, value in review.items()
                if key not in {"artifact", "artifact_sha256"}
            },
        }
        artifact_path = root / review["artifact"]
        _write(root, Path(review["artifact"]), artifact)
        review["artifact_sha256"] = hashlib.sha256(
            artifact_path.read_bytes()
        ).hexdigest()
        reviews.append(review)

    package = _load(root, PACKAGE_REL)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = ready_time.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    _write(root, PACKAGE_REL, package)
    for relative in (README_REL, OWNER_REL):
        path = root / relative
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Status: `REVIEW_REQUIRED`", "Status: `READY`", 1
            ),
            encoding="utf-8",
        )
    work = root / WORK_REL
    text = work.read_text(encoding="utf-8").replace(
        "- State: `REVIEW_REQUIRED`.", "- State: `READY`.", 1
    )
    text = text.replace(
        "- Frozen commit: `PENDING`.", f"- Frozen commit: `{frozen}`.", 1
    )
    text = text.replace(
        "- Reviewed digest: `PENDING`.", f"- Reviewed digest: `{digest}`.", 1
    )
    text = text.replace(
        "- Reviews: `PENDING`.",
        "- Reviews: `semantic-model` and `validator-integrity` READY.",
        1,
    )
    work.write_text(text, encoding="utf-8")
    _write(
        root,
        REGISTRY_REL,
        {
            "schema_version": "1.0.0",
            "package_id": "artemis-relation-ladder-v1",
            "status": "READY",
            "frozen_commit": frozen,
            "reviewed_content_sha256": digest,
            "required_review_count": 2,
            "review_scope_id": "relation-ladder-v1-canonical",
            "reviews": reviews,
        },
    )
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "finalize relation READY", when=ready_time)
    return frozen, digest


def test_relation_fixture_package_validates(tmp_path: Path) -> None:
    assert validator.validate_repository(_copy_repo(tmp_path)) == []


def test_require_ready_rejects_review_required_package(tmp_path: Path) -> None:
    assert any(
        "relation package is not READY" in item
        for item in validator.validate_repository(_copy_repo(tmp_path), require_ready=True)
    )


def test_relation_predicates_are_unranked_and_independent() -> None:
    package = _load(ROOT, PACKAGE_REL)
    predicates = {item["id"]: item for item in package["relation_predicates"]}
    assert all("rank" not in item for item in predicates.values())
    assert predicates["possible_encounter"]["requires_co_presence"] is True
    for predicate in validator.DOCUMENTED:
        assert predicates[predicate]["requires_co_presence"] is False


def test_predicate_metadata_cannot_be_swapped(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    predicates = {item["id"]: item for item in package["relation_predicates"]}
    predicates["interaction"]["family"] = "historical_effect"
    _write(root, PACKAGE_REL, package)
    assert any(
        "relation predicate interaction semantic profile drift" in item
        for item in validator.validate_repository(root)
    )


@pytest.mark.parametrize(
    ("case_id", "expected"),
    [
        ("case-same-city-no-contact", "confirmed"),
        ("case-disjoint-place", "excluded"),
        ("case-approximate-city-overlap", "possible"),
        ("case-open-interval-overlap", "possible"),
        ("case-conflicting-place-reconstruction", "possible"),
        ("case-inferred-route-proximity", "possible"),
        ("case-documented-encounter-unknown-extents", "unknown"),
    ],
)
def test_co_presence_uses_reviewed_uncertainty_semantics(
    case_id: str, expected: str
) -> None:
    package = _load(ROOT, PACKAGE_REL)
    parents = {
        item["child_ref"]: item["parent_ref"] for item in package["place_hierarchy"]
    }
    assert validator.co_presence_state(_case(package, case_id), parents) == expected


def test_nested_place_is_not_treated_as_a_different_place() -> None:
    package = _load(ROOT, PACKAGE_REL)
    parents = {
        item["child_ref"]: item["parent_ref"] for item in package["place_hierarchy"]
    }
    assert (
        validator.co_presence_state(_case(package, "case-plausible-workshop"), parents)
        == "confirmed"
    )


def test_year_precision_cannot_create_confirmed_co_presence() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = copy.deepcopy(_case(package, "case-same-city-no-contact"))
    for presence in case["presence_extents"]:
        candidate = presence["temporal_candidates"][0]
        candidate["kind"] = "instant"
        candidate["lower"] = {
            "value": "1504",
            "precision": "year",
            "qualifier": "exact",
            "inclusive": True,
        }
        candidate["upper"] = copy.deepcopy(candidate["lower"])
    parents = {
        item["child_ref"]: item["parent_ref"] for item in package["place_hierarchy"]
    }
    assert validator.co_presence_state(case, parents) == "possible"


def test_documented_predicates_do_not_require_personal_co_presence() -> None:
    package = _load(ROOT, PACKAGE_REL)
    independent = {
        "case-correspondence-without-co-presence": "interaction",
        "case-interaction-via-intermediary": "interaction",
        "case-posthumous-influence": "influence",
        "case-process-causal-dependency": "causal",
        "case-documented-encounter-unknown-extents": "documented_encounter",
    }
    for case_id, predicate in independent.items():
        case = _case(package, case_id)
        assert case["asserted_predicate"] == predicate
        assert case["co_presence_result"] in {"excluded", "unknown"}


@pytest.mark.parametrize(
    ("case_id", "mutation", "needle"),
    [
        (
            "case-plausible-workshop",
            lambda case: case.update(assumptions=[]),
            "requires explicit assumptions",
        ),
        (
            "case-plausible-workshop",
            lambda case: case.update(asserted_predicate="documented_encounter"),
            "predicate does not support asserted predicate",
        ),
        (
            "case-documented-encounter",
            lambda case: case.update(asserted_predicate="interaction"),
            "predicate does not support asserted predicate",
        ),
        (
            "case-correspondence-without-co-presence",
            lambda case: case.update(asserted_predicate="influence"),
            "predicate does not support asserted predicate",
        ),
        (
            "case-posthumous-influence",
            lambda case: case.update(asserted_predicate="causal"),
            "predicate does not support asserted predicate",
        ),
    ],
)
def test_validator_rejects_every_regression_boundary(
    tmp_path: Path, case_id: str, mutation, needle: str
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    mutation(_case(package, case_id))
    _write(root, PACKAGE_REL, package)
    assert any(needle in item for item in validator.validate_repository(root))


def test_promotion_rule_basis_cannot_be_weakened(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["promotion_rules"][3]["required_basis"] = ["supporting evidence"]
    _write(root, PACKAGE_REL, package)
    assert any(
        "promotion boundary interaction -> influence basis drift" in item
        for item in validator.validate_repository(root)
    )


def test_possible_encounter_requires_a_co_presence_signal(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-plausible-workshop")
    borin = _presence(case, "entity-borin")
    borin["spatial_candidates"][0]["place_ref"] = "place-south-city"
    case["co_presence_result"] = "excluded"
    _write(root, PACKAGE_REL, package)
    assert any(
        "possible encounter requires a co-presence signal" in item
        for item in validator.validate_repository(root)
    )


def test_computed_co_presence_never_creates_historical_relation(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-same-city-no-contact")
    case["relation_claim_ref"] = "claim-documented-encounter"
    _write(root, PACKAGE_REL, package)
    assert any(
        "computed co-presence must not create" in item
        for item in validator.validate_repository(root)
    )


def test_validator_rejects_swapped_case_claim_binding(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _case(package, "case-documented-encounter")[
        "relation_claim_ref"
    ] = "claim-interaction-correspondence"
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("Claim target binding mismatch" in item for item in errors)


def test_unreferenced_claim_cannot_expand_the_fixture_silently(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    claim = copy.deepcopy(_claim(package, "claim-possible-workshop"))
    claim.update(id="claim-unbound-inference", target_ref="case-unbound-inference")
    claim["assertion_sha256"] = validator.claim_digest(claim)
    package["claims"].append(claim)
    _write(root, PACKAGE_REL, package)
    assert any(
        "every relation Claim must bind to exactly one fixture case role" in item
        for item in validator.validate_repository(root)
    )


def test_validator_rejects_claim_assertion_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    _claim(package, "claim-influence-posthumous")["qualifiers"][
        "scope"
    ] = "all later work"
    _write(root, PACKAGE_REL, package)
    assert any(
        "assertion digest mismatch" in item
        for item in validator.validate_repository(root)
    )


def test_validator_rejects_locator_digest_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    source = root / "fixtures/world_model/relations/v1/sources/relation-profile.md"
    source.write_text(
        source.read_text(encoding="utf-8").replace("SHA256[c2df", "SHA256[0000", 1),
        encoding="utf-8",
    )
    assert any(
        "locator does not bind" in item for item in validator.validate_repository(root)
    )


def test_possible_encounter_cannot_gain_supporting_evidence_silently(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["evidence_links"].append(copy.deepcopy(package["evidence_links"][0]))
    link = package["evidence_links"][-1]
    link.update(
        id="evidence-possible-workshop",
        claim_id="claim-possible-workshop",
        locator="LOCATOR[claim-documented-encounter]",
    )
    _write(root, PACKAGE_REL, package)
    assert any(
        "non-supported Claim claim-possible-workshop" in item
        for item in validator.validate_repository(root)
    )


def test_interaction_requires_an_explicit_channel(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    claim = _claim(package, "claim-interaction-correspondence")
    claim["qualifiers"].pop("channel")
    claim["assertion_sha256"] = validator.claim_digest(claim)
    _write(root, PACKAGE_REL, package)
    assert any(
        "interaction requires a specific action and channel" in item
        for item in validator.validate_repository(root)
    )


def test_influence_requires_transmission_mode(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    claim = _claim(package, "claim-influence-posthumous")
    claim["qualifiers"].pop("transmission_mode")
    claim["assertion_sha256"] = validator.claim_digest(claim)
    _write(root, PACKAGE_REL, package)
    assert any(
        "influence requires direction, mechanism, scope and transmission mode" in item
        for item in validator.validate_repository(root)
    )


def test_causal_requires_distinct_basis_and_policy(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-process-causal-dependency")
    case["causal_basis_claim_ref"] = "claim-causal-process"
    case["causal_policy_ref"] = None
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("distinct Claim" in item for item in errors)
    assert any("causal policy reference" in item for item in errors)


def test_relation_extent_schema_cannot_drift_from_reviewed_330(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    schema_path = Path("fixtures/world_model/relations/v1/schema.json")
    schema = _load(root, schema_path)
    schema["$defs"]["bound"]["properties"]["precision"]["enum"].append("hour")
    _write(root, schema_path, schema)
    assert any(
        "must consume the reviewed #330 bound definition exactly" in item
        for item in validator.validate_repository(root)
    )


def test_extent_candidate_requires_reviewed_330_profile_ref(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-same-city-no-contact")
    case["presence_extents"][0]["temporal_candidates"][0][
        "semantic_profile_refs"
    ] = ["claim-named-place"]
    _write(root, PACKAGE_REL, package)
    assert any(
        "must bind to a reviewed #330 temporal semantic profile" in item
        for item in validator.validate_repository(root)
    )


def test_spatial_projection_policy_cannot_hide_uncertainty(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-inferred-route-proximity")
    _presence(case, "entity-ada")["spatial_candidates"][0][
        "projection_policy"
    ] = "show_exact"
    _write(root, PACKAGE_REL, package)
    assert any(
        "inferred_corridor requires projection_policy show_inferred_geometry" in item
        for item in validator.validate_repository(root)
    )


def test_presence_uncertainty_binding_cannot_be_dropped(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-inferred-route-proximity")
    _presence(case, "entity-ada")["uncertainty_refs"] = []
    _write(root, PACKAGE_REL, package)
    assert any(
        "presence presence-route-ada uncertainty binding mismatch" in item
        for item in validator.validate_repository(root)
    )


def test_alternative_order_does_not_select_a_first_winner() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = copy.deepcopy(_case(package, "case-ambiguous-court"))
    parents = {
        item["child_ref"]: item["parent_ref"] for item in package["place_hierarchy"]
    }
    assert validator.co_presence_state(case, parents) == "possible"
    _presence(case, "entity-ada")["temporal_candidates"].reverse()
    assert validator.co_presence_state(case, parents) == "possible"


def test_ui_language_rules_are_executable(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["ui_language_rules"][0]["required_label_template"] = "Same place and time"
    _write(root, PACKAGE_REL, package)
    assert any(
        "UI rule co_present required_label_template drift" in item
        for item in validator.validate_repository(root)
    )


def test_ui_language_rules_require_unique_complete_coverage(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["ui_language_rules"][1]["predicate"] = "co_present"
    _write(root, PACKAGE_REL, package)
    assert any(
        "UI language rules must uniquely cover" in item
        for item in validator.validate_repository(root)
    )


def test_classification_and_similarity_never_create_relation(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["non_relation_cases"][0]["creates_relation"] = True
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any(
        "classification and Similarity" in item or "False was expected" in item
        for item in errors
    )


def test_legacy_influence_cannot_be_accepted_by_compatibility(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["influenced"]["relation_predicate"] = "influence"
    _write(root, COMPAT_REL, compatibility)
    assert any(
        "legacy influenced must remain unresolved" in item
        for item in validator.validate_repository(root)
    )


def test_compatibility_envelope_rejects_hidden_fields(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    compatibility = _load(root, COMPAT_REL)
    compatibility["influenced"]["confidence"] = "high"
    _write(root, COMPAT_REL, compatibility)
    assert any(
        "legacy influenced must remain unresolved" in item
        for item in validator.validate_repository(root)
    )


def test_validator_rejects_base_package_binding_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["base_packages"][1]["reviewed_content_sha256"] = "0" * 64
    _write(root, PACKAGE_REL, package)
    assert any(
        "base package binding mismatch" in item
        for item in validator.validate_repository(root)
    )


def test_ready_transition_validates(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    assert validator.validate_repository(root, require_ready=True) == []


def test_ready_rejects_current_semantic_drift(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    package = _load(root, PACKAGE_REL)
    package["relation_predicates"][0][
        "definition"
    ] = "Drifted after review and no longer trustworthy."
    _write(root, PACKAGE_REL, package)
    assert any(
        "digest" in item
        for item in validator.validate_repository(root, require_ready=True)
    )


def test_review_digest_normalizes_only_ready_transition_metadata(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    before = validator.compute_review_digest(root)
    package = _load(root, PACKAGE_REL)
    package["status"] = "READY"
    package["record_time"]["reviewed_at"] = "2026-08-05T14:00:00Z"
    _write(root, PACKAGE_REL, package)
    for relative in (README_REL, OWNER_REL):
        path = root / relative
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Status: `REVIEW_REQUIRED`", "Status: `READY`", 1
            ),
            encoding="utf-8",
        )
    work = root / WORK_REL
    text = work.read_text(encoding="utf-8")
    text = text.replace("- State: `REVIEW_REQUIRED`.", "- State: `READY`.", 1)
    text = text.replace("- Frozen commit: `PENDING`.", "- Frozen commit: `1" + "0" * 39 + "`.", 1)
    text = text.replace("- Reviewed digest: `PENDING`.", "- Reviewed digest: `" + "0" * 64 + "`.", 1)
    text = text.replace(
        "- Reviews: `PENDING`.",
        "- Reviews: `semantic-model` and `validator-integrity` READY.",
        1,
    )
    work.write_text(text, encoding="utf-8")
    assert validator.compute_review_digest(root) == before


def test_strict_json_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text(
        '{"status":"READY","status":"REVIEW_REQUIRED"}', encoding="utf-8"
    )
    with pytest.raises(validator.DuplicateKeyError):
        validator.load_json(path)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_strict_json_loader_rejects_non_finite_numbers(
    tmp_path: Path, constant: str
) -> None:
    path = tmp_path / "non-finite.json"
    path.write_text(f'{{"value":{constant}}}', encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite"):
        validator.load_json(path)


def test_base_dependencies_cannot_duplicate_329_and_drop_330(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["base_packages"][1] = copy.deepcopy(package["base_packages"][0])
    _write(root, PACKAGE_REL, package)
    assert any(
        "exactly bind reviewed #329 and #330" in item
        for item in validator.validate_repository(root)
    )


def test_background_evidence_cannot_support_documented_predicate(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    link = next(
        item
        for item in package["evidence_links"]
        if item["id"] == "evidence-documented-encounter"
    )
    link["evidence_strength"] = "background"
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("requires reviewed supporting evidence" in item for item in errors)
    assert any("requires a supporting locator" in item for item in errors)


def test_causal_basis_must_bind_the_same_endpoints(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    basis = _claim(package, "claim-causal-process-basis")
    basis["subject_ref"] = "entity-unrelated-a"
    basis["object_ref"] = "entity-unrelated-b"
    _refresh_claim_locator(root, package, basis["id"])
    _write(root, PACKAGE_REL, package)
    assert any(
        "causal basis binding mismatch" in item
        for item in validator.validate_repository(root)
    )


def test_causal_policy_must_resolve_to_checked_artifact(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["causal_policies"][0]["sha256"] = "0" * 64
    _write(root, PACKAGE_REL, package)
    assert any(
        "causal policy checksum drift" in item
        for item in validator.validate_repository(root)
    )


def test_polygon_hole_excludes_point_from_corridor() -> None:
    package = _load(ROOT, PACKAGE_REL)
    case = copy.deepcopy(_case(package, "case-inferred-route-proximity"))
    corridor = _presence(case, "entity-ada")["spatial_candidates"][0]
    corridor["geometry"]["coordinates"].append(
        [[10.4, 50.4], [10.6, 50.4], [10.6, 50.6], [10.4, 50.6], [10.4, 50.4]]
    )
    parents = {
        item["child_ref"]: item["parent_ref"] for item in package["place_hierarchy"]
    }
    assert validator.co_presence_state(case, parents) == "excluded"


def test_polygon_handles_antimeridian_and_boundaries() -> None:
    polygon = [
        [[170.0, -10.0], [-170.0, -10.0], [-170.0, 10.0], [170.0, 10.0], [170.0, -10.0]]
    ]
    assert validator._point_in_polygon((179.0, 0.0), polygon)
    assert validator._point_in_polygon((-179.0, 0.0), polygon)
    assert not validator._point_in_polygon((0.0, 0.0), polygon)
    assert validator._point_in_polygon((170.0, 0.0), polygon)


def test_missing_presence_endpoint_fails_closed_without_crash(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-same-city-no-contact")
    case["presence_extents"][1]["entity_ref"] = "entity-unrelated"
    _write(root, PACKAGE_REL, package)
    errors = validator.validate_repository(root)
    assert any("must bind exactly one extent to each endpoint" in item for item in errors)
    assert any("presence extents must bind both case endpoints" in item for item in errors)


def test_no_relation_asserted_does_not_claim_historical_absence(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    case = _case(package, "case-disjoint-place")
    _presence(case, "entity-cira")["spatial_candidates"][0]["place_ref"] = "place-north-city"
    case["co_presence_result"] = "confirmed"
    _write(root, PACKAGE_REL, package)
    assert validator.validate_repository(root) == []


def test_ui_requires_overlap_status_and_uncertainty_disclosures(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["ui_language_rules"][0]["required_disclosures"] = ["extent_uncertainty"]
    _write(root, PACKAGE_REL, package)
    assert any(
        "required_disclosures drift" in item
        for item in validator.validate_repository(root)
    )


def test_source_path_cannot_escape_repository(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    package = _load(root, PACKAGE_REL)
    package["sources"][0]["path"] = "../../outside.md"
    _write(root, PACKAGE_REL, package)
    assert any(
        "source file load failed" in item and "canonical and relative" in item
        for item in validator.validate_repository(root)
    )


def test_ready_rejects_opaque_review_artifact(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _prepare_ready(root)
    registry = _load(root, REGISTRY_REL)
    artifact_relative = Path(registry["reviews"][0]["artifact"])
    _write(root, artifact_relative, {})
    registry["reviews"][0]["artifact_sha256"] = hashlib.sha256(
        (root / artifact_relative).read_bytes()
    ).hexdigest()
    _write(root, REGISTRY_REL, registry)
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "mutate review artifact")
    assert any(
        "review artifact/registry semantic drift" in item
        for item in validator.validate_repository(root, require_ready=True)
    )


def test_ready_digest_must_describe_frozen_commit_tree(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    frozen, old_digest = _prepare_ready(root)
    source = root / "fixtures/world_model/relations/v1/sources/relation-profile.md"
    source.write_text(source.read_text(encoding="utf-8") + "\nReviewed-scope mutation.\n", encoding="utf-8")
    new_digest = validator.compute_review_digest(root)
    assert new_digest != old_digest

    registry = _load(root, REGISTRY_REL)
    registry["reviewed_content_sha256"] = new_digest
    for review in registry["reviews"]:
        review["reviewed_content_sha256"] = new_digest
        artifact = {
            "artifact_format": "artemis-review-attestation-v1",
            **{
                key: review[key]
                for key in validator.REVIEW_FIELDS
                if key not in {"artifact", "artifact_sha256"}
            },
        }
        artifact_relative = Path(review["artifact"])
        _write(root, artifact_relative, artifact)
        review["artifact_sha256"] = hashlib.sha256(
            (root / artifact_relative).read_bytes()
        ).hexdigest()
    _write(root, REGISTRY_REL, registry)
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "retarget digest without moving frozen commit")

    errors = validator.validate_repository(root, require_ready=True)
    assert any("frozen commit does not contain" in item for item in errors)
    assert registry["frozen_commit"] == frozen
