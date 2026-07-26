# ARTEMIS — PRODUCT THESIS

## Статус

- Тип: canonical active product thesis.
- Версия: 2.0.
- Дата: 2026-07-26.
- Решение: focused architecture-history research vertical.
- Основание: Concept Lock v2 (`docs/work/2026-07-26_CONCEPT_LOCK_V2.md`).

## 1. Product statement

**ARTEMIS Architecture Atlas помогает старшекурснику или магистранту истории архитектуры превратить сравнительный вопрос о 2–3 объектах в проверяемый Research Brief с claims, источниками, выводом, неопределённостью и пространственно-временным контекстом.**

Дифференциация:

> ARTEMIS сохраняет не набор найденных карточек, а проверяемую цепочку от вопроса к выводу: что утверждается, каким evidence это поддерживается или оспаривается и где остаётся неопределённость.

Map и timeline являются привилегированными исследовательскими линзами. Их дополнительная ценность должна быть доказана отдельно от ценности Compare/Evidence.

## 2. Проблема

При подготовке сравнительного эссе, семинара или исследовательского задания студент собирает контекст из статей, каталогов, карт, изображений и заметок. В результате:

- утверждения отделяются от точных источников и locators;
- формальное сходство легко принимается за влияние;
- классификация смешивается с исторической relation;
- собственный вывод трудно восстановить и проверить;
- карта, хронология и evidence остаются в разных инструментах;
- перенос результата в эссе или презентацию требует повторной ручной сборки.

ARTEMIS должен уменьшить этот разрыв, не выдавая similarity, classification, interpretation или AI output за доказанную связь.

## 3. Primary user and job

Первичный пользователь:

- старшекурсник или магистрант истории архитектуры/искусства;
- у него есть сравнительное учебное или исследовательское задание со сроком в ближайшие 1–2 недели;
- он умеет читать источники, но не обязан знать внутреннюю терминологию ARTEMIS.

Job-to-be-done:

> Когда мне нужно подготовить сравнительное задание, я хочу собрать контекст 2–3 объектов, проверить конкретные утверждения и сформулировать доказательный вывод, чтобы перенести результат в свою работу без повторного восстановления evidence chain.

Secondary exploratory audiences:

- преподаватель или куратор — для оценки provenance, rubric и возможного guided use;
- профессиональный исследователь — только для требований к corpus depth и citation precision.

Результаты вторичных аудиторий не заменяют evidence по primary user.

## 4. Core value and loop

Инвариант ценности:

`Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved`

Текущий product loop:

1. Сформулировать или выбрать исследовательский вопрос.
2. Найти 2–3 объекта через доступные линзы, включая map/time/filter.
3. Сопоставить factual Claims, classifications и substantive Relations.
4. Проверить EvidenceLinks и locators; отдельно увидеть Similarity.
5. Зафиксировать findings, conclusion или explicit `unresolved`, а также uncertainty.
6. Сохранить immutable Slice Revision внутри Investigation.
7. Получить citation-ready Research Brief.
8. Вернуться к Investigation, создать новую revision или передать revision-pinned read-only результат.

Первая ценность возникает при доказательном сравнении. Повторная ценность возникает, когда revision и Brief позволяют продолжить или передать работу без потери evidence chain.

## 5. Research-work model

- `Investigation` — развивающаяся исследовательская работа с устойчивой identity.
- `Slice Revision` — неизменяемая версия Investigation.
- `Saved View` — вложенный UI-контекст map/time/filter/selection; полезный, но не достаточный результат.
- `Research Brief` — читаемая и экспортируемая проекция одной revision.

Current runtime `ResearchSlice v2` является compatibility persistence envelope. Он не доказывает, что Investigation/revision/Brief model уже реализована.

## 6. Product principles

1. Human judgment is the mission; AI is optional assistance.
2. Claims before generic notes.
3. EvidenceLinks before source lists.
4. Locators before unverifiable URLs.
5. Substantive Relations before pairwise classifications.
6. Evidence depth before corpus breadth.
7. Comparison creates understanding; revision preserves it; Brief transfers it.
8. Saved View supports research but does not define research.
9. Map/time must prove incremental cognitive value.
10. Visible uncertainty is preferable to false completion.
11. Public capability must precede navigation promise.
12. Current reality must never be inferred from North Star documentation.

## 7. Hypotheses to validate

### H1 — evidence-chain value

Claim-level evidence помогает пользователю создать более корректный, трассируемый и убедительный сравнительный Brief, чем его обычный workflow.

### H2 — comparison value

Сопоставление одних и тех же типов Claims по 2–3 объектам создаёт более глубокий вывод, чем последовательный просмотр карточек.

### H3 — relation literacy

Пользователь отличает substantive Relation от shared classification и computed Similarity и не использует последние как доказательство influence/causality.

### H4 — spatial-temporal increment

Map/time дают измеримое преимущество над same-content list/detail baseline хотя бы для части исследовательских вопросов.

### H5 — reusable outcome

Revision-pinned Research Brief полезнее mutable bookmark: пользователь переносит его в задание, дополняет новой revision или передаёт другому человеку.

### H6 — focused domain

Architecture-history vertical достаточно узок для claim-level curation и достаточно богат для проверки общей evidence-first модели ARTEMIS.

### H7 — sustainable curation

Один глубокий research module можно подготовить и проверить с измеримой стоимостью, пригодной для следующего пилота.

## 8. MVP success definition

MVP считается продуктово подтверждённым только по `PRODUCT_VALIDATION_PLAN.md`.

Минимальный смысл результата:

- участник завершает core loop без критической помощи;
- major Claims в Brief имеют traceable EvidenceLinks или явно помечены как unsupported/unresolved;
- shared classification и Similarity не превращаются в historical Relation;
- blind rubric показывает улучшение качества Brief относительно control;
- пользователь может объяснить отдельный вклад Compare/Evidence и map/time;
- хотя бы часть primary cohort самостоятельно использует результат на реальной задаче в течение 7 дней;
- стоимость подготовки одного module зафиксирована;
- принято явное решение `ITERATE`, `EXPAND`, `NARROW` или `STOP/RETHINK`.

Нравящийся интерфейс, технически успешное сохранение или высокий task completion сами по себе не подтверждают thesis.

## 9. Non-goals текущего цикла

- universal history platform;
- Stories/Courses как отдельные продукты;
- AI generation как primary feature;
- open-ended UGC;
- causal/predictive/counterfactual engine;
- multi-domain expansion;
- institution/enterprise workflows;
- framework rewrite;
- corpus scaling до deep-module и curation-cost evidence.

## 10. Long-term options

После core proof независимыми gates могут проверяться:

- guided exploration;
- source-bound AI assistance;
- institutional/teaching workflow;
- новые предметные domains;
- structured inference experiments.

Ни одна ветвь не открывается автоматически другой ветвью или общим обещанием «платформы».
