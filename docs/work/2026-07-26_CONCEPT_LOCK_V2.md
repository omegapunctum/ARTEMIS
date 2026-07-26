# ARTEMIS — CONCEPT LOCK v2

## Статус

- Тип: approved foundation decision record.
- Дата решения: 2026-07-26.
- Статус: `LOCKED FOR CURRENT VALIDATION CYCLE`.
- Scope: mission, core value, research-work model, epistemic model, relation boundary, validation corpus and decision protocol.
- Не является runtime/API specification и не утверждает, что target model уже реализована.

Этот документ фиксирует причины и границы решения. Нормативный смысл перенесён в соответствующие canonical owner documents. При конфликте owner document имеет приоритет.

## 1. Причина пересмотра

Предыдущий foundation cycle успешно ограничил scope, отделил capability truth от концепции и сделал evidence-aware comparison центральным сценарием. Однако три ещё не доказанные гипотезы были описаны почти как постоянные истины:

1. map и timeline обязательно создают основную ценность;
2. mutable `ResearchSlice` является окончательной единицей долгосрочного исследования;
3. entity-level Sources и существующие Relations достаточны для доказательного вывода.

Главный риск — построить дисциплинированную систему сохранения контекста, которая не делает исследовательский вывод сильнее и проверяемее.

## 2. Зафиксированные решения

### D1. Единственная миссия — усиливать человеческое исследование

ARTEMIS создаётся для человека, который формулирует вопрос, проверяет основания и остаётся субъектом суждения.

AI compatibility остаётся архитектурной опцией. AI research infrastructure, benchmark corpus и reasoning experiments не являются второй миссией и не определяют текущую продуктовую модель.

### D2. Ядро ценности — проверяемая цепочка от вопроса к выводу

Инвариант ARTEMIS:

`Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved`

Карта, timeline, фильтры и object cards имеют ценность только в той мере, в какой усиливают эту цепочку.

### D3. Map и time — привилегированные линзы, а не догма

Пространство и время остаются сильной дифференциацией и обязательным предметом validation. Но не каждое значимое утверждение обязано быть пространственным или временным.

Если same-content baseline покажет, что Compare/Evidence создаёт ценность, а map/time не дают измеримого преимущества, решение должно быть `NARROW`, а не искусственное сохранение map-first identity.

### D4. Research work имеет четыре уровня

1. `Investigation` — развивающаяся работа с устойчивой identity.
2. `Slice Revision` — неизменяемая версия Investigation в конкретный момент.
3. `Saved View` — вложенный UI-контекст map/time/filter/selection.
4. `Research Brief` — читаемая и переносимая проекция одной Slice Revision.

Research Brief не является отдельным источником истины: он детерминированно отображает revision. Update Investigation создаёт новую revision; прежняя revision не переписывается.

### D5. Claim является атомарной единицей доказательности

`Source` не «подтверждает объект вообще». Он связывается с конкретным `Claim` через `EvidenceLink` и locator.

Epistemic dimensions независимы:

- claim kind;
- origin;
- review state;
- confidence;
- evidence state;
- uncertainty.

`ai_generated`, `verified`, `source_backed`, `hypothesis` и `uncertain` больше не считаются значениями одного общего статуса.

### D6. Relation — структурированный Claim

Relation утверждает конкретную связь `subject → predicate → object` и наследует claim/evidence requirements.

`same_movement` не является содержательной Feature↔Feature Relation. Это производное documented shared classification: две отдельные classification assertions связывают Features с одним Movement/Layer.

Current `same_movement` records сохраняются как legacy compatibility data до отдельной миграции. Их запрещено:

- считать доказательством relation-value;
- включать в substantive Relation threshold;
- автоматически преобразовывать в influence/derivation claims.

### D7. Validation corpus строится исследовательскими модулями

Шесть количественных cohorts остаются техническим corpus envelope, но не достаточным evidence для product validation.

Перед внешним пилотом нужны три глубоких модуля. Каждый содержит:

- один реальный сравнительный вопрос;
- 4–6 объектов;
- 6–10 claims;
- claim-level EvidenceLinks с locators;
- минимум две substantive Relations;
- минимум один challenged, contested или medium-confidence элемент;
- reference Research Brief для blind scoring.

Execution contract: `docs/work/2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.

### D8. Validation оценивает результат, а не симпатию к интерфейсу

Обязательны:

- same-content baseline без map/time;
- benchmark обычного workflow участника;
- counterbalanced order;
- одинаковый timebox;
- Research Brief как обязательный output;
- blind scoring двумя независимыми оценщиками;
- абсолютные результаты для малого `n`;
- 7-day unprompted reuse.

### D9. После core proof действует ветвящееся управление

Guided exploration, AI assistance, institutional workflows и новые domains открываются независимыми evidence gates. Они не образуют обязательную линейную лестницу и не должны открываться одним общим `EXPAND`.

### D10. Concept target не равен текущему runtime

Текущий `ResearchSlice v2` остаётся рабочим mutable persistence envelope. Он не реализует:

- first-class `Investigation`;
- immutable revisions;
- pinned dataset snapshot/version semantics;
- first-class Claims/EvidenceLinks;
- deterministic citation-ready Brief export.

До отдельного docs/data/runtime migration эти возможности имеют статус `CONCEPT TARGET`.

## 3. Миграционная карта

| Current shape | Target meaning | Текущее решение |
|---|---|---|
| Mutable `ResearchSlice` row | Investigation draft/latest working state | Сохранить для compatibility; не называть immutable revision |
| `content_version` counter | Revision number hint | Не считать reproducibility proof |
| `evidence_refs` to Source/Relation | Claim-level EvidenceLinks | Расширять только отдельной schema migration |
| `finding` | User-authored Claim | Не повышать в canonical knowledge без governance |
| `saved_view` | Optional nested research lens | Сохранить как компонент |
| Shared live Slice | Revision-pinned share | Current share считать live mutable capability; immutable share requires new contract |
| `same_movement` Relation | Shared classification projection | Retain, relabel/exclude, then migrate without inventing evidence |
| `epistemic_status` | Compatibility projection of independent axes | Не использовать как target schema |
| Six comparison cohorts | Technical coverage envelope | Не использовать как validation-ready corpus |

## 4. Что намеренно не решается этим пакетом

- backend/API migration;
- изменение Airtable schema и public JSON artifacts;
- relabeling UI;
- production deployment;
- полный documentation/repository audit;
- бизнес-модель и институциональный owner content;
- фактическая подготовка источников для трёх research modules;
- Stories, Courses или AI implementation.

Эти задачи должны следовать отдельными пакетами после принятия canonical model.

## 5. Критерии завершения Concept Lock v2

Concept Lock считается завершённым, когда:

1. canonical concept/product/epistemic/entity/research/validation documents не противоречат решениям D1–D10;
2. current reality явно отделена от target model;
3. прежний quantitative corpus не называется достаточным для external validation;
4. `same_movement` исключён из substantive relation-value;
5. three-module execution contract зарегистрирован;
6. executable documentation guard предотвращает возврат ключевых противоречий;
7. полный release/test gate проходит без runtime regression.
