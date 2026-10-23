# Risk-guided review and recurring-finding analysis

Use alongside `code-review/SKILL.md`. Adapted cautiously from [Will Larson, "Speeding up code review with small-change"](https://lethain.com/small-changes/) (2026-10-17). The article reports an early experiment, not proof that AI approval is safe.

## Review-depth classification, not a bypass

Classify the inspected **change** using paths, effective behavior, reachable callers, repository-native controls, and missing context:

| Tier | Examples | Required attention |
| --- | --- | --- |
| `low` | Contained docs correction, narrow test-only edit, or demonstrably nonbehavioral local change | Focus on actual changed scope and the relevant contracts; confirm exclusions with evidence. |
| `medium` | Normal feature, local behavioral refactor, dependency update with bounded impact | Review behavior, tests, compatibility, callers, and failure paths. |
| `high` | Auth, authorization, privacy, money movement, migrations, shared libraries, installers, CI/security controls, global agent instructions, or cross-service contracts | Inspect sensitive invariants, indirect callers, adversarial/negative cases, rollback, and protection gates. |
| `unknown` | Missing diff, inaccessible context, uncertain blast radius or check provenance | Investigate gaps; mark relevant coverage partial/blocked. Never treat uncertainty as safe. |

- A short diff can be high risk. Do **not** adopt the article's 1,000-line cutoff, author PR count, or absence of AI P1/P2 findings as a sufficient safety predicate.
- No tier changes the existing `Review completeness`, `P0–P3`, or `APPROVE/COMMENT/REQUEST_CHANGES` decision contracts. A read-only `APPROVE` assessment is **not** an actual GitHub PR approval.
- Keep repository-specific mandatory human approval, sensitive-path review, required checks, and branch protection intact. Avoid skipped workflows leaving required checks pending.
- Prioritize evidence proportionately, but do not conceal applicable concerns or inflate findings merely to appear thorough.

## Discover related defects before handoff

For nontrivial changed behavior, map each required invariant to its relevant consumers, reachable boundary cases, and evidence in the existing coverage matrix. Choose cases according to risk and actual control flow; an exhaustive input cross-product is not required. Passing CI or the original example does not establish an untested invariant.

- Inspect transitions and interacting conditions, including failure paths, rather than checking each input category only in isolation. Follow a suspected defect through its shared owner and consumers before finalizing the ledger.
- For example, a mixed Markdown/HTML parser needs to preserve the distinction between active syntax, escaped text, and code when entering or leaving a comment. Check the resulting section eligibility, boundaries, and duplicate detection together; one green tag example does not cover every comment transition.
- Use relevant existing tests or safe, authorized probes to check a related counterexample. Propose missing regression coverage when execution would exceed the read-only review boundary. State what remains unverified.
- Group verified variants only when they share a root cause and remediation; retain their distinct evidence and impact under the traceable finding IDs. Keep independently remediable defects separate.
- Finish the planned discovery before handing off the batch. A first finding does not complete the other applicable review concerns, and `COMPLETE` never guarantees absence of defects.

## Triage repeated AI and human comments

1. Verify each claimed problem against the current revision, contract, and actual caller or failure behavior.
2. Mark duplicates by shared **root cause and remediation**, recording the cross-referenced IDs; similarity of wording alone is insufficient.
3. Classify older comments as current, stale, superseded, invalid/unsubstantiated, or blocked by unavailable evidence. Do not dismiss a valid concern because a later agent disagrees.
4. Issue one actionable finding per independently remediable defect. Preserve all independent P0/P1 defects and relevant impact evidence.
5. Recommend another **full** review after a material change, new evidence or newly exposed risk, or when explicitly requested by the user; do not turn unchanged findings into endless new work.

## Opt-in review-pattern audits

When explicitly asked to analyze a batch/cluster of PRs or review ledgers:

1. Establish the permitted repository set and time/snapshot range. Inspect only authorized source material; never infer rights to export employer/client/private material.
2. Associate each finding with a particular PR/snapshot, risk tier, observed evidence, and whether the correction was independently verified. Keep per-PR completeness and blockers explicit.
3. Group **verified recurrent root causes**, not superficial labels, and distinguish a pattern hypothesis from causal proof.
4. Propose a narrowly scoped verification improvement (test, static rule, harness check, documentation, or review checklist) with a counterexample and a way to measure false positives and cost.
5. Report sanitized pattern candidates to the user. Do not write a memory lesson, edit CI, post comments, label/approve/merge PRs, or promote a global rule; those actions require separate user authorization and applicable source consent.


## Turn recurring findings into prevention candidates

When a verified issue recurs across permitted reviews, decide whether a **focused regression test, architectural/static check, contract test, scoped review checklist, or candidate Agent Brain lesson** would actually catch its root cause. Record the affected invariant, reproducer or negative case, false-positive risk, ongoing maintenance/CI cost, and applicability limits. Avoid adding a broad check for a rare low-impact anecdote. A repeated AI comment is not independently verified evidence, and this analysis remains read-only until separately authorized.

For owner-requested efficiency experiments, follow [the optional paired measurement protocol](review-efficiency-experiment.md). Compare complete task cost and independently verified outcomes, not input-token counts alone. Never weaken coverage, source permissions, mandatory checks, or protected reviews to improve a benchmark.

## Efficient handoff and success measures

Pass deduplicated, evidence-backed IDs, affected invariants, and checked or unverified variants to `iterative-self-review`. Prefer one local verification batch before an authorized push, without suppressing required CI. Track user round trips, related defects found after a repair, repair-induced regressions, review time, and CI minutes per merged PR; reduction in review effort is not success if regressions rise.
