# Legacy scorecards

Behavioral model evals are not run or required for `implementation-plan`.
Existing scorecards in this directory are legacy reference artifacts. They are
not merge evidence and must not be presented as certification that model
behavior was tested.

Do not infer, reconstruct, or fabricate missing trials. Do not add a scorecard
for an eval run that was not actually performed.

A legacy JSON scorecard contains:

- `version`, fixed at `1`;
- `skill_name`, fixed at `implementation-plan`;
- `model`, `product_surface`, `run_date`, and tested `skill_commit`; and
- one result for every referenced eval ID.

Each result records `case_type`, `trials`, `triggers`, `accepted_activation`,
`assertion_passes`, `assertion_denominator`, `automatic_failures`, `result`, and
optional `notes`. The repository validator checks structure, eval-ID coverage,
and count consistency only; passing validation does not prove that any model run
occurred.
