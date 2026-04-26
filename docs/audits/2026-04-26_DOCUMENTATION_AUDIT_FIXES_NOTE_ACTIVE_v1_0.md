# 2026-04-26_DOCUMENTATION_AUDIT_FIXES_NOTE_ACTIVE_v1_0

## Статус документа

- Тип: audit follow-up note
- Статус: active
- Дата: 2026-04-26
- Layer: docs/audits

---

## 1. Назначение

Документ фиксирует первый точечный пакет исправлений после total documentation audit 2026-04-26.

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

---

## 3. Остаётся открытым

1. Archive/reference status hygiene.
2. DATA_CONTRACT schema expansion.
3. Canonical style unification.
4. Дополнительная проверка cross-links после следующих docs changes.

---

## 4. Минимальные проверки

- `python scripts/release_check.py`
- `pytest`
- проверка GitHub Pages artifact на наличие `css/main-screen.css`
- проверка отсутствия прямой ссылки на несуществующий manual smoke evidence path

---

## 5. Итог

Первый patch-пакет закрывает три audit findings: deploy artifact drift, phase-order drift и stale release evidence reference.
