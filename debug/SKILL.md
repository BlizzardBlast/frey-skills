---
name: debug
description: Use when the user asks to investigate, diagnose, troubleshoot, reproduce, or determine the root cause of a concrete failure, regression, flaky behavior, failing test, production incident, or environment-specific defect before editing. Produces a read-only, evidence-backed investigation with reproduction status, execution/data-flow trace, hypothesis ledger, contributing factors, and CONFIRMED/LIKELY/UNRESOLVED/NOT_A_DEFECT root-cause status. Do not use for direct implementation, implementation planning when the root cause is already established, code review or merge decisions, or remediation of an existing issue ledger.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.0.0'
  allow_implicit_invocation: 'true'
---

# Debug

## Non-negotiable boundary

This skill is read-only. Investigate and establish causality, but do not edit source files, configs, generated artifacts, lockfiles, branches, issues, PR state, databases, deployed environments, or external systems.

Prefer safe, non-mutating diagnostic commands. Do not install dependencies, change configuration, clear shared caches, run migrations, restart services, or apply speculative fixes merely to see whether the symptom disappears. Commands that may create disposable local caches or reports are allowed only when necessary, understood, and isolated from meaningful repository or external state.

If the user asks to diagnose and then fix, complete and emit the investigation first. Any implementation must happen after the debugging output and outside this skill.

## Activation boundary

Use this skill when the requested artifact is a diagnosis or root-cause investigation tied to a concrete codebase or system symptom. Typical triggers include:

- Investigate a deterministic error, crash, incorrect result, or failing test.
- Find the cause of a regression between versions, branches, commits, or environments.
- Diagnose flaky, timing-dependent, race-related, or nondeterministic behavior.
- Analyze logs, traces, telemetry, incidents, or production-only failures.
- Determine whether observed behavior is a repository defect, configuration issue, external dependency failure, or expected behavior.

Do not activate for:

- Direct implementation requests with no investigation request.
- Implementation planning when expected behavior and root cause are already sufficiently established; use `implementation-plan`.
- Code, PR, diff, or merge-readiness review; use `code-review`.
- Fixing a provided review/issue ledger or repeated remediation loop; use `iterative-self-review`.
- Generic explanations, broad repository audits, or speculative architecture discussion without a concrete symptom.

When intent overlaps, follow the requested artifact: diagnosis uses this skill; a requested plan uses `implementation-plan`; a requested review decision uses `code-review`; a requested ledger remediation uses `iterative-self-review`.

## Investigation modes

Choose exactly one primary mode and state it in the output.

- `failure investigation`: Deterministic error, exception, crash, incorrect output, or failing test.
- `regression investigation`: Behavior differs across versions, branches, commits, deployments, or environments.
- `flaky investigation`: Intermittent, timing-dependent, order-dependent, race-related, or nondeterministic behavior.
- `production investigation`: Logs, telemetry, incidents, production-only behavior, or incomplete reproduction access.

## Required workflow

1. Establish the exact symptom, expected behavior, environment, frequency, first known occurrence, and available reproduction.
2. Establish the investigation baseline: current branch/working state, relevant version/configuration, supplied logs, and known-good comparison when available.
3. Reproduce the symptom using the smallest safe non-mutating path. If reproduction is unavailable, characterize the evidence and state that limitation explicitly.
4. Capture observations before proposing causes. Separate observed facts, inferences, assumptions, and user-reported claims.
5. Trace the relevant execution, data, configuration, dependency, or lifecycle path far enough to identify the earliest meaningful divergence.
6. Build a hypothesis ledger with plausible competing explanations. Do not anchor on the first suspicious line, component, or recent change.
7. Run discriminating checks that can support or reject hypotheses. Prefer checks that distinguish between multiple plausible causes.
8. Update every hypothesis explicitly as `OPEN`, `SUPPORTED`, `CONFIRMED`, `REJECTED`, or `BLOCKED`; do not silently discard alternatives.
9. Identify the root cause and contributing factors. The final exception or failed assertion is not automatically the root cause.
10. Assign investigation completeness and root-cause status using the rules below, run `references/debugging-quality-checklist.md`, and stop before implementation.

## Evidence discipline

- Ground claims in inspected code, configs, tests, logs, traces, commands, documentation, version history, or reproducible behavior.
- Do not claim reproduction when only a fixture, log excerpt, or user report was inspected.
- Do not claim causation from timing, correlation, recency, or suspicion alone.
- Do not fabricate paths, symbols, commands, environment values, requests, logs, or test results.
- Treat missing credentials, external-service access, production telemetry, data samples, or environment parity as investigation limits.
- Follow the causal chain to the earliest divergence that explains the symptom; distinguish root cause from trigger, propagation, and final failure.
- Stop traversing when additional inspection no longer changes the hypothesis ranking or recommended next action materially.

## Hypothesis ledger

Use stable IDs such as `DBG-H1`. Every material hypothesis must include:

- `Hypothesis`: the proposed causal explanation.
- `Supporting evidence`: observations that increase confidence.
- `Contradicting evidence`: observations that weaken or disprove it; write `none observed` only when accurate.
- `Discriminating check`: the smallest safe check that distinguishes it from alternatives.
- `Status`: `OPEN`, `SUPPORTED`, `CONFIRMED`, `REJECTED`, or `BLOCKED`.

Status rules:

- `OPEN`: Plausible but not materially tested.
- `SUPPORTED`: Evidence favors it, but plausible alternatives or causal gaps remain.
- `CONFIRMED`: Evidence establishes the causal chain and sufficiently distinguishes it from plausible alternatives.
- `REJECTED`: Evidence contradicts the hypothesis or its predicted behavior.
- `BLOCKED`: A specific missing input, access boundary, or unsafe check prevents responsible evaluation.

At most one materially competing hypothesis should normally be `CONFIRMED`. When several conditions are jointly necessary, describe one causal chain and list the others as contributing factors.

## Investigation completeness

Set `Investigation completeness` to exactly one of:

- `COMPLETE`: The symptom was reproduced or sufficiently characterized, material paths and plausible alternatives were investigated, and the available evidence supports a responsible conclusion.
- `PARTIAL`: Useful evidence and a likely direction exist, but reproduction, environment parity, logs, access, or discriminating checks remain incomplete. State exactly what is missing.
- `BLOCKED`: Missing access, credentials, inputs, observability, or a safe reproduction path prevents a responsible diagnosis. State what would unblock it.

`COMPLETE` applies only to the requested symptom and evidence scope; it never means the whole repository or system was investigated.

## Root-cause status

Set `Root-cause status` to exactly one of:

- `CONFIRMED`: The causal chain is established by discriminating evidence and plausible alternatives are rejected or made immaterial. Requires `COMPLETE` investigation.
- `LIKELY`: Evidence favors one explanation, but material confirmation remains. Requires `PARTIAL` investigation.
- `UNRESOLVED`: Available evidence does not justify a single likely cause, or investigation is blocked.
- `NOT_A_DEFECT`: Evidence shows the observed behavior matches the documented/required contract or originates outside the investigated repository boundary. Requires `COMPLETE` investigation and must still explain the observed symptom.

Never use `CONFIRMED` when investigation completeness is `PARTIAL` or `BLOCKED`.

## Output format

Use this structure:

1. `Investigation mode`
2. `Investigation completeness: COMPLETE|PARTIAL|BLOCKED`
3. `Symptom and expected behavior`
4. `Baseline and reproduction`
5. `Evidence collected`
6. `Execution / data-flow trace`
7. `Hypothesis ledger`
8. `Root cause`
9. `Contributing factors`
10. `Recommended next action`
11. `Verification needed after a fix`
12. `Root-cause status: CONFIRMED|LIKELY|UNRESOLVED|NOT_A_DEFECT`

## Handoff rules

- Confirmed root cause plus a requested implementation plan -> hand off to `implementation-plan` with the causal evidence and preserved invariants.
- Confirmed root cause plus a direct fix request -> stop this skill after the investigation; implementation continues outside `debug`.
- Existing review/issue ledger already identifies the defect and remediation -> use `iterative-self-review`, not `debug`.
- Request to judge a proposed change or merge readiness -> use `code-review`, not `debug`.

## Guardrails

- Do not change the system being diagnosed to manufacture confirmation.
- Do not apply multiple speculative fixes at once.
- Do not treat a passing rerun as proof that a flaky problem is resolved or understood.
- Do not blame environment, configuration, concurrency, caching, or an external service without evidence.
- Do not erase rejected hypotheses; preserving them prevents repeated investigation loops.
- Do not broaden one symptom into a general code-quality audit.
- For security or privacy incidents, avoid exposing secrets or sensitive data in commands, logs, or output.
- For production investigations, distinguish observed production evidence from local reproduction and state telemetry gaps honestly.
- Do not claim commands, tests, traces, or reproductions succeeded unless they were actually run or inspected.

## Completion conditions

This skill is complete only when:

- The investigation mode and completeness are stated.
- The symptom, expected behavior, baseline, and reproduction status are explicit.
- Evidence is separated from inference and assumption.
- Material competing hypotheses are tracked with explicit statuses.
- The causal conclusion and contributing factors match the evidence.
- Missing access or evidence is reflected in `PARTIAL`/`BLOCKED` and root-cause status.
- The next workflow and post-fix verification are clear.
- No repository or external-system mutation was performed by this skill.
