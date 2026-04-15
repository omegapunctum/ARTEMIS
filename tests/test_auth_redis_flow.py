import importlib
import sys

import pytest
from fastapi import HTTPException

import app.auth.service as auth_service
import app.auth.session_store as auth_session_store


class _FakeRedisClient:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}
        self.calls: list[tuple] = []

    def ping(self) -> bool:
        self.calls.append(("ping",))
        return True

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.calls.append(("set", key, value, ex))
        self.storage[key] = value
        return True

    def get(self, key: str):
        self.calls.append(("get", key))
        value = self.storage.get(key)
        return value.encode("utf-8") if value is not None else None

    def delete(self, key: str) -> int:
        self.calls.append(("delete", key))
        existed = key in self.storage
        self.storage.pop(key, None)
        return int(existed)

    def getdel(self, key: str):
        self.calls.append(("getdel", key))
        value = self.storage.get(key)
        self.storage.pop(key, None)
        return value.encode("utf-8") if value is not None else None


def test_auth_service_flow_uses_redis_store_in_redis_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeRedisClient()

    class _FakeRedisClass:
        @staticmethod
        def from_url(url: str, decode_responses: bool = False):
            assert url == "redis://fake-redis:6379/0"
            assert decode_responses is False
            return fake_client

    class _FakeRedisModule:
        Redis = _FakeRedisClass

    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-auth-redis-flow")
    monkeypatch.setenv("AUTH_SESSION_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://fake-redis:6379/0")
    monkeypatch.setitem(sys.modules, "redis", _FakeRedisModule)

    try:
        reloaded_session_store = importlib.reload(auth_session_store)
        reloaded_service = importlib.reload(auth_service)

        assert isinstance(
            reloaded_session_store.default_refresh_session_store,
            reloaded_session_store.RedisRefreshSessionStore,
        )

        reloaded_service.init_db()
        db = reloaded_service.SessionLocal()
        try:
            reloaded_service.register_user(db, "redis-flow@example.com", "password123")
            _, refresh_token = reloaded_service.login_user(db, "redis-flow@example.com", "password123")
            refreshed_access_token, _ = reloaded_service.rotate_refresh_token(refresh_token, db)
            assert refreshed_access_token

            with pytest.raises(HTTPException) as exc:
                reloaded_service.rotate_refresh_token(refresh_token, db)
            assert exc.value.status_code == 401
            assert exc.value.detail == "Invalid refresh token"
        finally:
            db.query(reloaded_service.User).delete()
            db.commit()
            db.close()
            reloaded_service.reset_refresh_sessions_for_tests()

        assert any(call[0] == "set" for call in fake_client.calls)
        assert any(call[0] == "getdel" for call in fake_client.calls)
    finally:
        monkeypatch.undo()
        importlib.reload(auth_session_store)
        importlib.reload(auth_service)
