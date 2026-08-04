# Legacy scorecards

Behavioral model evals are not run or required for `implementation-execution`.
Existing scorecards in this directory are legacy reference artifacts. They are
not merge evidence and must not be presented as certification that model
behavior was tested.

Do not infer, reconstruct, or fabricate missing trials. Do not add a scorecard
for an eval run that was not actually performed.

A legacy scorecard identifies `implementation-execution`, contains one result
for every referenced eval ID, and follows the historical shape documented in
`eval-scorecards/README.md`.

The repository validator checks structure, eval-ID coverage, and count
consistency only. Passing validation does not prove that any model run occurred.
