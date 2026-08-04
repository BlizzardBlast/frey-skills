# Hypothesis Ledger

Use this reference when several explanations remain plausible or when an investigation risks anchoring on the first suspicious component.

## Ledger format

| ID     | Hypothesis                  | Supporting evidence   | Contradicting evidence                       | Discriminating check               | Status |
| ------ | --------------------------- | --------------------- | -------------------------------------------- | ---------------------------------- | ------ |
| DBG-H1 | Proposed causal explanation | Concrete observations | Concrete counter-evidence or `none observed` | Smallest safe distinguishing check | OPEN   |

Allowed statuses are `OPEN`, `SUPPORTED`, `CONFIRMED`, `REJECTED`, and `BLOCKED`.

## Causal quality rules

- A hypothesis must predict observable behavior. Vague labels such as “cache issue” or “race condition” are not sufficient without a mechanism.
- Prefer checks that separate two or more plausible hypotheses over checks that merely collect more of the same evidence.
- Record contradictory evidence even when the hypothesis remains favored.
- Do not promote a hypothesis from `SUPPORTED` to `CONFIRMED` solely because a suspicious change is recent.
- A passing rerun may weaken a deterministic-failure hypothesis but does not confirm a flaky root cause.
- Preserve rejected hypotheses so later investigators do not repeat already-disproved paths.

## Root cause versus contributing factors

The root cause is the earliest actionable divergence that explains the symptom. Contributing factors may increase probability, hide detection, worsen impact, or make recovery harder without independently causing the failure.

When several conditions are jointly necessary, represent them as one causal chain and list secondary conditions under contributing factors rather than confirming multiple competing root causes.
