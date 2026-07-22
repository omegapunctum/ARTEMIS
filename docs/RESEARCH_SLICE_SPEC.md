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
- owner CRUD сохраняет `visibility` как `private`;
- read-only share response использует вычисляемое значение `shared`, но не меняет owner resource и не публикует Slice в canonical dataset.

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
- `POST /api/research-slices/{slice_id}/share` — создать новую opaque read-only ссылку; предыдущая ссылка этого Slice аннулируется.
- `DELETE /api/research-slices/{slice_id}/share` — отозвать текущую read-only ссылку.
- `GET /api/research-slices/shared/{share_token}` — открыть Slice без аутентификации по capability-token.

## 4. Ownership and visibility
- Доступ только для аутентифицированного владельца.
- Owner CRUD остаётся private и owner-only.
- Cross-user authenticated access к owner endpoint отсутствует и возвращает `404`.
- Share является unlisted capability access, а не public listing: token должен быть известен читателю заранее.
- В БД хранится только SHA-256 token; raw token возвращается владельцу один раз при создании ссылки.
- Повторный `POST .../share`, revoke и удаление Slice делают ранее выданный token недействительным.
- Shared response не содержит `owner_id` и отправляется с `Cache-Control: private, no-store` и `Referrer-Policy: no-referrer`.
- Читатель не получает write endpoint; изменения и удаление требуют owner auth.

## 5. Integration points
- Map integration: **part of** slice-контракта (состояние карты фиксируется в `view_state` и `time_range`).
- Auth integration: **part of** slice-доступа (owner-only enforcement).
- Drafts integration: **not part of** Research Slice runtime-контракта.

## 6. Out of scope (current baseline)
- AI assistance (explain/compare/suggest).
- Collaborative access и searchable/public listing.
- Stories/scenario-layer orchestration.

## 6.1 Response shapes
- LIST (`GET /api/research-slices`) → lightweight payload (без `description` и без тяжёлых JSON-полей).
- DETAIL (`GET /api/research-slices/{slice_id}`) → full payload.
- SHARED DETAIL (`GET /api/research-slices/shared/{share_token}`) → full research context без `owner_id`, с `visibility=shared` и `shared_at`.
