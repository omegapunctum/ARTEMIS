# ARTEMIS — Public API Deployment Readiness v1

## Статус

- Тип: implementation/execution contract для issue #308.
- Дата: 2026-07-23.
- Capability status: `BACKEND-AVAILABLE`.
- Этот документ не является доказательством фактического public deployment.

## 1. Цель batch

Подготовить репозиторий к минимальному публичному backend contour, необходимому для validation Research Slice loop:

`public Pages → HTTPS FastAPI → persistent SQLite + Redis sessions → save/reopen/share/revoke`.

Batch не открывает multi-node scaling, Courses, AI, UGC или general-platform scope.

## 2. Проверенное исходное состояние

До этого batch:

- canonical backend entrypoint уже был `app.main:app` с base path `/api`;
- production startup уже fail-fast требовал `AUTH_SECRET_KEY`;
- non-development runtime уже fail-fast требовал Redis-backed refresh sessions;
- `MIGRATION_STARTUP_ROLE` уже разделял owner/non-owner startup path;
- CORS уже конфигурировался через `CORS_ALLOW_ORIGINS`;
- cookie attributes уже конфигурировались через env;
- persistence baseline фактически являлся SQLite-only: requirements не содержат PostgreSQL driver, а engine использует SQLite-compatible configuration;
- отдельного container/deployment manifest не было;
- uploads directory был жёстко привязан к относительному `uploads`.

## 3. Принятый repository contour

Для validation pilot репозиторий поддерживает следующий минимальный contour:

1. Один HTTPS container instance с `uvicorn app.main:app`.
2. Один persistent volume, смонтированный в `/runtime`.
3. SQLite database: `sqlite:////runtime/artemis.db`.
4. Upload storage: `/runtime/uploads`.
5. Один migration owner: `MIGRATION_STARTUP_ROLE=owner`.
6. Managed Redis для refresh sessions.
7. Точный credentialed CORS origin для GitHub Pages.
8. Cross-site refresh cookie: `Secure; HttpOnly; SameSite=None`.
9. Provider health probe: `/api/health`.
10. SQLite online backup через standard backup API и отдельная provider snapshot/retention policy.

Этот contour является single-instance/single-writer validation baseline, а не production-grade multi-node architecture.

## 4. Добавленные artifacts

- `Dockerfile` — non-root Python 3.12 runtime, canonical Uvicorn command и healthcheck.
- `.dockerignore` — исключает repository/test/data artifacts и local secrets из image context.
- `deploy/public-api.env.example` — redacted production configuration contract.
- `scripts/public_api_smoke.py` — HTTPS, health, request-ID и credentialed CORS smoke.
- `scripts/sqlite_backup.py` — verified atomic SQLite backup и integrity verification.
- `UPLOADS_DIR` env support в `app/main.py`.
- static contract tests для deployment artifacts.

## 5. Обязательная configuration matrix

| Variable | Public validation value | Rule |
|---|---|---|
| `APP_ENV` | `production` | запрещает dev secret/session fallbacks |
| `MIGRATION_STARTUP_ROLE` | `owner` | единственный instance применяет migrations |
| `AUTH_SECRET_KEY` | provider secret | длинное random значение, не в GitHub |
| `AUTH_SESSION_BACKEND` | `redis` | memory запрещён вне dev/test/local |
| `REDIS_URL` | managed secret URL | должен проходить startup ping |
| `AUTH_DATABASE_URL` | `sqlite:////runtime/artemis.db` | persistent volume, single writer |
| `UPLOADS_DIR` | `/runtime/uploads` | тот же persistent volume |
| `CORS_ALLOW_ORIGINS` | exact Pages origin | origin без path и wildcard |
| `COOKIE_HTTPONLY` | `true` | refresh token недоступен JavaScript |
| `COOKIE_SECURE` | `true` | обязательно для public HTTPS и SameSite=None |
| `COOKIE_SAMESITE` | `none` | требуется для Pages → отдельный API origin |
| `COOKIE_DOMAIN` | unset | host-only cookie |
| trusted proxies | provider-documented values | не угадывать proxy CIDR/IP |

## 6. Provision sequence

1. Создать managed Redis в том же регионе, что и API.
2. Создать persistent volume и смонтировать его в `/runtime`.
3. Создать public web service из repository Dockerfile.
4. Загрузить configuration names из `deploy/public-api.env.example` в provider secret store.
5. Установить точный Pages origin в `CORS_ALLOW_ORIGINS`.
6. Установить provider-documented trusted proxy values либо оставить proxy trust выключенным.
7. Deploy immutable commit SHA.
8. Проверить startup logs: migrations применены owner instance, Redis ping успешен, API слушает provider port.
9. Выполнить public smoke:

```bash
python scripts/public_api_smoke.py \
  --api-base https://API_HOST/api \
  --origin https://omegapunctum.github.io
```

10. Выполнить restart/redeploy и подтвердить сохранность пользователей и Slice data.
11. Создать и проверить backup.
12. Только после этого передавать API origin в Pages batch #309.

## 7. Backup and restore

### Backup

SQLite backup API создаёт согласованную копию даже при открытом source database:

```bash
python scripts/sqlite_backup.py backup \
  /runtime/artemis.db \
  /runtime/backups/artemis-YYYYMMDD-HHMMSS.db
```

После backup:

```bash
python scripts/sqlite_backup.py verify \
  /runtime/backups/artemis-YYYYMMDD-HHMMSS.db
```

Provider должен дополнительно иметь snapshot/retention policy вне единственного runtime volume.

### Restore drill

1. Остановить API instance или перевести его в maintenance state.
2. Сохранить повреждённый/current database как forensic copy.
3. Проверить выбранный backup через `sqlite_backup.py verify`.
4. Заменить `/runtime/artemis.db` проверенной копией атомарно.
5. Проверить ownership/permissions.
6. Запустить API и migration owner.
7. Выполнить health, auth и disposable Slice smoke.
8. Записать commit, backup identifier, время восстановления и результат.

Restore не считается проверенным только по наличию backup-файла.

## 8. Failure modes

| Failure | Expected behavior | Operator action |
|---|---|---|
| отсутствует `AUTH_SECRET_KEY` | startup fail-fast | исправить secret, redeploy |
| memory session backend в production | startup fail-fast | настроить Redis |
| Redis недоступен | startup fail-fast | проверить URL/network/Redis health |
| неверный migration role | startup fail-fast | установить `owner` для single instance |
| volume read-only/нет permissions | startup fail при DB/uploads init | исправить mount ownership/permissions |
| неверный CORS origin | browser preflight failure | установить exact origin без path |
| `SameSite=Lax` для separate API origin | refresh cookie не отправляется | установить `none` + `secure=true` |
| health `ok=false` | recent process-local 5xx signal | проверить request IDs/logs; не трактовать как global SLO |
| SQLite lock contention | warning/blocker evidence | остановить expansion и оценить storage hardening trigger |

## 9. Provider selection gate

Provider считается выбранным только после фактической проверки:

- HTTPS custom service availability;
- persistent volume semantics и mount path;
- managed Redis connectivity;
- secret injection;
- backup/snapshot support;
- restart/redeploy persistence;
- documented proxy network values;
- текущая стоимость validation environment.

Локальный Docker scaffold сам по себе не закрывает этот gate.

## 10. Evidence required to close #308

- provider и public API URL;
- deployed commit SHA;
- redacted environment matrix;
- successful `public_api_smoke.py` output;
- restart/redeploy persistence evidence;
- Redis refresh continuity evidence;
- backup identifier и successful restore drill;
- failure-mode smoke notes;
- explicit handoff to #309.

До появления этого evidence README/UI/release notes не должны переводить Research Slice capability в `PUBLIC NOW`.
