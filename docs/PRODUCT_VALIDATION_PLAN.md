# ARTEMIS — PRODUCT VALIDATION PLAN

## Статус

- Тип: historical Concept v2 validation protocol.
- Версия: 2.0 (superseded active protocol).
- Дата: 2026-07-26.
- Lifecycle: `SUPERSEDED AS ACTIVE PROTOCOL BY FOUNDATION V3`.
- Content prerequisite: три `READY` module из `docs/work/2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.

- Use: retained for Architecture Atlas evidence-history only.
- Active validation design: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md`.
- This document must not authorize #323–#325 or make map/time optional.

## 1. Цель

Проверить, помогает ли Architecture Atlas primary user создать более сильный и повторно используемый evidence-backed Research Brief, чем:

1. same-content list/detail workflow без map/time;
2. обычный исследовательский workflow самого участника.

Validation не является preference test, demo feedback или проверкой технической сохранности данных.

Три независимых gate:

- `USABILITY` — пользователь способен завершить core loop.
- `COGNITIVE VALUE` — Research Brief становится сильнее и epistemically точнее.
- `BEHAVIORAL VALUE` — результат самостоятельно используется в реальной работе.

Прохождение только `USABILITY` не подтверждает product thesis.

## 2. Primary cohort

Основной пилот: ровно 6 primary participants в одной волне.

Участник:

- старшекурсник или магистрант истории архитектуры/искусства;
- имеет сравнительное задание со сроком в ближайшие 1–2 недели;
- не знаком с внутренней терминологией ARTEMIS;
- не участвовал в подготовке corpus.

Допускаются 1–2 преподавателя/куратора для оценки rubric и provenance. Их результаты не входят в primary thresholds.

При расширении выборки результаты первой шестёрки не пересчитываются задним числом. Каждая новая wave записывается отдельно.

## 3. Experimental design

### 3.1 Baseline A — same content

Контроль содержит те же Features, Claims, Sources и EvidenceLinks, что ARTEMIS, но показывает их через list/detail/compare без map и timeline.

Purpose: изолировать дополнительную ценность spatial-temporal lenses.

### 3.2 Baseline B — normal workflow

Участник решает сопоставимую задачу своими обычными инструментами: browser, notes, library resources or other personally used workflow.

Purpose: проверить end-to-end usefulness, а не только компонентное преимущество.

### 3.3 Assignment and order

- используются эквивалентные, но не одинаковые вопросы из `READY` modules;
- порядок ARTEMIS/Baseline A counterbalanced;
- Baseline B выполняется на отдельном сопоставимом вопросе;
- timebox одинаков для controlled conditions;
- участник заранее получает одинаковый output brief;
- moderator не объясняет epistemic answer и не подсказывает, какой relation считать доказанным.

Порядок и module assignment фиксируются до первого participant и не меняются после просмотра результатов.

## 4. Обязательный output

Каждое условие заканчивается Research Brief со следующими полями:

1. question;
2. selected Features and rationale;
3. major Claims;
4. EvidenceLinks and locators;
5. substantive Relations;
6. findings;
7. conclusion or `unresolved`;
8. uncertainty;
9. references.

ARTEMIS additionally records revision and Saved View identifiers.

Пустой или технически сохранённый Brief без evidence chain считается незавершённым.

## 5. Test tasks

### Task 1 — orientation

Своими словами объяснить назначение продукта и определить, где начинается исследовательский вопрос.

### Task 2 — compare

Выбрать 2–3 Features и сопоставить их по заданным comparative lenses.

### Task 3 — epistemic literacy

Для предложенных примеров различить:

- factual/interpretive/hypothetical Claim;
- substantive Relation;
- shared classification;
- computed Similarity;
- supported, challenged and missing evidence.

### Task 4 — evidence chain

Связать major Claims с EvidenceLinks и повторно найти основание по locator.

### Task 5 — conclusion

Сформулировать conclusion либо explicit `unresolved`; назвать material uncertainty.

### Task 6 — save and transfer

Сохранить revision, повторно открыть её и получить revision-pinned read-only Brief.

До реализации immutable revisions test package обязан честно отмечать current share как mutable/live и не засчитывать его как reproducibility success.

### Task 7 — field follow-up

В течение 7 дней без дополнительной просьбы модератора:

- перенести часть Brief в реальное задание;
- создать новую revision с дополнением;
- либо передать revision/Brief преподавателю или коллеге.

## 6. Blind quality rubric

Два независимых evaluator не знают, в каком условии создан Brief. Они оценивают каждую dimension от `0` до `4`:

| Dimension | Что оценивается |
|---|---|
| Correctness | отсутствие явных фактических/логических ошибок |
| Evidence traceability | major Claims ведут к релевантным sources и locators |
| Comparative depth | вывод действительно сопоставляет объекты, а не перечисляет |
| Epistemic calibration | classification/similarity/uncertainty не выданы за доказанную Relation |
| Conclusion clarity | вывод отвечает на вопрос или честно фиксирует unresolved |

Total range: `0–20`.

Evaluator также отмечает critical error:

- invented source;
- unsupported causal/influence claim;
- material contradiction with provided evidence;
- classification or Similarity presented as proved Relation;
- uncertainty hidden in a way that changes conclusion.

Если оценки различаются более чем на 1 point по dimension, evaluator обсуждают только rubric interpretation и фиксируют reconciled score. Исходные оценки сохраняются.

## 7. Gate thresholds

Для малого `n=6` primary results сообщаются абсолютными числами; проценты могут быть только вторичным представлением.

### 7.1 USABILITY

Gate проходит, если:

- минимум 5 из 6 завершают Tasks 2–5 без critical moderator assist;
- 6 из 6 технических controlled runs сохраняют и повторно открывают доступный current artifact;
- минимум 5 из 6 находят provenance и locator;
- 6 из 6 не принимают shared classification/Similarity за доказанную Relation в финальном Brief.

### 7.2 COGNITIVE VALUE

Gate проходит, если:

- минимум у 4 из 6 ARTEMIS Brief выше соответствующего controlled baseline минимум на 2 total rubric points;
- ни один ARTEMIS Brief не содержит critical epistemic error;
- минимум 4 из 6 major conclusions полностью traceable либо честно marked unresolved;
- минимум 4 из 6 участников могут отдельно объяснить вклад Compare/Evidence;
- spatial-temporal increment анализируется отдельно и не выводится из общей оценки продукта.

Spatial-temporal lens считается подтверждённой для текущего vertical, если минимум у 3 из 6:

- participant называет конкретный вывод, который был получен или скорректирован благодаря map/time;
- этот вклад виден в Brief или observed behavior;
- same-content baseline не дал тот же вывод столь же явно в timebox.

Если core cognitive gate пройден, а spatial-temporal criterion нет, обязательное решение — `NARROW`.

### 7.3 BEHAVIORAL VALUE

Gate проходит, если минимум 3 из 6 в течение 7 дней без новой просьбы:

- используют Brief в реальном задании;
- создают содержательно изменённую revision;
- или передают результат реальному collaborator/teacher.

Простое открытие ссылки или действие, выполненное только по напоминанию, не засчитывается.

## 8. Evidence package

До decision сохраняются:

- commit, deployment and runtime capability state;
- dataset and module versions;
- assignment/counterbalance table, fixed before sessions;
- anonymized participant profiles;
- raw task outcomes and critical assists;
- all produced Briefs;
- both evaluator score sheets and reconciled scores;
- evidence-link/locator failures;
- epistemic errors;
- map/time contribution evidence;
- normal-workflow benchmark notes;
- 7-day field outcomes;
- preparation and review cost per module;
- issues with severity;
- decision log: keep, change, remove.

## 9. Decision rules

После complete evidence package принимается одно решение:

- `ITERATE` — все три gate подтверждают core direction, но current loop требует ограниченных исправлений.
- `EXPAND` — все три gate пройдены; разрешается только одна отдельно названная branch с собственным scope/evidence plan.
- `NARROW` — Compare/Evidence/Brief полезны, но map/time либо другая заявленная часть ядра не подтверждена.
- `STOP/RETHINK` — Brief не сильнее control, evidence literacy не достигнута или behavioral value отсутствует после допустимой corrective wave.

Automatic expansion запрещён. Даже `EXPAND` не открывает одновременно AI, Courses, new domains и institutional workflows.

Решение записывается в `VALIDATION_DECISION.md`. Пока оно `PENDING`, внешний пилот может готовиться, но product expansion запрещён.
