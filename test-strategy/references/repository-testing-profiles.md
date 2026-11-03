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

## Performance and resilience

Inspect latency-sensitive paths, resource limits, query plans, memory use, connection pools, backpressure, caching, and dependency failure.

Consider representative load, thresholds grounded in requirements, degradation behavior, timeout budgets, recovery, and observability. Do not invent performance targets.

## Observability and incident recovery

Inspect logs, metrics, traces, alerts, correlation identifiers, dashboards, runbooks, rollback, and data repair paths.

Consider whether failures are detectable, actionable, safely diagnosable, and recoverable. Observability checks supplement behavior tests; they do not replace them.
