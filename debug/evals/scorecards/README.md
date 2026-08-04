# Accepted scorecards

Commit accepted compact behavioral scorecards for this skill in this directory.
Keep raw prompts, transcripts, rejected runs, and grading notes under ignored
`eval-workspace/`; never infer missing trials.

Each JSON scorecard must contain:

- `version`, fixed at `1`;
- `skill_name`, fixed at `debug`;
- `model`, `product_surface`, `run_date`, and tested `skill_commit`; and
- one result for every current eval ID.

Each result records `case_type`, exactly 10 `trials`, `triggers`,
`accepted_activation`, `assertion_passes`, `assertion_denominator`,
`automatic_failures`, `result`, and optional `notes`. The repository validator
checks coverage and count consistency against `evals/evals.json`.
