# ARTEMIS — Validation Corpus Pilot v1

## Статус

- Тип: approved execution contract for issue #285.
- Дата: 2026-07-21.
- Scope: comparison-first Round 0 corpus.
- Не является заявлением о зрелом MVP-корпусе.
- Execution: V2 cohort expansion и V3 Relation graph загружены в Airtable 2026-07-22; профиль достиг `comparison_ready`.
- Concept Lock v2 supersession: остаётся historical/technical execution contract, но больше не является достаточным входом во внешнюю product validation.

После 2026-07-26:

- `comparison_ready` означает только прохождение legacy quantitative content profile;
- 10 `same_movement` records трактуются как documented shared-classification compatibility data;
- они не считаются substantive Relations и не доказывают relation-value;
- product-validation readiness требует три deep research modules из `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.

## 1. Решение

Для первой проверки comparison-first ценности утверждён сокращённый корпус вместо преждевременного набора 100–150 объектов.

Целевой envelope:

- 30–40 reviewed Features;
- 6–8 comparison cohorts, каждый минимум по 3 Features в одном опубликованном Layer;
- 12–20 reviewed evidence-backed Relations;
- 100% Features имеют reviewed Source;
- не менее 90% Features имеют reviewed primary Media;
- 100% Relations имеют reviewed evidence;
- 0 пустых опубликованных Layers;
- semantic gate имеет статус `ready` или `ready_with_warnings`.

Этот envelope оказался достаточным для технической проверки UI/export/provenance paths, но недостаточным для cognitive product validation. Более широкий количественный ориентир также не заменяет deep-module readiness.

## 2. Исходный baseline

`data/content_profile.json` фиксирует:

| Метрика | Сейчас | Минимум пилота | Gap |
|---|---:|---:|---:|
| Features | 19 | 30 | 11 |
| Comparison cohorts ≥3 Features | 0 | 6 | 6 |
| Reviewed Relations | 2 | 12 | 10 |
| Feature Source coverage | 100% | 100% | 0 |
| Primary Media coverage | 84.21% | 90% | 2 Media для текущих 19 |
| Relation evidence coverage | 100% | 100% | 0 |
| Published empty Layers | 0 | 0 | 0 |

На исходном snapshot status был `building`. Прохождение semantic gate означало publish-safe данные, но ещё не comparison readiness.

## 3. Состав минимального набора

Практический путь к 31 Feature без размывания классификации:

| Cohort / existing Layer | Сейчас | Добавить | После |
|---|---:|---:|---:|
| `classical_greece` | 1 | 2 | 3 |
| `roman_empire` | 1 | 2 | 3 |
| `gothic_europe` | 1 | 2 | 3 |
| `renaissance_italy` | 1 | 2 | 3 |
| `modernism_global` | 1 | 2 | 3 |
| `brutalism_uk` | 1 | 2 | 3 |

Это даёт 12 новых Features, 31 Feature всего и 6 реальных comparison cohorts. Конкретные объекты выбираются редакционно по наличию надёжного источника, географической/типологической вариативности и возможности доказательного сравнения; quota не является основанием для слабого объекта или Relation.

## 4. Content batches

### V1 — Rights and baseline cleanup

- закрыть 3 текущих Media-rights gap;
- сохранить 100% Source coverage;
- не менять публичные JSON вручную: source-of-truth остаётся Airtable.

### V2 — Cohort expansion

- добавить по 2 reviewed Features в шесть выбранных Layers;
- для каждого Feature до promotion создать reviewed primary Source;
- primary Media обязателен, если права подтверждены; batch должен удержать coverage ≥90%;
- не создавать новые singleton Layers.

#### V2 execution snapshot — 2026-07-22

V2 выполнен через Airtable в порядке `draft → control read → reviewed links → active/validated Feature`. Публичные JSON вручную не редактировались.

| Existing Layer | Добавленные Features | Primary evidence | Primary Media |
|---|---|---|---|
| `classical_greece` | Erechtheion; Temple of Apollo Epicurius at Bassae | Acropolis Museum; UNESCO | CC BY-SA 4.0; PD |
| `roman_empire` | Colosseum; Maison Carrée of Nîmes | Parco archeologico del Colosseo; UNESCO | CC BY-SA 2.5; CC BY-SA 4.0 |
| `gothic_europe` | Cologne Cathedral; Canterbury Cathedral | UNESCO; UNESCO | CC BY-SA 3.0; CC BY-SA 4.0 |
| `renaissance_italy` | Brunelleschi’s Dome; Villa Almerico Capra “La Rotonda” | Opera di Santa Maria del Fiore; official property site | CC BY-SA 4.0; CC BY-SA 4.0 |
| `modernism_global` | Bauhaus Building, Dessau; Sydney Opera House | UNESCO; UNESCO | CC BY-SA 4.0; CC BY-SA 3.0 |
| `brutalism_uk` | Preston Central Bus Station and Car Park; Park Hill, Sheffield | Historic England; Historic England | CC BY-SA 2.0; CC BY-SA 4.0 |

Airtable control read после promotion:

| Метрика | Результат |
|---|---:|
| Active + validated Features | 31 |
| Reviewed Source coverage | 31 / 31, 100% |
| Reviewed primary Media coverage | 28 / 31, 90.32% |
| Comparison cohorts ≥3 Features | 6 |
| Новые singleton Layers | 0 |
| Разорванные V2 Source/Media links | 0 |

Три прежних Media-rights gap остаются намеренно незакрытыми: Burj Khalifa, Villa Savoye и Centre Pompidou. Неподтверждённые изображения не публиковались; V2 достиг порога Media coverage за счёт двенадцати полностью лицензированных новых объектов.

Canonical `Export Airtable Data` snapshot создан 2026-07-22 в `06:26:26Z`: 31 Feature, 6 comparison cohorts, 31 reviewed Source, 28 reviewed Media и 2 reviewed Relation. Semantic gate: `ready_with_warnings`, 0 blocking errors, 14 контролируемых warnings. Content profile честно остаётся `building`; единственный незакрытый readiness check — ещё 10 Relations до минимального порога 12.

### V3 — Relation graph

- добавить минимум 10 Relations, чтобы достичь 12;
- каждый Relation получает reviewed evidence link и ограниченный `claim_note`;
- Relation не выводится из same-layer/time Similarity;
- предпочтительны связи, полезные для сравнения внутри cohort и между эпохами.

Каждый batch проходит Airtable control read, export, semantic gate, content-profile check и обычный release gate.

#### V3 execution snapshot — 2026-07-22

V3 выполнен через Airtable в порядке `draft Sources/Relations → draft RelationSources → control read → reviewed Sources → reviewed RelationSources → reviewed Relations`. Публичные JSON сформированы только canonical exporter; вручную они не редактировались.

| Cohort | Reviewed Relations | Evidence |
|---|---:|---|
| `classical_greece` | 1 | UNESCO Acropolis source covering the Parthenon and Erechtheion |
| `roman_empire` | 1 | Parco archeologico del Colosseo + UNESCO Maison Carrée |
| `gothic_europe` | 2 | UNESCO records for Cologne, Chartres and Canterbury |
| `renaissance_italy` | 2 | St. Peter’s reference + Opera del Duomo + Villa La Rotonda official site |
| `modernism_global` | 1 | UNESCO Bauhaus + UNESCO Le Corbusier/Villa Savoye |
| `brutalism_uk` | 3 | Historic England Park Hill/Preston + National Theatre official source |

Все 10 новых predicates имеют тип `same_movement`. На момент V3 они корректно отделялись от computed Similarity и имели reviewed classification evidence.

Concept Lock v2 уточняет их смысл: это pairwise compatibility projection двух ClassificationAssertions, а не substantive historical Relation. Они сохраняются без выдумывания новой evidence, исключаются из relation-value и должны быть перенесены только отдельной data migration.

Airtable control read после promotion:

| Метрика | Результат |
|---|---:|
| Reviewed Relations | 12 / 12 |
| Новые RelationSources | 19 / 19 reviewed |
| Всего RelationSources | 21 |
| Relations с evidence | 12 / 12, 100% |
| Relation-connected Features | 17 / 31, 54.84% |
| Разорванные Relation/Source/Feature links | 0 |

Canonical `Export Airtable Data` snapshot создан 2026-07-22 в `12:58:03Z`: 31 Feature, 6 comparison cohorts, 35 reviewed Sources, 28 reviewed Media и 12 reviewed Relations. Semantic gate: `ready_with_warnings`, 0 blocking errors, 14 прежних контролируемых warnings. `data/content_profile.json.readiness.status` стал `comparison_ready`; все gaps равны нулю.

## 5. Исполнимый профиль

Владельцы контракта:

- `scripts/content_profile.py` — детерминированный расчёт метрик и readiness;
- `data/content_profile.json` — checked-in snapshot;
- `scripts/export_airtable.py` — обновляет snapshot при экспорте;
- `scripts/release_check.py` — блокирует stale или вручную искажённый snapshot;
- `.github/workflows/etl.yml` — проверяет dry-run artifact.

Release не блокируется только потому, что corpus ещё `building`: это честное состояние активной работы. Release блокируется, если профиль отсутствует, не совпадает с данными или semantic artifacts не проходят gate.

## 6. Граница external validation

Этот corpus contract проверяет legacy technical data prerequisites. Он не объявляет external product validation, target Investigation/revision model или Stories ready.

- three deep modules must become `READY`;
- first-class claim/evidence and Brief behavior must be available to the test condition;
- current mutable Slice E2E does not prove immutable revision/share;
- Stories remain outside scope.

## 7. Acceptance для #285

Issue #285 закрывается, когда:

- `data/content_profile.json.readiness.status == comparison_ready`;
- semantic gate проходит без blocking errors;
- профиль содержит 30–40 Features, 6–8 cohorts и 12–20 Relations;
- Source/Media/evidence coverage достигает утверждённых порогов;
- фактический content batch и control-read evidence задокументированы.

Достижение maturity reference 100–150 / 50+ не требуется для закрытия исторического execution item и не должно выполняться до deep-module/validation evidence.
