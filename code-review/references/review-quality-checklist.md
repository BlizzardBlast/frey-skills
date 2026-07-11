# Review Quality Checklist

Run this before finalizing any `code-review` decision.

## Evidence integrity

- [ ] The scope mode is stated.
- [ ] Each requested concern appears in the coverage matrix.
- [ ] Applicable profile concerns are either reviewed or marked not applicable with evidence.
- [ ] Missing, truncated, sampled, or stale context is reflected in `Review completeness`.
- [ ] No command, test, or artifact is claimed unless it was run or inspected.

## Finding integrity

- [ ] Every actionable finding has an ID, severity, location, evidence, impact, remediation, and verification.
- [ ] P0/P1 findings are specific enough for a fixer to act without rediscovery.
- [ ] P2/P3 items are not disguised preference unless they affect maintainability, usability, or risk.
- [ ] Stale review comments are explicitly classified as current, stale, superseded, or blocked.

## Decision integrity

- [ ] Any P0/P1 maps to `REQUEST_CHANGES`.
- [ ] Complete review with only P2 maps to `COMMENT`.
- [ ] Complete review with only P3 or no actionable findings maps to `APPROVE`.
- [ ] Partial/blocked review without P0/P1 maps to `COMMENT`.
- [ ] `APPROVE` is not used for partial, blocked, sampled, truncated, or materially uninspected context.

## Read-only boundary

- [ ] The review did not mutate source, generated files, PR state, branches, or external systems.
- [ ] If fixes were requested, the response emits the ledger first and hands remediation to `iterative-self-review`.
