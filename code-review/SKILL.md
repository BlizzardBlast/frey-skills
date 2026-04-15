---
name: code-review
description: Use this skill when reviewing pull requests, branch diffs, pre-merge changes, or review comments for correctness, security, architecture impact, and maintainability. Trigger on requests like "review this PR", "final code check", "merge readiness", "check this diff", "find risks", or "address review comments", even when the user does not explicitly say "code review".
license: MIT
compatibility: Core instructions are tool-agnostic. Optional helper script requires git and Python 3.9+.
metadata: { author: BlizzardBlast, version: '1.0.0' }
---

# Code Review

## When to use this skill

Use this skill whenever:

- The user asks for a review of code changes, a pull request, a branch diff, or review comments.
- You need a merge-readiness check before finalizing implementation.
- You need structured findings with severity and actionable fixes.
- You need confidence on architecture impact (API contracts, schema changes, service boundaries).

## Activation boundaries

Prefer this skill for review-first tasks where analysis and feedback are the
primary output.

Do use it for:

- Pull request review and pre-merge validation.
- Architecture and maintainability assessment of changed code.
- Security and correctness checks on modified files.
- Post-implementation quality gates before final response.

Do not over-apply it for:

- Requests to directly implement features without a review ask.
- Pure style/formatting-only checks that are better handled by automation.

## Review modes

Use one mode explicitly per task:

- **Mode A — Review only (default):** Analyze and report findings without edits.
- **Mode B — Review + remediation loop:** Review first, then fix issues iteratively
  when the user asks to implement fixes.
  - This mode intentionally composes with the `iterative-self-review` workflow
    (issue log → fix → regression check → repeat).

## Goal

Produce a clear, prioritized, and actionable review that helps the author merge
safely with minimal back-and-forth.

## Inputs to gather before deep review (required)

Collect the minimum context first:

- Change scope (PR, commit range, or working-tree diff).
- Intended behavior and acceptance criteria (issue/PR/user ask).
- Risk context (auth, payments, data writes, migrations, public APIs).
- Existing tests and validation signals.

## Severity model (required)

Use this severity model consistently:

- **P0 (critical):** Security vulnerability, data loss risk, broken behavior.
- **P1 (high):** Likely bug, major performance issue, significant design flaw.
- **P2 (medium):** Maintainability/code smell worth fixing in this cycle.
- **P3 (low):** Minor clarity/readability suggestion.

## Review workflow (required order)

1. **Scope the change**
   - Identify files changed and the functional area affected.
   - Understand the intent from PR description, issue text, or commit summary.
2. **Run architecture impact screen**
   - Evaluate API contracts, data model/schema changes, dependency boundaries,
     auth boundaries, observability, and rollback safety.
   - If impact is non-trivial, load `references/architecture-impact-checklist.md`.
3. **Run high-level checks**
   - Validate architecture fit, data flow, and API contract impact.
   - Check whether test strategy matches risk level.
4. **Run detailed checks**
   - Correctness and edge cases
   - Security and input validation
   - Performance hotspots and resource usage
   - Error handling and observability
   - Readability and maintainability
5. **Write findings with evidence**
   - Include file path and line (or nearest anchor) whenever possible.
   - Explain impact and provide a concrete fix suggestion.
6. **Conclude with a decision**
   - `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
   - Include issue counts by severity.
7. **If Mode B, run iterative remediation loop**
   - Log issue list before editing.
   - Fix by severity order: P0 → P1 → P2 → P3.
   - Re-run review checks after each fix wave.
   - Maintain a regression ledger so new fixes do not reintroduce prior issues.
   - If the same fixes toggle more than 3 times, stop and ask for user guidance.
8. **Final quality gate**
   - Load `references/review-quality-checklist.md` and verify decision consistency.

## On-demand resources

Use progressive disclosure. Load only what is needed:

- `references/architecture-impact-checklist.md`
  - Load when changes touch contracts, schemas, boundaries, or deployment safety.
- `references/review-quality-checklist.md`
  - Load before finalizing the review decision.
- `scripts/collect_review_context.py`
  - Optional helper for deterministic diff scope summary.
  - Run only when git context is ambiguous or large.
- `references/evaluation-playbook.md`
  - Load when improving this skill itself (trigger quality and output quality evals).

## Review output format

Use this response structure:

1. `Summary`
   - Scope reviewed and overall decision.
2. `Findings`
   - Group by severity in order: P0, P1, P2, P3.
   - Each finding includes: location, issue, impact, suggested fix.
3. `Architecture impact`
   - State impacted boundaries and risk level (`low`, `medium`, `high`).
   - If no material impact, explicitly say so.
4. `Strengths`
   - Mention at least one positive observation when present.
5. `Next steps`
   - State exactly what should happen next (merge, fix blockers, follow-up task).

## Completion conditions

This skill is complete only when:

- A decision is provided (`APPROVE`, `COMMENT`, or `REQUEST_CHANGES`).
- Findings are prioritized by severity.
- Every blocking issue (P0/P1) includes a specific remediation path.
- Architecture impact is explicitly covered.
- If no issues are found, the review explicitly states what was checked.
- In Mode B, a final zero-blocker pass is completed after fixes.

## Guardrails

- Prioritize correctness and security over stylistic preferences.
- Do not block on formatting nits unless they hide functional risk.
- Avoid vague statements; every issue must be actionable.
- Keep recommendations incremental and safe by default.

## Gotchas

- Do not skip architecture impact review for schema/API/auth changes.
- Do not provide a decision without evidence-backed findings.
- Do not start fixing before logging issues first in Mode B.
- Do not collapse multiple blockers into one generic comment.
