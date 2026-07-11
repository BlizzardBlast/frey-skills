# Iterative Self-Review Evaluation Playbook

Use this only when evaluating or revising the `iterative-self-review` skill.

## Fresh-context method

Run each prompt in a fresh context with only the skill, the fixture files, and the incoming ledger or remediation request. Compare current behavior against prior accepted behavior after the run; do not include prior answers in the test prompt.

## Executable manual protocol

Model execution stays outside CI. CI may validate fixture syntax, references, and formatting only.

For each eval case in `evals/evals.json`:

1. Run exactly 10 fresh-context trials with only this skill, the eval prompt, and the referenced fixture files.
2. Classify each trial as `trigger` or `non-trigger`. The ordinary implementation fixture is a non-trigger case because it lacks an explicit ledger/remediation-loop request.
3. For trials whose activation behavior is accepted, grade every listed assertion as pass/fail.
4. Compare the current 10-run result with the prior accepted scorecard for the same eval ID. Record any activation, scope, pass-limit, ledger-state, verification, or baseline-reporting regression with evidence.

Denominators and scoring:

- Trigger-case activation rate = trigger trials / 10. Accept when >= 9/10.
- Non-trigger-case undesired activation rate = trigger trials / 10. Accept when <= 1/10.
- Assertion pass rate = assertion-passing accepted trials / accepted trials. Accept only at 100%; if no trial has accepted activation behavior, assertion pass rate is 0%.
- Out-of-scope mutation, silent pass-limit overrun, or whole-repository clean claims are automatic failures for the affected trial and reject the eval if they occur in any trial.

Use this compact scorecard:

| eval_id | case_type trigger/non-trigger | trials | triggers | accepted_activation | assertion_passes | assertion_denominator | current_result | prior_result | regressions/evidence |
| ------- | ----------------------------- | -----: | -------: | ------------------: | ---------------: | --------------------: | -------------- | ------------ | -------------------- |

Acceptance criteria:

- Every explicit remediation trigger case has at least 9/10 desired activations.
- Every non-trigger case has at most 1/10 undesired activations.
- Required output assertions pass on 100% of accepted runs.
- Current-vs-prior comparison shows no material regression, or the behavior change is intentional and documented.

Reject the change when any acceptance criterion fails.

## Targets

- Desired activation rate for explicit remediation prompts: >= 90% (at least 9/10 fresh-context runs per trigger case).
- Undesired activation rate for implicit or ordinary implementation prompts: <= 10% (at most 1/10 fresh-context runs per non-trigger case).
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
