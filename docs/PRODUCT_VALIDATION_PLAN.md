# ARTEMIS — PRODUCT VALIDATION PLAN

## Статус

- Тип: canonical validation gate document.
- Версия: 1.1.
- Дата: 2026-07-24.
- Применяется до открытия product expansion и general-platform work.

## 1. Цель

Проверить, помогает ли Architecture Atlas MVP продвинутому студенту истории архитектуры выполнить реальную сравнительную задачу лучше, чем обычный каталог/список: получить evidence-aware вывод и сохранить его как повторно используемый Research Slice.

Validation не является визуальным preference test.

Validation состоит из трёх независимых gate:

1. `USABILITY` — пользователь способен выполнить сценарий.
2. `COGNITIVE VALUE` — результат меняет или углубляет понимание и связан с evidence.
3. `BEHAVIORAL VALUE` — пользователь самостоятельно возвращается, изменяет или передаёт сохранённое исследование.

Прохождение только `USABILITY` не доказывает продуктовую ценность.

## 2. Исследовательские вопросы

1. Понимает ли пользователь назначение ARTEMIS за первые минуты?
2. Даёт ли связка map + time + detail преимущество перед обычным каталогом?
3. Может ли пользователь отличить факт, relation, similarity и interpretation?
4. Создаёт ли Compare новое понимание темы?
5. Воспринимается ли Research Slice как полезный результат?
6. Хочет ли пользователь вернуться или поделиться срезом?
7. Содержит ли Slice исследовательский вопрос, evidence, заметку/вывод и uncertainty, а не только Saved View?
8. Даёт ли spatial-temporal surface измеримое преимущество относительно catalogue/list baseline?

## 3. Участники

Primary cohort: 5–8 продвинутых студентов истории архитектуры/искусства, работающих над сравнительным эссе, семинаром или исследовательским заданием.

Secondary exploratory cohort не влияет на прохождение primary gate:

- 1–2 преподавателя или куратора;
- профессиональные исследователи — только для проверки требований к provenance и corpus depth.

Участник не должен быть знаком с внутренней терминологией ARTEMIS.

## 4. Сценарий теста

### Task 1 — orientation

Объяснить своими словами, для чего предназначен продукт, и найти заданное направление/период.

### Task 2 — find and compare

Найти два объекта из разных регионов и сравнить период, направление, признаки и источники.

Задача выполняется в двух сопоставимых вариантах:

- контроль: catalogue/list/detail без spatial-temporal workspace;
- ARTEMIS: map + time + compare + evidence.

Порядок вариантов чередуется между участниками. Сравниваются время, качество вывода, обнаружение связей и уверенность в evidence.

### Task 3 — relation literacy

Найти документированную relation и объяснить, чем она отличается от similarity.

### Task 4 — slice

Сохранить вопрос, выбранные объекты, evidence, заметку/вывод, uncertainty и текущий Saved View в Research Slice.

### Task 5 — return

Закрыть сценарий, повторно открыть Slice и проверить восстановление контекста.

### Task 6 — share

Получить read-only ссылку и объяснить, что увидит получатель.

### Task 7 — field follow-up

На реальной учебной задаче в течение 7 дней самостоятельно:

- повторно открыть Slice;
- изменить или дополнить вывод;
- либо передать read-only результат преподавателю/коллеге.

## 5. Метрики и gates

### 5.1 USABILITY

- task completion rate;
- time to first useful comparison;
- число критических подсказок модератора;
- save/restore technical success;
- relation/similarity classification accuracy;
- source/provenance discovery rate;

Thresholds:

- не менее 80% завершают core tasks;
- median time to useful comparison — до 5 минут;
- 100% технический успех save/restore в контролируемых прогонах;
- не менее 80% корректно различают relation и similarity;
- не менее 70% самостоятельно находят provenance;
- отсутствуют критические unsupported factual claims.

### 5.2 COGNITIVE VALUE

Обязательные evidence:

- participant формулирует новое или уточнённое понимание;
- вывод связан минимум с одним видимым source/relation;
- independent rubric оценивает качество вывода в control и ARTEMIS вариантах;
- участник может объяснить, какую роль сыграли map/time и какую — evidence/compare.

Threshold:

- не менее 70% primary cohort формулируют обоснованный новый/уточнённый вывод;
- ARTEMIS не уступает control по времени и превосходит его по quality rubric либо обнаружению evidence-backed relations.

Если преимущество создаёт Compare/Evidence, но не map + time, решение должно быть `NARROW`, а Comparison Workspace — стать центральной поверхностью.

### 5.3 BEHAVIORAL VALUE

Обязательные evidence:

- самостоятельный reopen;
- изменение/дополнение Slice или read-only share;
- связь действия с реальной учебной задачей, а не просьбой модератора.

Directional threshold для малого пилота:

- не менее 60% primary cohort выполняют хотя бы одно самостоятельное reuse-действие в течение 7 дней.

Threshold не является статистическим доказательством рынка; он определяет, достоин ли loop следующего пилота.

## 6. Evidence package

Для каждой волны сохраняются:

- версия commit/deployment;
- dataset version;
- anonymized participant profile;
- task outcomes;
- control-vs-ARTEMIS comparison;
- cognitive-value rubric и evidence links;
- 7-day reuse outcomes;
- blockers и observed behavior;
- screenshots/recording references при наличии согласия;
- decision log: keep, change, remove;
- список issues с severity.

## 7. Validation rounds

### Round 0 — internal truth check

Проверить public/runtime/data claims до приглашения пользователей.

### Round 1 — comprehension prototype

5–8 primary users, основной loop, epistemic literacy и control-vs-ARTEMIS comparison.

### Round 2 — corrected pilot

Повторить наиболее проблемные задачи после изменений и провести 7-day field follow-up. Не добавлять новый feature scope между раундами без evidence.

## 8. Decision gate

После Round 2 принимается одно решение:

- `ITERATE` — ценность подтверждена, но нужны точечные исправления;
- `EXPAND` — пройдены usability, cognitive и behavioral gates; можно планировать следующий domain/product layer;
- `NARROW` — ценность подтверждена только для Compare/Evidence или другого более узкого сценария;
- `STOP/RETHINK` — core loop не подтверждён.

Scaling, Courses expansion и AI generation не открываются до явно зафиксированного `EXPAND` либо отдельного обоснованного решения.

Решение и supporting evidence фиксируются в `VALIDATION_DECISION.md`. Пока документ имеет статус `PENDING`, расширение запрещено.
