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

This repository does not include marketplace metadata, marketplace submission
packaging, or a marketplace publishing workflow. Any local marketplace wiring is
optional personal setup outside the repo workflow.

## Local Setup

Use Python 3.11 or newer for the full validation set and ensure Git is on PATH.
The repository-only checks continue to support Python 3.9. Select the intended
interpreter before creating a local virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell, install both pinned dependency sets and run all checks
without activating the environment:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -r requirements-spec.txt
.venv\Scripts\python.exe scripts/check.py
```

On Linux or macOS:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt -r requirements-spec.txt
.venv/bin/python scripts/check.py
```

The runner checks dependencies in the selected interpreter before starting any
gate. It does not install packages, fetch Git refs, run behavioral model evals,
commit changes, or publish anything. Missing setup returns exit code 2. A failed
gate stops the runner and returns that gate's nonzero exit code. The runner emits
UTF-8 output and configures Python child processes for UTF-8, including when
output is redirected and repository paths contain non-ASCII characters.

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

Run the checks that match your change. The single command below runs repository
validation, Agent Skills specification validation, deterministic tests, plugin
build/parity validation, and staged and unstaged whitespace checks:

```bash
python scripts/check.py
```

Here and below, `python` means the selected environment's interpreter. Use the
explicit environment path from Local Setup if it is not active. The plugin
group replaces generated output at `dist/frey-skills`; canonical sources remain
untouched. Check symlink skips in test output; a skipped check is not a pass.

Select groups with repeatable `--group` arguments:

```bash
python scripts/check.py --group repository
python scripts/check.py --group spec
python scripts/check.py --group plugin
python scripts/check.py --group whitespace --base origin/main
```

The whitespace group checks both unstaged changes and the Git index. `--base`
adds committed whitespace checks from the merge base of an existing
local Git ref to `HEAD`. Fetch the intended base separately when needed. CI uses
these same groups on Ubuntu and runs the full set on Windows and macOS with
Python 3.12.

The plugin group includes `scripts.test_content_trust_contracts`, the focused
skill contracts, and bundle/release tests. The repository group includes the
validator, review-context helper, runner, workflow contracts, and offline
installation smoke assertion tests.

The repository validator checks Agent Skills frontmatter fields, local
references, optional eval schema and fixture references, committed scorecard
schema, OpenAI agent metadata, and single trailing newlines for recognized text
files. The separate `skills-ref` command provides an upstream specification
check.

## Installation Smoke Checks

CI also runs real Skills CLI installations on Windows, Linux, and macOS. These
checks are separate from `check.py` because they need Node.js, npm, Git, and
public network access. Install the exact CLI version without lifecycle scripts,
then invoke the smoke runner with its JavaScript entry point:

```bash
npm install --prefix dist/smoke-tools --no-save --ignore-scripts --no-audit --no-fund skills@1.7.2
python scripts/smoke_install.py --cli dist/smoke-tools/node_modules/skills/bin/cli.mjs
```

Use Node.js 24 and Python 3.11+ for this command. The runner verifies the CLI
version, stages the checkout's canonical skills without local runtime caches,
and separately installs the documented `v1.8.1` GitHub source pin. That tag must
still resolve to its recorded commit. Each source is checked with default and
explicit `--copy` installation, first selecting only `code-review`, then all
skills. `--list` must leave the project empty. Installed skill names, file sets,
and bytes must match the selected source, including supporting resources.

All installations use owned temporary directories with spaces and Unicode in
their paths, disposable child-process homes, disabled installer telemetry, and
no persisted checkout credentials. Existing files in the disposable user's home
must remain unchanged. No real agent installation is modified, and skill helper
scripts are inspected as bytes rather than executed. Commands have a timeout;
nonzero exits, file mismatches, and unavailable network access fail the job.

After installing the CLI, use `--source checkout` to check only the current
checkout without fetching GitHub sources. Use `--source pinned` to select only
the documented release. Offline assertion tests remain part of `check.py` and
do not invoke Node.js, npm, or the real installer. These are installation/file
checks; they do not test agent discovery, activation, or model behavior.

## Generated Plugin Development

Edit canonical sources first:

- root skill directories for skill behavior
- `plugin-template/.codex-plugin/plugin.json` for plugin manifest data
- `scripts/build_plugin.py` or `scripts/validate_plugin_bundle.py` for bundling
  logic

Then rebuild and validate:

```bash
python scripts/build_plugin.py --force
python scripts/validate_plugin_bundle.py dist/frey-skills
```

The generated bundle must match distributable canonical skill sources
byte-for-byte. Python bytecode, `__pycache__`, and `.pytest_cache` are local
runtime artifacts and are excluded; a generated bundle containing them fails
parity validation. Canonical skill roots and template paths must remain inside
the repository without symlink or junction traversal; discovery, build, and
parity checks reject linked source paths. If a release changes the plugin's published behavior or
manifest contract, update the
semantic version in `plugin-template/.codex-plugin/plugin.json` in the same
change.

For versioned GitHub releases, follow `RELEASING.md`. Publication requires an
authorized matching tag from a reviewed commit on `main`; it remains separate
from local validation and marketplace submission.

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
- Confirmation that no marketplace submission step is part of the repo
  workflow, and that any GitHub release publication is separately authorized.
