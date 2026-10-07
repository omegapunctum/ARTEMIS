# Knowledge Editor — portable public export v1

## 1. Owner direction and decision

On 2026-10-07 the owner confirmed the proposed next engineering task: a downloadable versioned JSON package of one published editorial object and its entire published history. Paid Render deployment is deferred; the existing local backend is sufficient. This opens `BOUNDED_EDITOR_PUBLIC_EXPORT_V1`, with prospective independent Architecture/Product scope review before `REVIEW` implementation. Earlier no-successor wording is superseded only for this task.

Question: how can a reader carry one published editorial record and its history without the private working database? Alternatives are the existing full SQLite backup, individually fetched public snapshots, and one explicit public JSON package. Choose the package for selective sharing; keep SQLite backup/restore for private recovery. No import, private transfer, source uploads, new knowledge, external deployment, automatic publishing or Globe intake is included. This is a new read-only projection contract, not a change to domain or historical semantics.

Canonical owners are `ARTEMIS_PRODUCT_SCOPE.md` for scope and `PLATFORM_ARCHITECTURE_DECISION.md` for delivery/privacy. `PROJECT_TRUTH.md` owns implementation/availability; `work/README.md` owns lifecycle. This document specifies only the bounded implementation and acceptance.

## 2. API and privacy

Add anonymous GET `/api/knowledge-editor/public/objects/{entity_id}/export`, returning one UTF-8 JSON attachment. Private, nonexistent and never-published objects return the same 404. Only existing immutable `EditorPublication.public_payload` values and their stored payload digests may supply snapshot content. Do not query/export private draft, accepted packet, event, reviewer reason, actor/account, token, secret or source-native expression content. Full private SQLite backup remains separate.

The root publication pointer and all included publication rows must be captured in one consistent database view, preferably one joined SELECT. A concurrent publication cannot create a package whose pointer is missing or whose manifest differs from its included snapshots. Fail closed on invalid stored public payload/digest or inconsistent object/series/revision references, without exposing diagnostic content. Download does not modify any data.

## 3. Portable format

Use `schema_version=knowledge-editor-public-export-v1`, `publication_scope=editorial_candidate_not_globe_corpus`, `entity_id`, `target_series_id`, `current_snapshot_id`, a manifest, full public snapshot responses and `package_digest`. Define and check the concrete v1 JSON Schema with unknown fields forbidden at each public object boundary. The snapshot schema is the existing `knowledge-editor-v1` public response, including `public_payload_digest`; preserve its exact field values, IDs, locators, predecessor references, source links, uncertainty, draft/missing states and review mode. Position, world time and normalized value remain null. Do not export the mutable object response's appended history inside each snapshot.

The exact top-level fields are `schema_version`, `publication_scope`, `entity_id`, `target_series_id`, `current_snapshot_id`, `manifest`, `snapshots` and `package_digest`. The manifest has exactly `snapshots` and `unresolved_predecessor_revision_ids`. Each manifest snapshot entry has `snapshot_id`, `revision_id` and `snapshot_digest`. It lists each included snapshot/revision ID and SHA-256 of its complete public snapshot response, in the same deterministic publication order as the snapshot array (literal public `published_at` then snapshot ID for ties). The gap list records sorted distinct predecessor revision IDs referenced by public snapshots but absent from this package. These are unresolved external references, not invented snapshots or evidence of a complete accepted/private chain. An accepted intermediate revision may never have been published; omit its private packet while retaining the literal predecessor reference. Only already-public references may appear in that gap list. Every published snapshot for this object must be included; an accepted but unpublished correction must not change an export.

Hash canonical JSON using UTF-8, `ensure_ascii=False`, sorted object keys, compact separators and `allow_nan=False`. The existing `public_payload_digest` covers the stored public payload without that digest field. Each manifest snapshot hash covers the complete exported public snapshot including that digest. `package_digest` covers the complete package except its own field. Include no download timestamp, local origin, actor or machine path, so unchanged publication state produces identical bytes across repeat download, restart and restore. Hashes establish internal byte integrity, not signer authenticity, source correctness, rights or historical acceptance.

Provide a bounded offline verification command for schema, package/snapshot hashes, uniqueness, entity/series consistency, current-pointer inclusion, manifest order and predecessor gap accounting. It reads a JSON file without networking or database writes, rejects malformed/unknown versions and reports generic success/failure without printing record contents. It does not import or promote data. Its documented invocation must work from a checkout and use the same format contract as the server.

Use a server-derived ASCII attachment filename based on the system object UUID, never a user-entered title. Send no-store/nosniff headers; use the existing public route rate limit. Schema/serialization/database failures must not produce a partial successful download.

## 4. Interface

Add one native, keyboard-accessible download action to the existing anonymous public card. Label it `Скачать опубликованную историю (JSON)` and explain that it includes all published versions of this object and omits private data. The same action on an older immutable snapshot still downloads the object's current published history, not just the displayed version; make that scope explicit. No new panel, theme, visualization or private-editor redesign is needed. Backend-produced bytes are authoritative; do not reconstruct packets in the browser. Failure must not claim a successful download or erase the displayed card. Preserve incumbent desktop/narrow behavior and source/history access.

## 5. Acceptance and stop

1. Exercise initial publication plus correction: anonymous attachment contains both exact public snapshot responses, correct current pointer and verifiable hashes. Repeat download is byte-identical and leaves rows/pointers unchanged.
2. Prove negative privacy with private source markers, account identifiers, reviewer notes, private drafts and accepted-but-unpublished corrections absent. An unpublished predecessor gap stays explicit; no private chain completion occurs.
3. Check nonexistent/private IDs, unsafe filenames, corrupted stored digest/schema/reference, manifest tampering, duplicate/missing snapshot, unsupported version and pointer mismatch fail closed. Offline validation must not contact URLs or mutate anything.
4. Verify consistent read behavior across concurrent publication; unchanged exports remain byte-identical after actual process restart and isolated SQLite restore.
5. Real native browser: download via the public card at desktop/narrow widths, actual downloaded JSON verified offline, old-snapshot download scope, keyboard and failure behavior. Synthetic accounts/records only; technical evidence is not historical/user-value validation.
6. Run owned editor/governance regressions, exact-head CI and distinct Architecture/Product implementation review. Frozen/data/Globe/Airtable inputs remain unchanged. No paid resources are created.

Stop after the package, UI and offline verifier pass those checks and merge under standing policy. Record exact source/review/CI evidence and backend-available delivery; do not claim a publicly hosted editor. Import, source-file intake and user-object/Globe mapping remain separate future tasks. Gate E/value/contextual/ATL dispositions remain unchanged.

## 6. Prospective review receipt

Before implementation, Architecture `/root/export_architecture_review` returned `ACCEPT_SCOPE` and Product `/root/export_product_review` returned `ACCEPT_PRODUCT_SCOPE` on pre-receipt specification SHA-256 `55b5aa0b1ca72e138a4d2cbe1052734ee87f56ec64a2c3e615e138ec375de2cb` and its matching canonical/current-state/registry appends. Both reported zero unresolved material findings. These are distinct AI scope reviews, not historical/user-value or implementation acceptance. The specification, owners and this receipt must be committed before runtime edits; final exact-head code/native/persistence acceptance remains required.
