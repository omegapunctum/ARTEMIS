# ARTEMIS — PRODUCT THESIS

## Статус

- Тип: canonical active product thesis.
- Версия: 3.2.
- Дата: 2026-08-29.
- Решение: Foundation v3 / first `Life in Context` vertical.
- Current proof surface: `Leonardo Temporal Map` on the public `/globe/` R&D prototype under issue `#355`.
- Current scope owner: `ARTEMIS_PRODUCT_SCOPE.md`.
- Основание: `ARTEMIS_CONCEPT.md`, issue `#355` и `work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.

## 1. Product statement

**ARTEMIS Life in Context помогает любознательному студенту или самостоятельному исследователю проследить жизнь исторической личности на интерактивном глобусе внутри изменяющегося мира: синхронно видеть её перемещения, локальные события, состояние региона и события, происходящие в других частях мира.**

Дифференциация:

> Обычная карта показывает место, биография — последовательность эпизодов, энциклопедия — отдельные статьи. ARTEMIS показывает их на глобальной пространственной поверхности как одну source-aware пространственно-временную конфигурацию и не превращает одновременность в выдуманную связь.

Текущий MVP intentionally проверяет более узкий первый шаг этой thesis. Наличие более широких hypotheses здесь не разрешает преждевременно добавлять их в current interface; active implementation scope определяется `ARTEMIS_PRODUCT_SCOPE.md`.

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

Long-term first-value thesis возникает, когда synchronized space/time/context дают пользователю новое понимание, которого не создаёт тот же материал в виде последовательности изолированных текстовых карточек.

Target core loop:

1. Выбрать личность и временной интервал на пространственной поверхности.
2. Перемещаться между её локальной траекторией и релевантным контекстом.
3. Видеть локальные события и состояние региона.
4. Включать/выключать полезные тематические слои.
5. Сравнивать локальный контекст с синхронными событиями в других местах.
6. Открывать source/evidence/uncertainty.
7. Отличать co-presence от documented encounter/relation.
8. Сохранять view или формулировать исследовательский вопрос, если это доказано полезным.

Research Brief, immutable revision и advanced comparison могут поддерживать глубокую работу, но не являются обязательным условием первой ценности.

### 4.1 Current proof loop

Текущий #355 proof deliberately проверяет фундаментальную часть thesis до добавления широкого context layer:

`object → time → path → place → information`

Для опубликованного PR `#396` это означает:

- `Range` — выбранный календарный интервал;
- `Scrub` — выбранное начало плюс один current-time cursor с накоплением пути;
- full-width bottom timeline как основной time instrument;
- shared map/timeline/selection/URL state;
- first-click popup без camera jump;
- optional right drawer;
- double-click focus;
- source/uncertainty under progressive disclosure;
- dashed chronology never becoming historical route geometry.

PR `#395` получил первый manual-feedback result `ITERATE`; PR `#396` реализовал эту коррекцию. Следующий шаг — fresh user check текущего loop, а не автоматическое расширение thesis в UI.

## 5. First World Slice thesis

Longer-term candidate: **Leonardo da Vinci, 1452–1519**.

A fuller validation Slice may eventually include only material necessary to test the relevant hypotheses:

- documented trajectory between selected places;
- events in the current place/time window;
- regional political/cultural states;
- selected contemporaries;
- documented encounters/relations after relation governance permits them;
- explicit co-presence without relation;
- selected synchronous global events;
- sources, locators and uncertainty;
- at least one changing region/state and one longer process where those hypotheses are actually tested.

Это не попытка дать полную историю Возрождения или мира 1452–1519.

The current four-Presence Romagna 1502 package is a smaller interaction scaffold and must not be described as this fuller thesis already implemented.

## 6. Hypotheses

### H1 — contextual configuration

Пользователь лучше понимает, «каким был мир вокруг личности» в выбранный момент, чем при последовательном чтении тех же материалов.

### H2 — simultaneity discovery

Пользователь замечает релевантные локальные или глобальные одновременные события, которые не назвал бы после изучения изолированной биографии.

### H3 — spatial-temporal change

Синхронизация trajectory, regions, events и time помогает точнее понять перемещение и изменение контекста.

The current Temporal Map proof tests the narrower prerequisite that the user can first understand time/path/place behavior itself.

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

This hypothesis is deferred until layers/context are intentionally included in the tested default experience.

### H7 — Globe orientation value

Переход между глобальным и локальным масштабом помогает понять расстояние, одновременность и пространственный контекст лучше, чем тот же материал в несинхронизированном или плоском baseline, и эта ценность не сводится к визуальной новизне 3D.

### H8 — sustainable World Slice

Ограниченный междисциплинарный World Slice можно подготовить и проверить с измеримой стоимостью.

## 7. Validation comparison

For a later controlled comparison, compare:

- synchronized ARTEMIS experience;
- same-content baseline without synchronized spatial/time/context interaction.

Обе condition должны получать одинаковый content scope, source access и timebox.

Possible measures include:

- reconstruction of context;
- discovery of simultaneity;
- understanding of change/trajectory;
- relation overclaim errors;
- source/uncertainty comprehension;
- delayed recall;
- preparation/review cost.

Do not score hypotheses whose content/interface is not actually present in the tested condition.

## 8. Success definition

The vertical earns further implementation only through evidence appropriate to the tested scope.

For the current post-#396 step, the immediate question is whether users can understand and use the corrected Temporal Map loop. The next recorded decision vocabulary is:

- `ITERATE`;
- `NARROW`;
- `STOP/RETHINK`.

A supported `ITERATE` may open at most one named evidence-backed next branch; branch opening is not a separate peer outcome.

For later broader validation, evidence may additionally require:

- better reconstruction of spatial-temporal configuration than baseline;
- measurable discovery of simultaneity/context;
- no increase in critical co-presence→influence errors;
- ability to inspect material Claims/evidence;
- explainable contribution from context/layers actually included in the test;
- known World Slice preparation/review cost;
- value that does not depend on AI/VR promises or decorative 3D novelty.

## 9. Non-goals

- полная биография Leonardo before the bounded loop justifies expansion;
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
7. Small understandable proof before corpus breadth.
8. `/globe/` is already a bounded public R&D research surface; public availability does not promote it to validated product capability.
9. Globe is the active interface candidate, but value must come from shared spatial-temporal semantics rather than decorative 3D.
10. A broader thesis does not authorize a broader current scope; active implementation follows `ARTEMIS_PRODUCT_SCOPE.md` and the current gate.
11. AI/VR and production-scale dynamic Earth remain separate gates.
12. Current truth is never inferred from the North Star or product thesis.