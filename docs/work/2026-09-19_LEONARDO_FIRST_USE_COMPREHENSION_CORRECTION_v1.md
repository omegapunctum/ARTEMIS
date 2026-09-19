# Leonardo — First-Use Comprehension Correction v1

- Date: 2026-09-19.
- Status: **ACCEPTED / bounded pre-E1 product correction specification**.
- Owner: issue #355 / Product & UX.
- Authority: explicit owner acceptance on 2026-09-19 after review of the current Leonardo public UI.
- Evidence basis: owner-annotated screenshots of the current Leonardo/Region public previews. These observations are product-owner evidence only; they are **not** E1 participant evidence.
- Parent execution authority: [Gate E evidence recovery specification](2026-09-19_GATE_E_EVIDENCE_RECOVERY_SPEC_v1.md).
- Implementation class after this decision: bounded `REVIEW` UX/runtime implementation under `docs/DEVELOPMENT_OPERATING_SYSTEM.md`.
- Scope: current Leonardo Temporal Map only.

## 1. Problem

The current Leonardo interface exposes correct underlying semantics but asks a first-time user to decode too much ARTEMIS-internal structure before they can answer the basic product questions.

The bounded problem has three parts:

1. **Cognitive load** — selected-Presence details expose long qualifiers and several internal evidence groupings before the user has a simple model of where Leonardo is shown, when, what is documented and what remains unknown.
2. **Temporal/navigation legibility** — the six coarse life-period controls and the eleven Presence-episode controls read as two similar navigation rows even though they serve different roles. Repeated Places and chronology-direction cues are also hard to associate with one selected Presence episode.
3. **Evidence/provenance comprehension** — labels such as `Reviewed package sources`, `Material uncertainty` and `Coverage / corpus limits` describe repository/evidence structure rather than the user's question: what supports this record, why these sources are shown, and what remains uncertain.

This correction addresses presentation/comprehension only. It does not change the World Model, historical evidence, temporal semantics, source selection or product information architecture.

## 2. Expected first-use model

Before deeper inspection, a novice should be able to form this mental model:

`Leonardo → documented Presence → time → Place → supporting evidence → explicit limits`

For a selected Presence, the first visible detail layer should answer in this order:

1. **Where?**
2. **When?**
3. **What is documented here?**
4. **What remains unknown?**
5. **What sources support this record?** — available by progressive disclosure.

Internal repository/evidence vocabulary must not be required to understand or complete Gate E tasks.

## 3. Selected-Presence detail hierarchy

The first visible selected-Presence block must prioritize:

- canonical Place name;
- Presence time/range at source-supported precision;
- a concise record-type/context statement;
- short material limitations.

The intended information pattern is:

- Place;
- time;
- `Documented presence` (or equivalent localized wording);
- optional concise **related documented context**;
- `Duration — not established`;
- `Exact historical position — unknown`;
- `Route — unknown` where applicable.

A related context statement must never read as a proven purpose of travel, exhaustive description of activity, duration, residence or causality unless the underlying evidence already supports that claim.

Long qualifiers may remain available deeper in the disclosure hierarchy, but they must not dominate the first drawer viewport.

## 4. Evidence and provenance comprehension

### 4.1 User-facing labels

Primary user-facing evidence labels should use task language rather than repository language:

- `Reviewed package sources` → **Sources supporting this presence**;
- `Material uncertainty` → **What remains uncertain**;
- `Coverage / corpus limits` → **Prototype coverage**.

Localized equivalents must preserve the same meaning.

Terms such as `package`, `corpus`, `frozen package`, repository verification or Claim/EvidenceLink internals may remain in deeper technical evidence where necessary for traceability, but they are not first-use vocabulary.

### 4.2 Source access

`Sources supporting this presence · N` must expose the already-existing source identity/title and locator/provenance path needed by T4. No new source claim is authorized.

A small secondary disclosure, **Why these sources?**, must communicate all three of these meanings:

1. these are the sources included in the current reviewed evidence for this displayed record;
2. this does **not** claim that no other historical sources exist;
3. ARTEMIS is **not** assigning a source reliability/credibility score here.

Exact copy may vary by locale, but these semantics are acceptance requirements.

### 4.3 Global coverage vs selected record

`Prototype coverage` is a global limitation of the bounded Leonardo proof, not a property of the selected Presence. It must be visually and structurally separated from selected-record evidence and should be collapsed by default.

No absence in the current prototype may be presented as historical absence.

## 5. Temporal/navigation legibility

The two existing temporal navigation rows remain, but their roles must be explicit:

- **Life periods / Периоды жизни** — six coarse presentation groupings for temporal context;
- **Documented presences / Документированные присутствия** — eleven concrete selectable Presence episodes.

This does not create a new timeline, temporal entity or temporal state.

One selected Presence must be visibly coherent across:

- map anchor;
- Presence row;
- containing life period;
- popup/details.

Repeated visits to the same Place remain distinct Presence identities while sharing one fixed Place anchor.

## 6. Range and Scrub comprehension

Canonical behavior is unchanged.

The active mode may show one short explanatory line:

- **Range / Интервал** — `Within the selected interval` / `Внутри выбранного периода`;
- **Scrub / Накопление** — `From the beginning to the current time` / `От начала до текущего времени`.

Do not add a permanent tutorial or duplicate long descriptions of both modes.

The visible explanation must correspond to the existing behavior:

- Range uses temporal overlap with a bounded interval;
- Scrub accumulates from the existing origin to current time.

## 7. Chronology direction and repeated Places

Chronology connectors remain presentation-only and historical route geometry remains unknown/null.

For first-use legibility:

- inactive connectors remain visually quiet;
- direction emphasis should primarily identify the transition related to the selected Presence or current Scrub position;
- for a repeated Place, emphasis must resolve to the selected Presence episode, not the Place as a whole;
- multiple direction cues should not compete at equal visual strength when one transition is contextually active.

A concise legend must continue to state that the connection is chronology only and route is unknown. No route arrows, inferred roads, curves or new geometry are authorized.

## 8. What must not change

This specification does **not** authorize:

- Region integration into Leonardo or a combined Globe/Region surface;
- a new project-wide information architecture;
- Global/Focus implementation or a second temporal state;
- new historical research, Presence data, sources or source selection;
- source-credibility, reliability or confidence scoring;
- changes to Claim/Evidence/Uncertainty semantics;
- new exact historical coordinates, routes or Relations;
- Place/Presence identity changes or spatial marker displacement;
- Range/Scrub semantic changes;
- backend/Airtable historical writes or dependencies;
- design-system/token/Figma work;
- a new product feature branch or capability/value claim.

Implementation remains inside issue #355 and the existing Gate E evidence-recovery contour.

## 9. Gate E correction-budget rule

This accepted **pre-E1** correction consumes the single bounded product-correction allowance that the Gate E recovery runway previously reserved for a possible E1 failure.

The runway is therefore:

`accepted First-Use correction → implementation/publication verification → fresh E1 → E2 if E1 clears → final Gate E outcome`.

After this correction is implemented, any fresh E1 result that reveals a material product failure requiring another product correction is an **escalation**. Do not automatically open a second correction.

The following do not consume another product-correction allowance when they preserve the frozen task meaning and product experience:

- completing a `NOT_RUN` observation;
- correcting an observer/evidence-recording error;
- a protocol wording clarification that does not lower or change the success criterion.

## 10. Browser/implementation verification

Implementation must preserve existing domain-specific assertions and add bounded checks for the accepted presentation contract.

At minimum verify:

1. first-open details expose Place, time, record type/context and key limitations before global prototype detail;
2. `reviewed package` and `corpus` are not primary user-facing section labels;
3. **Sources supporting this presence** reaches the existing source/locator provenance;
4. **Why these sources?** states non-exhaustiveness and absence of reliability scoring;
5. **Prototype coverage** is separated from selected-Presence evidence;
6. **Life periods** and **Documented presences** are visibly distinguishable;
7. selected Presence state remains coherent across map, Presence row, period context and details;
8. Range/Scrub compact explanations match their unchanged semantic behaviors;
9. repeated Place identity does not collapse Presence identity;
10. chronology emphasis resolves to selected/current episode while historical route geometry remains null;
11. single click still does not change camera state;
12. popup-first → explicit details, URL restoration, keyboard behavior and owned browser gates remain green.

Rendered browser evidence is required. Green automated checks do not by themselves establish visual acceptance.

## 11. Acceptance criteria for the fresh E1 T1–T5

These criteria refine what the correction must make legible; they do not replace the accepted Gate E task protocol.

### T1 — chronology comprehension

A novice can identify the beginning, a middle phase and the end of the displayed sequence and recognizes that it is not a complete biography. The distinction between **Life periods** and **Documented presences** does not require observer explanation.

### T2 — Range comprehension

A novice can use Range to show 1502–1504 and explain that the view contains Presences overlapping the selected interval. The UI does not encourage an inference of exact-day precision, continuous residence or historical absence outside displayed records.

### T3 — Scrub comprehension

A novice can distinguish Scrub from Range and explain it as accumulation from the beginning/origin to current time rather than as a second bounded interval.

### T4 — evidence/provenance comprehension

After selecting a Presence, a novice can find without internal ARTEMIS terminology:

- a supporting source;
- its locator/provenance;
- at least one material uncertainty/limit.

The user does not need to understand `reviewed package`, `corpus` or internal evidence architecture. Related documented context must not read as a proven purpose, duration or complete explanation of the Presence.

### T5 — chronology vs route

A novice understands that dashed connectors indicate chronology, not a documented route. For a repeated Place, the selected Presence episode and its adjacent chronology context remain identifiable. URL/state restoration remains unchanged.

## 12. Completion and handoff

The specification is complete when:

- it is merged and registered as the accepted bounded pre-E1 correction;
- Gate E recovery state points to implementation of this correction before fresh E1;
- no capability/value claim changes;
- the parent Gate E recovery specification records that the single correction allowance is consumed.

After that, implementation may proceed as one bounded Codex/Engineering task:

`inspect → implement → targeted tests → browser evidence → fix/rerun → self-review → PR → merge under policy → publication verification → fresh E1`.

A second product correction after the fresh E1 requires escalation.
