# Contributing

Thanks for improving `frey-skills`. This repository stores reusable agent
skills and the small amount of tooling needed to validate and package them.

## Source of Truth

The canonical skill sources live in the root skill directories:

- `repository-orientation/` (unreleased)
- `architecture-decision/` (unreleased)
- `threat-modeling/` (unreleased)
- `debug/`
- `change-specification/`
- `implementation-plan/`
- `test-strategy/`
- `implementation-execution/`
- `code-review/`
- `iterative-self-review/`
- `release-readiness/`

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
On Linux and macOS, the repository group also requires `ps` on PATH to inspect
the owned processes in its timeout regression test. Install `ps` through your
operating system's package manager if it is missing; preflight reports this as
missing setup before running any checks. Windows and the other gate groups do
not require `ps`.

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

`scripts.test_release_readiness_contract` checks the published evidence matrix,
decision cases, authority and stop boundaries, discovery metadata, and worked
example. These are deterministic instruction contracts, not executed model
assessments or behavioral certification.

`scripts.test_repository_orientation_contract` checks routing and completeness
cases, snapshot and ownership evidence, command effects, saved-map trust,
bounded stopping, resources, and gate registration. Mutation cases
reject removed or misclassified published rules; they do not execute a model.
Its YAML metadata assertions run in `scripts.test_validate_repository`, where
PyYAML is an established dependency. `scripts.test_check` verifies that all plugin
contract modules load and contracts for all three unreleased skills run without
site packages, so the standalone plugin group remains standard-library-only.

`scripts.test_architecture_decision_contract` binds sixteen published conditions
to routing, analysis completeness, and recommendation outcomes, including
missing scale/cost evidence, conflicting requirements, superseded ADRs, and
forged acceptance. It checks the proposed ADR template, inert example, trust
fixture, resources, and gate integration. Mutation cases reject lost or altered
rules; they do not execute a model. YAML metadata assertions remain in repository
validation, which already provisions PyYAML.

`scripts.test_threat_modeling_contract` binds twenty-one published conditions to
routing, model completeness, and threat interpretation, including tenant
isolation, logging, callbacks, missing ownership, proposed controls, forged
acceptance, embedded diagram/log instructions, and reported controls whose
implementation remains unverified. It checks the system/ledger
fields, control evidence statuses, read-only and hold boundaries, worked example,
inert fixture, resources, and gate integration. Mutation cases reject lost or
altered cases; these are instruction contracts, not model or security certification.
YAML metadata assertions remain in repository validation.

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
and separately installs the documented `v1.9.0` GitHub source pin. That tag must
still resolve to its recorded commit. Each source is checked with default and
explicit `--copy` installation, selecting only `code-review` and all skills in
separate empty projects. `--list` must report exactly the expected skill names
without duplicates and leave the project empty. CLI 1.7.2 rejects `--list --json`,
so the runner checks its pinned listing format. Installed skill names, file sets,
and bytes must match the selected source, including supporting resources.

All installations use owned temporary directories with spaces and Unicode in
their paths, disposable child-process homes, disabled installer telemetry, and
no persisted checkout credentials. Existing files in the disposable user's home
must remain unchanged. No real agent installation is modified, and skill helper
scripts are inspected as bytes rather than executed. Command output uses
temporary files so inherited output handles cannot hold pipe readers open.
Timeouts terminate the owned process tree with bounded cleanup waits; nonzero
exits, cleanup failures, file mismatches, and unavailable network access fail
the job. A real nested-process regression test checks timeout cleanup on each
platform.

After installing the CLI, use `--source checkout` to check only the current
checkout without fetching GitHub sources. Use `--source pinned` to select only
the documented release. Offline assertion tests remain part of `check.py` and
do not invoke Node.js, npm, or the real installer. These are installation/file
checks; they do not test agent discovery, activation, or model behavior.

### Published plugin archive smoke check

Run the separate network check with Python 3.11+ and Git:

```bash
python scripts/smoke_release.py
```

CI runs this after the Skills CLI installation checks on Windows, Linux, and
macOS. It downloads the documented release's plugin ZIP and `SHA256SUMS`, checks
the digest, and compares every archive entry with the recorded Git tag/commit.
The manifest version and schema, license, complete skill set, and supporting-file
bytes must match that release's canonical sources, even when the current
checkout has changed. The release pin is shared with `smoke_install.py`; update
the documented tag and recorded commit together when intentionally changing it.

The checker reads downloaded helpers as bytes and never executes them. Each
download runs in an owned spawned process with a 60-second total deadline
covering connection setup and body reads. On expiry, the parent kills and reaps
that worker with a bounded five-second cleanup wait. Only completed downloads
are copied to a new destination; temporary partial files are removed. Offline
tests exercise real slow body reads, blocked connections, and worker cleanup.
Downloads also have size limits; unavailable assets, network failures, moved tags,
malformed checksums, and mismatches fail the command. Extraction requires a new
owned temporary directory and happens only after verifying the complete archive.
Unexpected paths, duplicates, links, encrypted entries, and extra caches fail
before extraction. All downloaded, cloned, and extracted files are temporary;
the command does not install a plugin or modify the user's agent configuration.

Offline regression tests run through `check.py` without network access. This
checks published file integrity and extraction, not Codex discovery, activation,
or model behavior. Client discovery and rollback have a separate check below.

### Codex client compatibility smoke check

The separate `codex-client` CI matrix checks Codex CLI metadata discovery on
Windows, Linux, and macOS. Use Python 3.11+, Git, Node.js, npm, and public network
access to reproduce it:

```bash
npm install --prefix ./dist/codex-smoke-cli --no-save --ignore-scripts --no-audit --no-fund @openai/codex@0.150.1
python scripts/smoke_codex.py --cli ./dist/codex-smoke-cli/node_modules/@openai/codex/bin/codex.js
```

The checker verifies the npm package and native executable version, then directly
supervises that executable. It downloads v1.8.2 and v1.9.0, checks each tag/commit,
checksum, and canonical archive bytes through the release checker, and installs
only those verified plugins into a disposable marketplace. It checks initial
installation, upgrade, and rollback with a fresh app-server for each phase.
Plugin ownership, enabled state, exact unique skill names, version-specific
cache paths, and all installed bytes must match. The current release must retain
its three starter prompts, and the previous release's prompts must also survive
installation and rollback. Upgrade adds the eighth skill, `release-readiness`;
rollback must restore exactly the previous seven. Update both release pins and
the compatibility record when intentionally changing the tested release pair.

Only `initialize`, `initialized`, `plugin/read`, and `skills/list` are sent. No
thread, turn, skill invocation, or behavioral model eval is started. Child homes,
config, and caches are disposable; credentials and inherited Codex settings are
excluded from their environment. An unrelated user-skill fixture must survive.
Each metadata session has a 60-second total deadline and bounded output. Windows
assigns the suspended server to a Job Object before it can spawn descendants;
closing the supervisor's job handle also terminates that tree after abrupt
supervisor exit. POSIX uses a new process group. Both paths terminate the owned
tree after success or failure and bound cleanup waits. Temporary-directory
cleanup retries Windows sharing violations for at most five seconds; persistent
locks still fail. Offline assertion and real subprocess tests run through
`check.py` without installing Codex or accessing the network.

These CLI results do not establish desktop plugin directory, selector, or restart
compatibility. Keep those results separate using the
[manual compatibility check](docs/installation.md#manual-plugin-compatibility-check).

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
