# ARTEMIS — PRODUCT VALIDATION PLAN

## Статус

- Тип: canonical validation gate document.
- Версия: 1.0.
- Дата: 2026-07-16.
- Применяется до открытия product expansion и general-platform work.

## 1. Цель

Проверить, помогает ли Architecture Atlas MVP реальному пользователю исследовать и сравнивать архитектурные объекты, понимать доказательность связей и сохранять полезный Research Slice.

Validation не является визуальным preference test.

## 2. Исследовательские вопросы

1. Понимает ли пользователь назначение ARTEMIS за первые минуты?
2. Даёт ли связка map + time + detail преимущество перед обычным каталогом?
3. Может ли пользователь отличить факт, relation, similarity и interpretation?
4. Создаёт ли Compare новое понимание темы?
5. Воспринимается ли Research Slice как полезный результат?
6. Хочет ли пользователь вернуться или поделиться срезом?

## 3. Участники

Первая волна: 5–8 человек.

Желаемый состав:

- 3–4 студента истории архитектуры/искусства;
- 1–2 преподавателя;
- 1–2 исследователя, автора или куратора.

Участник не должен быть знаком с внутренней терминологией ARTEMIS.

## 4. Сценарий теста

### Task 1 — orientation

Объяснить своими словами, для чего предназначен продукт, и найти заданное направление/период.

### Task 2 — find and compare

Найти два объекта из разных регионов и сравнить период, направление, признаки и источники.

### Task 3 — relation literacy

Найти документированную relation и объяснить, чем она отличается от similarity.

### Task 4 — slice

Сохранить выбранные объекты, время и заметку в Research Slice.

### Task 5 — return

Закрыть сценарий, повторно открыть Slice и проверить восстановление контекста.

### Task 6 — share

Получить read-only ссылку и объяснить, что увидит получатель.

## 5. Метрики

Обязательные:

- task completion rate;
- time to first useful comparison;
- число критических подсказок модератора;
- save/restore technical success;
- relation/similarity classification accuracy;
- source/provenance discovery rate;
- qualitative value statement участника.

Предлагаемые thresholds:

- не менее 80% завершают core tasks;
- median time to useful comparison — до 5 минут;
- 100% технический успех save/restore в контролируемых прогонах;
- не менее 80% корректно различают relation и similarity;
- не менее 70% самостоятельно находят provenance;
- отсутствуют критические unsupported factual claims.

## 6. Evidence package

Для каждой волны сохраняются:

- версия commit/deployment;
- dataset version;
- anonymized participant profile;
- task outcomes;
- blockers и observed behavior;
- screenshots/recording references при наличии согласия;
- decision log: keep, change, remove;
- список issues с severity.

## 7. Validation rounds

### Round 0 — internal truth check

Проверить public/runtime/data claims до приглашения пользователей.

### Round 1 — comprehension prototype

5–8 пользователей, основной loop и epistemic literacy.

### Round 2 — corrected pilot

Повторить наиболее проблемные задачи после изменений. Не добавлять новый feature scope между раундами без evidence.

## 8. Decision gate

После Round 2 принимается одно решение:

- `ITERATE` — ценность подтверждена, но нужны точечные исправления;
- `EXPAND` — thresholds достигнуты, можно планировать следующий domain/product layer;
- `NARROW` — ценность есть только в более узком сценарии;
- `STOP/RETHINK` — core loop не подтверждён.

Scaling, Courses expansion и AI generation не открываются до явно зафиксированного `EXPAND` либо отдельного обоснованного решения.
