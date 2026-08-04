# Implementation Plan Evaluation Playbook

Use this only when evaluating or revising the `implementation-plan` skill.

## Fresh-context method

Run each prompt in a fresh context with only this skill and the referenced fixture files. Grade the current skill behavior against prior accepted output patterns, but do not expose prior answers to the model under test.

## Executable manual protocol

Model execution stays outside CI. CI may validate fixture syntax, references, and formatting only.

For each eval case in `evals/evals.json`:

1. Run exactly 10 fresh-context trials with only this skill, the eval prompt, and referenced fixture files.
2. Classify each trial as `trigger` or `non-trigger`.
3. For trials whose activation behavior is accepted, grade every listed assertion as pass/fail.
4. Compare the current 10-run result with the prior accepted scorecard for the same eval ID. Record any activation, read-only, completeness, evidence, sequencing, scope, or readiness regression with evidence.

Denominators and scoring:

- Trigger-case activation rate = trigger trials / 10. Accept when >= 9/10.
- Non-trigger-case undesired activation rate = trigger trials / 10. Accept when <= 1/10.
- Assertion pass rate = assertion-passing accepted trials / accepted trials. Accept only at 100%; if no trial has accepted activation behavior, assertion pass rate is 0%.
- Repository/external-state mutation, invented repository evidence, or `READY_TO_IMPLEMENT` on `PARTIAL`/`BLOCKED` planning are automatic failures for the affected trial and reject the eval if they occur in any trial.

Use this compact scorecard:

| eval_id | case_type trigger/non-trigger | trials | triggers | accepted_activation | assertion_passes | assertion_denominator | current_result | prior_result | regressions/evidence |
| ------- | ----------------------------- | -----: | -------: | ------------------: | ---------------: | --------------------: | -------------- | ------------ | -------------------- |

Acceptance criteria:

- Every planning trigger case has at least 9/10 desired activations.
- Every non-trigger case has at most 1/10 undesired activations.
- Required output assertions pass on 100% of accepted runs.
- Current-vs-prior comparison shows no material regression, or the behavior change is intentional and documented.

Reject the change when any acceptance criterion fails.

## Durable evidence

Keep raw prompts, transcripts, rejected runs, and grading notes under ignored
`eval-workspace/`. After the complete protocol is accepted, commit only the
compact scorecard under `evals/scorecards/`, using the format in
`evals/scorecards/README.md`. The committed scorecard must identify the
model, product surface, run date, tested commit, and one result for every eval
ID. Never infer or reconstruct missing trials.

## Manual evidence grading

For each accepted run, grade:

- Correct trigger/non-trigger behavior and scope mode.
- Read-only behavior.
- Evidence-backed current-state findings with no fabricated paths/symbols.
- Planning completeness matches available context.
- Requirements/invariants preserve contracts unless the prompt explicitly changes them.
- Ordered steps satisfy the step contract and avoid unrelated cleanup.
- Verification maps to changed behavior and affected boundaries.
- Readiness follows completeness and material-assumption rules.

Reject runs that implement code, silently broaden scope, invent repository details, hide material uncertainty, or produce a readiness status inconsistent with completeness.
