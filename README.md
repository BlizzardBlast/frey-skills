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

**Investigation modes:** `failure investigation`, `regression investigation`,
`flaky investigation`, and `production investigation`.

**What it enforces:**

- A read-only investigation boundary.
- Explicit symptom, baseline, reproduction, and evidence.
- A stable hypothesis ledger.
- `COMPLETE`, `PARTIAL`, or `BLOCKED` investigation completeness.
- `CONFIRMED`, `LIKELY`, `UNRESOLVED`, or `NOT_A_DEFECT` root-cause status.

### implementation-plan

Produces read-only, evidence-backed implementation plans grounded in the current
repository.

**Scope modes:** `change plan`, `refactor plan`, `migration plan`, and
`plan refinement`.

**What it enforces:**

- A read-only planning boundary.
- Evidence-backed current-state findings.
- Explicit requirements and invariants.
- Ordered repository-anchored implementation steps and focused verification.
- `COMPLETE`, `PARTIAL`, or `BLOCKED` planning completeness.
- `READY_TO_IMPLEMENT`, `READY_WITH_ASSUMPTIONS`, or `NOT_READY` readiness.

### implementation-execution

Executes, continues, or resumes an existing approved implementation plan through
bounded repository edits and focused verification. It does not activate for
ordinary direct implementation without an approved plan.

**Execution modes:**

- `plan execution` — execute an approved plan from the beginning.
- `implementation continuation` — reconcile completed work and continue only
  remaining steps.

**What it enforces:**

- Baseline capture for branch, HEAD, staged, unstaged, and untracked work.
- An executable-plan eligibility gate before editing.
- One coherent plan step at a time.
- A plan-conformance ledger with changed paths, verification, and deviations.
- Preservation of unrelated dirty work and canonical generated-source ownership.
- A material deviation gate that stops rather than inventing design decisions.
- `IMPLEMENTED`, `PARTIAL`, or `BLOCKED` execution status.
- Handoff of the completed diff to `code-review`.

### code-review

Performs read-only, evidence-backed reviews for pull requests, diffs, targeted
files, repository snapshots, and stale review comments.

**Scope modes:** `diff review`, `targeted audit`, `repository audit`, and
`review-comment triage`.

**What it enforces:**

- A coverage matrix for every requested or applicable concern.
- `COMPLETE`, `PARTIAL`, or `BLOCKED` review completeness.
- A severity-ranked finding ledger.
- `APPROVE`, `COMMENT`, or `REQUEST_CHANGES` decisions.
- Handoff of requested fixes to `iterative-self-review`.

### iterative-self-review

Runs an explicit-only remediation loop for a provided issue ledger, scoped
defects, failing tests, or review comments.

**What it enforces:**

- Baseline capture before editing.
- Scoped fixes by issue ID or user instruction.
- A default maximum of three review/fix/verify passes.
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
implementation-execution
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

Once installed, compatible agents can activate skills when the task context
matches each skill's activation rules.

**Example prompts:**

```text
Investigate why this test is flaky before editing anything.
```

```text
Plan this feature against the current repository before editing.
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
Use iterative-self-review to fix CR-P1-001 from the review ledger.
```

## Skill Structure

Each skill directory can include:

- `SKILL.md` — required metadata and instructions
- `agents/` — optional client-specific metadata
- `scripts/` — optional helper automation
- `references/` — optional supporting guidance
- `assets/` — optional templates or static resources
- `evals/` — optional behavioral evaluation fixtures and scorecards

Current layout:

```text
code-review/
debug/
implementation-plan/
implementation-execution/
iterative-self-review/
```

Every canonical skill contains a `SKILL.md`; individual skills may additionally
contain `agents/`, `evals/`, `references/`, or `scripts/` according to their
workflow.

## Quality Gates

The repository combines executable checks with manual behavioral evidence:

- project validation for metadata, references, eval schema, scorecards, and
  source hygiene;
- the official `skills-ref` validator for Agent Skills compatibility;
- regression tests for review-context collection and bundle safety;
- deterministic plugin build and source-parity validation; and
- compact behavioral scorecards when the exact fresh-context protocol has been
  completed.

Raw behavioral-eval transcripts and disposable repositories remain under ignored
`eval-workspace/`. Missing trials must be reported honestly and never
reconstructed or inferred.

## Generated Codex Plugin Bundle

The root skill directories are the canonical source of truth. The generated
Codex plugin bundle is built into `dist/frey-skills` from those sources and
`plugin-template/.codex-plugin/plugin.json`.

```bash
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
```

Do not hand-edit `dist/frey-skills`; rebuild it from canonical sources.

## Notes for Authors

- Keep each `SKILL.md` focused and task-oriented.
- Include valid YAML frontmatter and explicit activation boundaries.
- Define stop and completion conditions.
- Move deep detail to `references/`.
- Run mutation-oriented evals only in disposable repositories.
- Never fabricate behavioral scorecards.
- Keep generated plugin output in sync by rebuilding and validating it.

See `CONTRIBUTING.md` for setup, validation, behavioral evaluation, and PR
expectations.

## License

MIT. See `LICENSE` for full text.
