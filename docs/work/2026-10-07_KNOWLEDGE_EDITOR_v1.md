# ARTEMIS — Knowledge Editor v1

## Status and authority

- Type: prospective bounded decision and implementation specification.
- Date: 2026-10-07.
- Decision: `BOUNDED_KNOWLEDGE_EDITOR_V1`.
- Lifecycle: prospective decision independently accepted and recorded in the canonical owners; REVIEW implementation is authorized within this specification.
- Classification: `DECISION`, then `REVIEW` implementation on its exact final head.
- Explicit owner instruction: the owner approved the proposed first complete user-entry scenario on 2026-10-07: one new architecture object, one Source and one atomic Claim; save draft, review, publish, propose a correction retaining accepted history. Earlier standing authorization covers AI development and self-merges under the Development Operating System, not automatic editorial acceptance of knowledge.
- Canonical owners: `ARTEMIS_PRODUCT_SCOPE.md`, `DATA_CONTRACT.md`, `PLATFORM_ARCHITECTURE_DECISION.md`; semantic dependencies are `EPISTEMIC_CONTRACT.md`, `CONTENT_GOVERNANCE.md` and `PROGRESSIVE_REFINEMENT_CONTRACT.md`.
- Baseline: remote `main` `e58adbd8a18e716783430b74dfc5988b757d05ec`, tree `a5c9badc662883b23e2f97358fa4541c28a4cb64`.

## 1. Question, alternatives and decision

How can the owner contribute a small source-aware knowledge record through an interface, rather than editing repository fixtures, without overwriting accepted knowledge or silently entering the public Globe corpus?

| Alternative | Assessment |
|---|---|
| Extend the legacy Atlas draft → Airtable publish path | Reject for this pilot: its required map/date fields and whole-feature workflow would conflate compatibility export with the epistemic core. |
| Start PostgreSQL/PostGIS, file storage and production hosting immediately | Defer: useful target direction, but neither spatial querying nor source-file ingestion is necessary for this first URLs/bibliography-only loop. Hosting and operational credentials are not currently configured. |
| New bounded editor contour in the preserved FastAPI/SQLite backend | Prefer: reuse accounts, sessions and server delivery; keep accepted records immutable and expose a separate read-only publication. This proves the complete contribution loop without migration. |

The decision opens only that third contour. SQLite is the initial single-process implementation, not a decision that the complete future corpus must remain in SQLite. Relational/spatial storage, S3-compatible files and tested production backups remain the preferred growth direction; no PostgreSQL/PostGIS migration, object-storage provisioning or public backend deployment is authorized or claimed by this pilot.

## 2. First complete user scenario

1. An authenticated author creates one architecture-object proposal and records a name. Incomplete information can be saved as a private draft.
2. The author adds one Source and one atomic Claim with its precise locator, source-native expression and uncertainty. No date, coordinate or image is mandatory.
3. Submission freezes the proposed content and its digest for review. Submitted content cannot be edited in place; a return/request for changes creates an editable state with a new version and requires resubmission.
4. An authorized moderator examines the source and exact submitted content; records editorial accept, request changes or reject with a reason. Acceptance creates one immutable accepted editorial revision and its review receipt. The server records `owner_self_review` when moderator and author are the same account, otherwise `separate_principal_review`; neither mode silently changes epistemic status.
5. A separately explicit authorized publication action creates a persistent immutable read-only snapshot/card. Acceptance alone does not publish.
6. The author starts a correction from the accepted revision, gives a reason and edits the candidate Claim/evidence. The old accepted revision and publication remain accessible while correction review is pending. A new accepted correction retains the predecessor and becomes the latest accepted editorial revision. Publication of that correction is another explicit action; old publication remains addressable.

“Accepted” in this document means editorial workflow acceptance, not accepted canonical World Model knowledge or historical validation. Publication is a clearly marked pilot read-only editorial record, not entry into the public knowledge/map corpus. The stopping artifact is that one complete loop through correction and retained history. No second domain, ingestion framework, automatic successor or full-corpus editor follows from passing it.

## 3. Data boundary and minimal shape

The editor creates new namespaced stable UUID identities. It does not mutate, merge with or claim identity equivalence to existing frozen World Slices, Atlas objects or Sources. A minimal search/list of editor objects prevents obvious repeated entry; cross-corpus duplicate resolution and merges are deferred.

| Record | Required at submission/review | Preserved limitations |
|---|---|---|
| Object proposal | Stable ID, architecture type, name | Description is editorial metadata, not an independently accepted historical Claim. Historical life time and position remain unknown; no default point or present-day lifetime. |
| Source | Stable ID, title, source type, author/organization when known; safe URL or bibliographic reference | Missing author/publication metadata remains null/unknown. AI output is not a Source. Access date is record provenance, not world time. |
| Claim | Stable target-series identity, statement, subject reference, canonical claim kind, origin, confidence and uncertainty | One atomic assertion per proposal. Default confidence unknown; a non-unknown confidence requires its basis. Reviewer judges atomicity and evidential adequacy; structural validation does not prove either. |
| EvidenceLink | Stable ID, Claim/Source refs, exact locator, `supports`, `challenges` or `contextualizes`; `direct`, `indirect` or `background` strength | Locator and source-native expression are preserved literally. A URL alone is not a Claim-level locator. Review provenance identifies the exact accepted content. |
| Accepted editorial revision | Stable revision ID, series/subject/target refs, `initial` or `correct`, predecessor refs, recorded time, source value, Claim/evidence refs, uncertainty and reason | `normalized_value=null`; native precision is explicitly unresolved. No automatic timeline normalization. Other refinement operations are not implemented in v1. |
| Publication | Stable snapshot ID, exact accepted revision ID, digest, publish actor/time and public schema version | Immutable public payload; draft text, account email and private review comments are excluded. Public source locators, epistemic dimensions and history references remain inspectable. |

Only an initial statement and later correction of that same atomic target are implemented. The target key is a stable proposal assertion identity, not a generated date/coordinate/type inference. Corrections retain Entity and series identity while receiving new revision, Claim and EvidenceLink identities. The accepted Source packet is immutable per revision, whether the same bibliographic Source identity is reused or a new source is supplied; stable IDs must not be reused for changed immutable payloads.

The Source packet retains the submitted bibliographic metadata, source-native excerpt/expression and exact locator as immutable content. Review attests correspondence with the actual source in the stated scope; it does not certify that an external website will remain unchanged or that a whole book was reviewed. Record the canonical SHA-256 of the complete source value (raw expression plus unresolved precision), `normalized_value=null`, the packet and the submitted payload. The accepted editorial packet binds those values for provenance and future review. It is not claimed to be a frozen World Model package or a complete executable Progressive Refinement ledger. No full copyrighted work is copied by default. Source rights/license remain explicit and may be unknown; a bibliographic/link license does not grant excerpt republication rights. The source-native packet is private in v1 and its copied excerpt is omitted from public HTML/JSON, regardless of bibliography availability. The public card exposes user-authored statement, citation/locator, uncertainty and packet digest, not the private source quotation. Do not infer document/media rights from a URL or access permission. An absent locator/native expression prevents submission; unreproduced or unsuitable evidence can receive a request for evidence or rejection. No fabricated quotation/locator or supported historical acceptance is permitted.

Workflow and epistemic dimensions stay independent. Draft/submitted/request-changes/accepted/rejected workflow states are not Claim kinds or confidence. Claim, Source and EvidenceLink `review_state` remain draft throughout this pilot; Claim `evidence_state` remains missing, because candidate links have not passed separately authorized epistemic promotion. Confidence remains the author's explicit assessment with its basis, default unknown. Editorial approval does not set epistemic reviewed/supported states, whether moderator is the author or a different account. Acceptance does not automatically set confidence high, eliminate uncertainty or validate a whole object's dates/geometry. A materially competing historical attribution requires later bounded alternative-handling authorization, not misuse of `correct` to erase disagreement.

## 4. Roles, privacy and concurrency

- Reuse existing authenticated user IDs and session/token validation. Normal registration cannot grant reviewer/admin privileges; reviewer provisioning is an explicit server-operator action.
- Authors can read and update only their drafts. Reviewers/admins can inspect the submitted queue and act only through authorized review/publication endpoints.
- The initially sole owner may review their own human-authored proposal only when explicitly provisioned as a moderator/admin and the proposal has `origin=user`; AI-origin proposals cannot be approved through this mode. V1 accepts human-authored proposals only and rejects AI-origin promotion; an author attestation is recorded without pretending the system can detect undisclosed AI authorship. The server derives `owner_self_review` from actor ID equality and stores/displays it on the review receipt and public snapshot. This is transparent owner editorial approval, not independent validation. A different authorized account is recorded as `separate_principal_review`; account separation alone is not proof of distinct humans or editorial competence. Ordinary authors cannot review any submission. No user-selected reviewer label can override this provenance.
- The pilot has no automatic AI content generation, AI source extraction or AI editorial acceptance. AI development/browser fixtures are technical evidence, not acceptance of historical facts. Existing AI-origin content-review rules remain in force.
- A reviewer may also publish after acceptance, but publication remains a separate explicit action. Public readers see only published snapshots; private drafts and unreviewed correction candidates never leak through public list/history endpoints.
- Each mutation carries an expected version and, for correction acceptance, expected accepted predecessor. Review acts on the exact expected submitted version and canonical content digest. Publication names the exact accepted revision/digest and compare-and-swaps the expected current publication pointer/version; a delayed old publication cannot silently replace a newer correction. Stale writes/reviews/acceptance/publication return a conflict. Transactional acceptance guarantees one latest accepted editorial revision; repeated requests cannot create duplicate accepted/public records.
- Owner/admin actor IDs are stored privately as provenance. Public receipts use non-sensitive technical identifiers/role labels; account email, session tokens and private reviewer notes are not exposed.

## 5. Persistence and delivery

Add editor-specific tables/models under the existing backend persistence boundary; do not repurpose legacy `Draft.payload`, `publish_status`, Airtable IDs or `/api/map/feed`. Additive initialization/migration must preserve existing rows and old API behavior. Filesystem persistence must be configurable and survive service restart. SQLite test files are isolated from working data.

Serve the editor from that same backend, for example `/editor/`, using same-origin `/api/knowledge-editor/...` endpoints and existing authentication. A private draft is durably saved only after server acknowledgement. Unsaved browser text is not described as a backup or committed draft. Disconnected/expired-session/write-failure states preserve visible input and provide a retry; secrets and private text do not enter URLs/logs.

The public read-only card/snapshot lives on the running backend. A stable record URL resolves the latest explicitly published snapshot; immutable snapshot URLs and history resolve earlier published versions. Unpublished accepted revisions need not be public. JSON and native read-only HTML are sufficient; no runtime adapter into the shared Globe or automatic GitHub Pages export is included.

GitHub Pages cannot run this backend. A published static editor shell, if provided, must explain that a configured backend is required and never fabricate a successful durable save. Backend-available, locally verified and publicly hosted are different capabilities. Production hosting, domain, credentials, privacy policy and operational backup setup remain a later deployment step with concrete external access, not an inferred completed effect.

For this pilot, provide a bounded database backup/restore procedure and prove accepted/public revision readback after restart and restore on an isolated copy. Do not claim automated off-device backups or production disaster recovery. Store no large source files in Git or SQLite. Source uploads, object-storage credentials, binary rights handling and S3 URLs are deferred.

## 6. Product acceptance

Use the incumbent ARTEMIS visual language. Russian-first compact sections are Object, Source and Claim, with optional detail disclosure. The author sees what is required to submit without completing every possible knowledge field. Display draft/save/submission/review/publication states explicitly. Review has source access, exact submitted content/digest, reason entry and separate decision actions. The public card labels the record an editorially approved candidate, displays review mode and all draft/missing/unknown dimensions, exposes the proposed source link and locator, and preserves correction history. It must not label approval as historical validation.

Keyboard controls, labels, visible errors, desktop/narrow layouts and Escape/focus behavior where dialogs exist are required. Test the real native form and read-only card; API-only success is insufficient. No maps, density redesign, educational narration or elaborate reviewer console is needed.

## 7. Verification, independent review and closeout

Acceptance evidence must bind the exact implementation commit/tree and relevant checks:

1. Real authenticated API loop: incomplete draft save/readback, submit, owner self-review and distinct-account moderator review, explicit publish, anonymous published readback, correction review and republish with old snapshot retained.
2. Negative tests: unauthenticated/non-owner reads and writes, non-admin review/publish, forged review mode/actor and self-review presented as independent, stale draft/content digest/predecessor, changed submitted payload, duplicate acceptance/publication, publish without acceptance, private candidate leakage, incomplete locator/native expression, forged system IDs/review states and unsafe URLs.
3. Persistence: restart and isolated backup/restore preserve accepted revision bytes/digests, source/evidence closure, histories and public snapshots. DB failure must not claim save success.
4. Actual browser evidence: author form and correction, reviewer actions, published card/history, narrow layout and keyboard flow; record no backend/publication claims beyond the exercised environment.
5. Compatibility: existing auth/session and Atlas draft/moderation paths remain intact; frozen inputs, `data/*`, Airtable write paths and unified Globe assets are byte-unchanged. Run the relevant existing regression and governance checks; do not broaden to unrelated suites without cause.
6. Distinct Architecture and Product AI reviewers inspect the exact final head and actual test/browser evidence. Zero unresolved material findings before merge under the current Development Operating System. This is technical conformity, not historical source correctness or comparative user-value validation.

Closeout updates truth/registry with exact scope, checked source, review and persistence/browser receipts. If hosting is unavailable, stop at honestly verified backend-available delivery and a reproducible run procedure; do not claim that the owner can already save on the public GitHub Pages URL. Gate E stays closed, E2 waived/not collected, formal/comparative value UNVALIDATED, contextual composition DEFERRED and ATL conflict non-public. No automatic successor opens.

## 8. Prospective decision review

Independent review must inspect this prospective specification together with its canonical owner appends and record a durable exact-revision verdict before semantic implementation. Decision authoring is complete when both Architecture and Product reviews have no unresolved material scope/semantic findings. This section must record actual verdicts and exact content bindings, not a future promise represented as acceptance.

## Prospective decision acceptance — before implementation

Architecture `/root/editor_scope_review`: `ACCEPT_SCOPE`; Product `/root/editor_product`: `ACCEPT_PRODUCT_DECISION`. Both independently inspected specification SHA-256 `0c7704cfc641d1e63441a15778cd9613658c16c6110f4a63825041346a1247d0` and its five matching owner/current-state files before semantic code. Both reported zero unresolved material findings. This receipt records only the bounded decision; final exact-head code/native-interface/persistence review and availability verification remain required. The user chose direct implementation of the working form in the incumbent ARTEMIS style on 2026-10-07.
