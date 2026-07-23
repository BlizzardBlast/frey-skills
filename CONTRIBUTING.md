# Contributing

Thanks for improving `frey-skills`. This repository stores reusable agent
skills and the small amount of tooling needed to validate and package them.

## Source of Truth

The canonical skill sources live in the root skill directories:

- `code-review/`
- `implementation-plan/`
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

## Validation Commands

Run the checks that match your change. For skill or documentation changes, the
full local validation set is:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s code-review/scripts -p 'test_*.py'
python3 -m unittest scripts.test_validate_repository
python3 -m unittest scripts.test_build_plugin
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

The repository validator checks skill metadata, local references, eval fixture
references, OpenAI agent metadata, and single trailing newlines for source files.

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

Use this procedure:

1. Snapshot the prior skill text and relevant fixtures before editing.
2. Read each applicable case in the skill's `evals/evals.json`.
3. For each applicable eval, run 10 fresh-context attempts against the current
   skill.
4. Compare behavior with the prior skill or no-skill baseline, whichever is
   relevant to the change.
5. Score accepted runs with this assertion scorecard:
   - at least 90% of desired assertions are satisfied
   - no more than 10% of undesired behavior appears
   - 100% of accepted runs respect safety, scope, and activation boundaries
6. Record prompts, outputs or summaries, pass/fail decisions, and human notes
   under ignored `eval-workspace/`.

Do not present these manual checks as hosted model evals or CI. They are local
human-reviewed behavioral evidence.

## Pull Request Checklist

Before opening a PR, include:

- Scope: which skill(s), docs, scripts, or plugin artifacts changed.
- Evidence: exact validation commands run and their results.
- Behavior changes: activation, output, workflow, decision, or stop-condition
  changes, including before/after examples when useful.
- Manual eval evidence when a skill description or workflow changed.
- Confirmation that generated plugin output was rebuilt and validated when
  plugin-relevant sources changed.
- Confirmation that no marketplace or public submission step is part of the
  repo workflow.
