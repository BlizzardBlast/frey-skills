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

An upstream failure remains a failure when it violates the applicable dependency or system contract. Report the external owner and the local handling evidence separately. Do not use the repository boundary alone to rule out a defect, especially when propagation, retries, fallback, or recovery violate a local contract.

## Outcome and stopping cases

These are deterministic instruction cases, not executed model trials. Each case assumes no additional material gap beyond the stated condition. Complete outcomes require the materially relevant causal chain, local handling, and alternatives to be established.

| Case | Condition | Investigation completeness | Root-cause status |
| --- | --- | --- | --- |
| DBG-CASE-001 | An upstream outage violates its service contract; the causal chain and local handling are established | COMPLETE | CONFIRMED |
| DBG-CASE-002 | An upstream error exposes a local retry or fallback contract violation; the causal chain is established | COMPLETE | CONFIRMED |
| DBG-CASE-003 | The reported symptom and failure handling satisfy the applicable contracts; material alternatives are resolved | COMPLETE | NOT_A_DEFECT |
| DBG-CASE-004 | Safe checks no longer discriminate between plausible causes and no single cause is favored | PARTIAL | UNRESOLVED |
| DBG-CASE-005 | Evidence favors one cause but safe checks cannot supply the remaining material confirmation | PARTIAL | LIKELY |
| DBG-CASE-006 | Missing access or an unsafe diagnostic dependency prevents diagnosis | BLOCKED | UNRESOLVED |
| DBG-CASE-007 | A bounded flaky-sampling limit is exhausted without discriminating evidence or a favored cause | PARTIAL | UNRESOLVED |

Stop when no distinct safe check could materially change the conclusion. For repeated sampling, establish a discriminating rationale and finite limit before rerunning; stop at that limit. Return the ledger, remaining uncertainty, and smallest missing evidence without expanding access, repairing the system, or treating rerun success as a diagnosis.
