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
- Clean handoffs to implementation planning, review, or remediation workflows.

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

### code-review

Performs read-only, evidence-backed reviews for pull requests, diffs, targeted
files, repository snapshots, and stale review comments.

**Scope modes:**

- `diff review`
- `targeted audit`
- `repository audit`
- `review-comment triage`

**What it enforces:**

- A coverage matrix for every requested or materially applicable concern.
- Explicit review completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Severity-ranked finding ledger with stable IDs and verification guidance.
- Decision semantics: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
- A handoff ledger to `iterative-self-review` when fixes are requested.

### iterative-self-review

Runs an explicit-only remediation loop for a provided issue ledger, user-scoped
defects, failing tests, or review comments.

**What it enforces:**

- Baseline capture before editing.
- Scoped fixes by issue ID or user instruction.
- A default maximum of 3 review/fix/verify passes.
- Early stop when scoped issues are resolved and focused verification is
  recorded.
- Honest `RESOLVED`, `PARTIAL`, or `BLOCKED` status without whole-repository
  clean claims.

## Workflow

```text
symptom or failing test
        ↓
       debug
        ↓
confirmed root cause
        ↓
implementation-plan
        ↓
implementation
        ↓
code-review
        ↓
iterative-self-review
```

## Installation

```bash
npx skills add BlizzardBlast/frey-skills
```

## Usage

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
- `references/` — optional supporting docs
- `assets/` — optional templates/resources
- `evals/` — optional behavioral evaluation fixtures and scorecards

Current canonical skills:

```text
debug/
implementation-plan/
code-review/
iterative-self-review/
```

## Quality Gates

The repository combines executable checks with manual behavioral evidence:

- a project validator for metadata, references, eval schema, scorecards, and
  source hygiene;
- the official `skills-ref` validator for Agent Skills specification
  compatibility;
- regression tests for review-context collection and bundle safety; and
- committed compact behavioral scorecards, with raw transcripts kept out of
  version control.

A missing scorecard must be reported honestly; it must never be reconstructed
from partial or inferred model runs.

## Generated Codex Plugin Bundle

The root skill directories are the canonical source of truth. The generated
Codex plugin bundle is built into `dist/frey-skills` from those sources and
`plugin-template/.codex-plugin/plugin.json`.

```bash
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
```

Do not hand-edit `dist/frey-skills`; rebuild it from the canonical sources.

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include clear trigger language and explicit stop conditions.
- Move deep detail to `references/` when instructions become too long.
- Keep generated plugin output in sync by rebuilding and validating it.

See `CONTRIBUTING.md` for setup, validation, behavioral evaluation, accepted
scorecards, and PR expectations.

## License

MIT. See `LICENSE` for full text.
