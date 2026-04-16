---
name: iterative-self-review
description: Use this skill when the user asks for an iterative self-review loop, repeated fix-and-recheck cycles, or post-review remediation until zero issues remain. Trigger on requests like "iterate until no issues," "review and keep fixing," or "run another pass." For PR/diff/merge-readiness discovery, use `code-review` first and then hand off findings to this skill.
license: MIT
metadata: { author: BlizzardBlast, version: '1.0.2' }
---

# Iterative Self-Review

## When to use this skill

Use this skill whenever:

- You write new code.
- You refactor existing code.
- The user asks to "review your work" or requests a self-check.

## Activation boundaries

Prefer this skill when correctness and regression risk matter more than speed.

Do use it for:

- Pre-merge or pre-commit quality passes.
- Bug-fix verification after code edits.
- Sensitive changes (data flow, auth, validation, migrations).
- Follow-up iterative remediation after `code-review` findings.

Do not over-apply it for:

- Purely informational responses with no code edits.
- Trivial non-behavioral changes (e.g., comment-only wording tweaks), unless the
  user explicitly requests a full review loop.

If a request includes PR/diff/merge-readiness analysis, do not replace
`code-review`; use this skill after first-pass findings are available.

## Goal

Rigorously review newly changed code, identify concrete issues, and iteratively
fix them until the codebase is clean while preventing regression loops.

## Companion usage with `code-review`

When this skill is used after `code-review` findings:

- Treat incoming P0/P1 findings as mandatory fix-first blockers.
- Fix in severity order (P0 → P1 → P2 → P3) unless the user overrides.
- Preserve traceability: map each fix to the finding it resolves.
- Do not mark completion while blocker findings remain unresolved.

## Iterative review loop (required order)

Follow these steps in exact order:

1. **Initial code review**
   - Analyze the code you just wrote or modified.
   - Check for syntax errors, logic bugs, edge-case failures, performance issues,
     and prompt-requirement mismatches.
2. **Status check**
   - If **no issues** are found, output: `Code review complete. No issues found.`
     and exit the loop.
   - If **issues** are found, continue.
3. **Log issues before editing**
   - Explicitly list each issue before applying fixes.
4. **Apply fixes**
   - Update the code to resolve the logged issues.
5. **Update regression ledger**
   - Track fixed issues in a mental "Regression Ledger."
   - Explicitly verify new changes do not reintroduce previously fixed problems.
6. **Repeat**
   - Return to step 1 and run a fresh review pass on updated code.

## Strict constraints and anti-loop rules

- **No guessing:** Do not stop until a full pass finds zero issues.
- **Break infinite loops:** If you toggle between the same fixes more than
  3 times, stop and ask the user for intervention.
- **No regressions:** Never sacrifice an earlier fix to solve a newer one.
  Rethink the approach if fixes conflict.

## Gotchas

- Do not skip the issue log step before making fixes.
- Do not claim completion without an explicit zero-issue final pass.
- Do not collapse multiple distinct issues into one vague bullet.
- Do not hide unresolved conflicts; surface them clearly when blocked.
- If the same issue recurs across passes, compare against the regression ledger
  before editing again.

## Required output for each pass

Use this structure during the loop:

1. `Review pass N`
2. `Issues found:`
   - `- <issue 1>`
   - `- <issue 2>`
3. `Fixes applied:`
   - `- <fix 1>`
4. `Regression check:`
   - `- Verified no reintroduction of <prior issue>`
5. `Next status:`
   - `Continue loop` or `Code review complete. No issues found.`
