# Code Review Skill Evaluation Playbook

Use this playbook to iteratively improve this skill using eval-driven feedback.

## 1) Trigger evaluation (description quality)

Create realistic should-trigger and should-not-trigger prompts.

- Include near-misses (mentions “review” but asks for implementation)
- Include implicit prompts (“Can you sanity-check this before merge?”)
- Run each query multiple times to account for model nondeterminism

Target:

- Should-trigger queries: trigger rate >= 0.5
- Should-not-trigger queries: trigger rate < 0.5

## 2) Output quality evaluation

Define scenario-based prompts and expected review outcomes.

For each scenario, evaluate:

- Severity assignment accuracy (P0-P3)
- Evidence quality (location + impact + fix)
- Architecture impact coverage
- Decision correctness (`APPROVE`/`COMMENT`/`REQUEST_CHANGES`)

## 3) Assertions

Prefer verifiable assertions such as:

- “Findings are grouped by P0-P3 in order.”
- “At least one blocker includes explicit remediation steps.”
- “Architecture impact is explicitly labeled low/medium/high.”

Avoid vague assertions like “review is good.”

## 4) Iteration loop

1. Run evals
2. Grade results with evidence
3. Identify recurring failure patterns
4. Update `SKILL.md` and/or references
5. Re-run evals in a new iteration

Stop when results plateau or failure patterns are resolved.

## 5) Cost-awareness

Track quality vs cost:

- Pass rate delta
- Token usage delta
- Duration delta

Keep the skill lean: remove instructions that add overhead without measurable quality gains.
