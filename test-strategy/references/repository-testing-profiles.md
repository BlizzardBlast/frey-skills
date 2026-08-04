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

## Performance and resilience

Inspect latency-sensitive paths, resource limits, query plans, memory use, connection pools, backpressure, caching, and dependency failure.

Consider representative load, thresholds grounded in requirements, degradation behavior, timeout budgets, recovery, and observability. Do not invent performance targets.

## Observability and incident recovery

Inspect logs, metrics, traces, alerts, correlation identifiers, dashboards, runbooks, rollback, and data repair paths.

Consider whether failures are detectable, actionable, safely diagnosable, and recoverable. Observability checks supplement behavior tests; they do not replace them.
