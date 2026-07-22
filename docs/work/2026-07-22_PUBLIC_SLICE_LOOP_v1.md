# ARTEMIS — Public Research Slice Loop v1

## Статус

- Тип: approved execution contract for issue #286.
- Фаза: 4.5 Product/Data Validation.
- Статус исполнения: Batch A/B implemented locally; public deployment pending.
- Основание: validation corpus #285 завершён, `comparison_ready` достигнут.

## 1. Цель

Сделать честным полный public loop:

> создать исследовательский контекст → сохранить → закрыть → открыть снова → передать read-only ссылку → открыть её в чистой browser session.

Наличие FastAPI-кода в репозитории не считается выполнением. Финальная приёмка требует отдельно развернутый API и browser evidence с публичного frontend.

## 2. Batches

### Batch A — contract and threat boundary

- private Slice остаётся owner-only resource;
- share не публикует UGC в canonical dataset;
- read-only access является unlisted capability URL;
- public response не раскрывает `owner_id`;
- private/API responses не кэшируются.

### Batch B — runtime share loop

- owner создаёт или ротирует share token;
- в persistence хранится только SHA-256 token;
- unauthenticated reader получает полный Slice context без write capability;
- revoke, rotation и удаление Slice аннулируют старую ссылку;
- frontend умеет создать/copy link и восстановить shared context через `#shared_slice=`; token остаётся во fragment и не отправляется Pages-серверу или в HTTP `Referer`;
- configured external API base применяется ко всем authenticated runtime modules.

### Batch C — deployment readiness

- выбрать один provider contour для FastAPI + durable SQL + Redis;
- устранить SQLite-only assumptions до заявления external SQL support;
- определить migration owner, health/readiness, CORS, cookie и secret policy;
- добавить provider-neutral deploy manifest и smoke commands;
- документировать backup/restore и failure modes.

### Batch D — public acceptance

- развернуть API и persistence;
- задать Pages `ARTEMIS_API_BASE` и capability flags без hardcoded local fallback;
- выполнить register/login и save/reopen/update/delete;
- открыть read-only link в чистой browser session;
- подтвердить CORS, cookies, service-worker no-store и отсутствие route fallback noise;
- сохранить dated evidence с public URLs и exact commit.

## 3. Share security contract

- token создаётся через cryptographic RNG и имеет не менее 256 бит entropy;
- raw token возвращается только при создании/rotation и не хранится;
- одинаковый error shape `404` не раскрывает существование private Slice;
- каждый Slice имеет не более одного действующего token;
- rotation инвалидирует старый token;
- shared response включает title, description, Feature refs, time/view state и annotations;
- shared response исключает owner identity и administrative metadata;
- link possession означает read access ко всему текущему Slice, поэтому UI предупреждает владельца перед rotation;
- share URL не является механизмом collaborative editing.

## 4. Deployment gate

Фактический provider не выбирается скрытым предположением внутри Batch A/B. До Batch C нужно подтвердить:

1. FastAPI hosting с HTTPS и стабильным публичным origin;
2. durable SQL, совместимый с фактическими migrations;
3. Redis для non-development refresh sessions;
4. managed secrets и explicit `AUTH_SECRET_KEY`;
5. один migration-owner instance или отдельный migration job;
6. CORS только для production Pages origin и локальных development origins;
7. backup/restore contour;
8. стоимость и режим sleep/cold start, приемлемые для validation rounds.

## 5. Acceptance evidence

Batch A/B принимается, когда:

- focused API, migration, frontend state, auth routing и service-worker tests проходят;
- full regression и `scripts/release_check.py` проходят;
- share token отсутствует в stored rows в raw form;
- rotation/revoke/delete tests доказывают invalidation;
- canonical Slice docs синхронизированы.

Issue #286 остаётся открытым до Batch D. Локальный или CI-only E2E не заменяет public clean-browser evidence.
