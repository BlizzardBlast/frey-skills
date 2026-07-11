# Baseline and Pass Rules

Use this when setting up or reporting an `iterative-self-review` run.

## Baseline commands

Prefer non-mutating commands:

- Current branch: `git branch --show-current`
- Working state: `git status --short`
- Default remote: `git symbolic-ref refs/remotes/origin/HEAD --short`
- Available bases: `git rev-parse --verify <candidate>`
- Diff scope: `git diff --name-status <base>...HEAD` plus `git diff --name-status` for local edits

Resolve the base in this order: user-provided base, `origin/HEAD`, `origin/main`, `main`, `origin/master`, `master`.

## BASELINE_LIMITED

Use `BASELINE_LIMITED` when no base is available, history is shallow/missing, generated context is absent, or existing dirty state prevents a reliable broader regression claim.

Suggested wording:

`BASELINE_LIMITED: I could compare the requested files and current working state, but I could not prove broader regressions against <missing base/context>.`

## Ledger states

- `resolved`: fix applied and scoped verification supports the result.
- `unresolved`: still failing or not yet attempted within scope.
- `blocked`: cannot safely continue because context, command access, or requirements are missing/conflicting.
- `deferred by user scope`: known item intentionally left out because the user narrowed the task.

## Pass budget behavior

Default to 3 passes. A pass counts once you inspect current code and either make or intentionally skip a fix for an in-scope issue. Stop before the limit when all scoped items are resolved and verified. At the limit, report remaining ledger states and ask for direction.
