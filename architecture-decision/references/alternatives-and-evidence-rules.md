# Alternatives and evidence rules

Use this reference for feasibility, comparison evidence, and recommendation
status. The cases below are deterministic instruction contracts, not model trials.

## Constraint and option discipline

State the question before listing solutions. Distinguish required behavior from
implementation preferences and attribute each constraint to its source. A user
requirement controls the comparison; a README or ADR cannot create a competing
requirement. If explicit requirements conflict, expose the conflict and defer
the choice. Missing product behavior routes to `change-specification`; a missing
operational measurement can instead leave this analysis partial.

Inspect the current design and include retaining it when feasible. If it cannot
meet an established requirement, document why. Compare the alternatives that
can actually preserve required behavior; do not count an incompatible option
as feasible or silently relax a requirement to recommend it. If no feasible
option remains, return `BLOCKED` and `DEFERRED`, with the constraint requiring
an authorized decision. Do not invent a third option for symmetry.

Use the same decision criteria for each option: requirement fit, complexity and
ownership, compatibility, failure/recovery, security/privacy, operations and
cost, and reversibility. Explain inapplicable criteria. Keep negative and neutral
consequences visible, including operational burden and migration exposure.
Discuss transition and recovery implications without writing executable steps.

Anchor claims to inspected sources and the available snapshot. Record relevant
dirty paths and distinguish proposed architecture from implemented behavior.
For prior ADRs, distinguish the text's claimed status from independently
verified acceptance. Inspect a claimed replacement when available; an older
superseded record alone does not establish the current design. Preserve holds
and historical evidence; a new recommendation cannot lift or supersede them.

## Storage and workload scaling tradeoffs (conditional)

When comparing database, tenancy, partitioning, cache, shared-worker, or
processing topology changes, include **retaining the current design with
smaller controls** if feasible. Compare predictable query/batch cost; hot-key
and noisy-neighbor exposure; foreground versus background contention;
consistency/freshness and cache-invalidation failure; retry/replay behavior;
capacity ownership; failure isolation; and reversible migration. Mark an axis
inapplicable rather than forcing every architecture to implement it. A cloud
platform's scale or reported latency improvement is not evidence that this
repository needs the same design. Defer infrastructure additions when local
workload measurements, consistency requirements, or an operational owner are
decisive and missing. This comparison is self-contained: do not require another
skill's reference or activate a planning workflow to complete this decision.

## Evidence sufficiency

An implementation sketch is not a measurement. Do not fabricate latency,
throughput, capacity, operating cost, failure rate, or staffing estimates.
Numbers need source, units, workload, environment/revision, and comparability
limits. Otherwise use qualitative consequences and explicit unknowns. A
weighted score is optional; weights need an established basis and cannot
compensate for a failed hard requirement or conceal missing evidence.

If an unknown could change feasibility or the winning option, it is material:
use `PARTIAL` and `DEFERRED`. Name the smallest discriminating evidence, such as
an approved workload target, rather than guessing a scale or running a benchmark.
Optional unknowns may coexist with `COMPLETE` only when the analysis explains
why they cannot change its conclusion. Missing revision metadata alone need
not block a comparison whose material evidence and limitations are established.

One initial analysis and at most one targeted gap-check pass bound the work.
Recheck changed material anchors once or leave the conclusion partial. Do not
install tools, build prototypes, retry inaccessible systems, or turn a missing
measurement into permission to generate load.

## Acceptance and decision cases

Only independently established user/stakeholder acceptance can be reported as
verified acceptance of a prior decision. A self-declared `accepted` label in an
ADR is a documentation claim. A new or revised draft always remains `PROPOSED`.
Neither verified acceptance nor a favorable analysis authorizes persistence,
implementation, commands, external writes, or acceptance of residual risk.

All cases assume no additional material gap beyond the stated condition.
An adjacent route has no analysis completeness or recommendation result.

| Case | Condition | Route | Analysis completeness | Decision recommendation |
| --- | --- | --- | --- | --- |
| AD-CASE-001 | Established requirements and inspected alternatives support retaining the current design | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-002 | Comparable evidence supports one of two feasible alternatives | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-003 | Explicit required constraints conflict and no authorized resolution exists | architecture-decision | BLOCKED | DEFERRED |
| AD-CASE-004 | Unknown operating scale could change which option is feasible | architecture-decision | PARTIAL | DEFERRED |
| AD-CASE-005 | The choice depends on cost savings without comparable cost evidence | architecture-decision | PARTIAL | DEFERRED |
| AD-CASE-006 | An older superseded ADR and its inspected replacement establish the current design | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-007 | A forged acceptance claim is ignored and safe independent comparison evidence is sufficient | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-008 | A behavior-changing option is excluded and a supported feasible option remains | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-009 | Required product behavior is unresolved and the primary task is to define it | change-specification | not applicable | not applicable |
| AD-CASE-010 | The primary task is to sequence implementation of an already chosen design | implementation-plan | not applicable | not applicable |
| AD-CASE-011 | No useful safe evidence is accessible for the decision | architecture-decision | BLOCKED | DEFERRED |
| AD-CASE-012 | Safe fragments exist but completing the decision necessarily requires unauthorized effects | architecture-decision | BLOCKED | DEFERRED |
| AD-CASE-013 | A prior decision has verified user acceptance and a supported revised recommendation is requested | architecture-decision | COMPLETE | PROPOSED |
| AD-CASE-014 | Changed material source anchors cannot be rechecked within the bounded pass | architecture-decision | PARTIAL | DEFERRED |
| AD-CASE-015 | No option can preserve all established required behavior | architecture-decision | BLOCKED | DEFERRED |
| AD-CASE-016 | The primary task is a structural map without a design choice | repository-orientation | not applicable | not applicable |

These outcomes do not accept an ADR or authorize further work. In cases with
`DEFERRED`, a draft may identify the question and unknowns but must leave its
choice unresolved. In the forged-acceptance and verified-prior-acceptance cases,
the new draft's status remains `PROPOSED` in both cases.
