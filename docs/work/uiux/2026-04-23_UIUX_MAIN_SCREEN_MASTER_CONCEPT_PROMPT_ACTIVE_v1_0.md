# 2026-04-23_UIUX_MAIN_SCREEN_MASTER_CONCEPT_PROMPT_ACTIVE_v1_0

## Статус документа
- Тип: working prompt spec
- Статус: active
- Назначение: зафиксировать **один финальный master-concept prompt** для генерации главного экрана ARTEMIS
- Основа: `2026-04-23_UIUX_MAIN_SCREEN_ART_DIRECTION_SPEC_ACTIVE_v1_0.md` + `2026-04-23_UIUX_MAIN_SCREEN_TECHNICAL_SPEC_ACTIVE_v1_0.md`
- Scope: только **main screen / primary workspace concept**

---

# 1. Цель prompt

Этот prompt нужен для следующего шага visual production:
- генерации одного сильного master-concept;
- сборки Figma-концепта;
- дальнейшего сравнения с runtime-реализацией;
- передачи в image model / design assistant.

Ключевая задача prompt:
сгенерировать **не просто красивую презентацию**, а **одну сильную, цельную, продуктово-правильную сцену главного экрана ARTEMIS**.

Главная формула:

**ARTEMIS main screen = one strong slice-centered, map-first, timeline-led research workspace.**

---

# 2. Что prompt обязан удерживать

Финальный master-concept обязан ясно показать:

1. ARTEMIS — это spatial-temporal research workspace.
2. Центральная рабочая единица — **research slice**.
3. Карта — главная сцена.
4. Timeline — структурная ось.
5. Right detail panel — главный смысловой контейнер после карты.
6. AI встроен как explainable layer, а не как отдельный шумный продукт.
7. Экран выглядит как реальный runtime product, а не как feature collage.

---

# 3. Источник итогового направления

Финальное направление строится по формуле:

**Композиционная база №5 + editorial clarity №2 + epistemic structure №3 + brand depth №1.**

То есть итоговый концепт должен:
- взять из №5 — общую композицию и slice-centered runtime-логику;
- взять из №2 — чистоту, дисциплину и editorial trust;
- взять из №3 — понятный язык knowledge layers;
- взять из №1 — глубину dark mood и сильное ощущение serious research platform.

Концепт №4 использовать только косвенно и только на уровне намёка на аналитическую глубину. Не делать из него основу.

---

# 4. Финальный master-concept prompt

Ниже — основной prompt, который можно использовать как рабочий master prompt для image generation.

## 4.1 Full prompt

```text
Create a high-end UI/UX master concept presentation for ARTEMIS, a spatial-temporal historical research platform. The output must be a polished 16:9 presentation board that shows one strong, coherent main screen concept rather than a collage of many unrelated features.

Core product identity:
ARTEMIS is a map-first, slice-centered, timeline-led research workspace. It is not a generic SaaS dashboard, not a sci-fi control room, not a marketing landing page, and not a museum-style decorative website. It should feel like a calm, serious, editorial, evidence-oriented digital research environment for historians, researchers, analysts, and storytellers.

Primary composition:
Show one dominant desktop interface on a premium laptop mockup as the visual center. Also show one secondary mobile adaptation on a smartphone mockup to the right. If supportive presentation content is used, keep it minimal and secondary. Avoid a feature collage. The desktop screen must clearly be the hero.

Overall composition rules:
- 16:9 layout
- central dominant desktop runtime concept
- secondary phone adaptation on the right
- optional narrow branding/support strip on the left, but much quieter than in the earlier concepts
- very little external explanatory framing
- the product UI itself must explain the product

Visual direction:
Use a dark, refined, premium research atmosphere with graphite and deep charcoal surfaces, subtle blue interaction accents, a restrained warm archival accent, and a soft violet accent for AI suggestion or hypothesis. The visual language should feel “Cartographic Research Editorial”: calm, dense, elegant, intelligent, and trustworthy. Use restrained lighting, subtle depth, fine borders, and minimal glow. No heavy neon, no futuristic spectacle, no noisy glassmorphism.

Brand tone:
Show ARTEMIS as a serious research platform. Include the ARTEMIS wordmark clearly but elegantly. The feeling should be premium, intellectual, and product-grade. The brand presence should be strong but not overpower the workspace.

Main desktop UI structure:
The desktop interface must clearly show a two-row top shell, a large map workspace, a right detail panel, and a bottom timeline band.

Top shell — row 1:
- ARTEMIS wordmark
- quiet main navigation: Workspace, Research, Stories, Courses, Saved
- compact search field
- quiet profile avatar
This row must be visually light and secondary to the map.

Top shell — row 2, slice sub-bar:
Clearly show the current research slice as the active working unit.
Include:
- “Slice: Byzantine Networks”
- status badge: “Saved”
- period: “330–1200 CE”
- optional small context chips
- right-side actions: Save, Compare, Share
This row is essential. It must make the slice immediately visible as the main product object.

Map workspace:
The map is the primary visual stage and should take about 70% of the desktop workspace width. Show an elegant historical-style map centered on the Eastern Mediterranean / Byzantine world. Visible labels should include Constantinople, Nicaea, Antioch, Alexandria, Jerusalem, Black Sea, Mediterranean Sea. Selected focal entity: Constantinople.

On-map data language:
Show a small number of high-quality spatial traces and nodes, with clearly differentiated epistemic layers:
- Fact = cool blue
- Relation = orange-archival route or connection
- Interpretation = warm editorial callout
- AI Suggestion / Hypothesis = soft violet or purple line or tag
Add only 2–3 small inline map callouts, such as:
- “Trade route — Fact”
- “Pilgrimage network — Interpretation”
Optionally one subtle AI or hypothesis cue.
Do not overload the map. Keep it readable, spatial, and elegant.

Left map tools rail:
Show a slim vertical rail on the left edge of the map with quiet icons for select, layers, filters, relation/network mode, annotation, and zoom. This rail must be minimal and not feel like a heavy GIS tool panel.

Right detail panel:
The right panel should take about 30% of the desktop workspace width and must feel like the main meaning container after the map. It should not look like a generic object card. It must show a structured editorial research panel with four clear levels:

Level 1 — Preview header:
- Title: “Constantinople”
- Type: “City”
- Period: “330–1453 CE”
- Category: “Place”
- Optional small thumbnail image

Level 2 — Research Slice Context:
- slice title: “Byzantine Networks”
- active layer dots or chips
- selected entities count
- short contextual note
- status badge: “Saved”

Level 3 — Knowledge structure:
Show four clearly separated knowledge blocks with visible semantic distinction:
1. Fact
2. Relation
3. Interpretation
4. AI Suggestion

Each block should have:
- a color marker
- a clear label
- 2–4 lines of content
- source or provenance line where appropriate
- strong visual difference between verified and interpretive content

Suggested example content:
Fact:
“Constantinople was founded as Byzantium by Constantine I in 330 CE.”
“Source: Procopius, De Aedificiis”

Relation:
“Connected to Nicaea via imperial and ecclesiastical networks.”
“Source: Tabula Peutingeriana”

Interpretation:
“Its location between Europe and Asia made it one of the strategic and symbolic centers of the Byzantine world.”
“Source: Modern scholarship synthesis”

AI Suggestion:
“This city’s harbor network likely enabled faster grain redistribution during periods of regional stress.”
“Confidence: 72%”
“Why this?”

Level 4 — Action zone:
Include compact action buttons:
- Save Slice
- Add to Research
- Compare
- Explain

Timeline band:
Across the bottom of the desktop workspace, show a strong timeline band spanning the width of the map area. The timeline must feel like a core structural axis, not a secondary filter. Show:
- selected range: “330–1200 CE”
- a visible active range line
- a few historical anchor events, for example:
  - 330 — Byzantium founded
  - 532 — Hagia Sophia completed
  - 726–843 — Iconoclasm
  - 1054 — East–West Schism
  - 1204 — Fourth Crusade
  - 1453 — Fall of Constantinople
The timeline should be elegant, readable, and strongly integrated into the desktop UI.

Mobile adaptation:
Show a mobile version to the right. It should not be just a shrunk desktop. It should feel like a staged mobile adaptation of the same workspace. Use:
- top mobile bar with ARTEMIS wordmark and simple icons
- compact map at top
- timeline or selected time range below
- bottom-sheet style detail card for Constantinople
- visible knowledge layer tabs or segmented sections
- primary actions such as Save Slice and AI Explain
The mobile UI should clearly belong to the same product family as the desktop version.

Typography and visual tone:
Use a refined research-oriented combination of elegant serif influence for brand/editorial accents and disciplined sans-serif UI typography. Ensure strong hierarchy, calm density, restrained shadows, and clean surfaces. The interface should look like a real product concept for a serious, modern research platform.

Presentation background:
Use a dark, premium backdrop with very subtle cartographic texture or faint topographic pattern. Keep the background quiet. The devices and UI must remain dominant.

What to avoid completely:
- no large feature-collage composition
- no oversized marketing explanation cards around the interface
- no sci-fi neon dashboard aesthetic
- no loud AI-centric hero treatment
- no overly decorative museum style
- no generic startup SaaS look
- no heavy glassmorphism
- no cluttered compare dashboard on the main screen
- no too many floating widgets
- no overloading the map with too many labels or lines

Desired result:
The final image should feel like the definitive master concept of the ARTEMIS main screen: a slice-centered, map-first, timeline-led, explainable historical research workspace, presented as a polished premium product concept with one dominant desktop runtime and one coherent mobile adaptation.
```

---

# 5. Краткая operational version

Если нужен более короткий prompt для быстрого прогона, использовать этот вариант.

## 5.1 Short prompt

```text
Design a premium 16:9 UI/UX master concept board for ARTEMIS, a spatial-temporal historical research platform. Show one dominant desktop interface on a laptop and one secondary mobile adaptation on a phone. The concept must be dark, calm, editorial, and product-grade, not a feature collage.

ARTEMIS must read as a map-first, slice-centered, timeline-led research workspace. Use the composition logic of a coherent runtime product: two-row top shell, large historical map workspace, right detail panel, and strong bottom timeline band.

Desktop UI requirements:
- Row 1: ARTEMIS wordmark, Workspace / Research / Stories / Courses / Saved, compact search, profile avatar
- Row 2: “Slice: Byzantine Networks”, “Saved”, “330–1200 CE”, actions Save / Compare / Share
- Main map: Eastern Mediterranean / Byzantine world, selected Constantinople, elegant spatial traces and labels, minimal on-map callouts
- Epistemic map colors: Fact blue, Relation orange, Interpretation warm editorial, AI Suggestion violet
- Slim left map tools rail
- Right panel for Constantinople with slice context and four knowledge blocks: Fact, Relation, Interpretation, AI Suggestion
- Bottom timeline with active range 330–1200 CE and key events such as 330, 532, 726–843, 1054, 1204, 1453

Mobile UI requirements:
- same visual family
- top map
- compact timeline/range
- bottom-sheet detail card
- visible knowledge tabs
- actions Save Slice and AI Explain

Visual style:
Dark graphite research atmosphere, subtle blue accents, restrained warm archival accents, soft violet AI accents, refined typography, calm density, premium surfaces, minimal glow, subtle cartographic background.

Avoid: marketing collage, huge side cards, sci-fi neon, noisy dashboards, loud AI hero treatment, overcomplicated compare widgets.
```

---

# 6. Negative / guardrail instructions

Ниже — guardrail-блок, который полезно добавлять, если генератор склонен уводить концепт не туда.

## 6.1 Guardrail block

```text
Important constraints:
- The interface itself must be the main hero, not external marketing cards.
- Keep the left support area minimal.
- Do not create a collage of multiple product modes.
- Do not turn AI into the loudest or most authoritative visual layer.
- Do not make the map secondary to panels.
- Do not overload the concept with too many compare, analytics, or dashboard widgets.
- Preserve strong hierarchy: map first, timeline second, detail panel third, top shell fourth.
- The result should look like a real product main screen, not a concept moodboard only.
```

---

# 7. Acceptance criteria for output

Сгенерированный мастер-концепт считается удачным, если:

1. За 3 секунды считывается, что это исследовательская карта.
2. Видно, что текущая рабочая единица — **slice**, а не просто object card.
3. Timeline визуально ощущается как core axis.
4. Right panel выглядит как meaning container, а не как простая карточка объекта.
5. AI встроен внутрь knowledge system и не доминирует над facts/provenance.
6. Desktop выглядит как единая сцена, а не как набор фич.
7. Mobile — логичное staged-продолжение desktop.
8. Общий тон — premium, calm, research-grade.
9. Карта остается главным героем.
10. Визуальный язык соответствует формуле ARTEMIS:
   **Graphite structure + Research Blue interaction + Archival Warm meaning + Slice-centered research clarity.**

---

# 8. Практический вывод

Если нужен **один основной prompt** для следующего раунда генерации, использовать раздел **4.1 Full prompt**.

Если нужен быстрый рабочий прогон — использовать раздел **5.1 Short prompt**.

Если нужен более управляемый результат в image model, добавлять также блок из раздела **6.1 Guardrail block**.

