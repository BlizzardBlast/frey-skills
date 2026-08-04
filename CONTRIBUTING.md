# Contributing

Thanks for improving `frey-skills`. This repository stores reusable agent
skills and the small amount of tooling needed to validate and package them.

## Source of Truth

The canonical skill sources live in the root skill directories:

- `debug/`
- `implementation-plan/`
- `implementation-execution/`
- `code-review/`
- `iterative-self-review/`

Each skill owns its `SKILL.md`, optional `agents/` metadata, helper `scripts/`,
supporting `references/`, optional `assets/`, and behavioral `evals/`.

The generated Codex plugin bundle lives at `dist/frey-skills` and is rebuilt
from the root skill directories plus `plugin-template/.codex-plugin/plugin.json`.
Do not hand-edit generated files in `dist/frey-skills`.

This repository does not include marketplace metadata, public submission
packaging, or a marketplace publishing workflow. Any local marketplace wiring is
optional personal setup outside the repo workflow.

## Local Setup

Install the development dependency used by the repository validators:

```bash
python3 -m pip install -r requirements-dev.txt
```

The CI specification check uses the official Agent Skills reference validator
on Python 3.11 or newer:

```bash
python3 -m pip install -r requirements-spec.txt
```

## Validation Commands

Run the checks that match your change. For skill or documentation changes, the
full local validation set is:

```bash
python3 scripts/validate_repository.py
for skill_file in */SKILL.md; do skills-ref validate "$(dirname "${skill_file}")"; done
python3 -m unittest discover -s code-review/scripts -p 'test_*.py'
python3 -m unittest scripts.test_validate_repository
python3 -m unittest scripts.test_build_plugin
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

The repository validator checks Agent Skills frontmatter fields, local
references, eval schema and fixture references, committed behavioral scorecards,
OpenAI agent metadata, and single trailing newlines for recognized text files.
The separate `skills-ref` command provides an upstream specification check.

## Generated Plugin Development

Edit canonical sources first:

- root skill directories for skill behavior
- `plugin-template/.codex-plugin/plugin.json` for plugin manifest data
- `scripts/build_plugin.py` or `scripts/validate_plugin_bundle.py` for bundling
  logic

Then rebuild and validate:

```bash
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
```

The generated bundle must match canonical skill sources byte-for-byte. If a
release changes the plugin's published behavior or manifest contract, update the
semantic version in `plugin-template/.codex-plugin/plugin.json` in the same
change.

## Manual Behavioral Evals

Run manual behavioral evals whenever a `SKILL.md` description, activation
boundary, output format, workflow, stop condition, or decision rule changes.
A behavior-changing PR is not merge-ready until these required trials pass and
an accepted scorecard is committed.

Use this procedure:

1. Snapshot the prior skill text and relevant fixtures before editing.
2. Read each applicable case in the skill's `evals/evals.json`.
3. For each applicable eval, run 10 fresh-context attempts against the current
   skill.
4. Run mutation-oriented evals only in disposable repositories created from the
   committed fixture setup; never use a meaningful working tree.
5. Compare behavior with the prior skill or no-skill baseline, whichever is
   relevant to the change.
6. Apply the exact acceptance thresholds from the skill's evaluation
   playbook:
   - trigger cases activate in at least 9 of 10 trials;
   - non-trigger cases activate in no more than 1 of 10 trials;
   - every required assertion passes in 100% of accepted runs; and
   - no automatic-failure condition occurs.
7. Keep prompts, transcripts, working notes, disposable repositories, and
   rejected runs under ignored `eval-workspace/`.
8. Commit the accepted compact scorecard under
   `<skill>/evals/scorecards/<model-and-surface>.json`, using
   `eval-scorecards/template.json` and the rules in
   `eval-scorecards/README.md`.

Do not infer or reconstruct missing trials. Do not present these manual checks
as hosted model evals or CI. They are local human-reviewed behavioral evidence,
with only the accepted compact scorecard committed for future regression
comparison.

## Pull Request Checklist

Before opening a PR, include:

- Scope: which skill(s), docs, scripts, or plugin artifacts changed.
- Evidence: exact validation commands run and their results.
- Behavior changes: activation, output, workflow, decision, or stop-condition
  changes, including before/after examples when useful.
- The committed accepted eval scorecard for every behavior-changing skill PR.
- If required behavioral trials have not passed, keep the PR in draft and state
  the missing evidence explicitly; do not waive the gate or fabricate results.
- Confirmation that generated plugin output was rebuilt and validated when
  plugin-relevant sources changed.
- Confirmation that no marketplace or public submission step is part of the
  repo workflow.
