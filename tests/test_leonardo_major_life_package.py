import copy
import json

import pytest

import scripts.validate_leonardo_major_life_package as validator
from scripts.validate_leonardo_major_life_package import (
    PACKAGE_PATH,
    MajorLifePackageError,
    validate_package,
)


def _package():
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def _empty_suffix_package():
    package = _package()
    package["audit"]["prior_reviews"] = package["audit"]["prior_reviews"][:9]
    package["audit"]["canonical_review_status"] = "pending_independent_rereview"
    package["audit"]["current_decision"] = None
    return package


def _review_row(round_number, track, decision, *, major=0, medium=0):
    return {
        "round": round_number,
        "track": track,
        "reviewed_head": "f" * 40,
        "review_envelope_digest_sha256": "d" * 64,
        "decision": decision,
        "independence_method": "separate_agent_task_read_only",
        "review_record_locator": (
            "https://github.com/omegapunctum/ARTEMIS/pull/400"
            f"#issuecomment-{6000000000 + round_number}"
        ),
        "review_record_authentication": "reference_only_not_verified_by_validator",
        "unresolved_major": major,
        "unresolved_medium": medium,
        "duration_minutes": None,
        "measurement_state": "not_captured_do_not_estimate",
        "artifact_ref": (
            "fixtures/world_slices/leonardo_major_life/v1/reviews/"
            f"round-{round_number}-{track.replace('_', '-')}.json"
        ),
    }


def test_source_audited_candidate_package_passes_fail_closed_validation() -> None:
    assert validate_package() == {
        "package_id": "leonardo-major-life-presence-candidates-v1",
        "status": "CANDIDATE_SOURCE_AUDITED",
        "place_count": 5,
        "macro_period_count": 6,
        "new_presence_count": 7,
        "referenced_romagna_presence_count": 4,
        "composed_anchor_count": 11,
        "new_unknown_transition_count": 7,
        "source_count": 11,
        "claim_count": 28,
        "evidence_link_count": 35,
        "uncertainty_count": 8,
        "runtime_authorized": False,
        "canonical_review_status": "independent_review_complete",
        "current_decision": "FREEZE_FOR_REVIEW",
        "prior_review_decisions": [
            "NARROW", "NARROW", "NARROW", "NARROW", "NARROW",
            "FREEZE_FOR_REVIEW", "NARROW", "FREEZE_FOR_REVIEW", "NARROW",
            "FREEZE_FOR_REVIEW", "FREEZE_FOR_REVIEW",
        ],
    }


def test_candidate_package_cannot_authorize_runtime() -> None:
    package = _package()
    package["runtime_authorized"] = True

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_presence_cannot_gain_unreviewed_geometry() -> None:
    package = _package()
    package["presences"][0]["geometry"] = {
        "type": "Point",
        "coordinates": [10.923, 43.787],
    }

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_presence_must_resolve_to_a_named_place_identity() -> None:
    package = _package()
    package["presences"][0]["place_ref"] = "place-does-not-exist"

    with pytest.raises(MajorLifePackageError, match="missing Place"):
        validate_package(package)


def test_place_cannot_gain_unreviewed_geometry() -> None:
    package = _package()
    package["places"][0]["geometry"] = {
        "type": "Point",
        "coordinates": [10.923, 43.787],
    }

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_unknown_transition_cannot_gain_line_or_route_evidence() -> None:
    package = _package()
    transition = package["transitions"][0]
    transition["source_refs"] = ["source-museo-leonardiano-places"]

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_florence_year_precision_cannot_be_inflated_to_day() -> None:
    package = _package()
    presence = next(
        row
        for row in package["presences"]
        if row["presence_id"] == "presence-leonardo-florence-st-luke-1472"
    )
    presence["temporal"].update(
        {"start": "1472-01-01", "end": "1472-01-01", "precision": "day"}
    )

    with pytest.raises(MajorLifePackageError, match="temporal precision drifted"):
        validate_package(package)


def test_romagna_segment_must_remain_an_identity_preserving_reference() -> None:
    package = _package()
    external = package["trajectory"]["external_segments"][0]
    external["identity_policy"] = "copied_into_major_life_package"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_evidence_link_must_resolve_to_registered_source() -> None:
    package = _package()
    package["evidence_links"][0]["source_id"] = "source-does-not-exist"

    with pytest.raises(MajorLifePackageError, match="missing Source"):
        validate_package(package)


def test_evidence_link_cannot_escape_its_atomic_claim() -> None:
    package = _package()
    package["evidence_links"][0]["claim_id"] = package["claims"][1]["claim_id"]

    with pytest.raises(MajorLifePackageError, match="escaped its atomic Claim"):
        validate_package(package)


def test_macro_period_cannot_become_world_model_entity() -> None:
    package = _package()
    package["macro_periods"][0]["presentation_only"] = False

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_candidate_package_cannot_self_assert_canonical_review() -> None:
    package = _package()
    package["audit"]["canonical_review_status"] = "ready"
    package["audit"]["current_decision"] = "FREEZE_FOR_REVIEW"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_historical_drive_cost_cannot_be_retroactively_estimated() -> None:
    package = _package()
    package["audit"]["curation_cost"]["duration_minutes"] = 30

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_missing_presence_uncertainty_is_rejected() -> None:
    package = _package()
    target = package["presences"][0]["uncertainty_refs"][0]
    package["uncertainties"] = [
        row for row in package["uncertainties"] if row["uncertainty_id"] != target
    ]

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_transition_topology_cannot_be_redirected() -> None:
    package = _package()
    package["transitions"][0]["to_ref"] = "presence-leonardo-milan-altarpiece-contract-1483"

    with pytest.raises(MajorLifePackageError, match="transition topology drifted"):
        validate_package(package)


def test_presence_cannot_belong_to_two_macro_periods() -> None:
    package = _package()
    package["macro_periods"][1]["presence_refs"].append(
        "presence-leonardo-vinci-birth-1452"
    )

    with pytest.raises(MajorLifePackageError, match="membership or order drifted"):
        validate_package(package)


def test_presence_cannot_own_another_presence_claim() -> None:
    package = _package()
    package["presences"][0]["claim_refs"][0] = package["presences"][1]["claim_refs"][0]

    with pytest.raises(MajorLifePackageError, match="four atomic Claims"):
        validate_package(package)


def test_place_claim_ownership_must_be_complete() -> None:
    package = _package()
    florence = next(row for row in package["places"] if row["place_id"] == "place-florence")
    florence["claim_refs"].pop()

    with pytest.raises(MajorLifePackageError, match="Claim ownership is incomplete"):
        validate_package(package)


def test_every_material_claim_requires_supporting_evidence() -> None:
    package = _package()
    claim_id = package["claims"][0]["claim_id"]
    for link in package["evidence_links"]:
        if link["claim_id"] == claim_id:
            link["relation_to_claim"] = "contextualizes"
            link["evidence_strength"] = "background"

    with pytest.raises(MajorLifePackageError, match="no supporting EvidenceLink"):
        validate_package(package)


def test_orphan_source_is_rejected() -> None:
    package = _package()
    orphan = copy.deepcopy(package["sources"][0])
    orphan["source_id"] = "source-orphan"
    package["sources"].append(orphan)

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_source_native_temporal_token_cannot_drift() -> None:
    package = _package()
    package["presences"][0]["temporal"]["source_native"] = "1452"

    with pytest.raises(MajorLifePackageError, match="temporal precision drifted"):
        validate_package(package)


def test_frozen_romagna_review_identity_cannot_drift() -> None:
    package = _package()
    package["trajectory"]["external_segments"][0]["reviewed_content_digest"] = "0" * 64

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_uncertainty_target_must_register_the_uncertainty_reciprocally() -> None:
    package = _package()
    package["uncertainties"][0]["target_refs"] = [
        "presence-leonardo-florence-st-luke-1472"
    ]

    with pytest.raises(MajorLifePackageError, match="not reciprocally registered"):
        validate_package(package)


def test_coordinated_source_identity_rename_is_rejected() -> None:
    package = _package()
    old_id = package["sources"][0]["source_id"]
    new_id = "source-coordinated-rename"
    package["sources"][0]["source_id"] = new_id
    for link in package["evidence_links"]:
        if link["source_id"] == old_id:
            link["source_id"] = new_id

    with pytest.raises(MajorLifePackageError, match="Source identity set drifted"):
        validate_package(package)


def test_coordinated_evidence_identity_rename_is_rejected() -> None:
    package = _package()
    old_id = package["evidence_links"][0]["evidence_link_id"]
    new_id = "evidence-coordinated-rename"
    package["evidence_links"][0]["evidence_link_id"] = new_id
    for claim in package["claims"]:
        claim["evidence_link_refs"] = [
            new_id if ref == old_id else ref for ref in claim["evidence_link_refs"]
        ]

    with pytest.raises(MajorLifePackageError, match="EvidenceLink identity set drifted"):
        validate_package(package)


def test_coordinated_uncertainty_identity_rename_is_rejected() -> None:
    package = _package()
    old_id = package["uncertainties"][0]["uncertainty_id"]
    new_id = "uncertainty-coordinated-rename"
    package["uncertainties"][0]["uncertainty_id"] = new_id
    for presence in package["presences"]:
        presence["uncertainty_refs"] = [
            new_id if ref == old_id else ref for ref in presence["uncertainty_refs"]
        ]
    for claim in package["claims"]:
        claim["uncertainty_refs"] = [
            new_id if ref == old_id else ref for ref in claim["uncertainty_refs"]
        ]

    with pytest.raises(MajorLifePackageError, match="Uncertainty identity set drifted"):
        validate_package(package)


def test_presence_interval_cannot_become_exclusive() -> None:
    package = _package()
    package["presences"][0]["temporal"]["start_inclusive"] = False

    with pytest.raises(MajorLifePackageError, match="temporal bounds must remain inclusive"):
        validate_package(package)


def test_possible_bounds_cannot_be_inverted() -> None:
    package = _package()
    uncertainty = next(
        row for row in package["uncertainties"]
        if row["uncertainty_id"] == "uncertainty-amboise-continuous-position"
    )
    uncertainty["possible_bounds"]["not_before"] = "1516-12"

    with pytest.raises(MajorLifePackageError, match="inverted bounds"):
        validate_package(package)


def test_possible_bounds_cannot_escape_target_presence() -> None:
    package = _package()
    uncertainty = next(
        row for row in package["uncertainties"]
        if row["uncertainty_id"] == "uncertainty-amboise-continuous-position"
    )
    uncertainty["possible_bounds"]["not_before"] = "1516-08"

    with pytest.raises(MajorLifePackageError, match="starts outside its target"):
        validate_package(package)


def test_presence_cannot_register_foreign_uncertainty() -> None:
    package = _package()
    package["presences"][0]["uncertainty_refs"].append(
        "uncertainty-florence-1472-address"
    )

    with pytest.raises(MajorLifePackageError, match="reviewed semantic profile drifted"):
        validate_package(package)


def test_claim_cannot_register_foreign_uncertainty() -> None:
    package = _package()
    package["claims"][0]["uncertainty_refs"].append(
        "uncertainty-florence-1472-address"
    )

    with pytest.raises(MajorLifePackageError, match="reviewed Uncertainty ownership drifted"):
        validate_package(package)


def test_extent_semantics_cannot_drift() -> None:
    package = _package()
    package["presences"][0]["temporal"]["extent_semantics"] = "documentary_context_anchor"

    with pytest.raises(MajorLifePackageError, match="reviewed semantic profile drifted"):
        validate_package(package)


def test_spatial_precision_cannot_drift() -> None:
    package = _package()
    package["presences"][0]["spatial_precision"] = "named_city"

    with pytest.raises(MajorLifePackageError, match="reviewed semantic profile drifted"):
        validate_package(package)


def test_frozen_romagna_gap_semantics_cannot_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    original_load = validator._load
    selection_path = (
        validator.ROOT
        / "fixtures"
        / "world_slices"
        / "leonardo_romagna_1502"
        / "v1"
        / "selection_manifest.json"
    )
    corrupted_selection = original_load(selection_path)
    trajectory = next(
        row for row in corrupted_selection["candidate_objects"]
        if row.get("object_id") == "trajectory-leonardo-romagna-1502"
    )
    gap = next(row for row in trajectory["segments"] if row["segment_kind"] == "inferred_gap")
    gap["spatial_mode"] = "documented_path"

    def fake_load(path):
        if path == selection_path:
            return corrupted_selection
        return original_load(path)

    monkeypatch.setattr(validator, "_load", fake_load)
    with pytest.raises(MajorLifePackageError, match="segment and gap semantics drifted"):
        validate_package(_package())


def test_reviewed_claim_statement_cannot_be_substituted() -> None:
    package = _package()
    package["claims"][0]["statement"] = "A false unrelated statement about another person."

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_reviewed_source_url_and_locator_cannot_be_substituted() -> None:
    package = _package()
    package["sources"][0]["url"] = "https://example.com/unrelated"
    package["sources"][0]["locator"] = "An unrelated locator with enough characters."

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_reviewed_evidence_locator_cannot_be_substituted() -> None:
    package = _package()
    package["evidence_links"][0]["locator"] = "A fabricated but structurally valid locator."

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_reviewed_place_payload_cannot_be_coordinately_substituted() -> None:
    package = _package()
    place = package["places"][0]
    presence = next(row for row in package["presences"] if row["place_ref"] == place["place_id"])
    place["label"] = "Atlantis"
    place["place_kind"] = "city"
    presence["place_label"] = "Atlantis"

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_reviewed_presence_labels_and_rationale_cannot_be_substituted() -> None:
    package = _package()
    package["presences"][0]["activity_label"] = "Fabricated activity"
    package["presences"][0]["selection_rationale"] = "Fabricated rationale"

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_reviewed_uncertainty_description_and_effect_cannot_be_substituted() -> None:
    package = _package()
    package["uncertainties"][0]["description"] = "Exact geometry is fully known."
    package["uncertainties"][0]["effect"] = "Render an exact coordinate."

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_uncertainty_requires_canonical_review_state() -> None:
    package = _package()
    package["uncertainties"][0]["review_state"] = "candidate_source_audited"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_review_history_accepts_a_complete_append_only_round(monkeypatch) -> None:
    package = _package()
    monkeypatch.setattr(validator, "_validate_appended_review_artifact", lambda *_args: None)
    monkeypatch.setattr(
        validator,
        "_review_history_append_commits",
        lambda _rows: {6: ("a" * 40, "f" * 40), 7: ("b" * 40, "f" * 40)},
    )
    package["audit"]["prior_reviews"].extend(
        [
            _review_row(7, "semantic_content", "FREEZE_FOR_REVIEW"),
            _review_row(7, "validator_integrity", "NARROW", major=1),
        ]
    )
    package["audit"]["canonical_review_status"] = "pending_independent_rereview"
    package["audit"]["current_decision"] = None

    summary = validate_package(package)
    assert summary["canonical_review_status"] == "pending_independent_rereview"
    assert summary["prior_review_decisions"][-2:] == ["FREEZE_FOR_REVIEW", "NARROW"]


def test_immutable_review_prefix_cannot_be_rewritten() -> None:
    package = _package()
    package["audit"]["prior_reviews"][0]["decision"] = "STOP"

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_recorded_round_four_cannot_be_deleted() -> None:
    package = _package()
    del package["audit"]["prior_reviews"][5:7]

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


def test_recorded_round_four_cannot_be_rewritten_as_freeze() -> None:
    package = _package()
    validator_row = package["audit"]["prior_reviews"][6]
    validator_row["decision"] = "FREEZE_FOR_REVIEW"
    validator_row["unresolved_major"] = 0

    with pytest.raises(MajorLifePackageError, match="schema validation failed"):
        validate_package(package)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("research_workspace", "Unrelated workspace"),
        ("research_artifacts", ["Unrelated artifact A", "Unrelated artifact B"]),
    ],
)
def test_immutable_research_provenance_is_digest_locked(field, replacement) -> None:
    package = _package()
    package["audit"][field] = replacement

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_immutable_curation_note_is_digest_locked() -> None:
    package = _package()
    package["audit"]["curation_cost"]["note"] = "Rewritten provenance note."

    with pytest.raises(MajorLifePackageError, match="reviewed semantic content drifted"):
        validate_package(package)


def test_positive_decision_only_descendant_does_not_resign_content() -> None:
    package = _package()
    original_digest = package["candidate_content_digest_sha256"]

    summary = validate_package(package)
    assert package["candidate_content_digest_sha256"] == original_digest
    assert summary["current_decision"] == "FREEZE_FOR_REVIEW"


def test_appended_rounds_cannot_be_physically_interleaved(monkeypatch) -> None:
    package = _package()
    monkeypatch.setattr(validator, "_validate_appended_review_artifact", lambda *_args: None)
    monkeypatch.setattr(
        validator,
        "_review_history_append_commits",
        lambda _rows: {
            6: ("a" * 40, "f" * 40),
            7: ("b" * 40, "f" * 40),
            8: ("c" * 40, "f" * 40),
        },
    )
    package["audit"]["prior_reviews"].extend(
        [
            _review_row(7, "semantic_content", "FREEZE_FOR_REVIEW"),
            _review_row(8, "semantic_content", "FREEZE_FOR_REVIEW"),
            _review_row(7, "validator_integrity", "FREEZE_FOR_REVIEW"),
            _review_row(8, "validator_integrity", "FREEZE_FOR_REVIEW"),
        ]
    )

    with pytest.raises(MajorLifePackageError, match="contiguous adjacent pairs"):
        validate_package(package)


def test_fabricated_reviewed_head_cannot_authorize_freeze(monkeypatch) -> None:
    package = _package()
    row = _review_row(7, "semantic_content", "FREEZE_FOR_REVIEW")

    with pytest.raises(MajorLifePackageError, match="review head cannot be verified"):
        validator._validate_appended_review_artifact(
            row, package["candidate_content_digest_sha256"], "a" * 40, "e" * 40
        )


def test_review_artifact_binds_exact_row_and_candidate_digest(monkeypatch) -> None:
    package = _package()
    row = _review_row(6, "semantic_content", "FREEZE_FOR_REVIEW")
    digest = package["candidate_content_digest_sha256"]
    artifact = {
        "schema_version": "1.0.0",
        "package_id": package["package_id"],
        "candidate_content_digest_sha256": digest,
        "review_envelope_digest_sha256": row["review_envelope_digest_sha256"],
        "review": {key: value for key, value in row.items() if key != "artifact_ref"},
        "review_record_locator": row["review_record_locator"],
        "review_record_authentication": "reference_only_not_verified_by_validator",
    }

    def fake_git(*args):
        if args[:2] == ("rev-parse", "--verify"):
            return row["reviewed_head"]
        if args == ("rev-parse", "HEAD"):
            return "e" * 40
        if args[0] == "rev-parse" and ":" in args[1]:
            return "b" * 40
        if args[0] == "merge-base":
            return ""
        if args[0] == "rev-list":
            return ""
        if args[0] == "show":
            return json.dumps(artifact)
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    monkeypatch.setattr(
        validator,
        "_review_envelope_digest",
        lambda _head: (row["review_envelope_digest_sha256"], digest),
    )
    validator._validate_appended_review_artifact(row, digest, "a" * 40, "f" * 40)


def test_freeze_decision_requires_two_positive_latest_tracks(monkeypatch) -> None:
    package = _package()
    package["audit"]["prior_reviews"][-1]["decision"] = "NARROW"
    package["audit"]["prior_reviews"][-1]["unresolved_major"] = 1
    monkeypatch.setattr(validator, "_validate_appended_review_artifact", lambda *_args: None)
    monkeypatch.setattr(
        validator,
        "_review_history_append_commits",
        lambda _rows: {6: ("a" * 40, "f" * 40)},
    )

    with pytest.raises(MajorLifePackageError, match="two positive latest tracks"):
        validate_package(package)


def test_review_suffix_cannot_be_deleted_after_its_append(monkeypatch) -> None:
    base = _empty_suffix_package()
    appended = copy.deepcopy(base)
    appended["audit"]["prior_reviews"].extend(
        [
            _review_row(6, "semantic_content", "FREEZE_FOR_REVIEW"),
            _review_row(6, "validator_integrity", "NARROW", major=1),
        ]
    )
    deleted = copy.deepcopy(base)
    commits = ["1" * 40, "2" * 40, "3" * 40]
    packages = {
        commits[0]: base,
        commits[1]: appended,
        commits[2]: deleted,
    }
    for row in appended["audit"]["prior_reviews"][-2:]:
        row["reviewed_head"] = commits[0]

    def fake_git(*args):
        if args[:4] == ("rev-list", "--first-parent", "--reverse", "HEAD"):
            return "\n".join(commits)
        if args[0] == "show":
            commit = args[1].split(":", 1)[0]
            return json.dumps(packages[commit])
        if args[0] == "rev-parse" and args[1].endswith("^1"):
            commit = args[1][:-2]
            return commits[commits.index(commit) - 1]
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    with pytest.raises(MajorLifePackageError, match="deleted, rewritten"):
        validator._review_history_append_commits(deleted["audit"]["prior_reviews"])


def test_historical_candidate_digest_is_recomputed(monkeypatch) -> None:
    package = _package()
    package["presences"][0]["activity_label"] = "Fabricated historical content"
    schema = json.loads(validator.SCHEMA_PATH.read_text(encoding="utf-8"))

    def fake_git(*args):
        path = args[1].split(":", 1)[1]
        if path == validator.PACKAGE_RELATIVE:
            return json.dumps(package)
        if path == validator.SCHEMA_RELATIVE:
            return json.dumps(schema)
        if path == validator.VALIDATOR_RELATIVE:
            return "validator source"
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    with pytest.raises(MajorLifePackageError, match="does not match its content"):
        validator._review_envelope_digest("a" * 40)


def test_transient_prefix_drift_cannot_hide_an_earlier_suffix_append(monkeypatch) -> None:
    base = _empty_suffix_package()
    hidden_append = copy.deepcopy(base)
    hidden_append["audit"]["prior_reviews"][0]["decision"] = "STOP"
    hidden_append["audit"]["prior_reviews"].extend(
        [
            _review_row(6, "semantic_content", "FREEZE_FOR_REVIEW"),
            _review_row(6, "validator_integrity", "FREEZE_FOR_REVIEW"),
        ]
    )
    restored = copy.deepcopy(hidden_append)
    restored["audit"]["prior_reviews"][0] = copy.deepcopy(
        base["audit"]["prior_reviews"][0]
    )
    commits = ["a" * 40, "b" * 40, "c" * 40]
    for row in hidden_append["audit"]["prior_reviews"][-2:]:
        row["reviewed_head"] = commits[1]
    for row in restored["audit"]["prior_reviews"][-2:]:
        row["reviewed_head"] = commits[1]
    packages = {
        commits[0]: base,
        commits[1]: hidden_append,
        commits[2]: restored,
    }

    def fake_git(*args):
        if args[:4] == ("rev-list", "--first-parent", "--reverse", "HEAD"):
            return "\n".join(commits)
        if args[0] == "show":
            commit = args[1].split(":", 1)[0]
            return json.dumps(packages[commit])
        if args[0] == "rev-parse" and args[1].endswith("^1"):
            commit = args[1][:-2]
            return commits[commits.index(commit) - 1]
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    with pytest.raises(MajorLifePackageError, match="prefix changed after the Git baseline"):
        validator._review_history_append_commits(restored["audit"]["prior_reviews"])


def test_unreadable_package_cannot_be_skipped_after_history_baseline(monkeypatch) -> None:
    package = _empty_suffix_package()
    commits = ["a" * 40, "b" * 40, "c" * 40]

    def fake_git(*args):
        if args[:4] == ("rev-list", "--first-parent", "--reverse", "HEAD"):
            return "\n".join(commits)
        if args[0] == "show":
            commit = args[1].split(":", 1)[0]
            if commit == commits[1]:
                return "{not-json"
            return json.dumps(package)
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    with pytest.raises(MajorLifePackageError, match="unreadable after the Git baseline"):
        validator._review_history_append_commits(package["audit"]["prior_reviews"])


def test_review_artifact_cannot_change_and_then_be_restored(monkeypatch) -> None:
    package = _package()
    row = _review_row(6, "semantic_content", "FREEZE_FOR_REVIEW")
    digest = package["candidate_content_digest_sha256"]
    artifact = {
        "schema_version": "1.0.0",
        "package_id": package["package_id"],
        "candidate_content_digest_sha256": digest,
        "review_envelope_digest_sha256": row["review_envelope_digest_sha256"],
        "review": {key: value for key, value in row.items() if key != "artifact_ref"},
        "review_record_locator": row["review_record_locator"],
        "review_record_authentication": "reference_only_not_verified_by_validator",
    }
    append_commit = "a" * 40
    later_commit = "c" * 40

    def fake_git(*args):
        if args[:2] == ("rev-parse", "--verify"):
            return row["reviewed_head"]
        if args == ("rev-parse", "HEAD"):
            return "e" * 40
        if args[0] == "merge-base":
            return ""
        if args[0] == "rev-list":
            return later_commit
        if args[0] == "rev-parse" and args[1].startswith(later_commit + ":"):
            return "d" * 40
        if args[0] == "rev-parse" and ":" in args[1]:
            return "b" * 40
        if args[0] == "show":
            return json.dumps(artifact)
        raise AssertionError(args)

    monkeypatch.setattr(validator, "_git", fake_git)
    monkeypatch.setattr(
        validator,
        "_review_envelope_digest",
        lambda _head: (row["review_envelope_digest_sha256"], digest),
    )
    with pytest.raises(MajorLifePackageError, match="changed in later Git history"):
        validator._validate_appended_review_artifact(
            row, digest, append_commit, row["reviewed_head"]
        )
