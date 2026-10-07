"""Owner-first public runtime; legacy/local app and domain models stay separate."""
from __future__ import annotations

import logging
import os
from ipaddress import ip_network
from pathlib import Path
from urllib.parse import urlsplit


def configure() -> tuple[str, str]:
    """Fail before importing auth or creating data when required settings are absent."""
    from pydantic import EmailStr, TypeAdapter, ValidationError

    origin = os.getenv("ARTEMIS_EDITOR_ORIGIN") or os.getenv("RENDER_EXTERNAL_URL", "")
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment
            or any(char.isspace() or ord(char) < 32 for char in origin)):
        raise RuntimeError("A canonical HTTPS editor origin is required")
    try:
        if parsed.port not in {None, 443}:
            raise ValueError
        owner = str(TypeAdapter(EmailStr).validate_python(os.getenv("ARTEMIS_OWNER_EMAIL", "")))
    except (ValueError, ValidationError):
        raise RuntimeError("Valid editor origin and owner configuration are required") from None
    secret = os.getenv("AUTH_SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("A stable AUTH_SECRET_KEY of at least 32 characters is required")
    redis_url = os.getenv("REDIS_URL", "")
    if urlsplit(redis_url).scheme not in {"redis", "rediss"}:
        raise RuntimeError("A private Redis connection is required")
    proxy_ranges = os.getenv("ARTEMIS_EDITOR_PROXY_CIDRS", "").strip().split(",")
    try:
        networks = [ip_network(value.strip(), strict=True) for value in proxy_ranges]
        if not networks or any(not network.is_private or network.prefixlen == 0 for network in networks):
            raise ValueError
    except ValueError:
        raise RuntimeError("Explicit private trusted proxy IPs/CIDRs are required") from None
    raw_directory = os.getenv("ARTEMIS_EDITOR_DATA_DIR", "")
    directory = Path(raw_directory)
    if not raw_directory or not directory.is_absolute() or not directory.is_dir() or directory.is_symlink():
        raise RuntimeError("An existing absolute mounted data directory is required")
    if (directory / "editor.sqlite3").is_symlink():
        raise RuntimeError("The database must not be a symlink")
    os.umask(0o077)
    os.environ.update({
        "APP_ENV": "production", "AUTH_SESSION_BACKEND": "redis",
        "AUTH_DATABASE_URL": "sqlite:///" + str(directory.resolve() / "editor.sqlite3"),
        "AUTH_ALGORITHM": "HS256", "MODERATOR_EMAILS": owner,
        "COOKIE_SECURE": "true", "COOKIE_HTTPONLY": "true", "COOKIE_SAMESITE": "lax",
        "COOKIE_PATH": "/", "COOKIE_DOMAIN": "", "MIGRATION_STARTUP_ROLE": "owner",
        # The hosted ASGI proxy middleware resolves the chain once, from the right.
        "ARTEMIS_TRUSTED_PROXIES": "", "TRUSTED_PROXY_IPS": "",
    })
    return parsed.hostname, owner


class PublicLogFilter(logging.Filter):
    """No email, DB bindings or exception traces in this runtime's structured logs."""
    def filter(self, record):
        allowed = {"route", "path", "method", "request_id", "status_code", "duration_ms", "error_type"}
        record.event_data = {key: value for key, value in getattr(record, "event_data", {}).items() if key in allowed}
        record.exc_info = None
        record.exc_text = None
        return True


def bootstrap_owner(owner: str) -> None:
    from app.auth.service import SessionLocal, User
    from app.auth.utils import hash_password

    password = os.environ.pop("ARTEMIS_OWNER_PASSWORD", "")
    with SessionLocal() as db:
        existing = db.query(User).filter_by(email=owner).first()
        if existing:
            # Do not convert an existing unprivileged account into an operator.
            if not existing.is_admin:
                raise RuntimeError("Existing owner account needs explicit operator provisioning")
            return
        if not 12 <= len(password.encode("utf-8")) <= 72:
            raise RuntimeError("Initial owner password must contain 12 to 72 UTF-8 bytes")
        db.add(User(email=owner, password_hash=hash_password(password), is_admin=True))
        db.commit()


def create_app():
    hostname, owner = configure()
    from fastapi import FastAPI, Depends, Request, HTTPException
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    from sqlalchemy import text
    from app.auth import service as auth
    from app.auth.routes import router as auth_router
    from app.auth.schemas import UserResponse
    from app.auth.session_store import default_refresh_session_store
    from app.knowledge_editor import service as editor
    from app.knowledge_editor.routes import router, knowledge_editor_error_handler
    from app.observability import (setup_logging, ObservabilityMiddleware,
        http_exception_handler, unhandled_exception_handler)

    setup_logging()
    for handler in logging.getLogger().handlers:
        handler.addFilter(PublicLogFilter())
    auth.init_db()
    editor.init_db()
    bootstrap_owner(owner)
    app = FastAPI(title="ARTEMIS Knowledge Editor", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[hostname, "127.0.0.1", "localhost"])
    app.add_middleware(ProxyHeadersMiddleware,
        trusted_hosts=[value.strip() for value in os.environ["ARTEMIS_EDITOR_PROXY_CIDRS"].split(",")])
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(editor.KnowledgeEditorError, knowledge_editor_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    async def invalid_request(request, exc):
        # Validation errors may include submitted passwords/private native expressions.
        return JSONResponse(status_code=422, content={"error": "invalid_request"})
    app.add_exception_handler(RequestValidationError, invalid_request)

    # Reuse actual routes and dependencies; registration is absent server-side.
    from fastapi import APIRouter
    public_auth = APIRouter()
    public_auth.routes = [route for route in auth_router.routes
        if route.path in {"/auth/login", "/auth/refresh", "/auth/logout"}]
    app.include_router(public_auth, prefix="/api")
    app.include_router(router, prefix="/api")

    @app.get("/api/me", response_model=UserResponse)
    def me(user = Depends(auth.get_current_user)):
        return {"id": user.id, "email": user.email, "is_admin": bool(user.is_admin)}

    @app.get("/api/ready")
    def ready():
        try:
            with auth.engine.connect() as db:
                db.execute(text("SELECT 1 FROM users LIMIT 1"))
                db.execute(text("SELECT 1 FROM knowledge_editor_objects LIMIT 1"))
            default_refresh_session_store._client.ping()
        except Exception:
            return JSONResponse(status_code=503, content={"ok": False})
        return {"ok": True}

    @app.middleware("http")
    async def headers(request: Request, call_next):
        if request.method == "POST" and request.url.path == "/api/auth/login":
            try:
                payload = await request.json()
                password = payload.get("password") if isinstance(payload, dict) else None
                if isinstance(password, str) and len(password.encode("utf-8")) > 72:
                    return JSONResponse(status_code=422, content={"error": "invalid_request"},
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
            except (ValueError, UnicodeError):
                return JSONResponse(status_code=422, content={"error": "invalid_request"},
                    headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
        response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY"})
        return response

    static = Path(__file__).parent / "static"

    @app.get("/editor/", include_in_schema=False)
    def editor_page():
        # Same form; only the unavailable public registration action is hidden.
        page = (static / "index.html").read_text()
        page = page.replace('id="register-submit"', 'id="register-submit" hidden')
        return HTMLResponse(page)

    @app.get("/editor/index.html", include_in_schema=False)
    def editor_index():
        return RedirectResponse("/editor/", status_code=307)

    app.mount("/editor", StaticFiles(directory=static, html=True), name="editor")
    return app
