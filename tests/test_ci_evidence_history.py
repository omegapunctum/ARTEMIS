from __future__ import annotations

import pytest

from scripts.validate_ci_evidence_history import (
    EvidenceHistoryError,
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
