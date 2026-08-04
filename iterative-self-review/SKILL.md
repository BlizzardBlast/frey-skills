---
name: iterative-self-review
description: Use only when explicitly invoked for an issue ledger, remediation request, repeated fix-and-recheck loop, or post-review repair. Accepts code-review findings or user-specified issues, fixes them in bounded passes, compares against a resolved task/default-branch baseline, and reports scoped verification without claiming the whole repository is clean.
license: MIT
metadata:
  author: BlizzardBlast
  version: '1.1.0'
  allow_implicit_invocation: 'false'
---

# Iterative Self-Review

## Activation boundary

Use this skill only when the user explicitly requests iterative self-review, repeated remediation, or fixes for a provided issue ledger. Do not invoke it implicitly for ordinary implementation or one-off review.

Inputs may be:

- A `code-review` finding ledger.
- Explicit user remediation instructions.
- A scoped list of failing tests, review comments, or defects to fix.

## Default pass budget

Run at most 3 review/fix/verify passes by default. Stop early only when the scoped issues are resolved and the required verification for those issues has passed or is honestly marked blocked. After pass 3, stop and ask for direction if any in-scope item remains unresolved or blocked. Do not run pass 4 or any later pass unless the user explicitly asks for additional passes after seeing the pass-limit status; never continue past the limit silently.

Do not claim “zero issues”, “all clean”, or whole-repository correctness. Report only scoped resolution and verification evidence.

## Baseline setup

Before editing, record a working-state baseline:

- Branch name and dirty/untracked status.
- Files in scope and incoming issue IDs.
- Existing failing or skipped verification that may affect claims.

Resolve the comparison base in this order:

1. User-provided base.
2. `origin/HEAD`.
3. `origin/main`.
4. `main`.
5. `origin/master`.
6. `master`.

If no base can prove broader regression claims, set `BASELINE_LIMITED` and state what comparison remains valid, such as current working tree only or issue-specific files only.

## Required loop

For each pass:

1. Review the unresolved ledger items and current code against the baseline.
2. Plan the smallest safe fix set for this pass.
3. Edit only in-scope files needed to resolve the ledger.
4. Verify with the most relevant focused commands or evidence.
5. Update the ledger: `resolved`, `unresolved`, `blocked`, or `deferred by user scope`.
6. Stop if scoped issues are resolved; otherwise continue until the pass budget is exhausted.

Fix order is `P0 -> P1 -> P2 -> P3` unless the user narrows scope. If a request is P1-only, do not opportunistically fix P2/P3 items except for necessary supporting edits.

## Conflict and blocker rules

- If two fixes conflict, choose the safer requirement-preserving path and document the tradeoff.
- If the same issue toggles across passes, stop rather than churn.
- If verification cannot run or required context is missing, mark the affected item `blocked` with exact evidence.
- If the 3-pass default limit is reached with unresolved items, stop, report what remains, and ask for direction. Continue to pass 4 or any later pass only after the user explicitly requests additional passes after that status is reported.

## References

Load only as needed:

- `references/baseline-and-pass-rules.md` for baseline commands, pass ledger states, and `BASELINE_LIMITED` wording.
- `references/issue-ledger-format.md` for a compact remediation ledger template.
- `references/evaluation-playbook.md` only when evaluating this skill.

## Output format

Use this concise structure:

1. `Baseline`
   - base used, working-state notes, and `BASELINE_LIMITED` if applicable.
2. `Pass N`
   - issue IDs attempted, edits made, verification run, and ledger updates.
3. `Final status`
   - `RESOLVED`, `PARTIAL`, or `BLOCKED` for the requested scope.
4. `Remaining concerns`
   - unresolved blockers, skipped out-of-scope items, and any verification limits.

## Completion conditions

This skill is complete when one of these is true:

- All in-scope ledger items are resolved and required verification is recorded.
- The pass budget is exhausted and remaining work is reported.
- A blocker prevents further safe progress and is reported with evidence.
