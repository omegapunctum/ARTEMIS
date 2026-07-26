# ARTEMIS — PROJECT PHASES v5.0

## Статус

- Тип: canonical operational phases document.
- Статус: active.
- Дата изменения модели: 2026-07-26.
- Активная фаза: **4.5 Concept-Locked Product Validation**.

Фазы управляют порядком исполнения. Они не заменяют North Star and independent branch gates из `ARTEMIS_CONCEPT.md` и не используются как список всех идей.

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

## Фаза 4.5 — Concept-Locked Product Validation [активная]

### Цель

Превратить Concept Lock v2 в validation-ready evidence-first Architecture Atlas и доказать либо сузить current vertical до scaling/expansion.

### Track A — Concept Lock v2

- human research as only mission;
- evidence chain as core;
- map/time as independently validated lenses;
- Claim/EvidenceLink model;
- Investigation/SliceRevision/SavedView/ResearchBrief model;
- independent future branch gates.

### Track B — Claim/Evidence and Relation foundation

- first-class Claims and EvidenceLinks with locators;
- independent epistemic dimensions;
- ClassificationAssertions;
- substantive Relation predicates;
- preserve current data without invented evidence;
- exclude `same_movement` from substantive readiness.

Existing UUID/Source/Media/semantic-gate work remains completed technical foundation.

### Track C — Deep research modules

- exactly three modules;
- 4–6 Features and 6–10 Claims each;
- claim-level EvidenceLinks/locators;
- minimum two substantive Relations;
- challenge/contest/uncertainty;
- reference revision and hidden Brief;
- two-reviewer `READY`;
- curation cost.

The 31-Feature/six-cohort profile remains technical envelope, not external-validation readiness.

### Track D — Versioned research outcome

- stable Investigation;
- immutable revisions;
- pinned dataset/schema identity;
- revision-pinned share or visible live mode;
- Research Brief export;
- safe legacy migration.

### Track E — Public research interface

- question/Claim/evidence/conclusion hierarchy;
- Compare 2–3 Features;
- source locator access;
- Relation/classification/Similarity literacy;
- map/time synchronized without dominating evidence;
- public target E2E;
- browser regression.

### Track F — User validation

- exactly six primary users in one wave;
- same-content controlled baseline;
- normal-workflow benchmark;
- counterbalanced order and equal timebox;
- blind two-evaluator Brief rubric;
- absolute thresholds and critical errors;
- separate map/time contribution;
- 7-day unprompted reuse;
- outcome in `VALIDATION_DECISION.md`.

### Exit criteria

- Concept Lock v2 complete;
- `3/3` research modules `READY`;
- semantic validation проходит;
- Claim/Evidence and Relation semantics implemented for test condition;
- public Investigation/revision/Brief loop passes target E2E;
- Relation/classification/Similarity semantics correct;
- primary flows подтверждены на desktop/tablet/mobile;
- six-person validation thresholds checked;
- решение `ITERATE`, `EXPAND`, `NARROW` или `STOP/RETHINK` записано в `VALIDATION_DECISION.md`.

## Фаза 5 — Scaling/Hardening [приостановлена]

Статус: **PAUSED / NOT PRIMARY**.

Допустимы только:

- security/reliability fixes;
- deployment work, необходимое для public MVP loop;
- migration/data-integrity blockers;
- observability, нужная для validation.

Запрещено опережающее scaling ради предполагаемого роста. Полный Phase 5 reopen требует evidence из Phase 4.5 и конкретную нагрузочную/операционную причину.

## Фаза 6 — Product Expansion [заблокирована]

Stories depth, Courses, AI assistance, new domains, institutional workflows и secondary extensions не открываются до Phase 4.5 decision gate.

`EXPAND` открывает только одну named branch. Возможный порядок определяется отдельным phase update, а не старым roadmap.

## Фаза 7 — Business/Platform [отложена]

Монетизация, enterprise API, integrations, marketplace и platform distribution находятся вне текущего рабочего контура.

## Активный порядок работ

1. Concept Lock v2.
2. Three deep research modules.
3. Claim/Evidence/Relation migration.
4. Investigation/revision/Brief migration.
5. Research interface and public target E2E.
6. Six-person controlled/field validation.
7. Decision gate.

Scaling и expansion рассматриваются только после пункта 7.

## Правило обновления

Документ обновляется, если:

1. изменена active phase;
2. достигнут или изменён exit gate;
3. выявлена новая обязательная зависимость;
4. validation decision меняет дальнейший порядок.

Execution details живут в issues/working specs; historical snapshots — в archive/audits.
