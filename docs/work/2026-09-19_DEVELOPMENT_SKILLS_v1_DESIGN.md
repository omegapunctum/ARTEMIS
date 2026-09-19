# ARTEMIS Development Skills v1 — design candidate

Recorded 2026-09-19. Scope: engineering tooling design only, not installed or enabled; no product successor. Status: design prepared; plugin-eval execution BLOCKED (required skill unavailable in this environment). This document is not an operational-policy owner.

## Inspected layout and provenance

Repository inspected at main `4526c95e214d423170affe5137bee76622baaac3`: `AGENTS.md` is the repository entrypoint; no ARTEMIS plugin manifest or repository skill package exists. Execution rules belong to `docs/DEVELOPMENT_OPERATING_SYSTEM.md`. Existing scripts, tests and workflows remain the verification system.

This hosted session exposes managed system skills and cached curated plugins. `skill-creator` and `plugin-creator` instructions and the latter's manifest reference were read. No `plugin-eval` skill/tool or local package was found in the available catalogs or skill/plugin directories; no `codex` executable is on PATH. This describes this session, not the owner's desktop or all Codex installations. No credentials/configuration contents were inspected, and no installation/configuration was changed.

Format checked against current official [Build plugins](https://learn.chatgpt.com/docs/build-plugins) and [Build skills](https://learn.chatgpt.com/docs/build-skills), accessed 2026-09-19. The current documentation distinguishes portable root `plugin.json` from the supported plugin-creator `.codex-plugin/plugin.json` compatibility scaffold. Choose the latter for this v1 to match the available creator/validator. Skills use `SKILL.md` with YAML `name` and `description`; optional UI metadata is unnecessary here. No second manifest or duplicate `.agents/skills` installation is proposed.

## Minimal proposed package

Package root: `plugins/artemis-development/` in ARTEMIS if implementation is subsequently requested. It contains only:

| Path under package root | Purpose |
|---|---|
| `.codex-plugin/plugin.json` | Skills-only manifest |
| `skills/task-router/SKILL.md` | Resolve task and live owners |
| `skills/engineering-loop/SKILL.md` | Execute accepted bounded work |
| `skills/pr-self-review/SKILL.md` | Review exact PR head against owners |

Proposed manifest (not installed):

```json
{
  "name": "artemis-development",
  "version": "1.0.0",
  "description": "Owner-directed ARTEMIS engineering workflows",
  "author": {"name": "ARTEMIS"},
  "skills": "./skills/",
  "interface": {
    "displayName": "ARTEMIS Development",
    "shortDescription": "Route, execute and review ARTEMIS work"
  }
}
```

No MCP server, app, hooks, background pickup, framework, copied contracts, design tokens or bundled test runner. Use existing GitHub access. Installation/distribution is outside this design task.

## Candidate skill contents

### task-router

```markdown
---
name: task-router
description: Route a new ARTEMIS task to its current GitHub owners and autonomy class before implementation. Use for task intake or unclear ownership, not generic coding or an already-routed execution step.
---
Read the current AGENTS.md in https://github.com/omegapunctum/ARTEMIS and follow its context/owner routing. Resolve the current default-branch SHA through GitHub; read owners at that SHA and record it. An existing checkout is usable only after checking its base against that revision. Do not use chat history or this skill as current-state authority.

Read docs/DEVELOPMENT_OPERATING_SYSTEM.md at that revision for classification, escalation and execution rules. For current state follow AGENTS.md to the human, machine and work-registry owners. Read only the additional task-specific owners needed; use docs/FOUNDATION_INDEX.md if unresolved.

Return the confirmed input, owner links/revision, allowed scope/files, autonomy class with owner basis, smallest verification plan and unresolved decision/blocker. Hand accepted engineering work to engineering-loop. Route an unresolved product/semantic choice to the appropriate ARTEMIS chat named by the owners/request; do not invent a policy or implement it.

If live owners cannot be read or disagree, report the exact access/authority problem; do not substitute cached policy. Re-resolve ownership when scope changes.
```

### engineering-loop

```markdown
---
name: engineering-loop
description: Implement or fix an already-authorized ARTEMIS repository task through its owned verification loop. Use after task routing; not for deciding new product scope or reviewing an existing PR alone.
---
Locate https://github.com/omegapunctum/ARTEMIS. Read current AGENTS.md and docs/DEVELOPMENT_OPERATING_SYSTEM.md from the GitHub default branch, recording the revision. Verify the supplied task's owner/scope against that revision; obtain task-router output if missing or stale.

Follow the live operating system's execution loop and autonomy/escalation contract. Inspect the affected files and owned workflows/tests, state the minimal plan, implement within the accepted scope, run relevant checks, fix in-scope failures and rerun. Preserve unrelated work. Record evidence commands, revisions, results and limitations; distinguish local, CI, deployed and human-reported evidence.

Update directly affected current-state/document owners only when supported by the authorized result. Use ARTEMIS's existing scripts/tests for repeatable checks, not a parallel framework. Request pr-self-review on the exact proposed head before handoff. Apply the live PR/handoff and merge sections, including any task-specific hold; this skill grants no merge permission. Return PR/branch, changes, preserved boundaries, verification, remaining human checks and status.
```

### pr-self-review

```markdown
---
name: pr-self-review
description: Self-review a prepared ARTEMIS PR or diff against its accepted scope and current GitHub owners. Use before merge or when the PR head changes; not a new implementation intake or independent human acceptance.
---
Read current AGENTS.md and docs/DEVELOPMENT_OPERATING_SYSTEM.md from https://github.com/omegapunctum/ARTEMIS, recording the default-branch revision. Resolve the PR's base/head and accepted task-specific owners. Review the actual diff and relevant evidence, not just the PR summary.

Check intended behavior, bounded file scope, owner consistency, preserved domain assertions, regressions, evidence provenance and unsupported capability/value claims. Inspect relevant CI results and review threads for the exact head. For each finding give the file, concrete failure/risk and required correction; distinguish blockers from limitations.

Return findings, inspected revisions, checks actually observed and readiness under the live operating system's merge contract. Self-review cannot stand in for a required human review or independent review. A changed head requires renewed applicable review/checks. Hand in-scope corrections back to engineering-loop. Do not merge merely because this skill ran; consult current merge authority and task-specific holds.
```

## Evaluation plan and limits

Use `skill-creator`'s `quick_validate.py` for each materialized candidate and `plugin-creator`'s `validate_plugin.py` for the package. These validate structure, not behavior. Required `plugin-eval` must be made available and its instructions read before creating/running its evaluation artifacts; no guessed CLI or substitute evaluator is specified.

| Representative case | Expected observation |
|---|---|
| New ARTEMIS bug task with known owner | Router resolves current SHA/owner/class; does not implement at intake |
| Accepted bounded fix | Engineering loop preserves scope, uses owned checks, repairs caused failures |
| Prepared PR review | Self-review inspects diff/current head and CI; does not relaunch intake unnecessarily |
| Non-ARTEMIS request | None of these skills should trigger |
| Request to invent new geometry/product capability | Routes to live decision authority; no silent implementation |
| Old chat says Region pending; live owners say complete | Current GitHub owner wins, with revision cited |
| GitHub unavailable or contradictory owners | Exact blocker reported, no invented current state |
| Green CI but changed head / explicit hold / missing required review | No merge; apply current operating-system contract |
| Owner policy changes after plugin packaging | Updated owner applied without editing skill policy text |
| Automated UI PASS offered as E1/E2 or validated value | Evidence kind preserved; no value promotion |

Run these as isolated representative tasks with negative trigger cases. Record plugin/skill content digest, owner SHA, evaluator/version, prompts, observed traces, findings and limitations. No mutations to product data, real merges or installation are needed for these eval cases; use a test fixture/temporary checkout for actions. An evaluation result cannot grant production authority.

Current evidence: layout inspection and design self-review only. Behavioral evaluation, activation and plugin-eval PASS are NOT claimed. No test result for Region or product maturity derives from this tooling design.
