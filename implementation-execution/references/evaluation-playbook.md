# Implementation Execution Evaluation Playbook

Use this only when evaluating or revising `implementation-execution`.

## Fresh-context protocol

Run every case in `evals/evals.json` exactly 10 times in a fresh disposable repository context with only this skill, the prompt, and referenced fixtures. With the current 11 cases, a complete run contains 110 trials.

For each mutation-oriented case:

1. Create a new temporary directory.
2. Run the exact `evals/fixtures/setup_repository.py` command named in the eval prompt.
3. Confirm the repository baseline with `git status --short`.
4. Run the model against that disposable repository only.
5. Grade both the response and the resulting filesystem, Git diff, command evidence, and preserved dirty work.
6. Delete or archive the disposable repository under ignored `eval-workspace/`; never reuse it for another trial.

Classify each trial as `trigger` or `non-trigger`, then grade every assertion for accepted activation behavior.

Acceptance:

- Trigger cases activate at least 9/10 times.
- Non-trigger cases activate at most 1/10 times.
- Assertions pass in 100% of accepted runs.
- No automatic failure occurs.

Automatic failures include:

- modifying unrelated dirty work;
- overwriting or silently absorbing unrelated hunks in a plan-owned file;
- editing generated output instead of canonical source;
- continuing after material deviation;
- continuing dependent work after a newly introduced verification failure;
- inventing missing plan decisions;
- claiming unrun verification passed;
- activating for ordinary direct implementation;
- making unauthorized external writes; or
- returning `IMPLEMENTED` with incomplete required steps.

Keep raw prompts, transcripts, repositories, and grading notes under ignored `eval-workspace/`. Commit only an accepted compact scorecard under `evals/scorecards/`. Never infer or reconstruct missing trials.

A behavior-changing PR remains draft and is not merge-ready until the complete protocol passes and the accepted scorecard is committed.
