# Repository Testing Profiles

Use these profiles to decide which risks, layers, data, environments, and residual concerns materially apply. Include only relevant concerns and mark missing evidence explicitly.

## Frontend and accessibility

Inspect component ownership, state/query/route contracts, forms, loading/error/empty states, hydration, browser APIs, and generated routes.

Consider:

- semantic controls, keyboard flow, focus, labels, ARIA, and screen-reader-visible feedback;
- client/server validation consistency;
- optimistic updates, retry, stale cache, and cancellation behavior;
- responsive and browser-specific boundaries;
- component or integration tests for observable behavior rather than implementation detail.

## Backend and APIs

Inspect request/response validation, authn/authz, tenancy, idempotency, pagination, error semantics, retries, timeouts, cancellation, and downstream dependencies.

Consider contract tests, service integration tests, permission matrices, partial failure, duplicate requests, rate limits, and observability without secret or PII leakage.

## Databases and migrations

Inspect schemas, constraints, defaults, indexes, backfills, retained data, transactions, rollout ordering, and old/new application coexistence.

Consider representative historical data, null and enum transitions, idempotent and resumable backfills, lock behavior, rollback limits, compatibility matrices, and post-migration data verification.

## Monorepos and toolchains

Inspect workspace boundaries, package exports, generated artifacts, path aliases, task graphs, cache inputs/outputs, lockfiles, supported runtimes, and publication contracts.

Consider focused package tests, cross-package contract tests, build reproducibility, code generation parity, cache invalidation, and installation from a clean environment.

## CI and release pipelines

Inspect required checks, artifact identity, environment scoping, permissions, secrets, reports, feature flags, deployment order, smoke checks, and rollback paths.

Consider failure-path tests for skipped or flaky checks, artifact promotion, environment-specific configuration, canary verification, and production-safe observability checks.

## Dependencies and framework upgrades

Inspect peer and runtime compatibility, removed or deprecated APIs, configuration changes, native bindings, install scripts, generated files, and bundle/runtime impact.

Consider clean-install verification, compatibility matrices, focused migrated-API tests, broader build/type confidence, and rollback or version pinning.

## Authentication, authorization, privacy, and sensitive data

Inspect every trust boundary, permission enforcement point, tenant isolation, data storage, logging, error handling, audit trails, and secret handling.

Consider positive and negative permission cases, confused-deputy paths, object-level authorization, sensitive-data redaction, and safe failure behavior.

## Jobs, queues, retries, and distributed systems

Inspect scheduling, ordering, deduplication, idempotency, retry policy, timeouts, cancellation, dead-letter handling, concurrency, and partial failure.

Consider duplicate delivery, out-of-order messages, worker restart, poison messages, retry exhaustion, race conditions, and recovery evidence.

## Git-backed published state and concurrent agents (conditional)

Use this profile **only** when the changed system actually publishes, reads, or synchronizes Git refs or treats Git history as authoritative application state. Ordinary Git usage in a project, routine PR review, or a monorepo alone does not trigger it. First inspect the existing Git implementation, tests, host and backend contract; distinguish local `update-ref` from remote push/fetch semantics. Do not assume all Git servers provide Pando's consistency model.

- **Same-ref updates:** identify the expected previous tip and the publisher's atomic compare-and-swap or lease check (such as `git update-ref <ref> <new> <old>` locally, or an appropriately constrained remote push). A stale competing writer must not silently overwrite another writer. Verify which outcomes are observable and which need reconciliation.
- **Independent refs and cross-ref reads:** allow independent branches to progress unless a documented cross-ref invariant needs coordination. This applies to read-only consumers as well as publishers. Do not infer a repository-wide point-in-time snapshot from individually observed refs; explicitly test any required multi-ref consistency rather than globally serializing all writers by default.
- **Publication and acknowledgment:** distinguish prepared Git objects, successfully published refs, confirmed rejection, and an uncertain outcome after a timeout or lost reply. A failed subprocess acknowledgment is not proof the ref update failed. Check the exact intended ref and commit where trusted observations permit; a ref that has moved *again* cannot by itself prove whether the original publication happened. Do not blindly retry a possibly successful write or claim certainty without evidence.
- **Fetch and recovery:** after an acknowledged publication, verify that a separate reader can fetch the intended tip **and every required reachable object** under the documented visibility contract. Include interrupted transfers, retry, or stale-cache cases only if those paths exist. Preserve independent changes and uncommitted local work during recovery.
- **Deterministic verification:** for material races, prefer disposable real-Git repositories, explicit scheduling barriers, and fault injection immediately before/after publication over sleeps or random stress alone. Keep unit tests for isolated rules; use bounded integration or protocol conformance checks where mocked operations cannot prove Git behavior. State which interleavings and backend guarantees were actually exercised.

| Case | Condition | Observable test-strategy decision |
| --- | --- | --- |
| `GIT-CASE-001` | Changed behavior neither reads nor writes Git refs and does not rely on Git history as application state | Use ordinary risk selection; do not add Git-specific scenarios |
| `GIT-CASE-002` | Two agents target one ref | A stale expected-OID update is rejected and earlier committed work survives |
| `GIT-CASE-003` | Independent refs change during a multi-ref read | Check documented consistency needs; do not assume a repository-wide snapshot |
| `GIT-CASE-004` | Publication acknowledgment is lost | Reconcile the intended ref/commit; an unresolved outcome must not prompt blind retry |
| `GIT-CASE-005` | A new ref is acknowledged before a reader fetches | Verify the intended tip and reachable objects from an independent reader |
| `GIT-CASE-006` | A read-only consumer combines refs that can advance independently | Test required cross-ref consistency and read-time interleavings even without writes by the consumer |

This is a **conditional test-design reference**, not a requirement to run Git commands, build a Git server, install OpenAI's Git fork, adopt Pando, add formal verification, or enable hosted CI. Model designs and production claims in [OpenAI's Pando article](https://openai.com/index/scaling-git-at-openai/) (2026-11-02) motivate failure modes, but are not evidence of this repository's performance or guarantees. Respect the parent skill's read-only and evidence/readiness boundaries.

## AI model-mediated application behavior (conditional)

Apply this profile **only when the system under test** makes behavior-affecting model calls, delegates actions to an AI agent, or relies on model-selected tools. Using a coding assistant to *write ordinary application code* does not activate this profile. Inspect the real entry points, provider settings, tool permissions, and tests before choosing relevant scenarios; do not assume live model access or a particular agent framework.

- **Independent outcome and grader integrity:** Freeze expected behavior outside the model's control; where applicable, verify the resulting artifact, observable state, and authorized side effects through trusted deterministic checks or qualified independent human review. An agent's success claim, generated test, or green self-reported log is not an independent oracle. Test plausible grader/fixture tampering or shortcut paths only in isolated, synthetic or authorized environments; if the agent can influence the only scorer, mark correctness unverified.
- **Untrusted inputs and authority:** If the workflow consumes repository content, retrieved pages, tool responses, or model-produced text, test relevant prompt injection, false tool output, scope escalation, unauthorized writes, and cross-user disclosure at the actual enforcement boundaries. Verify denied actions remain denied regardless of what the model says.
- **Failure and abstention:** For applicable integrations, cover malformed/empty responses, timeouts, provider errors, refusals, partial tool failures, and bounded retries. Verify conservative fallback or explicit uncertainty, accurate provenance, and observability without leaking prompts, credentials, or sensitive user material.
- **Matched efficiency comparisons:** Only when model, adapter, prompt, or harness configuration is the behavior being changed, define permitted representative and held-out tasks, pin snapshots, model/harness/tool configuration and budgets across arms, and independently judge pass/fail and critical failures. Measure complete-run retries, tool calls, token usage, elapsed time, and monetary cost **only where observable**. A provider's benchmark or fewer tokens alone cannot prove better outcomes, and unmatched harness/task results are not a fair comparison.

| Case | Condition | Observable test-strategy decision |
| --- | --- | --- |
| `AI-CASE-001` | Change has no runtime model or agent dependency | Use ordinary risk selection; do not add AI-agent-specific scenarios |
| `AI-CASE-002` | Agent claims success or passing tests | Independently inspect required artifacts, permitted effects and a trusted outcome oracle |
| `AI-CASE-003` | Agent can view or alter the grader, expected output or benchmark fixture | Isolate held-out scoring or mark independent correctness unverified |
| `AI-CASE-004` | Model, tool or retrieved content is untrusted input | Exercise applicable injection and unauthorized action boundaries |
| `AI-CASE-005` | Provider or model returns an error or invalid response | Verify conservative and observable failure handling without fabricated success |
| `AI-CASE-006` | Comparing a model, adapter or agent harness | Hold tasks and grants fixed; report independently verified quality and measured total work |

These are **conditional test-design decisions**, not permission to run model evaluations, modify graders, collect transcripts, contact providers, buy tokens, or create CI jobs. Preserve the parent skill's read-only scope and the repository's policy against requiring behavioral model evaluations as a merge gate. Use synthetic/public or specifically authorized data. If material outcome verification is unavailable, record the blocked or unverified scenario under existing readiness rules rather than asserting a pass. The [METR capability update](https://metr.org/blog/2026-11-20-q4-2026-capability-update/) motivates checking reward hacking; [Hugging Face harness-adapter research](https://huggingface.co/blog/harness-adapters-at-scale) motivates matched model/harness comparisons. Neither source establishes a result for the repository being assessed.

## Performance and resilience

Inspect latency-sensitive paths, resource limits, query plans, memory use, connection pools, backpressure, caching, and dependency failure.

Consider representative load, thresholds grounded in requirements, degradation behavior, timeout budgets, recovery, and observability. Do not invent performance targets.

## Observability and incident recovery

Inspect logs, metrics, traces, alerts, correlation identifiers, dashboards, runbooks, rollback, and data repair paths.

Consider whether failures are detectable, actionable, safely diagnosable, and recoverable. Observability checks supplement behavior tests; they do not replace them.
