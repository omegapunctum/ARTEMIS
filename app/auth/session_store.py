from __future__ import annotations

import os
from typing import Protocol

try:
    import redis
except ModuleNotFoundError:  # pragma: no cover - exercised when redis backend is explicitly selected without dependency.
    redis = None


class RefreshSessionStore(Protocol):
    def store_refresh_session(self, jti: str, user_id: str) -> None:
        ...

    def get_refresh_session_user(self, jti: str) -> str | None:
        ...

    def delete_refresh_session(self, jti: str) -> None:
        ...

    def consume_refresh_session(self, jti: str) -> str | None:
        ...


def _refresh_session_ttl_seconds() -> int:
    refresh_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    return max(refresh_days, 1) * 24 * 60 * 60


class InMemoryRefreshSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, str] = {}

    def store_refresh_session(self, jti: str, user_id: str) -> None:
        self._sessions[jti] = user_id

    def get_refresh_session_user(self, jti: str) -> str | None:
        return self._sessions.get(jti)

    def delete_refresh_session(self, jti: str) -> None:
        self._sessions.pop(jti, None)

    def consume_refresh_session(self, jti: str) -> str | None:
        return self._sessions.pop(jti, None)

    def clear(self) -> None:
        self._sessions.clear()

    @property
    def raw_sessions(self) -> dict[str, str]:
        return self._sessions


class RedisRefreshSessionStore:
    def __init__(
        self,
        client: "redis.Redis",
        *,
        key_prefix: str = "auth:refresh:",
        ttl_seconds: int | None = None,
    ) -> None:
        self._client = client
        self._key_prefix = key_prefix
        self._ttl_seconds = ttl_seconds if ttl_seconds is not None else _refresh_session_ttl_seconds()

    def _key(self, jti: str) -> str:
        return f"{self._key_prefix}{jti}"

    @staticmethod
    def _decode(value: str | bytes | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def store_refresh_session(self, jti: str, user_id: str) -> None:
        self._client.set(self._key(jti), user_id, ex=self._ttl_seconds)

    def get_refresh_session_user(self, jti: str) -> str | None:
        return self._decode(self._client.get(self._key(jti)))

    def delete_refresh_session(self, jti: str) -> None:
        self._client.delete(self._key(jti))

    def consume_refresh_session(self, jti: str) -> str | None:
        key = self._key(jti)
        getdel = getattr(self._client, "getdel", None)
        if callable(getdel):
            return self._decode(getdel(key))

        value = self._client.get(key)
        if value is None:
            return None
        self._client.delete(key)
        return self._decode(value)


def create_default_refresh_session_store() -> RefreshSessionStore:
    backend = (os.getenv("AUTH_SESSION_BACKEND") or "memory").strip().lower()
    if backend == "memory":
        return InMemoryRefreshSessionStore()
    if backend != "redis":
        raise RuntimeError("Unsupported AUTH_SESSION_BACKEND. Expected 'memory' or 'redis'.")

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise RuntimeError("REDIS_URL is required when AUTH_SESSION_BACKEND=redis")
    if redis is None:
        raise RuntimeError("redis dependency is required when AUTH_SESSION_BACKEND=redis")

    try:
        client = redis.Redis.from_url(redis_url, decode_responses=False)
        client.ping()
    except Exception as exc:  # pragma: no cover - environment/network dependent.
        raise RuntimeError("Failed to initialize Redis refresh session store") from exc
    return RedisRefreshSessionStore(client=client)


default_refresh_session_store = create_default_refresh_session_store()
