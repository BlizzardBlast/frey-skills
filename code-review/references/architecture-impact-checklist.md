# Architecture Impact Checklist

Use when a change may affect contracts, schemas, boundaries, deployment, or operations.

## Boundary checks

| Boundary | Signals | Review action |
| --- | --- | --- |
| Public API | endpoint, field, status, SDK, event, query-param, or route-state changes | Verify backward compatibility, versioning, and caller migration. |
| Data model | migrations, constraints, enums, backfills, serialization | Check safety, idempotency, rollback, data integrity, and old-data behavior. |
| Domain invariants | pricing, limits, approvals, statuses, state transitions | Require evidence that important invariants still hold. |
| Auth and privacy | permission checks, PII, secrets, tenancy, audit logs | Confirm enforcement at every sensitive boundary and no leakage in logs/errors. |
| Dependencies | new service, package, protocol, generated artifact, cache | Check ownership, failure behavior, fallback, timeout, and supply-chain risk. |
| Observability | logging, metrics, traces, alerts, error handling | Ensure failures remain diagnosable without leaking sensitive data. |
| Release safety | feature flags, migration order, rollback, CI/CD, config | Confirm incremental rollout and a safe rollback story. |

## Risk note

In the review output, state impacted boundaries, risk level (`low`, `medium`, `high`), missing mitigations, and the smallest safe mitigation. If required context is absent, mark the coverage row `partial` or `blocked`; do not approve.

## Review reliability checks

- Prefer machine-stable diff/config formats for large or generated changes.
- Treat helper scripts and generators as architecture-affecting when they change build, CI, routing, migrations, or release artifacts.
- Check portability and determinism for tools: encoding, path handling, host-specific output, clocks, ordering, and generated file stability.
