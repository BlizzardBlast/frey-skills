# Debug Evaluation Playbook

Use this only when evaluating or revising the `debug` skill.

## Fresh-context method

Run each prompt in a fresh context with only this skill and the referenced fixture files. Grade current behavior against prior accepted patterns, but never expose prior answers to the model under test.

## Executable manual protocol

Model execution stays outside CI. CI validates fixture syntax, references, scorecard consistency, and formatting only.

For each case in `evals/evals.json`:

1. Run exactly 10 fresh-context trials with only the skill, prompt, and referenced fixture files.
2. Classify each trial as `trigger` or `non-trigger`.
3. For trials with accepted activation behavior, grade every listed assertion pass/fail.
4. Compare the result with the prior accepted scorecard for the same eval ID and record regressions with evidence.

Scoring:

- Trigger-case activation rate = trigger trials / 10. Accept when >= 9/10.
- Non-trigger undesired activation rate = trigger trials / 10. Accept when <= 1/10.
- Assertion pass rate = assertion-passing accepted trials / accepted trials. Accept only at 100%.
- Mutation, fabricated evidence, false reproduction, or `CONFIRMED` with `PARTIAL`/`BLOCKED` investigation automatically fails the affected trial and rejects the eval if it occurs in any trial.

Acceptance requires all trigger and non-trigger thresholds, 100% required assertions on accepted runs, no automatic failure, and no undocumented material regression.

## Manual evidence grading

Grade:

- correct activation and investigation mode;
- read-only behavior;
- symptom/baseline/reproduction accuracy;
- observed facts separated from inference and assumption;
- competing hypothesis quality and explicit statuses;
- discriminating checks rather than confirmation-seeking repetition;
- completeness and root-cause status consistency;
- correct handoff to planning, implementation, review, or remediation.

Reject runs that anchor on the first suspicious component, treat the final error as the root cause without tracing it, infer causation from recency, hide alternatives, or overclaim production/environment evidence.

## Durable evidence

Keep raw prompts, transcripts, rejected runs, and grading notes under ignored `eval-workspace/`. After the complete protocol is accepted, commit only the compact scorecard under `evals/scorecards/`. Identify the model, product surface, run date, tested commit, and one result for every eval ID. Never infer or reconstruct missing trials.
