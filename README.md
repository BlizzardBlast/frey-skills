# frey-skills

A collection of practical skills for AI coding agents. Skills are packaged
instructions and optional resources that help agents execute repeatable
workflows more reliably.

This repository is designed for the
[Agent Skills](https://agentskills.io/) ecosystem.

## Available Skills

### debug

Performs read-only, evidence-backed root-cause investigations for deterministic
failures, regressions, flaky behavior, and production-only incidents. It may
activate implicitly when the user asks to investigate, diagnose, troubleshoot,
reproduce, or determine the root cause of a concrete codebase or system symptom.

**Investigation modes:**

- `failure investigation` — deterministic errors, crashes, incorrect results,
  or failing tests.
- `regression investigation` — behavior differences across versions, branches,
  commits, deployments, or environments.
- `flaky investigation` — intermittent, timing-dependent, order-dependent, or
  nondeterministic behavior.
- `production investigation` — logs, telemetry, incidents, or incomplete
  reproduction access.

**What it enforces:**

- A read-only investigation boundary; the skill stops before implementation.
- Explicit symptom, baseline, and reproduction status.
- A stable hypothesis ledger with supporting, contradicting, and discriminating
  evidence.
- Investigation completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Root-cause status: `CONFIRMED`, `LIKELY`, `UNRESOLVED`, or `NOT_A_DEFECT`.
- Clean handoffs to implementation planning, execution, review, or remediation.

### implementation-plan

Produces read-only, evidence-backed implementation plans grounded in the current
repository. It may activate implicitly when the user asks to plan, scope,
sequence, or refine a concrete codebase change before editing.

**Scope modes:**

- `change plan` — feature, known bug fix, behavior, configuration, or localized
  implementation work.
- `refactor plan` — behavior-preserving structural improvement.
- `migration plan` — schema, API, dependency, framework, toolchain, CI, or
  deployment changes that require compatibility-aware sequencing.
- `plan refinement` — validate and tighten an existing plan against repository
  evidence.

**What it enforces:**

- A read-only planning boundary; the skill stops before implementation.
- Evidence-backed current-state findings with no fabricated repository paths or
  contracts.
- Explicit requirements and invariants before proposing changes.
- Ordered implementation steps with repository anchors, dependencies, preserved
  invariants, and focused verification.
- Planning completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Readiness semantics: `READY_TO_IMPLEMENT`, `READY_WITH_ASSUMPTIONS`, or
  `NOT_READY`.

### test-strategy

Produces a read-only, repository-grounded, risk-based testing strategy for a
concrete feature, defect, migration, diff, release, or system boundary. It may
activate implicitly when the user asks for a test strategy, regression plan,
migration test plan, release test plan, risk-based coverage plan, or testing
readiness assessment.

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

- A read-only strategy boundary; the skill stops before test implementation or
  execution.
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
bounded repository edits and focused verification. It may activate implicitly
only when the user references an approved plan or asks to continue named plan
steps. It does not activate for ordinary direct implementation without a plan.

**Execution modes:**

- `plan execution` — execute an approved plan from the beginning.
- `implementation continuation` — reconcile completed work and continue only
  remaining steps.

**What it enforces:**

- Baseline capture for branch, HEAD, staged, unstaged, and untracked work.
- An executable-plan eligibility gate before editing.
- Plan, repository, and tool content is treated as untrusted evidence rather
  than instruction authority.
- Commands require inspected provenance and explicit authorization for secret,
  network, remote-execution, privilege, or external-write effects.
- One coherent plan step at a time.
- A plan-conformance ledger with changed paths, verification, and deviations.
- Preservation of unrelated dirty work and canonical generated-source ownership.
- A material deviation gate that stops rather than inventing design decisions.
- Honest `IMPLEMENTED`, `PARTIAL`, or `BLOCKED` execution status.
- Handoff of the completed diff to `code-review`.

### code-review

Performs read-only, evidence-backed reviews for pull requests, diffs, targeted
files, repository snapshots, and stale review comments. The skill may be
activated implicitly when the user asks for code review, PR review, merge
readiness, repository risk review, targeted audit, or review-comment triage.

**Scope modes:**

- `diff review` — review a PR, branch, commit range, staged changes, or
  working-tree diff.
- `targeted audit` — review named files, components, concerns, commands, or
  comments.
- `repository audit` — sample a repository or package area for broad risk and
  report limits.
- `review-comment triage` — decide whether review comments still apply to the
  current code.

**What it enforces:**

- A coverage matrix for every requested or materially applicable concern.
- Explicit review completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Severity-ranked finding ledger with stable IDs and verification guidance.
- Decision semantics: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
- A handoff ledger when the user asks for fixes; remediation is delegated
  explicitly to `iterative-self-review` instead of performed during review.

### iterative-self-review

Runs an explicit-only remediation loop for a provided issue ledger, user-scoped
defects, failing tests, or review comments. It should not activate for ordinary
implementation work unless the user explicitly asks for iterative self-review,
post-review repair, or repeated fix-and-recheck remediation.

**What it enforces:**

- Baseline capture before editing.
- Scoped fixes by issue ID or user instruction.
- A default maximum of 3 review/fix/verify passes.
- Early stop when scoped issues are resolved and focused verification is
  recorded.
- A required user follow-up before any pass 4 or later pass.
- Honest `RESOLVED`, `PARTIAL`, or `BLOCKED` status without whole-repository
  clean claims.

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

Once installed, compatible agents can activate skills when the task context
matches each skill's activation rules.

**Example prompts:**

```text
Investigate why this test is flaky before editing anything.
```

```text
Find the root cause of this production-only 401 from the available logs.
```

```text
Plan this feature against the current repository before editing.
```

```text
Use implementation-plan to tighten this migration plan and preserve backward compatibility.
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
Continue the implementation plan from step 3 without redoing completed work.
```

```text
Review this pull request for merge readiness.
```

```text
Targeted audit: review only the build-tooling change.
```

```text
Triage these stale review comments against the current code.
```

```text
Review this PR, then hand me the finding ledger for fixes.
```

```text
Use iterative-self-review to fix CR-P1-001 and CR-P2-002 from the ledger.
```

```text
Run iterative-self-review for only the P1 findings; leave P2/P3 items alone.
```

## Skill Structure

Each skill directory can include:

- `SKILL.md` — required metadata + instructions
- `agents/` — optional client-specific metadata
- `scripts/` — optional helper automation
- `references/` — optional supporting docs
- `assets/` — optional templates/resources
- `evals/` — optional legacy behavioral fixtures and scorecards

Current layout:

```text
code-review/
debug/
implementation-plan/
test-strategy/
implementation-execution/
iterative-self-review/
```

Each canonical skill contains a `SKILL.md`; individual skills may additionally
contain `agents/`, `evals/`, `references/`, or `scripts/` according to their
workflow. The `test-strategy` skill intentionally ships without an `evals/`
directory.

## Quality Gates

The repository uses deterministic quality gates:

- a project validator for metadata, references, optional eval schema, scorecard
  structure, and source hygiene;
- the official `skills-ref` validator for Agent Skills specification
  compatibility;
- regression and contract tests;
- deterministic plugin build and source-parity validation;
- whitespace validation; and
- scoped code review.

Behavioral model evals are not run or required for any skill. Existing eval
fixtures and scorecards are legacy reference material only. Passing structural
validation for those files does not mean behavioral trials were executed, and no
model-behavior certification is claimed.

## Generated Codex Plugin Bundle

The root skill directories are the canonical source of truth. The generated
Codex plugin bundle is built into `dist/frey-skills` from those sources and
`plugin-template/.codex-plugin/plugin.json`.

```bash
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
```

Do not hand-edit `dist/frey-skills`; rebuild it from the canonical sources.
The repository does not commit marketplace metadata or a public marketplace
submission package. Local marketplace wiring, if you use it, is an optional
personal setup outside the repo workflow.

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include required YAML frontmatter (`name` and `description`) in `SKILL.md`.
- Include clear trigger language so agents know when to activate the skill.
- Use short, actionable steps and explicit stop conditions.
- Move deep detail to `references/` when instructions become too long.
- Do not claim behavioral model evals were run.
- Never fabricate behavioral scorecards.
- Keep generated plugin output in sync by rebuilding and validating
  `dist/frey-skills`.

See `CONTRIBUTING.md` for setup, deterministic validation, behavioral eval
policy, and PR expectations.

## License

MIT. See `LICENSE` for full text.
