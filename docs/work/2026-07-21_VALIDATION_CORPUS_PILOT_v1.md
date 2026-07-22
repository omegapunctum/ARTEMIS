# ARTEMIS — Validation Corpus Pilot v1

## Статус

- Тип: approved execution contract for issue #285.
- Дата: 2026-07-21.
- Scope: comparison-first Round 0 corpus.
- Не является заявлением о зрелом MVP-корпусе.
- Execution: V2 cohort expansion загружен в Airtable 2026-07-22; V3 Relation graph остаётся открытым.

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

Этого достаточно для проверки сравнения, provenance и различения Relation/Similarity. Более широкий ориентир 100–150 Features, 50+ Relations, 3 Stories и 5–10 reference Slices сохраняется как maturity reference, а не как входной барьер Round 0.

## 2. Текущий baseline

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

Status остаётся `building`. Прохождение semantic gate означает publish-safe данные, но не comparison readiness.

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

## 5. Исполнимый профиль

Владельцы контракта:

- `scripts/content_profile.py` — детерминированный расчёт метрик и readiness;
- `data/content_profile.json` — checked-in snapshot;
- `scripts/export_airtable.py` — обновляет snapshot при экспорте;
- `scripts/release_check.py` — блокирует stale или вручную искажённый snapshot;
- `.github/workflows/etl.yml` — проверяет dry-run artifact.

Release не блокируется только потому, что corpus ещё `building`: это честное состояние активной работы. Release блокируется, если профиль отсутствует, не совпадает с данными или semantic artifacts не проходят gate.

## 6. Граница Stories и Research Slices

Этот corpus contract проверяет data prerequisites для comparison-first Round 0. Он не объявляет публичные Stories или Research Slice loop готовыми.

- deployment и save → reopen → share принадлежат issue #286;
- reference Slices создаются только на работающем public loop;
- curated Story создаётся поверх reviewed Features/Relations после подтверждения Slice E2E;
- полная внешняя validation не начинается до выполнения соответствующих runtime criteria.

## 7. Acceptance для #285

Issue #285 закрывается, когда:

- `data/content_profile.json.readiness.status == comparison_ready`;
- semantic gate проходит без blocking errors;
- профиль содержит 30–40 Features, 6–8 cohorts и 12–20 Relations;
- Source/Media/evidence coverage достигает утверждённых порогов;
- фактический content batch и control-read evidence задокументированы.

Достижение maturity reference 100–150 / 50+ не требуется для закрытия сокращённого пилота и рассматривается только после пользовательского decision gate.
