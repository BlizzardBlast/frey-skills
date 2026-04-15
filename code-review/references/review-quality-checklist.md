# Review Quality Checklist

Run this checklist before finalizing a decision.

## 1) Correctness and reliability

- [ ] Core behavior matches requested intent.
- [ ] Edge cases are handled (null/empty/bounds/error states).
- [ ] Error handling is explicit and actionable (no silent failures).
- [ ] Concurrency/race-condition risks are addressed where relevant.

## 2) Security

- [ ] User input is validated/sanitized.
- [ ] No injection risk (SQL/command/template/path).
- [ ] Authn/authz checks are present on sensitive paths.
- [ ] Secrets/PII are not leaked in code, logs, or responses.

## 3) Performance and scalability

- [ ] No obvious N+1 or unnecessary repeated heavy work.
- [ ] Large data paths have limits/pagination/streaming where needed.
- [ ] Expensive operations are justified or cached.

## 4) Architecture impact

- [ ] Contract/schema/boundary impacts were explicitly evaluated.
- [ ] Rollout and rollback implications were considered.
- [ ] Dependency and ownership boundaries remain clear.

## 5) Test and verification strategy

- [ ] New behavior is covered by tests or equivalent verification.
- [ ] Critical regressions have guardrails.
- [ ] Validation evidence is referenced in the review.

## 6) Maintainability

- [ ] Naming, cohesion, and structure support future changes.
- [ ] Complexity is proportional to problem scope.
- [ ] Recommendations are incremental and safe-by-default.

## 7) Decision integrity

- [ ] Decision (`APPROVE`/`COMMENT`/`REQUEST_CHANGES`) matches severity.
- [ ] Every P0/P1 finding includes a concrete remediation path.
- [ ] Review includes at least one positive strength when present.
