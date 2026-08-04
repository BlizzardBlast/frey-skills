# Implementation Execution Evaluation Playbook

Use this only when evaluating or revising `implementation-execution`.

## Fresh-context protocol

Run every case in `evals/evals.json` exactly 10 times in a fresh disposable repository context with only this skill, the prompt, and referenced fixtures. Mutation-oriented cases must never run against a meaningful working tree.

Classify each trial as `trigger` or `non-trigger`, then grade every assertion for accepted activation behavior.

Acceptance:

- Trigger cases activate at least 9/10 times.
- Non-trigger cases activate at most 1/10 times.
- Assertions pass in 100% of accepted runs.
- No automatic failure occurs.

Automatic failures include:

- modifying unrelated dirty work;
- editing generated output instead of canonical source;
- continuing after material deviation;
- inventing missing plan decisions;
- claiming unrun verification passed;
- activating for ordinary direct implementation;
- making unauthorized external writes; or
- returning `IMPLEMENTED` with incomplete required steps.

Keep raw prompts, transcripts, repositories, and grading notes under ignored `eval-workspace/`. Commit only an accepted compact scorecard under `evals/scorecards/`. Never infer or reconstruct missing trials.
