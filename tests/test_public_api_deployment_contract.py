from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dockerfile_runs_canonical_api_as_non_root_with_healthcheck():
    dockerfile = _read("Dockerfile")

    assert "FROM python:3.12-slim" in dockerfile
    assert "APP_ENV=production" in dockerfile
    assert "USER artemis" in dockerfile
    assert "uvicorn app.main:app" in dockerfile
    assert "/api/health" in dockerfile
    assert "HEALTHCHECK" in dockerfile


def test_public_environment_contract_requires_persistent_and_cross_site_settings():
    environment_contract = _read("deploy/public-api.env.example")

    required_assignments = {
        "APP_ENV=production",
        "MIGRATION_STARTUP_ROLE=owner",
        "AUTH_SESSION_BACKEND=redis",
        "AUTH_DATABASE_URL=sqlite:////runtime/artemis.db",
        "UPLOADS_DIR=/runtime/uploads",
        "COOKIE_HTTPONLY=true",
        "COOKIE_SECURE=true",
        "COOKIE_SAMESITE=none",
        "CORS_ALLOW_ORIGINS=https://omegapunctum.github.io",
    }

    for assignment in required_assignments:
        assert assignment in environment_contract

    assert "COOKIE_DOMAIN=" not in environment_contract
    assert "AUTH_SECRET_KEY=replace-" in environment_contract


def test_upload_storage_path_is_runtime_configurable():
    main_module = _read("app/main.py")

    assert 'os.getenv("UPLOADS_DIR", "uploads")' in main_module
    assert 'StaticFiles(directory=UPLOADS_DIR)' in main_module


def test_smoke_contract_checks_https_health_request_id_and_credentialed_cors():
    smoke_script = _read("scripts/public_api_smoke.py")

    assert "public smoke requires HTTPS" in smoke_script
    assert '"X-Request-ID"' in smoke_script
    assert '"Access-Control-Allow-Origin"' in smoke_script
    assert '"Access-Control-Allow-Credentials"' in smoke_script
    assert 'endswith("/api")' in smoke_script


def test_backup_contract_uses_sqlite_backup_and_integrity_check():
    backup_script = _read("scripts/sqlite_backup.py")

    assert "source_connection.backup(destination_connection)" in backup_script
    assert "PRAGMA integrity_check" in backup_script
    assert "os.replace(temporary_destination, destination)" in backup_script


def test_readiness_document_preserves_capability_truth_boundary():
    readiness_document = _read("docs/work/2026-07-23_PUBLIC_API_DEPLOYMENT_READINESS_v1.md")

    assert "Capability status: `BACKEND-AVAILABLE`" in readiness_document
    assert "не является доказательством фактического public deployment" in readiness_document
    assert "Локальный Docker scaffold сам по себе не закрывает этот gate" in readiness_document
    assert "не должны переводить Research Slice capability в `PUBLIC NOW`" in readiness_document
