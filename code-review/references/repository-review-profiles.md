# Repository Review Profiles

Use these profiles to decide which concerns are applicable. Include applicable concerns in the coverage matrix; mark irrelevant concerns `not applicable` with evidence.

## Frontend and accessibility

- State/query/route contracts, form validation, loading and error states, cache invalidation, hydration, and generated routes.
- Accessibility: semantic controls, labels, keyboard flow, focus management, color/contrast risk, ARIA correctness, and screen-reader-visible error feedback.
- Browser/runtime risks: bundle size, client/server boundaries, environment variables, and unsafe DOM insertion.

## Backend and API

- Request validation, authz/authn, tenancy, rate limits, idempotency, error status semantics, pagination, and compatibility.
- Background jobs, queues, retries, timeouts, cancellation, and partial failure behavior.
- Observability that helps triage without leaking secrets or PII.

## Database and migrations

- Migration ordering, locks, backfills, default values, constraints, rollback safety, and old/new app compatibility.
- Query plans, indexes, N+1 risks, transaction boundaries, and data retention/privacy.

## Monorepo and toolchain

- Workspace boundaries, package exports, generated artifacts, path aliases, task pipelines, cache keys, lockfiles, and cross-package API drift.
- Test runner, linter, formatter, type checker, codegen, and build reproducibility.

## CI and release

- Required checks, artifact publishing, environment scoping, secrets, deployment gates, feature flags, rollback, and versioning.
- Flaky or skipped checks that reduce confidence in the requested review scope.

## Dependencies and supply chain

- New or upgraded packages, licenses, transitive risk, abandoned packages, install scripts, native bindings, and bundle/runtime footprint.
- Pinning strategy and compatibility with supported runtimes.

## Docs and dead code

- Public docs, changelogs, examples, comments, generated docs, stale flags, unused exports, and unreachable branches.
- Treat docs/dead-code findings as actionable when they can mislead users, hide risk, or keep obsolete behavior alive.
