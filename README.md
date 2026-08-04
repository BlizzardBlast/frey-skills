# frey-skills

A collection of practical skills for AI coding agents. Skills are packaged
instructions and optional resources that help agents execute repeatable
workflows more reliably.

This repository is designed for the
[Agent Skills](https://agentskills.io/) ecosystem.

## Available Skills

### debug

Performs read-only, evidence-backed root-cause investigations for deterministic
failures, regressions, flaky behavior, and production-only incidents.

**Investigation modes:**

- `failure investigation`
- `regression investigation`
- `flaky investigation`
- `production investigation`

**What it enforces:** read-only investigation, explicit reproduction state, a
hypothesis ledger, honest completeness, and clean handoffs.

### implementation-plan

Produces read-only, evidence-backed implementation plans grounded in the current
repository.

**Scope modes:**

- `change plan`
- `refactor plan`
- `migration plan`
- `plan refinement`

**What it enforces:** current-state evidence, explicit requirements and
invariants, ordered repository-anchored steps, focused verification, planning
completeness, and implementation readiness.

### test-strategy

Produces a read-only, repository-grounded, risk-based testing strategy for a
concrete feature, defect, migration, diff, release, or system boundary.

**Scope modes:**

- `change test strategy` — focused feature, behavior, defect, configuration, or
  diff coverage.
- `regression test strategy` — protect established behavior after a confirmed
  defect, refactor, incident, or dependency change.
- `migration test strategy` — compatibility, data transition, rollback, and
  old/new version coverage.
- `release test strategy` — testing concerns for a release candidate, staged
  rollout, or production promotion.

**What it enforces:**

- A read-only boundary; it does not implement or execute tests.
- A prioritized risk matrix and observable contract inventory.
- Risk-to-layer and risk-to-scenario traceability.
- Explicit test data, environment, automation, and execution requirements.
- Entry and exit criteria plus residual risk.
- Strategy completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Test readiness: `READY`, `READY_WITH_GAPS`, or `NOT_READY`.

A test strategy is supplementary evidence. It is not an executable
implementation plan by itself and does not decide merge readiness or broader
release readiness.

### implementation-execution

Executes, continues, or resumes an existing approved implementation plan through
bounded repository edits and focused verification.

**Execution modes:**

- `plan execution`
- `implementation continuation`

**What it enforces:** baseline capture, an executable-plan gate, one coherent
step at a time, a plan-conformance ledger, preservation of unrelated work, a
material-deviation stop, and honest execution status.

### code-review

Performs read-only, evidence-backed reviews for pull requests, diffs, targeted
files, repository snapshots, and stale review comments.

**Scope modes:**

- `diff review`
- `targeted audit`
- `repository audit`
- `review-comment triage`

**What it enforces:** a coverage matrix, explicit completeness, a severity-ranked
finding ledger, merge-readiness decisions, and a remediation handoff.

### iterative-self-review

Runs an explicit-only remediation loop for a provided issue ledger, user-scoped
defects, failing tests, or review comments.

**What it enforces:** baseline capture, scoped fixes, a default three-pass limit,
focused verification, and honest `RESOLVED`, `PARTIAL`, or `BLOCKED` status.

## Workflow

The primary implementation lifecycle remains:

```text
symptom or failing test
        ↓
       debug
        ↓
confirmed root cause
        ↓
implementation-plan
        ↓
implementation-execution
        ↓
code-review
        ↓
iterative-self-review
```

`test-strategy` is an optional specialist workflow that can inform planning,
test implementation, review of test sufficiency, migration confidence, and
release testing. It is not a mandatory stage for every change.

## Installation

```bash
npx skills add BlizzardBlast/frey-skills
```

## Usage

Example prompts:

```text
Investigate why this test is flaky before editing anything.
```

```text
Plan this feature against the current repository before editing.
```

```text
Create a change test strategy for this feature.
```

```text
Design regression coverage for this confirmed defect.
```

```text
Create a migration test strategy covering old/new compatibility and rollback.
```

```text
Assess whether this release is test-ready from the available evidence.
```

```text
Execute the approved implementation plan.
```

```text
Review this pull request for merge readiness.
```

```text
Use iterative-self-review to fix CR-P1-001 and CR-P2-002 from the ledger.
```

## Skill Structure

Each skill directory can include:

- `SKILL.md` — required metadata and instructions
- `agents/` — optional client-specific metadata
- `scripts/` — optional helper automation
- `references/` — optional supporting documents
- `assets/` — optional templates or static resources
- `evals/` — optional behavioral fixtures and accepted scorecards

Current layout:

```text
code-review/
debug/
implementation-plan/
test-strategy/
implementation-execution/
iterative-self-review/
```

The `test-strategy` skill intentionally ships without an `evals/` directory. Its
initial quality gate uses Agent Skills specification validation, deterministic
contract tests, repository validation, plugin build/parity validation, and
scoped code review. No model-eval result or scorecard is claimed.

## Quality Gates

The repository combines:

- project validation for metadata, references, optional eval schemas,
  scorecards, and source hygiene;
- the official `skills-ref` validator;
- deterministic regression tests;
- deterministic plugin build and source-parity validation; and
- behavioral scorecards for skills that own an applicable release-gating eval
  suite.

Never reconstruct missing behavioral trials or present deterministic tests as
certification of model behavior.

## Generated Codex Plugin Bundle

The root skill directories are canonical. Build the generated bundle with:

```bash
python3 scripts/build_plugin.py --force dist/frey-skills
python3 scripts/validate_plugin_bundle.py dist/frey-skills
```

Do not hand-edit `dist/frey-skills`.

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include clear activation and non-trigger boundaries.
- Use explicit completion and stop conditions.
- Move deep detail to `references/`.
- Keep product-specific metadata in `agents/`.
- Never fabricate behavioral scorecards.
- Keep generated plugin output synchronized through the build process.

See `CONTRIBUTING.md` for validation and pull request expectations.

## License

MIT. See `LICENSE` for full text.
