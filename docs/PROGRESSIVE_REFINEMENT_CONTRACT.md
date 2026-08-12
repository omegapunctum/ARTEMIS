# ARTEMIS — PROGRESSIVE REFINEMENT CONTRACT

## Status

- Type: scoped canonical extension candidate.
- Version: 1.0-draft.
- Date: 2026-08-12.
- Status: `REVIEW_REQUIRED` under issue `#377`.
- Extends: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `UNCERTAINTY_SEMANTICS_CONTRACT.md`, `EPISTEMIC_CONTRACT.md` and `ENTITY_MODEL.md`.
- Owns: non-destructive coarse-to-fine knowledge refinement, revision lineage and deterministic current-view semantics.
- Does not own: core object identity, relation semantics, runtime/database schema, Airtable authority, historical readiness or public capability.

The reviewed #329 World Model and #330 Uncertainty packages remain immutable. This contract is a
scoped extension; it must not rewrite their accepted evidence to obtain compatibility.

## 1. Problem

ARTEMIS can already represent ranges, approximate locations, unknown routes and alternative
reconstructions. It also has a progressive-fidelity resource rule. Those capabilities do not by
themselves define what happens when better evidence arrives.

Without one refinement contract, a curator or adapter could:

- overwrite a coarse assertion and erase its evidence history;
- confuse a changed world state with improved knowledge of the same state;
- label a contradiction as a monotonic refinement;
- choose one competing reconstruction by array order;
- infer finer time or geometry merely because a renderer can display it;
- spend research budget on resolution that cannot affect the current decision.

This contract closes that gap for every domain, including biography, political geography,
ecological ranges, climate, geology and architecture.

## 2. Core distinction: world time and knowledge time

Two independent clocks are mandatory:

- `valid_time` says when the asserted state, event, route or geometry applies to the represented
  world;
- `recorded_at` says when ARTEMIS created a knowledge revision.

A wolf range in 1900 and a wolf range in 2000 are two world states even if both records are entered
today. A coarse 1900 range entered today and a better-supported 1900 range entered next year are
two knowledge revisions of the same world-state assertion.

Record time must never be projected onto the historical timeline. A new record does not imply a
new historical Event, State or Region geometry.

## 3. Stable identity and atomic targets

Entity and change-object identity remains stable while knowledge changes. Refinement operates on
an atomic assertion target, not an entire card or object.

Examples of independent targets for one Trajectory segment:

- temporal presence;
- named place or spatial extent;
- movement mode;
- route geometry;
- participation or attribution.

Refining the place must not silently rewrite the date, route, subject identity or evidence for any
other dimension. A material value is changed only by adding a new immutable revision to the target
series.

## 4. Immutable refinement ledger

Each target has one ordered, append-only revision series. A revision contains:

```text
id
series_ref
operation
predecessor_refs[]
recorded_at
origin
source_value
normalized_value?
claim_ref
evidence_link_refs[]
uncertainty_refs[]
change_reason
```

Accepted revision bytes are immutable. A typo or semantic error is repaired by a new revision,
not by mutating history. Stable ids are never reused for different payloads.

The pair `(subject_ref, target_key)` identifies one atomic target and may resolve to exactly one
series in a package. A second ledger for the same pair is invalid even if it uses another series
id. The declared target dimension must agree with the target key and the value family.

The permitted operations are:

| Operation | Meaning | Current-view effect |
|---|---|---|
| `initial` | First assertion for the atomic target | adds one frontier value |
| `refine` | Strictly narrows the predecessor's possible set using stronger evidence | replaces named predecessor(s) |
| `correct` | Replaces a materially wrong or incompatible assertion | replaces named predecessor(s), preserves contradiction history |
| `add_alternative` | Adds a materially competing value without selecting a winner | keeps predecessors and adds another frontier value |
| `withdraw` | Removes an assertion from current use without erasing it | removes named predecessor(s), adds no value |

`refine` is not a synonym for any later edit. For interval or fuzzy-area values, the new possible
set must be a strict subset of the predecessor. If the new value lies partly outside the old set,
the operation is `correct` or `add_alternative`.

## 5. Source-native value and normalized value

Every value-bearing revision preserves:

- source identifier and locator through its Claim/EvidenceLink chain;
- source-native raw expression;
- source-native precision or unresolved normalization state;
- normalized value used by query/projection, when normalization is supported.

A reviewed supporting EvidenceLink must resolve to a checked-in or otherwise immutable Source
artifact, a reproducible Claim-level locator and the exact source-native expression used by the
revision. The locator must also bind canonical SHA-256 values for the complete `source_value`
(raw expression plus declared precision) and the exact normalized assertion, including `null` for
withdrawal. Changing either source-native precision or a normalized day, boundary or value cannot
remain attached to unchanged source/Claim evidence. Reference closure without locator reproduction
and both bindings is not sufficient for `supported`.

Normalization may retain or coarsen precision. It may not produce a value finer than the source
and evidence support. A source saying “August 1502” cannot normalize to a day. A regional range map
cannot normalize to a survey-grade boundary.

Finer source-native values that already exist should be preserved even if the current UI displays
a coarser projection. Display generalization is reversible; invented sharpening is not.

## 5.1 Intake and promotion workflow

The semantic ledger is one stage in a controlled knowledge flow, not a direct editing shortcut:

`source/research artifact → candidate intake → atomic Claim/revision → epistemic review → accepted ledger revision → deterministic current frontier → separately authorized export/publication`

At candidate intake, the curator records the decision target, source-native expression, material
dimensions, uncertainty and minimum sufficient fidelity. A coarse value may be accepted when it is
honest and sufficient; missing precision is not a validation failure by itself.

When a target series already exists, the intake proposal must explicitly choose `refine`,
`correct`, `add_alternative` or `withdraw`. A storage field update has no independent semantic
meaning and cannot bypass lineage or Claim/Evidence review.

Research originals, GIS and media may remain in Google Drive; authorized curated records may live
in Airtable; contracts, frozen evidence, reviews and decisions live in GitHub. These systems do not
become competing truth owners. AI may propose candidate revisions or source leads, but cannot act
as Source, approve its own proposal or silently publish a frontier value.

Ledger acceptance and public publication are separate decisions. A valid revision may remain
non-public, and a public projection may generalize it without changing the accepted source-native
value.

## 6. Dimension-specific refinement

### 6.1 Temporal values

A temporal refinement must:

- keep the same assertion target and calendar profile;
- be contained by the predecessor's possible interval;
- reduce the interval or establish a finer supported precision;
- carry its own atomic Claim and evidence;
- preserve open, approximate or alternative semantics when they remain material.

Executable subset validation covers the primary interval and every explicit alternative, including
open bounds, inclusivity and qualified-bound direction. Every refined member must be contained by
at least one predecessor member, and the calendar/normalization profile remains identical. A new
alternative outside the predecessor possible set is `add_alternative`, not `refine`.
Strictness is evaluated over the union of the primary interval and all alternatives, not only the
primary bounds. A retained universal/unknown alternative therefore prevents a false narrowing.
Open-to-finite and inclusivity narrowing are valid set reductions; equal single-member sets require
a strictly finer supported precision.
The validator canonicalizes and merges the interval union before testing strictness; splitting one
unchanged predecessor interval across primary and alternative members is not a refinement.
The top-level temporal precision and the precision carried by `valid_time` are one semantic value
and must agree exactly. A finite primary or alternative interval must represent a non-empty set;
an exclusive instant or another inclusivity combination that removes every represented day is
invalid rather than an empty refinement.
Within one revision, every temporal alternative must be no finer than both the source-native and
top-level temporal precision. A materially finer alternative requires its own atomic Claim/source
and `add_alternative` revision rather than borrowing a coarser revision's evidence.

The temporal envelope carries the accepted #330 semantics rather than reducing them to two dates:
calendar/normalization state, exact or qualified bounds, inclusivity, open-start/open-end/unknown
kind, precision, basis Claims and explicit alternatives. A refinement may narrow a possible set,
but it cannot discard an open bound, qualifier, calendar state or alternative merely because the
current fixture uses a finite Gregorian example.

An interval is not refined merely because a midpoint was chosen.

### 6.2 Points, places and fuzzy areas

A spatial refinement may narrow:

- an explicit tolerance around a point;
- a fuzzy bounding area or probability/possibility envelope;
- a named region to a contained named place when the containment relation is evidence-bound;
- an inferred corridor to a narrower supported corridor.

Coordinates alone do not establish accuracy. The normalized precision label cannot exceed the
source-native/evidence precision.

### 6.3 Routes and trajectories

Documented presences and movement gaps are separate targets. Better evidence for an endpoint does
not create route geometry between endpoints.

`unknown_route` requires `geometry=null`. A later `documented_path` or `inferred_corridor` is a new
revision with its own evidence or assumptions; it cannot be synthesized from display
interpolation.

### 6.4 Temporal Regions and ecological ranges

Two cases must remain distinct:

1. a different `valid_time` means another world state or geometry version;
2. the same `valid_time` with a later `recorded_at` means revised knowledge of that world state.

A coarse ecological range may start as a fuzzy area. Later evidence may narrow that same
valid-time reconstruction or add an alternative. A real range shift is encoded as another temporal
State/Region version, not as refinement lineage across valid times.

For every non-temporal target, `refine`, `correct` and `add_alternative` preserve the predecessor's
full `valid_time` semantic envelope. A correction to a spatial value may move the geometry, but it
cannot silently move that geometry to another world state; that requires a different atomic
valid-time target/series.

## 7. Deterministic current view

The current view is a derived frontier, not a mutable `current=true` flag:

1. process revisions by `recorded_at` and stable id;
2. `initial` adds its value;
3. `refine` and `correct` remove their predecessors and add the new revision;
4. `add_alternative` keeps its predecessors and adds the new revision;
5. `withdraw` removes its predecessors and adds no value.

Every predecessor must already exist in the same series. Cycles, orphan lineage and future-dated
predecessors fail closed.

If the frontier contains multiple values, the current selection is
`unresolved_alternatives`. Array order, confidence, recency and visual convenience cannot silently
select a winner. Choosing a preferred reconstruction requires a separate reviewed policy/Claim.

Any earlier accepted view can be reconstructed by applying the ledger up to a record-time cutoff.

## 8. Fidelity budget and stop rule

Each curation task declares a decision target and the minimum material resolution required for the
dimensions it touches. Research stops when all required dimensions are honest and sufficient for
that decision.

Refinement receives priority only when it can materially change at least one of:

- object identity;
- temporal ordering or boundary inclusion;
- overlap/co-presence classification;
- visible geometry at the decision scale;
- relation interpretation;
- user understanding;
- trust/safety;
- the gate decision.

Hour/minute resolution, building-level coordinates, meter-scale borders, complete paths and
exhaustive source coverage are not default goals. Unknown remains an acceptable current value when
further precision would not change the active decision or lacks evidence.

## 9. Projection and UI rules

Projection may generalize a value for the current zoom/time scale, but must preserve access to the
source-native value, uncertainty and lineage.

Required representations include:

- range or band for temporal uncertainty;
- tolerance/fuzzy area for approximate spatial values;
- named place without invented centroid when geometry is unresolved;
- visible alternative reconstructions;
- inferred corridor visibly distinct from documented path;
- gap/no line for `unknown_route`;
- geometry-withheld Region rather than a plausible polygon.

Smooth animation must not interpolate an unsupported historical path or boundary.

## 10. Corrections, conflicts and withdrawal

A correction records why the predecessor was materially wrong and keeps both evidence chains.
Conflicting sources may instead create alternatives when no reviewed basis selects one.

Withdrawal removes a revision from the current view because of retraction, invalid evidence,
scope error or governance decision. It does not delete the Claim, Source, EvidenceLink or earlier
views.

Revision operation, review state, confidence and evidence state remain independent. A newer
revision is not automatically stronger or reviewed.

## 11. Compatibility and migration

Legacy mutable records without history import as one `initial` revision only when their source
value, provenance and precision can be represented honestly. ARTEMIS must not manufacture prior
revisions from database timestamps or infer a refinement chain from current values.

A storage system may denormalize the current frontier for performance, but the append-only ledger
and Claim/Evidence lineage remain authoritative. Airtable, database, API and renderer mappings must
round-trip without losing operations, predecessor refs, source-native values or valid/record time.

The frozen Leonardo Gate C package is not migrated or re-curated by this contract. Gate D may
consume it only at its frozen fidelity until a separately authorized revision contour exists.

## 12. Executable fixture boundary

The v1 fixture package must cover:

- a Leonardo-like presence refined from a coarse interval to a supported day;
- independent spatial refinement for the same stable subject;
- an `unknown_route` that remains geometry-null;
- a fuzzy ecological range refined for one valid-time state;
- a different valid-time range state that is not linked as a refinement;
- correction, alternative and withdrawal operations;
- deterministic current frontier and historical record-time replay;
- source-native precision and Claim/Evidence closure.

Negative tests must reject mutation-by-omission, false refinement, orphan/cyclic/cross-series
lineage, unsupported precision, valid/record-time collapse, invented route geometry, automatic
alternative winner and erased evidence/history.

Passing fixtures proves the mechanism is representable. It does not prove historical accuracy,
runtime/storage implementation, user value or public readiness.

## 13. Change control

Acceptance requires:

- issue `#377` scope and explicit non-goals;
- synchronized routing/operational documents without changing `project_state.json`;
- versioned fixture, schema, validator and controlled-corruption tests;
- one frozen reviewed content revision;
- a fail-closed review request/registry that binds both reviewer instances to that exact revision
  and one reviewed-content digest;
- two independent reviews covering semantic content and validator integrity;
- zero unresolved critical/material findings;
- one machine-validated decision artifact: `ACCEPT`, `NARROW` or `REJECT`, bound to the same frozen
  commit/tree, reviewed-content digest and review registry.

Lifecycle normalization is limited to the exact approved version/status header values. It cannot
hide extra authorization or semantic text. Every EvidenceLink and Uncertainty is bidirectionally
reachable from its Claim/revision, and a refinement in one dimension cannot mutate another
dimension's full semantic envelope (including calendar, inclusivity, qualifiers and alternatives).
All decided outcomes, including `NARROW` and `REJECT`, bind the frozen commit and tree.
The review request itself is byte-identical to the copy in the frozen commit, so neither reviewed
scope nor pre-issued reviewer identity can change after content freeze. Capability prohibitions are
enforced directly by reviewed validator code, independent of mutable control-schema wording.
The request, registry, review-artifact and acceptance-decision schemas are also byte-bound to the
frozen commit, preventing post-review introduction of new authorization fields or relaxed controls.
The completed envelope also preserves `prior_reviews` exactly from the frozen registry, so negative
review history and its artifact bindings cannot be erased during the metadata-only READY transition.
Every `review_id` across prior and current registry entries is unique, and every review artifact has
unique `finding_id` values. Package, registry and contract lifecycle headers must resolve to one
state: a non-READY registry keeps the package/contract `REVIEW_REQUIRED`, while `READY` requires all
three to transition together. After content freeze, the descendant may change only the exact
package/contract lifecycle files, registry, acceptance decision and the two pre-issued current review
artifacts; any other changed path invalidates READY even when it was outside `review_scope`.
Canonical READY validation runs only on a clean Git index/worktree with no untracked or ignored
files. It rejects tracked index entries marked `assume-unchanged`, `skip-worktree` or another
nonstandard visibility state, forces a full index refresh, then evaluates cleanliness. Every allowed
lifecycle/control path must resolve to a regular in-repository `100644` Git blob; symlinks and
external mutable payloads are invalid.

Changes after `READY` require a new version and review. Runtime or storage implementation requires a
separate migration decision.

## 14. Final rule

ARTEMIS improves knowledge by adding traceable, evidence-bound revisions. It never improves the
appearance of certainty by overwriting history or inventing detail.
