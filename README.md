# frey-skills

A collection of practical skills for AI coding agents. Skills are packaged
instructions and optional resources that help agents execute repeatable
workflows more reliably.

This repository is designed for the
[Agent Skills](https://agentskills.io/) ecosystem.

## Choose a skill

| Your task | Skill | Main output | Edits files? |
| --- | --- | --- | --- |
| Understand an unfamiliar repository or subsystem | [repository-orientation](repository-orientation/SKILL.md) | Bounded source-linked map, coverage, and verification entry points | No |
| Investigate an unknown failure or regression | [debug](debug/SKILL.md) | Hypotheses, evidence, and root-cause status | No |
| Define required behavior and acceptance criteria | [change-specification](change-specification/SKILL.md) | Requirements, contracts, and planning readiness | No |
| Compare architecture alternatives or draft an ADR | [architecture-decision](architecture-decision/SKILL.md) | Evidence-backed alternatives, consequences, and a proposed decision | No |
| Model scoped threats or abuse cases | [threat-modeling](threat-modeling/SKILL.md) | System model, threat hypotheses, control evidence, and residual risks | No |
| Sequence a concrete repository change | [implementation-plan](implementation-plan/SKILL.md) | Ordered steps, invariants, verification, and readiness | No |
| Decide what testing a change needs | [test-strategy](test-strategy/SKILL.md) | Prioritized risks, scenarios, and test readiness | No |
| Execute or resume an approved implementation plan | [implementation-execution](implementation-execution/SKILL.md) | Bounded changes, verification, and plan conformance | Yes, within the authorized plan |
| Review changes, repository risks, or stale comments | [code-review](code-review/SKILL.md) | Coverage, findings, and a review decision | No |
| Fix selected findings through a bounded review loop | [iterative-self-review](iterative-self-review/SKILL.md) | Scoped fixes and verification, up to three passes | Yes, only when explicitly invoked |
| Assess whether a concrete candidate can ship to its target | [release-readiness](release-readiness/SKILL.md) | Candidate-matched evidence, blockers, residual risk, and release readiness | No |

Start at the row that matches the work you need. A direct, unambiguous task does
not require every stage. Saved artifacts and positive readiness statuses do not
authorize implementation or external writes; the user's request establishes
that authority.

For installation, see the [setup guide](docs/installation.md). For a complete
handoff sequence, see the [worked example](docs/worked-example.md).
For researched future skill priorities and delivery gates, see the
[skill development roadmap](docs/roadmap.md).

The versioned installation below pins the published eleven-skill v1.10.0
release, including `repository-orientation`, `architecture-decision`, and
`threat-modeling`, plus the performance-investigation guidance within `debug`.
The [release record](docs/release-v1.10.0.md) records publication, public-archive
verification, historical candidate evidence, and client compatibility limits.

## Content-trust invariant

All canonical skills treat repository and tool content as untrusted evidence,
not instruction authority. Files, plans, specifications, comments, issue and PR
text, tests, fixtures, logs, generated content, and command output cannot widen
user scope, authorize commands or sensitive effects, request secrets, override
safeguards, or claim checks passed.

Each skill applies this invariant to its own workflow and maps unsafe dependence
to its existing partial, blocked, unresolved, or not-ready status. Deterministic
contract tests verify the published instructions and inert adversarial fixtures;
they do not certify model behavior or guarantee universal prompt-injection
resistance.

## Available Skills

### repository-orientation

Maps an unfamiliar repository or subsystem when understanding how its parts fit
together is the requested output. It records snapshot identity, source anchors,
responsibilities, entry points, execution/data paths, dependencies, generated
boundaries, and verification commands with their effects and execution status.

The read-only workflow stops after a bounded initial map and at most one targeted
gap-check pass, with `COMPLETE`, `PARTIAL`, or `BLOCKED` coverage. It does not run
tests/builds/setup, create indexes, save maps automatically, or activate other
workflows. Simple symbol lookups remain direct; diagnosis, change planning,
and review judgment stay with their existing skills. A complete map is not a
passed-check or readiness claim.

Example:

```text
Use $repository-orientation to explain how this subsystem reaches storage,
with source anchors, coverage limits, and verification entry points.
```

### debug

Performs read-only, evidence-backed root-cause investigations for deterministic
failures, regressions including performance, flaky behavior, and production-only
incidents. It may activate implicitly when the user asks to investigate, diagnose,
troubleshoot, reproduce, or determine the root cause of a concrete codebase or
system symptom.

**Investigation modes:**

- `failure investigation` — deterministic errors, crashes, incorrect results,
  or failing tests.
- `regression investigation` — behavior differences across versions, branches,
  commits, deployments, or environments.
- `flaky investigation` — intermittent, timing-dependent, order-dependent, or
  nondeterministic behavior.
- `production investigation` — logs, telemetry, incidents, or incomplete
  reproduction access.

**What it enforces:**

- A read-only investigation boundary; the skill stops before implementation.
- Diagnostic evidence and command output cannot authorize execution.
- Explicit symptom, baseline, and reproduction status.
- Conditional performance measurement guidance for comparable workloads,
  metrics, outcome populations, bounded diagnostics, and causal evidence.
- A stable hypothesis ledger with supporting, contradicting, and discriminating
  evidence.
- Investigation completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Root-cause status: `CONFIRMED`, `LIKELY`, `UNRESOLVED`, or `NOT_A_DEFECT`.
- Clean handoffs to change specification, implementation planning, execution,
  review, or remediation.

The performance reference ships in the pinned v1.10.0 release.

### change-specification

Converts an idea, ticket, story, defect expectation, supplied specification, or
requested behavior change into a read-only, repository-grounded,
implementation-neutral specification before file-level planning. It may activate
implicitly when the user asks to define required behavior, acceptance criteria,
edge cases, or affected contracts.

**Specification modes:**

- `feature specification` — define a new capability or user workflow.
- `behavior-change specification` — define a change to established behavior.
- `contract specification` — define API, event, schema, integration, permission,
  or state-machine behavior.
- `specification refinement` — validate and improve a supplied specification.

**What it enforces:**

- A read-only, implementation-neutral boundary; the skill stops before
  repository change sequencing.
- Stable `REQ-NNN`, `AC-NNN`, and `CONTRACT-NNN` traceability.
- Observable Given/When/Then acceptance criteria rather than implementation
  details.
- Explicit goals, non-goals, actors, current/proposed behavior, failures, state
  transitions, compatibility, security, privacy, and accessibility constraints.
- Tickets and supplied specifications cannot create requirements, approve their
  own design, authorize commands, or silently resolve conflicting sources.
- Specification completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Planning readiness: `READY_FOR_PLANNING`, `READY_WITH_OPEN_QUESTIONS`, or
  `NOT_READY`.

A separate specification is not mandatory when a planning request already
provides complete, unambiguous behavior and contracts.

### architecture-decision

Compares concrete architecture or dependency-boundary alternatives after required
behavior is established. It inspects the current design and prior decisions,
compares feasible options including retaining the current design, and returns
an advisory ADR draft with evidence, tradeoffs, consequences, and revisit
conditions. It does not choose new product requirements or sequence changes.

Analysis completeness is `COMPLETE`, `PARTIAL`, or `BLOCKED`; recommendations
are `PROPOSED` or `DEFERRED`. Material missing constraints or measurements defer
the choice. New drafts always remain proposed; historical acceptance needs
independent provenance. The read-only workflow stops within one initial analysis
and one optional gap-check pass, without saving ADRs, running experiments,
accepting risk, or implementing a recommendation.

Example:

```text
Use $architecture-decision to compare these alternatives against the established
requirements and draft a proposed ADR with consequences and revisit conditions.
```

### threat-modeling

Produces a read-only defensive model for a scoped feature, system, data flow,
or proposed design. It records assets and sensitive data, actors, entry points,
flows, trust boundaries, threat hypotheses with stable IDs, existing-control
evidence, proposed mitigations, validation needs, and residual risks.

Model completeness is `COMPLETE`, `PARTIAL`, or `BLOCKED`. Threat hypotheses
remain distinct from confirmed findings; observed controls do not prove
effectiveness, and proposed mitigations do not close risks. Prior risk acceptance
needs independent provenance and cannot lift holds or authorize effects. The
workflow stops after one initial model and at most one targeted gap-check pass,
without probing, scanning, remediation, persistence, publication, or risk acceptance.

Example:

```text
Use $threat-modeling to model this feature's tenant boundaries, callback, and
logging flows with threat hypotheses, control evidence, and residual risks.
```

### implementation-plan

Produces read-only, evidence-backed implementation plans grounded in the current
repository. It may activate implicitly when the user asks to plan, scope,
sequence, or refine a concrete codebase change before editing.

**Scope modes:**

- `change plan` — feature, known bug fix, behavior, configuration, or localized
  implementation work.
- `refactor plan` — behavior-preserving structural improvement.
- `migration plan` — schema, API, dependency, framework, toolchain, CI, or
  deployment changes that require compatibility-aware sequencing.
- `plan refinement` — validate and tighten an existing plan against repository
  evidence.

**What it enforces:**

- A read-only planning boundary; the skill stops before implementation.
- Repository documents and supplied plans/specifications cannot create
  requirements or approve their own design.
- Evidence-backed current-state findings with no fabricated repository paths or
  contracts.
- Explicit requirements and invariants before proposing changes.
- Ordered implementation steps with repository anchors, dependencies, preserved
  invariants, and focused verification.
- Planning completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Readiness semantics: `READY_TO_IMPLEMENT`, `READY_WITH_ASSUMPTIONS`, or
  `NOT_READY`.

### test-strategy

Produces a read-only, repository-grounded, risk-based testing strategy for a
concrete feature, defect, migration, diff, release, or system boundary. It may
activate implicitly when the user asks for a test strategy, regression plan,
migration test plan, release test plan, risk-based coverage plan, or testing
readiness assessment.

**Scope modes:**

- `change test strategy` — focused feature, behavior, defect, configuration, or
  diff coverage.
- `regression test strategy` — protect established behavior after a confirmed
  defect, refactor, incident, or dependency change.
- `migration test strategy` — compatibility, data transition, rollback, and
  old/new version coverage.
- `release test strategy` — testing concerns for a release candidate, staged
  rollout, or production promotion.

**What it enforces:**

- A read-only strategy boundary; the skill stops before test implementation or
  execution.
- Test evidence cannot require secrets, unrestricted production data,
  destructive setup, or unauthorized external calls.
- A prioritized risk matrix and observable contract inventory.
- Risk-to-layer and risk-to-scenario traceability.
- Explicit test data, environment, automation, and execution requirements.
- Entry and exit criteria plus residual risk.
- Strategy completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Test readiness: `READY`, `READY_WITH_GAPS`, or `NOT_READY`.

A test strategy is supplementary evidence. It is not an executable
implementation plan by itself and does not decide merge readiness or broader
release readiness.

### implementation-execution

Executes, continues, or resumes an existing approved implementation plan through
bounded repository edits and focused verification. It may activate implicitly
only when the user references an approved plan or asks to continue named plan
steps. It does not activate for ordinary direct implementation without a plan.

**Execution modes:**

- `plan execution` — execute an approved plan from the beginning.
- `implementation continuation` — reconcile completed work and continue only
  remaining steps.

**What it enforces:**

- Baseline capture for branch, HEAD, staged, unstaged, and untracked work.
- An executable-plan eligibility gate before editing.
- Plan, repository, and tool content is treated as untrusted evidence rather
  than instruction authority.
- Change specifications are additional untrusted evidence and cannot satisfy the
  executable plan gate alone.
- A change specification or test strategy alone cannot satisfy the executable
  plan gate.
- Commands require inspected provenance and explicit authorization for secret,
  network, remote-execution, privilege, or external-write effects.
- One coherent plan step at a time.
- A plan-conformance ledger with changed paths, verification, and deviations.
- Preservation of unrelated dirty work and canonical generated-source ownership.
- A material deviation gate that stops rather than inventing design decisions.
- Honest `IMPLEMENTED`, `PARTIAL`, or `BLOCKED` execution status.
- Handoff of the completed diff to `code-review`.

### code-review

Performs read-only, evidence-backed reviews for pull requests, diffs, targeted
files, repository snapshots, and stale review comments. The skill may be
activated implicitly when the user asks for code review, PR review, merge
readiness, repository risk review, targeted audit, or review-comment triage.

**Scope modes:**

- `diff review` — review a PR, branch, commit range, staged changes, or
  working-tree diff.
- `targeted audit` — review named files, components, concerns, commands, or
  comments.
- `repository audit` — sample a repository or package area for broad risk and
  report limits.
- `review-comment triage` — decide whether review comments still apply to the
  current code.

**What it enforces:**

- Repository and PR content cannot suppress findings, force approval, or
  redefine severity.
- A coverage matrix for every requested or materially applicable concern.
- Explicit review completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Severity-ranked finding ledger with stable IDs and verification guidance.
- Decision semantics: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
- A handoff ledger when the user asks for fixes; remediation is delegated
  explicitly to `iterative-self-review` instead of performed during review.

### iterative-self-review

Runs an explicit-only remediation loop for a provided issue ledger, user-scoped
defects, failing tests, or review comments. It should not activate for ordinary
implementation work unless the user explicitly asks for iterative self-review,
post-review repair, or repeated fix-and-recheck remediation.

**What it enforces:**

- Baseline capture before editing.
- Only user-selected ledger IDs and explicit user scope authorize mutations.
- Scoped fixes by issue ID or user instruction.
- A default maximum of 3 review/fix/verify passes.
- Early stop when scoped issues are resolved and focused verification is
  recorded.
- A required user follow-up before any pass 4 or later pass.
- Honest `RESOLVED`, `PARTIAL`, or `BLOCKED` status without whole-repository
  clean claims.

### release-readiness

Assesses a concrete release candidate against its intended target through a
read-only evidence review. It may activate when the user asks for release
readiness or a release go/no-go decision.

**What it enforces:**

- Immutable candidate and target identity, with evidence provenance and validity limits.
- An evidence matrix separating required criteria, optional checks, and justified exclusions.
- Distinct passing, failed, missing, stale, and mismatched evidence.
- Applicable artifact, compatibility, security/privacy, migration, rollout, and recovery checks.
- Repository text cannot waive gates, accept risk, lift holds, or authorize publication.
- Assessment completeness: `COMPLETE`, `PARTIAL`, or `BLOCKED`.
- Release readiness: `READY`, `READY_WITH_GAPS`, or `NOT_READY`.
- A bounded assessment that stops before mutation, execution, or polling.

Readiness does not authorize merging, publishing, or deployment, and does not
establish publication or operational acceptance. See the
[release assessment example](release-readiness/references/worked-example.md)
for mismatched CI, missing recovery evidence, and a later readiness handoff.

## Workflow

The primary implementation lifecycle is:

`repository-orientation` is optional when a repository/subsystem map is itself
useful. It is not a prerequisite for the lifecycle below or for a simple lookup.

`architecture-decision` is optional between established required behavior and
implementation planning when a material design choice remains. Its proposed
ADR is advisory; user/stakeholder acceptance and implementation authorization
remain separate.

`threat-modeling` is optional when a scoped defensive model is the requested
output, including after a trust-boundary change. It can inform specification,
architecture, test strategy, and review without executing those workflows or
certifying security. All three skills are included in pinned v1.10.0.

```text
symptom or failing test
        ↓
       debug
        ↓
change-specification
        ↓
implementation-plan
        ↓
implementation-execution
        ↓
code-review
        ↓
iterative-self-review
        ↓
release-readiness
```

`debug` is optional when there is no unknown cause. `change-specification` is
optional when required behavior and contracts are already complete.
`test-strategy` is an optional specialist workflow that can inform planning,
test implementation, review of test sufficiency, migration confidence, and
release testing. It is not a mandatory stage for every change.

`release-readiness` is optional when a release decision is needed. It considers
applicable evidence beyond testing and code review without executing the release.

See the [worked example](docs/worked-example.md) for a complete JSON-export
change, including user approvals, artifact handoffs, a failed verification,
read-only review, and scoped remediation. Its outputs are illustrative, not
behavioral model eval evidence.

## Installation

Install the versioned skill sources with the Skills CLI:

```bash
npx skills add https://github.com/BlizzardBlast/frey-skills/tree/v1.10.0
```

Choose the skills, agent, and project or user scope in the installer. To follow
the default branch instead, use `npx skills add BlizzardBlast/frey-skills`.

The [installation guide](docs/installation.md) covers selecting individual
skills, the versioned Codex plugin ZIP, verification, upgrades, and rollback.

## Usage

Once installed, compatible agents can activate skills when the task context
matches each skill's activation rules.

**Example prompts:**

```text
Investigate why this test is flaky before editing anything.
```

```text
Find the root cause of this production-only 401 from the available logs.
```

```text
Turn this ticket into concrete requirements and acceptance criteria.
```

```text
Use change-specification to define the API contract and failure behavior before planning.
```

```text
Refine this supplied feature specification and assess planning readiness.
```

```text
Plan this feature against the current repository before editing.
```

```text
Use implementation-plan to tighten this migration plan and preserve backward compatibility.
```

```text
Create a change test strategy for this feature.
```

```text
Design regression coverage for this confirmed defect.
```

```text
Create a migration test strategy covering old/new compatibility and rollback.
```

```text
Assess whether this release is test-ready from the available evidence.
```

```text
Execute the approved implementation plan.
```

```text
Continue the implementation plan from step 3 without redoing completed work.
```

```text
Review this pull request for merge readiness.
```

```text
Targeted audit: review only the build-tooling change.
```

```text
Triage these stale review comments against the current code.
```

```text
Review this PR, then hand me the finding ledger for fixes.
```

```text
Use iterative-self-review to fix CR-P1-001 and CR-P2-002 from the ledger.
```

```text
Run iterative-self-review for only the P1 findings; leave P2/P3 items alone.
```

```text
Use release-readiness to assess this candidate for the Linux release channel; report blockers without publishing.
```

## Skill Structure

Each skill directory can include:

- `SKILL.md` — required metadata + instructions
- `agents/` — optional client-specific metadata
- `scripts/` — optional helper automation
- `references/` — optional supporting docs
- `assets/` — optional templates/resources
- `evals/` — optional legacy behavioral fixtures and scorecards

Current layout:

```text
change-specification/
code-review/
debug/
implementation-plan/
test-strategy/
implementation-execution/
iterative-self-review/
release-readiness/
repository-orientation/
architecture-decision/
threat-modeling/
```

Each canonical skill contains a `SKILL.md`; individual skills may additionally
contain `agents/`, `evals/`, `references/`, or `scripts/` according to their
workflow. The `change-specification`, `test-strategy`, and `release-readiness`
skills intentionally ship without an `evals/` directory.

## Quality Gates

After installing the dependencies into a Python 3.11+ environment, run all
deterministic checks with:

```bash
python scripts/check.py
```

The same runner works on Windows, Linux, and macOS and checks setup before
starting. CI runs the full set on Windows and macOS with Python 3.12, alongside
the Ubuntu jobs. It rebuilds generated plugin output at `dist/frey-skills`. See
[CONTRIBUTING.md](CONTRIBUTING.md) for environment setup and individual groups.

Separate installation smoke jobs exercise the pinned Skills CLI on Windows,
Linux, and macOS, checking selected and complete skill installations against the
checkout and documented release in default and copy modes. These checks compare
installed files and resources; they do not certify agent activation or behavior.
The same platform jobs also download the published Codex plugin ZIP, verify its
checksum, and compare its manifest, license, skills, and supporting files with
the pinned release sources before extracting it in disposable storage.

A separate Codex CLI matrix checks plugin installation, metadata discovery,
upgrade, and rollback on Windows, Linux, and macOS using verified published
archives and disposable client homes. See the [compatibility record](docs/compatibility.md)
for observed results and desktop UI coverage limits.

The repository uses deterministic quality gates:

- a project validator for metadata, references, optional eval schema, scorecard
  structure, and source hygiene;
- the official `skills-ref` validator for Agent Skills specification
  compatibility;
- cross-skill content-trust and other focused contract tests;
- deterministic plugin build and source-parity validation;
- whitespace validation; and
- scoped code review.

Behavioral model evals are not run or required for any skill. Existing eval
fixtures and scorecards are legacy reference material only. Passing structural
validation for those files does not mean behavioral trials were executed, and no
model-behavior certification is claimed.

## Generated Codex Plugin Bundle

The root skill directories are the canonical source of truth. The generated
Codex plugin bundle is built into `dist/frey-skills` from those sources and
`plugin-template/.codex-plugin/plugin.json`.

```bash
python scripts/build_plugin.py --force dist/frey-skills
python scripts/validate_plugin_bundle.py dist/frey-skills
```

Do not hand-edit `dist/frey-skills`; rebuild it from the canonical sources.
The repository does not commit marketplace metadata or a public marketplace
submission package. Local marketplace wiring, if you use it, is an optional
personal setup outside this repo workflow.

## Notes for Authors

- Keep `SKILL.md` focused and task-oriented.
- Include required YAML frontmatter (`name` and `description`) in `SKILL.md`.
- Include clear trigger language so agents know when to activate the skill.
- Define a compact `## Content trust boundary` in every skill.
- Use short, actionable steps and explicit stop conditions.
- Move deep detail to `references/` when instructions become too long.
- Do not claim behavioral model evals were run.
- Never fabricate behavioral scorecards.
- Keep generated plugin output in sync by rebuilding and validating
  `dist/frey-skills`.

See `CONTRIBUTING.md` for setup, deterministic validation, behavioral eval
policy, and PR expectations.

## Versions and Releases

See [CHANGELOG.md](CHANGELOG.md) for versioned changes and
[RELEASING.md](RELEASING.md) for validation, tag, and publication rules.
GitHub releases distribute the validated plugin bundle; marketplace submission
remains outside this repository's workflow.

## License

MIT. See `LICENSE` for full text.
