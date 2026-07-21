# ARTEMIS — PROJECT PHASES v4.2

## Статус

- Тип: canonical operational phases document.
- Статус: active.
- Дата изменения модели: 2026-07-16.
- Активная фаза: **4.5 Product/Data Validation**.

Фазы управляют порядком исполнения. Они не заменяют долгосрочную лестницу `ARTEMIS_CONCEPT.md` и не используются как список всех идей.

## Принцип перехода

Фаза закрывается только при наличии проверяемого exit evidence. Наличие кода, документа или structural check само по себе не подтверждает пользовательскую ценность, semantic data quality или production readiness.

## Фаза 0 — Foundation [закрыта]

Зафиксировано:

- frontend MapLibre/GeoJSON baseline;
- FastAPI backend baseline;
- Airtable → ETL → `data/*`;
- GitHub Actions/Pages;
- базовая структура репозитория.

## Фаза 1 — Public Map Baseline [закрыта]

Зафиксировано:

- `data/features.geojson` как public map source;
- map, layers, filters, list/detail baseline;
- отсутствие production-default fallback на `/api/map/feed`.

Закрытие означает техническое наличие public map, но не зрелость content corpus.

## Фаза 2 — UGC/Auth Baseline [закрыта с ограничениями]

Зафиксировано:

- auth, drafts, uploads и moderation code paths;
- governance boundary против direct runtime publish;
- Redis session proof paths.

Ограничения:

- GitHub Pages не исполняет backend;
- public end-to-end доступность не подтверждена;
- production multi-node readiness не заявляется.

## Фаза 3 — Controlled Release Stabilization [закрыта]

Зафиксировано:

- release/data artifact consistency baseline;
- executable structural release gate;
- workflow и documentation discipline.

Structural release success не равен semantic content validation.

## Фаза 4 — PWA/UX Baseline Stabilization [закрыта как baseline]

Зафиксировано:

- service worker/private API boundaries;
- loading/error/offline baseline;
- responsive main-flow baseline;
- map-first UI foundation.

Закрытие baseline не означает завершённый product UX. Новый refinement выполняется после data/product decisions и не требует переоткрывать старый stabilization scope.

## Фаза 4.5 — Product/Data Validation [активная]

### Цель

Доказать focused Architecture Atlas vertical до scaling и product expansion.

### Track A — Strategy truth

- синхронизировать canonical documentation с Option A;
- разделить `PUBLIC NOW`, `BACKEND-AVAILABLE`, `PILOT` и `FUTURE`;
- привести GitHub backlog к новой фазе;
- убрать противоречивые navigation/product claims.

### Track B — Data foundation

- выбрать UUID как canonical public ID;
- отделить `source_record_id`;
- нормализовать Sources и Media;
- создать reviewed Relations model;
- отделить Relation от Similarity;
- добавить semantic ETL/release gate;
- устранить enabled empty Layers.

Execution status 2026-07-21: identity, normalized Source/Media export and Relation/Similarity semantics are merged. #284 is merged as `d4e8b53`; the semantic gate excludes 7 enabled empty Layers from public artifacts while retaining bounded warnings. Three Media-rights gaps stay tracked separately in #283.

### Track C — Content pilot

- approved Round 0 envelope: 30–40 architecture Features;
- 6–8 comparison cohorts минимум по 3 Features;
- 12–20 reviewed Relations;
- 100% Source coverage, ≥90% primary Media, 100% Relation evidence;
- executable checked-in content profile;
- 100–150 / 50+ / Stories / reference Slices остаются maturity reference после decision gate.

### Track D — Public product loop

- deploy/configure backend;
- обеспечить public save/open/share Slice;
- скрыть или clearly label недоступные surfaces;
- проверить public E2E.

### Track E — Product UX

- map-first shell refinement;
- compare workflow;
- sourced detail;
- compact timeline;
- CSS/JS ownership cleanup;
- browser-level regression coverage.

### Track F — User validation

- 5–8 участников первой волны;
- Round 1 comprehension/core loop;
- исправления;
- Round 2 decision gate.

### Exit criteria

- approved Round 0 data threshold достигнут;
- semantic validation проходит;
- public Slice loop проходит E2E;
- relation/similarity semantics корректны;
- primary flows подтверждены на desktop/tablet/mobile;
- validation thresholds из `PRODUCT_VALIDATION_PLAN.md` проверены;
- принято `ITERATE`, `EXPAND`, `NARROW` или `STOP/RETHINK`.

## Фаза 5 — Scaling/Hardening [приостановлена]

Статус: **PAUSED / NOT PRIMARY**.

Допустимы только:

- security/reliability fixes;
- deployment work, необходимое для public MVP loop;
- migration/data-integrity blockers;
- observability, нужная для validation.

Запрещено опережающее scaling ради предполагаемого роста. Полный Phase 5 reopen требует evidence из Phase 4.5 и конкретную нагрузочную/операционную причину.

## Фаза 6 — Product Expansion [заблокирована]

Stories depth, Courses, AI assistance, new domains и secondary extensions не открываются до Phase 4.5 decision gate.

Возможный порядок после `EXPAND` определяется отдельным phase update, а не наследуется автоматически из старого roadmap.

## Фаза 7 — Business/Platform [отложена]

Монетизация, enterprise API, integrations, marketplace и platform distribution находятся вне текущего рабочего контура.

## Активный порядок работ

1. Documentation/strategy reset.
2. Identity, Sources, Media и Relations contract.
3. Semantic validation gate.
4. Architecture content pilot.
5. Public backend/Slice loop.
6. Product UX refinement и maintainability.
7. User validation.
8. Decision gate.

Scaling и expansion рассматриваются только после пункта 8.

## Правило обновления

Документ обновляется, если:

1. изменена active phase;
2. достигнут или изменён exit gate;
3. выявлена новая обязательная зависимость;
4. validation decision меняет дальнейший порядок.

Execution details живут в issues/working specs; historical snapshots — в archive/audits.
