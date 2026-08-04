# Legacy behavioral evaluation scorecards

Behavioral model evals are not run or required for any skill in this repository.
The evaluation playbooks, fixtures, and scorecards are retained only as legacy
reference material. They are not merge gates and must not be presented as
certification that model behavior was tested.

Existing scorecards may remain under:

```text
<skill>/evals/scorecards/<model-and-surface>.json
```

Do not infer, reconstruct, or fabricate missing trials. Do not create a new
scorecard for an eval run that was not actually performed.

`scripts/validate_repository.py` may validate committed scorecards against the
current `evals/evals.json`. The validator checks JSON structure, eval-ID
coverage, trial counts, and count relationships. Passing that deterministic
validation means only that the committed legacy artifact is structurally
consistent; it does not reproduce, verify, or certify any model run.

`template.json` remains available only to document the historical scorecard
shape. A legacy scorecard contains:

- the model, product surface, run date, and tested commit;
- one result for every referenced eval ID;
- trial, activation, assertion, and automatic-failure counts; and
- a recorded `pass` or `fail` result.
