# ТЕКУЩИЕ ПРИОРИТЕТЫ ARTEMIS v4.0

Статус: checkpoint-обновление после завершения stabilization baseline cycle (2026-04-14).
Назначение документа: фиксировать только актуальные load-bearing приоритеты проекта.

Правило:
- здесь нет архивных задач;
- здесь нет полного roadmap;
- здесь нет дальних продуктовых идей;
- если задача не влияет на устойчивость текущего цикла, она не должна попадать в этот файл.

---

## ПРИНЦИП ПРИОРИТИЗАЦИИ v4.0

Приоритетом считается только то, что:
- влияет на корректность public data / release / runtime;
- удерживает архитектурные boundaries;
- устраняет системный drift;
- снижает риск тихой деградации.

Если задача не влияет на эти четыре пункта, она не должна быть в top-priority списке.

---

## CHECKPOINT 2026-04-13 (фикс статуса)

Закрытые циклы, снятые из активного top-priority:
- contract sync / release-discipline fix;
- data layer stabilization;
- UI/UX stabilization;
- courses stabilization;
- map exploration stabilization.

Следующий load-bearing фокус:
- canonical planning docs re-sync по фактически закрытым stabilization-блокам;
- creator / draft UX hardening и clear auth-required UX для contributor flows;
- mobile/narrow-screen UX verification + manual smoke/runtime validation;
- затем scaling/hardening трек и только после него product expansion направления.

---

## КРИТИЧЕСКИЕ ПРИОРИТЕТЫ

### 1. Закрыть canonical planning drift и зафиксировать новый активный цикл
Что нужно:
- досинхронизировать `docs/PROJECT_PHASES.md` и `docs/PRIORITIES.md` с фактически закрытыми stabilization-работами;
- зафиксировать переход активного цикла от baseline cleanup к creator/mobile hardening;
- удержать формулировку, что product expansion не является текущим этапом.

Почему это важно:
- без этого docs перестают быть исполнимым управленческим слоем и снова накапливают drift.

### 2. Hardening creator / draft UX и auth-required contributor flows
Что нужно:
- убрать двусмысленности в первичных состояниях экрана создания/черновика;
- явно показывать auth-required ограничения до действий, ведущих к блокировкам;
- удержать mutually exclusive state surfaces в creator/runtime-потоках.

Почему это важно:
- текущий риск уже не в contract drift, а в UX-ошибках на критическом contributor пути.

### 3. Подтвердить mobile/narrow-screen UX поведением, а не только desktop baseline
Что нужно:
- завершить cleanup верхней зоны и primary actions на узких экранах;
- пройти ручной smoke по first-screen и creator/draft сценариям на mobile;
- проверить, что loading/readiness состояния не конфликтуют в narrow-layout.

Почему это важно:
- mobile regressions остаются самым вероятным источником тихой деградации UX.

### 4. Провести manual smoke и runtime validation как обязательный post-stabilization барьер
Что нужно:
- закрепить короткий обязательный smoke-набор после UX/hardening правок;
- проверять runtime readiness/loading state consistency в реальном ручном прогоне;
- не считать цикл закрытым без подтверждения на реальном UI.

Почему это важно:
- иначе стабилизация остаётся "по документам", но не подтверждается эксплуатационно.

### 5. Подготовить следующий переход: scaling/hardening, затем product expansion
Что нужно:
- держать отдельно backlog архитектурного hardening (auth/session/storage/runtime);
- не смешивать этот backlog с product growth инициативами;
- открыть expansion-направления только после закрытия hardening-гейтов.

Почему это важно:
- это удерживает реалистичный порядок работ и защищает проект от преждевременного расширения.

---

## ВЫСОКИЙ ПРИОРИТЕТ

### 6. Удерживать canonical documentation framework как операционную норму
Что нужно:
- создать устойчивую структуру `docs/`;
- выделить minimal canonical set;
- перевести старые документы в archive/reference-слой.

### 7. Удержать canonical public map source без повторного drift
Что нужно:
- продолжать удерживать `/data/features.geojson` как единственный public map source;
- не допускать трактовки `/api/map/feed` как primary/canonical data source.

### 8. Изолировать или удалить mock runtime entities из `/api/map/feed`
Что нужно:
- перестать держать временные `place`-сущности в production-like контурах;
- явно отделить internal/tooling runtime read-model от публичного data layer.

### 9. Закрыть single-instance auth/scaling risk как документированный технический долг
Что нужно:
- зафиксировать архитектурное ограничение явно;
- подготовить отдельный scaling-cycle: session store, refresh registry, storage model.

### 10. Подтвердить release/readiness/manual smoke одной терминологией
Что нужно:
- унифицировать язык release docs;
- исключить документы, которые создают ложное ощущение полного production green при существующих ограничениях.

---

## СРЕДНИЙ ПРИОРИТЕТ

### 11. Завершить UX/PWA stabilization pass
Что нужно:
- offline edge cases;
- installability smoke;
- стабильные loading/error/offline состояния;
- финальный main-screen UX baseline.

### 12. Провести cleanup `docs/reference/` и старых snapshot-документов
Что нужно:
- сохранить архивную ценность старых версий;
- перестать использовать их как активные ориентиры.

### 13. Подготовить scaling/hardening backlog отдельно от product expansion backlog
Что нужно:
- перестать смешивать архитектурный долг и продуктовые идеи в одном operational списке.

---

## ВНЕ ТЕКУЩЕГО ПРИОРИТЕТНОГО ЦИКЛА

На текущем этапе не должны считаться top priority:
- monetization;
- enterprise/institutional integrations;
- gamification;
- native mobile apps;
- AR/VR;
- predictive AI layers;
- маркетинговые кампании;
- тяжёлое расширение social-функций.

Эти темы допустимы только после закрытия текущих load-bearing конфликтов.

---

## ПРАВИЛО ОБНОВЛЕНИЯ ДОКУМЕНТА

Файл обновляется только если:
1. появляется новый load-bearing риск;
2. существующий риск закрыт и может быть снят;
3. меняется активная последовательность фаз проекта.

Если задача просто "интересная" или "полезная в будущем", её здесь быть не должно.
