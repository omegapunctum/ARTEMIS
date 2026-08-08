# ARTEMIS — RELATION SEMANTICS CONTRACT v1

## Status

- Type: canonical semantic contract candidate for issue `#331`.
- Date: 2026-08-08.
- Version: `1.0.0`.
- Dependencies: Foundation v3 World Model (`#329 / PR #336`) and Uncertainty Semantics (`#330 / PR #337`).
- Executable registry: `fixtures/world_model/relations/v1/predicate_registry.json`.
- Validation: `scripts/validate_relation_semantics.py`.
- Promotion status: this candidate becomes the active relation owner only after review/merge; until then the accepted World Model and uncertainty owners remain authoritative.

## 1. Purpose

`Relation` is reserved for an **explicitly asserted relation between canonical knowledge objects**, backed by Claim/Evidence semantics appropriate to the predicate.

ARTEMIS must not turn every spatial-temporal coincidence into a graph edge.

The central distinction is:

```text
Observation / computed overlap / similarity
                ≠
              Relation
```

A Relation states that the evidence/claim layer supports a named relation predicate. It is not merely the output of a spatial, temporal or statistical query.

## 2. Relation v1 scope

Relation v1 is intentionally small.

Only predicates registered in the executable predicate registry are valid.

Initial registered predicates:

1. `documented_encounter`;
2. `influence`.

No generic `related_to`, `associated_with`, `connected_to` or automatically inferred predicate is admitted in v1.

A new predicate requires a contract/registry change plus positive and negative tests. Adding a string in content data is insufficient.

## 3. Core Relation shape

A Relation uses the World Model record shape:

```text
Relation
├── id
├── type = Relation
├── subject_ref
├── predicate
├── object_ref
├── directionality
├── temporal_extent
├── spatial_extent
├── mechanism?     # predicate-dependent
├── scope?         # predicate-dependent
├── claim_refs[]
├── uncertainty_refs[]
└── layer_refs[]
```

Rules:

- `subject_ref` and `object_ref` resolve to canonical Entity IDs in relation v1;
- self-relations are forbidden for all v1 predicates;
- predicate semantics come from the registry, not from UI labels;
- `directionality` must equal the registry rule;
- Relation Claim/Evidence requirements are predicate-specific;
- Relation temporal/spatial extents remain evidence-bound and must not be expanded for visual convenience;
- a renderer may visualize a Relation only after the Relation exists semantically; renderer proximity cannot create one.

## 4. Predicate: `documented_encounter`

### Meaning

A source-backed assertion that the two endpoint Entities encountered/interacted at the asserted time/place.

It does **not** mean:

- they merely occupied the same city/region/time window;
- they were similar;
- one influenced the other;
- they had an enduring social relationship beyond the documented encounter.

### Contract

- semantic class: `documented_interaction`;
- directionality: `symmetric`;
- self relation: forbidden;
- `mechanism`: not required and must not be used to smuggle causal meaning;
- `scope`: optional;
- required Relation Claim kind: `factual`;
- required evidence: at least one reviewed supporting EvidenceLink;
- required minimum supporting evidence strength: `direct`;
- uncertainty: optional when the encounter is well supported; required when the Relation/Claim is explicitly contested or evidence materially conflicts.

### Symmetry

`A documented_encounter B` has the same semantic meaning as `B documented_encounter A`.

The data layer must not contain mirrored duplicates for the same predicate/endpoints/semantic assertion.

Symmetry does **not** make all endpoint roles in the supporting Event/Source interchangeable; it only defines Relation directionality.

## 5. Predicate: `influence`

### Meaning

A source-backed **interpretive directional claim** that the subject affected the object within an explicit mechanism and scope.

`influence` is stronger than:

- temporal precedence;
- co-presence;
- geographic proximity;
- similarity;
- participation in the same Process;
- a plausible narrative inferred by AI or curator without supporting evidence.

It is weaker/more scoped than a universal causal assertion. The predicate says only what the bounded Claim/Evidence supports.

### Contract

- semantic class: `interpretive_influence`;
- directionality: `directed`;
- self relation: forbidden;
- `mechanism`: required, non-empty;
- `scope`: required, non-empty;
- required Relation Claim kind: `interpretation`;
- required evidence: at least one reviewed supporting EvidenceLink;
- supporting evidence may be challenged by other EvidenceLinks;
- if the claim is `contested`, evidence is `mixed`, or a reviewed EvidenceLink challenges it, material uncertainty must be explicit on both the Relation and its principal Claim;
- uncertainty must never be converted into visual confidence by the renderer.

### No causal shortcut

The following sequence is invalid:

```text
A happened before B
        ↓
A influenced B
```

Temporal ordering may be one input to research, but it cannot satisfy the `influence` predicate contract by itself.

## 6. Relation Claim binding

Every Relation must have at least one principal Claim that explicitly targets the Relation record.

For each Relation principal Claim:

- `target_refs` contains the Relation ID;
- the Claim kind is allowed by the predicate registry;
- at least one reviewed supporting EvidenceLink resolves to that Claim;
- each EvidenceLink resolves to a Source;
- evidence locators remain source-specific evidence pointers;
- Relation and Claim uncertainty references are compatible with the evidence/review state.

A Claim about two Entities that does not target the Relation is not enough to create a Relation edge automatically.

## 7. Evidence requirements

### Supporting evidence

At least one reviewed EvidenceLink with `relation_to_claim = supports` is required for every Relation principal Claim.

Predicate-specific minimum evidence strength applies.

For v1:

- `documented_encounter` requires at least one `direct` supporting EvidenceLink;
- `influence` requires at least one reviewed supporting EvidenceLink; the interpretation remains bounded by mechanism/scope and may remain contested.

### Challenging evidence

A reviewed `challenges` EvidenceLink does not delete the Relation automatically.

Instead it changes the epistemic state:

- contested/mixed semantics must remain visible;
- material uncertainty must be referenced;
- UI/renderers may expose competing evidence but may not silently choose certainty.

## 8. Relation vs DerivedObservation

`DerivedObservation` records computational/analytical results that are useful for exploration but do not themselves assert a Relation.

Examples:

- co-presence;
- overlapping time intervals;
- same-place overlap;
- similarity;
- proximity;
- synchronized global context.

Rule:

```text
DerivedObservation.relation_created = false
```

for the current co-presence fixture.

A DerivedObservation may motivate research. It may not be promoted to Relation unless a **new explicit Relation Claim + Evidence** satisfies a registered predicate contract.

The observation itself is not supporting historical evidence for `documented_encounter` or `influence`.

## 9. Co-presence is not encounter

If two people are modeled as present at the same place during overlapping time:

- ARTEMIS may show them together in context;
- ARTEMIS may produce a `co_presence` DerivedObservation;
- ARTEMIS must not say they met;
- ARTEMIS must not create `documented_encounter`;
- ARTEMIS must not create `influence`.

This distinction is foundational for Life in Context: showing simultaneous context must not fabricate interaction.

## 10. Similarity is not Relation

Similarity/search/recommendation outputs remain analytical or UI results unless a registered semantic predicate with evidence explicitly applies.

Forbidden shortcut:

```text
high similarity score → Relation
```

## 11. Process/sequence is not influence

A Process or ordered set of stages may show sequence, spread, change or analytical grouping.

Unless the World Model contains an explicit Relation Claim satisfying `influence`:

- earlier stage does not influence later stage automatically;
- geographic spread does not establish diffusion mechanism;
- visual arrows do not authorize semantic directionality.

## 12. Renderer rule

Render Projection / 2D / Globe layers consume accepted Relations; they do not create them.

Renderer-only operations that **cannot** alter Relation semantics:

- clustering;
- bundling;
- line curvature;
- arrow styling;
- camera/zoom;
- spatial proximity;
- timeline animation;
- terrain draping;
- AI-generated explanatory copy.

Any renderer relation payload must preserve:

- Relation ID;
- subject/object IDs;
- predicate;
- directionality;
- temporal/spatial validity;
- Claim refs;
- uncertainty refs;
- mechanism/scope where required.

Relation rendering remains deferred in Render Projection v1 until this contract is accepted.

## 13. AI rule

AI may:

- suggest candidate relations for review;
- surface possible evidence;
- explain an accepted Relation and its uncertainty;
- identify co-presence/similarity as research leads.

AI may not:

- create an accepted Relation from narrative plausibility;
- convert temporal order into influence;
- convert co-presence into encounter;
- invent mechanism/scope/evidence;
- treat its own output as Source.

Candidate AI output remains a hypothesis/draft until curated evidence satisfies the contract.

## 14. Duplicate/mirror rule

For symmetric predicates, a mirrored endpoint record with the same predicate and semantic assertion is forbidden.

For directed predicates:

- `A influence B` and `B influence A` are distinct possible claims;
- each direction requires its own evidence/Claim contract;
- reverse direction must never be generated automatically.

## 15. Executable registry

`fixtures/world_model/relations/v1/predicate_registry.json` is the machine-readable v1 registry.

It owns executable constraints for:

- predicate ID;
- semantic class;
- directionality;
- mechanism/scope requirements;
- allowed Claim kinds;
- minimum supporting evidence strength;
- self-relation policy;
- inference policy.

The registry is contract evidence, not historical content.

## 16. Validation requirements

`scripts/validate_relation_semantics.py` must validate the reviewed synthetic World Model package without rewriting it.

It checks at least:

- all Relation predicates registered;
- endpoint identity/type;
- directionality;
- self relation;
- mechanism/scope requirements;
- Relation-targeting principal Claims;
- Claim kind;
- supporting EvidenceLinks and Sources;
- predicate evidence strength;
- contested/challenged uncertainty requirements;
- symmetric mirror duplicates;
- DerivedObservation non-promotion;
- no unregistered semantic shortcut.

Negative tests must prove that each barrier fails closed.

## 17. Versioning

Relation predicate meaning is versioned semantic API.

Breaking changes include:

- changing directionality;
- weakening evidence requirements;
- changing predicate meaning/class;
- making mechanism/scope optional where previously required;
- allowing inference from DerivedObservation;
- allowing a previously forbidden endpoint type.

Such changes require a new contract/registry version and migration analysis.

## 18. Definition of Ready for Relation v1

READY requires:

1. registry/schema exists;
2. reviewed #329 World Model Relation fixtures pass;
3. negative cases fail closed;
4. uncertainty rules align with #330;
5. no DerivedObservation is silently promoted;
6. Release/Relation CI is green;
7. at least one independent semantic review confirms that predicate meaning/evidence barriers are sufficient.

Until independent review is recorded, the implementation may be technically complete but must not be labeled READY.

## 19. Non-goals

Relation v1 does not attempt to define every human relationship.

Not included yet:

- kinship ontology;
- membership/office/ownership taxonomies;
- treaty/diplomatic relation families;
- causal graph engine;
- probabilistic relation inference;
- similarity edges;
- AI-generated relationship graph;
- automatic social network reconstruction.

Add them only when real World Slice evidence requires them.

## 20. Final invariant

**ARTEMIS may show that two things coincide before it may claim that they are related.**

A Relation exists because an explicit registered predicate is supported by Claim/Evidence semantics — not because a map, timeline, algorithm or AI makes the connection look plausible.
