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
- For material claims about implemented behavior, commands, compatibility or release status, check current code, configuration, tests and relevant execution/release evidence; an accepted ADR is not proof of implementation. For intended architecture or policy, verify decision acceptance independently and distinguish proposed guidance, accepted intent and implementation gaps. Mark unsupported claims; a passing Markdown/link check or AI-generated explanation is not factual verification.
- Check that readers and agents can identify the authoritative version. Flag conflicting or stale copies of policies, instructions and architecture guidance; distinguish canonical sources from generated or exported artifacts rather than maintaining independent versions.
- When discoverability is material, inspect semantic headings, actual lists/tables, specific section titles and usable references—not just appearance or syntactically valid links. Apply this only to relevant documents; do not demand a new format or impose cosmetic rewrites.
- Treat docs/dead-code findings as actionable when they can mislead users, hide risk, or keep obsolete behavior alive.
