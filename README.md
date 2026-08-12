# ARTEMIS

**ARTEMIS** is a source-aware spatial-temporal knowledge model about the world: an interactive environment for exploring entities, events, states and processes as synchronized layers across space and time.

The technical term **World Model** remains the name of the shared semantic core. At the North Star level, ARTEMIS models source-aware knowledge, claims, observations and reconstructions **about** the world; it does not claim to be objective reality, a complete digital twin or a complete model of human knowledge.

Its mission is to help people understand the world as an interconnected system—not as isolated map points, timeline entries or encyclopedia pages. Evidence remains mandatory through Claims, Sources, EvidenceLinks, locators and uncertainty, but it is the trust layer of the knowledge model rather than the product identity.

The long-term attractor is an explorable spatial-temporal model of human knowledge about the world in which people and future AI can traverse space, time, entities, events, states, processes, Claims, Evidence and Uncertainty as one connected cognitive environment. The attractor guides architecture; it does **not** authorize implementation scope.

Foundation v3 restored space and time as core coordinates. Foundation v3.1, accepted in PR `#364`, clarifies the attractor, one-semantic-core/many-domains/many-interfaces rule and future AI exploration boundary without changing current capability. The first validation vertical is **Life in Context**: follow a historical person's trajectory while seeing local events, regional states, documented relations when permitted, mere co-presence and selected simultaneous events elsewhere. Architecture Atlas remains the current public/technical baseline and a thematic layer.

The public runtime does **not** yet implement the Foundation target. A browser-executed MapLibre Globe R&D artifact exists, and issue #355 remains the source-aware Globe MVP product vertical. Gate C is completed/FREEZE for the non-public Leonardo-in-Romagna 1502 World Slice boundary; Gate D is now in progress as a non-public source-aware Globe experience. The Globe is not public or product-validated; generative AI, personal knowledge, causal reasoning, VR/AR and universal coverage remain future/gated scope.

This README is the **root documentation entrypoint and current baseline summary**. Detailed normative rules belong to the relevant canonical documents listed in the documentation section below.

---

## Overview

ARTEMIS currently combines:
- curated architecture data (Airtable → ETL → GeoJSON)
- interactive map visualization (MapLibre)
- backend implementations for auth, UGC/moderation and research workflows
- mutable ResearchSlice v2 compatibility runtime (backend-available, private/owner-only)
- stories and courses as frozen thin orchestration layers
- explain-context contract payloads without AI generation
- batch public publish pipeline
- progressive web app (PWA)

The current operational state is **controlled engineering prototype / Gate C frozen / Foundation v3.1 accepted / Gate D in progress and non-public**. See `docs/PROJECT_TRUTH.md` for the authoritative boundary.

### Current capability boundary

| Status | Meaning | Current examples |
|---|---|---|
| `PUBLIC NOW` | Works on GitHub Pages without backend execution | map, timeline/filter/detail baseline, checked-in `data/*` |
| `BACKEND-AVAILABLE` | Implemented in the repository but requires a separately deployed API | auth, slices, stories, courses, uploads, moderation |
| `PILOT` | Exists but lacks sufficient content/user validation | architecture corpus, comparison/relation experience |
| `R&D` | Executable experimental evidence, not a public capability | generated MapLibre 5.24.0 Globe spike and renderer contracts |
| `CONCEPT TARGET` | Defined but not implemented in public runtime | spatial-temporal knowledge model, Life in Context, State/Process/Trajectory/Region |
| `FUTURE` | Not an active product capability | source-bound AI/exploration actions, personal knowledge, causal/counterfactual runtime, production-scale dynamic Earth, VR/AR |

---

## Architecture

### Data Pipeline
- Source: Airtable (curated data)
- ETL: `scripts/export_airtable.py`
- Output:
  - `/data/features.json`
  - `/data/features.geojson`
  - `/data/id_aliases.json`
  - `/data/layers.json`
  - `/data/sources.json`, `/data/media.json`, `/data/relations.json`
  - `/data/validation_report.json`
  - `/data/content_profile.json`
  - `/data/export_meta.json`
  - `/data/rejected.json`
- Publication chain:
  1. Airtable `Features` records are exported by ETL
  2. validated artifacts are written to `data/*`
  3. public dataset is published only by batch overwrite through ETL/export workflow
  4. artifacts are committed to GitHub `main`
  5. GitHub Pages serves the map from published `data/*`

### Frontend
Vanilla JavaScript (no frameworks):

- `data.js` — data loading
- `map.js` — MapLibre integration
- `ui.js` — filters, list, state
- `auth.js` — authentication (in-memory tokens)
- `ui.ugc.js` — user drafts
- `ui.moderation.js` — moderation panel
- `pwa.js` — PWA logic

### Backend (canonical)
- FastAPI app entrypoint: **`app.main:app`**
- Canonical API base path: **`/api`**
- Auth API (JWT + refresh cookie)
- Drafts API (CRUD)
- Research Slices API (private/owner-only MVP: save, list, open/restore, delete)
- Stories API (thin orchestration layer over research slices: private/owner-only CRUD)
- Courses API (thin orchestration layer over stories: private/owner-only CRUD)
- Explain Context Contract API (`/api/explain-context` context payload for `slice|story|course`; AI generation/explanation mode is not part of current baseline)
- Upload API (images)
- Moderation API (review/approve/reject + Airtable staging sync; not direct public dataset publish)
- Airtable integration (staging sync for review outcomes; canonical public publish remains ETL/export workflow only)
- Upload lifecycle cleanup: orphan `/uploads/*` files are cleaned safely when drafts are updated/deleted and by periodic orphan scan.

### CI/CD
- GitHub Actions
- The workflow layer covers ETL/export, deploy/pages, release/readiness, and targeted integration checks
- `scripts/release_check.py` remains a canonical executable release/readiness entrypoint, but exact enforcement points must be read from the current workflow files rather than inferred from simplified README prose
- Dedicated integration workflows cover moderation and Redis-backed auth/session scenarios
- Data export and checked-in release artifacts must stay aligned with canonical docs and workflow semantics

---

## Key Principles

- Credentials, tokens, owner identity and private research content are never stored in `localStorage` or `sessionStorage`.
- Current low-sensitivity Web Storage use is limited to UI preference/session hints and frozen Courses progress; it is not a persistence contract for research data.
- Access token stored **in memory only**
- Refresh token stored in **httpOnly cookie**
- **GeoJSON is the single source of truth for the current public 2D map only**
- Canonical public dataset for map rendering: **`data/features.geojson`** (served from `/data/*`)
- `/api/map/feed` is an auxiliary, non-canonical runtime support/read-model route (not the production-default public map source)
- No direct Airtable access from frontend
- Minimal, clean code (no overengineering)

---

## Data Validation Rules

- `data/features.geojson` MUST be a valid GeoJSON `FeatureCollection` and MUST be non-empty for release.
- Every public Feature ID MUST be UUID v4; Airtable `rec...` IDs are provenance-only and resolve through `data/id_aliases.json`.
- `coordinates_source` uses a strict ETL allowlist; unknown values are rejected with `invalid_coordinates_source`.
- Rejected records are tracked in `data/rejected.json`, and aggregate reasons are exposed via `data/export_meta.json`.

## Static Runtime Constraints

- GitHub Pages is a static runtime: it serves frontend + published `data/*` without backend API execution.
- In static mode, auth refresh flow must not spam POST refresh attempts against unavailable endpoints.
- Auth refresh guard prevents recurring `405` noise on static runtime by using controlled fallback behavior.

## PWA Runtime Baseline Semantics (Current)

- Service worker static asset handling is currently **cache-first baseline** for static resources; freshness is tied to service worker update flow (new worker install/activation + update application), so static assets may remain stale until that flow completes.
- Offline baseline is currently **data-offline oriented**, not full app-shell offline navigation mode: map/data requests can fall back to cached data where present, but navigation itself is network-first/no-store and does not provide a dedicated offline shell fallback page.
- Private/auth/API requests are bypassed from SW cache handling (network-only path), and responses marked `Cache-Control: no-store` or `private` are intentionally not written to cache.

## Auth / Deployment Constraints (Current Baseline)

- `AUTH_SECRET_KEY` **must** be explicitly configured for real runtime; ephemeral per-process fallback is dev-only and not an acceptable deployment mode.
- Current auth/session guarantees should be treated as **baseline-capable but not fully production-hardened for multi-instance deployments**.
- The project already includes hardening work beyond the original memory-only MVP, including Redis-backed/session continuity proof paths and related integration coverage, but this should **not** be described as a finished production-ready multi-node auth/session architecture.
- Multi-instance scaling, persistence, and ops hardening are paused unless required by the public Architecture Atlas MVP or a critical reliability/security issue.
- Current persistence baseline uses a **shared SQLAlchemy engine/Base scope** (auth + drafts + research slices + stories + courses) rather than isolated per-domain database engines.
- Current DB baseline remains **SQLite as an acceptable baseline storage layer**, but this must be treated as baseline-capable only (not a production-grade multi-node/high-concurrency storage contour).
- SQLite operational guardrails (current baseline):
  - concurrency expectation: single-instance / low-to-moderate concurrent write pressure; do not interpret current mode as horizontally scaled write-ready storage;
  - locking/recovery caveat: lock contention and restart-time migration/bootstrap sensitivity must be treated as operational risk signals, not as edge-case impossibilities;
  - trigger conditions for next storage-hardening stage include recurring lock-related runtime failures, sustained write-latency under normal workload, and repeated operational need for multi-instance write concurrency.
- Migration/bootstrap behavior is **runtime-startup driven**: `init_db()` paths run during API startup and apply versioned migrations against the active DB.
- Startup owner gate (current baseline hardening): migration apply path is owner-only via `MIGRATION_STARTUP_ROLE`; `owner` runs startup `init_db()`/apply sequence, `non-owner` skips apply path.
- Outside development/testing/local aliases, `MIGRATION_STARTUP_ROLE` must be explicitly configured (`owner` or `non-owner`) as a fail-fast startup policy.
- Versioned migrations use a shared `schema_version` discipline and should be treated as a current baseline mechanism, not as a fully hardened production migration platform.
- Runtime startup for API is currently **fail-fast** on DB/bootstrap/migration initialization errors (`init_db()` startup path), and should be treated as baseline behavior, not as a fully hardened startup-orchestration platform.
- Session backend policy (current baseline hardening):
  - `AUTH_SESSION_BACKEND=memory` is allowed only for development/testing/local environments (including short aliases `dev`/`test`);
  - non-development/testing/local deployments must use Redis-backed refresh session storage (`AUTH_SESSION_BACKEND=redis` + `REDIS_URL`) and fail fast on misconfiguration.
  - Redis-backed refresh-session consume follows an atomic one-time path (`GETDEL`, then atomic fallbacks via `EVAL` or `WATCH/MULTI/EXEC`); legacy non-atomic `get+delete` is not baseline behavior.
- Rate limiting baseline remains process-local in-memory; it is not a distributed/global limiter in current scope.
- `X-Forwarded-For` is trusted for rate-limit client IP extraction only when request peer belongs to configured trusted proxies (`ARTEMIS_TRUSTED_PROXIES` or `TRUSTED_PROXY_IPS`); otherwise peer IP is used.
- Current `/api/health` semantics are baseline-level and process-local: `total_errors` remains an accumulated historical diagnostic counter, while `health.ok` reflects whether there were recent server-side errors within a fixed baseline decay window; this should not be interpreted as a fully hardened readiness/SLO contract.
  - Baseline default decay window is `120s`; it can be locally tuned via `HEALTH_ERROR_DECAY_SECONDS` env (invalid/empty values safely fall back to `120`) as a narrow hardening control, not as an observability-platform redesign.
  - Operator policy (runbook-light, current baseline):
    - `ok=true` means no recent process-local 5xx in the active decay window; it does **not** mean zero historical errors and does **not** by itself prove cluster/global readiness.
    - `ok=false` means a recent server-side failure was observed in this process; short-lived `ok=false` within decay window is a warning signal and is not automatically equal to sustained outage.
    - `counts.total_errors` is a historical diagnostic counter for this process lifetime and must be interpreted together with `ok`, `uptime`, and recent logs/events, not as a standalone outage state.
- Backend runtime currently guarantees request correlation and structured failure envelope at baseline level (`X-Request-ID` + `request_id` in error payloads), but this should not be described as a completed observability platform.

---

## Current Baseline API Surface (summary)

This section is a **summary of the current runtime surface**, not the sole owner of API/runtime rules.
For detailed boundaries and interpretation, read together with:
- `docs/PROJECT_STRUCTURE.md`
- `docs/DATA_CONTRACT.md`
- `docs/CONTROLLED_RELEASE_DECISION.md`
- `docs/ARTEMIS_MASTER_PROMPT.md`

- Auth (`/api/auth/*`):
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `POST /api/auth/logout`
- User/session:
  - `GET /api/me`
  - `GET /api/health`
- Drafts:
  - `GET /api/drafts`
  - `GET /api/drafts/my`
  - `POST /api/drafts`
  - `PUT /api/drafts/{draft_id}`
  - `DELETE /api/drafts/{draft_id}`
- Uploads:
  - `POST /api/uploads`
    - runtime upload endpoint; use backend-returned file URL in the response as source of truth
    - request (multipart/form-data):
      - required: `file`, `license`
    - response:
      - `id` (string)
      - `url` (string)
      - `filename` (string)
      - `license` (string)
  - `POST /api/uploads/image`
    - draft-image upload endpoint bound to an existing draft
    - request (multipart/form-data):
      - required: `draft_id`, `file`
    - response:
      - `url` (string)
  - public uploaded-file serving remains static via `/uploads/*`, not via a separate documented API read route
- Moderation (`/api/moderation/*`):
  - review/approve/reject runtime routes for moderation workflow
  - current baseline approval semantics are two-step: `pending -> review -> approved/publish-attempt`
  - first `approve` advances draft from `pending` to `review` only; publish-attempt path is allowed only after review stage
- Research slices (`/api/research-slices/*`):
  - current API mutates one ResearchSlice row and increments `content_version`; it does not create immutable Slice Revisions
  - `POST /api/research-slices` (save slice)
  - `GET /api/research-slices` (list my slices)
  - `GET /api/research-slices/{slice_id}` (open/restore)
  - `PATCH /api/research-slices/{slice_id}`
  - `DELETE /api/research-slices/{slice_id}`
  - `POST /api/research-slices/{slice_id}/share` (create/rotate unlisted read-only capability)
  - `DELETE /api/research-slices/{slice_id}/share` (revoke active capability)
  - `GET /api/public/research-slices/shared` with `X-ARTEMIS-Share-Token` (clean-session read-only restore)
  - owner CRUD remains private-only/owner-only; sharing is unlisted, revocable, no-store and does not publish into canonical data
  - current share reads the mutable row and is therefore live/mutable, not revision-pinned reproducibility
- Stories (`/api/stories/*`):
  - `POST /api/stories`
  - `GET /api/stories`
  - `GET /api/stories/{story_id}`
  - `PATCH /api/stories/{story_id}`
  - `DELETE /api/stories/{story_id}`
  - current baseline model: thin orchestration layer, private-only, owner-only
- Courses (`/api/courses/*`):
  - `POST /api/courses`
  - `GET /api/courses`
  - `GET /api/courses/{course_id}`
  - `DELETE /api/courses/{course_id}`
  - current baseline model: thin orchestration layer, private-only, owner-only
- Explain Context Contract (`/api/explain-context`):
  - `POST /api/explain-context` with `scope ∈ {slice, story, course}`
  - returns normalized context payload for explainability/runtime handoff
  - current baseline is context contract only; AI generation/explanation runtime is not implemented
- Auxiliary runtime feed:
  - `GET /api/map/feed` (auxiliary, non-canonical runtime support/read-model endpoint for UI; canonical public map source remains `data/features.geojson`)
- Canonical public map data path:
  - `/data/*` (exported ETL datasets; `data/features.geojson` is the production-default canonical public source)

---

## Development

### Requirements
- Python 3.11+
- FastAPI backend
- Dependencies are pinned in `requirements.txt` for reproducible local/CI/prod environments.

Install dependencies:
```bash
pip install -r requirements.txt
```

### Run backend
```bash
uvicorn app.main:app --reload --port 8001
```

### Run frontend
```bash
python -m http.server 8000
```

The frontend is fail-closed: without an explicit deployment configuration it
does not send auth or API requests to the static origin. For local development,
generate the non-secret configuration before starting the frontend:

```bash
python scripts/generate_pages_runtime_config.py \
  --api-base http://127.0.0.1:8001/api \
  --output deployment-config.js
```

GitHub Pages generates the same file from the repository/environment variable
`ARTEMIS_API_BASE`. Production values must be HTTPS URLs ending in `/api`.
Backend-dependent UI is enabled only after `/api/health` succeeds.

### Import / Export datasets (local ETL input/output)
Without direct Airtable writes, you can import prepared CSV/GeoJSON datasets into local `data/*`
using the same validation contract as ETL:

```bash
python scripts/import_features.py import --input ./dataset.csv --format csv --layers data/layers.json --out-dir data
python scripts/import_features.py import --input ./dataset.geojson --format geojson --layers data/layers.json --out-dir data
```

Import output:
- `data/features.json` (validated records)
- `data/features.geojson` (validated RFC 7946 FeatureCollection)
- `data/rejected.json` (invalid records + reasons)

Export validated dataset for external usage:

```bash
python scripts/import_features.py export --geojson-in data/features.geojson --out-dir data/export
```

Optional raw export (if `data/features.json` exists):

```bash
python scripts/import_features.py export --geojson-in data/features.geojson --raw-json-in data/features.json --include-raw --out-dir data/export
```

## Documentation System

README is the **root documentation entrypoint**, not the sole owner of detailed project rules.
Repository documentation is organized into five pragmatic layers:

- **canonical** — source of truth documents that define current project rules and structure.
- **work** — active working documents for current implementation tracks.
- **audits** — verification, audit, and validation outputs.
- **archive** — historical snapshots kept for traceability.
- **reference** — diagnostic and supporting materials that are useful for analysis but are not normative.

Documentation governance is defined in `docs/DOCUMENTATION_SYSTEM.md`. The authoritative canonical registry, owner routing and reading order live only in `docs/FOUNDATION_INDEX.md`; working-document lifecycle lives only in `docs/work/README.md`.

Project decisions follow five distinct levels:

1. `docs/ARTEMIS_CONCEPT.md` — North Star, identity and long-term attractor.
2. `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` — reviewed spatial-temporal World Model semantics.
3. `docs/PRODUCT_THESIS.md` and `docs/ARTEMIS_PRODUCT_SCOPE.md` — the user, problem and product being tested now.
4. `docs/PROJECT_TRUTH.md` — what actually works.
5. `docs/VALIDATION_DECISION.md` — what user evidence has proved and which one next branch is allowed.

Start with `AGENTS.md` for repository work, then follow the current reading order in `docs/FOUNDATION_INDEX.md`. Do not infer that every file under `docs/work/` is active; consult `docs/work/README.md`.

UI/UX working specs live in `docs/work/uiux/`. They preserve implemented and transitional design context, but their current lifecycle and authority are defined by `docs/work/README.md` and the canonical product contracts.

The current accepted main-screen shell is documented by:
- `docs/work/uiux/2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0.md`
- `docs/work/uiux/2026-07-17_CSS_OWNERSHIP_MIGRATION_AUDIT_v1.md` — measured CSS ownership baseline and rollout batches.

These files describe the implemented visual-shell baseline. They do not define the next product hierarchy: any new UI work must follow Foundation v3.1: synchronized space/time/layers are core, change objects are first-class, co-presence must remain separate from documented Relations, and the long-term attractor does not itself open future product scope. They also do not replace the owner-doc roles of `ARTEMIS_UI_UX_SYSTEM.md`, `ARTEMIS_UI_UX_COMPONENT_MAP.md`, `ARTEMIS_UI_UX_VISUAL_SYSTEM.md`, or `docs/work/ARTEMIS_UI_UX_IMPLEMENTATION_PLAN_v1_0.md`.

Historical documents live in `docs/archive/`, and diagnostic/reference documents live in `docs/reference/`; for example, `docs/reference/Artemis_UI_UX_Report.md` is diagnostic/reference material and **not** the primary UI/UX specification.
