# ARTEMIS — PRODUCT THESIS

## Статус

- Тип: canonical active product thesis.
- Версия: 1.0.
- Дата: 2026-07-16.
- Решение: Option A — focused architecture-history vertical.

## 1. Product statement

**ARTEMIS — доказательный пространственно-временной атлас истории архитектуры, который помогает изучать и сравнивать объекты, направления и влияние эпох через карту, время, документированные связи и прозрачные источники.**

## 2. Проблема

История архитектуры обычно изучается через линейные тексты, разрозненные каталоги и статические изображения. Пользователю трудно одновременно увидеть:

- где находились объекты;
- когда они возникли;
- какие направления и регионы можно сопоставить;
- чем подтверждается предполагаемое влияние;
- как сохранить конкретный исследовательский контекст.

ARTEMIS должен уменьшить этот разрыв, не выдавая визуальную близость или AI-output за исторический факт.

## 3. Primary user

Первичная аудитория vertical MVP:

- продвинутый студент истории архитектуры или искусства;
- преподаватель, готовящий визуально подтверждённый материал;
- исследователь или автор, которому нужен быстрый сравнительный spatial-temporal обзор.

Общий job-to-be-done:

> Найти, сопоставить и сохранить архитектурные объекты в пространстве и времени, понимая источники и статус показанных связей.

## 4. Core value loop

1. Выбрать эпоху, направление или регион.
2. Найти релевантные объекты на карте и timeline.
3. Открыть карточку с provenance и media attribution.
4. Сравнить 2–3 объекта.
5. Изучить подтверждённые relations или явно обозначенное similarity.
6. Сохранить Research Slice.
7. Вернуться к нему или поделиться read-only представлением.

Research Slice остаётся главной единицей повторного использования, но первая ценность возникает раньше — в доказательном сравнении объектов.

UX decision 2026-07-17: comparison-first означает, что интерфейс сначала помогает выбрать и сопоставить 2–3 Features, а затем предлагает сохранить полученный контекст. Research Slice не является обязательным первым действием или заменой object comparison. Пользовательская подпись до validation — «Сохранённое исследование», внутреннее canonical name остаётся `Research Slice`.

## 5. Product principles

1. Evidence before breadth.
2. Real relations before inferred relations.
3. Content depth before platform expansion.
4. Public capability before navigation promise.
5. Map, time and detail form one research surface.
6. AI may explain sourced context, but may not manufacture provenance.
7. Smaller curated corpus is preferable to a large weak corpus.
8. Comparison creates understanding; Slice preserves it.

## 6. Hypotheses to validate

### H1 — comparison value

Пользователь получает новое понимание темы, когда может сопоставить объекты одновременно по карте, времени, направлению и источникам.

### H2 — relation value

Документированные relations повышают ценность сильнее, чем дополнительное число несвязанных map points.

### H3 — slice value

Пользователь понимает Research Slice как сохраняемый исследовательский результат, а не как технический snapshot интерфейса.

### H4 — focused domain

Архитектурный vertical достаточно узок для качественной курации и достаточно богат для проверки общей модели ARTEMIS.

## 7. MVP success definition

Vertical MVP считается продуктово доказанным, если:

- пользователь без помощи находит и сравнивает минимум два объекта;
- provenance читается рядом с factual content;
- relation и similarity не смешиваются;
- Slice можно сохранить, закрыть и восстановить на публичном runtime;
- минимум 80% тестовых пользователей завершают основной сценарий;
- продуктовая ценность объясняется пользователем без терминов внутренней архитектуры.

## 8. Non-goals текущего цикла

- универсальный исторический охват;
- Courses expansion;
- open-ended UGC;
- AI generation как primary feature;
- causal/predictive/counterfactual claims;
- enterprise/platform integrations;
- framework rewrite ради самого rewrite;
- scaling до подтверждения product loop.

## 9. Long-term option

После доказательства vertical MVP модель может быть расширена на события, людей, процессы и другие культурно-исторические области. Такое расширение является отдельным решением и не должно неявно входить в текущий backlog.
