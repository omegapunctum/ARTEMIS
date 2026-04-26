# 2026-04-26_DOCUMENTATION_AUDIT_FIXES_NOTE_ACTIVE_v1_0

## Статус документа

- Тип: audit follow-up note
- Статус: active
- Дата: 2026-04-26
- Layer: docs/audits

---

## 1. Назначение

Документ фиксирует точечные исправления после total documentation audit 2026-04-26.

---

## 2. Исправлено

### 2.1 GitHub Pages artifact drift

Файл: `.github/workflows/pages.yml`

Исправление:
- `css/main-screen.css` добавлен в список файлов, копируемых в GitHub Pages artifact.

Причина:
- `index.html` подключает `css/main-screen.css`, но workflow ранее не включал его в deploy artifact.

### 2.2 Master prompt phase-order drift

Файл: `docs/ARTEMIS_MASTER_PROMPT.md`

Исправление:
- активный порядок работ синхронизирован с текущим repo-baseline:
  - Phase 5 / Scaling Hardening — основной активный цикл;
  - Phase 6 / Product Expansion — следующий запланированный слой;
  - Phase 4 и Phase 3 — closed baseline reference без reopen при отсутствии нового drift.

### 2.3 Stale manual smoke evidence reference

Файл: `docs/CONTROLLED_RELEASE_DECISION.md`

Исправление:
- удалена прямая ссылка на отсутствующий `docs/MANUAL_SMOKE_EVIDENCE_2026-04-11.md`;
- добавлено правило, что smoke evidence artifact можно цитировать только после проверки фактического пути в репозитории.

### 2.4 DATA_CONTRACT schema expansion

Файл: `docs/DATA_CONTRACT.md`

Исправление:
- добавлен canonical status block;
- добавлена owner chain Airtable → ETL/export → checked-in `data/*` → public map runtime;
- расширен release artifact contract;
- добавлен public GeoJSON schema baseline;
- добавлена таблица public feature properties schema;
- добавлены date contract, validation/rejection semantics и change-control rule.

Причина:
- прежняя версия фиксировала release artifact semantics, но не задавала полноценный schema-level data contract.

### 2.5 Reference storage policy status hygiene

Файл: `docs/reference/2026-04-19_DOCUMENTATION_STORAGE_POLICY_SYSTEM_ACTIVE_v1_0.md`

Исправление:
- внутренний статус понижен с `active` до `reference / historical governance-support material`;
- добавлено указание, что текущий canonical source of truth для documentation governance — `docs/DOCUMENTATION_SYSTEM.md`.

### 2.6 Archive documentation structure status hygiene

Файл: `docs/archive/2026-04-19_DOCUMENTATION_SYSTEM_STRUCTURE_SPEC_ACTIVE_v1_0.md`

Исправление:
- внутренний статус понижен с `active` до `archived / historical reference`;
- добавлено указание, что текущий canonical documentation governance определяется в `docs/DOCUMENTATION_SYSTEM.md`.

---

## 3. Остаётся открытым

1. Проверить, остались ли другие archive/reference файлы с misleading active-status.
2. Canonical style unification.
3. Дополнительная проверка cross-links после следующих docs changes.

---

## 4. Минимальные проверки

- `python scripts/release_check.py`
- `pytest`
- проверка GitHub Pages artifact на наличие `css/main-screen.css`
- проверка отсутствия прямой ссылки на несуществующий manual smoke evidence path
- проверка, что `DATA_CONTRACT.md` не конфликтует с текущими `data/*` artifacts
- проверка, что archive/reference docs не используются как canonical source of truth

---

## 5. Итог

Текущий patch-пакет закрывает шесть audit findings: deploy artifact drift, phase-order drift, stale release evidence reference, недостаточную schema-level детализацию data contract, reference status drift и archive status drift.
