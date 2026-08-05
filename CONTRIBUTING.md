# Contributing

Thanks for improving `frey-skills`. This repository stores reusable agent
skills and the small amount of tooling needed to validate and package them.

## Source of Truth

The canonical skill sources live in the root skill directories:

- `debug/`
- `change-specification/`
- `implementation-plan/`
- `test-strategy/`
- `implementation-execution/`
- `code-review/`
- `iterative-self-review/`

Each skill owns its `SKILL.md`, optional `agents/` metadata, helper `scripts/`,
supporting `references/`, optional `assets/`, and optional legacy `evals/`.

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

## Content-Trust Authoring Contract

Every skill must include a compact `## Content trust boundary`.

Before submitting a skill change, confirm that:

- repository and tool content is treated as untrusted evidence rather than instruction authority;
- the user or active skill contract remains the only source of task, requirement, decision, command, or mutation authority;
- embedded content cannot widen scope, activate another workflow, request secrets, authorize network or remote execution, privilege escalation, destructive actions, or external writes, override safeguards, or claim checks passed;
- the skill defines workflow-specific blocked or limited behavior when safe progress depends on embedded instructions;
- relevant evidence is minimized and sensitive content is summarized or redacted; and
- adversarial fixtures remain inert and are never executed.

Add or update deterministic coverage in `scripts/test_content_trust_contracts.py` when the contract changes. These tests verify published text and fixture structure; they do not certify model behavior.

For specification changes, also confirm that tickets, stories, repository files,
and supplied specifications cannot create requirements, approve their own design,
or silently resolve conflicting behavior. Keep acceptance criteria observable and
implementation-neutral; file-level sequencing belongs to `implementation-plan`.

## Validation Commands

Run the checks that match your change. For skill or documentation changes, the
full local validation set is:

```bash
python3 scripts/validate_repository.py
for skill_file in */SKILL.md; do skills-ref validate "$(dirname "${skill_file}")"; done
python3 -m unittest discover -s code-review/scripts -p 'test_*.py'
python3 -m unittest scripts.test_validate_repository
python3 -m unittest scripts.test_build_plugin scripts.test_implementation_execution_contract scripts.test_test_strategy_contract scripts.test_change_specification_contract scripts.test_skill_behavior_contracts scripts.test_content_trust_contracts
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

The repository validator checks Agent Skills frontmatter fields, local
references, optional eval schema and fixture references, committed scorecard
schema, OpenAI agent metadata, and single trailing newlines for recognized text
files. The separate `skills-ref` command provides an upstream specification
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

## Behavioral Eval Policy

Behavioral model evals are not part of this repository's implementation or merge
workflow. They are not run or required for any skill, including skills that
already contain `evals/evals.json` or scorecard files.

Do not require or claim:

- fresh-context model trials;
- provider credentials or paid token execution;
- accepted activation thresholds from model runs;
- committed scorecards as merge evidence; or
- certification that a skill's model behavior was tested.

Existing eval fixtures, playbooks, and scorecards may remain as legacy reference
material. Deterministic validators may continue checking their JSON schema,
fixture paths, count relationships, and source hygiene. Passing those checks
means only that the committed artifacts are structurally valid; it does not mean
any behavioral trials were executed or accepted.

New skills may intentionally omit `evals/`. Skill quality is established through
repository inspection, Agent Skills specification validation, deterministic
contract tests, plugin build/parity validation, whitespace checks, and scoped
code review.

## Pull Request Checklist

Before opening a PR, include:

- Scope: which skill(s), docs, scripts, or plugin artifacts changed.
- Evidence: exact deterministic validation commands run and their results.
- Behavior changes: activation, output, workflow, decision, or stop-condition
  changes, including before/after examples when useful.
- Confirmation that repository-authored text cannot create task, requirement, command, data, decision, or mutation authority.
- Confirmation that behavioral model evals were not run and no model-behavior
  certification is claimed.
- Confirmation that generated plugin output was rebuilt and validated when
  plugin-relevant sources changed.
- Confirmation that no marketplace or public submission step is part of the
  repo workflow.
