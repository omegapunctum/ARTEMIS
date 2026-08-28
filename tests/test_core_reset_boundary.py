from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_required_check_is_bounded_to_artemis_core() -> None:
    workflow = _text(".github/workflows/release-gate.yml")
    assert "name: ARTEMIS Core Check" in workflow
    assert "validate_leonardo_world_slice.py" in workflow
    assert "build_globe_spike.py" in workflow
    assert "test_globe_runtime_spike.py" in workflow
    assert "pip install -r requirements.txt" not in workflow
    assert "release_check.py" not in workflow
    assert "validate_airtable" not in workflow
    assert "preflight_migration_check" not in workflow


def test_progressive_refinement_is_historical_manual_evidence() -> None:
    workflow = _text(".github/workflows/progressive-refinement.yml")
    trigger = workflow.split("jobs:", 1)[0]
    assert "workflow_dispatch:" in trigger
    assert "pull_request:" not in trigger
    assert "push:" not in trigger
    assert "#392" in trigger


def test_legacy_integrations_are_path_scoped() -> None:
    auth = _text(".github/workflows/auth-redis-integration.yml").split("jobs:", 1)[0]
    moderation = _text(".github/workflows/moderation-integration.yml").split("jobs:", 1)[0]
    etl = _text(".github/workflows/etl.yml").split("jobs:", 1)[0]

    assert '"app/auth/**"' in auth
    assert '"app/moderation/**"' in moderation
    assert '"data/**"' in etl
    assert '".github/workflows/etl.yml"' not in etl
    assert "workflow_dispatch:" in auth
    assert "workflow_dispatch:" in moderation
    assert "workflow_dispatch:" in etl
