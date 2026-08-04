---
name: implementation-execution
description: Use when the user asks to execute, continue, or resume an existing approved, repository-grounded implementation plan. Performs bounded edits one coherent plan step at a time, verifies each step, preserves invariants and unrelated work, records a plan-conformance ledger, and stops on material plan deviation. Do not use for creating or refining a plan, ordinary direct implementation without an approved plan, debugging, code review, or remediation of an existing issue ledger.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.0.1'
  allow_implicit_invocation: 'true'
---

# Implementation Execution

## Activation boundary

Use this skill only when the user asks to execute, continue, or resume an existing approved implementation plan.

Eligible inputs include:

- A `READY_TO_IMPLEMENT` plan produced by `implementation-plan`.
- A user-provided plan that satisfies the executable plan contract below.
- A partially completed plan plus a request to continue its remaining steps.
- A request to resume from a named plan step.

Do not activate for:

- Creating, reviewing, refining, or sequencing a plan; use `implementation-plan`.
- Root-cause investigation; use `debug`.
- Ordinary direct implementation without an approved plan.
- Reviewing a diff or deciding merge readiness; use `code-review`.
- Fixing an existing issue ledger or running repeated remediation; use `iterative-self-review`.

When intent overlaps, follow the requested artifact. Plan creation belongs to `implementation-plan`; approved plan execution belongs here; review belongs to `code-review`; known-ledger remediation belongs to `iterative-self-review`.

## Execution modes

Choose exactly one primary mode and state it in the output.

- `plan execution`: Execute an approved plan from the beginning.
- `implementation continuation`: Reconcile a partially implemented plan against current repository state and continue only remaining steps.

Do not create feature, refactor, migration, dependency, or test modes. Those properties come from the supplied plan.

## Executable plan gate

Classify the plan before editing:

- `ELIGIBLE`: Ordered, repository-grounded, and free of unresolved material decisions.
- `ELIGIBLE_WITH_VALIDATION`: Only low-risk reversible assumptions remain and can be validated before the affected step.
- `INELIGIBLE`: A material contract, architecture, security, data, compatibility, rollout, or ownership decision is missing.

An executable plan must include:

- the desired outcome and constraints;
- ordered steps;
- repository paths or resolvable anchors;
- relevant invariants;
- dependencies or sequencing;
- verification for each material step; and
- no unresolved material design decision.

`READY_TO_IMPLEMENT` is eligible. `READY_WITH_ASSUMPTIONS` is eligible only when every relevant assumption can be validated safely before its step. `NOT_READY` is ineligible.

Resolve moved files, renamed symbols, and equivalent repository commands by inspection. Do not invent missing APIs, migrations, architecture, or rollout decisions.

## Baseline

Before editing, record:

- branch and HEAD;
- staged, unstaged, and untracked files;
- plan-owned paths;
- unrelated dirty paths;
- dirty plan-owned paths and the ownership of each existing hunk;
- relevant existing verification failures, or that they were not established; and
- the comparison base when one is needed.

For dirty plan-owned paths, reconcile existing hunks before editing. Classify them as compatible partial implementation, unrelated user work, or conflict. Preserve compatible and unrelated user changes. Stop when ownership or intent is ambiguous or when continuing would overwrite user work.

Prefer the commands in `references/baseline-and-verification-rules.md`. Never use destructive cleanup, broad checkout restoration, automatic stashing, or reset to make the baseline convenient.

## Required workflow

1. Capture the execution baseline and preserve unrelated work.
2. Parse the supplied plan into ordered steps, dependencies, invariants, and verification.
3. Apply the executable plan gate.
4. Reconcile every plan step and every dirty plan-owned hunk against current repository state.
5. In continuation mode, verify completed objectives and do not redo them.
6. Execute one coherent plan step at a time.
7. Change canonical source rather than generated output.
8. Run the focused verification required by that step.
9. Update the plan-conformance ledger with changed paths and evidence.
10. Stop immediately when a material deviation is required.
11. After all executable steps, run the smallest integration checks justified by affected boundaries.
12. Hand the completed diff to `code-review`.

Load references only as needed:

- `references/baseline-and-verification-rules.md` for baseline and verification handling.
- `references/plan-conformance-and-deviation-rules.md` for statuses and the deviation gate.
- `references/execution-quality-checklist.md` before finalizing.
- `references/evaluation-playbook.md` only when evaluating this skill.

## Step execution rules

For each plan step:

1. Restate the plan objective and preserved invariants.
2. Inspect the current implementation and relevant surrounding contract.
3. Classify the step as `not started`, `in progress`, `completed`, `blocked`, `skipped by plan`, or `deferred by user`.
4. Apply the smallest coherent edit set needed for that objective.
5. Run the plan-specified check or an evidenced equivalent.
6. Record exact changed paths, verification, and deviations.
7. Continue only when the step objective and invariants remain satisfied.

A step is `completed` only when its objective is implemented and required verification supports it. File presence or code edits alone are insufficient.

## Plan-conformance ledger

Use the original step numbering when available; otherwise assign stable IDs such as `PLAN-01`.

| Step    | Plan objective | Status    | Changed paths | Verification       | Deviation |
| ------- | -------------- | --------- | ------------- | ------------------ | --------- |
| PLAN-01 | Objective      | completed | `path/file`   | command and result | none      |

Distinguish:

- paths changed during this execution;
- paths already dirty before execution;
- paths inspected but not modified;
- verification actually run;
- verification not run;
- minor deviations; and
- material blockers.

## Deviation gate

Minor deviations may proceed and must be recorded:

- An evidenced file moved since the plan was written.
- A symbol was renamed without changing the contract.
- The repository provides an equivalent verification command.
- An existing test belongs in a different canonical test file.
- A local implementation detail changes while the objective and invariants remain identical.

Material deviations must stop execution:

- A public API, serialized field, event, route, or compatibility contract must change.
- A new dependency, service, package, architectural layer, or trust boundary is required.
- Planned migration or deployment ordering is unsafe.
- Security, privacy, authorization, data-integrity, or rollout assumptions are invalid.
- Unrelated cleanup is required to continue.
- Canonical source ownership cannot be established.
- Dirty plan-owned work has ambiguous ownership or cannot be preserved safely.
- Required verification cannot run and no equivalent evidence exists.
- An irreversible or external operation lacks explicit authorization.
- A continuation step believed complete does not satisfy its objective and fixing it changes the approved design.

When material deviation occurs, report:

```text
Execution status: BLOCKED
Recommended next action: refine the plan with implementation-plan
```

## Verification rules

- Run the smallest focused check that proves the changed objective.
- Distinguish pre-existing failures from failures introduced by the execution.
- Do not claim a command passed unless it was run and its result was inspected.
- A newly introduced verification failure is an invalidating failure: mark the affected step `blocked`, stop dependent work, and set `Execution status: BLOCKED`.
- Do not mark the overall execution `IMPLEMENTED` when required verification failed or was skipped without plan authorization.
- Stop when a verification failure invalidates the plan assumption or makes subsequent steps unsafe.
- Final integration checks must be proportionate to the affected boundaries.

## External-write boundary

Repository edits are allowed within the approved plan. Commits, pushes, pull requests, releases, deployments, production migrations, databases, and other external systems require explicit authorization from the user or an explicit approved plan step.

Never self-approve, merge, or make a merge-readiness decision. That belongs to `code-review`.

## Final status

Set `Execution status` to exactly one of:

- `IMPLEMENTED`: Every required step is completed and required verification passed.
- `PARTIAL`: Safe progress was completed, but remaining work is deferred, unfinished, or limited only by a non-invalidating constraint.
- `BLOCKED`: A material deviation, unsafe state, missing decision, missing authorization, ambiguous dirty-work ownership, or invalidating verification failure prevents safe continuation.

## Output format

Use this structure:

1. `Execution mode`
2. `Execution baseline`
3. `Plan source and eligibility`
4. `Requirements and invariants`
5. `Repository reconciliation`
6. `Plan-conformance ledger`
7. `Deviations`
8. `Final integration verification`
9. `Handoff`
10. `Execution status: IMPLEMENTED|PARTIAL|BLOCKED`

## Guardrails

- No opportunistic refactors or nearby defect fixes.
- No widening scope beyond the approved plan.
- No overwriting unrelated dirty or untracked work.
- No overwriting or silently absorbing pre-existing hunks in plan-owned files.
- No editing generated artifacts instead of their canonical source.
- No claiming verification passed unless it was run.
- No continuing after a material plan assumption is disproven.
- No destructive migration, production change, release, or external write without explicit authorization.
- No self-approval or merge-readiness decision.
- No repeated fix-and-review loop after findings are known; use `iterative-self-review`.

## Completion conditions

This skill is complete when one of these is true:

- All required plan steps are completed with recorded verification and the diff is handed to `code-review`.
- Safe partial progress is recorded and remaining work is explicit.
- A material deviation or blocker is reported with the required next action.
