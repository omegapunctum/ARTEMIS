# ARTEMIS — VALIDATION DECISION

## Статус

- Тип: canonical validation outcome document.
- Статус решения: `PENDING`.
- Дата последнего обновления: 2026-07-24.
- Evidence protocol: `PRODUCT_VALIDATION_PLAN.md`.
- Владелец смысла: доказанный результат product validation и разрешение либо запрет следующего product scope.

Этот документ фиксирует только принятое решение по итогам validation. Он не заменяет протокол тестирования, `PROJECT_TRUTH.md` или product scope.

## 1. Текущее решение

`PENDING`

Usability, cognitive-value и behavioral-value gates ещё не пройдены на primary cohort. Product expansion, новые домены, Courses depth и AI generation остаются закрыты.

## 2. Допустимые решения

- `ITERATE` — core value подтверждена, но нужны точечные исправления текущего loop.
- `EXPAND` — пройдены все три gate; разрешено планировать следующий domain/product layer.
- `NARROW` — ценность подтверждена только для более узкого сценария; scope должен быть сужен.
- `STOP/RETHINK` — core loop не подтверждён; дальнейшее расширение прекращается до новой thesis.

## 3. Обязательное evidence перед сменой статуса

### Usability

- версия commit/deployment;
- primary cohort и anonymized profiles;
- task completion и critical moderator assists;
- public save/restore/share technical evidence;
- relation/similarity и provenance literacy.

### Cognitive value

- control-vs-ARTEMIS protocol;
- quality rubric;
- evidence-backed participant conclusions;
- вывод о том, создают ли map + time дополнительную ценность.

### Behavioral value

- 7-day field follow-up;
- самостоятельный reopen, update или share;
- связь reuse с реальной учебной задачей.

## 4. Decision record

| Поле | Значение |
|---|---|
| Decision | `PENDING` |
| Validation round | Not completed |
| Commit/deployment | Not recorded |
| Dataset version | Not recorded |
| Primary cohort | Not completed |
| Usability gate | Not passed |
| Cognitive-value gate | Not passed |
| Behavioral-value gate | Not passed |
| Approved scope change | None |

## 5. Change-control rule

Статус может быть изменён только отдельным decision commit после завершённого evidence package.

Каждое изменение должно:

1. указать одно допустимое решение;
2. сослаться на evidence package;
3. объяснить, какие thresholds пройдены или не пройдены;
4. перечислить разрешённые и запрещённые изменения scope;
5. синхронизировать `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `PROJECT_TRUTH.md`, `PROJECT_PHASES.md` и `PRIORITIES.md`, если решение меняет направление проекта.

Отсутствие заполненного evidence package означает `PENDING`, независимо от субъективной оценки качества продукта.
