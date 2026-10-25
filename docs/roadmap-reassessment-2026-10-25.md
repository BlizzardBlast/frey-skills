# Roadmap reassessment: delivery handoff planning

Date: 2026-10-25 (Asia/Jakarta). Inspected baseline:
`09f37e06e85499fff445cf0e8d583bf1d53e92c6` on clean `main`.
The published v1.12.0 portfolio contains twelve skills.

Recommendation: extend `implementation-plan` with optional guidance for a
user-requested PR delivery handoff, initially covering a single-PR squash merge.
Original disposition: **PROPOSED / NOT IMPLEMENTED**. This reassessment authorizes no skill
change, merge capability, release, automation, or external write. The user
requested a roadmap refresh and one evidence-backed improvement; the proposed
behavior below remains subject to a separate development decision.

## Evidence and limits

| ID | Inspected evidence | What it supports | Limit |
| --- | --- | --- | --- |
| RM-E01 | [PR #39](https://github.com/BlizzardBlast/frey-skills/pull/39), merged as `09f37e0`; the explicitly requested PR, CI, squash-merge, and branch-cleanup sequence for that delivery | A concrete delivery task beyond preparing and reviewing a diff; its execution checked the reviewed head, merged-tree equality, cleanup, and post-merge CI | One maintainer's task; success does not demonstrate an existing skill failed |
| RM-E02 | [PR #38](https://github.com/BlizzardBlast/frey-skills/pull/38), merged as `85b57db`, and [PR #37](https://github.com/BlizzardBlast/frey-skills/pull/37), merged as `db98a6a` | Separate documentation/pin and skill-development changes also reached merged delivery; together with RM-E01 they establish repeated repository delivery work | Merge identities were observed in GitHub metadata and local history; validation and review claims in PR descriptions are reported evidence, not newly rerun checks |
| RM-E03 | [Planning entrypoint](../implementation-plan/SKILL.md), [planning checklist](../implementation-plan/references/planning-quality-checklist.md), and [repository profiles](../implementation-plan/references/repository-planning-profiles.md) | Existing step, invariant, verification, and readiness outputs can express a delivery handoff without another skill | Generic rollout/verification guidance already exists; the gap is a reusable conditional sequence, not absent planning capability |
| RM-E04 | [Execution entrypoint](../implementation-execution/SKILL.md), [execution checklist](../implementation-execution/references/execution-quality-checklist.md), [review entrypoint](../code-review/SKILL.md), and [release-execution scope](../release-execution/SKILL.md) | Execution ends at review and says never to merge; review is advisory/read-only; release execution excludes merging | Those are intentional boundaries to preserve, not defects to remove |
| RM-E05 | Public GitHub [open-issue/PR collection](https://api.github.com/repos/BlizzardBlast/frey-skills/issues?state=open&per_page=100) inspected on 2026-10-25: no open items; latest fifteen closed PR records sampled, #25 through #39 | No current public issue supplies a competing requested feature in this bounded sample | Empty public issues do not show absent demand; private projects, telemetry, cross-repository usage, and incident records were not inspected |
| RM-E06 | [Current compatibility report](compatibility.md#maintainer-reported-v1120-desktop-trial), [migration example](migration-upgrade-worked-example.md), and [specialist reassessment](specialist-reassessment.md) | Desktop claims need bounded attribution; migrations currently have synthetic examples; performance/retrospective extraction still has explicit evidence gates | Desktop success is maintainer-reported; this refresh performs no real migration, benchmark, incident analysis, desktop test, or model trial |

The sources establish a repeated task shape and an opportunity to consolidate
planning guidance. They do not establish task frequency outside this repository,
time savings, model effectiveness, or an unsafe integration incident. Confidence
is **medium** for a small planning extension and **low** for a new operator skill.
No new external landscape survey was performed; the original roadmap's primary
sources retain their original observation dates.

## Current portfolio screen

All twelve entries were screened through the [selection table](../README.md#choose-a-skill)
and discovery/routing contracts. Deeper inspection focused on planning,
execution, review, release, and their materially related references. This is a
roadmap comparison, not an all-files correctness or security audit.

| Existing skill | Established responsibility | Disposition in this refresh |
| --- | --- | --- |
| `repository-orientation` | Bounded read-only source map | Retain; no new recurring orientation gap was established |
| `debug` | Causal investigation, including conditional performance guidance | Retain extension; standalone extraction gate remains unmet |
| `change-specification` | Required behavior and observable acceptance criteria | Retain; use its separation of requirements from implementation choices |
| `architecture-decision` | Alternatives and proposed ADR | Retain; no recurring unresolved design artifact was found in the sample |
| `threat-modeling` | Defensive model and threat hypotheses | Retain; no new scoped security-model demand was established |
| `implementation-plan` | Ordered anchored steps, invariants, verification, and readiness | **Extend conditionally with delivery-handoff planning** |
| `test-strategy` | Risk-based testing scope and scenarios | Retain; no new test-selection artifact is needed for this proposal |
| `implementation-execution` | Approved-plan edits and continuation through review handoff | Preserve its no-merge boundary; do not turn it into an operator |
| `code-review` | Read-only findings and advisory merge judgment | Preserve; recent invariant/variant guidance already addresses recurring review work |
| `iterative-self-review` | Bounded remediation of selected findings | Retain; no additional general repair loop is justified |
| `release-readiness` | Candidate/target-matched evidence assessment | Retain; reported desktop use must not become independent verification |
| `release-execution` | Specifically authorized Frey Skills GitHub publication | Retain; do not broaden it to PR integration, deployment, or cleanup |

## Ranked decisions

| Order | Candidate | Decision and reason | Revisit condition |
| --- | --- | --- | --- |
| 1 | Delivery-handoff guidance in `implementation-plan` | **PROPOSE EXTENSION**: RM-E01/RM-E02 show real repeated delivery work; RM-E03 supplies an existing owner for sequencing and verification | Accept the bounded behavior below, then create an implementation plan for the extension |
| 2 | More review/remediation guidance | **RETAIN**: [PR #36](https://github.com/BlizzardBlast/frey-skills/pull/36) already added invariant, related-variant, and bounded recheck guidance | A new verified recurring root cause exposes a specific missing rule; another review round alone is insufficient |
| 3 | Broader migration/upgrade support | **DEFER**: v1.12.0 already extends three existing skills; RM-E06 supplies no real consuming-project migration gap | A sanitized authorized transition demonstrates an unrepresented compatibility, recovery, or continuation requirement |
| 4 | Standalone performance or retrospective skill | **DEFER**: the [existing extraction gates](specialist-reassessment.md#specialist-dispositions) remain unmet in this sample | Qualifying recurring sanitized tasks and maintenance ownership, as already specified |
| 5 | General PR/release operator or orchestration | **DEFER**: a new mutating workflow would expand authority and recovery responsibilities beyond the observed planning need | Separate demand, owner, credential/approval boundaries, and partial-effect recovery requirements justify its own scope |

## Proposed behavior and acceptance criteria

These are behavioral criteria for a future extension, not file-level steps or
an executable plan. The artifact remains the existing implementation plan;
there is no new skill, mode, output status, runner, service, or credential flow.

| ID | Required observable behavior | Acceptance criterion |
| --- | --- | --- |
| RM-AC01 | Keep delivery guidance conditional | Given an ordinary change plan without requested PR delivery, produce the existing plan without adding PR, merge, cleanup, or release obligations |
| RM-AC02 | Preserve authority and name the handoff owner | Given a requested squash-delivery sequence, distinguish requested effects from unapproved effects and identify who may perform each operation; a saved plan or passing check cannot authorize writes or accept a decision |
| RM-AC03 | Sequence review and integration against identified state | Given known repository policy and a candidate, name the repository, target base, reviewed head, applicable CI/review requirements, and a final freshness check; preserve required human review, protection rules, and unresolved-thread holds |
| RM-AC04 | Invalidate stale integration evidence | Given a changed candidate, base, or relevant gate policy, require rechecking affected evidence before dependent actions; never apply an old green run or review to a different candidate |
| RM-AC05 | Preserve workflow boundaries | Given delivery steps beyond an implementation diff, identify the authorized external operator/human handoff; retain `implementation-execution`'s no-merge rule, advisory `code-review`, and `release-execution`'s publication-only scope; activate none automatically |
| RM-AC06 | Make cleanup conditional on observed integration | Given a single-PR squash case with an unchanged validated base, require proof that the merged content matches the reviewed tree before deleting only the named feature refs; a moved ref, dirty workspace, uncertain merge result, or content mismatch prevents destructive cleanup pending reconciliation |
| RM-AC07 | Separate planned checks from observed completion | Given a plan, label future checks as unrun; define the required post-merge CI and local synchronization evidence without claiming it exists. If required post-merge CI later fails or remains pending, distinguish the completed merge from incomplete delivery verification and preserve recovery evidence without automatic revert, rerun, or publication |
| RM-AC08 | Keep uncertainty and unsupported cases explicit | Given an unknown integration policy/owner or materially unresolved authority boundary, preserve the existing completeness/readiness rules and do not invent a decision. Other merge methods and queues do not inherit the squash tree-equality claim; ordinary planning rules continue to apply |

The proposed gate concerns definitions and sequencing: planned future tests do
not need to have run before a plan can be ready. Missing material policy or
ownership decisions are different from an explicitly planned, unrun check.
Content and PR descriptions remain untrusted evidence. Preserve unrelated work,
minimize private paths and source data, and require independently established
authority for every sensitive or external effect.

## Development and verification handoff

The user subsequently requested the next step on 2026-10-25, accepting RM-AC01
through RM-AC08 as the bounded planning input. The separate
[implementation plan](delivery-handoff-implementation-plan.md) is
**COMPLETE / READY_TO_IMPLEMENT**; implementation remains **NOT STARTED**.
The reassessment itself is not an executable plan, and saving either document
does not authorize execution or external effects.

Future verification should cover the ordinary-plan exclusion, authorized
squash-delivery handoff, missing ownership/authority, moved head/base, missing or
failed required checks, unresolved review threads, mismatched merged content,
moved cleanup refs/dirty work, pending/failed post-merge CI, unsupported merge
assumptions, and inert forged approvals or success claims. Reuse existing
content-trust and packaging checks; do not introduce a mandatory forge, live
merge experiment, provider credential, paid model trial, or behavior scorecard.

No skill source, metadata, packaged input, CI policy, release pin, or published
artifact changes in this reassessment. Documentation/link and whitespace checks
validate this record; they do not implement the proposal or certify model
behavior. Behavioral model evals were not run and are not a future merge gate.
