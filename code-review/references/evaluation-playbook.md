# Code Review Evaluation Playbook

Use this only when evaluating or revising the `code-review` skill.

## Fresh-context method

Run each prompt in a fresh context with only the skill and the referenced fixture files. Grade the current skill behavior against prior accepted output patterns, but do not expose prior answers to the model under test.

## Executable manual protocol

Model execution stays outside CI. CI may validate fixture syntax, references, and formatting only.

For each eval case in `evals/evals.json`:

1. Run exactly 10 fresh-context trials with only this skill, the eval prompt, and the referenced fixture files.
2. Classify each trial as `trigger` or `non-trigger`.
3. For trials whose activation behavior is accepted, grade every listed assertion as pass/fail.
4. Compare the current 10-run result with the prior accepted scorecard for the same eval ID. Record any activation, decision, severity, completeness, read-only, or hand-off regression with evidence.

Denominators and scoring:

- Trigger-case activation rate = trigger trials / 10. Accept when >= 9/10.
- Non-trigger-case undesired activation rate = trigger trials / 10. Accept when <= 1/10.
- Assertion pass rate = assertion-passing accepted trials / accepted trials. Accept only at 100%; if no trial has accepted activation behavior, assertion pass rate is 0%.
- Read-only violations are automatic failures for the affected trial and reject the eval if they occur in any trial.

Use this compact scorecard:

| eval_id | case_type trigger/non-trigger | trials | triggers | accepted_activation | assertion_passes | assertion_denominator | current_result | prior_result | regressions/evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |

Acceptance criteria:

- Every trigger case has at least 9/10 desired activations.
- Every non-trigger case has at most 1/10 undesired activations.
- Required output assertions pass on 100% of accepted runs.
- Current-vs-prior comparison shows no material regression, or the behavior change is intentional and documented.

Reject the change when any acceptance criterion fails.

## Targets

- Desired activation rate: >= 90% (at least 9/10 fresh-context runs per trigger case).
- Undesired activation rate: <= 10% (at most 1/10 fresh-context runs per non-trigger case).
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
