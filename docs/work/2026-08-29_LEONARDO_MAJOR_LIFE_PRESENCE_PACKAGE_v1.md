# Leonardo major-life Presence package v1

Status: `MACHINE_CHECKABLE_CANDIDATE / SOURCE_AUDITED / ROUNDS_1_4_NARROW / INDEPENDENT_REREVIEW_PENDING / RUNTIME_NOT_AUTHORIZED`.

Parent product contour: issue #355.

## 1. Problem

The published Leonardo Temporal Map currently uses four source-bound Romagna Presence anchors from the frozen 1502 Gate C package. That is sufficient as an interaction scaffold, but it cannot show a coarse whole-life path from Vinci to Amboise.

The next bounded data hypothesis is to add only a small number of major-life Presence anchors, with honest source-native temporal/spatial precision, before considering broader context, richer events or a complete biography.

This document records a research-audited candidate package. It does **not** modify the frozen Gate C package, authorize Airtable historical writes or change the public Globe runtime.

## 2. Decision

Use six macro-period groupings for curation/navigation:

1. Vinci / Florence formation — 1452–1482;
2. Milan I — c. 1482/83–1499;
3. Florence II — 1500–1506;
4. Milan II — 1506–1513;
5. Rome — 1513–1516;
6. Amboise / Clos Lucé — 1516–1519.

A macro-period is **not** a new World Model entity. It is a presentation/curation grouping over a Trajectory.

The formative Vinci / Florence group requires two separate Presence candidates. One Presence must not span two places merely because the UI groups them into one period.

The frozen Romagna 1502 Presence sequence remains a finer source-aware segment inside the broader chronological story. Its IDs, evidence, uncertainty and unknown-route semantics are not rewritten by this package.

## 3. Candidate Presence set

| Macro-period | Presence ID | Place | Source-native time used for candidate | Precision | Primary evidence | Audit result |
|---|---|---|---|---|---|---|
| Vinci / Florence formation | `presence-leonardo-vinci-birth-1452` | Vinci | 15 April 1452 | day | Museo Leonardiano: birth in Vinci; grandfather Antonio recorded birth/baptism | `READY_FOR_CANONICAL_REVIEW` |
| Vinci / Florence formation | `presence-leonardo-florence-st-luke-1472` | Florence | 1472 | year | Museo Leonardiano: registration with the Compagnia di San Luca in Florence | `READY_FOR_CANONICAL_REVIEW` |
| Milan I | `presence-leonardo-milan-altarpiece-contract-1483` | Milan | surviving contract dated 25 April 1483 | year / documentary context | National Gallery: surviving San Francesco Grande altarpiece contract | `READY_FOR_CANONICAL_REVIEW` |
| Florence II | `presence-leonardo-florence-second-period-1503` | Florence | 1503 | year | Uffizi: Leonardo back in Florence in 1503 | `READY_FOR_CANONICAL_REVIEW` |
| Milan II | `presence-leonardo-milan-ms-f-1508-09-12` | Milan | 12 September 1508 | day | Museo Galileo chronology: Manuscript F begun in Milan on that date | `READY_FOR_CANONICAL_REVIEW` |
| Rome | `presence-leonardo-rome-belvedere-1513-1516` | Rome / Vatican Belvedere | Roman stay 1513–1516; work locator c. 1514 | year range + approximate year locator | Museo Galileo, Codex Atlanticus f. 213v / `ATL.0426.1` | `READY_FOR_CANONICAL_REVIEW` |
| Amboise / Clos Lucé | `presence-leonardo-amboise-clos-luce-1516-1519` | Clos Lucé, Amboise | settled autumn 1516; died there 2 May 1519 | season/year start + day end | Château du Clos Lucé official biography | `READY_FOR_CANONICAL_REVIEW` |

These seven candidates are in addition to, not replacements for, the four frozen Romagna Presences.

## 4. Presence-level source audit

### 4.1 Vinci — 15 April 1452

Primary source: [Museo Leonardiano — Leonardo's places](https://museoleonardiano.it/en/leonardo-in-vinci/leonardos-places/).

Cross-check: [Museo Leonardiano — biography](https://museoleonardiano.it/en/leonardo-in-vinci/biografia/).

Supported:

- Vinci as birthplace;
- 15 April 1452;
- the birth/baptism memory was recorded by Leonardo's paternal grandfather Antonio.

Limit:

- the Anchiano house is identified by the museum as the traditional birthplace; the candidate therefore uses Vinci at named-settlement precision and does not claim the house as an exact evidenced birth coordinate.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.2 Florence — 1472

Primary source: [Museo Leonardiano — biography](https://museoleonardiano.it/en/leonardo-in-vinci/biografia/).

Cross-check: [National Gallery of Art — Leonardo da Vinci](https://www.nga.gov/artists/1479-leonardo-da-vinci).

Supported:

- Leonardo's Florentine formation with Verrocchio;
- registration/joining of the painters' Compagnia/Confraternity of Saint Luke in 1472.

Limit:

- the current candidate supports city/year Presence. It does not require an exact workshop/address coordinate for the current fidelity level.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.3 Milan I — 25 April 1483

Primary source: [National Gallery — The lost altarpiece](https://www.nationalgallery.org.uk/exhibitions/past/leonardo-experience-a-masterpiece/the-lost-altarpiece).

Cross-check: [National Gallery — The Virgin of the Rocks](https://www.nationalgallery.org.uk/paintings/leonardo-da-vinci-the-virgin-of-the-rocks).

Supported:

- a surviving contract dated 25 April 1483;
- Leonardo and the de Predis painters;
- the San Francesco Grande altarpiece context in Milan.

Limit:

- the documentary context supports a Milan year/context anchor; it does not establish Leonardo's body position on that day.
- the broad Milan I macro-period must not be encoded as one uninterrupted 1482/83–1499 Presence on the strength of this contract alone.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.4 Florence II — 1503

Primary source: [Gallerie degli Uffizi — La nuova sala di Leonardo](https://www.uffizi.it/news/la-nuova-sala-di-leonardo).

Cross-check: [Musée du Louvre — Leonardo da Vinci](https://presse.louvre.fr/leonardo-da-vinci/?lang=en).

Supported:

- Leonardo was back in Florence in 1503;
- the broader biographical sequence returns him to Florence in 1500 and to Milan again in 1506.

Limit:

- `1500–1506` is a macro-period grouping, not an uninterrupted Florence Presence.
- the frozen Rimini/Cesena/Cesenatico/Imola 1502 Presences remain explicit finer segments and prevent false continuity.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.5 Milan II — 12 September 1508

Primary source: [Museo Galileo — Chronology of Leonardo da Vinci](https://brunelleschi.imss.fi.it/itinerari/itinerario/CronologiaLeonardo.html).

Cross-check: [Bibliothèque de l'Institut de France — Carnet F](https://minerva.bibliotheque-institutdefrance.fr/expositions/exhibitions/7-carnet-f2).

Supported:

- the Museo Galileo chronology transcribes the Manuscript F incipit `cominciato a Milano addì 12 settembre 1508`;
- the same chronology places Leonardo in the parish of San Babila outside Porta Orientale during the Milan period;
- the Institut de France describes Carnet F as the first codex of the period in which Leonardo had re-established himself in Milan.

Limit:

- 12 September 1508 is a strong Presence anchor; it does not prove uninterrupted physical presence in Milan throughout 1506–1513.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.6 Rome / Vatican Belvedere — 1513–1516

Primary source: [Museo Galileo — Codex Atlanticus `ATL.0426.1`](https://teche.museogalileo.it/leonardo/foglio/index.html?lang=en&num=ATL.0426.1).

Supported:

- Leonardo's Roman stay between 1513 and 1516;
- residence in the Belvedere villa during that stay;
- the cited folio is dated circa 1514 and depicts the Belvedere context.

Limit:

- spatial precision is the Belvedere complex / Rome, not an exact room or daily position;
- a residence range does not imply known movements within Rome.

Decision: `READY_FOR_CANONICAL_REVIEW`.

### 4.7 Clos Lucé / Amboise — autumn 1516 to 2 May 1519

Primary source: [Château du Clos Lucé — Leonardo da Vinci](https://www.vinci-closluce.com/en/leonardo-da-vinci/).

Cross-check: [Musée du Louvre — Leonardo da Vinci](https://presse.louvre.fr/leonardo-da-vinci/?lang=en).

Supported:

- Leonardo moved to France in 1516;
- the Clos Lucé source states that he settled at Clos Lucé in autumn 1516;
- he died there on 2 May 1519.

Limit:

- the residence does not provide route geometry or prove his position at Clos Lucé continuously for every moment of the interval;
- movements around Amboise/France remain outside this coarse Presence unless separately evidenced.

Decision: `READY_FOR_CANONICAL_REVIEW`.

## 5. Temporal/spatial fidelity rules

- Preserve source-native time separately from normalized UI/calendar values.
- Day precision is used only where the source supports it.
- Year, range and approximate-year precision remain first-class; they must not be normalized into invented exact dates.
- A macro-period range is not automatically a Presence range.
- New places initially require only source-bound named-place/reference geometry with explicit historical-position uncertainty.
- Numerically precise present-day coordinates must not be presented as exact historical positions.
- Every transition between separated Presences remains `unknown_route`; historical route geometry remains `null` unless independently evidenced later.

## 6. Composition constraint with frozen Gate C

Current runtime presentation is bound to `trajectory-leonardo-romagna-1502` and the current Gate D adapter intentionally closes exactly the four reviewed Romagna settlement anchors.

Therefore **do not**:

- append the new 1452–1519 Presences directly to the frozen Gate C trajectory;
- rename `trajectory-leonardo-romagna-1502` into a whole-life trajectory;
- expand the current four-anchor registry in place and weaken its fail-closed validator;
- copy the new source assertions into the frozen Gate C source/Claim/EvidenceLink manifests;
- draw route lines between major-life Presences.

The candidate storage/composition form is now materialized under
`fixtures/world_slices/leonardo_major_life/v1/`. It references the frozen Romagna Trajectory as a
finer external segment, keeps a separate candidate whole-life Trajectory authority, and preserves
all unsupported inter-segment transitions as evidence-free `unknown_route` gaps with null geometry.

This machine-checkable candidate form is not a runtime/public schema decision. A later integration
decision must still choose how the reviewed package enters the shared World Model → Explorer State
→ Render Projection path.

## 7. Drive evidence workspace

The human-readable research package and row-level audit are maintained in Google Drive under:

`ARTEMIS / 02_WORLD_SLICES / Leonardo_Life_in_Context`.

Relevant operational artifacts:

- `Research Notes / Leonardo_Major_Life_Periods_v1`;
- `Sources / Leonardo_Source_Index / Presence_Audit`.

Drive is evidence/research workspace only. GitHub remains the owner of product/architecture decisions and any eventual machine-readable runtime package.

## 8. GitHub candidate package

The reviewable repository package contains:

- `fixtures/world_slices/leonardo_major_life/v1/package.json`;
- `fixtures/world_slices/leonardo_major_life/v1/package.schema.json`;
- `scripts/validate_leonardo_major_life_package.py`;
- `tests/test_leonardo_major_life_package.py`.

It closes candidate Place → Presence → atomic identity/time/place/selection Claims → EvidenceLink →
Source and structured Uncertainty references, preserves the seven Drive audit decisions, and fails
closed on geometry, route evidence, temporal-precision inflation, frozen-Romagna identity copying,
Relations, runtime authorization and self-declared review completion. A deterministic SHA-256
envelope additionally locks all substantive package content—including statements, locators, labels,
rationales and Uncertainty meaning—plus immutable research-workspace, artifact and curation-note
provenance. Only lifecycle status, current decision and the validated append-only review log remain
outside the digest, so a positive decision-only descendant does not re-sign historical content.

## 9. Current lifecycle

This package changes the state from “candidate idea” to a **source-audited, machine-checkable
candidate awaiting canonical review**.

It does not claim that the public Globe currently contains the seven new Presences.

Lifecycle dependency PR `#399` is merged and records the direct post-#396 `ITERATE`, opening exactly
one `Leonardo Major-Life Presence Scope v1` branch. Independent review round 1 on PR `#400` head
`5672fbae6f224b0fb90ccc09080ca47d4574c511`, both round-2 tracks on
`fb82e272b76645446c41be8c98b35942c44547c7`, and both round-3 tracks on
`b26e7b2704b6091e0859a75c75728b323bb28d5a` returned `NARROW`. Round 4 on
`a58540aaadcb912a800ab1d21cc732ad814c09f6` returned semantic `FREEZE_FOR_REVIEW` and validator
`NARROW`, so its combined result remains `NARROW`. Their provenance is preserved in package audit
history; the audit-only remediation awaits a new exact-revision review.

## 10. Exit condition for this package

Research package is ready when:

- all seven candidate Presences have independent source/locator review;
- uncertainty and precision are explicit;
- no macro-period is mistaken for an uninterrupted Presence;
- frozen Romagna data is unchanged;
- a future runtime implementation can consume the package without weakening Gate C or inventing routes.

All seven current candidates meet the source-audit threshold for `READY_FOR_CANONICAL_REVIEW`.

The package remains `pending_independent_rereview`. Its next decision is exactly one of
`FREEZE_FOR_REVIEW`, `NARROW` or `STOP`. Runtime integration is a later decision and is not
authorized by this candidate package or by a passing structural check.
