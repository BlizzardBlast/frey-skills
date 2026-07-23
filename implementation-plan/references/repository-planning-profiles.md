# Repository Planning Profiles

Use these profiles to determine which boundaries must be traced before an implementation plan can be considered actionable. Include only materially affected concerns in the output.

## Frontend and accessibility

Inspect when the change touches UI, routing, forms, client state, data fetching, browser APIs, or server/client rendering boundaries.

Plan for applicable concerns:

- component ownership and state/query/route contracts;
- loading, error, empty, optimistic, and retry behavior;
- form validation and server/client validation consistency;
- semantic controls, keyboard flow, focus management, labels, ARIA, and screen-reader-visible feedback;
- hydration, environment variables, unsafe DOM insertion, bundle/runtime boundaries, and generated routes;
- component/integration tests that verify user-observable behavior rather than implementation detail.

## Backend and API

Inspect when the change touches endpoints, handlers, services, jobs, auth, external integrations, or shared contracts.

Plan for applicable concerns:

- request/response validation and compatibility;
- authn/authz, tenancy, privacy, rate limits, and idempotency;
- transaction boundaries and partial failure behavior;
- retries, timeouts, cancellation, queues, and background jobs;
- status/error semantics and observability without secret/PII leakage;
- callers/consumers that must migrate together or remain backward compatible.

## Database and migrations

Inspect when schemas, constraints, indexes, persistence models, serialization, or retained data change.

Plan for applicable concerns:

- expand/migrate/contract sequencing for rolling deployments;
- old/new application compatibility and whether older writers can violate new constraints;
- backfill size, idempotency, resumability, locks, defaults, and null/enum transitions;
- indexes/query plans, N+1 risk, transactions, and data integrity;
- rollback feasibility and irreversible operations;
- migration and post-migration verification against representative existing data.

## Monorepo and toolchain

Inspect when workspaces, package exports, build tools, test runners, codegen, lint/format/typecheck config, or shared packages change.

Plan for applicable concerns:

- package ownership and dependency direction;
- exports, path aliases, generated artifacts, and cross-package API compatibility;
- task graphs, cache inputs/outputs, environment-sensitive cache keys, and build reproducibility;
- supported runtimes and package-manager/lockfile behavior;
- affected package-level and repository-level verification without rebuilding unrelated areas unnecessarily.

## CI and release

Inspect when workflows, deployment config, required checks, publishing, environments, or runtime configuration change.

Plan for applicable concerns:

- required checks and branch/release gates;
- artifact paths, reports, package publishing, and environment scoping;
- secrets/permissions and least-privilege boundaries;
- feature flags, deployment order, smoke checks, rollback, and failure recovery;
- whether old/new versions coexist during rollout and which order preserves compatibility.

## Dependencies and framework upgrades

Inspect when adding, removing, or upgrading packages/frameworks.

Plan for applicable concerns:

- official migration requirements already represented in repository code/config;
- peer/runtime compatibility and package boundary impact;
- deprecated/removed APIs and configuration changes;
- lockfile/install-script/native-binding implications;
- generated files, bundle/runtime footprint, and release sequencing;
- focused verification for migrated APIs plus broader build/type/test confidence where necessary.

## Cross-cutting architecture and security

Use for any change that alters a public contract, trust boundary, sensitive data path, domain invariant, or deployment topology.

Trace:

- public API/event/field/route contracts and consumer migration;
- domain invariants and invalid-state prevention;
- sensitive-data entry, storage, logging, and exposure points;
- authorization enforcement at each relevant boundary;
- ownership and failure behavior of new dependencies/services;
- observability needed to diagnose rollout failures safely.
