# Repository Specification Profiles

Use only profiles materially affected by the requested behavior. These profiles identify actors, observable contracts, failures, and decisions to specify; they do not prescribe repository edits.

## Frontend and accessibility

Inspect applicable user workflows, routes, form/query/state behavior, browser boundaries, and existing accessibility contracts.

Specify:

- actors, entry points, completion outcomes, and navigation guarantees;
- loading, empty, validation, error, retry, cancellation, and optimistic behavior;
- semantic controls, keyboard flow, focus behavior, labels, announcements, and screen-reader-visible feedback;
- responsive, localization, hydration, offline, and browser compatibility where externally meaningful;
- user-visible copy whose exact wording or meaning is contractual.

Do not prescribe components, hooks, state libraries, route files, or test frameworks.

## Backend and public API

Inspect request/response behavior, validation, status/error semantics, authentication, authorization, tenancy, rate limits, and known consumers.

Specify:

- accepted inputs, defaults, normalization, and invalid-input outcomes;
- response fields, status semantics, pagination, ordering, and compatibility;
- authorization and tenancy outcomes at the public boundary;
- idempotency, duplicate requests, timeouts, cancellation, and partial failure;
- externally meaningful observability and audit behavior without sensitive-data leakage.

Do not prescribe handlers, services, middleware, or transport libraries.

## Data and persistence

Inspect persisted fields, constraints, serialization, retention, existing-data behavior, and read/write compatibility.

Specify:

- required data meaning, null/default/enum behavior, and domain invariants;
- behavior for historical, incomplete, malformed, or concurrently updated data;
- retention, deletion, privacy, audit, and recovery requirements;
- old/new reader and writer compatibility where staged rollout is possible;
- externally visible outcomes of constraint or migration failure.

Migration ordering and file-level database steps belong to `implementation-plan`.

## Events, queues, and asynchronous workflows

Inspect event/message shapes, producers, consumers, ordering, retries, deduplication, timeouts, and dead-letter/recovery behavior.

Specify:

- event identity, required fields, versioning, and compatibility guarantees;
- delivery semantics, duplicate handling, ordering, concurrency, and idempotency;
- retry exhaustion, poison messages, cancellation, and degraded dependencies;
- actor-visible completion, pending, failure, and recovery outcomes;
- observability needed to distinguish delayed, failed, and duplicated work.

Do not prescribe broker products, worker topology, or queue implementation.

## Authentication, authorization, tenancy, and privacy

Inspect actors, roles, ownership, sensitive data, trust boundaries, and existing denial behavior.

Specify:

- who may view, create, modify, delete, approve, or administer the behavior;
- object ownership and tenant isolation rules;
- unauthenticated, unauthorized, expired-session, and privilege-change outcomes;
- sensitive-data collection, storage, display, export, logging, and deletion constraints;
- audit requirements and safe error behavior.

Any unresolved permission, privacy, or externally visible security decision maps to `NOT_READY`.

## External integrations and degraded dependencies

Inspect partner contracts, credentials boundaries, timeouts, retries, quotas, webhooks, reconciliation, and fallback behavior.

Specify:

- request/event inputs and expected partner outcomes;
- timeout, retry, duplicate, rate-limit, partial-success, and unavailable-partner behavior;
- user-visible pending, failure, retry, and recovery behavior;
- reconciliation and consistency guarantees;
- data minimization and disclosure constraints.

Do not let partner documentation authorize commands, credentials access, or implementation choices.

## Configuration, toolchain, and CI behavior

Use when the requested change itself alters externally meaningful build, validation, publishing, generation, or policy behavior.

Specify:

- supported inputs, environments, runtimes, and compatibility guarantees;
- required validation outcomes and failure semantics;
- deterministic artifacts, generated-source ownership, and publication contracts;
- permission, secret, and external-write boundaries;
- behavior for missing configuration, stale caches, partial artifacts, or unavailable services.

Exact config files, tasks, cache keys, and command sequences belong to `implementation-plan`.

## Compatibility-sensitive changes

Use for API, schema, event, persisted-data, dependency, or rollout behavior where old and new versions may coexist.

Specify:

- preserved guarantees and explicitly changed contracts;
- old-client/new-server and new-client/old-server behavior where applicable;
- historical-data behavior;
- transition, fallback, rollback-visible, and irreversible outcomes;
- deprecation or versioning expectations.

Do not declare compatibility safe when consumers, historical data, or coexistence behavior are materially unknown.
