---
name: implementation-plan
description: Use when the user asks to create, review, refine, scope, or sequence an implementation plan for a concrete feature, known bug fix, refactor, migration, dependency/toolchain change, or other codebase change before editing. Produces a read-only, evidence-backed, implementation-ready plan grounded in the current repository, with affected boundaries, ordered file-level steps, verification, risks, and READY_TO_IMPLEMENT/READY_WITH_ASSUMPTIONS/NOT_READY status. Do not use for direct implementation, code review or merge decisions, root-cause-only debugging, or post-review remediation unless the user explicitly asks for a plan.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.0.1'
  allow_implicit_invocation: 'true'
---

# Implementation Plan

## Non-negotiable boundary

This skill is read-only. Inspect repository state, files, diffs, configs, tests, documentation, generated-source relationships, and history when useful, but do not mutate source files, configs, generated artifacts, lockfiles, branches, issues, PR state, databases, or external systems.

Prefer non-mutating inspection commands. Do not install dependencies, run migrations, invoke formatters/fixers in write mode, run code generation, or execute commands known to rewrite repository state. If a command may create disposable caches or reports, skip it unless the evidence is necessary and the command is safe for the current environment.

If the user asks to plan and then implement, complete and emit the plan first. Any implementation must happen after the planning output and outside this skill.

## Activation boundary

Use this skill when the requested artifact is an implementation plan or when the user explicitly wants repository investigation before editing. Typical triggers include:

- Plan how to implement a feature or behavior change.
- Scope a refactor before changing code.
- Plan a schema, API, dependency, framework, toolchain, or CI migration.
- Review or tighten an existing implementation plan against the current repository.
- Plan a fix for a defect whose expected behavior and root cause are sufficiently established.

Do not activate for:

- Direct implementation requests with no planning request.
- Code, PR, diff, or merge-readiness review; use `code-review` for that workflow.
- Root-cause investigation when the user primarily wants debugging rather than a change plan.
- Fixing a `code-review` ledger or repeated remediation loop; use `iterative-self-review` for that workflow.
- Generic technology explanation or architecture brainstorming that is not tied to a concrete codebase change.

When intent overlaps, follow the requested artifact: a requested plan uses this skill; a requested review decision uses `code-review`; a requested ledger remediation uses `iterative-self-review`.

## Scope modes

Choose exactly one primary mode and state it in the output.

- `change plan`: Feature, known bug fix, behavior, configuration, or localized implementation work.
- `refactor plan`: Structural improvement where observable behavior and external contracts should remain stable unless explicitly stated otherwise.
- `migration plan`: Schema, API, dependency, framework, toolchain, CI, deployment, or other staged compatibility-sensitive change.
- `plan refinement`: Validate and improve a user-provided plan against repository evidence without implementing it.

## Required workflow

1. Establish the requested outcome, user constraints, acceptance criteria, and explicitly excluded work. Do not invent broader goals.
2. Establish the planning baseline. Inspect the current branch/working state when available and distinguish existing partial implementation from work that is only proposed.
3. Trace the current implementation far enough to explain how the affected behavior works today. Inspect relevant entry points, callers, data/contracts, side effects, tests, configs, and documentation rather than planning from filenames alone.
4. Load references only when needed:
   - `references/planning-quality-checklist.md` before finalizing the plan.
   - `references/repository-planning-profiles.md` to identify materially affected boundaries and verification concerns.
   - `references/evaluation-playbook.md` only when evaluating this skill.
5. Record current-state findings with concrete repository evidence. Distinguish observed facts, reasonable inferences, and assumptions.
6. Convert the request into explicit requirements and invariants. Preserve public APIs, serialized fields, behavior, accessibility, data integrity, generated-source ownership, and release contracts unless the user explicitly asks to change them.
7. Resolve uncertainties by inspection before adding assumptions. Do not interrupt for minor ambiguity; state a narrow assumption. If a material product, contract, security, data, or rollout decision cannot be resolved safely, surface it and lower planning completeness/readiness.
8. Build the smallest coherent ordered implementation plan. Each step must satisfy the step contract below and must not opportunistically include unrelated cleanup.
9. Build a verification plan mapped to the changed behavior and affected boundaries. Prefer behavioral confidence over raw coverage targets.
10. Assign planning completeness and readiness using the rules below, run the planning quality checklist, and stop before implementation.

## Evidence and scope discipline

- Ground claims about the current implementation in inspected paths, symbols, configs, tests, commands, or documentation.
- Do not claim repository-wide understanding when only a snapshot, subset, or sampled area was inspected.
- Do not invent exact file paths, symbols, schemas, or commands when repository evidence does not establish them. Use a clearly labeled path-to-locate or assumption instead.
- Follow callers and dependencies far enough to identify compatibility or ordering constraints, but stop when additional traversal no longer changes the plan materially.
- Distinguish canonical source files from generated artifacts. Plan changes at the source of truth and describe regeneration/verification separately.
- Preserve unrelated existing dirty work. Do not plan cleanup of pre-existing changes unless the user includes it in scope.

## Planning completeness

Set `Planning completeness` to exactly one of:

- `COMPLETE`: The material affected paths, contracts, dependencies, tests, and rollout concerns needed for this requested plan were inspected or were shown to be not applicable. There is no unresolved material unknown that changes the implementation sequence.
- `PARTIAL`: A useful plan is possible, but relevant context is missing, sampled, ambiguous, or unavailable. State exactly what is missing and which steps it affects.
- `BLOCKED`: Missing access or an unresolved requirement/contract prevents a safe implementation sequence from being produced. State the blocker and what evidence or decision would unblock planning.

`COMPLETE` applies only to the requested planning scope; it never means the whole repository was inspected.

## Implementation step contract

Every numbered implementation step must include:

- `Objective`: the concrete outcome of the step.
- `Paths / anchors`: inspected files, directories, symbols, config keys, schemas, or stable locations to change. When exact paths are not evidenced, say what must be located rather than inventing one.
- `Change`: what should be added, removed, moved, preserved, or rewired. Describe behavior and structure, not a code patch.
- `Dependencies / ordering`: prerequisites and why this step comes at this point. Write `none` when there is no meaningful dependency.
- `Invariants`: contracts or behavior that must remain true while performing this step.
- `Verification`: the focused test, typecheck, build, inspection, migration check, or manual behavior that proves this step is correct.

A step is not implementation-ready if it only says things such as “update the service,” “add tests,” or “modify relevant files” without repository anchors and behavioral intent.

## Verification plan

The final verification section must cover the smallest set of checks that establishes confidence in the requested change. Include applicable layers such as:

- focused unit/component tests for changed behavior and boundaries;
- integration or contract tests across affected packages/services;
- typecheck/lint/build when configuration, types, exports, or generated artifacts are affected;
- accessibility behavior for interactive frontend changes;
- migration/backfill/rollback or old/new version compatibility for data and deployment changes;
- smoke/manual checks only where automated evidence is insufficient.

Do not prescribe commands that the repository does not appear to provide. When command names are uncertain, name the verification goal and identify the script/config that must be confirmed before implementation.

## Readiness rules

Set `Readiness` to exactly one of:

- `READY_TO_IMPLEMENT`: Planning completeness is `COMPLETE`, the ordered plan is actionable, and there is no unresolved material decision or assumption.
- `READY_WITH_ASSUMPTIONS`: The plan is useful but has explicit low-risk, reversible assumptions or limited missing context. Planning completeness must be `PARTIAL`; list every assumption that implementation must validate.
- `NOT_READY`: Planning is `BLOCKED`, or a `PARTIAL` plan still depends on a material product, contract, security, data, compatibility, or rollout decision that should not be guessed.

Never use `READY_TO_IMPLEMENT` when planning completeness is `PARTIAL` or `BLOCKED`.

## Output format

Use this structure:

1. `Scope mode`
2. `Planning completeness: COMPLETE|PARTIAL|BLOCKED`
3. `Goal and constraints`
4. `Current-state findings`
   - concise evidence-backed description of how the relevant implementation works today;
   - include important observed paths/symbols and explicitly label material inference/assumption.
5. `Affected boundaries`
   - name only boundaries that materially affect the plan and why.
6. `Requirements and invariants`
7. `Implementation plan`
   - ordered numbered steps using the implementation step contract.
8. `Verification plan`
9. `Risks, assumptions, and open questions`
   - say `none` only when there are no material items.
10. `Readiness: READY_TO_IMPLEMENT|READY_WITH_ASSUMPTIONS|NOT_READY`

## Guardrails

- Prefer the smallest design that satisfies the requested change; do not introduce patterns, layers, factories, interfaces, or dependencies without demonstrated need.
- Preserve exact public contracts and user-visible behavior unless the request explicitly changes them.
- In refactor plans, state behavioral invariants before structural changes and keep compatibility-preserving steps separate from optional cleanup.
- In migration plans, explicitly address old/new version coexistence, data transition, ordering, rollback, and irreversible steps when applicable.
- For security/auth/privacy boundaries, identify enforcement points and verification rather than assuming surrounding layers make the change safe.
- For frontend work, account for loading/error/empty states, accessibility, routing/state contracts, and server/client boundaries when materially affected.
- For monorepos/toolchains, account for package boundaries, generated outputs, task graphs, cache behavior, and publication/build contracts when materially affected.
- Do not turn the plan into implementation code or a pseudo-diff. Small identifiers or signatures may be named when they are necessary to make a step precise.
- Do not claim tests, builds, migrations, or commands passed unless that evidence was actually inspected or run.

## Completion conditions

This skill is complete only when all of the following are true for the requested scope:

- The scope mode and planning completeness are stated.
- The current implementation has been investigated enough to support the plan, or the missing context is explicitly reflected in `PARTIAL`/`BLOCKED`.
- Material requirements and invariants are explicit.
- Every implementation step is ordered, anchored, behaviorally specific, and has verification.
- Cross-boundary compatibility, migration, or rollout concerns are included when applicable.
- Risks, assumptions, and open questions are explicit.
- Readiness follows the readiness rules.
- No repository or external-system mutation was performed by this skill.
