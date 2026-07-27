# ARTEMIS — Public Research Slice E2E v1

## Статус

- Тип: execution contract/evidence для issue #286.
- Дата: 2026-07-22.
- Compatibility stage A is implemented; this file is retained as current mutable ResearchSlice v2 evidence.
- Deployment stage B остаётся pending; backend capability нельзя обозначать `PUBLIC NOW` до smoke на реальном URL.
- Concept Lock v2 target E2E is gated by Claim/Evidence and immutable revision/Brief migrations; this file cannot close that target.

## 1. Цель

Доказать полный пользовательский цикл:

`save → close → reopen → create share → open in clean session → revoke`.

Этап не расширяет scope на Stories, Courses, AI, UGC или multi-node architecture.

## 2. Stage A — contract and local E2E

Реализованный контракт:

- owner-only create/list/get/patch/delete остаётся private-by-default;
- `POST /api/research-slices/{id}/share` создаёт новый 256-bit capability token;
- в БД хранится только SHA-256 token;
- повторный share инвалидирует прежнюю ссылку;
- `DELETE /api/research-slices/{id}/share` отзывает доступ;
- `GET /api/public/research-slices/shared` работает без auth, принимает capability только через `X-ARTEMIS-Share-Token` и возвращает полный read-only state без `owner_id`;
- public response имеет `no-store`, `no-referrer`, `noindex`;
- frontend использует `#share=<token>`, восстанавливает map/time/layers/features/annotations и маркирует state как read-only;
- frontend API resolver применяет production `ARTEMIS_API_BASE` к Slices/Stories/Courses/UGC paths без двойного `/api`.

Security semantics:

- share является unlisted possession capability, а не public directory entry;
- token не попадает в HTTP request к Pages host, API URL/access log или обычный referrer;
- shared state отражает актуальную owner-версию до rotation/revoke/delete;
- edit/collaboration через share URL отсутствует.

## 3. Stage B — deployment gate

Repository-side deployment readiness:

- Pages generates a public `deployment-config.js` from `ARTEMIS_API_BASE`;
- the generated value must be an HTTPS URL ending in `/api`;
- an early `/api/health` probe enables an explicit capability set only after success;
- missing or unavailable API keeps the public UI in Explore-only mode;
- auth/API resolution has no implicit `/api` or static-origin fallback;
- `deployment-config.js` and all API responses are network-only in the service worker.

These controls make Stage B deployable but do not prove `PUBLIC NOW`.

До `PUBLIC NOW` требуется:

- provisioned HTTPS FastAPI origin;
- persistent single-writer database volume и documented backup/restore;
- Redis-backed refresh sessions;
- отдельный controlled migration owner;
- production `AUTH_SECRET_KEY`, secure cookie и trusted proxy configuration;
- точный `CORS_ALLOW_ORIGINS` для Pages origin;
- Pages injection `ARTEMIS_API_BASE=<https-origin>/api` и capability flags;
- health, auth, save/reopen/share/revoke smoke в clean browser session;
- подтверждение, что service worker не кэширует private или shared API responses;
- failure-mode evidence и rollback path.

Provider не считается выбранным только по локальному Docker/config scaffold. Финальный contour фиксируется после проверки актуальных ограничений persistent storage, Redis, secrets, backups и стоимости на provisioned среде.

## 4. Acceptance

Stage A принимается только при зелёных migration/API/frontend/PWA/release tests.

Issue #286 закрывается только после Stage B и фактического public E2E. Наличие кода Stage A само по себе не закрывает issue и не включает capability в primary public navigation.
