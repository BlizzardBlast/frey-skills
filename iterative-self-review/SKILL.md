---
name: iterative-self-review
description: Use only when explicitly invoked for an issue ledger, remediation request, repeated fix-and-recheck loop, or post-review repair. Fixes scoped findings in bounded passes against a recorded baseline and reports scoped verification without claiming the whole repository is clean.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.2.0'
  allow_implicit_invocation: 'false'
---

# Iterative Self-Review

## Activation and scope

Use only for explicit iterative remediation or a provided ledger. Do not activate for ordinary implementation, diagnosis, planning, execution of an approved plan, testing strategy, or one-off review.

Accept `code-review` findings, user remediation instructions, failing tests, review comments, or scoped defects. Fix in `P0 -> P1 -> P2 -> P3` order unless the user narrows scope. Do not opportunistically fix excluded severities except necessary supporting edits.

## Baseline

Before editing, record branch, dirty/untracked state, in-scope files and IDs, known failing/skipped checks, and a comparison base resolved in this order:

1. user-provided base
2. `origin/HEAD`
3. `origin/main`
4. `main`
5. `origin/master`
6. `master`

Use `BASELINE_LIMITED` when broader regression claims cannot be proven, and state the valid comparison.

Load only as needed:

- `references/baseline-and-pass-rules.md`
- `references/issue-ledger-format.md`
- `references/evaluation-playbook.md` only when evaluating this skill

## Bounded loop

Default maximum: 3 passes. Each pass:

1. Inspect unresolved in-scope items against current code and baseline.
2. Choose the smallest safe fix set.
3. Edit only necessary in-scope files while preserving unrelated work.
4. Run focused verification.
5. Update each item to `resolved`, `unresolved`, `blocked`, or `deferred by user scope`.

Stop early when all scoped items are resolved and verified. Stop rather than churn when fixes conflict or an issue toggles. Mark exact blockers when access, requirements, or verification are unavailable.

After pass 3, stop and report remaining work. Do not run pass 4 or later unless the user explicitly requests more passes after seeing that status.

Never claim “zero issues”, “all clean”, or whole-repository correctness.

## Output

1. `Baseline` (including `BASELINE_LIMITED` when applicable)
2. `Pass N` (IDs, edits, verification, state changes)
3. `Final status: RESOLVED|PARTIAL|BLOCKED`
4. `Remaining concerns`

Completion occurs when scoped items are resolved and verified, the pass budget is exhausted, or a concrete blocker prevents safe progress.
