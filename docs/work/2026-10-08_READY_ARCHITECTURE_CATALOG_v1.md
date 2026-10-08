# Ready architecture catalog v1 — prospective decision and specification

## Decision

Autonomy: DECISION before runtime/source edits, then REVIEW implementation.
Owner instruction, 2026-10-08: after clarifying that ordinary visitors must receive
ready objects/layers without entering Wikipedia links or using the editor, the
owner instructed implementation to begin. The instruction opens this bounded new
source-intake/public reference layer, not universal coverage or historical acceptance.

Question: can a visitor search and inspect an automatically populated, source-bound
catalog in the existing shared Explorer without authoring records first?
Alternatives: extend the mandatory editor form; scrape encyclopedic prose; or use
a small structured, revision-pinned Wikidata cohort with deterministic extraction.
Preferred: the third option. Wikimedia supplies actual source data; AI agents write
and technically review the adapter, never become its historical source.

Prospective independent Architecture and Product scope reviews must be recorded
below before code or checked-in source capture changes. Canonical Product Scope
and Platform Architecture appends own this exception. Previous no-intake/no-successor
dispositions remain historical and are superseded only within this contour.

## Bounded cohort and source contract

Ten existing London architectural buildings/monuments or complexes, explicitly
enumerated by QID: Q83125, Q62378, Q5933, Q62408, Q173882, Q42182, Q642039,
Q205666, Q207385, Q607700. The source audit must verify their actual identities,
current reference suitability and coordinate eligibility before intake. This is a
selected pilot, not comprehensive London coverage; site/complex extent is unknown.
Existing 31 Atlas identities/names/URLs must be checked for candidate duplicates.
Any failed or ambiguous candidate is withheld and reported; replacement needs
prospective scope-review acknowledgement rather than a silent larger harvest.

Use Wikimedia's structured API/EntityData with identifying User-Agent, bounded
requests/timeouts, rate-limit backoff and no credentials. Capture immutable native
JSON by entity/revision into a new operator-selected directory. Preserve retrieval
time, exact downloaded byte SHA-256, revision identity/pinned URL, native labels,
aliases, descriptions, sitelinks and all statements with qualifiers/references/ranks.
No article text or images are copied. Wikidata structured content is CC0-1.0;
Wikipedia sitelinks are contextual navigation, not independent corroboration.

Build/release runs use checked-in bounded snapshots, not live external requests.
Import script offers explicit capture and offline normalization separately. Rebuild
from the same inputs is byte-identical, stable QID-derived IDs do not duplicate rows,
and changed revisions are captured separately with an explicit comparison, preserving
old bytes. Changed inputs never silently update the published bundle.

P625 eligibility: exactly one non-deprecated value statement, unqualified, with
Earth globe and finite in-range longitude/latitude. Preserve all native statements;
ambiguous, qualified, missing, non-Earth or malformed coordinates fail closed.
Provider precision stays literal, not a measurement-accuracy guarantee. Non-null
precision must be finite and positive; negative provider precision is withheld,
never repaired. The source audit excluded Q193639 (Royal Albert Hall) for negative
P625 precision and prospectively selected Q642039 (Banqueting House) instead.
QID and revision identities, manifest hashes, label language tags and duplicates
must validate before normalization. Dates remain native source metadata; no date
guess, temporal interval, lifespan or historical position is generated.

## Shared model/projection boundary

Add a separate small reference input envelope/adapter beside unchanged legacy
architecture input. This is a source-bound, atemporal reference extension of the
accepted workspace envelope, not a second World Model or migration of frozen schemas.
Each row has `item_id=catalog:wikidata:QID`, `layer_id=catalog`,
`kind=catalog_reference`, label/aliases/external IDs, original P625 payload,
source/revision pointers and present-day reference geometry. Its interval,
historical_position and historical applicability remain null/unknown.

Provide a source-relative coordinate Claim ('this Wikidata revision reports this
coordinate'), Source and EvidenceLink with native statement locator. Claim kind is
factual, origin imported, review_state draft, confidence unknown, evidence_state
missing; Source/EvidenceLink review states are draft. Technical adapter acceptance
is not factual evidence review. Uncertainty distinguishes source numeric precision,
measurement accuracy, site extent and unknown historical applicability.

Compose via the existing unified builder, registry, ledger and one MapLibre instance.
Keep the original 31 Atlas records, 11 Leonardo Presence identities/unknown routes,
three Roman reconstructions and 91–1519 calendar coverage unchanged. Exclude catalog
references from historical time filtering and simultaneity claims.

## Visitor behavior

Fourth layer `catalog` is on in a fresh /globe/ or /region/ entry; explicit saved
`layers` URLs remain authoritative. Label pilot count and London coverage. No login,
link entry, editor, live Wikidata request or API key is required by the visitor.

Add search to the existing visible-record chooser. Match Unicode-normalized RU/EN
and original names, aliases and QID, without replacing multilingual originals or
inventing translations. Search filters only chooser results, never map records,
canonical time, camera or current inspector. Empty search results and clear action
are explicit; selection and native source disclosure remain keyboard accessible.

Cards show name (fallback language tagged), source-relative modern point meaning,
the Wikidata revision link, Wikipedia context link where present, and concise limits.
Native disclosures retain original coordinate/precision/alternatives, Claim/Evidence,
source version, CC0 and input provenance. Do not require users to interpret raw JSON
to understand what the imported point means. No confidence score or 'verified' badge.

Suggested RU copy: 'Пилотный каталог · 10 объектов · Лондон'; 'Импортировано из
Wikidata; независимая проверка не выполнена.'; 'Современная опорная точка.
Историческое положение и период существования не установлены.' EN equivalents
must communicate the same limits. Language/layer/Globe↔2D/history preserve one map.
Explicit focus is the only new catalog action that moves the camera.

## Acceptance and stop

- Live captured source audit resolves the exact ten identities/coordinates, hashes,
  revisions, precision/qualifiers/references and legacy duplicate candidates.
- Offline tests verify deterministic reimport/no duplicate QIDs, immutable capture
  collisions, changed-revision comparison, integrity rejection and invalid/ambiguous
  coordinate withholding; no network call during build/test/visitor runtime.
- Existing unified workspace regression tests preserve legacy/source/time/selection
  and single-map behavior; data ledger and static release manifest include new inputs.
- Actual native desktop and 390px narrow browser evidence covers fresh ready catalog,
  search→select→source→explicit focus, multilingual fallback, empty search/clear,
  URL/history/layer/Globe↔2D continuity, unchanged map identity and no overflow.
- Distinct Architecture/Product agents accept the exact current source with zero
  material findings. Required/relevant current-head CI passes before authorized merge.
- Public availability requires separately checked Pages deployment and live bytes;
  local/merged implementation alone never becomes a live-publication claim.

Stop after this cohort's complete bounded delivery. No automatic next import,
scheduled job, corpus expansion, object relations, editor rewrite, AI moderation,
paid Render, backend/SQLite migration, frozen fixture change, Gate E reopening,
contextual composition or user-value validation. Repository stores this small
reproducible source package, not the future operational universal corpus.

## Prospective review receipts

Pre-receipt specification SHA-256:
`3a3a6bd188448dbb627620b89c2621750988cb829dba8a1387ecb8b3d6159048`.
Both distinct agents inspected this complete specification plus Product Scope §16,
Platform Architecture bounded intake append and work registry on base `fb051c2`,
before runtime/source changes; both reported zero material findings:

- `/root/catalog_architecture`: **ACCEPT_SCOPE**.
- `/root/catalog_product`: **ACCEPT_PRODUCT_SCOPE**.

This receipt records prospective technical scope acceptance only. Implementation
is now authorized under REVIEW; it is not source-truth or user-value acceptance.
