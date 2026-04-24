# 2026-04-23_UIUX_DARK_MASTER_CONCEPT_PROMPT_ACTIVE_v1_0

## Статус документа
- Тип: working prompt spec
- Статус: active
- Назначение: зафиксировать отдельный prompt для **dark master-concept главного экрана ARTEMIS**
- Основа: `2026-04-23_UIUX_MAIN_SCREEN_ART_DIRECTION_SPEC_ACTIVE_v1_0.md`, `2026-04-23_UIUX_MAIN_SCREEN_TECHNICAL_SPEC_ACTIVE_v1_0.md`, `2026-04-23_UIUX_MAIN_SCREEN_MASTER_CONCEPT_PROMPT_ACTIVE_v1_0.md`
- Scope: только **main screen / desktop + mobile concept**
- Роль: dark flagship direction

---

# 1. Зачем нужен этот документ

Этот prompt нужен для отдельного dark-направления ARTEMIS.

Его задача:
- собрать **один flagship dark master-concept**;
- удержать сильный brand presence;
- показать ARTEMIS как serious research platform;
- не уйти в sci-fi dashboard, neon UI или cinematic spectacle.

Главная формула:

**Dark ARTEMIS = graphite research workspace with premium depth, slice-centered runtime, timeline-led structure, and restrained explainable AI layer.**

---

# 2. Что этот dark-концепт должен передать

Dark master-concept обязан ясно показать:

1. Это не просто красивая темная карта, а рабочая исследовательская среда.
2. Центральная единица — **research slice**, а не isolated object card.
3. Карта — главная сцена.
4. Timeline — load-bearing structural axis.
5. Right detail panel — смысловой и epistemic container.
6. AI — встроенный explainable layer, подчиненный factual/provenance logic.
7. Общий тон — premium, calm, scholarly, product-grade.

---

# 3. Характер dark theme

## 3.1 Общая формула
Визуальный стиль должен звучать как:

- premium
- deep
- quiet
- evidence-oriented
- editorial
- cartographic
- trustworthy

## 3.2 Чем dark theme не должна быть
Запрещено уходить в:
- sci-fi command center
- neon cyber interface
- gaming HUD
- glossy luxury dashboard
- over-dramatic cinematic poster
- AI-first futuristic product

---

# 4. Цветовая логика

## 4.1 Основа
Использовать темную исследовательскую палитру:

- deep graphite
- charcoal black-blue
- muted navy depth
- restrained steel-blue interaction
- archival warm accent in very limited amount
- soft violet only for AI suggestion / hypothesis

## 4.2 Цветовые роли
- **Fact** — cool blue
- **Relation** — warm archival orange
- **Interpretation** — warm editorial amber
- **AI Suggestion / Hypothesis** — muted violet / purple

## 4.3 Ограничения
- не использовать кислотный cyan
- не делать glow главным носителем стиля
- не строить всю атмосферу на purple-blue lighting
- не смешивать action color и meaning color

---

# 5. Композиция dark master-concept

## 5.1 Главная структура
Показывать:
- один большой desktop runtime в центре;
- один phone screen справа;
- минимальную support area слева;
- темный premium background с очень тихой картографической текстурой.

## 5.2 Приоритет композиции
1. Desktop workspace
2. Timeline
3. Right panel
4. Minimal brand strip
5. Mobile adaptation

## 5.3 Что нельзя делать
- не делать большой marketing-column
- не обкладывать экран карточками-фичами
- не превращать изображение в feature-board
- не перегружать окружающее пространство декоративными блоками

---

# 6. Структура desktop UI

## 6.1 Top shell row 1
Показывать:
- ARTEMIS wordmark
- quiet nav: Workspace / Research / Stories / Courses / Saved
- compact search
- profile avatar

Тон:
- тихий
- тонкий
- не доминирующий
- secondary relative to map

## 6.2 Top shell row 2
Показывать:
- `Slice: Byzantine Networks`
- `Saved`
- `330–1200 CE`
- compact context chips
- actions: Save / Compare / Share

Критично:
эта строка должна явно делать **slice** главной текущей рабочей единицей.

## 6.3 Map workspace
Показывать:
- Eastern Mediterranean / Byzantine world
- selected focal entity: Constantinople
- labels: Constantinople, Nicaea, Antioch, Alexandria, Jerusalem, Black Sea, Mediterranean Sea
- несколько качественных traces
- 2–3 встроенных map callouts, не больше

## 6.4 Left map rail
Тихая вертикальная панель:
- select
- layers
- filters
- relation/network mode
- annotation
- zoom

## 6.5 Right detail panel
Показывать четыре уровня:

### Level 1 — Preview header
- Constantinople
- City
- 330–1453 CE
- Place
- optional small thumbnail

### Level 2 — Slice context
- Byzantine Networks
- layer dots
- selected entities count
- short note
- Saved badge

### Level 3 — Knowledge blocks
Обязательно:
- Fact
- Relation
- Interpretation
- AI Suggestion

### Level 4 — Actions
- Save Slice
- Add to Research
- Compare
- Explain

## 6.6 Timeline
Timeline должен быть плотным, ясным, структурным.
Показывать:
- active range `330–1200 CE`
- timeline anchors:
  - 330
  - 532
  - 726–843
  - 1054
  - 1204
  - 1453

Важно:
timeline не должен выглядеть как обычный filter widget.

---

# 7. Характер карты

## 7.1 Карта
Карта должна быть:
- глубокой
- спокойной
- фактурной
- исторической по ощущению
- очень читаемой

## 7.2 На карте должно быть видно
- пространство
- маршруты
- selected nodes
- временной и смысловой контекст
- epistemic distinctions

## 7.3 Чего нельзя делать
- перегружать карту множеством линий
- превращать карту в network diagram
- использовать слишком яркие подсветки
- делать карту темнее, чем нужно для чтения

---

# 8. Mobile adaptation

## 8.1 Общий принцип
Mobile не должен быть mini-desktop.
Он должен быть staged adaptation того же workspace.

## 8.2 Что показать
- top mobile bar
- map at top
- compact time range
- bottom-sheet style detail card
- visible knowledge tabs
- Save Slice
- AI Explain

## 8.3 Тон mobile
- темный
- собранный
- спокойный
- без перегруза
- максимально coherent с desktop

---

# 9. Основной prompt

```text
Create a premium dark 16:9 UI/UX master concept board for ARTEMIS, a spatial-temporal historical research platform. The concept must show one dominant desktop runtime on a laptop and one secondary mobile adaptation on a phone. It must feel like a real product main screen, not a marketing collage.

ARTEMIS is a map-first, slice-centered, timeline-led research workspace. The visual mood must be dark, calm, editorial, and evidence-oriented. This is not a sci-fi dashboard, not a neon control room, and not a cinematic poster. It should feel like a premium scholarly digital environment for serious historical research.

Use a graphite and deep charcoal palette with restrained blue interaction accents, very subtle warm archival accents, and soft violet only for AI suggestion or hypothesis. No heavy glow. No futuristic spectacle. No noisy glassmorphism.

Composition:
- one dominant desktop interface centered
- one secondary phone adaptation on the right
- optional minimal left-side brand/support strip only
- minimal external explanatory framing
- the UI itself must explain the product

Desktop UI:
Show a two-row top shell, large historical map workspace, right detail panel, and strong bottom timeline band.

Top row:
- ARTEMIS wordmark
- Workspace, Research, Stories, Courses, Saved
- compact search field
- profile avatar

Second row:
- Slice: Byzantine Networks
- Saved
- 330–1200 CE
- compact context chips
- actions: Save, Compare, Share

Map:
- Eastern Mediterranean / Byzantine world
- selected Constantinople
- labels: Constantinople, Nicaea, Antioch, Alexandria, Jerusalem, Black Sea, Mediterranean Sea
- a small number of elegant routes and nodes
- 2–3 inline epistemic callouts only

Epistemic map colors:
- Fact = cool blue
- Relation = warm orange
- Interpretation = editorial amber
- AI Suggestion / Hypothesis = muted violet

Left map rail:
- select
- layers
- filters
- relation/network mode
- annotation
- zoom

Right panel:
Must feel like a meaning container, not a generic card.
Structure it with:
1. Preview header — Constantinople, City, 330–1453 CE, Place, optional thumbnail
2. Slice context — Byzantine Networks, layer dots, selected entities count, short note, Saved badge
3. Knowledge blocks — Fact, Relation, Interpretation, AI Suggestion
4. Action zone — Save Slice, Add to Research, Compare, Explain

Example knowledge content:
Fact:
“Constantinople was founded as Byzantium by Constantine I in 330 CE.”
“Source: Procopius, De Aedificiis”

Relation:
“Connected to Nicaea via imperial and ecclesiastical networks.”
“Source: Tabula Peutingeriana”

Interpretation:
“Its location between Europe and Asia made it one of the strategic and symbolic centers of the Byzantine world.”

AI Suggestion:
“This city’s harbor network likely enabled faster grain redistribution during periods of regional stress.”
“Confidence: 72%”
“Why this?”

Timeline:
Show a clear active range 330–1200 CE with elegant anchors for:
330, 532, 726–843, 1054, 1204, 1453
The timeline must feel structural and visually important.

Mobile:
Show a staged dark mobile adaptation with:
- top map
- compact range selector
- bottom-sheet detail card
- knowledge tabs or segmented sections
- primary actions Save Slice and AI Explain

Background:
Dark premium backdrop with faint cartographic texture, very subtle and quiet.

Avoid:
- feature collage
- giant marketing side column
- neon sci-fi UI
- loud AI-centric treatment
- overloaded compare widgets
- too many floating cards
- dashboard clutter
- excessive glow
- overloading the map with too many lines or labels

Desired result:
A definitive premium dark master concept of the ARTEMIS main screen: slice-centered, map-first, timeline-led, explainable, elegant, trustworthy, and product-grade.
```

---

# 10. Краткая версия

```text
Design a premium dark 16:9 master concept for ARTEMIS, a slice-centered, map-first, timeline-led historical research workspace. Show one dominant desktop UI on a laptop and one mobile adaptation on a phone. Use deep graphite tones, restrained blue interaction accents, warm archival highlights, and soft violet AI suggestion cues. Show a two-row top shell, large historical map of the Byzantine / Eastern Mediterranean world, right structured detail panel for Constantinople, and a strong bottom timeline for 330–1200 CE. Make it calm, editorial, trustworthy, and product-grade. Avoid neon sci-fi, feature collage, dashboard clutter, loud AI hero treatment, and oversized marketing side cards.
```

---

# 11. Acceptance criteria

Dark output считается удачным, если:
- выглядит как dark flagship продукта;
- сохраняет calm research tone;
- не скатывается в sci-fi;
- slice clearly visible;
- timeline visually strong;
- карта остается главным героем;
- AI встроен тихо и понятно;
- right panel выглядит как meaning container;
- mobile coherent with desktop;
- результат ощущается как premium runtime, а не постер.

---

# 12. Итог

Этот prompt нужен для **основного dark master-concept ARTEMIS**.

Его практическая формула:

**Dark ARTEMIS = premium graphite research workspace with strong map primacy, visible slice state, structural timeline, editorial detail, and restrained explainable AI.**
