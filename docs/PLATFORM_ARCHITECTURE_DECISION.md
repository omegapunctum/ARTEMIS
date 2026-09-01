# ARTEMIS — PLATFORM ARCHITECTURE DECISION

## Status

- Type: canonical architecture decision.
- Date: 2026-09-01.
- Status: ACCEPTED.
- Owner: application platform, delivery, renderer and repository/storage boundary.
- Capability truth remains owned by `docs/PROJECT_TRUTH.md`.
- Repository/runtime structure remains owned by `docs/PROJECT_STRUCTURE.md`.

This document answers four recurring architecture questions:

1. Is ARTEMIS a website, application, desktop program or PWA?
2. Are 2D Map and Globe separate product directions?
3. How must the application scale when the corpus grows?
4. What belongs in Git/GitHub versus operational data storage and backups?

It is a platform decision, not a claim that all target infrastructure already exists.

---

## 1. Decision

### 1.1 Canonical application platform

ARTEMIS is a **web-first Web Application**.

Browser execution is the canonical client platform for the current product direction. A public landing page may behave like a website, but the ARTEMIS Explorer itself is an interactive application.

`PWA` is a delivery/install capability of the same Web Application, not a separate product architecture. A future desktop or mobile wrapper may likewise package the same product when justified by evidence; it must not create a competing semantic core.

Therefore the canonical distinction is:

```text
ARTEMIS product
└── Web Application
    ├── Browser delivery            — canonical/current
    ├── PWA install/offline mode    — optional capability
    └── Future native wrapper       — gated, only if justified
```

The project must not maintain independent "website", "PWA", "desktop" and "mobile" product architectures unless a future accepted decision explicitly proves that the shared Web Application boundary is insufficient.

### 1.2 One core, many presentation renderers

2D Map and Globe are **presentation renderers of one ARTEMIS Explorer**, not separate products and not separate historical/data systems.

Both must consume the same semantic chain:

```text
World Model
    ↓
Explorer State
    ↓
Render Projection / query boundary
    ↓
┌───────────────┬───────────────┐
│   2D Map      │     Globe     │
└───────────────┴───────────────┘
```

Renderer-local concerns may differ: camera, projection math, GPU resources, tile caches, picking buffers, transitions and visual styling. They must not own canonical entity identity, historical truth, temporal semantics, Claims, Evidence, Sources or Uncertainty.

The current Globe is the active product-development surface for `Life in Context`. This does **not** redefine ARTEMIS as "a Globe product" and does not authorize a parallel 2D product branch.

### 1.3 Timeline is shared exploration state, not a third product direction

Time controls are part of the shared Explorer interaction model. `Range`, `Scrub` and future time navigation modes must modify renderer-neutral selected time/state and then be projected to whichever spatial renderer is active.

A 2D Map, Globe and timeline may have separate UI components, but they are synchronized views over one exploration state.

### 1.4 Source-federated semantic boundary

M4 under issue `#355` records `ADOPT` for the source-federated semantic direction.

Bounded external or curated source inputs may use source-specific adapters, but normalized output must enter one canonical path:

```text
source snapshot/intake
        ↓
Claim + EvidenceLink + Source + Uncertainty
        ↓
World Model → Explorer State → Render Projection
```

Normalization must preserve provider identity, source-native locator/revision, rights, precision, uncertainty and material agreement/challenge/refinement semantics. A provider adapter must not become a second ontology, silently merge competing Claims or invent missing evidence and geometry.

This is a semantic architecture decision, not authorization for live federation, automatic reconciliation, generic ingestion infrastructure, backend/storage migration or public runtime data. The current safe intake remains deterministic and reviewable through bounded source-specific snapshots or curated packages. Shared infrastructure requires later measured evidence that these bounded mechanisms are insufficient.

---

## 2. Scaling decision

Corpus growth does not require migration from a Web Application to a desktop program.

The scaling boundary is **data access and projection**, not client packaging.

The client must not receive the complete ARTEMIS corpus. As data volume grows, the architecture must preserve the ability to request only the material required for the current exploration state, including where relevant:

- visible spatial extent;
- selected or visible time interval/current time;
- active semantic layers;
- selected entities/relations;
- appropriate level of spatial/temporal/detail precision;
- source/evidence details only when requested or required by disclosure policy.

Conceptually:

```text
ARTEMIS Web App
      ↓
Explorer State
      ↓
Query / Projection boundary
      ↓
Authoritative data + indexes + derived delivery artifacts
```

This permits progressive loading, spatial/temporal filtering, level-of-detail strategies, tiles and caching later without changing the product identity.

### 2.1 Progressive refinement and progressive loading are compatible but distinct

ARTEMIS must preserve the existing semantic requirement that knowledge can be refined from coarse/approximate to precise without destructive remodeling.

That semantic refinement must not be confused with runtime loading optimization:

- **progressive refinement** concerns what the data means and how improved knowledge supersedes or narrows prior knowledge;
- **progressive loading / LOD** concerns how much of that knowledge is transmitted/rendered for the current view.

Neither mechanism may manufacture false precision.

### 2.2 No premature production-scale infrastructure

This decision does **not** require immediate migration to PostgreSQL/PostGIS, graph databases, vector-tile services, object storage, distributed caches or microservices.

Those are implementation choices to be introduced only when current evidence, corpus size, latency, concurrency or operational needs justify them.

The architecture must remain compatible with such evolution, but MVP work must not build infrastructure for hypothetical scale before the central `Life in Context` value is validated.

---

## 3. Repository and storage decision

### 3.1 GitHub and local clones are complementary

The canonical source-code collaboration/history remote is the GitHub repository `omegapunctum/ARTEMIS` unless superseded by an explicit repository-governance decision.

Normal working topology:

```text
GitHub canonical remote
        ↕
local working clone(s)
        ↕
independent backup / mirror where appropriate
```

GitHub is not a substitute for a local working copy, and a local PC is not a substitute for an off-device remote.

Recommended responsibilities:

- **GitHub remote** — canonical shared commit history, `main`, branches, pull requests, issues, CI/CD and canonical documentation;
- **local clone** — development workspace and local Git history;
- **independent backup/mirror** — resilience against account, device or provider failure when project value warrants it.

A removable drive may be used for backup/mirror purposes, but it must not become the only canonical repository.

### 3.2 Git is not the future ARTEMIS corpus database

Git/GitHub should contain items that benefit from reviewable version history and remain practical repository assets, such as:

- source code;
- schemas and migrations;
- canonical documentation;
- tests;
- small deterministic fixtures;
- configuration and release metadata;
- small checked-in public artifacts while they remain operationally appropriate.

A production-scale ARTEMIS corpus must not be stored as an ever-growing mass of repository JSON/GeoJSON, imagery, terrain, tiles, source documents or generated binary artifacts.

As scale requires, operational data belongs behind explicit storage/query boundaries such as relational/spatial storage, indexes, object storage, tile delivery and backups. Exact technologies remain undecided until justified.

### 3.3 Repository data is not automatically semantic truth

Checked-in fixtures and delivery artifacts may provide executable evidence or current public projections. Their presence in Git does not by itself make them the canonical semantic owner of the World Model.

The semantic/source-of-truth rules remain governed by the relevant data, epistemic, World Model and capability contracts.

---

## 4. Current implementation versus target

### Current implementation

As of 2026-08-29:

- the public product is browser-executed through GitHub Pages;
- `/globe/` is the primary Leonardo research prototype;
- `/atlas/` is a compatibility-only 2D Architecture Atlas surface;
- PWA code/manifest/service-worker capability exists in the compatibility system but is outside the active Core critical path;
- GitHub Pages is static and does not execute the preserved FastAPI backend;
- current small checked-in fixtures/artifacts are acceptable for the bounded prototype/review scope.

For exact maturity/public availability, always defer to `docs/PROJECT_TRUTH.md`.

### Target architecture implied by this decision

ARTEMIS may grow into a larger web-delivered system with server-side query/storage infrastructure while preserving:

1. one semantic World Model;
2. one renderer-neutral Explorer State;
3. multiple presentation renderers;
4. source/evidence/uncertainty semantics independent of renderer;
5. progressive data access rather than full-corpus client loading;
6. replaceable storage/delivery implementations behind explicit boundaries.

This target is an architectural compatibility direction, not an implementation commitment for the current gate.

---

## 5. Non-goals

This decision does not authorize:

- a separate native desktop ARTEMIS implementation;
- a separate mobile product codebase;
- a new parallel 2D ARTEMIS development vertical;
- making PWA/offline installation a current MVP requirement;
- replacing the current Globe as active `Life in Context` validation surface;
- migrating the current data stack only for hypothetical future scale;
- microservices;
- a graph database;
- production-scale dynamic Earth infrastructure;
- duplicating semantic data per renderer;
- storing the future universal corpus in GitHub.

Each such expansion requires its own evidence-backed decision if and when it becomes necessary.

---

## 6. Invariants

The following are canonical platform invariants:

1. **ARTEMIS is web-first.** Browser execution is the canonical client platform until an explicit accepted decision changes it.
2. **PWA is packaging/delivery, not a second architecture.**
3. **2D Map and Globe are renderers, not separate products.**
4. **Renderer choice cannot change historical/semantic truth.**
5. **Timeline state is renderer-neutral Explorer State.**
6. **Client scale is controlled by query/projection/loading boundaries, not by sending the whole corpus.**
7. **Large operational datasets do not belong in Git merely because current prototypes use checked-in artifacts.**
8. **GitHub remote + local clone + independent backup are complementary roles, not mutually exclusive storage choices.**
9. **Future infrastructure must be introduced in response to measured need, not speculative scale.**
10. **One semantic core must survive changes in renderer, delivery mechanism and storage technology.**

---

## 7. Conflict routing

If another document says or implies that:

- ARTEMIS is fundamentally a PWA rather than a Web Application;
- Globe and 2D Map own separate semantic/data cores;
- a renderer owns canonical temporal or historical truth;
- the complete future corpus should live in Git/GitHub;
- a desktop/native rewrite is required solely because data volume grows;

this document owns the platform-level decision, while `PROJECT_TRUTH.md` still owns what is actually implemented and public now.

If code conflicts with this decision, code describes current implementation but the mismatch must be classified explicitly rather than silently redefining the decision.

---

## 8. Change control

Changing any of the following requires an explicit architecture decision and documentation synchronization:

- canonical client platform away from web-first;
- creation of a semantically independent renderer/product branch;
- replacement of shared Explorer State with renderer-owned state;
- repository becoming an operational corpus database by design;
- adoption of a platform constraint that prevents renderer/storage replaceability.

Ordinary implementation changes inside the accepted boundaries do not require reopening this decision.

---

## 9. Final rule

ARTEMIS is one spatial-temporal knowledge application with one semantic core. Browser/PWA/future wrappers are delivery choices; 2D/Globe are presentation choices; storage technologies are implementation choices. None of them may fragment the World Model or become a substitute for the product itself.
