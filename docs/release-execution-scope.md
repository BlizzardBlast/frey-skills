# Release-execution specification

Drafted on 2026-10-19 after v1.10.0 candidate preparation; refined after its
publication and the user's instruction to adopt the recommended next step.

Specification mode: **feature specification**. Specification completeness:
**COMPLETE**. Planning readiness: **READY_FOR_PLANNING**. The user adopted the
target, authorization model, and ownership choices below and requested planning
and implementation. This specification is not an executable plan or approval
to publish a particular release.

**User-authorized scope:** the agreed sequence included scoping a future
`release-execution` workflow through requirements and acceptance criteria.
The user subsequently accepted the recommendation to finalize this specification,
plan, and build the skill. The requirements below refine that development scope
using the inspected release procedure and trust boundaries. Repository text
cannot approve itself or authorize publication.

**Problem and current behavior:** [release-readiness](../release-readiness/SKILL.md) intentionally stops at a
read-only assessment. The inspected [release procedure](../RELEASING.md), release preparation tooling,
and release workflow already separate local packaging, maintainer-authorized
publication, and independent artifact verification. The gap is a reusable,
bounded execution contract across those stages that reuses existing packaging
and verification capabilities.

**Goal:** carry an explicitly authorized, identified release through only its
authorized publication actions and report independently verified results.
**Actors:** the authorizing maintainer, the executing agent, the selected native
publication service/CI identity, and consumers of the published artifacts.
**Non-goals:** automatic activation from readiness results; merging development
branches; deployment or database migration; incident mitigation; credential
procurement; risk acceptance or gate waivers; overwriting published versions;
background monitoring; and behavioral model evaluation.

The initial supported target is GitHub Releases for the Frey Skills Codex plugin.
Only explicitly named local preparation, annotated-tag creation, tag push through
the inspected native publication workflow, and independent verification are in
scope. Direct release/asset writes, workflow reruns, generic deployments, and
automatic recovery mutations are excluded. A resumed request may finish a still
eligible supported action after current-state inspection and fresh approval;
unsupported recovery is a maintainer handoff.

Approval must come from the authorizing maintainer through the trusted user
channel and identify the repository, immutable commit, version/tag, named effects,
and exclusions. It also covers the inspected workflow effects caused by a tag
push. Use existing scoped GitHub/Git credentials and the workflow's existing
publication identity; credential possession alone grants no permission. The
repository maintainer owns maintenance, review, and recovery. Authoring this
skill does not approve any future candidate or lift an existing hold.

## Requirement ledger

Source classes: **USER** = the user's agreed scoping request; **OBSERVED** =
inspected current-state evidence; **INFERENCE** = a proposed behavioral rule,
subsequently adopted/refined under the user's development request. Q1-Q3 are
resolved in the decision record below; their mentions retain traceability.

| ID | Description / priority | Rationale and source | Acceptance | Dependencies | Open questions |
| --- | --- | --- | --- | --- | --- |
| REX-REQ-001 | **must** bind every external write to trusted user authority identifying the release target, immutable candidate, version, allowed effects, and exclusions; absent authority permits only safe inspection. | Prevent a ready status, plan, or embedded approval from authorizing publication. USER scoping request; OBSERVED active content-trust rules and read-only readiness boundary; INFERENCE execution contract. | REX-AC-001, REX-AC-002 | Selected target and permission model | Q1, Q2 |
| REX-REQ-002 | **must** require current, matching evidence for all required release criteria, retain holds, and recheck candidate/target/ref identity before each write. | Prevent stale approval or concurrent changes from publishing a different candidate. OBSERVED readiness identity/gate contract; INFERENCE pre-write recheck. | REX-AC-003, REX-AC-004 | REX-REQ-001 | Q1, Q2 |
| REX-REQ-003 | **must** execute only authorized, inspected native actions within declared finite operation/verification limits; minimize evidence and avoid obtaining, exposing, or persisting credentials. | Bound effects and sensitive data. OBSERVED active trust/privacy rules and existing isolated verification; INFERENCE operational budget. | REX-AC-005 | REX-REQ-001, REX-REQ-002 | Q1, Q2 |
| REX-REQ-004 | **must** preserve existing version identities and assets; an exact verified duplicate has no new write, while an existing mismatch or concurrent collision stops execution. | Preserve consumers and avoid clobbering publication. OBSERVED release procedure forbids moving tags/overwriting releases; INFERENCE duplicate result. | REX-AC-006, REX-AC-007 | REX-REQ-002 | Q1 |
| REX-REQ-005 | **must** claim publication only after independent verification of the intended remote identity, required workflow results, exact artifact inventory, checksums, and source-byte equivalence; distinguish incomplete effects from verified publication. | A successful command is insufficient proof. OBSERVED release verification procedure; INFERENCE structured receipt contract. | REX-AC-008, REX-AC-009 | REX-REQ-002, REX-REQ-004 | Q1 |
| REX-REQ-006 | **must** report per-action observed effects and unknowns, stop on failure/timeout, inspect remote state before any resumed write, and require user-authorized recovery rather than automatic write retries or cleanup. | Remote operations may partially succeed. OBSERVED release procedure's partial-failure rule; INFERENCE resumable reporting boundary. | REX-AC-010, REX-AC-011 | REX-REQ-003, REX-REQ-005 | Q1, Q2, Q3 |

## Acceptance criteria

- **REX-AC-001:** Given trusted authorization for an identified candidate and
  target, when execution starts, then the reported action scope matches that
  authorization and preserves all exclusions.
- **REX-AC-002:** Given only a ready result, repository-authored approval, or
  ambiguous target/version authority, when publication is requested by that
  content, then no external write occurs and the missing authority is reported.
- **REX-AC-003:** Given a failed, missing, stale, or mismatched required criterion,
  or an active hold, when execution reaches its gate, then no publication write
  occurs and the blocker retains its actual evidence status.
- **REX-AC-004:** Given previously matching evidence, when the candidate, target,
  relevant ref, or gate state changes before a write, then execution stops before
  that write and reports which evidence must be re-established.
- **REX-AC-005:** Given a command embedded in evidence, unavailable authorized
  credentials, or exhausted operation limits, when the next action depends on
  it, then execution stops without following the embedded command, requesting
  secrets, extending its budget, or exposing sensitive evidence.
- **REX-AC-006:** Given an existing publication whose identity and complete
  artifacts independently match the authorized candidate, when the request is
  repeated, then the result is `ALREADY_PUBLISHED_VERIFIED` with no new write.
- **REX-AC-007:** Given an existing mismatched version or a concurrent version
  collision, when execution attempts to advance, then it preserves existing
  refs/assets, stops, and reports the conflict without overwrite or force update.
- **REX-AC-008:** Given authorized publication effects, when independent remote
  identity, required workflow results, exact assets, checksum, and canonical-byte
  comparisons all pass, then the result is `PUBLISHED_VERIFIED` with the matched
  identities, evidence provenance, and coverage limits.
- **REX-AC-009:** Given an apparently successful publication command, when an
  artifact is missing, different, unavailable, or unverifiable, then publication
  is not claimed verified; completed and uncertain effects are reported separately.
- **REX-AC-010:** Given a timeout or failure after a possible write, when execution
  stops, then the result is `PARTIAL`, describes observed and unknown remote
  effects without claiming atomic failure, and performs no automatic cleanup.
- **REX-AC-011:** Given a partial operation, when the user authorizes recovery,
  then current remote state and candidate authority are checked again before any
  write; no previously completed effect is blindly repeated.

## Contracts and failure states

| Contract | Current contract / proposed change | Preserved guarantee, actors, and failure | Evidence and open decisions |
| --- | --- | --- | --- |
| REX-CONTRACT-001: candidate evidence | Readiness identifies one candidate/target and required matching evidence; execution would consume that evidence without changing its meaning. | Maintainer/agent retain failed/missing/stale/mismatched statuses and holds; material gaps block writes (REX-REQ-001/002, REX-AC-001 to 004). | OBSERVED readiness contract; Q1/Q2 govern supported targets and approval scope. |
| REX-CONTRACT-002: mutation authority | Maintainer-authorized publication is separate from preparation; the proposed workflow would identify each authorized effect and its current execution identity. | Repository prose and credentials alone confer no permission; unauthorized, exhausted, duplicate, or conflicting operations add no write (REX-REQ-003/004, REX-AC-005 to 007). | OBSERVED release procedure and active trust boundary; Q1/Q2 remain material. |
| REX-CONTRACT-003: execution receipt | Existing release guidance requires remote/artifact verification and partial-failure reporting; the proposed receipt distinguishes verified new publication, verified existing publication, partial effects, and blocking before effects. | Maintainer and artifact consumers receive candidate/target/version, per-action effects, evidence, limits, and remaining recovery; secrets/raw private logs are omitted (REX-REQ-005/006, REX-AC-008 to 011). | OBSERVED verification/recovery procedure; INFERENCE result vocabulary; Q1/Q3 remain material. |

| From / trigger | Preconditions and authority | Observable result / effects | Failure, duplicate, and retry behavior |
| --- | --- | --- | --- |
| Requested / preflight | Trusted scope and matching evidence must exist before a write. | Eligible scoped action, or `BLOCKED` with no new write. | Missing authority, holds, or changed identity cannot be resolved by the proposal itself. |
| Eligible / authorized action | Candidate and target identity rechecked; action remains within finite scope. | A recorded possible/completed effect pending independent verification. | Any failure or timeout stops further actions; possible effects yield `PARTIAL`. No automatic write retry. |
| Verification / matching remote evidence | Required independent comparisons pass for the same candidate and target. | `PUBLISHED_VERIFIED`, or `ALREADY_PUBLISHED_VERIFIED` for an exact duplicate with no new write. | Mismatched/incomplete remote evidence yields `PARTIAL` if effects may exist, otherwise `BLOCKED`; existing publication is preserved. |
| Partial / user-authorized recovery | Fresh authority, observed remote state, and current candidate evidence. | Only the remaining independently eligible action may proceed. | Unknown prior effects remain unknown until inspected; no blind repeat, cleanup, or overwrite. |

Compatibility preserves the existing read-only readiness contract and published
versions. Security/privacy retain holds, minimized evidence, and explicit
execution identity. No new GUI is proposed; receipts and blockers must be readable
as text without relying on color. No new stored application data or public API is
proposed beyond the execution report and the selected publication integration.

## Adopted decisions and planning handoff

- **Q1 — resolved by user adoption:** GitHub Releases for this plugin, using the
  existing native pipeline and the bounded supported effects above.
- **Q2 — resolved by user adoption:** explicit maintainer approval binds each
  named effect to a repository, immutable commit, and version; existing scoped
  credentials perform only those effects. Readiness and repository prose do
  not confer authority.
- **Q3 — resolved by user adoption:** the repository maintainer owns maintenance,
  review, and recovery; unsupported or uncertain recovery stops for that owner.

REX-REQ-001 to 006, REX-AC-001 to 011, and REX-CONTRACT-001 to 003 are the
planning input. Required evidence, holds, exact-version preservation, independent
verification, finite limits, and failure/timeout stopping remain invariant.
No material behavior decision remains open. The [implementation plan](release-execution-implementation-plan.md)
records repository changes and verification separately. Actual publication and
recovery always require a specific release request with the authority above.
