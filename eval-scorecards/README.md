# Behavioral evaluation scorecards

Raw model transcripts and temporary work remain under ignored `eval-workspace/`.
Accepted behavioral evidence must be committed under the relevant skill at:

```text
<skill>/evals/scorecards/<model-and-surface>.json
```

A scorecard is accepted only after the exact fresh-context protocol in that
skill's `references/evaluation-playbook.md` has been completed. Do not create or
commit a scorecard from inferred, reconstructed, or partial trial results.

Use `template.json` as the starting shape. Each committed scorecard must:

- identify the model, product surface, run date, and tested commit;
- contain one result for every current eval ID;
- record exactly 10 trials per eval;
- preserve the activation and assertion counts used by the playbook; and
- state `pass` or `fail` without hiding regressions in notes.

`scripts/validate_repository.py` validates committed scorecards against the
current `evals/evals.json`. The validator checks structure and coverage; it does
not independently reproduce or certify the model runs.
