"""Production deployment failure gates and real Redis-backed isolated app."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from app.knowledge_editor.hosted import configure


@pytest.fixture
def configured(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", os.environ.copy())
    settings = {"ARTEMIS_EDITOR_ORIGIN": "https://editor.example.com",
        "ARTEMIS_OWNER_EMAIL": "owner@example.com", "AUTH_SECRET_KEY": "synthetic-stable-secret-only-1234567890",
        "REDIS_URL": "redis://127.0.0.1:6379/0", "ARTEMIS_EDITOR_DATA_DIR": str(tmp_path),
        "ARTEMIS_EDITOR_PROXY_CIDRS": "10.1.2.0/24"}
    for key, value in settings.items():
        monkeypatch.setenv(key, value)
    original = os.umask(0o077)
    yield settings
    os.umask(original)


@pytest.mark.parametrize("key,value", [
    ("ARTEMIS_EDITOR_ORIGIN", "http://editor.example.com"),
    ("ARTEMIS_EDITOR_ORIGIN", "https://owner:password@editor.example.com"),
    ("ARTEMIS_EDITOR_ORIGIN", "https://editor.example.com/path"),
    ("ARTEMIS_EDITOR_ORIGIN", "https://editor.example.com:bad"),
    ("ARTEMIS_OWNER_EMAIL", "invalid"), ("AUTH_SECRET_KEY", "short"),
    ("REDIS_URL", ""), ("ARTEMIS_EDITOR_DATA_DIR", "relative"),
    ("ARTEMIS_EDITOR_PROXY_CIDRS", ""), ("ARTEMIS_EDITOR_PROXY_CIDRS", "*"),
    ("ARTEMIS_EDITOR_PROXY_CIDRS", "0.0.0.0/0"),
])
def test_missing_or_unsafe_configuration_fails_before_database(configured, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError):
        configure()
    assert not (Path(configured["ARTEMIS_EDITOR_DATA_DIR"]) / "editor.sqlite3").exists()


def test_production_overrides_unsafe_inherited_configuration(configured, monkeypatch):
    for key, value in {"APP_ENV": "local", "AUTH_SESSION_BACKEND": "memory", "COOKIE_SECURE": "false",
                       "COOKIE_HTTPONLY": "false", "COOKIE_DOMAIN": "foreign.example.com"}.items():
        monkeypatch.setenv(key, value)
    assert configure() == ("editor.example.com", "owner@example.com")
    assert os.environ["APP_ENV"] == "production"
    assert os.environ["AUTH_SESSION_BACKEND"] == "redis"
    assert os.environ["COOKIE_SECURE"] == os.environ["COOKIE_HTTPONLY"] == "true"
    assert os.environ["COOKIE_DOMAIN"] == ""


def test_database_symlink_rejected(configured, tmp_path):
    (tmp_path / "editor.sqlite3").symlink_to(tmp_path / "other.sqlite3")
    with pytest.raises(RuntimeError, match="symlink"):
        configure()


def test_real_redis_owner_only_app_loop_and_restart(tmp_path):
    redis_url = os.getenv("EDITOR_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Real Redis integration runs in hosted-editor CI; no fake Redis substitute")
    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(root), os.getenv("PYTHONPATH", "")]),
        "ARTEMIS_EDITOR_ORIGIN": "https://editor.example.com",
        "ARTEMIS_EDITOR_DATA_DIR": str(tmp_path), "ARTEMIS_OWNER_EMAIL": "owner@example.com",
        "ARTEMIS_OWNER_PASSWORD": "synthetic-password-for-test", "REDIS_URL": redis_url,
        "ARTEMIS_EDITOR_PROXY_CIDRS": "10.1.2.0/24",
        "AUTH_SECRET_KEY": "synthetic-stable-hosted-secret-1234567890"}
    script = '''
import json, os
from fastapi.testclient import TestClient
from app.knowledge_editor.hosted import create_app
app=create_app()
from app.auth import service as auth
from app.auth.session_store import default_refresh_session_store as sessions
from app.knowledge_editor import service as editor
from scripts.knowledge_editor_backup import copy_database
from pathlib import Path
with auth.SessionLocal() as db:
    user=db.query(auth.User).filter_by(email="owner@example.com").one()
    identity=(user.id, user.password_hash, user.is_admin)
with TestClient(app, base_url="https://editor.example.com") as client:
    assert client.get("/api/ready").json()=={"ok":True}
    page=client.get("/editor/")
    assert page.status_code==200 and 'id="register-submit" hidden' in page.text
    alias=client.get("/editor/index.html",follow_redirects=False)
    assert alias.status_code==307 and alias.headers["location"]=="/editor/"
    assert 'id="register-submit" hidden' in client.get("/editor/index.html").text
    for path in ("/api/auth/register", "/api/drafts", "/api/map/feed", "/uploads/", "/docs"):
        assert client.get(path).status_code==404
    assert client.post("/api/auth/register",json={"email":"attacker@example.com","password":"unused"}).status_code==404
    assert client.get("/api/me").status_code==401
    for long_password in ("x"*73,"Ж"*37):
        rejected=client.post("/api/auth/login",json={"email":"owner@example.com","password":long_password})
        assert rejected.status_code==422 and long_password not in rejected.text
    login=client.post("/api/auth/login",json={"email":"owner@example.com","password":"synthetic-password-for-test"})
    assert login.status_code==200,login.text
    assert "Secure" in login.headers["set-cookie"] and "HttpOnly" in login.headers["set-cookie"]
    previous=client.cookies.get("refresh_token")
    refreshed=client.post("/api/auth/refresh")
    assert refreshed.status_code==200
    stale=client.post("/api/auth/refresh",headers={"Cookie":"refresh_token="+previous})
    assert stale.status_code==401
    headers={"Authorization":"Bearer "+refreshed.json()["access_token"]}
    assert client.get("/api/me",headers=headers).json()["is_admin"]
    content={"entity":{"name":"Synthetic hosted object"},"source":{"title":"Synthetic source","url":"https://example.org/source"},"claim":{"statement":"Synthetic candidate statement"},"evidence":{"locator":"section 1","native_expression":"PRIVATE_SYNTHETIC_EXPRESSION"},"human_authored_attestation":True}
    base="/api/knowledge-editor"
    item=client.post(base+"/drafts",headers=headers,json={"content":content}).json()
    item=client.post(base+"/drafts/"+item["id"]+"/submit",headers=headers,json={"expected_version":item["version"]}).json()
    item=client.post(base+"/drafts/"+item["id"]+"/review",headers=headers,json={"expected_version":item["version"],"submitted_digest":item["submitted_digest"],"expected_predecessor_revision_id":None,"decision":"accept","reason":"Synthetic review"}).json()
    item=client.post(base+"/drafts/"+item["id"]+"/publish",headers=headers,json={"expected_version":item["version"],"accepted_revision_id":item["accepted_revision_id"],"accepted_revision_digest":item["accepted_revision_digest"],"expected_object_version":item["object_version"],"expected_publication_id":None}).json()
    url=base+"/public/snapshots/"+item["published_snapshot_id"]
    snapshot=client.get(url)
    assert snapshot.status_code==200
    assert "PRIVATE_SYNTHETIC_EXPRESSION" not in snapshot.text
    assert "owner@example.com" not in snapshot.text
    assert "no-store" in snapshot.headers["cache-control"]
    previous_body=snapshot.text
    update=client.post(base+"/revisions/"+item["accepted_revision_id"]+"/corrections",headers=headers,json={"expected_revision_id":item["accepted_revision_id"],"expected_object_version":item["object_version"],"reason":"Synthetic correction"}).json()
    updated_content=update["content"]
    updated_content["claim"]["statement"]="Synthetic corrected statement"
    updated_content["human_authored_attestation"]=True
    update=client.put(base+"/drafts/"+update["id"],headers=headers,json={"expected_version":update["version"],"content":updated_content}).json()
    update=client.post(base+"/drafts/"+update["id"]+"/submit",headers=headers,json={"expected_version":update["version"]}).json()
    update=client.post(base+"/drafts/"+update["id"]+"/review",headers=headers,json={"expected_version":update["version"],"submitted_digest":update["submitted_digest"],"expected_predecessor_revision_id":update["predecessor_revision_id"],"decision":"accept","reason":"Synthetic correction review"}).json()
    update=client.post(base+"/drafts/"+update["id"]+"/publish",headers=headers,json={"expected_version":update["version"],"accepted_revision_id":update["accepted_revision_id"],"accepted_revision_digest":update["accepted_revision_digest"],"expected_object_version":update["object_version"],"expected_publication_id":update["published_snapshot_id"]}).json()
    new_url=base+"/public/snapshots/"+update["published_snapshot_id"]
    assert client.get(url).text==previous_body
    corrected=client.get(new_url)
    assert corrected.status_code==200 and "Synthetic corrected statement" in corrected.text
    (Path(os.environ["ARTEMIS_EDITOR_DATA_DIR"])/"snapshot.json").write_text(json.dumps({"url":url,"body":previous_body,"new_url":new_url,"new_body":corrected.text,"identity":identity}))
    original_ping=sessions._client.ping
    sessions._client.ping=lambda: (_ for _ in ()).throw(RuntimeError("private diagnostics"))
    assert client.get("/api/ready").status_code==503
    assert client.get("/api/ready").json()=={"ok":False}
    sessions._client.ping=original_ping
copy_database(Path(os.environ["ARTEMIS_EDITOR_DATA_DIR"])/"editor.sqlite3",Path(os.environ["ARTEMIS_EDITOR_DATA_DIR"])/"backup.sqlite3")
print("HOSTED_LOOP_PASS")
'''
    result = subprocess.run([sys.executable, "-c", script], env=env, cwd=tmp_path,
                            capture_output=True, text=True, timeout=50)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "HOSTED_LOOP_PASS" in result.stdout
    assert "owner@example.com" not in result.stderr
    assert "synthetic-password-for-test" not in result.stderr
    assert "PRIVATE_SYNTHETIC_EXPRESSION" not in result.stderr
    restart = '''
import json, os
from pathlib import Path
from fastapi.testclient import TestClient
from app.knowledge_editor.hosted import create_app
saved=json.loads((Path(os.environ["ARTEMIS_EDITOR_DATA_DIR"])/"snapshot.json").read_text())
app=create_app()
from app.auth import service as auth
with auth.SessionLocal() as db:
    user=db.query(auth.User).filter_by(email="owner@example.com").one()
    assert [user.id,user.password_hash,user.is_admin]==saved["identity"]
with TestClient(app,base_url="https://editor.example.com") as client:
    assert client.get(saved["url"]).text==saved["body"]
    assert client.get(saved["new_url"]).text==saved["new_body"]
print("RESTART_PASS")
'''
    env["ARTEMIS_OWNER_PASSWORD"] = "different-env-password-must-not-reset"
    result = subprocess.run([sys.executable, "-c", restart], env=env, cwd=tmp_path,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RESTART_PASS" in result.stdout
    from scripts.knowledge_editor_backup import copy_database
    restored = tmp_path / "restored"
    copy_database(tmp_path / "backup.sqlite3", restored / "editor.sqlite3")
    (restored / "snapshot.json").write_bytes((tmp_path / "snapshot.json").read_bytes())
    env["ARTEMIS_EDITOR_DATA_DIR"] = str(restored)
    result = subprocess.run([sys.executable, "-c", restart], env=env, cwd=restored,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RESTART_PASS" in result.stdout


@pytest.mark.parametrize("password", ["short", "Ж" * 37])
def test_invalid_bootstrap_password_cannot_create_owner(tmp_path, password):
    if not os.getenv("EDITOR_TEST_REDIS_URL"):
        pytest.skip("Real Redis deployment CI required")
    env = {**os.environ, "ARTEMIS_EDITOR_ORIGIN": "https://editor.example.com",
        "ARTEMIS_EDITOR_DATA_DIR": str(tmp_path), "ARTEMIS_OWNER_EMAIL": "owner@example.com",
        "ARTEMIS_OWNER_PASSWORD": password, "REDIS_URL": os.environ["EDITOR_TEST_REDIS_URL"],
        "ARTEMIS_EDITOR_PROXY_CIDRS": "10.1.2.0/24",
        "AUTH_SECRET_KEY": "synthetic-bootstrap-rejection-secret-1234567890"}
    script = '''
from app.knowledge_editor.hosted import create_app
try:
    create_app()
except RuntimeError as error:
    assert str(error)=="Initial owner password must contain 12 to 72 UTF-8 bytes"
else:
    raise AssertionError("Invalid bootstrap was accepted")
from app.auth import service as auth
with auth.SessionLocal() as db:
    assert db.query(auth.User).count()==0
'''
    result = subprocess.run([sys.executable, "-c", script], env=env, cwd=Path(__file__).resolve().parents[1],
                            capture_output=True, text=True, timeout=25)
    assert result.returncode == 0, result.stdout + result.stderr


def test_trusted_proxy_separates_clients_and_ignores_spoofed_prefix():
    import asyncio
    from app.security.rate_limit import get_client_ip
    from starlette.requests import Request
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

    async def address(peer, forwarded):
        values = []
        async def app(scope, receive, send):
            values.append(get_client_ip(Request(scope)))
        middleware = ProxyHeadersMiddleware(app, trusted_hosts=["10.1.2.0/24"])
        scope={"type":"http","method":"POST","path":"/api/auth/login",
            "client":(peer,1234),"scheme":"http","headers":[(b"x-forwarded-for",forwarded.encode())]}
        await middleware(scope,None,None)
        return values[0]
    assert asyncio.run(address("10.1.2.3","198.51.100.10"))=="198.51.100.10"
    assert asyncio.run(address("10.1.2.3","198.51.100.11"))=="198.51.100.11"
    assert asyncio.run(address("10.1.2.3","192.0.2.99, 198.51.100.10"))=="198.51.100.10"
    assert asyncio.run(address("198.51.100.20","192.0.2.99"))=="198.51.100.20"
