# Iterative Self-Review Evaluation Playbook

Use this only when evaluating or revising the `iterative-self-review` skill.

## Fresh-context method

Run each prompt in a fresh context with only the skill, the fixture files, and the incoming ledger or remediation request. Compare current behavior against prior accepted behavior after the run; do not include prior answers in the test prompt.

## Targets

- Desired activation rate for explicit remediation prompts: >= 90%.
- Undesired activation rate for implicit review-only prompts: <= 10%.
- Required output assertions: 100% on accepted runs.
- Model runs stay outside CI; CI may validate fixture syntax only.

## Manual evidence grading

For each accepted run, grade:

- Explicit-only activation behavior.
- Baseline resolution order and working-state baseline reporting.
- `BASELINE_LIMITED` when broader regression claims cannot be proven.
- Maximum 3 passes by default.
- Severity/scope discipline, especially P1-only requests.
- Ledger state updates and verification evidence.
- No absolute “all clean” or “zero issues” repository-wide claim.

Reject runs that silently continue past the pass limit, mutate out-of-scope files, fix unrequested lower-severity issues in a narrowed task, or hide unresolved blockers.
