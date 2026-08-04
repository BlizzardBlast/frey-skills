---
name: test-strategy
description: Use when the user asks to design, review, refine, or assess a risk-based testing strategy for a concrete feature, defect, migration, diff, release, or system boundary. Produces a read-only, repository-grounded strategy covering risks, contracts, test layers, scenarios, data, environments, execution order, entry and exit criteria, residual risk, and test readiness. Do not use for implementing tests, executing verification, debugging root causes, creating a general implementation plan, reviewing merge readiness, or release readiness beyond testing concerns.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.0.0'
  allow_implicit_invocation: 'true'
---

# Test Strategy

## Non-negotiable boundary

This skill is read-only. Inspect source, tests, diffs, schemas, configuration, CI, environments, observability, incidents, and documentation, but do not edit files, implement tests, install dependencies, mutate test data, deploy, run migrations, or change external systems.

Do not claim a test, command, environment, or coverage result unless the evidence was actually inspected. Do not turn the strategy into code, a patch, or an executable implementation plan.

## Activation boundary

Use this skill when the requested primary artifact is a testing strategy, test plan, regression plan, migration test plan, release test plan, risk-based coverage plan, or test-readiness assessment tied to a concrete repository change or system boundary.

Do not activate for:

- Implementing tests or production code.
- Running tests or verification commands as the primary task.
- Debugging an unknown root cause; use `debug`.
- Creating a general implementation plan; use `implementation-plan`.
- Executing an approved implementation plan; use `implementation-execution`.
- Reviewing a diff or deciding merge readiness; use `code-review`.
- Fixing an existing issue ledger; use `iterative-self-review`.
- General release readiness beyond testing concerns.
- Generic explanations of testing concepts without a concrete strategy artifact.

When intent overlaps, follow the requested artifact. A normal implementation plan may include focused verification; a dedicated risk matrix, scenario catalogue, data/environment plan, and readiness assessment belong here.

## Scope modes

Choose exactly one primary mode and state it in the output.

- `change test strategy`: Feature, localized behavior change, known defect fix, configuration change, or concrete diff.
- `regression test strategy`: Protect established behavior after a defect, refactor, incident, dependency change, or repeated regression.
- `migration test strategy`: Schema, API, event, dependency, framework, infrastructure, or compatibility-sensitive migration.
- `release test strategy`: Testing concerns for a release candidate, staged rollout, deployment, or production promotion.

Release mode covers testing only. It must not make the broader business, operational, compliance, or deployment go/no-go decision.

## Required workflow

1. Establish the testing objective, requested scope, exclusions, target decision, and available evidence.
2. Establish the baseline: changed behavior or paths, existing tests and tooling, environments, data, incidents, and missing context.
3. Trace relevant entry points, callers, contracts, state transitions, persistence, external dependencies, security boundaries, failure paths, and recovery behavior.
4. Load references only when needed:
   - `references/repository-testing-profiles.md` for applicable repository risks and layers.
   - `references/risk-and-scenario-rules.md` for prioritization and traceability.
   - `references/strategy-quality-checklist.md` before finalizing.
5. Build a prioritized risk inventory using repository evidence.
6. Allocate each material risk to the smallest appropriate test layer.
7. Build a scenario catalogue linked to risk IDs and observable contracts.
8. Identify test data, environment, tooling, service, and observability requirements.
9. Separate existing automated coverage, missing automated coverage, manual or exploratory coverage, and blocked checks.
10. Prioritize automation candidates by risk reduction, repeatability, determinism, and maintenance cost.
11. Define execution order, dependencies, entry criteria, and exit criteria.
12. Record residual risks, assumptions, and accepted gaps.
13. Assign strategy completeness and test readiness, run the quality checklist, and stop before implementation or execution.

## Evidence and scope discipline

- Ground current-state claims in inspected paths, symbols, configs, tests, contracts, commands, or documentation.
- Distinguish observed facts, reasonable inferences, assumptions, and unavailable context.
- Do not invent exact paths, commands, environments, traffic, defect frequency, data volume, or coverage percentages.
- Do not claim repository-wide completeness from a snapshot or sampled area.
- Prefer behavior and contract coverage over raw coverage targets.
- Stop adding scenarios when they no longer cover a distinct material risk, contract, boundary, state transition, or failure mode.

## Risk matrix contract

Use stable IDs such as `TS-RISK-001`. Each material risk must include:

- `Behavior or boundary`
- `Failure mode`
- `Impact`
- `Likelihood`: `high`, `medium`, `low`, or `unknown`
- `Change exposure`
- `Detectability`
- `Recovery`
- `Priority`: `critical`, `high`, `medium`, or `low`
- `Evidence`
- `Planned coverage`

Prioritize irreversible, security-sensitive, data-integrity, externally visible, compatibility-sensitive, and difficult-to-detect failures. Mark uncertain factors `unknown` instead of inventing precision.

## Test-layer allocation

Consider only materially applicable layers:

- static analysis, type checking, lint, or policy checks;
- unit, component, contract, integration, and end-to-end tests;
- migration and data verification;
- accessibility and security verification;
- performance, load, resilience, and concurrency checks;
- smoke, exploratory, and observability-based production verification.

For each allocation, state which risk or contract it covers, why the layer is appropriate, what remains outside that layer, required dependencies, and whether coverage is existing or proposed. Do not force every risk through every layer.

## Scenario catalogue contract

Use stable IDs such as `TS-SCENARIO-001`. Each scenario must include:

- `Covered risks`
- `Contract or behavior`
- `Preconditions`
- `Test data`
- `Action`
- `Expected result`
- `Test layer`
- `Environment`
- `Automation status`: `existing`, `candidate`, `manual`, `blocked`, or `not recommended`
- `Priority`
- `Evidence or gap`

Favor boundaries, invalid input, state transitions, partial failure, retries, timeouts, concurrency, idempotency, permissions, compatibility, accessibility, recovery, rollback, and failure observability when applicable. Avoid an unprioritized exhaustive checklist.

## Strategy completeness

Set `Strategy completeness` to exactly one of:

- `COMPLETE`: Material behavior, contracts, risks, existing coverage, major gaps, data, and environment dependencies for the requested scope are understood. No unresolved material unknown changes the strategy.
- `PARTIAL`: A useful strategy is possible, but relevant code, contract, environment, data, test, or rollout context is missing or sampled. State what is missing and which sections it affects.
- `BLOCKED`: Expected behavior, a material contract, or required access is unresolved enough that correct outcomes cannot be defined safely.

`COMPLETE` applies only to the requested scope, never the whole repository.

## Test readiness

Set `Test readiness` to exactly one of:

- `READY`: Strategy completeness is `COMPLETE`, required scenarios are actionable, critical data and environments are available or have an established provisioning path, and no material correctness criterion is unresolved.
- `READY_WITH_GAPS`: Strategy completeness is `PARTIAL`, the highest-priority testing remains actionable, and every gap and residual risk is explicit.
- `NOT_READY`: Strategy completeness is `BLOCKED`, or a material correctness, data, environment, security, compatibility, or release-testing condition cannot safely be tested yet.

Never use `READY` with `PARTIAL` or `BLOCKED` completeness.

## Handoffs

- Hand repository-level implementation work to `implementation-plan`.
- A test strategy alone does not satisfy the executable-plan gate for `implementation-execution`.
- Test implementation requires an approved plan mapping strategy risks and scenarios to repository paths, steps, invariants, and verification.
- `code-review` may use an existing strategy to assess test sufficiency, but this skill does not decide merge readiness.
- For a confirmed defect, `debug` may hand regression-design work here.

## Output format

Use this structure:

1. `Scope mode`
2. `Test objective and scope`
3. `Risk matrix`
4. `Behavior and contract inventory`
5. `Test-layer allocation`
6. `Scenario catalogue`
7. `Test data and environment requirements`
8. `Automation candidates`
9. `Execution order`
10. `Entry and exit criteria`
11. `Residual risk`
12. `Strategy completeness: COMPLETE|PARTIAL|BLOCKED`
13. `Test readiness: READY|READY_WITH_GAPS|NOT_READY`

## Guardrails

- Keep the strategy risk-based, evidence-backed, and proportionate.
- Do not use coverage percentage as a substitute for behavior coverage.
- Do not require a formal strategy for every low-risk change.
- Do not implement tests, edit CI, or execute the proposed strategy.
- Do not hide an unresolved root cause behind speculative regression cases.
- Do not broaden release mode into general release readiness.
- Do not prescribe repository commands that were not evidenced.

## Completion conditions

This skill is complete only when:

- The scope mode is stated.
- Material risks and observable contracts are traceable to prioritized scenarios.
- Applicable test layers, data, environments, automation candidates, and execution order are explicit.
- Entry and exit criteria and residual risks are stated.
- Completeness and readiness follow their rules.
- Missing context and blocked checks are honest.
- No repository or external-system mutation was performed.
