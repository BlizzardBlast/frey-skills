# Execution Quality Checklist

## Plan and scope

- [ ] The execution mode is stated.
- [ ] The plan source and eligibility are explicit.
- [ ] Material requirements, invariants, and exclusions are preserved.
- [ ] No missing design decision was invented.
- [ ] No unrelated cleanup or nearby defect fix was included.

## Baseline and ownership

- [ ] Branch, HEAD, staged, unstaged, and untracked state were captured.
- [ ] Plan-owned and unrelated dirty paths are distinguished.
- [ ] Existing hunks in dirty plan-owned files were classified before editing.
- [ ] Compatible partial work and unrelated same-file user hunks were preserved.
- [ ] Ambiguous or conflicting dirty target ownership caused execution to stop.
- [ ] Unrelated work was not overwritten, stashed, reset, or cleaned.
- [ ] Canonical source ownership was established before editing generated output.

## Step conformance

- [ ] Every plan step has a ledger row.
- [ ] Continuation mode verifies completed objectives and does not redo them.
- [ ] Changed paths belong to the step objective.
- [ ] Minor deviations are evidenced and recorded.
- [ ] Material deviations stop execution.

## Verification

- [ ] Every completed step has actual verification evidence.
- [ ] Failed or skipped checks are reported honestly.
- [ ] Pre-existing failures are distinguished from execution regressions.
- [ ] A newly introduced failure blocks the affected step and dependent work.
- [ ] Final integration checks are proportionate to affected boundaries.
- [ ] `IMPLEMENTED` is not used when required verification failed or was skipped.

## Handoff and external writes

- [ ] The completed diff is handed to `code-review`.
- [ ] Known finding-ledger remediation is delegated to `iterative-self-review`.
- [ ] No merge-readiness decision or self-approval was made.
- [ ] Commits, pushes, PRs, releases, deployments, migrations, and other external writes had explicit authorization.
