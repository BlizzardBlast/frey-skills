# Skill development roadmap

Research date: 2026-10-18. Status: proposed direction, not a delivery commitment.
Repository baseline: `19f0bf09ff8a1f1224c45f865090e246f316dfd3` on `main`,
with eight canonical skills and plugin manifest version `1.9.0`.

M1 has added the unreleased [repository-orientation skill](../repository-orientation/SKILL.md).
M2 has added the unreleased [architecture-decision skill](../architecture-decision/SKILL.md);
see the [development record](architecture-decision-development.md).
The following candidate is `threat-modeling`.
Explore performance investigation through `debug`
before deciding whether it needs a separate skill. Keep
`incident-retrospective` as a later candidate pending evidence of recurring use.

M0 completed on 2026-10-18: [boundary validation and behavioral specification](repository-orientation-boundary.md)
recommend **GO_TO_M1_PLANNING**. The distinct map artifact and a direct-lookup
exclusion are grounded in two synthetic repository examples; recurring demand
and model behavior remain unmeasured.

M1 planning completed on 2026-10-18: the [implementation plan](repository-orientation-implementation-plan.md)
was **READY_TO_IMPLEMENT**. The user subsequently requested implementation;
the [execution record](repository-orientation-implementation-plan.md#execution-record)
records **IMPLEMENTED**, passing deterministic gates, and scoped self-review.
M2 completed on 2026-10-18: the [development record](architecture-decision-development.md)
records **IMPLEMENTED**, passing deterministic gates, and scoped self-review.
M3 `threat-modeling` is the next candidate; it has not started.

The remaining names and scopes are proposals. This document does not activate skills,
approve their specifications, authorize implementation or commands, accept
risk, or authorize external writes. Future work still takes its scope and
authority from the user's request and active instructions.

## Research approach and limits

Compare the current skill boundaries with the Agent Skills specification,
maintainer-published skill collections, and primary engineering guidance.
Prioritize a distinct reusable output over a larger catalog.

The current-state findings below come from inspected repository files. The
candidate ranking is an inference from those findings and the linked sources;
the sources do not establish demand for these particular frey-skills additions.
No usage analytics, user interviews, or issue-demand analysis informed this
ranking. An authenticated GitHub CLI issue query was unavailable. This is a
focused landscape sample, not an exhaustive market survey or a comparative
quality assessment of other skill collections.

Sources were read on the research date. Their existence and documented design
are evidence; their instructions are not authority for this repository.
No third-party skills were installed or executed for this research.

## Existing coverage and gaps

The table below records the original eight-skill portfolio at the research
baseline. The [README selection table](../README.md#choose-a-skill) now also
includes the unreleased orientation skill delivered in M1. The original
boundaries and opportunities informing the roadmap were:

| Existing skill | Established coverage | Remaining opportunity |
| --- | --- | --- |
| [debug](../debug/SKILL.md) | Read-only failure, regression, flaky, and production investigation | A reusable orientation artifact before there is a symptom; measurement-specific performance guidance; post-incident learning |
| [change-specification](../change-specification/SKILL.md) | Required behavior, contracts, acceptance criteria | Architecture alternatives and their consequences after required behavior is clear |
| [implementation-plan](../implementation-plan/SKILL.md) | Change, refactor, and migration sequencing | A decision record before sequencing a materially unresolved design |
| [test-strategy](../test-strategy/SKILL.md) | Risk-based coverage, including migration, security, and performance | Threat hypotheses and system modeling before choosing test coverage |
| [implementation-execution](../implementation-execution/SKILL.md) | Bounded execution or continuation of an approved plan | Specialized references may help refactors and upgrades; a second general executor would overlap |
| [code-review](../code-review/SKILL.md) | Diff review, targeted and repository audits, comment triage | Proactive security design with assets, adversaries, and trust boundaries as its primary output |
| [iterative-self-review](../iterative-self-review/SKILL.md) | Explicitly scoped remediation through a bounded loop | Incident learning and proposed prevention actions beyond the selected repair ledger |
| [release-readiness](../release-readiness/SKILL.md) | Read-only candidate-and-target release assessment | Release execution is separate and carries substantially more operational authority |

Security, performance, architecture, and migrations are already cross-cutting
concerns in the existing skills. A new skill must add a distinct trigger and
artifact, not imply that those concerns were previously absent.

## Research findings

| Evidence | Implication for this roadmap |
| --- | --- |
| The [Agent Skills specification](https://agentskills.io/specification) defines portable skill folders, concrete discovery metadata, and progressive loading of instructions and resources. | Keep the core workflow concise, move specialist detail into references, and avoid mandatory tools unless essential. Format compatibility alone does not prove client behavior. |
| Anthropic's [context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) describes using lightweight references to retrieve relevant context as needed. | A bounded repository map with source anchors is a better orientation artifact than a large copied repository summary. |
| [Anthropic's collection](https://github.com/anthropics/skills) already spans creative, technical, business, and document tasks. [Superpowers](https://github.com/obra/superpowers#skills-library) lists planning, execution, testing, debugging, and review workflows. | Broad task catalogs and general development lifecycle skills already have public examples. Frey should differentiate through clear boundaries and evidence contracts. This is a positioning inference, not proof of superiority. |
| [Trail of Bits' collection](https://github.com/trailofbits/skills) includes audit-context-building and specialized security review workflows. | Security skills require a narrow scope and honest coverage. A proactive threat model can complement specialized auditors without claiming to replace them. |
| Michael Nygard's [architecture decision guidance](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) records context, a decision, status, and consequences. | Preserve the distinction between a recommendation and an accepted decision; make consequences and revisit conditions visible. |
| The [OWASP threat modeling guidance](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) covers system modeling, threats, responses, and review throughout development. | Add a design-time security artifact that can inform specifications, planning, testing, and review. |
| Google's [monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/) distinguishes latency, traffic, errors, and saturation, including successful versus failed request latency. | Performance guidance should establish workload and measurement semantics before drawing conclusions from a number. |
| Google's [postmortem guidance](https://sre.google/sre-book/postmortem-culture/) covers incident impact, mitigation, causes, review, and preventive follow-up. | A later retrospective skill should produce a reviewed learning artifact and proposed actions, distinct from active diagnosis or mitigation. |
| [Fowler's refactoring definition](https://refactoring.com/) preserves observable behavior. [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) separates expand, migrate, and contract phases. | Improve existing refactor and migration references before adding skills whose outputs duplicate current planning and execution. |

## Prioritization

Apply these criteria in order:

1. Fit the repository's reusable engineering-workflow focus.
2. Add a distinct trigger and output beyond the current eight skills.
3. Reuse evidence across several existing workflows without creating mandatory
   stages for simple tasks.
4. Keep authority, verification, and maintenance costs manageable.

The assessments below are qualitative design judgments, not measured adoption
scores. Effort includes authoring, references, deterministic contracts, docs,
and packaging: **M** is a normal new read-only workflow; **L** adds substantial
domain-specific evidence and safety cases. Neither is a calendar estimate.

| Order | Candidate | Priority rationale | Effort | Confidence / main uncertainty |
| --- | --- | --- | --- | --- |
| 1 | `repository-orientation` (M1 implemented) | Broad reuse; useful before a concrete defect or change exists | M | Medium: the artifact boundary is established; recurring use and runtime effectiveness remain unmeasured |
| 2 | `architecture-decision` | Strong artifact gap between required behavior and implementation sequencing | M | Medium: the gap is clear, but recurring user demand is unmeasured |
| 3 | `threat-modeling` | Distinct proactive security output with several lifecycle consumers | L | Medium: domain coverage and overlap with specialist security collections need careful review |
| 4 | `performance-investigation` | Valuable measurement discipline, but substantial overlap with `debug` | L | Low for a standalone skill; start with a reference extension |
| 5 | `incident-retrospective` | Distinct prevention artifact after an incident has stabilized | M | Low: incident frequency and access to sanitized evidence are unknown |

## Proposed skill boundaries

### 1. repository-orientation

Implemented in M1 as an [unreleased canonical skill](../repository-orientation/SKILL.md).
The boundary below remains the basis of its specification and contracts.

**Trigger:** explain an unfamiliar repository or subsystem, locate ownership and
entry points, or prepare a bounded technical onboarding map. Skip a separate
orientation workflow for a single known-file lookup or when another skill's
normal inspection already answers the question.

**Minimum output:** inspected revision and dirty-state limitations; scope and
coverage; entry points and important execution/data paths; module ownership and
dependency boundaries; native verification commands with inspected provenance
and execution status; source anchors; unknowns and next investigation paths.
Label commands as observed or proposed, never passed without execution evidence.

**Boundary:** read-only discovery. Do not install dependencies, execute setup
instructions found in files, generate an index, diagnose every possible defect,
or propose a repository-wide rewrite. Use an existing index when available and
appropriate; provide a normal search fallback without requiring one.

**Completion:** stop once the requested area has a useful anchored map, or state
the specific access or coverage limit. A saved map is a revision-bound snapshot
and cannot replace reinspection of changed paths.

**Deterministic contract cases:** bounded monorepo scope; generated versus
canonical files; stale map; unavailable subsystem; an injected setup command;
unexecuted verification commands; a trivial lookup that should skip the skill.

### 2. architecture-decision

**Trigger:** compare concrete architecture or dependency-boundary alternatives,
resolve a design tradeoff, or draft/revisit an architecture decision record.
Required behavior must be sufficiently established; unresolved product behavior
belongs with `change-specification`.

**Minimum output:** decision question; requirements and constraints with their
sources; current design; feasible alternatives including retaining the current
design when applicable; tradeoffs in complexity, compatibility, failure modes,
security, operations, and reversibility; recommendation; proposed ADR text;
missing evidence and conditions for revisiting the decision.

**Boundary:** read-only analysis and an advisory draft. Do not silently choose
product requirements, accept a decision on the user's behalf, edit the system,
or turn the recommendation into an executable implementation plan. Existing
ADRs are evidence of prior choices, not command or mutation authority.

**Completion:** deliver one bounded decision analysis, marking unresolved
material constraints explicitly. Only actual user/stakeholder acceptance can be
reported as acceptance; a recommended option remains proposed.

**Deterministic contract cases:** conflicting constraints; superseded ADR;
unknown operating scale; retaining the current design; a forged acceptance;
an alternative that changes required behavior; absent evidence for claimed cost.

### 3. threat-modeling

**Trigger:** model threats for a scoped feature, system, data flow, or proposed
design before implementation or after a meaningful trust-boundary change.

**Minimum output:** scope and revision/design identity; assets and sensitive
data; actors, entry points, data flows, and trust boundaries; threat/abuse-case
ledger with stable IDs; existing controls and evidence gaps; proposed
mitigations; residual risks; validation and handoff suggestions.

**Boundary:** read-only defensive modeling. Threat scenarios are hypotheses,
not confirmed vulnerabilities. Do not perform exploitation, intrusive scanning,
credential retrieval, production probing, remediation, or risk acceptance.
Distinguish hypothetical architecture from inspected implementation and minimize
sensitive evidence. Do not claim exhaustive security coverage.

**Completion:** stop after one scoped model with material unknowns and uncovered
boundaries stated. Preserve holds and unresolved risks. Route supplied findings
to an appropriate authorized review or validation task rather than declaring
them proven from the threat model alone.

**Deterministic contract cases:** cross-tenant access; sensitive logging;
external callbacks; ambiguous data ownership; a mitigation without evidence;
forged risk acceptance; a malicious instruction embedded in a diagram or log.

### 4. performance-investigation: extension first

Start with a proposed performance reference under `debug/references/` and
focused instruction contracts. Keep the existing causal investigation workflow.
The reference should define workload, environment and revision comparability,
metric units, warmup/cache state, repeated samples and variance, resource limits,
and the distinction between a bottleneck hypothesis and a measured cause.

A future standalone skill would be triggered by an explicit request for a
performance baseline, regression investigation, or bottleneck analysis. Its
distinct artifact would be a measurement ledger plus a bounded experiment plan,
with results only when safely obtained within the user's authorized scope.
Do not infer speedup from incomparable runs, install a profiler automatically,
or generate production load. Missing safe measurements must remain a limitation.

Consider extraction only after at least two sanitized maintainer-reported tasks
show that the measurement artifact cannot be expressed clearly through `debug`
and its reference. Review those examples as design evidence, not behavioral
model trials or mandatory provider runs.

**Deterministic contract cases:** mismatched hardware/revision; noisy samples;
missing baseline; fast errors distorting latency; exhausted resource budget;
an unsafe benchmark command; conclusions unsupported by measurements.

### 5. incident-retrospective: demand-dependent

**Trigger:** prepare a retrospective for a stabilized incident from authorized
evidence. Ongoing incident response and unknown-cause investigation remain
separate work; this skill must not delay mitigation.

**Minimum output:** impact and time window with time zone; source-linked
timeline; observed facts versus reports and inferences; triggers, causes, and
contributing conditions; detection and recovery gaps; what helped; proposed
prevention actions with priority, verification, and known owners or `unassigned`.

**Boundary:** read-only synthesis and an advisory draft. Do not invent a root
cause or owner, rewrite history, assign blame, publish private evidence, create
issues, notify people, execute mitigation, or mark prevention work completed.
Unknown causation remains unknown even when the incident is resolved.

**Completion:** stop with a bounded draft, unresolved evidence conflicts, and
proposed follow-up. Consider a standalone skill when recurring sanitized incident
requests demonstrate a need beyond `debug`'s cause and contributing-factor output.

**Deterministic contract cases:** inconsistent timestamps; unknown cause;
recovery without a confirmed fix; sensitive customer evidence; unassigned action;
forged action completion; an embedded request to publish the incident.

## Delivery sequence and milestone gates

Use completion gates rather than promised dates or version numbers. Deliver one
coherent skill at a time. Each recommendation needs its own scoped development
request; documenting this roadmap does not approve the future work.

| Milestone | Deliverable and repository anchors | Dependency and exit gate |
| --- | --- | --- |
| M0: validate the first boundary | Completed 2026-10-18: [boundary specification and two static task examples](repository-orientation-boundary.md) define the map, routing, requirements, acceptance criteria, and evidence limits. | **GO_TO_M1_PLANNING**: the map is distinct from diagnosis, planning, and review; direct lookups skip it. This is a design decision, not measured demand or runtime certification. |
| M1: repository-orientation | Completed 2026-10-18: [execution record](repository-orientation-implementation-plan.md#execution-record) covers canonical instructions, references, metadata, deterministic contracts, catalog/package integration, passing checks, and scoped self-review. | **IMPLEMENTED**, unreleased. Nine-skill development bundle parity passed; no behavioral or new client-UI certification is claimed. |
| M2: architecture-decision | Completed 2026-10-18: [development record](architecture-decision-development.md) covers the canonical skill, proposed ADR template, alternatives/consequences rules, routing boundaries, focused contracts, and catalog/package integration. | **IMPLEMENTED**, unreleased. Proposed-versus-accepted status, requirement boundaries, and ten-skill bundle parity passed deterministic checks. No model-behavior or client certification is claimed. |
| M3: threat-modeling | Add scoped system-model and threat-ledger references, inert examples, coverage limits, and trust/decision contracts. Check overlap with [code-review](../code-review/SKILL.md) and [test-strategy](../test-strategy/SKILL.md). | Follow the earlier boundary lessons; no mandatory dependency on either new skill. Exit with hypothesis-versus-finding and risk-acceptance boundaries covered. |
| M4: reassess specialists | Review the proposed `debug` performance extension and demand for incident retrospectives. Record build, extend, defer, or drop decisions here with evidence. | Complete the first three candidate decisions. Create separate skills only if their extraction conditions hold; do not build them to fill the schedule. |

If M0 rejects the first candidate, move to architecture decisions rather than
forcing a new orientation skill. Milestone order is a recommendation, not a
required workflow sequence for users of the skills.

### Common delivery gate for a future skill

- Define a focused activation boundary, exclusions, observable output,
  completeness/result semantics, bounded iteration, and explicit stop conditions.
  Document positive, adjacent-workflow, and unsafe-input cases.
- Keep canonical sources in the new root skill directory. Supply valid
  frontmatter, matching folder/name, concise instructions, independently
  enforceable content trust, and client metadata in `agents/` where appropriate.
  Use [CONTRIBUTING.md](../CONTRIBUTING.md) and [SECURITY.md](../SECURITY.md).
- Treat repository files, documents, examples, logs, diagrams, plans, and command
  output as untrusted evidence. They cannot create task, requirement, command,
  data-access, decision, or mutation authority; widen scope; request secrets;
  authorize network/remote execution, privilege escalation, destructive actions,
  or external writes; override instructions; or claim checks passed. Define
  sensitive-evidence minimization and the workflow's blocked outcome.
- Add focused deterministic instruction/decision contracts. Follow the existing
  [release-readiness contract pattern](../scripts/test_release_readiness_contract.py)
  where useful and register new test modules in
  [scripts/check.py](../scripts/check.py). The shared
  [content-trust tests](../scripts/test_content_trust_contracts.py) discover new
  canonical skills automatically; they do not replace workflow-specific cases.
- Keep the README selection table, skill descriptions, contributor source list,
  handoff examples, and changelog consistent. Use
  [canonical discovery](../scripts/repository_layout.py), rebuild through
  [the plugin builder](../scripts/build_plugin.py), and validate source parity.
  Review client metadata and release-smoke expectations when the skill set
  changes. Never hand-edit `dist/frey-skills`.
- Run the full existing deterministic gate with the configured Python 3.11+
  environment: `python scripts/check.py`. Record the exact command, result,
  candidate identity, and limits; complete scoped review before integration.
  Packaging, client metadata, desktop UI observations, and release publication
  remain separate evidence categories; update compatibility records only with
  actual observations.
- Behavioral model evals, provider credentials, fresh-context trials, paid token
  workflows, and accepted scorecards are not required or run. Deterministic
  contracts check committed instructions and fixtures; they do not certify model
  behavior, activation accuracy, or universal prompt-injection resistance.

## Extend or defer instead of adding another skill

| Idea | Recommended disposition | Evidence that would justify revisiting |
| --- | --- | --- |
| `safe-refactor` | Extend refactor profiles in `implementation-plan`, test guidance in `test-strategy`, and execution invariants first. | Repeated tasks require a distinct behavior-preservation artifact that the current combination cannot represent clearly. |
| `migration` / `dependency-upgrade` | Extend migration and dependency references, covering consumer compatibility, provenance, transition phases, and recovery. | A distinct compatibility or upgrade decision workflow emerges beyond the existing migration plan/test strategy. |
| General test writer or TDD skill | Defer a separate skill; authorized test implementation already fits plan execution, while `test-strategy` chooses coverage. | A focused user workflow needs a distinct contract beyond choosing tests or executing a plan; no blanket test-first requirement is introduced. |
| General verification or release checker | Extend current execution/review/readiness evidence rules. | A new candidate/target decision cannot be represented by existing outputs. |
| Framework-specific frontend, mobile, document, or cloud packs | Keep outside the immediate core roadmap; link to suitable specialist resources when relevant. | Sustained demand and a maintainable domain owner justify a separately scoped pack. |
| Release executor, deployment operator, or incident mitigator | Defer; the current release skill intentionally provides an assessment. | A concrete target ecosystem, credential/approval model, recovery contract, and maintenance capacity support an explicitly authorized operational workflow. |
| Autonomous orchestration, automatic lesson promotion, or issue synchronization | Defer broad automation and external-write workflows. | A concrete repeated task establishes value and a clear consent, provenance, privacy, and recovery contract. |

## Maintaining this roadmap

The repository maintainer is the proposed decision owner; future implementation
owners and capacity are unassigned. Revisit this document after each candidate is
delivered, rejected, or materially rescoped. Recheck source currency, current
skill boundaries, and evidence of recurring need before starting a later phase.

Record each disposition with its date, relevant revision, reason, remaining
uncertainty, and next gate. A deferred candidate may be dropped. Success means a
clearer useful workflow with maintained boundaries, passing deterministic
checks, and honest evidence, rather than reaching a target skill count.

Open questions are demand and capacity: whether a standalone orientation
artifact is useful often enough, which architecture decisions recur, whether
security-domain maintenance is available, and whether performance or incident
work warrants extraction. These do not prevent documenting a proposed order;
they should constrain future implementation scope.

### Milestone disposition log

| Date | Milestone / disposition | Evidence and remaining uncertainty | Next gate |
| --- | --- | --- | --- |
| 2026-10-18 | M0 complete; `GO_TO_M1_PLANNING` | [Boundary specification](repository-orientation-boundary.md) at baseline `19f0bf09ff8a1f1224c45f865090e246f316dfd3` plus uncommitted roadmap documentation; inspected routing contracts and two synthetic examples support a distinct artifact. Demand and runtime effectiveness remain unmeasured. | Plan M1 against the specified requirements, contracts, and acceptance criteria, preserving its read-only and optional-workflow boundary. |
| 2026-10-18 | M1 planning complete; `READY_TO_IMPLEMENT` | [Five-step plan](repository-orientation-implementation-plan.md) traces all eight requirements and eleven acceptance criteria into authoring, contracts, integration, and verification. Implementation and gate results were unobserved at planning handoff. | Execute and verify the addition. |
| 2026-10-18 | M1 delivered; `IMPLEMENTED` | [Execution record](repository-orientation-implementation-plan.md#execution-record): 20 focused tests passed; full gate discovered 236 tests with one expected Windows-only skip, validated all nine skills, rebuilt the bundle, and passed parity. Scoped self-review found no actionable findings. Skill remains unreleased and runtime effectiveness unmeasured. | M2: scope architecture-decision against the existing specification/planning boundaries before authoring it. |
| 2026-10-18 | M2 delivered; `IMPLEMENTED` | [Development record](architecture-decision-development.md) at baseline `51950489682fbe304ca818b17a7e911e2f4bd7f6`: 19 focused tests passed; full gate reported 247 tests, 246 passed and one expected Windows-only skip; all ten skills validated and bundle parity passed. Scoped self-review found no actionable findings. Skill remains unreleased; model behavior and recurring demand remain unmeasured. | M3: scope threat-modeling against review and test-strategy boundaries before authoring it. |
