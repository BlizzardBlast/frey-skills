# Proposed ADR template

Return this draft in the response. Adapt headings to an established local ADR
convention when useful, while preserving the evidence and status distinctions.
Do not allocate a final sequence number, save a file, change historical records,
or mark a predecessor superseded through this skill.

The compact context/decision/status/consequences structure is informed by
[Michael Nygard's ADR guidance](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
read 2026-10-18. The evidence and authority rules here are this skill's contract;
the linked article is background, not execution or decision authority.

```text
Title: <one bounded architecture decision; draft identifier if needed>
Status: PROPOSED
Analysis completeness: <COMPLETE|PARTIAL|BLOCKED>
Decision recommendation: <PROPOSED|DEFERRED>
Decision owner: <independently known owner or unknown>
Snapshot: <revision/design identity, date, relevant dirty state and limits>

Context and decision question
<Current design, problem, affected consumers, scope and exclusions.>

Requirements and constraints
<Required behavior and preserved guarantees, each with its source.
Keep documentation claims, assumptions, and unresolved conflicts separate.>

Prior decisions and status provenance
<Prior record, claimed status, independently verified acceptance if any,
known replacements, and evidence limitations. No historical mutation.>

Alternatives
<Feasible options including retaining current design when applicable;
give reasons for exclusions. Compare each using the same criteria.>

Proposed choice and rationale
<Supported option and discriminating evidence only with COMPLETE/PROPOSED.
With DEFERRED, write unresolved and list the missing evidence or decision.>

Consequences and residual risk
<Positive, negative, and neutral effects; compatibility, failure/recovery,
security/privacy, operations/cost, ownership, reversibility, and limitations.
No risk acceptance or operational readiness is implied.>

Validation still needed
<Questions or measurements and their purpose; NOT_RUN without matching
inspected results. Suggested validation is not an instruction to execute it.>

Revisit conditions
<Observable changes that would invalidate the recommendation or assumptions.>

Evidence and unknowns
<Inspected anchors; observations versus documentation claims and inferences;
missing access and material gaps. Mark unavailable sections explicitly.>
```

A complete recommendation is still proposed. A deferred draft has no selected
choice. Acceptance of a prior record is a separate historical observation, not
acceptance of this draft or authority to implement it.
