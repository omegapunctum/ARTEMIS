# ARTEMIS — VALIDATION RESEARCH MODULES v1

## Статус

- Тип: approved working execution contract.
- Дата: 2026-07-26.
- Scope: content prerequisites for the Architecture Atlas product-validation pilot.
- Владелец продуктового gate: `PRODUCT_VALIDATION_PLAN.md`.
- Статус исполнения: `NOT READY`.

Этот документ задаёт вопросы и acceptance для content work. Он не утверждает факты или relations заранее. Любой claim и relation становится допустимым только после source review и claim-level evidence linkage.

## 1. Общий contract модуля

Каждый модуль обязан содержать:

- один вопрос, пригодный для реального сравнительного задания;
- 4–6 Features;
- 4–6 явно названных comparative lenses;
- 6–10 atomic Claims;
- минимум восемь reviewed EvidenceLinks;
- locator для каждого EvidenceLink;
- минимум две substantive Relations, не являющиеся shared classification или computed similarity;
- минимум один `challenges` или contested/medium-confidence evidence case;
- explicit uncertainty;
- reference Slice Revision;
- citation-ready reference Research Brief, скрытый от участника.

Если качественные evidence и Relations не удаётся получить, редактор меняет состав объектов. Quota не оправдывает слабый claim.

## 2. Module A — Прецедент и архитектурное переосмысление

### Research question

> Какие документированные связи позволяют говорить о переосмыслении античного центрально-купольного прецедента в архитектуре Ренессанса и неоклассицизма, а где вывод основан только на формальном сходстве?

### Candidate Features

- Pantheon (Rome);
- Brunelleschi’s Dome;
- St. Peter’s Basilica;
- Villa Almerico Capra “La Rotonda”;
- Panthéon (Paris).

### Required lenses

- функция и заказчик;
- конструктивная система;
- форма и композиция;
- временная последовательность;
- географический перенос;
- documented reception versus visual similarity.

### Required evidence shape

- минимум две substantive relation candidates из `influenced`, `modelled_on`, `derived_from`, `adapted_from`;
- отдельные evidence для factual attributes и relation claims;
- минимум один случай, где источник contextualizes или limits influence claim;
- запрет: общая купольная форма не считается доказательством influence.

## 3. Module B — Модернизм, программа и послевоенная общественная архитектура

### Research question

> Как функция, материал и институциональная программа меняют архитектурную форму внутри широкого поля модернизма и британского брутализма, и какие связи между объектами действительно документированы?

### Candidate Features

- Bauhaus Building, Dessau;
- Villa Savoye;
- Sydney Opera House;
- Park Hill, Sheffield;
- Preston Central Bus Station and Car Park;
- Royal National Theatre.

### Required lenses

- housing, education, transport and cultural program;
- material and construction;
- individual monument versus collective infrastructure;
- patronage/institution;
- chronology;
- geography and transmission.

### Required evidence shape

- не менее двух specific relation candidates; `same_movement` не засчитывается;
- минимум один competing interpretation об общей классификации;
- явно зафиксированный отрицательный результат допустим: отсутствие evidence связи должно оставаться `unresolved`, а не заполняться similarity;
- если substantive Relations не подтверждаются, состав модуля пересматривается до пилота.

## 4. Module C — Готика: классификация, передача или независимое развитие

### Research question

> Какие сходства между европейскими соборами являются общей стилевой классификацией, какие объясняются хронологией и программой, а какие подтверждают конкретную передачу строительной или композиционной практики?

### Candidate Features

- Chartres Cathedral;
- Canterbury Cathedral;
- Cologne Cathedral;
- Santiago de Compostela Cathedral;
- один дополнительный Feature допускается только при достаточном evidence.

### Required lenses

- строительная хронология и продолжительность;
- liturgical/institutional program;
- structure and construction;
- regional context;
- documented workshop/model transmission;
- classification boundary between Romanesque and Gothic.

### Required evidence shape

- shared classification представляется через classification assertions, не pairwise Relations;
- минимум две substantive relation candidates либо документированный вывод об их отсутствии;
- минимум один contested classification or attribution case;
- timeline не должен превращать последовательность дат в causal claim.

## 5. Reference Brief contract

Reference Research Brief для каждого модуля содержит:

1. question;
2. compared Features and selection rationale;
3. major Claims;
4. EvidenceLinks with source title and locator;
5. substantive Relations;
6. findings;
7. conclusion or `unresolved`;
8. uncertainty;
9. dataset/schema/revision identifiers;
10. Saved View reference.

Reference Brief используется только для подготовки scoring rubric и проверки corpus completeness. Участник его не видит.

## 6. Readiness decision

Module имеет статус `READY`, только если два reviewer независимо подтверждают:

- claim атомарен и понятен;
- evidence действительно supports/challenges/contextualizes этот claim;
- locator позволяет повторно найти основание;
- relation не является замаскированной similarity/classification;
- uncertainty не скрыта;
- reference Brief может быть восстановлен из revision без устных пояснений автора.

External product validation запрещена, пока все три модуля не имеют `READY`.
