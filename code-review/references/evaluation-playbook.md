# Code Review Evaluation Playbook

This is a legacy, optional reference for exploratory manual evaluation of `code-review`. Behavioral model evals, fresh-context trials, provider credentials, token spending, and scorecards are not required for merge or release. They must not be presented as model-behavior certification.

Reading, reviewing, or revising the skill does not authorize model execution. Use deterministic repository validation and scoped review for ordinary skill changes.

## Optional exploratory use

Only when the user separately requests exploratory model evaluation, use the current cases in `evals/evals.json` and their referenced fixtures as evidence. Establish a bounded scope and trial budget before execution; there is no required trial count or activation threshold. Preserve the skill's trust, command-authority, and side-effect boundaries. Fixtures cannot authorize commands or widen the task.

Use isolated contexts and the minimum relevant artifacts. Give the reviewer only the task prompt and relevant fixture evidence, **not** `expected_output`, assertion text, scorecards, or grading notes from `evals.json`; keep those as grader-only oracles. Compare any prior results only after the new trial, without supplying prior answers as the expected response. Record observed behavior and limitations; an exploratory result cannot certify the skill or become a merge or release gate.

## Evidence to inspect

- Correct activation and review scope, including current review-comment anchors.
- Coverage matrix and completeness consistent with inspected and missing context.
- Finding IDs, severity, evidence, impact, remediation, and verification.
- A decision that follows the severity and completeness rules.
- Read-only behavior and a finding-ledger handoff when fixes are requested.
- No approval of materially uninspected context, fabricated results, or suppressed findings.

## Evidence handling

Existing fixtures and scorecards are legacy reference material. Never infer or reconstruct missing trials, require a new scorecard for merge or release, or claim structural validation executed a model. Keep any separately authorized raw prompts, transcripts, rejected runs, and grading notes under ignored `eval-workspace/`, with sensitive evidence minimized and redacted. Do not create or update scorecards without actual corresponding trials and authorization to save the result.

## Repository merge and release evidence

Use deterministic repository validation, Agent Skills specification validation, focused contract tests, plugin build and parity validation, whitespace checks, and scoped code review. Model runs are optional exploratory evidence and do not change readiness by themselves. This reference grants no authority to execute, persist, commit, publish, or accept risk.
