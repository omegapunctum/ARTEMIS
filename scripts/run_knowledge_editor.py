"""Start the bounded local editor with persistent, private account/data storage."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]


def configure(data_dir: Path, owner_email: str, port: int) -> None:
    os.umask(0o077)
    data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    secret_path = data_dir / "auth-secret.key"
    try:
        descriptor = os.open(secret_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(secrets.token_urlsafe(48))
    if secret_path.is_symlink():
        raise ValueError("The runtime secret must be a regular private file")
    secret = secret_path.read_text().strip()
    if len(secret) < 32:
        raise ValueError("The existing runtime secret is invalid; do not replace it silently")
    os.environ.update({
        "APP_ENV": "local", "AUTH_SESSION_BACKEND": "memory",
        "MIGRATION_STARTUP_ROLE": "owner", "AUTH_SECRET_KEY": secret,
        "AUTH_DATABASE_URL": "sqlite:///" + str(data_dir.resolve() / "editor.sqlite3"),
        "MODERATOR_EMAILS": owner_email, "COOKIE_SECURE": "false",
        "CORS_ALLOW_ORIGINS": f"http://127.0.0.1:{port},http://localhost:{port}",
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True, help="Private persistent runtime directory")
    parser.add_argument("--owner-email", required=True, help="Existing or first registered owner account")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if "@" not in args.owner_email or not 1 <= args.port <= 65535:
        parser.error("Provide a valid owner email and port")
    configure(args.data_dir, args.owner_email, args.port)
    sys.path.insert(0, str(ROOT))
    # Local-only: production authentication, Redis and external hosting are separate setup.
    os.chdir(args.data_dir)
    import uvicorn
    print(f"ARTEMIS editor: http://127.0.0.1:{args.port}/editor/", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
