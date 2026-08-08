# ARTEMIS — Geospatial Assets / Terrain / Imagery Contract v1

## Status

- Type: working executable contract proposal.
- Date: 2026-08-08.
- Parent issue: #342.
- Architecture: #339 / PR #346 (merged).
- Explorer State: #340 / PR #347 (merged).
- Render Projection: #341 / PR #348 (merged).
- Capability status: R&D infrastructure contract only; it does not select a provider or make 3D Globe `PUBLIC NOW`.

## 1. Purpose

ARTEMIS needs Earth-rendering infrastructure that can change independently from historical knowledge.

This contract defines how terrain, imagery, basemaps, tiles and related geospatial resources are described, licensed, cached and supplied to a renderer without becoming a second World Model.

The core distinction is:

```text
World Model / World Slice
= historical / analytical knowledge semantics

Render Projection
= deterministic knowledge → renderer projection

Geospatial Asset Manifest
= Earth-rendering infrastructure and contextual surfaces
```

A terrain tile being visible beneath an Event does not make the terrain tile an Event, State, Region or Source for that Event.

## 2. Architectural boundary

Geospatial assets may provide:

- terrain/elevation surface;
- raster imagery;
- raster/vector basemap context;
- raster/vector tiles;
- 3D Tiles or equivalent spatial rendering resources;
- analytical contextual surfaces where explicitly marked.

They do not own:

- `Entity`, `Event`, `State`, `Process`, `Trajectory`, `Region` or `Relation` meaning;
- selected historical time;
- World Slice membership;
- Claim/Evidence/Uncertainty truth;
- historical trajectory interpolation;
- historical borders merely because a provider serves vector tiles;
- historical terrain/coastline validity merely because a modern DEM or imagery layer is visible.

## 3. Three semantic roles

Every asset declares exactly one `semantic_role`.

### 3.1 `present_day_context`

Provides modern/current Earth context for orientation or rendering.

Examples:

- modern terrain DEM;
- current satellite imagery;
- current basemap labels;
- current coastlines used as non-historical visual context.

Rule: it must never imply that the same physical or political surface is historically valid at the Explorer State time.

### 3.2 `analytical_context`

Provides a derived or analytical spatial surface that is useful for interpretation but is not itself a historical assertion unless separately bound to World Model claims.

Examples:

- hillshade;
- generalized relief;
- density surface;
- non-authoritative grid or reference overlay.

### 3.3 `historical_reconstruction`

Represents a reconstruction that makes a claim about past spatial state.

Examples may include a reconstructed historical coastline, paleotopography or another temporally bounded physical surface.

This role requires:

- explicit historical validity interval;
- explicit provenance;
- explicit World Model Claim references or equivalent accepted knowledge bindings;
- explicit uncertainty references field;
- a reconstruction method identifier/description;
- a visible distinction from modern context.

Historical reconstruction assets remain renderer/geospatial resources; the meaning of their historical assertion must still be anchored in the World Model / evidence layer.

## 4. Manifest identity

The manifest is a versioned runtime/R&D configuration artifact, not public historical data.

Conceptual shape:

```text
GeospatialAssetManifest
├── schema_version
├── manifest_id
├── manifest_mode
└── assets[]
    ├── asset_id
    ├── label
    ├── asset_kind
    ├── semantic_role
    ├── provider
    ├── spatial_reference
    ├── coverage
    ├── temporal_semantics
    ├── provenance
    ├── licensing
    ├── cache_policy
    └── runtime_policy
```

`asset_id` identifies the logical configured asset. Provider credentials are never part of that identity.

## 5. Asset kinds

Contract v1 recognizes:

- `terrain_elevation`;
- `raster_imagery`;
- `raster_basemap`;
- `vector_basemap`;
- `raster_tiles`;
- `vector_tiles`;
- `three_d_tiles`;
- `analytical_surface`.

The asset kind is technical/rendering information. It does not define historical semantics.

## 6. Provider abstraction

Provider metadata is isolated under `provider`.

Required concepts:

- `provider_id`;
- `adapter_kind`;
- optional public endpoint/template;
- `credential_mode`;
- optional environment-variable name for a runtime credential.

Rules:

1. literal API keys, access tokens, passwords, signatures and secrets are forbidden in the manifest;
2. provider URL/query parameters must not contain credential material;
3. a required credential is referenced only by environment/config indirection;
4. provider URL, account ID or credential name must never enter World Model semantics;
5. swapping provider infrastructure must not change World Slice meaning;
6. static GitHub Pages cannot safely hold a private runtime secret, so an asset requiring `runtime_secret` cannot be marked `public_pages_allowed=true`.

## 7. Coordinate reference policy

Every asset declares a source horizontal CRS.

The neutral Render Projection v1 remains `EPSG:4326` longitude/latitude. A renderer/provider adapter owns any required transformation from asset coordinates into its engine coordinate system.

No provider-specific CRS assumption is allowed to silently modify World Model geometry.

Minimum metadata:

- `horizontal_crs`;
- `axis_order`;
- vertical reference object;
- height unit where vertical values exist.

## 8. Vertical reference and height semantics

Vertical semantics are intentionally separated from the current Render Projection v1, which remains `vertical_semantics=not_modeled`.

A terrain/elevation or height-bearing 3D asset must declare:

- vertical mode: `ellipsoidal_height` or `orthometric_height`;
- vertical datum/reference name;
- height unit;
- positive direction.

A 2D imagery/basemap asset may use `not_applicable`.

Rules:

- terrain height cannot be copied into canonical World Model objects merely because it is available;
- clamping a visual marker to terrain is a renderer operation unless altitude itself is part of an accepted historical assertion;
- absolute historical altitude requires its own model/evidence semantics before it can become knowledge;
- vertical datum conversion must be explicit when materially relevant.

## 9. Coverage and resolution

Every asset describes its usable spatial envelope and quality bounds.

Minimum fields:

- WGS84 coverage bbox for discovery/intersection;
- optional source resolution range;
- optional LOD/zoom range;
- coverage kind (`global` or `regional`).

Coverage absence must fail honestly. A provider's missing tile must not become a historical absence claim.

LOD/generalization is presentation infrastructure and must not change canonical knowledge identity or uncertainty.

## 10. Temporal semantics

`temporal_semantics.mode` is one of:

- `current_context`;
- `dated_snapshot`;
- `not_applicable`;
- `historical_validity`.

Rules:

### Current context

- may be shown as modern orientation context;
- has no historical validity interval;
- has no World Model historical Claim binding;
- must be visually/semantically distinguishable from historical reconstruction when the selected ARTEMIS time is in the past.

### Dated snapshot

- carries a source/reference date;
- does not automatically become valid outside that observation date;
- remains contextual unless separately asserted through historical knowledge semantics.

### Historical validity

Required only for `semantic_role=historical_reconstruction`.

It requires:

- `valid_from`;
- `valid_to`;
- non-empty `world_model_claim_refs`;
- `uncertainty_refs` field;
- reconstruction method.

The renderer cannot extend validity beyond the declared interval.

## 11. Provenance

Every asset needs enough provenance to answer:

- who published/provided it;
- what dataset/product it represents;
- which version/edition is configured;
- when it was retrieved/configured;
- where its source/metadata can be inspected;
- whether it is synthetic fixture, official/open dataset, commercial provider or internal asset.

Provider marketing text is not provenance.

Historical reconstruction needs provenance for both the geospatial artifact and the knowledge/evidence that justifies its historical meaning.

## 12. Licensing and attribution

Every configured asset declares:

- license identifier/name;
- optional license URL;
- attribution text;
- whether attribution is required;
- redistribution status.

Redistribution statuses:

- `allowed`;
- `restricted`;
- `prohibited`.

Rules:

- unknown rights are not accepted in an executable production/prototype manifest;
- cached-byte redistribution cannot be enabled when redistribution is restricted/prohibited;
- provider attribution requirements must survive renderer integration;
- a Globe prototype must have a visible attribution path before provider promotion.

## 13. Cache and offline policy

Cache policy is explicit per asset.

It includes:

- whether browser/runtime caching is allowed;
- whether offline caching is allowed;
- whether cached bytes may be redistributed;
- optional maximum cache age.

Rules:

- licensing wins over performance convenience;
- offline cache cannot override provider terms;
- a service worker must not cache restricted provider responses merely because other ARTEMIS assets are cacheable;
- R&D fixtures may use permissive synthetic rules to test the contract.

## 14. Runtime/deployment policy

Each asset declares where it may run.

Minimum policy:

- allowed environments;
- network requirement;
- whether a runtime secret is required;
- whether it may be used from public GitHub Pages;
- fallback asset reference if any;
- failure policy.

Failure policy is explicit:

- `fail_closed` — do not substitute another semantically different asset;
- `fallback_allowed` — fallback is permitted only to the declared compatible asset.

A terrain failure must not silently cause a modern basemap or historical reconstruction to change semantic role.

## 15. Security rules

The manifest must reject:

- literal tokens/API keys/passwords/secrets;
- credential query parameters in endpoint templates;
- private secrets intended for browser-exposed Pages runtime;
- provider configuration embedded in World Model claims;
- unreviewed arbitrary script/plugin payloads.

Credential resolution belongs to runtime configuration, not checked-in historical data.

## 16. Provider-swap invariant

ARTEMIS must be able to change a terrain/imagery provider without changing:

- World Slice identity;
- Explorer State;
- Render Projection semantic items;
- canonical object IDs;
- historical Claim/Evidence/Uncertainty semantics.

Provider swap may change visual quality, coverage, latency, licensing and cost. Those differences are infrastructure decisions and must be evaluated separately.

## 17. Interaction with Render Projection

Render Projection contains knowledge geometry and semantic/epistemic references.

Geospatial assets provide environmental/rendering context around that projection.

Example:

```text
World Slice + Explorer State
        ↓
Render Projection
        ↓
Historical Region polygon / Event point / Trajectory segment
        +
Geospatial Asset Manifest
        ↓
Globe renderer
        ├── modern terrain context
        ├── imagery/basemap context
        └── ARTEMIS historical projection
```

The renderer may drape/project ARTEMIS primitives over an asset surface, but the asset does not rewrite the primitive's historical meaning.

## 18. Historical reconstruction gate

A geospatial asset can be labeled `historical_reconstruction` only when all are true:

1. temporal validity is explicit;
2. provenance is explicit;
3. historical Claim bindings are non-empty;
4. uncertainty field is present;
5. reconstruction method is explicit;
6. licensing is usable;
7. renderer presentation distinguishes it from present-day context.

Without those conditions it remains context/analysis, not historical reconstruction.

## 19. R&D fixture policy

The executable v1 manifest is synthetic and tests the infrastructure contract only.

It must not:

- imply endorsement of a real provider;
- imply production licensing readiness;
- claim real-world terrain/imagery freshness;
- create historical facts.

Real provider selection belongs to #343/#345 after current contracts are stable and should use evidence on performance, browser/runtime compatibility, attribution, cost and licensing.

## 20. Acceptance for #342

The contract is ready when tests prove at minimum:

- provider configuration can change without touching World Model semantics;
- terrain has explicit vertical reference;
- present-day context cannot declare historical validity;
- historical reconstruction cannot exist without validity + Claim binding;
- secret material is rejected;
- public Pages cannot require a private runtime secret;
- licensing constrains cache/offline behavior;
- duplicate asset identities are rejected;
- manifest/schema/validator are executable in CI.

## 21. Non-goals

This contract does not:

- choose Cesium, MapLibre Globe, Three.js or another engine;
- choose a production terrain/imagery provider;
- add altitude to the World Model;
- replace Render Projection;
- add historical terrain data to ARTEMIS;
- implement the 3D runtime spike (#343);
- change the current public Pages application.

## 22. Next dependency

After #342 is green, #343 may choose and implement a bounded Globe engine spike using:

- merged Explorer State;
- merged Render Projection;
- this geospatial asset/provider boundary.

#343 must not bypass these contracts for convenience.