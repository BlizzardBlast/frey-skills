# frey-skills

A collection of practical skills for AI coding agents. Skills are packaged
instructions and optional resources that help agents execute repeatable
workflows more reliably.

This repository is designed for the
[Agent Skills](https://agentskills.io/) ecosystem.

## Available Skills

### iterative-self-review

Rigorously reviews newly written or refactored code in an iterative loop,
applies fixes, and prevents regressions or infinite fix-toggle cycles.

**Use when:**

- You just wrote new code and want a structured self-review pass
- You refactored existing logic and need regression-safe validation
- You explicitly ask the agent to "review your work"

**What it enforces:**

- Explicit issue discovery before applying fixes
- A repeatable fix-and-recheck loop until no issues remain
- An anti-loop safeguard after repeated implementation toggling
- Regression discipline so new fixes do not reintroduce old bugs

### code-review

Performs structured code reviews for pull requests and diffs, including
architecture impact checks, severity triage, and optional remediation loops.

**Use when:**

- You want a merge-readiness review of current changes
- You need severity-ranked findings (P0-P3) with concrete fixes
- You want a review decision: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`
- You need architecture/boundary impact validation before merge

**What it enforces:**

- Review scope and intent confirmation before deep analysis
- Consistent severity model for triaging risk
- Explicit architecture impact assessment (contracts, schema, auth, rollback)
- Evidence-based findings with impact and fix suggestions
- Optional review+fix iterative loop that composes with `iterative-self-review`
- Explicit completion criteria and clear next steps

## Installation

```bash
npx skills add BlizzardBlast/frey-skills
```

## Usage

Once installed, compatible agents can automatically activate the skill when the
task context matches.

**Example prompts:**

```text
Review your latest changes before finalizing.
```

```text
I refactored this module—do an iterative self-review and fix issues.
```

```text
Run a strict self-check on this implementation and prevent regressions.
```

```text
Review this pull request and give me severity-ranked findings before merge.
```

```text
Review this PR, then fix only P0/P1 findings in an iterative self-review loop.
```

## Skill Structure

Each skill directory can include:

- `SKILL.md` — required metadata + instructions
- `scripts/` — optional helper automation
- `references/` — optional supporting docs
- `assets/` — optional templates/resources

Current layout:

```text
code-review/
├── SKILL.md
├── references/
│   ├── architecture-impact-checklist.md
│   ├── evaluation-playbook.md
│   └── review-quality-checklist.md
└── scripts/
    └── collect_review_context.py
iterative-self-review/
├── SKILL.md
```

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include required YAML frontmatter (`name` and `description`) in `SKILL.md`.
- Include clear trigger language so agents know when to activate the skill.
- Use short, actionable steps and explicit stop conditions.
- Move deep detail to `references/` when instructions become too long.

## License

MIT. See `LICENSE` for full text.
