# Controlled Release Decision

## Статус документа

- Тип: historical compatibility release decision document
- Статус: preserved / compatibility baseline; **not the current ARTEMIS Core release owner**
- Историческая роль: зафиксировать controlled-release baseline Architecture Atlas/backend contour и границу между этим baseline и production-grade claims
- Current Core routing: фактическая доступность — `PROJECT_TRUTH.md`; current product execution — `DEVELOPMENT_OPERATING_SYSTEM.md`, `PRIORITIES.md`, `PROJECT_PHASES.md`; executable product signal — current GitHub workflows, прежде всего `ARTEMIS Core Check`
- Scope: Architecture Atlas checked-in data artifacts, preserved backend/runtime baseline, legacy release/readiness interpretation

Этот документ сохраняет принятое историческое решение и не переписывается как будто оно относилось к нынешнему Leonardo Temporal Map. После Core Reset / PR `#393` он не определяет active #355 product gate и не может требовать backend/ETL/PWA checks от статического read-only Core path.

---

## 1. Verified compatibility baseline

- `python scripts/release_check.py` остаётся executable compatibility check для Architecture Atlas/backend/data contour; он не является единственным current ARTEMIS Core product signal.
- Legacy release gate/ETL проверяют owned `data/*` artifacts и применяются, когда меняются соответствующие compatibility paths.
- PWA behavior, auth/session, moderation и `/api/map/feed` относятся к preserved compatibility runtime, а не к current Leonardo Temporal Map critical path.
- Governance boundary остаётся полезной и действующей внутри этого contour: checked-in `data/*` — public Architecture Atlas projection; auxiliary `/api/map/feed` не становится canonical public dataset.
- Moderation baseline сохраняет two-step review invariant: `pending -> review -> approved/publish-attempt`.
- Auth/session baseline сохраняет собственные operational constraints и не должен описываться как production-hardened multi-node system.

Compatibility release unit:

- required artifacts: `data/features.geojson`, `data/features.json`, `data/id_aliases.json`, `data/export_meta.json`, `data/rejected.json`, `data/validation_report.json`, `data/content_profile.json`;
- canonical public Architecture Atlas map dataset: `data/features.geojson`;
- supporting/derived artifacts: `features.json`, `export_meta.json`, `rejected.json`;
- owned compatibility gate blocks if required artifacts are missing, record counts diverge or warning thresholds exceed its policy.

This release unit is **not** the Leonardo Globe/Temporal Map historical data source. The active Globe consumes the reviewed repository World Model/World Slice through Explorer State and Render Projection.

## 2. Remaining gaps and classification

Inside the preserved compatibility contour:

- `/api/map/feed` remains an auxiliary adapter rather than a production-grade public read model;
- production-grade multi-instance persistence, broader scaling and observability remain unclaimed;
- manual smoke evidence may be cited only when the referenced artifact actually exists and matches the relevant runtime revision.

These are compatibility/post-baseline gaps, not blockers for the current static read-only #355 Temporal Map loop unless a future accepted decision reopens the corresponding runtime branch.

Historical status sync from the original baseline remains traceable through Git history and prior audits; it must not be used to infer current product maturity.

## 3. Historical decision

**MOVE TO CONTROLLED RELEASE BASELINE**

Interpretation:

- the decision closed the controlled baseline gate for the then-current Architecture Atlas/backend scope;
- it never meant blanket production readiness;
- it does not close Gate D, validate Life in Context or authorize current product expansion.

## 4. Current routing

For a current ARTEMIS question, do **not** use this file as a general release owner.

Use:

1. `PROJECT_TRUTH.md` — what is actually public/backend/R&D now;
2. `DEVELOPMENT_OPERATING_SYSTEM.md` + `project_state.json` — active lifecycle/gate;
3. current workflow files — executable product/repository behavior;
4. `DATA_CONTRACT.md` — Architecture Atlas ETL/public data mechanics when that contour is relevant;
5. this document — only to interpret the preserved controlled-release compatibility baseline and its historical production-grade boundary.

## 5. Compatibility baseline vs production-grade

Acceptable inside the preserved compatibility baseline:

- static Architecture Atlas delivery from published `/data/*`, with `data/features.geojson` as that contour's canonical public dataset;
- auxiliary authenticated/runtime usage of `/api/map/feed` as a non-canonical support route;
- moderation runtime remaining separate from public dataset overwrite path, with two-step review gate enforced before publish-attempt;
- single-instance-oriented auth/session baseline with explicit operational constraints;
- split compatibility CI/workflow lanes that prove their owned subsystems.

Not to be described as production-grade merely because this historical baseline exists:

- `/api/map/feed` as a mature public read model;
- multi-instance/high-availability auth/session guarantees as finished operational truth;
- broader persistence governance, scaling envelope and observability/ops hardening as completed;
- the whole ARTEMIS runtime as production-ready;
- the current `/globe/` R&D prototype as validated product capability.