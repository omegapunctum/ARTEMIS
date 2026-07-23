# RESEARCH SLICE SPEC

## 1. Concept definition
Research Slice — это canonical runtime-сущность пользовательского исследовательского состояния (выбор объектов, временной диапазон, состояние карты и заметки), сохраняемая для последующего восстановления контекста.

## 2. JSON model (final)
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "feature_refs": [
    { "feature_id": "string" }
  ],
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
  "annotations": [
    {
      "id": "string",
      "type": "fact",
      "text": "string",
      "feature_id": "string"
    }
  ],
  "visibility": "private",
  "user_id": "string",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

Нормативные ограничения:
- `feature_refs` не пустой;
- `time_range.start <= time_range.end`;
- `view_state.selected_feature_id` (если задан) обязан ссылаться на `feature_refs[*].feature_id`;
- `annotation.type ∈ ["fact", "interpretation", "hypothesis"]`;
- owner CRUD сохраняет `visibility = private`;
- явный share создаёт отдельную unlisted capability-ссылку и не меняет owner resource на публичную запись.

## 2.1 Field constraints
- `feature_refs`: required, non-empty.
- `description`: optional.
- `annotations`: optional.
- `selected_feature_id`: optional, but must belong to `feature_refs[*].feature_id`.

## 3. API endpoints (core runtime contract)
- `POST /api/research-slices` — сохранить новый slice.
- `GET /api/research-slices` — получить список моих slices.
- `GET /api/research-slices/{slice_id}` — открыть/восстановить slice по id.
- `DELETE /api/research-slices/{slice_id}` — удалить slice по id.
- `PATCH /api/research-slices/{slice_id}` — обновить owner-only slice.
- `POST /api/research-slices/{slice_id}/share` — создать новый read-only capability token; предыдущий token этого Slice становится недействительным.
- `DELETE /api/research-slices/{slice_id}/share` — отозвать активную share-ссылку.
- `GET /api/public/research-slices/shared` + `X-ARTEMIS-Share-Token` — открыть unlisted read-only Slice без аутентификации; token не помещается в request URL/access log.

## 4. Ownership and visibility
- Доступ только для аутентифицированного владельца.
- Owner CRUD остаётся owner-only и возвращает `404` для другого пользователя.
- Share является явным unlisted read-only доступом по capability token, а не публикацией в каталоге.
- В базе хранится только SHA-256 token; raw token возвращается владельцу один раз при создании/rotation.
- Public response не содержит `owner_id`, не допускает mutation и отправляется с `Cache-Control: no-store`, `Referrer-Policy: no-referrer` и `X-Robots-Tag: noindex`.
- UI-ссылка хранит token во fragment `#share=...`, поэтому он не передаётся Pages-серверу и не входит в обычный HTTP referrer.
- Повторный share атомарно ротирует capability; revoke, rotation или удаление Slice делают прежнюю ссылку недействительной.

## 5. Integration points
- Map integration: **part of** slice-контракта (состояние карты фиксируется в `view_state` и `time_range`).
- Auth integration: **part of** slice-доступа (owner-only enforcement).
- Drafts integration: **not part of** Research Slice runtime-контракта.

## 6. Out of scope (current baseline)
- AI assistance (explain/compare/suggest).
- public searchable Slice directory;
- collaborative/edit access по share-ссылке;
- multi-token ACL и per-recipient permissions;
- immutable share snapshot: текущая ссылка показывает актуальную owner-версию Slice до revoke/rotation.
- Stories/scenario-layer orchestration.

## 6.1 Response shapes
- LIST (`GET /api/research-slices`) → lightweight payload (без `description` и без тяжёлых JSON-полей).
- DETAIL (`GET /api/research-slices/{slice_id}`) → full payload.
- PUBLIC DETAIL (`GET /api/public/research-slices/shared`) → full read-only state без owner identity, `visibility = shared_read_only`; capability передаётся только в `X-ARTEMIS-Share-Token`.
