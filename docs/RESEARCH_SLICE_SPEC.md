# RESEARCH SLICE SPEC

## 1. Concept definition

`ResearchSlice v2` — current mutable runtime persistence envelope для одного сохранённого исследовательского состояния и его вложенного Saved View.

Target product semantics принадлежат `RESEARCH_SLICE_CONTRACT.md`. Там зафиксирована модель `Investigation → immutable Slice Revision → Research Brief`. Эта спецификация описывает уже реализованный executable schema v2 и не переименовывает current mutable row в immutable revision.

Текущий capability status:

- schema/database/API/client sync: implemented and covered by executable release checks;
- owner create/edit/reopen/delete and unlisted share/rotate/revoke: backend-available;
- public deployment E2E: not yet proved;
- Investigation identity, immutable revisions, claim-level EvidenceLinks with locators, pinned dataset identity and Brief export: not implemented;
- product validation: this compatibility runtime has no current product-validation authorization; ARTEMIS user-value status is owned by `VALIDATION_DECISION.md` and active scope by `ARTEMIS_PRODUCT_SCOPE.md`. Historical `PRODUCT_VALIDATION_PLAN.md` is not an active Foundation v3 owner.

## 2. JSON model v2

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "research_question": "string",
  "selection_rationale": "string",
  "feature_refs": [
    { "feature_id": "string" }
  ],
  "evidence_state": "supported",
  "evidence_refs": [
    {
      "kind": "source",
      "ref_id": "string",
      "supports_finding_ids": ["finding-id"]
    },
    {
      "kind": "relation",
      "ref_id": "string",
      "supports_finding_ids": ["finding-id"]
    }
  ],
  "findings": [
    {
      "id": "finding-id",
      "type": "interpretation",
      "text": "string",
      "feature_id": "string"
    }
  ],
  "conclusion_status": "concluded",
  "conclusion": "string",
  "uncertainty_notes": "string",
  "saved_view": {
    "time_range": {
      "start": 0,
      "end": 0,
      "mode": "range"
    },
    "view_state": {
      "center": [0.0, 0.0],
      "zoom": 0.0,
      "enabled_layer_ids": ["string"],
      "active_quick_layer_ids": ["string"],
      "selected_feature_id": "string"
    },
    "filter_state": {
      "search": "string",
      "confidence": "reviewed"
    },
    "comparison_feature_ids": ["string"]
  },
  "schema_version": "2.0",
  "content_version": 1,
  "content_status": "complete",
  "visibility": "private",
  "owner_id": "string",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

`evidence_state = missing` обязан сопровождаться пустым `evidence_refs`. `conclusion_status = unresolved` явно фиксирует отсутствие завершённого вывода и не требует искусственного текста.

## 2.1 Normative constraints

- `feature_refs` required, non-empty and unique;
- `research_question` required after compatibility normalization;
- `selection_rationale` required after compatibility normalization;
- `saved_view.time_range.start <= saved_view.time_range.end`;
- `saved_view.view_state.selected_feature_id`, `comparison_feature_ids` и `finding.feature_id` обязаны ссылаться на `feature_refs[*].feature_id`;
- `finding.type ∈ [fact, interpretation, hypothesis]`;
- finding ids unique;
- `evidence.kind ∈ [source, relation]`;
- evidence `ref_id` non-empty;
- `supports_finding_ids` ссылаются только на существующие findings;
- `evidence_state = supported` требует минимум один evidence ref;
- `evidence_state = missing` запрещает evidence refs;
- `conclusion_status = concluded` требует непустой `conclusion`;
- `content_version` начинается с 1 и увеличивается при каждом успешном PATCH; это optimistic content counter, а не immutable revision id;
- owner CRUD всегда сохраняет `visibility = private`;
- share создаёт unlisted read-only capability и не превращает Slice в searchable/public-curated запись.

## 2.2 Saved View boundary

Saved View является вложенным компонентом current ResearchSlice и future Slice Revision, а не самостоятельным исследовательским результатом.

Он хранит:

- time range and mode;
- viewport and zoom;
- enabled and quick layers;
- selected Feature;
- serializable filter state;
- comparison Feature ids.

Question, rationale, evidence, findings, conclusion и uncertainty находятся вне Saved View и не могут быть заменены viewport snapshot.

## 2.3 Compatibility mirrors

Для одного rolling-deployment cycle DETAIL/PUBLIC DETAIL сохраняют legacy mirrors:

- `time_range` = `saved_view.time_range`;
- `view_state` = `saved_view.view_state`;
- `annotations` = `findings`.

Legacy create/update payloads принимаются и нормализуются в v2. Новые клиенты обязаны отправлять canonical v2 fields.

Compatibility не разрешает скрывать неполноту:

- отсутствие evidence становится `evidence_state = missing`;
- отсутствие завершённого вывода становится `conclusion_status = unresolved`;
- lightweight LIST возвращает `content_status`, `evidence_state`, `conclusion_status`, `finding_count` и `content_version`.

## 2.4 Migration 203

Migration `203/research_slices_product_complete_v2`:

- добавляет v2 columns;
- сохраняет `id`, `user_id`, timestamps, share-token hash и `shared_at`;
- переносит legacy `annotations_json` в `findings_json`;
- формирует Saved View из существующих time/view columns;
- не создаёт evidence и conclusion;
- ставит legacy rows в `missing/unresolved`;
- идемпотентна в versioned migration registry.

Название существующей migration отражает прежний scope. После Concept Lock v2 оно не является доказательством product-complete target research model и не переименовывается задним числом.

## 3. API endpoints

- `POST /api/research-slices` — создать Slice.
- `GET /api/research-slices` — получить lightweight owner list.
- `GET /api/research-slices/{slice_id}` — открыть полный owner Slice.
- `PATCH /api/research-slices/{slice_id}` — изменить current mutable row и увеличить `content_version`; immutable history не создаётся.
- `DELETE /api/research-slices/{slice_id}` — удалить Slice.
- `POST /api/research-slices/{slice_id}/share` — создать/ротировать read-only capability token.
- `DELETE /api/research-slices/{slice_id}/share` — отозвать token.
- `GET /api/public/research-slices/shared` + `X-ARTEMIS-Share-Token` — открыть unlisted read-only Slice без owner identity.

## 4. Ownership, privacy and sharing

- Owner CRUD требует аутентификацию и возвращает `404` для другого пользователя.
- В базе хранится только SHA-256 capability token.
- Raw token возвращается владельцу только при create/rotate.
- Public response не содержит `owner_id` и не допускает mutation.
- Public response отправляется с `Cache-Control: no-store`, `Pragma: no-cache`, `Referrer-Policy: no-referrer` и `X-Robots-Tag: noindex`.
- UI хранит token во fragment `#share=...`; backend получает его через header, а не request URL.
- Rotate, revoke или удаление Slice делают прежний token недействительным.
- Shared response отражает current mutable row. Author PATCH может изменить последующее содержимое по прежней share capability; поэтому current share является `live/mutable`, а не revision-pinned.

## 5. Client behavior

Клиент поддерживает:

- create complete Slice from current comparison/map context;
- explicit `source:<id>` / `relation:<id>` evidence refs;
- explicit evidence missing state;
- typed findings;
- concluded/unresolved state and uncertainty;
- owner edit through PATCH;
- full Saved View restore;
- save-as-copy from shared read-only Slice;
- unlisted share/rotate/revoke.

## 6. Executable evidence

Обязательное test coverage:

- v2 API round trip and PATCH version increment;
- malformed evidence and epistemic-state rejection;
- Saved View semantic restoration;
- deterministic legacy migration;
- owner isolation;
- public response privacy/no-store headers;
- share rotation and revoke;
- frontend payload construction and nested Saved View precedence.

Schema/code sync не равен public validation. Historical compatibility work item #309 defined deployment evidence for a create → edit → reopen → share backend/API loop, but that path is not the active #355 ARTEMIS Core product-validation route and cannot authorize current scope by itself.

Even if that compatibility E2E is later proved, current capability would confirm only the mutable Slice v2 loop. Target Investigation/revision/Brief model requires a separate docs/data/runtime migration and new E2E, and current ARTEMIS user-value status remains governed by `VALIDATION_DECISION.md`.

## 7. Out of scope

- public searchable Slice directory;
- collaborative editing;
- multi-token ACL/per-recipient permissions;
- immutable share snapshot;
- first-class Investigation;
- immutable revision history;
- Claim/EvidenceLink entities with source locator, evidence relation and strength;
- pinned dataset/export identity;
- deterministic citation-ready Research Brief;
- Stories, Courses or AI expansion;
- conversion of findings into canonical facts without governance.