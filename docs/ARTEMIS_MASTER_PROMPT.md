# ARTEMIS — МАСТЕР-ПРОМПТ v5.0

Статус: canonical operational governance document for AI agents and assistants in ARTEMIS.
Назначение: единая инструкция для ИИ-ассистентов и агентов, работающих над проектом ARTEMIS.

---

## 1. РОЛЬ ПРОЕКТА

North Star ARTEMIS — evidence-first human research environment with privileged spatial-temporal lenses and versioned outcomes.
В активном operational контуре ARTEMIS — focused Architecture Atlas vertical:
- один primary user: старшекурсник/магистрант истории архитектуры с реальным сравнительным заданием;
- один JTBD: превратить вопрос о 2–3 объектах в evidence-backed Research Brief;
- Claim/EvidenceLink and locator as epistemic foundation;
- map/time как independently validated lenses;
- target model: Investigation → immutable Slice Revision → Research Brief, with nested Saved View;
- current ResearchSlice v2 as mutable compatibility runtime;
- public capability не может быть заявлена только на основании backend-кода;
- Stories/Courses, AI, institutional workflow, UGC and new domains заморожены до branch-specific decision.

Ключевой принцип продукта:
**question → claims → evidence → comparison → conclusion/unresolved → revision → brief → reuse**.

Первая ценность:
**evidence-aware object comparison**.

Ключевой повторно используемый артефакт:
**immutable Slice Revision and its Research Brief**.

---

## 2. ОСНОВНЫЕ ПРАВИЛА ИСТОЧНИКА ИСТИНЫ

В проекте действует иерархия документации с отдельным foundation-layer.

### 2.1 Canonical source of truth
Единственный реестр canonical документов, порядок чтения и маршрутизация владельцев смысла находятся в `docs/FOUNDATION_INDEX.md`. Этот prompt не дублирует реестр.

Правило:
- если информация не синхронизирована с canonical docs, она не должна считаться окончательной;
- `AGENTS.md` является repository entrypoint для агентов и направляет к этому prompt и canonical owner docs;
- `FOUNDATION_INDEX.md` определяет, какой документ владеет конкретным решением;
- `docs/work/README.md` определяет lifecycle working-документов;
- старые целевые имена вроде `ARCHITECTURE.md`, `RELEASE_SYSTEM.md` и `ROADMAP.md` не должны использоваться как текущий canonical-набор, если они не существуют как действующие source-of-truth файлы в репозитории.

### 2.2 Working docs
`docs/work/*` — рабочие документы текущего цикла.
Они помогают в разработке, но не заменяют canonical layer.

Отдельное правило:
- lifecycle и допустимое использование каждого working-документа определяет `docs/work/README.md`;
- архивная `docs/archive/ARTEMIS_AI_STRATEGY_v1_0.md` сохраняет historical context и не открывает AI scope.

### 2.3 Audits
`docs/audits/*` — документы проверки.
Они не определяют архитектуру или roadmap, а только проверяют их.

### 2.4 Archive
`docs/archive/*` и старые snapshot-файлы — только historical reference.
Их нельзя использовать как актуальный source of truth.

---

## 3. РОЛИ ИИ-ИНСТРУМЕНТОВ

| Инструмент | Основная ответственность |
|---|---|
| ChatGPT | архитектура, системный анализ, документация, промпты, приоритизация |
| Codex | точечные patch-изменения, ETL, backend, CI, tests |
| Claude | исторический контент, тексты, таблицы, CSV, нормализация данных |

Правила:
- роли не смешивать без явной причины;
- один запрос — один тип артефакта;
- сначала решение и документация, потом patch в репозиторий.

---

## 4. ТЕХНИЧЕСКИЙ СТЕК (ЗАФИКСИРОВАН)

### Frontend
- Vanilla JavaScript ES modules
- HTML
- CSS
- MapLibre

### Backend
- FastAPI
- SQLite как текущий baseline
- дальнейший рост допускает PostgreSQL

### Data
- Airtable как curated source
- ETL публикует canonical данные в `data/*`
- public map читает только `data/features.geojson`

### Hosting / automation
- GitHub Pages для frontend
- backend отдельно
- GitHub Actions для ETL / checks / release workflows
- release/workflow слой должен быть согласован с checked-in `data/*` и текущим набором canonical docs

### Жёсткие запреты
- React / Vue / Angular / TypeScript без отдельного архитектурного решения
- прямой доступ frontend к Airtable
- хранение токенов в browser storage
- превращение `/api/map/feed` в второй canonical public source
- скрытое изменение архитектуры через "маленький патч"

---

## 5. АРХИТЕКТУРНЫЕ ИНВАРИАНТЫ

### 5.1 Public data contract
- `data/features.geojson` — единственный canonical public map source.
- `features.json` — не public source of truth.
- runtime API не подменяет published `/data/*`.

### 5.2 Runtime boundaries
- `app/` — единственный backend runtime.
- legacy root package `api/` удалён; competing backend package запрещён.
- moderation path не равен publish path.
- upload runtime contract должен быть синхронизирован между `js/*`, `app/uploads/*`, `README.md` и tests; нельзя допускать, чтобы frontend и backend ожидали разные обязательные поля одного и того же endpoint.

### 5.3 Governance
- intake → review 1 → review 2 → batch publish → overwrite public dataset.
- publish не выполняется напрямую из runtime UI.
- UGC не становится canonical public content без `CONTENT_GOVERNANCE.md`, ETL/export validation и release discipline.

### 5.4 Auth
- access token — только в памяти клиента;
- refresh token — только в httpOnly cookie;
- текущие auth/session guarantees следует трактовать как baseline-capable, но не fully production-hardened для multi-instance deployments;
- hardening beyond original memory-only MVP уже существует, но не должен описываться как finished production-ready multi-node architecture.

### 5.5 PWA
- private/auth requests не должны кэшироваться;
- PWA semantics проверяются по реальному поведению, а не по наличию/отсутствию строк в `sw.js`.

### 5.6 Foundation invariants
- Evidence-aware comparison создаёт первую пользовательскую ценность.
- Claim is the unit of evidence; Source uses EvidenceLink and locator.
- Claim kind, origin, review, confidence, evidence state and uncertainty are independent.
- Relation is a structured Claim; classification and Similarity are separate.
- `same_movement` does not count as substantive Relation.
- Target research model is Investigation → immutable Slice Revision → Research Brief.
- Saved View is nested context, not the result.
- Current mutable ResearchSlice/content_version/share must not be described as immutable/revision-pinned.
- Stories/Courses/AI/institutional/new-domain branches require independent decisions.
- AI, if opened, remains origin/assistant and never Source.

---

## 6. ТЕКУЩИЙ ПОРЯДОК РАБОТ

Активный рабочий контур — **Phase 4.5 Concept-Locked Product Validation**.

Порядок:

1. three deep research modules;
2. Claim/Evidence/Relation migration;
3. Investigation/revision/Brief migration;
4. research interface and public target E2E;
5. six-person controlled and field validation;
6. explicit outcome in `VALIDATION_DECISION.md`.

Phase 5 Scaling/Hardening приостановлена, кроме critical security/reliability и MVP deployment blockers. Phase 6 Product Expansion заблокирована, пока `VALIDATION_DECISION.md` не содержит `EXPAND` либо отдельного canonical decision.

---

## 7. ПРАВИЛО DOCS-FIRST

Для изменений в ARTEMIS действует порядок:
1. анализ;
2. определение затронутых foundation/canonical/working docs;
3. обновление проектной документации;
4. проверка внутренней согласованности;
5. только потом patch / команда для Codex;
6. затем тесты, smoke и audit note.

Если изменение затрагивает architecture / data contract / release semantics / docs hierarchy / product scope / research slice semantics / entity model / epistemic model / content governance / роль ИИ в продукте, нельзя сразу идти в код.

---

## 8. ПРАВИЛА ДЛЯ ЛЮБОГО ИЗМЕНЕНИЯ

### 8.1 Что обязательно определить до patch
- цель изменения;
- конкретные файлы;
- текущий конфликт;
- границы scope;
- проверки;
- какие canonical docs должны быть обновлены;
- затрагивает ли изменение active product decision set (`PROJECT_TRUTH.md`, `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `MVP_ARCHITECTURE_ATLAS.md`, `DATA_DICTIONARY.md`, `PRODUCT_VALIDATION_PLAN.md`) либо foundation contracts.

### 8.2 Что запрещено
- рефакторинг без явной причины;
- расширение scope по ходу patch;
- скрытое изменение API/контракта;
- изменение архитектуры под видом багфикса;
- развитие frozen Stories/Courses/AI/UGC scope до validation decision;
- использование AI-output как source-backed/canonical knowledge без governance;
- смешение fact/interpretation/hypothesis/AI-output/counterfactual;
- работа по старому архивному документу как по основному ориентиру.

### 8.3 Обязательная проверка после patch
- изменены только заявленные файлы;
- контракт не сломан;
- tests проходят;
- docs sync выполнен;
- foundation-layer не нарушен;
- нет competing architecture.

---

## 9. DEFINITION OF READY

Задача готова к исполнению, только если:
- проблема воспроизводима;
- указан ожидаемый результат;
- есть scope lock;
- названы конкретные файлы;
- понятны happy path и error case;
- ясно, требует ли задача обновления canonical docs;
- ясно, затрагивает ли задача foundation-layer.

Если один из пунктов отсутствует, задача не считается готовой.

---

## 10. DEFINITION OF DONE

Задача считается выполненной только если:
- patch применён чисто;
- изменены только нужные файлы;
- tests прошли;
- happy path подтверждён;
- error case подтверждён;
- архитектурные инварианты сохранены;
- foundation инварианты сохранены;
- docs sync выполнен;
- нет скрытого drift после изменения.

---

## 11. ПРАВИЛА РАБОТЫ С ДОКУМЕНТАМИ

### Обновлять canonical docs обязательно при изменении:
- architecture boundaries;
- backend/runtime entrypoints;
- data contract;
- ETL/export/publish semantics;
- release gate / readiness / smoke semantics;
- upload/auth/runtime API surface;
- статуса фаз и порядка работ;
- миссии, продуктового ядра и допустимой роли ИИ в проекте;
- Investigation/revision/SavedView/Brief semantics;
- Claim/EvidenceLink/uncertainty/source discipline;
- entity/relation/classification/similarity model;
- content governance / UGC promotion / moderation trust model;
- AI behavior / AI-output / AI policy.

### Не использовать audits как замену canonical docs
Если аудит выявил конфликт, нужно обновить соответствующий canonical doc, а не только добавить новый audit file.

### Не использовать working docs как скрытый foundation-layer
Если working doc начинает определять устойчивое правило продукта, AI, content governance, entity model или epistemic behavior, его смысл должен быть перенесён в canonical/foundation doc.

### Не использовать archive как текущий ориентир
Старые v3.x snapshot-документы можно читать только для истории решений.

---

## 12. ФОРМАТ ОТВЕТА ДЛЯ РАБОЧИХ ЗАДАЧ

Если требуется анализ:
- сначала вывод;
- затем список конфликтов;
- затем next action.

Если требуется документация:
- сначала готовый документ или пакет документов;
- затем краткий комментарий, что именно изменилось;
- не дублировать уже действующую информацию между foundation/canonical docs, а только связывать роли этих документов.

Если требуется задача для Codex:
- GOAL
- CONTEXT
- DO
- SCOPE LOCK
- CHECKS
- OUTPUT FORMAT

---

## 13. АНТИ-ПАТТЕРНЫ

Запрещено:
- "сделай всё сразу";
- "улучши весь проект";
- patch без scope lock;
- patch без checks;
- работа только по устаревшему snapshot-документу;
- смешение roadmap, audits и archive в одном operational файле;
- добавление нового уровня архитектуры без отдельного решения;
- product expansion без проверки against foundation-layer;
- AI feature без `AI_POLICY.md` и `EPISTEMIC_CONTRACT.md`;
- UGC/public content feature без `CONTENT_GOVERNANCE.md`;
- story/course feature, обходящая `RESEARCH_SLICE_CONTRACT.md`;
- entity/relation expansion, обходящая `ENTITY_MODEL.md`.

---

## 14. КРАТКАЯ ЦЕЛЬ ДЛЯ ВСЕХ АГЕНТОВ

Не расширять ARTEMIS ценой потери целостности.

Сначала:
- coherent Claim/Evidence foundation;
- three deep research modules;
- versioned Investigation/revision/Brief outcome;
- honest public E2E;
- blind cognitive and behavioral validation.

Потом:
- one evidence-backed branch;
- only branch-specific implementation;
- no automatic platform/AI/Courses expansion.
