# ARTEMIS — PRODUCT THESIS

## Статус

- Тип: canonical active product thesis.
- Версия: 3.1.
- Дата: 2026-08-09.
- Решение: Foundation v3 / first `Life in Context` Globe MVP vertical.
- Основание: `ARTEMIS_CONCEPT.md`, issue `#355` и `work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.

## 1. Product statement

**ARTEMIS Life in Context помогает любознательному студенту или самостоятельному исследователю проследить жизнь исторической личности на интерактивном глобусе внутри изменяющегося мира: синхронно видеть её перемещения, локальные события, состояние региона и события, происходящие в других частях мира.**

Дифференциация:

> Обычная карта показывает место, биография — последовательность эпизодов, энциклопедия — отдельные статьи. ARTEMIS показывает их на глобальной пространственной поверхности как одну source-aware пространственно-временную конфигурацию и не превращает одновременность в выдуманную связь.

## 2. Проблема

При изучении личности или эпохи пользователь вынужден мысленно соединять:

- биографию;
- карту;
- хронологию;
- политическую и культурную историю;
- сведения о других людях;
- источники и спорные реконструкции.

Из-за этого он:

- помнит отдельные факты, но слабо видит конфигурацию мира;
- теряет масштаб расстояний и длительность перемещений;
- не замечает релевантные одновременные процессы;
- принимает co-presence за encounter или influence;
- плохо видит, где данные точны, приблизительны или отсутствуют;
- тратит усилия на сбор контекста вместо его осмысления.

## 3. Primary user and job

Первичный пользователь:

- студент гуманитарной дисциплины или самостоятельный learner;
- изучает историческую личность, период или вопрос;
- хочет понимать контекст, а не только запоминать биографическую последовательность;
- не обязан владеть GIS, ontology или внутренней терминологией ARTEMIS.

Job-to-be-done:

> Когда я изучаю человека или эпоху, я хочу одновременно видеть путь личности и изменяющийся мир вокруг неё, чтобы понимать контекст, замечать возможные связи и не путать совпадение с доказанным влиянием.

Secondary exploratory audiences:

- преподаватель — для contextual learning;
- исследователь — для требований к точности, provenance и конкурирующим реконструкциям;
- музейный/архивный куратор — для будущих guided slices.

## 4. Core value

Первая ценность возникает, когда synchronized map/time/layers дают пользователю новое понимание, которого не создаёт тот же материал в виде последовательности текстовых карточек.

Core loop:

1. Выбрать личность и временной интервал на глобусе.
2. Перемещаться между глобальным контекстом и её локальной траекторией.
3. Видеть локальные события и состояние региона.
4. Включать/выключать тематические слои.
5. Сравнивать локальный контекст с синхронными событиями в других местах.
6. Открывать source/evidence/uncertainty.
7. Отличать co-presence от documented encounter/relation.
8. Сохранять view или формулировать исследовательский вопрос.

Research Brief, immutable revision и advanced comparison могут поддерживать глубокую работу, но не являются обязательным условием первой ценности.

## 5. First World Slice

Кандидат: **Leonardo da Vinci, 1452–1519**.

Slice должен включать только материал, необходимый для проверки гипотез:

- documented trajectory between selected places;
- events in the current place/time window;
- regional political/cultural states;
- selected contemporaries;
- documented encounters/relations;
- explicit co-presence without relation;
- selected synchronous global events;
- sources, locators and uncertainty;
- at least one changing region/state and one longer process.

Это не попытка дать полную историю Возрождения или мира 1452–1519.

## 6. Hypotheses

### H1 — contextual configuration

Пользователь лучше понимает, «каким был мир вокруг личности» в выбранный момент, чем при последовательном чтении тех же материалов.

### H2 — simultaneity discovery

Пользователь замечает релевантные локальные или глобальные одновременные события, которые не назвал бы после изучения изолированной биографии.

### H3 — spatial-temporal change

Синхронизация trajectory, regions, events и time помогает точнее понять перемещение и изменение контекста.

### H4 — relation literacy

Пользователь отличает:

- co-presence;
- possible encounter;
- documented encounter;
- interaction;
- influence;
- causal claim.

### H5 — trust and uncertainty

Источники, locators и uncertainty повышают доверие, не разрушая основной визуальный опыт.

### H6 — layer usefulness

Пользователь может объяснить вклад хотя бы двух тематических слоёв в своё понимание, а не только факт их наличия.

### H7 — Globe orientation value

Переход между глобальным и локальным масштабом помогает понять расстояние, одновременность и пространственный контекст лучше, чем тот же материал в несинхронизированном или плоском baseline, и эта ценность не сводится к визуальной новизне 3D.

### H8 — sustainable World Slice

Ограниченный междисциплинарный World Slice можно подготовить и проверить с измеримой стоимостью.

## 7. Validation comparison

Сравниваются:

- synchronized ARTEMIS experience;
- same-content baseline без synchronized map/time/layer interaction.

Обе condition получают одинаковый content scope, source access и timebox.

Оцениваются:

- reconstruction of context;
- discovery of simultaneity;
- understanding of change/trajectory;
- relation overclaim errors;
- source/uncertainty comprehension;
- delayed recall;
- preparation/review cost.

## 8. Success definition

Vertical получает право на следующую реализацию только если:

- участники лучше восстанавливают пространственно-временную конфигурацию, чем baseline;
- возникает измеримое discovery of simultaneity/context;
- critical co-presence→influence errors не увеличиваются;
- пользователи могут проверять существенные claims;
- минимум два слоя дают объяснимый вклад;
- observed value не зависит от обещаний AI/VR или визуальной новизны 3D без пространственно-временного понимания;
- World Slice имеет известную стоимость подготовки и review;
- принято решение `ITERATE`, `EXPAND ONE BRANCH`, `NARROW VERTICAL` или `STOP/RETHINK`.

## 9. Non-goals

- полная биография Leonardo;
- полная мировая история 1452–1519;
- generative AI;
- causal engine;
- counterfactual simulation;
- photorealistic or universal historical 3D reconstruction;
- VR/AR;
- public UGC;
- institution/enterprise workflow;
- миграция mutable ResearchSlice runtime;
- отказ от evidence discipline ради визуального впечатления.

## 10. Product principles

1. Context before isolated cards.
2. Change before static dates.
3. Synchronization before adjacent widgets.
4. Co-presence is not relation.
5. Evidence supports the model; it does not replace the experience.
6. Uncertainty is visible and spatial-temporal.
7. Small complete World Slice before corpus breadth.
8. Generated/non-public Globe evidence first; public deployment only after a separate promotion decision.
9. Globe is the active interface candidate, but value must come from shared spatial-temporal semantics rather than decorative 3D.
10. AI/VR and production-scale dynamic Earth remain separate gates.
11. Current truth is never inferred from the North Star.
