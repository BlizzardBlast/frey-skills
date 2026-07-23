# frey-skills

A collection of practical skills for AI coding agents. Skills are packaged
instructions and optional resources that help agents execute repeatable
workflows more reliably.

This repository is designed for the
[Agent Skills](https://agentskills.io/) ecosystem.

## Available Skills

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

## Installation

```bash
npx skills add BlizzardBlast/frey-skills
```

## Usage

Once installed, compatible agents can activate skills when the task context
matches each skill's activation rules.

**Example prompts:**

```text
Plan this feature against the current repository before editing.
```

```text
Use implementation-plan to tighten this migration plan and preserve backward compatibility.
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
- `evals/` — optional behavioral evaluation fixtures

Current layout:

```text
code-review/
├── agents/
│   └── openai.yaml
├── evals/
│   ├── evals.json
│   └── fixtures/
├── references/
├── scripts/
│   ├── collect_review_context.py
│   └── test_collect_review_context.py
└── SKILL.md
implementation-plan/
├── agents/
│   └── openai.yaml
├── evals/
│   ├── evals.json
│   └── fixtures/
├── references/
└── SKILL.md
iterative-self-review/
├── agents/
│   └── openai.yaml
├── evals/
│   ├── evals.json
│   └── fixtures/
├── references/
└── SKILL.md
```

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
personal setup outside this repo workflow.

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include required YAML frontmatter (`name` and `description`) in `SKILL.md`.
- Include clear trigger language so agents know when to activate the skill.
- Use short, actionable steps and explicit stop conditions.
- Move deep detail to `references/` when instructions become too long.
- Keep generated plugin output in sync by rebuilding and validating
  `dist/frey-skills`.

See `CONTRIBUTING.md` for setup, validation, manual behavioral evaluation, and
PR expectations.

## License

MIT. See `LICENSE` for full text.
