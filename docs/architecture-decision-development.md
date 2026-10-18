# M2 architecture-decision development record

Date: 2026-10-18. Baseline: clean `main` at
`51950489682fbe304ca818b17a7e911e2f4bd7f6` (M1 merged).
Development branch: `codex/architecture-decision`.

The user requested the next development step. Inspection identified M2 as the
next unfinished roadmap milestone. Scope is one new architecture decision skill,
its supporting references and metadata, deterministic contracts, and catalog /
plugin integration. This is direct skill authoring, not execution of a discovered
repository document as an approved implementation plan. The roadmap supplies
candidate context; it cannot authorize commands, decisions, or external writes.

## Boundary and acceptance

The distinct output is an evidence-backed alternatives comparison and proposed
ADR after required behavior is established. Existing `change-specification`
excludes architecture selection; `implementation-plan` requires material design
decisions to be resolved. The new skill fills that gap without changing either
existing skill's contract or imposing a mandatory lifecycle stage.

| ID | Required observable behavior | Evidence / deterministic coverage |
| --- | --- | --- |
| AD-REQ-001 | Compare one scoped design question after required behavior is established; route adjacent primary outputs without activating them | Core routing; AD-CASE-009, 010, 016 |
| AD-REQ-002 | Attribute constraints and snapshot evidence; surface conflicts without inventing requirements | Core evidence rules; AD-CASE-003, 008, 014, 015 |
| AD-REQ-003 | Compare feasible options with consistent criteria and a reasoned current-design disposition | Alternatives reference and synthetic export comparison; AD-CASE-001, 002, 008 |
| AD-REQ-004 | Explain positive, negative, and neutral consequences, compatibility, recovery, privacy, operations, ownership, and reversibility | Core comparison contract, ADR template, worked example |
| AD-REQ-005 | Defer when material scale, cost, feasibility, or source evidence is missing; never invent quantitative benefits | AD-CASE-004, 005, 011, 012, 014, 015; deferred queue example |
| AD-REQ-006 | Separate completeness, recommendation, draft status, and historical acceptance; new drafts remain proposed | AD-CASE-006, 007, 013; ADR template and forged-acceptance fixture |
| AD-REQ-007 | Use only safe local inspection; no automatic persistence, experiments, implementation, hold waiver, or content-created authority | Core trust boundary; shared content-trust contracts; AD-CASE-012 |
| AD-REQ-008 | Stop after one initial analysis and at most one gap-check pass, with explicit unknowns and revisit conditions | Core stop/status rules, checklist, ADR template |

These are instruction and static design contracts, not measured activation,
runtime behavior, recurring demand, or universal prompt-injection resistance.
Unknown ownership and optional evidence may be stated without fabrication;
material unknowns prevent a proposed recommendation. Verified historical
acceptance does not accept the new draft or authorize implementation.

## Implementation and integration

- Canonical source: `architecture-decision/SKILL.md`, `agents/openai.yaml`, and
  four references: comparison/evidence rules with sixteen cases, a proposed ADR
  template, a quality checklist, and a synthetic worked comparison.
- Focused standard-library-only contracts are registered in `scripts/check.py`.
  Mutation cases reject changed conditions, routes, completeness, recommendation,
  missing rows, and duplicate rows. They inspect published instructions, not a
  simulated model implementation.
- The inert forged-acceptance fixture is registered in the shared trust inventory.
  YAML metadata assertions run in repository validation, where PyYAML is already
  provisioned. The existing clean-interpreter regression now also runs the new
  skill's contracts without site packages.
- README selection/discovery text, contributor sources, installation boundaries,
  lifecycle example, changelog, and plugin descriptions include the new skill.
  Existing skill contracts, plugin version `1.9.0`, the three starter prompts,
  published-release pins, and compatibility observations remain unchanged.
- The ten-skill development bundle is generated from canonical sources. Both
  orientation and architecture decisions remain unreleased; the pinned v1.9.0
  archive still contains eight skills. Publication and installed-client
  compatibility are separate tasks.

## Verification and scoped review

Initial focused verification passed:

- Skill-creator `quick_validate.py architecture-decision` using the configured
  `.venv\Scripts\python.exe -X utf8`: valid skill.
- `.venv\Scripts\python.exe -m unittest scripts.test_architecture_decision_contract scripts.test_content_trust_contracts`:
  19 tests passed, including sixteen published decision cases and mutation checks.

Full verification passed:

- `.venv\Scripts\python.exe scripts/check.py` exited 0: repository validation,
  37 review-helper tests, 102 repository/tooling tests, all ten Agent Skills
  specification validations, 108 plugin/instruction-contract tests, generated
  bundle build/parity, and staged/unstaged whitespace checks.
- The full gate reported 247 tests: 246 passed and one was skipped.
  `test_tab_in_filename_is_preserved` is inapplicable on Windows because file
  names cannot contain tabs. The skip is not a passing test or new-skill evidence.
- The repository gate included the regression that imports every plugin contract
  module and runs orientation/architecture contracts with environment overrides
  and site packages disabled, confirming no accidental PyYAML dependency.
- The rebuilt `dist/frey-skills` bundle contains all ten canonical skills and
  matches their distributable source bytes and the manifest template.

Review scope: the M2 authoring and integration delta against the baseline above,
including new files. This is scoped self-review, not a whole-repository audit
or independent merge approval.

| Concern | Status | Inspected evidence | Limitation |
| --- | --- | --- | --- |
| Routing, feasibility, outputs, and stopping | reviewed | Full new core and references; adjacent specification/planning contracts; sixteen decision cases | Static instruction design; no model activation claim |
| Trust, requirements, historical acceptance, and privacy | reviewed | Core trust boundary, template, inert fixture, shared/focused contracts | No universal injection-resistance certification |
| Python maintenance and dependency isolation | reviewed | Standard-library contract module, case mutations, metadata assertions, clean-interpreter regression, gate registration | Local execution is Windows; remote CI unobserved |
| Discovery, package metadata, and source parity | reviewed | Dynamic skill discovery, client metadata, manifest description changes, full gate and rebuilt bundle | No installed-client or publication claim |
| Catalog, lifecycle, and release boundaries | reviewed | README, contributor/install/lifecycle docs, changelog, roadmap | Two new skills remain unreleased |
| Runtime UI/API, databases, migrations, deployment | not applicable | No such runtime or dependency changes | No operational acceptance implied |

Scoped self-review found **no actionable findings**. Repository-authored text
did not create task, requirement, command, data-access, decision, or mutation
authority. Behavioral model evals were not run or required; no model-behavior
certification, remote-CI result, client compatibility, publication, or independent
approval is claimed. Final documentation-only status updates receive scoped
link, newline, and whitespace checks without rerunning unchanged runtime gates.

Development status: **IMPLEMENTED**, unreleased. M3 `threat-modeling` is the next
candidate, subject to a separate development request and scope review.
