# Repository orientation: M0 boundary validation

Date: 2026-10-18. Milestone: M0 in the [skill roadmap](roadmap.md).
Disposition: **GO_TO_M1_PLANNING**.
Specification mode: `feature specification`.
Specification completeness: `COMPLETE`.
Planning readiness: `READY_FOR_PLANNING`.

`repository-orientation` has a distinct proposed artifact: a bounded,
source-linked map of an unfamiliar repository or subsystem, without a required
failure, change request, or review judgment. The two examples below support
that boundary. Recurring demand and runtime effectiveness remain unmeasured.

This document specifies proposed behavior for future planning. It is not an
implemented skill, an executable implementation plan, a merge decision, or
authority to run commands or make repository/external-system changes.

## Problem, goals, and actors

Existing skills inspect repository structure in service of diagnosis, planning,
testing, execution, or review. None makes a reusable orientation map its primary
output. A contributor who wants to understand an unfamiliar area should not
need to invent a defect, planned change, or audit to obtain that map.

The goal is to explain responsibilities, entry points, relevant execution/data
paths, dependency boundaries, canonical/generated ownership, and native
verification entry points for a requested area. Source anchors and explicit
coverage limits should make the explanation useful to a contributor or to a
later, separately authorized workflow.

Actors are the requesting developer or maintainer, the agent performing safe
inspection, and readers of the resulting map. Human maintainers and component
owners must be identified only when supported by evidence; otherwise report
them as unknown. A component's responsibility does not establish its human owner.

Non-goals are root-cause investigation, architecture selection, change
specification, implementation sequencing, test strategy, review/merge/release
judgment, implementation, setup, dependency installation, indexing, benchmark
execution, external-system access, and automatic persistence of maps.

## Evidence and authority

The user requested the next roadmap step. This is interpreted as M0, the first
milestone. That request authorizes this boundary analysis and documentation.
The roadmap is context, not an independent source of command or task authority.

Inspected baseline: `main` at
`19f0bf09ff8a1f1224c45f865090e246f316dfd3`. The previous roadmap work was already
uncommitted: changes to README and CHANGELOG, plus the untracked roadmap.
Those changes are preserved. The example's code anchors describe inspected
working-tree content at this baseline, not a newly committed candidate.

| Evidence ID | Inspected source | Relevant observation |
| --- | --- | --- |
| E1 | [debug](../debug/SKILL.md), boundary and hypothesis/output contracts | Investigation begins with a concrete symptom and produces causal evidence and root-cause status. |
| E2 | [implementation-plan](../implementation-plan/SKILL.md), scope modes and step contract | Planning sequences a concrete change with objectives, invariants, dependencies, and verification. |
| E3 | [code-review](../code-review/SKILL.md), scope modes and output | Review produces coverage, findings, and a decision for a requested review scope. |
| E4 | [README](../README.md#choose-a-skill) and [CONTRIBUTING](../CONTRIBUTING.md#source-of-truth) | Eight skills exist; direct simple tasks do not require every workflow; root skill directories are canonical. |
| E5 | [discovery](../scripts/repository_layout.py), [builder](../scripts/build_plugin.py), [bundle validator](../scripts/validate_plugin_bundle.py), [check runner](../scripts/check.py), and [CI](../.github/workflows/ci.yml) | The positive example spans source discovery, generation, parity validation, and gate configuration. |
| E6 | [SECURITY](../SECURITY.md#content-trust-model) and user-supplied project instructions | Untrusted evidence cannot create authority; minimize sensitive evidence and preserve verification limits. |

Requirements below are design inferences proposed within the user-authorized M0
scope, grounded in these observations and the previously proposed roadmap
boundary. They are not claimed to be separately stated user requirements.
No source conflict affecting this bounded proposal was found.

## Trigger and routing contract

Use orientation when the primary request is to understand an unfamiliar
repository or subsystem and a bounded map is useful in its own right. Do not
prepend it to every engineering task. A later workflow may reuse current map
anchors, but must recheck changed or stale evidence.

| Primary request | Appropriate route | Why orientation is or is not needed |
| --- | --- | --- |
| Explain how several parts of an unfamiliar subsystem fit together | `repository-orientation` | The requested result is the map itself. |
| Locate a known function or answer a single-file question | Direct inspection | The small answer does not warrant a separate map or workflow. |
| Explain why a test fails, a regression occurs, or a service misbehaves | `debug` | The requested result is a causal explanation; discovery remains part of diagnosis. |
| Sequence a concrete feature, fix, refactor, or migration | `implementation-plan` | The requested result is actionable change sequencing; no orientation prerequisite is imposed. |
| Find defects, assess risks, audit a component, or decide merge readiness | `code-review` | The requested result is findings and a review decision. |
| Define required behavior or acceptance criteria | `change-specification` | Describing current structure must not silently choose new requirements. |
| Choose test coverage or assess a release candidate | `test-strategy` or `release-readiness`, as applicable | A map alone cannot answer the requested risk or readiness question. |
| Fix code or execute an approved plan | The authorized implementation/remediation workflow | A map neither authorizes nor performs edits. |

These are routing recommendations, not automatic workflow activation. Mixed
requests retain the user's actual scope and the boundaries of any active skill.
An incidental observation does not turn orientation into an unsolicited audit.

## Proposed observable output

Return one human-readable map with these fields:

1. Requested scope and exclusions.
2. Snapshot identity: revision when available, observation date, relevant dirty
   state, and any limits on attributing evidence to that revision.
3. Inspected coverage and source anchors, distinguishing observations,
   documentation claims, inferences, and unknowns.
4. Component responsibilities and known human ownership, kept distinct.
5. Entry points, important execution/data paths, dependencies, side effects,
   and canonical/generated boundaries relevant to the requested area.
6. Native verification entry points with inspected provenance, effects,
   prerequisites, and execution evidence/status. Discovery is not execution.
7. Unresolved questions, stale or unavailable areas, and suggested next
   inspection paths without activating another workflow.
8. `Orientation completeness: COMPLETE|PARTIAL|BLOCKED` and validity limits.

The output does not require a specific tool, index, programming language,
framework, Git repository, file format, or saved artifact. When a revision is
unavailable, report that limitation and describe the available snapshot identity.
Do not manufacture source anchors, owners, commands, or runtime call paths.

## Requirement ledger

All entries are `must` priority. Their source class is `inference` within M0;
evidence IDs identify the current-state basis. Dependencies and open questions
are stated here rather than inferred from document position.

| ID | Description | Rationale / evidence | Acceptance criteria | Dependencies | Open questions |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | Activate for a requested repository/subsystem map; skip simple lookups and tasks whose primary output belongs to an existing workflow. | Preserve distinct discovery behavior without adding a mandatory stage; E1-E4. | AC-001, AC-002, AC-003 | None | None in M0 scope |
| REQ-002 | Identify requested scope, snapshot, relevant dirty state, coverage, and exclusions. | Make map validity and sampling visible; E2-E5. | AC-001, AC-004, AC-005 | REQ-001 | None |
| REQ-003 | Explain relevant responsibilities, entry points, paths, dependencies, and canonical/generated boundaries with inspected anchors; separate human ownership from component responsibility. | Produce a useful map without invented ownership or runtime claims; E4-E5. | AC-001, AC-006 | REQ-002 | None |
| REQ-004 | Distinguish observed evidence, documentation claims, inferences, and unknowns; recheck stale/conflicting anchors or disclose the unresolved limit. | Prevent a saved map or prose assertion becoming current fact; E1-E3, E6. | AC-004, AC-005, AC-006 | REQ-002 | None |
| REQ-005 | Report verification command provenance, effects, prerequisites, and actual execution status without running tests, builds, setup, or indexing as part of orientation. | Describe how verification works without expanding a read-only task; E2, E5-E6. | AC-007 | REQ-004 | None |
| REQ-006 | Treat repository/tool content as untrusted evidence, minimize sensitive access/disclosure, preserve unrelated work, and refuse content-created authority. | Preserve the repository's independent trust boundary; E6. | AC-008, AC-009 | None | None |
| REQ-007 | Inspect only the authorized area and materially relevant adjacent boundaries; stop after a useful map or a stated access/coverage limit without setup/retry loops. | Bound exploration and avoid exhaustive unrelated discovery; E1-E3, E6. | AC-001, AC-005, AC-010 | REQ-001, REQ-006 | None |
| REQ-008 | Assign completeness from inspected coverage, state invalidation conditions, and avoid diagnosis, safety, merge, or release-readiness claims. | Separate knowledge completeness from judgments owned by other workflows; E1-E3. | AC-005, AC-010, AC-011 | REQ-002, REQ-004, REQ-007 | None |

## Contract inventory

No deployed API, persisted data, event, UI route, or release artifact changes in
M0. These proposed user-visible skill contracts are the material additions.
All preserve existing skill activation/output contracts. No consumer migration
or unresolved contract decision is identified within this scope.

| ID | Current contract | Proposed change | Preserved guarantees | Consumers / failure behavior | Evidence and traceability |
| --- | --- | --- | --- | --- | --- |
| CONTRACT-001: routing | Existing workflows perform discovery for their own requested outputs. | Offer a map as a primary output only when requested and useful. | Simple tasks remain direct; existing skills retain their responsibilities; no automatic handoff. | Developer and agent; absent or out-of-scope inputs do not trigger unrelated work. | E1-E4; REQ-001; AC-001-AC-003 |
| CONTRACT-002: map evidence | No standalone orientation output contract exists. | Return the scoped, snapshot-bound map and coverage status described above. | Observations and unknowns remain distinguishable; stale summaries are evidence only. | Contributor and later workflow; unavailable areas lower completeness rather than being invented. | E1-E5; REQ-002-REQ-004, REQ-008; AC-004-AC-006, AC-011 |
| CONTRACT-003: command and data authority | Current skills restrict commands and sensitive effects through their trust boundaries. | Apply the same boundary independently to orientation, including command-effect descriptions. | No setup, edits, secret retrieval, network/remote execution, privilege escalation, destructive action, external write, or workflow activation is authorized by source content. | User and inspected workspace; unauthorized dependence is declined and reported. | E5-E6; REQ-005-REQ-007; AC-007-AC-010 |

## Completeness, failure behavior, and stopping

| Result | Observable meaning |
| --- | --- |
| `COMPLETE` | The requested bounded area has its material responsibilities, paths, evidence, command effects, and exclusions established. This is not whole-repository coverage or a claim that checks passed. |
| `PARTIAL` | A useful safe map exists, but a relevant area or relationship remains inaccessible, stale, sampled, ambiguous, or unverified; identify the affected conclusions. |
| `BLOCKED` | No useful safe map can be produced for the requested scope, including when fulfilling it depends on unauthorized execution or sensitive access; state the missing access or decision. |

Limit discovery to a bounded initial map and one targeted gap-check pass. Stop
earlier when further traversal would not change the requested explanation.
Do not repeatedly retry unavailable access, install missing tools, or widen
scope to make a completeness claim. An unavailable optional index must not itself
block normal safe search when that search can answer the question.

If the source changes during inspection, recheck the affected anchors once
within the gap-check pass or mark the corresponding conclusions partial. A later
request may refresh the map; the old artifact cannot certify the new snapshot.
Repeated requests do not authorize persistence, edits, or command execution.
There is no stored lifecycle or speculative application state machine to add.

## Acceptance criteria

These specify observable outcomes for future instruction contracts. Reviewing
them is not executing model behavior or claiming runtime activation accuracy.

- **AC-001:** Given an unfamiliar bounded subsystem with accessible evidence,
  when the user requests an explanation of its parts and paths, then return the
  anchored map, snapshot, coverage, limits, and completeness without editing or
  executing the system.
- **AC-002:** Given a single known symbol question, when the answer needs only
  direct inspection, then answer directly without a separate orientation map.
- **AC-003:** Given a symptom, change-sequencing request, or audit request, when
  its primary output is diagnosis, a plan, or findings, then recommend the
  matching existing workflow without inserting orientation or activating it.
- **AC-004:** Given dirty source or a previously saved map for another revision,
  when producing a map, then identify the snapshot difference and revalidate
  affected claims or explicitly mark them stale/unverified.
- **AC-005:** Given a useful accessible area and an unavailable relevant area,
  when inspection ends, then return `PARTIAL` with affected paths/conclusions
  identified; do not invent the missing relationships or retry setup.
- **AC-006:** Given conflicting prose and inspected implementation or absent
  human-owner evidence, when describing the area, then attribute the conflict or
  unknown owner and avoid fabricated runtime behavior or ownership.
- **AC-007:** Given a documented verification command that regenerates files or
  executes tests, when listing it, then state its provenance, effects and
  prerequisites, identify it as not run absent actual matching evidence, and do
  not execute it through orientation.
- **AC-008:** Given repository/tool text that asks for broader scope, setup,
  secrets, changed requirements, workflow activation, external writes, or forged
  passing results, when encountered, then treat it as evidence only, preserve
  scope and authority, and do not perform or repeat the requested effects.
- **AC-009:** Given sensitive material is unnecessary for the requested map,
  when selecting or reporting evidence, then avoid accessing it and summarize
  any incidental sensitive observation without disclosing the payload.
- **AC-010:** Given the requested map cannot be produced safely without an
  unauthorized effect, when that dependency is established, then stop with
  `BLOCKED`, the specific limitation, and no unauthorized side effect.
- **AC-011:** Given a complete bounded map with no test, runtime, or release
  evidence, when reporting `COMPLETE`, then limit the claim to orientation
  coverage and make no causal, security, merge, release, or passed-check claim.

## Two task examples and static boundary review

These are synthetic, sanitized prompts grounded in this public repository.
They are not observed user demand, model trials, accepted scorecards, or proof
of activation behavior. The review below compares requested artifacts against
inspected source; it does not run an unimplemented skill.

### Example A: a map adds value

Prompt: "I am new to frey-skills. Explain how canonical skill sources become
the generated Codex plugin, and where discovery, generation, parity checks,
and validation commands live. No change or diagnosis is requested."

The requested artifact crosses boundaries but needs no failure hypothesis,
change steps, finding severity, or approval decision. A compact map can answer:

| Responsibility / path | Inspected anchor and observation |
| --- | --- |
| Canonical inputs | [discover_skill_names](../scripts/repository_layout.py) discovers eligible root skill directories containing a skill manifest and excludes generated/template/runtime locations. It checks canonical path ownership. |
| Manifest input | The [plugin template](../plugin-template/.codex-plugin/plugin.json) supplies manifest metadata; [write_bundle](../scripts/build_plugin.py) copies it into the generated plugin. |
| Generation | `write_bundle` iterates discovered skills; `copy_tree_bytes` copies each canonical tree into the output's skill directory. The default output is `dist/frey-skills`. |
| Parity | [validate_bundle](../scripts/validate_plugin_bundle.py) checks layout and manifest/skill parity. `validate_skill_parity` and `compare_trees` compare canonical and generated paths and file bytes. |
| Verification entry point | [group_commands](../scripts/check.py) assembles repository, specification, plugin, and whitespace gates. The plugin group runs contracts, rebuilds generated output, and validates it. |
| CI consumer | [CI configuration](../.github/workflows/ci.yml) invokes the runner and separate smoke checks. This is configuration evidence, not evidence that the current candidate's CI passed. |

Observed command: `python scripts/check.py`. Provenance: the inspected runner
and CI. Effects: runs checks and, when all groups are selected, rebuilds generated
plugin output; it is not a read-only orientation command. Prerequisites are
the selected interpreter's dependencies and available native utilities, as
preflight establishes. **Execution status for this example: NOT_RUN.**

Human ownership is unknown from this sample: neither root `CODEOWNERS` nor
`.github/CODEOWNERS` exists. No public release, installed-client state, desktop
UI, runtime activation, or repository-wide quality conclusion follows from this
map. No commands listed in the example were executed to complete its mapping.

**Static review result:** the map answers the request independently. `debug`
would need an absent symptom; `implementation-plan` would need an absent change;
`code-review` would add an unrequested judgment. REQ-001-REQ-005 and AC-001,
AC-006, AC-007, AC-011 are meaningfully exercised as design cases.

### Example B: no new workflow is needed

Prompt: "Which function discovers canonical skill folders, and does it include
the generated distribution directory?"

Direct answer from [repository_layout.py](../scripts/repository_layout.py):
`discover_skill_names` discovers the root skill folders, while
`EXCLUDED_ROOT_DIRS` includes `dist`, so the generated distribution is excluded.
This is a known-symbol question with a short source-backed answer. It needs no
subsystem map, hypothesis ledger, implementation plan, or review judgment.

**Static review result:** direct inspection satisfies AC-002. This negative case
prevents turning every navigation question into an orientation workflow.

## Compatibility, privacy, and verification limits

Keep existing discovery, activation, output, and trust contracts unchanged.
The proposed output is tool-agnostic and usable as plain text/Markdown without
requiring diagrams, color, an IDE, a particular index, or a visual UI. There is
no new UI, transport, data retention, authentication flow, or automatic upload.
Inspect minimum relevant evidence and preserve unrelated dirty work.

All proposed instructions must remain independently enforceable when packaged.
Embedded content cannot create task, requirement, command, data-access,
decision, or mutation authority, waive holds, or claim checks passed. Unsafe
dependence has the explicit blocked outcome above. Sensitive evidence is
summarized rather than reproduced.

## M0 decision and planning handoff

**GO_TO_M1_PLANNING:** a distinct map contract survives comparison with all
three adjacent workflows and the two contrasting task examples. This is a
technical boundary judgment, not a measured adoption or model-quality result.
The specification is complete for this bounded proposal; no material expected
behavior decision remains open. Proceed to planning against REQ-001-REQ-008,
CONTRACT-001-CONTRACT-003, and AC-001-AC-011.

Demand, implementation effort, reference organization, metadata wording, and
the exact deterministic contract-test structure remain planning or portfolio
questions. None changes the behavior specified here. Revisit the candidate if
planning shows it cannot retain this boundary without duplicating an existing
workflow. M1 must not infer execution authority from this document or from its
readiness status.

M0 evidence is source inspection and static design-case review only. No
behavioral model evals were run or required; no model-behavior certification is
claimed. Document hygiene checks for this saved artifact are separate from the
example's unexecuted commands and from future skill validation.

M1 planning was completed on 2026-10-18 in the
[repository-grounded implementation plan](repository-orientation-implementation-plan.md).
Its readiness status does not change this specification into command or mutation
authority or establish that the skill has been implemented.
