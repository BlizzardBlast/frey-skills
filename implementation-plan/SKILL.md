---
name: implementation-plan
description: Use when the user asks to create, review, refine, scope, or sequence an implementation plan for a concrete codebase change before editing. Produces a read-only repository-grounded plan with affected boundaries, ordered anchored steps, verification, risks, completeness, and READY_TO_IMPLEMENT/READY_WITH_ASSUMPTIONS/NOT_READY status. Do not use for direct implementation, diagnosis, review decisions, execution, or ledger remediation.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.1.0'
  allow_implicit_invocation: 'true'
---

# Implementation Plan

## Boundary and routing

This skill is read-only. Inspect safely; do not edit files, install dependencies, run mutating tools, or change external systems. For plan-then-implement requests, emit the plan first; implementation occurs outside this skill.

Choose one mode:

- `change plan`: feature, known fix, behavior, or configuration.
- `refactor plan`: structural change preserving observable contracts.
- `migration plan`: schema, API, dependency, framework, toolchain, CI, or rollout.
- `plan refinement`: validate and tighten a supplied plan.

Route diagnosis to `debug`, direct execution of an approved plan to `implementation-execution`, merge review to `code-review`, testing strategy to `test-strategy`, and ledger remediation to `iterative-self-review`.

## Workflow

1. Establish outcome, constraints, acceptance criteria, and exclusions.
2. Capture the available branch/working-state baseline and distinguish existing work from proposed work.
3. Trace relevant entry points, callers, contracts, data, side effects, tests, configs, docs, and generated-source ownership until further traversal would not change the plan.
4. Load only needed references:
   - `references/repository-planning-profiles.md` for affected boundaries.
   - `references/planning-quality-checklist.md` before finalizing.
   - `references/evaluation-playbook.md` only when evaluating this skill.
5. Record observed facts, inferences, assumptions, and missing context separately.
6. Define requirements and invariants; preserve public APIs, serialized fields, behavior, accessibility, data integrity, and release contracts unless explicitly changed.
7. Resolve uncertainty by inspection. Use narrow reversible assumptions only; material unknowns lower completeness/readiness.
8. Produce the smallest ordered plan and mapped verification. Stop before implementation.

## Completeness and readiness

`Planning completeness`:

- `COMPLETE`: material paths, contracts, dependencies, tests, and rollout concerns for this scope are known or evidenced not applicable.
- `PARTIAL`: a useful plan exists, but relevant context is missing, sampled, or ambiguous; identify affected steps.
- `BLOCKED`: missing access or a material unresolved decision prevents a safe sequence.

`Readiness`:

- `READY_TO_IMPLEMENT`: only with `COMPLETE`, actionable steps, and no material unknown.
- `READY_WITH_ASSUMPTIONS`: only with `PARTIAL` and explicit low-risk reversible assumptions to validate.
- `NOT_READY`: `BLOCKED`, or `PARTIAL` with a material product, contract, security, data, compatibility, or rollout decision.

Never use `READY_TO_IMPLEMENT` with `PARTIAL` or `BLOCKED`.

## Step contract

Every numbered step includes:

- `Objective`
- `Paths / anchors` (inspected paths/symbols/configs; otherwise say what must be located)
- `Change` (behavior/structure, not a patch)
- `Dependencies / ordering`
- `Invariants`
- `Verification`

Reject vague steps such as “update the service” or invented paths/commands. Prefer focused behavioral, contract, accessibility, migration, build/type, and rollout checks only where evidenced.

## Output

1. `Scope mode`
2. `Planning completeness: COMPLETE|PARTIAL|BLOCKED`
3. `Goal and constraints`
4. `Current-state findings`
5. `Affected boundaries`
6. `Requirements and invariants`
7. `Implementation plan`
8. `Verification plan`
9. `Risks, assumptions, and open questions`
10. `Readiness: READY_TO_IMPLEMENT|READY_WITH_ASSUMPTIONS|NOT_READY`

Keep scope minimal, preserve unrelated dirty work, change canonical sources rather than generated artifacts, and never claim unrun checks passed.
