# ARTEMIS — RESEARCH WORK / SLICE REVISION CONTRACT

## Статус документа

- Тип: canonical foundation product/data/UI contract.
- Версия: 3.0.
- Дата: 2026-07-28.
- Статус: active supporting concept target with explicit runtime compatibility boundary.
- Filename сохранён для совместимости ссылок; документ владеет optional deep research-work model, not the first ARTEMIS value.
- Runtime/API authority: `RESEARCH_SLICE_SPEC.md`.

## 1. Главная формула

Когда пользователь переходит от spatial-temporal exploration к глубокой исследовательской работе, ARTEMIS может сохранять не только viewport или mutable note, а версионированный результат.

Canonical model:

```text
Investigation
└── Slice Revision (immutable)
    ├── Question
    ├── Compared entities
    ├── Claims / Findings
    ├── Evidence Links
    ├── Conclusion or Unresolved
    ├── Uncertainty
    ├── Dataset / schema identity
    └── Saved View
         ├── map
         ├── time
         ├── filters
         └── selection

Research Brief = readable projection of one Slice Revision
```

Первая пользовательская ценность Foundation v3 возникает в contextual spatial-temporal understanding. Investigation удерживает последующую глубокую работу во времени; Slice Revision делает её проверяемой; Research Brief переносит результат. Не каждый synchronized exploration обязан создавать Investigation или Brief.

## 2. Термины и identity

### 2.1 Investigation

`Investigation` — развивающаяся работа пользователя вокруг одного вопроса или связанной линии исследования.

It owns:

- stable investigation id;
- owner;
- title;
- current question/scope;
- ordered revision ids;
- latest revision pointer;
- private/share policy;
- created/updated timestamps.

Investigation может меняться. Его history не должна переписываться.

### 2.2 Slice Revision

`Slice Revision` — неизменяемая версия Investigation в конкретный момент.

Revision pins:

- revision id and number;
- parent investigation id;
- optional parent revision id;
- research content;
- epistemic content;
- dataset/content identifier;
- schema version;
- created timestamp;
- creator/origin context.

После создания revision не редактируется. Update Investigation создаёт новую revision.

### 2.3 Saved View

`Saved View` — вложенный serializable UI-context:

- viewport;
- time range/mode;
- enabled layers;
- filters;
- selected/compared entities;
- optional display mode.

Saved View:

- помогает восстановить контекст;
- может быть пустым/ограниченным для вопроса, где map/time несущественны;
- не содержит conclusion;
- не является Research Slice Revision сам по себе.

### 2.4 Research Brief

`Research Brief` — детерминированное человекочитаемое представление одной revision.

Brief:

- не имеет независимого epistemic content;
- показывает revision id/version;
- сохраняет Claim/Evidence/uncertainty semantics;
- пригоден для copy/export в Markdown/plain text;
- является citation-ready в пределах доступных source metadata/locators.

Если Brief и revision расходятся, revision является source of truth, а Brief должен быть перегенерирован.

## 3. Почему mutable ResearchSlice недостаточен

Mutable record полезен для editing, но не обеспечивает:

- воспроизводимость старого вывода;
- стабильную shared citation;
- понимание, какие data были видимы на момент вывода;
- безопасное сравнение изменений;
- rollback without data loss.

`content_version += 1` в одной mutable row не является immutable revision history.

Поэтому current runtime `ResearchSlice v2` трактуется как compatibility persistence envelope/latest working state, а не завершённая target model.

## 4. Обязательный состав Slice Revision

### 4.1 Question and scope

- research question;
- optional task/context;
- selection rationale;
- explicit scope limits.

### 4.2 Compared entities

- stable entity/Feature refs;
- display labels as snapshot only where needed;
- comparison order/focus;
- no silent identity remapping.

### 4.3 Claims and findings

Revision содержит:

- selected canonical Claims or stable refs;
- user-authored Claims/findings;
- claim kind and origin;
- review/confidence/evidence summary;
- optional entity/relation references.

User finding не становится canonical public Claim без отдельного governance flow.

### 4.4 EvidenceLinks

Major Claims связываются с:

- Source id;
- locator;
- `supports`, `challenges` or `contextualizes`;
- evidence strength;
- review state.

Source list без claim linkage не является полноценной evidence chain.

### 4.5 Conclusion

Revision содержит:

- conclusion Claim; или
- explicit `unresolved`.

`unresolved` является полноценным исследовательским результатом, если объяснены missing/conflicting evidence.

### 4.6 Uncertainty

Material uncertainty фиксируется по типу и влиянию на conclusion.

### 4.7 Versions

Revision обязана идентифицировать:

- revision schema version;
- dataset/content export version or immutable snapshot reference;
- relevant relation/source artifact versions where available.

Хеш/номер без определённой semantics не считается pinned dataset identity.

### 4.8 Saved View

Saved View вложен и отделён от epistemic content.

## 5. Lifecycle

### 5.1 Create Investigation

Создаётся stable investigation identity и первая revision.

Create не должен заставлять пользователя выдумывать conclusion или evidence:

- evidence может быть `missing`;
- conclusion может быть `unresolved`;
- uncertainty должна быть сохранена честно.

### 5.2 Create revision

Каждое содержательное изменение создаёт новую immutable revision:

- question/scope;
- entity selection;
- Claims/findings;
- EvidenceLinks;
- conclusion/uncertainty;
- Saved View when material.

Autosave draft mechanics могут быть mutable, но draft не называется revision до explicit save/commit.

### 5.3 Reopen

Reopen Investigation:

- показывает latest revision by default;
- позволяет открыть конкретную prior revision;
- восстанавливает research content before or alongside Saved View;
- не заменяет unavailable entity/source новой записью без notice.

### 5.4 Compare revisions

Future but compatible behavior:

- added/removed Claims;
- changed EvidenceLinks;
- conclusion changes;
- uncertainty changes;
- Saved View changes.

Revision compare не входит в current MVP exit, но target model не должна его блокировать.

### 5.5 Delete

Owner may delete Investigation under privacy policy.

До реализации retention/recovery policy продукт не обещает audit-grade permanent archive. Delete должен отзывать public capabilities.

### 5.6 Share

Target baseline:

- share URL pins one immutable revision;
- response is read-only;
- owner identity is not exposed by default;
- capability is unlisted and revocable;
- response is no-store/noindex;
- recipient can copy into own Investigation without mutating original.

Optional future `live` share may follow latest revision only with visible mutable/live label.

Current runtime share points to mutable `ResearchSlice`. До revision migration он не может называться revision-pinned or reproducible share.

### 5.7 Export Brief

Revision can render:

- Markdown;
- plain text;
- read-only web representation.

Minimal export contains:

- title/question;
- entity selection/rationale;
- Claims/findings;
- evidence citations and locators;
- conclusion/unresolved;
- uncertainty;
- revision and dataset identifiers.

PDF/DOCX are not required for current MVP.

## 6. Reproducibility semantics

ARTEMIS may call a result reproducible only if:

1. a specific immutable revision can be reopened;
2. dataset/content identity is pinned and meaningful;
3. Claims and EvidenceLinks preserve stable refs or explicit snapshots;
4. source locator is retained;
5. Brief identifies the revision;
6. mutable/live behavior is labelled.

If an external Source changes or disappears:

- ARTEMIS preserves metadata/locator available at revision time;
- it may show source-unavailable state;
- it must not silently substitute a different Source.

ARTEMIS does not promise legal archival copy of third-party source content unless separately authorized.

## 7. Epistemic rules

`EPISTEMIC_CONTRACT.md` owns Claim/Evidence semantics.

Inside revision:

- factual, interpretation, hypothesis and counterfactual kinds remain distinct;
- origin remains visible where material;
- major conclusion is traceable;
- shared classification and Similarity are not substantive Relations;
- challenging evidence is not dropped;
- unsupported Claim remains hypothesis/missing-evidence or is removed;
- AI-origin content, if introduced, remains marked.

## 8. Ownership and privacy

Default:

- Investigation private;
- owner-only mutation;
- public share is unlisted read-only capability;
- canonical public dataset is unchanged;
- user-authored Claims are not searchable public knowledge;
- recipient cannot infer owner identity from public payload;
- token rotation/revoke invalidates prior capability.

Collaborative editing, searchable public directory and per-recipient ACL are outside current scope.

## 9. Relationship to product entities

- `Entity/Feature` is researched.
- `Claim` states something about Entity/context.
- `EvidenceLink` connects Claim to Source.
- `Relation` is a structured Claim.
- `Investigation` organizes evolving research.
- `Slice Revision` freezes one result state.
- `Saved View` preserves UI context.
- `Research Brief` transfers revision content.
- future Story/Course/AI may consume revision, but cannot define its core semantics.

## 10. Current runtime compatibility

`RESEARCH_SLICE_SPEC.md` v2 currently provides:

- one mutable `ResearchSlice` id;
- question and rationale;
- Feature refs;
- Source/Relation evidence refs;
- typed findings;
- conclusion/unresolved;
- uncertainty;
- nested Saved View;
- content/schema version;
- owner CRUD and mutable unlisted share.

It does not provide:

- Investigation/revision separation;
- immutable revision history;
- claim-level locator/relation/strength;
- pinned dataset export identity;
- revision-pinned share;
- deterministic Brief export.

Documentation and UI must not describe absent target capabilities as implemented.

## 11. Migration constraints

Future migration must:

1. preserve current ids, owner, timestamps and share state where safe;
2. create Investigation identity without inventing user intent;
3. migrate current row as an initial revision snapshot;
4. preserve `missing`/`unresolved`;
5. not invent locators, EvidenceLinks, confidence or dataset version;
6. identify current mutable shares and explicitly choose pin-latest or pin-migrated-revision behavior;
7. remain idempotent and covered by rollback/preflight tests;
8. retain compatibility read path for one controlled cycle.

## 12. Out of scope

- real-time collaboration;
- public searchable Investigation directory;
- automatic canonical promotion;
- mandatory AI summaries;
- Story/Course generation;
- citation-style completeness beyond available metadata;
- source-content archiving without rights;
- revision merge/conflict resolution;
- institutional retention policy.

## 13. Acceptance criteria

Target research-work model is product-complete when:

1. Investigation has stable identity and multiple immutable revisions.
2. Update creates a revision rather than rewriting history.
3. Revision preserves question, Claims, EvidenceLinks, conclusion/unresolved and uncertainty.
4. Saved View is nested and optional to epistemic completeness.
5. Dataset/schema identity is meaningful and pinned.
6. Shared URL points to an immutable revision or is visibly `live`.
7. Brief is generated from revision and includes citations/locators.
8. Reopen and share do not disclose owner or permit mutation.
9. Legacy migration does not invent evidence.
10. Public E2E and product validation pass the canonical gates.

## 14. Failure modes

The model is degraded if:

- Research Slice is only a bookmark;
- one mutable row is called immutable history;
- content version is called reproducibility without pinned data;
- Source list is shown without claim linkage;
- conclusion cannot be traced;
- shared link changes silently after author edits;
- Brief becomes an independent stale copy;
- Saved View is mandatory even when irrelevant to question;
- user Claims become public facts automatically;
- migration fabricates evidence or confidence.

## 15. Change control

Any research-work change must check:

- `PRODUCT_THESIS.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `PRODUCT_VALIDATION_PLAN.md`;
- `RESEARCH_SLICE_SPEC.md`;
- `EPISTEMIC_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `DATA_CONTRACT.md`;
- `CONTENT_GOVERNANCE.md`;
- privacy/share headers and token behavior;
- migrations and executable tests.

Product semantics, runtime shape and UI must not drift silently.

## 16. Итог

The stable research chain is:

`Investigation → immutable Slice Revision → Research Brief`

Each revision preserves:

`Question → Claims → Evidence → Findings → Conclusion / Unresolved`

Saved View enriches this result with spatial-temporal context but does not replace it.
