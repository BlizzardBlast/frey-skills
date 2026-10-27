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

Confidence and evidence basis
<Qualitative confidence in the recommendation with explicit reasons and limits;
not a calibrated probability or proof. With DEFERRED state why confidence is
insufficient, not an unjustified preference. Do not invent an agent or reviewer.>

Consequences and residual risk
<Positive, negative, and neutral effects; compatibility, failure/recovery,
security/privacy, operations/cost, ownership, reversibility, and limitations.
No risk acceptance or operational readiness is implied.>

Validation still needed
<List actually inspected evidence and separately any executed checks with
source/revision and result. Explicitly name material NOT_RUN and unavailable
validation, plus unknown implementation/decision acceptance. Treat checks as
NOT_RUN without matching inspected results. Suggestions are not instructions
to execute; do not imply a test passed by omission.>

Revisit conditions
<Observable falsifier or decision/ruling that would make this recommendation
wrong, and which option or comparison to revisit if known. A consequence or
cost of failure is not itself a falsifier.>

Open decision questions (only when needed)
<For PARTIAL/DEFERRED or BLOCKED/DEFERRED, include safely answerable material
questions when they exist: a stable draft-local reference if cited, why it
matters, owner or unknown, what evidence/answer is needed, and unanswered or
deferred status. If unsafe access prevents a useful question, report the blocker
elsewhere rather than inventing one. No fabricated human answers or automatic
acceptance. If no such question exists, omit this section.>

Evidence and unknowns
<Inspected anchors; observations versus documentation claims and inferences;
missing access and material gaps. Mark unavailable sections explicitly.>
```

A complete recommendation is still proposed. A deferred draft has no selected
choice. Acceptance of a prior record is a separate historical observation, not
acceptance of this draft or authority to implement it.
