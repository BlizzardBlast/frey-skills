# Baseline and Verification Rules

## Baseline commands

Prefer non-mutating commands:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git diff --name-status
git diff --cached --name-status
git ls-files --others --exclude-standard
```

Resolve a comparison base only when required, in this order: user-provided base, `origin/HEAD`, `origin/main`, `main`, `origin/master`, `master`.

Record plan-owned and unrelated dirty paths separately. Do not stash, reset, clean, or broadly restore files to simplify execution.

## Existing failures

Run only focused baseline checks needed to distinguish existing failures from execution regressions. Record commands and results. When no baseline check was run, say so rather than implying a clean baseline.

## Verification evidence

For each step, record:

- command or inspected artifact;
- exit/result status;
- behavior proved;
- known limitation; and
- whether a failure existed before the step.

Use an equivalent repository command only when it proves the same objective and record the substitution as a minor deviation.

## Generated files

Identify canonical source using repository documentation, generator configuration, headers, build scripts, or history. Edit the canonical source and regenerate only when the plan authorizes generation and the command is understood.
