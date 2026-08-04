# Contributing

Thanks for improving `frey-skills`. This repository stores reusable agent
skills and the small amount of tooling needed to validate and package them.

## Source of Truth

The canonical skill sources live in the root skill directories:

- `debug/`
- `implementation-plan/`
- `test-strategy/`
- `implementation-execution/`
- `code-review/`
- `iterative-self-review/`

Each skill owns its `SKILL.md`, optional `agents/` metadata, helper `scripts/`,
supporting `references/`, optional `assets/`, and optional behavioral `evals/`.

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
python3 -m unittest scripts.test_build_plugin scripts.test_implementation_execution_contract scripts.test_test_strategy_contract
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

The repository validator checks Agent Skills frontmatter fields, local
references, optional eval schema and fixture references, committed behavioral
scorecards, OpenAI agent metadata, and single trailing newlines for recognized
text files. The separate `skills-ref` command provides an upstream specification
check.

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

## Behavioral Evals

Behavioral evals are required only when the affected skill owns an
`evals/evals.json` suite whose evaluation playbook declares the trials as a
release gate. A new skill may intentionally ship without behavioral evals. In
that case, the pull request must state that no eval suite exists and must rely on
specification validation, deterministic contract tests, plugin validation, and
scoped review evidence. Never invent missing trials.

For skills with an applicable eval suite, run manual behavioral evals whenever a
`SKILL.md` description, activation boundary, output format, workflow, stop
condition, or decision rule changes. Such a behavior-changing PR is not
merge-ready until the required trials pass and an accepted scorecard is
committed.

Use this procedure for applicable suites:

1. Snapshot the prior skill text and relevant fixtures before editing.
2. Read each applicable case in the skill's `evals/evals.json`.
3. For each applicable eval, run 10 fresh-context attempts against the current
   skill.
4. Run mutation-oriented evals only in disposable repositories created from the
   committed fixture setup; never use a meaningful working tree.
5. Compare behavior with the prior skill or no-skill baseline, whichever is
   relevant to the change.
6. Apply the exact acceptance thresholds from the skill's evaluation playbook.
7. Keep raw evidence under ignored `eval-workspace/`.
8. Commit the accepted compact scorecard under the skill's `evals/scorecards/`
   directory.

Do not infer or reconstruct missing trials. Do not present deterministic contract
tests as certification of model behavior.

`test-strategy` intentionally ships without an `evals/` directory. Adding a
behavioral suite for it requires a separate explicitly approved change.

## Pull Request Checklist

Before opening a PR, include:

- Scope: which skill(s), docs, scripts, or plugin artifacts changed.
- Evidence: exact validation commands run and their results.
- Behavior changes: activation, output, workflow, decision, or stop-condition
  changes, including before/after examples when useful.
- The committed accepted eval scorecard for each changed skill that owns an
  applicable release-gating eval suite.
- For a skill intentionally shipped without evals, explicit confirmation that no
  eval suite or scorecard exists and that no model-eval result is claimed.
- Confirmation that generated plugin output was rebuilt and validated when
  plugin-relevant sources changed.
- Confirmation that no marketplace or public submission step is part of the
  repo workflow.
