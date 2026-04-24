# 2026-04-23_UIUX_MAIN_SCREEN_TECHNICAL_SPEC_ACTIVE_v1_0

## Статус документа
- Тип: working UI/UX technical spec
- Назначение: зафиксировать **идеальную структуру главного экрана ARTEMIS** как основу для следующего UI-концепта, Figma-screen и дальнейшей runtime-реализации
- Статус: active
- Scope: **только main screen / primary workspace** для desktop и mobile
- Не покрывает: full story screen, course player, compare full-screen mode, settings/profile screens

---

# 1. Цель

Собрать такой главный экран ARTEMIS, который:
- ясно показывает продукт как **map-first research workspace**;
- делает **research slice** главным продуктовым объектом;
- показывает **timeline** как structural axis, а не secondary widget;
- даёт сильный **detail / slice panel** как главный смысловой контейнер после карты;
- визуально различает **fact / relation / interpretation / AI suggestion**;
- выглядит как реальный product runtime, а не как marketing collage.

---

# 2. Базовый продуктовый принцип

Главный экран ARTEMIS должен продавать не список функций, а **основной рабочий цикл**:

1. пользователь входит в тему или открывает saved slice;
2. видит карту и временной контекст;
3. изучает выбранную пространственно-временную конфигурацию;
4. раскрывает смысл через detail panel;
5. сохраняет / обновляет / сравнивает slice;
6. продолжает исследование, story или AI explanation.

Следовательно, главный экран должен показывать в первую очередь:
- активный slice;
- карту;
- timeline;
- detail context;
- next research actions.

---

# 3. Главный тезис экрана

**ARTEMIS main screen = one strong research workspace, not a feature collage.**

Это означает:
- один основной desktop-screen как ядро;
- минимум внешних promo-card элементов;
- никакого визуального конфликта между presentation layer и runtime layer;
- сама структура интерфейса должна объяснять продукт лучше, чем маркетинговый текст.

---

# 4. Приоритеты композиции

## 4.1 Desktop visual hierarchy
Порядок визуального веса:
1. Map workspace
2. Timeline
3. Detail / Slice panel
4. Top shell
5. Secondary status cues

## 4.2 Что должно читаться за 3 секунды
Пользователь или зритель должен сразу понять:
- это исследовательская карта;
- здесь важен период времени;
- открыт исследовательский slice;
- справа расположен смысловой контейнер по выбранной сущности и текущему slice;
- AI встроен как explainable layer, а не как отдельный чат.

---

# 5. Desktop main screen — точная структура

## 5.1 Общая сетка
Рекомендуемая композиция desktop:
- **70% ширины** — map workspace
- **30% ширины** — right detail / slice panel
- снизу по всей ширине workspace — **timeline band**
- сверху — quiet shell из 2 горизонтальных уровней

## 5.2 Высотная структура
1. Top shell primary row
2. Top shell secondary row / slice sub-bar
3. Main map + right panel area
4. Bottom timeline band

---

# 6. Top shell

## 6.1 Primary row
Содержимое:
- ARTEMIS wordmark
- main navigation:
  - Workspace
  - Research
  - Stories
  - Courses
  - Saved
- compact search
- quiet profile avatar

## 6.2 Правила для primary row
- shell должен быть тихим;
- не должен спорить с картой;
- не должен выглядеть как SaaS command center;
- nav визуально вторична по отношению к map workspace.

## 6.3 Secondary row / slice sub-bar
Обязательное содержимое:
- label текущего slice:
  - `Slice: Byzantine Networks`
- статус:
  - `Saved` / `Modified`
- period:
  - `330–1200 CE`
- optional context chip:
  - region / theme / active layer count
- действия справа:
  - Save
  - Compare
  - Share

## 6.4 Смысл secondary row
Этот уровень нужен, чтобы **research slice был виден как текущая рабочая единица**, а не прятался в глубине UI.

---

# 7. Map workspace

## 7.1 Роль
Карта — главная сцена продукта.
Она должна не просто показывать точки, а удерживать:
- spatial context;
- selection;
- layer logic;
- связь с timeline;
- связь с slice.

## 7.2 Что должно быть видно на карте
Для hero main screen рекомендуется:
- регион: Eastern Mediterranean / Byzantine world
- видимые labels:
  - Constantinople
  - Nicaea
  - Antioch
  - Alexandria
  - Jerusalem
  - Black Sea
  - Mediterranean Sea
- selected focal entity: Constantinople
- несколько route/entity traces
- небольшое число, но качественно различённых knowledge layers

## 7.3 Epistemic map language
На карте должно быть различимо:
- **Fact** — холодный синий, более точный и уверенный
- **Relation** — тёплый оранжево-архивный маршрут / связка
- **Interpretation** — editorial warm framed cue
- **AI Suggestion / Hypothesis** — мягкий violet / purple path or tag

## 7.4 Inline callouts on map
Рекомендуется показывать не более 2–3 встроенных подписей:
- `Trade route — Fact`
- `Pilgrimage network — Interpretation`
- optional: one AI route or weak hypothesis cue

Важно:
- callouts не должны превращать карту в диаграмму;
- карта должна оставаться чистой и читаемой.

## 7.5 Left map tools rail
Слева на карте допустима slim vertical rail:
- pointer/select
- layers
- filters
- relation/network mode
- annotations
- zoom

Правило:
- rail узкая и тихая;
- не выглядит как complex GIS panel;
- не забирает на себя внимание.

---

# 8. Right detail / slice panel

## 8.1 Роль
Это **главный смысловой контейнер после карты**.
Не просто карточка объекта, а место, где собираются:
- selected entity preview;
- slice context;
- provenance;
- structured knowledge layers;
- AI explanation;
- next actions.

## 8.2 Внутренняя структура панели
Панель должна быть собрана в 4 уровня:

### Level 1 — Preview header
Содержимое:
- entity title: `Constantinople`
- type: `City`
- period: `330–1453 CE`
- category: `Place`
- optional small thumbnail / image

### Level 2 — Research Slice Context
Содержимое:
- current slice title
- active layers
- selected entities count
- short note / context
- status badge: Saved / Modified

### Level 3 — Knowledge structure
Четыре обязательных блока:
1. Fact
2. Relation
3. Interpretation
4. AI Suggestion

### Level 4 — Action zone
Кнопки:
- Save Slice
- Add to Research
- Compare
- Explain

## 8.3 Как должен выглядеть knowledge structure
Каждый блок должен иметь:
- свой цветовой маркер;
- короткий label;
- 2–4 строки содержимого;
- source/provenance line при необходимости;
- явную визуальную разницу между verified и interpretive слоями.

### Fact block
Содержит:
- базовое утверждение о сущности;
- конкретный source link / reference.

Пример:
- `Constantinople was founded as Byzantium by Constantine I in 330 CE.`
- `Source: Procopius, De Aedificiis`

### Relation block
Содержит:
- связанность с другими сущностями или сетями.

Пример:
- `Connected to Nicaea via imperial and ecclesiastical networks.`
- `Source: Tabula Peutingeriana`

### Interpretation block
Содержит:
- scholarly framing;
- editorial synthesis;
- но не должен визуально выглядеть как warning.

Пример:
- `Its location between Europe and Asia made it the strategic and symbolic heart of Byzantium.`

### AI Suggestion block
Содержит:
- слабый / исследовательский вывод;
- confidence cue;
- возможность раскрыть why / basis.

Пример:
- `The city’s harbor network likely enabled faster grain redistribution during crises.`
- `Confidence: 72%`

## 8.4 Важное правило панели
Панель должна ощущаться как **editorial research surface**, а не как e-commerce info card и не как developer debug panel.

---

# 9. Timeline as structural axis

## 9.1 Роль
Timeline — вторая главная ось ARTEMIS.
Он должен быть визуально и смыслово сильнее, чем обычный bottom filter.

## 9.2 Композиция
Timeline занимает нижнюю полосу под map workspace и visually connects:
- current range;
- key historical anchors;
- map state;
- slice state.

## 9.3 Обязательное содержимое
- range selection: `330–1200 CE`
- visible start/end handles
- event anchors:
  - 330 — Byzantium founded
  - 532 — Hagia Sophia completed
  - 726–843 — Iconoclasm
  - 1054 — East–West Schism
  - 1204 — Fourth Crusade
  - 1453 — Fall of Constantinople

## 9.4 Правила
- timeline должен быть выше и насыщеннее, чем в обычных dashboard patterns;
- он должен показывать не только текущий range, но и temporal meaning;
- визуально должен ощущаться как load-bearing object.

## 9.5 Что запрещено
- делать timeline слишком тонкой полосой;
- превращать его в декоративный slider;
- убирать подписи якорных событий в пользу чистой геометрии.

---

# 10. Главный сценарий, который должен считываться на desktop

Главный экран должен показывать именно этот момент работы:

> Пользователь открыл или продолжает сохранённый research slice, видит текущий пространственно-временной контекст, изучает выбранную сущность, различает knowledge layers и может сохранить / сравнить / объяснить текущее состояние.

Если этот сценарий не читается с экрана, главный экран не выполнен.

---

# 11. Mobile main screen — точная структура

## 11.1 Главный принцип
Mobile = **staged workspace**, а не уменьшенный desktop.

## 11.2 Композиция mobile
Сверху вниз:
1. Top bar
2. Compact map
3. Compact timeline
4. Bottom sheet detail + slice context
5. Primary actions

## 11.3 Top bar
Содержимое:
- menu / back / route control
- ARTEMIS wordmark
- search or profile

## 11.4 Map section
- занимает верхнюю половину mobile workspace;
- показывает selected context;
- не перегружается мелкими control elements;
- допускает 1–2 overlay actions.

## 11.5 Compact timeline
Сразу под картой:
- selected range
- 3–5 видимых anchors
- минимум clutter

## 11.6 Bottom sheet
Содержимое:
- entity preview
- short slice context
- active layers
- selected entities count
- short note
- status Saved / Modified

## 11.7 Mobile actions
Primary actions:
- Save Slice
- AI Explain

Secondary actions допускаются через overflow или expandable sheet.

## 11.8 Что запрещено на mobile
- пытаться показать полную desktop panel hierarchy сразу;
- держать одновременно слишком много knowledge blocks раскрытыми;
- визуально убить карту тяжелым UI.

---

# 12. Product presentation rules for next render / Figma

## 12.1 Что нужно показать
Следующий концепт должен показать:
- один сильный desktop main screen;
- один coherent mobile screen;
- минимум promo clutter;
- реальный product runtime feel.

## 12.2 Что нужно убрать по сравнению с предыдущими презентационными вариантами
- избыток floating concept cards;
- длинные marketing bullet lists;
- лишние compare widgets вне main screen;
- плотный collage-effect.

## 12.3 Что нужно усилить
- slice visibility;
- timeline scale and weight;
- editorial strength of detail panel;
- product realism;
- coherence between desktop and mobile.

---

# 13. Copy / labeling tone

Рекомендуемый тон:
- спокойный;
- исследовательский;
- точный;
- без маркетинговой экзальтации.

Подходящие labels:
- Slice
- Saved
- Selected range
- Fact
- Relation
- Interpretation
- AI Suggestion
- Source
- Compare
- Explain

Неподходящие:
- overly friendly CTA;
- hype wording;
- vague “smart insights” language без epistemic статуса.

---

# 14. Acceptance criteria for next concept

Следующий главный экран считается удачным, если:

1. За 3 секунды читается, что это map-first research workspace.
2. Видно, что current unit of work = slice.
3. Timeline ощущается как core axis, а не bottom widget.
4. Detail panel выглядит как main meaning container.
5. Различие fact / relation / interpretation / AI suggestion визуально ясно.
6. Презентация не перегружена окружающими карточками.
7. Mobile выглядит как самостоятельная staged adaptation.
8. Экран ощущается как продукт, а не как moodboard.

---

# 15. Ready-to-use prompt basis for next visual generation

Ниже — короткая operational formula для следующего рендера или Figma prompt:

> Create the ideal ARTEMIS main screen as a strong product runtime concept, not a collage. Show one dominant desktop workspace and one coherent mobile adaptation. The desktop must be map-first, slice-centered, timeline-led, and epistemically structured. Use a quiet top shell, a 70/30 layout with a large map and a right editorial detail/slice panel, and a strong bottom timeline band with labeled historical anchors. Show the current slice clearly in the sub-bar. In the right panel, include preview, research slice context, fact, relation, interpretation, and AI suggestion with visible provenance. Keep the presentation minimal, realistic, and product-focused.

---

# 16. Итог

Главный экран ARTEMIS должен перестать быть «красивым набором подсистем» и стать **ясной исследовательской рабочей сценой**.

Его главная задача:
- не перечислить возможности,
- а показать, как пользователь реально работает с пространством, временем, knowledge layers и research slices внутри одного coherent workspace.
