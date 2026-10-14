from __future__ import annotations

import pytest

from scripts.validate_ci_evidence_history import (
    EvidenceHistoryError,
    EXTERNAL_MANIFEST,
    EXTERNAL_REPOSITORY,
    EXTERNAL_COMMIT,
    fixture_document_refs,
    collect_commit_refs,
    fixture_commit_refs,
)


def test_fixture_commit_refs_are_complete_sha1_values() -> None:
    refs = fixture_commit_refs()
    assert len(refs) >= 20
    assert all(len(value) == 40 for value in refs)


def test_commit_ref_collection_rejects_malformed_values() -> None:
    with pytest.raises(EvidenceHistoryError, match="invalid commit reference"):
        collect_commit_refs({"frozen_commit": "shallow-placeholder"})


def test_commit_ref_collection_ignores_non_commit_hashes() -> None:
    assert collect_commit_refs({"frozen_tree": "a" * 40, "sha256": "b" * 64}) == set()


def test_external_source_commit_is_not_local_evidence() -> None:
    refs = fixture_commit_refs()
    assert EXTERNAL_COMMIT not in refs
    assert "957899ee241f6e0c3af66dd4d91b964db1c3824b" in refs


@pytest.mark.parametrize("field,value", [("repository", "https://example.com/repo"),
                                         ("commit", "a" * 40), ("commit", "bad")])
def test_external_binding_cannot_drift(field, value) -> None:
    manifest = {"repository": EXTERNAL_REPOSITORY, "commit": EXTERNAL_COMMIT}
    manifest[field] = value
    with pytest.raises(EvidenceHistoryError, match="binding mismatch"):
        fixture_document_refs(EXTERNAL_MANIFEST, manifest)


def test_external_binding_excludes_only_top_level_commit() -> None:
    manifest = {"repository": EXTERNAL_REPOSITORY, "commit": EXTERNAL_COMMIT,
                "nested": {"frozen_commit": "a" * 40}, "review_commit": "b" * 40}
    assert fixture_document_refs(EXTERNAL_MANIFEST, manifest) == {"a" * 40, "b" * 40}
    manifest["nested"]["frozen_commit"] = "bad"
    with pytest.raises(EvidenceHistoryError, match="invalid commit"):
        fixture_document_refs(EXTERNAL_MANIFEST, manifest)


def test_unknown_repository_does_not_bypass_local_history() -> None:
    from pathlib import Path
    assert fixture_document_refs(Path("other.json"),
        {"repository": "https://example.com/repo", "commit": "a" * 40}) == {"a" * 40}
