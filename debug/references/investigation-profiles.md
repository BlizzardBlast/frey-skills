# Investigation Profiles

Use these profiles to identify the evidence and causal boundaries relevant to the symptom. Include only materially applicable concerns.

## Application and test failures

Trace:

- failing assertion or user-visible symptom back through the caller and state/data source;
- test setup, fixtures, mocks, clocks, random seeds, ordering, and isolation;
- validation, error mapping, retries, and partial failure behavior;
- differences between test and production code paths.

Prefer focused reproduction and boundary checks over repeatedly running the entire suite.

## Frontend and browser behavior

Inspect applicable concerns:

- event flow, state/query/cache transitions, route state, form validation, and async races;
- loading/error/empty/optimistic states and stale response ordering;
- hydration, browser APIs, storage, service workers, generated routes, and environment variables;
- accessibility behavior when keyboard, focus, semantics, or assistive feedback is part of the symptom.

## Backend, API, and jobs

Inspect applicable concerns:

- request parsing, validation, authn/authz, tenancy, serialization, and status/error mapping;
- transaction boundaries, retries, idempotency, queues, timeouts, cancellation, and partial failures;
- upstream/downstream contracts and whether the observed failure is local or propagated;
- logs and traces without exposing secrets or PII.

## Data and migrations

Inspect applicable concerns:

- historical data shape, null/default/enum transitions, constraints, backfills, and old/new version coexistence;
- transaction isolation, locking, query plans, indexes, ordering, and N+1 behavior;
- whether the symptom is caused by invalid retained data, a reader/writer mismatch, or migration sequencing.

Do not run migrations or mutate production data during investigation.

## Monorepo, build, and CI

Inspect applicable concerns:

- package boundaries, exports, path aliases, generated artifacts, task graphs, and cache inputs/outputs;
- runtime/tool versions, package-manager behavior, lockfiles, environment variables, and platform differences;
- workflow event, permissions, checkout depth, artifacts, required checks, and shell behavior;
- deterministic differences between local and CI execution.

## Flaky and concurrent behavior

Inspect applicable concerns:

- clocks, timers, randomization, shared mutable state, ports, filesystem paths, network dependence, and resource contention;
- ordering, retries, eventual consistency, cancellation, cleanup, and leaked processes;
- whether repeated runs change probability without establishing mechanism.

Use controlled variation and discriminating evidence. A passing rerun is not a diagnosis.

## Production and external dependencies

Inspect applicable concerns:

- exact deployment version/configuration, rollout overlap, feature flags, traffic shape, and regional/environment differences;
- logs, traces, metrics, request IDs, partner responses, rate limits, timeouts, and service health;
- observability gaps and whether local reproduction is representative.

When production or partner access is unavailable, report `PARTIAL` or `BLOCKED`; do not fabricate parity or confirmation.
