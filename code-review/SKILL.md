---
name: code-review
description: Use when the user asks to review code, a PR, branch diff, current changes, merge readiness, repository risks, targeted files, CI/tooling changes, or stale review comments. Produces a read-only, evidence-backed review with coverage matrix, severity-ranked finding ledger, and APPROVE/COMMENT/REQUEST_CHANGES decision. If the user asks for fixes, first emit the ledger, then explicitly hand remediation to iterative-self-review.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.1.0'
  allow_implicit_invocation: 'true'
---

# Code Review

## Non-negotiable boundary

This skill is read-only. Inspect files, diffs, commands, logs, and comments, but do not mutate source files, configs, generated artifacts, branches, issues, or PR state. If the user asks to fix problems, complete this review first, emit a finding/issue ledger, and then say that remediation must continue with `iterative-self-review`.

## Scope modes

Choose exactly one primary mode and state it in the output.

- `diff review`: Review a PR, branch, commit range, staged changes, or working-tree diff.
- `targeted audit`: Review named files, components, concerns, commands, or review comments.
- `repository audit`: Review a repository or package area for broad risk; sample deliberately and report limits.
- `review-comment triage`: Decide whether review comments still apply to current code before recommending action.

## Required workflow

1. Establish scope, base, intent, and requested concerns.
2. Inspect the relevant diff/files/configs/tests before judging. For stale comments, inspect the current target line and surrounding code.
3. Load references only when needed:
   - `references/review-quality-checklist.md` for final decision integrity.
   - `references/maintainability-and-solid-checklist.md` for cohesion, dependency, complexity, or design concerns.
   - `references/repository-review-profiles.md` for applicability-driven concern coverage.
   - `references/architecture-impact-checklist.md` for contracts, schema, auth, dependency, release, or rollout impact.
   - `references/evaluation-playbook.md` only when evaluating this skill.
4. Build a coverage matrix for every requested concern and any profile concern that materially applies.
5. Write findings as a ledger with stable IDs.
6. Decide `APPROVE`, `COMMENT`, or `REQUEST_CHANGES` using the decision rules below.

## Coverage matrix

Every review must include a matrix with these columns:

- `Concern`: requested or applicable concern.
- `Status`: `reviewed`, `partial`, `not applicable`, or `blocked`.
- `Inspected paths/config`: concrete files, directories, config names, commands, or comment anchors.
- `Commands/evidence`: commands run, artifacts read, or source evidence.
- `Limitation`: remaining uncertainty; write `none` only when there is no meaningful limitation.

Set `Review completeness` to:

- `COMPLETE` when all requested/applicable concerns are reviewed or not applicable with evidence.
- `PARTIAL` when some relevant context is missing, truncated, sampled, or uninspected but a useful review is still possible.
- `BLOCKED` when missing access/context prevents a responsible decision.

Truncated, missing, sampled, or uninspected required context cannot receive `APPROVE` until resolved.

## Finding ledger

Use one ID per actionable finding, for example `CR-P1-001`. Each finding must include:

- `ID` and `severity` (`P0`, `P1`, `P2`, or `P3`).
- `Location`: file and line or the nearest stable anchor.
- `Evidence`: concrete code, behavior, command output, or current-vs-stale comment proof.
- `Impact`: why it matters.
- `Remediation`: smallest safe fix direction.
- `Verification`: how to prove the fix.

Severity:

- `P0`: critical security, data loss, outage, or corruption risk.
- `P1`: likely bug, broken requirement, major regression, or serious release risk.
- `P2`: maintainability, accessibility, performance, or design issue worth fixing in this cycle.
- `P3`: minor clarity, docs, naming, or follow-up suggestion.

## Decision rules

- Any `P0` or `P1` finding -> `REQUEST_CHANGES`.
- Complete review with one or more `P2` findings and no `P0`/`P1` findings -> `COMMENT`, even when `P3` findings are also present.
- Complete review with only `P3` findings or no actionable findings -> `APPROVE`.
- Partial or blocked review without `P0`/`P1` -> `COMMENT`.
- Never `APPROVE` when review completeness is `PARTIAL` or `BLOCKED`.

## Output format

Use this structure:

1. `Scope mode`
2. `Review completeness: COMPLETE|PARTIAL|BLOCKED`
3. `Coverage matrix`
4. `Findings`
   - Say `No actionable findings` only after showing evidence in the coverage matrix.
5. `Decision: APPROVE|COMMENT|REQUEST_CHANGES`
6. `Hand-off for fixes`
   - Include only when the user asked for remediation: restate the ledger and instruct `iterative-self-review` to fix by ID/severity.

## Guardrails

- Keep reviews evidence-backed and concise; do not block on pure preference.
- Treat SOLID as a practical cohesion/dependency lens, not a reason to invent abstractions.
- Preserve exact contracts, public behavior, copy, migrations, and API shapes unless the review is explicitly about changing them.
- Surface uncertainty honestly; sampled repository audits must say what was and was not inspected.
- Do not claim tests passed unless you ran or inspected the relevant evidence.
