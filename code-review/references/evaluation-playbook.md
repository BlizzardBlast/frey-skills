# Code Review Evaluation Playbook

Use this only when evaluating or revising the `code-review` skill.

## Fresh-context method

Run each prompt in a fresh context with only the skill and the referenced fixture files. Grade the current skill behavior against prior accepted output patterns, but do not expose prior answers to the model under test.

## Targets

- Desired activation rate: >= 90%.
- Undesired activation rate: <= 10%.
- Required output assertions: 100% on accepted runs.
- Model runs stay outside CI; CI may validate fixture syntax only.

## Manual evidence grading

For each accepted run, grade:

- Correct trigger or non-trigger behavior.
- Presence and correctness of the coverage matrix.
- Completeness label matches inspected/missing context.
- Finding IDs, severity, evidence, impact, remediation, and verification.
- Decision follows the severity/completeness rules.
- Read-only behavior; fix requests produce a hand-off to `iterative-self-review`.

Reject runs that approve uninspected required context, mutate files, omit requested concerns, or fail to identify the fixture's primary P0/P1 issue.

## Release use

Before releasing skill changes, run a small mixed set from `evals/evals.json`, compare current-vs-prior behavior, record failures with evidence, revise instructions, and re-run only the affected scenarios plus one clean-diff control.
