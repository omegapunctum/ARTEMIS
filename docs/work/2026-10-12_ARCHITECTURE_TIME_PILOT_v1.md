# Architecture time pilot v1 — prospective decision and specification

## Status and authority

Status: accepted prospective DECISION; REVIEW implementation is authorized.
Implementation and publication are not claimed.
On 2026-10-11 the owner accepted a bounded temporal architecture cycle, then
instructed work to begin after reviewing Airtable's role. The 2026-10-12 continuation
executes that direction. Performance diagnosis remains paused and separate.
Autonomy: DECISION before data/runtime changes, then REVIEW implementation with
independent prospective Architecture/Product acceptance and distinct final review.

Question: can three existing architecture records respond to the shared calendar
while making building identity, construction, source support and unknowns clear?
Alternatives are (a) treating imported date fields as lifetimes, (b) a new universal
historical schema/intake, or (c) a small source-bound assertion overlay on existing
identities. Adopt (c). Raw imported dates do not justify (a); (b) exceeds this task.

This decision opens only the scoped exception in Product Scope and Platform
Architecture. It does not reopen Airtable intake, frozen fixtures, editor import,
Gate E, contextual composition or comparative/formal user-value validation.

## Fixed cohort and evidence gate

Exactly three existing catalog identities are eligible:

| Existing item ID | Subject scope | Research candidate boundaries |
|---|---|---|
| `catalog:wikidata:Q83125` | Tower Bridge, the named bridge | Construction 1886–1894; opening 1894-06-30 |
| `catalog:wikidata:Q642039` | Present Banqueting House building | Construction 1619–1622; completion 1622 |
| `catalog:wikidata:Q607700` | The Monument, the named monument | Construction 1671–1677; completion/opening 1677 |

These are candidates pending source/locator acceptance, not facts established by
this specification. Research identifies official Tower Bridge, Historic Royal
Palaces, London Museum and Monument histories as the bounded sources. The evidence
packet must record exact URLs, publisher/title, retrieval date, section/object
locator, source-native expression, identity scope and rights/reuse limits before
its claims affect filtering. Prefer concise paraphrases/factual normalization and
links; do not reproduce whole copyrighted pages or images. Pin the reviewed packet
and its hashes; live pages remain mutable and retrieval is not independent review.

A predecessor Banqueting House, the wider palace and the current building are not
interchangeable. Palace destruction must not become this building's end date.
Opening and completion remain distinct claims even when they share a year.
Westminster Abbey's partial phases and Hampton Court's conflicting start years
are excluded; no silent substitution or additional harvest is authorized.

## Input and semantic boundary

Add a separately validated read-only temporal evidence package keyed by these
existing IDs. Preserve the 55 registry identities, all original Atlas/Wikidata
bytes, source-native dates/statuses, Leonardo/Roman inputs and original geometries.
Do not edit or reinterpret the existing imported/draft coordinate claims. New
assertions have their own Source/Claim/EvidenceLink references, evidence/review
status, subject scope, source-native time, precision and uncertainty. Technical
checks do not promote historical confidence or source reliability.

The overlay records distinct construction/completion/opening assertions and any
explicit continued-existence assertion. Derived phase intervals list their basis
claims, derivation rule and limitations. A source-relative assertion ('source
reports X') is distinguishable from an accepted historical assertion and from an
inference. No completion-to-infinity default is permitted.

Tower Bridge's keeper narrative may directly support continued existence, subject
to locator review. Post-completion persistence for Banqueting House and Monument
may be represented only as an explicit, source-bound inference from their keeper's
continuous-building narrative, with supporting claims and finite coverage through
1894. It is not a direct source statement of every year's existence. A mere modern
listing or two isolated observations is insufficient by itself. If continuity or
identity cannot be justified, flag that interval unknown and withhold its historical
phase rather than manufacture it. Inference remains visible in the compact card
and details, including in Range collections.

Retain current points as modern reference anchors. Historical position, footprint,
site extent and spatial precision remain unknown; dated building information does
not promote the point to historical geometry. No new footprint, moved point,
reconstructed predecessor or relation follows.

## Calendar and query contract

Calendar scope is CE, proleptic Gregorian, year-granularity selection, finite
91–1894. The upper boundary is the largest accepted finite pilot event year; if
1894 is not accepted, fail the proposed scope for review rather than substitute a
runtime clock or an arbitrary boundary. This is a navigation envelope, not complete
historical coverage. Preserve Leonardo defaults 1452–1519, Roman presets, legacy
URLs and canonical source-native state. BCE/year zero and calendar conversions
are outside this pilot. All controls, presets, validation and ARIA bounds agree.

- Architecture Scrub evaluates the selected year, never Leonardo's accumulated
  trace from `from`. Leonardo and Roman query semantics are unchanged.
- Range returns overlapping eligible phases as an interval collection; it never
  asserts simultaneous existence of all returned records.
- Construction and completed phases may share a transition year at year precision.
  Show the transition/possible phases; do not silently invent January 1 or an exact
  day. A source's day precision is retained even though the selector is yearly.
- Before a supported start, or outside supported/inferred finite coverage, the
  record is not a dated historical match. Dataset exclusion is not a claim that
  no building or earlier structure existed at that location.
- Unknown values stay unknown. Unsupported approximations have no invented range;
  conflicting alternatives are retained, never resolved by order or source rank.
  Unresolved conflict fails automatic phase admission in this first pilot.
- The other 38 architecture references remain explicit atemporal reference context
  under the existing layer choice. Label them and their counts separately from
  dated matches; do not count them as historical matches or imply contemporaneity.
  A pilot interval that cannot be established is similarly disclosed as unknown
  context, not displayed as a supported historical phase.
- Preserve native selection clearing when its dated item no longer matches; do not
  leave stale selected geometry/cards. A source-approved unknown-context item can
  remain selectable only with its unknown-context classification visible.

## Visitor behavior

The same Globe/2D map and item identity persist. Compact cards show name, relevant
phase/source-native time, direct-versus-inferred support and modern-point limit.
Details expose claims, locator links, derivation, precision and unknowns. Construction
uses plain phase text in this cycle; special styling, animation and completed-building
visual models are deferred. No fabricated appearance is rendered.

List/search labels distinguish dated matches and atemporal references. Range can
list multiple intersecting phases for one object without duplicating its registry
identity. Preserve accessible keyboard controls, EN/RU, URL/history and small-screen
interaction. The existing camera and native picking continue to operate.

## Implementation contour and verification

Expected contour: new bounded evidence package/validator and tests;
`scripts/build_unified_explorer.py` overlay/ledger/calendar composition;
`scripts/unified_explorer/runtime.js` pure query, card/list disclosures and bounds;
`index.html.template` calendar controls and labels. No frozen schema migration.
Existing contracts already support Object Events/States, precision and inference;
any change to their meanings requires their own change-control instead.

Acceptance requires:

1. Prospective independent Architecture/Product scope acceptance and a reviewed
   source packet closing each material claim/locator/identity/derivation reference.
2. Deterministic offline build; unchanged original payload/geometry and 55 identities;
   no runtime provider or Airtable request; negative checks for unsupported identity,
   missing evidence references, invented precision and indefinite persistence.
3. Query tests before/within/after construction, transition years, finite endpoint,
   unknown/conflict rejection, Range phases, Scrub and existing Leonardo/Roman cases.
4. URL roundtrip/old defaults, consistent input/ARIA limits, hidden selection cleanup,
   modern-point and inference disclosures, and unknown-context counts.
5. Native desktop/narrow Globe/2D inspection of a source-supported transition and
   details, then distinct final implementation review and required current-head CI.
   Merge and separate public byte/interaction verification are distinct receipts.

Use existing unified builder/behavior/browser and catalog preservation tests where
applicable; broaden only to cover changed contours or required gates. Source reviews,
software browser checks and publication are not proof of historical completeness or
validated user value.

## Stop condition and handoff

Stop after these three existing objects have a source-auditable temporal projection
and the visitor can understand why an object appears in a selected year and what
remains unknown. If sources cannot support the proposed phase, document the exact
gap and withhold that phase; do not enlarge the cohort or infer a lifetime to meet
a target. The next cycle, if requested, can address construction styling or expand
content. No automatic successor is opened.

## Review receipts

Prospective independent Architecture/Product scope review: ACCEPTED on 2026-10-12
by distinct agent `/root/time_decision_review`, with zero material findings. Reviewed
four-file candidate digest (sorted path + NUL + bytes + NUL, SHA-256):
`cc3680babba6b4f19e1065c09926d8987307a2d13faed199a001e5491948427d`,
against baseline `3089b092aaab9d4a46c586342dd844f5865ebcde`. This accepts the
framework only; historical claims and phase inferences require separate packet
acceptance before admission. Editorial spacing and this receipt followed review.
Implementation: not started by this record.
Publication: not claimed. Subsequent receipts must identify the reviewed commit and
source packet; this prospective record must not be presented as completed evidence.


### Evidence admission — 2026-10-12

Distinct source review by `/root/temporal_evidence_review`: ACCEPT, zero material
findings, exact evidence packet SHA-256
`891cca33ad6db050839bbadb136910e577f7866344f9e32dac739c6822e64873`.
All six institutional source URLs and locators were independently checked. The
separate `fixtures/architecture_time_pilot/v1/acceptance.json` admits source-relative
claims and explicit finite inferences; original proposed states remain preserved.

Tower Bridge and Monument each admit construction and completed phases. Monument
continuity through 1894 is explicitly inferred from its keeper's identity-preserving
maintenance narrative, not direct annual testimony or unchanged fabric.
Banqueting House remains unknown/conflicting reference context: Historic England
reports construction 1619–1625/opening 1622, whereas HRP reports completion 1622
and London Museum construction 1619–1622. Scope difference is not established.
Its phase array is empty; candidates remain separately withheld. No source rank
resolves the conflict. This applies the existing stop/withhold rule, not a new cohort.
The delivered pilot therefore targets two dated objects and one visible unresolved
case. Native identities and geometry remain unchanged.

### Implementation checkpoint — 2026-10-14

The bounded overlay, offline admission validator, shared calendar through 1894,
phase query and source-aware card/details are implemented locally. The compact
card now retains labelled source-native construction/completion/opening expressions
in addition to the year-level projection. Imported records and geometry are unchanged.

Saved verification from 2026-10-13: 41 owned temporal/unified tests passed, including
query, URL, startup, mobile and compact-card behavior; 92 project-state/Core-boundary
tests passed. Interrupted Airtable work is tracked independently in its worktree.
Native desktop/narrow evidence, final exact-head independent review and CI remain
pending. This checkpoint is not merge or publication acceptance.

### Verification and delivery checkpoint — 2026-10-14

Implementation source: `b40f9b25cb6249796253aab1225493caf26f020a`.
The full owned Core regression contour completed locally: **459 passed** in
70.54 seconds; source log `temporal-core-tests-resume.log` is retained in the local
verification workspace. The browser runner passes Node syntax and both owned
artifact/offline guard checks; it now covers Monument's 1676/1677/1678/1670 phases
and Tower Bridge's 1894 compact source-native dates/details in Globe and 2D.

Actual native runs and screenshot inspection are not completed: no local Chromium
binary survived the environment reset, and the supplied download was a corrupt ZIP.
Remote CI has not started. Git push failed with missing HTTPS credentials. The
parallel Airtable repair also encountered an automatic approval rejection for
repository disclosure; no alternative upload was attempted. Publishing the branch,
required CI/native evidence, final merge acceptance and public verification remain
pending. This checkpoint does not weaken those requirements.

### Independent implementation conformity review — 2026-10-14

Distinct reviewer `/root/temporal_merge_review` reviewed exact local head
`5a1e97eacbcdf8ea4eb23c8e5294b1e05770c102` (runtime/native runner source
`b40f9b25cb6249796253aab1225493caf26f020a`): **ACCEPT code/specification
conformity**, zero unresolved material findings. It inspected the scope, temporal
evidence admission, builder/runtime/mobile/cards, validators/tests and native runner,
and independently checked admission, Node syntax and both artifact/offline guards.
Saved 41/92/459 passing logs were inspected. This receipt accepts the local code
only. Final delivery/merge acceptance remains pending native desktop/narrow execution
and screenshot inspection plus required remote checks on the current branch head.
