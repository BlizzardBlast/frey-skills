# Architecture Impact Checklist

Use this checklist when reviewing changes that may affect system boundaries,
contracts, or operational safety.

## When to load this reference

Load this file when a change touches one or more of:

- Public API contracts (REST/GraphQL/SDK/event payloads)
- Data model/schema/migration logic
- Authentication/authorization boundaries
- Service-to-service dependencies or protocol assumptions
- Deployment/rollback strategy

## Boundary checklist

| Boundary              | Signals in diff                                                     | Why it matters                               | Required review action                                                   |
| --------------------- | ------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| API contracts         | Endpoint shape changes, field renames/removals, status code changes | Can break clients silently                   | Verify backward compatibility, deprecation path, and versioning strategy |
| Data schema           | Migrations, constraints, enum changes, backfills                    | Can corrupt data or block deploys            | Check migration safety, rollback path, idempotency, and data integrity   |
| Domain invariants     | Business rule edits (pricing, limits, state transitions)            | Can produce valid-looking but wrong behavior | Require tests that assert invariants before/after change                 |
| Dependency boundaries | New infra/service/lib dependencies                                  | Hidden coupling and runtime fragility        | Confirm ownership, failure mode handling, and fallback behavior          |
| Auth boundaries       | Permission checks moved/removed, role logic edits                   | Security exposure risk                       | Confirm authn/authz checks at every sensitive path                       |
| Observability         | Logging/metrics/tracing changes                                     | Harder incident triage                       | Ensure key paths still emit actionable telemetry                         |
| Rollout/rollback      | Feature flags, migration ordering, one-way changes                  | Operational blast radius                     | Validate incremental rollout and explicit rollback plan                  |

## Risk scoring

Score each boundary as:

- `0` = not impacted
- `1` = impacted, low uncertainty
- `2` = impacted, moderate/high uncertainty

Interpretation:

- **0-2 total:** low architecture risk
- **3-5 total:** medium architecture risk (require explicit mitigation notes)
- **6+ total:** high architecture risk (default to `REQUEST_CHANGES` unless mitigations are concrete)

## Required architecture note in review output

When any boundary is impacted, include:

1. Impacted boundaries
2. Risk level (`low`, `medium`, `high`)
3. Missing mitigations
4. Suggested mitigation steps (smallest safe increments)

## Gotchas

- “Small” refactors can still break contracts if types/field names change.
- Migration success is not enough; rollback safety must be reviewed too.
- New dependencies should include failure-mode behavior, not only happy-path integration.

## Focused checklist: portability, determinism, and review reliability

Use this section when reviewing helper scripts, CLIs, or generated artifacts.

- [ ] **Portability / decoding stability**
  - Text decoding is explicit (encoding + error policy), not locale-dependent.
- [ ] **Determinism of outputs**
  - Default output avoids wall-clock, host, or session-dependent values.
  - Non-deterministic fields are explicit opt-ins.
- [ ] **Diff-format robustness**
  - Parsing logic handles rename/copy/path edge cases (prefer machine-stable formats such as `-z` where applicable).
- [ ] **Privacy-safe outputs**
  - Avoid leaking absolute local paths, usernames, or machine-specific identifiers in default output.
- [ ] **Comment validity triage**
  - Verify whether a review comment targets current code or stale diff hunks before applying changes.
- [ ] **Micro-fixture validation**
  - Use small synthetic fixtures for edge-case behavior (e.g., rename/copy diff records) before finalizing fixes.
