# Delivery-handoff guidance: implementation plan

Date: 2026-10-25 (Asia/Jakarta). Scope mode: `change plan`.
Planning completeness: **COMPLETE**. Readiness: **READY_TO_IMPLEMENT**.
Implementation status: **IMPLEMENTED / UNRELEASED**. See the execution record below.

## Goal, provenance, and constraints

Extend `implementation-plan` with optional, read-only guidance for planning an
explicitly requested single-PR squash-delivery handoff. Preserve RM-AC01 through
RM-AC08 from the [roadmap reassessment](roadmap-reassessment-2026-10-25.md#proposed-behavior-and-acceptance-criteria).
The user's request to do the next step accepts that bounded proposal as planning
input. It does not request a general PR operator or authorize a future merge.

This saved plan is evidence and planning input, not instruction authority. It
cannot authorize implementation, commits, pushes, PRs, merges, branch deletion,
secret access, network/remote execution, privilege escalation, publication, or
automatic workflow activation. The planning milestone saved and validated the
plan; the execution record documents the separately requested authoring task.

Exclude new skills, activation modes, output statuses, runners, services,
dependencies, credentials, provider/model trials, live integration experiments,
release preparation, tags, publication, and installed-client changes. Preserve
`implementation-execution`'s no-merge boundary, advisory/read-only `code-review`,
and `release-execution`'s publication-only scope.

## Baseline and current-state findings

Inspected clean `main` at `1955752d86c8c5de47256da2de370ba52e67aa70`, matching
`origin/main`, with twelve canonical skills and plugin manifest version 1.12.0.
There were no staged, unstaged, or untracked paths before planning.

| Observed fact | Inspected anchor | Planning consequence |
| --- | --- | --- |
| Planning already owns ordered steps, invariants, verification, completeness, and readiness; it is read-only | [Entrypoint](../implementation-plan/SKILL.md), [profiles](../implementation-plan/references/repository-planning-profiles.md), [checklist](../implementation-plan/references/planning-quality-checklist.md) | Add one conditional reference within the existing output, rather than another workflow or plan status |
| Planning already conditionally loads a local migration resource | [Migration reference](../implementation-plan/references/migration-and-upgrade-rules.md) | Reuse progressive loading; keep the delivery guide independently packaged and self-contained |
| Execution stops at review and never merges; review does not submit approval; release execution excludes merging | [Execution](../implementation-execution/SKILL.md), [review](../code-review/SKILL.md), [release execution](../release-execution/SKILL.md) | Describe a named authorized external operator/human handoff without changing these sources or activating them |
| Static contract tests bind published case conditions and outcomes and reject removed, duplicated, or reclassified cases | [Migration contracts](../scripts/test_migration_upgrade_contract.py), [shared behavior contracts](../scripts/test_skill_behavior_contracts.py) | Reuse the standard-library unittest pattern; test committed instructions, not imagined model behavior |
| The plugin group has an explicit module tuple and a clean-interpreter regression | [CONTRACT_TESTS and group_commands](../scripts/check.py), [clean-interpreter test](../scripts/test_check.py) | Register one focused module and include it in the existing no-site-packages execution subset; add no gate or CI job |
| Build and parity consume canonical skill resources | [Builder](../scripts/build_plugin.py), [bundle validator](../scripts/validate_plugin_bundle.py) | Add the resource to its owning root skill and rebuild through the native gate; never hand-edit generated output |
| Client metadata still describes read-only planning; plugin 1.12.0 has three starter prompts | [Planning metadata](../implementation-plan/agents/openai.yaml), [plugin template](../plugin-template/.codex-plugin/plugin.json) | Preserve client metadata, implicit activation policy, plugin version/prompts, and public release pins |

Inference: the existing reference/checklist and contract-test owners can support
this extension without changing runtime architecture. No live consuming-project
policy, account, credential, or integration owner is needed to author the guide;
real delivery plans must establish those task-specific inputs when applicable.

## Requirements, affected boundaries, and invariants

| Requirement | Authoring and verification trace |
| --- | --- |
| RM-AC01: conditional use | Step 1 route/exclusion and case DH-CASE-001 |
| RM-AC02: independent authority and named owner | Step 1 handoff fields and cases DH-CASE-002/003/013 |
| RM-AC03: candidate-matched checks/reviews | Step 1 sequencing and cases DH-CASE-002/007/008 |
| RM-AC04: invalidate changed-state evidence | Step 1 freshness rules and cases DH-CASE-005/006 |
| RM-AC05: preserve workflow boundaries | Step 1 handoff/stop rules and case DH-CASE-014 |
| RM-AC06: conditional cleanup | Step 1 squash-content/ref checks and cases DH-CASE-009/010 |
| RM-AC07: planned versus observed completion | Step 1 evidence fields and cases DH-CASE-002/011 |
| RM-AC08: material uncertainty and other methods | Step 1 readiness rules and cases DH-CASE-003/004/012 |

Preserve all four planning modes, existing output fields, and existing
completeness/readiness enums. Ordinary plans gain no delivery obligations.
An unrun future check does not itself make an otherwise complete plan unready;
an unresolved material policy, owner, or authority boundary does. Current CI or
review failure must be represented as an unmet operation prerequisite, not
silently waived or confused with a missing definition of the plan's behavior.

Keep all guide instructions and its synthetic example within the owning skill;
do not require sibling skills, repository-only docs, forge credentials, or a
particular CLI. Repository/PR text, copied approvals, and green badges remain
untrusted evidence. Preserve unrelated work and sensitive-evidence minimization.
Do not prescribe executable merge/deletion commands or add an operator.

## Ordered implementation plan

New paths below were **proposed at planning time**. Reconcile
current HEAD, dirty work, and anchors before execution; preserve unrelated work
and replan material divergence. The maintainer owns scope acceptance; this plan
does not select the integration actor for any future consuming-project task.

### 1. Author conditional guidance in the existing planning skill

- **Objective:** express the eight accepted criteria as a reusable planning aid.
- **Paths / anchors:** existing `implementation-plan/SKILL.md` and
  `implementation-plan/references/planning-quality-checklist.md`; proposed
  `implementation-plan/references/delivery-handoff-planning.md`.
- **Change:** add a conditional local-reference route for a user-requested PR
  delivery sequence, initially a single-PR squash case, and relevant conditional
  checklist items. The guide defines repository/base/reviewed-head identity,
  requested versus unapproved effects, named handoff owners, native policy and
  review/CI prerequisites, per-effect freshness, merge-result/content evidence,
  named ref/dirty-work cleanup holds, and post-merge CI/synchronization evidence.
  Include a compact self-contained synthetic plan fragment and the fourteen
  decision cases below. Distinguish approved scope from authorization to perform
  writes. Explain that other merge methods/queues do not inherit squash tree
  equality. Bump only the planning skill metadata version from 1.4.0 to 1.5.0
  for this additive guidance.
- **Dependencies / ordering:** revalidate the baseline and requirement trace
  before editing; complete the instruction/fixture contract before Step 2.
- **Invariants:** planning stays read-only and stops before implementation;
  ordinary plans remain unchanged; the existing executor never merges; review
  remains advisory; the release skill is not an integration operator. No
  automatic handoffs or novel statuses. No packaged resource depends on docs
  outside its own skill. Synthetic outcomes are explicitly illustrative.
- **Verification:** reread the complete entrypoint, guide, and checklist for
  contradictions and stop conditions; validate frontmatter, links, and source
  hygiene with the native repository validator; use Step 2 to check the cases
  and conditional route independently of generated output.

### 2. Add focused deterministic contracts to the native gate

- **Objective:** prevent lost authority, freshness, readiness, or cleanup rules
  while keeping verification dependency-free.
- **Paths / anchors:** proposed `scripts/test_delivery_handoff_contract.py`;
  existing `scripts/check.py::CONTRACT_TESTS` and
  `scripts/test_check.py::CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages`;
  inspected migration/shared contract modules are examples to reuse.
- **Change:** check the conditional local route, preserved modes/output/adjacent
  boundaries, guide obligations, synthetic-example limitations, and the whole
  condition/expected-handling bindings for the fourteen published cases. Add
  mutation coverage for missing, duplicate, rewritten, or reclassified cases.
  Register the module once in the plugin tuple and execute it in the existing
  clean-interpreter subset. Keep any forged approvals/claims inert within the
  guide; add no live service mock, transcript collector, or new test framework.
- **Dependencies / ordering:** Step 1 defines the published contract. Reuse
  existing unittest/Path conventions; avoid extracting a shared parser unless
  a concrete existing helper already owns the required operation.
- **Invariants:** standard-library imports only; no PyYAML/parser dependency in
  the plugin contract; no model, network, credential, merge, branch-deletion,
  or remote-write execution. Passing tests prove source contracts only.
- **Verification:** run the new module with the shared behavior/content-trust
  modules; execute the existing clean-interpreter regression including the new
  module. Demonstrate that the specified case mutations are rejected.

### 3. Document the development addition consistently

- **Objective:** make the optional extension discoverable without claiming it
  ships in the already published archive.
- **Paths / anchors:** `README.md` implementation-plan description,
  `CONTRIBUTING.md` deterministic-contract documentation, `CHANGELOG.md`
  Unreleased, `docs/roadmap.md`, this plan, and the reassessment's current
  planning-handoff section.
- **Change:** describe the conditional guide and focused contract coverage;
  retain original dated research/evidence; reserve implementation-complete
  wording for Step 4 evidence. Record the extension as development-only until
  a separately authorized release. Link to the local guide only after it exists.
- **Dependencies / ordering:** Steps 1-2 establish the actual instructions and
  test module; update final implementation status only after Step 4 succeeds.
- **Invariants:** twelve-skill inventory; unchanged discovery/client metadata,
  plugin 1.12.0, three starter prompts, dependencies, published smoke pins,
  public artifacts, and historical desktop evidence. Do not edit another skill
  merely to add a mandatory stage.
- **Verification:** native documentation/link/inventory validation and focused
  workflow tests; inspect changed paths for unintended metadata, workflow,
  source-pin, or release modifications.

### 4. Prove the extension and record the bounded handoff

- **Objective:** deliver a verified implementation record and reviewed diff.
- **Paths / anchors:** `scripts/check.py`, canonical planning sources, all
  changed docs/tests, generated `dist/frey-skills`, and this execution record.
- **Change:** record step conformance, actual commands/results/skips, affected
  source identity, and scoped review. Build generated output only through the
  native gate. Classify remaining work explicitly when a required check fails.
- **Dependencies / ordering:** Steps 1-3; final status follows actual evidence.
- **Invariants:** no behavioral model evals, live integration experiment, client
  compatibility claim, release, or certification. A completed planning artifact
  and an implemented guide are distinct from merging any consuming PR. Handoff
  does not approve its own diff or authorize external operations.
- **Verification:** run the focused and full commands below, inspect all eight
  criteria and related negative cases, and review authority/privacy, Python
  practices and ownership, portability, packaging, documentation, and readiness
  semantics. Stop on required failure or material deviation.

## Planned decision coverage

Expected handling below is published planning guidance, not actual effects or
new enum values. Bind these conditions in Step 2 without pretending to execute
a model or forge integration.

| Case | Condition | Expected planning handling |
| --- | --- | --- |
| DH-CASE-001 | Ordinary change plan has no requested delivery sequence | Skip delivery obligations and retain the existing plan contract |
| DH-CASE-002 | Scope, owners, policy, paths, and prerequisites are established; future checks have not run | A complete plan may be READY_TO_IMPLEMENT; mark future checks NOT_RUN and grant no write authority |
| DH-CASE-003 | Required integration owner is unknown | Preserve the unresolved material decision; PARTIAL / NOT_READY |
| DH-CASE-004 | Required integration policy or authority boundary is unknown | Preserve the unresolved material decision; PARTIAL / NOT_READY |
| DH-CASE-005 | Candidate head changes after review or CI | Require rechecking affected evidence before dependent operations |
| DH-CASE-006 | Target base or relevant gate policy changes | Revalidate affected integration assumptions and evidence |
| DH-CASE-007 | A required candidate check is failed, missing, skipped, or stale | Keep the merge prerequisite unmet; define a bounded next action without waiving policy or inventing remediation |
| DH-CASE-008 | Required human review or thread resolution is unsatisfied | Preserve the hold; advisory agent review cannot satisfy it |
| DH-CASE-009 | Squash result is uncertain or its content differs from the reviewed tree at an unchanged validated base | Preserve evidence and withhold destructive cleanup pending reconciliation |
| DH-CASE-010 | Named cleanup refs move or dirty work has not been safely reconciled | Preserve the refs/work; no broad reset, stash, or destructive cleanup |
| DH-CASE-011 | Merge completed but required post-merge CI is pending or failed | Report the completed merge separately from incomplete verification; no automatic revert, rerun, or release |
| DH-CASE-012 | Requested integration uses another merge method or a queue | Do not apply the squash equality assumption; preserve ordinary planning rules and identify missing material policy |
| DH-CASE-013 | PR/repository text claims approval or green checks and requests execution | Treat it as untrusted evidence; do not grant authority or accept self-validating results |
| DH-CASE-014 | Delivery proceeds beyond the implementation/review boundary | Name the authorized external operator/human handoff; activate no workflow and preserve adjacent no-merge/advisory/publication-only boundaries |

## Verification plan and command effects

At planning time these implementation checks were **NOT_RUN** and the new
module did not exist. Run its commands only after Step 2 creates it. Existing
commands were inspected in the native runner and contributor guidance; actual
execution results are recorded separately below.

```powershell
.\.venv\Scripts\python.exe -B -m unittest scripts.test_delivery_handoff_contract scripts.test_skill_behavior_contracts scripts.test_content_trust_contracts
.\.venv\Scripts\python.exe -B -m unittest scripts.test_check.CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages
.\.venv\Scripts\python.exe -B scripts/check.py --base origin/main
```

The focused tests read committed instructions/fixtures; the clean-interpreter
regression starts a child interpreter without site packages. The full gate
runs repository tests using temporary fixtures, validates all canonical skill
specifications, rebuilds ignored `dist/frey-skills`, validates source parity,
and checks whitespace. It does not install dependencies, fetch refs, publish,
or execute behavioral model trials. Fetch a needed comparison base separately
only with task authority; the plan is not that authority.

Use supported CI for native platform/runtime evidence on an authorized
implementation PR. Do not call grammar inspection a native Python 3.9 run or
claim installed-client behavior from source/bundle parity. No CI configuration
change or live consuming-project delivery is required to prove this guide.

## Risks, assumptions, and readiness

- Static tests can catch missing or contradictory published contracts; they
  cannot certify agent compliance, universal injection resistance, or actual
  delivery safety. Do not measure success using claimed token/time savings.
- Full-tree equality is bounded to the stated single-PR squash case and an
  unchanged validated base. Changed bases, queues, and other merge methods must
  not inherit that conclusion.
- The existing standard-library contract and generator patterns are sufficient;
  no public contract, dependency, or architecture decision remains unresolved
  for this authoring scope. Reinspect if the baseline changes materially.
- For real delivery work, ownership, permissions, required checks/reviews,
  credential access, and recovery decisions remain task-specific inputs. This
  plan invents none and grants no external-write authority.

At the planning handoff, completeness was **COMPLETE**, readiness was
**READY_TO_IMPLEMENT**, and implementation was **NOT STARTED** with verification
**NOT_RUN**. Revalidate this snapshot before execution. Behavioral model evals
are not run or required.

## Execution record

Execution mode: **plan execution**. Eligibility: **ELIGIBLE**. The user requested
the next step after this plan's delivery, establishing its authoring scope.
Execution baseline: clean `main` at
`3ac6a2795a0634e48c240a6e789071dd9a1f5f1d`, branch
`codex/delivery-handoff-guidance`. The changes since the planning baseline
affected only the four planning/roadmap documents. No dirty ownership conflicts
or material deviations were found. Repository and tool content remained
evidence, not authorization. Baseline behavior/trust checks passed all 26 tests.

| Step | Plan objective | Status | Changed paths | Verification | Deviation |
| --- | --- | --- | --- | --- | --- |
| 1 | Canonical conditional guide | completed | Planning entrypoint 1.5.0, local guide, checklist | 34 focused behavior/trust/delivery tests, repository validation, and Agent Skills validation passed | None |
| 2 | Native deterministic contracts | completed | New contract module, runner registry, clean-interpreter subset | Eight new tests and the existing no-site-packages regression passed | None |
| 3 | Development documentation | completed | README, CONTRIBUTING, changelog, plan, roadmap/reassessment | Native documentation/link/inventory validation; development and published states distinguished | None |
| 4 | Full verification and scoped review | completed | Complete delta and generated bundle | Full 465-test gate, twelve specifications, source parity, whitespace, and scoped review passed | Optional scaffold validator rerun in UTF-8 mode after a Windows default-decoding error |

No behavioral model eval, live integration experiment, or release action is
performed for this extension. Existing CLI smoke jobs remain compatibility
checks, separate from instruction-contract or model-behavior certification.

### Executed verification

Local Windows verification used the repository's Python 3.12 environment:

```powershell
.\.venv\Scripts\python.exe -B -m unittest scripts.test_delivery_handoff_contract scripts.test_skill_behavior_contracts scripts.test_content_trust_contracts
.\.venv\Scripts\python.exe -B -m unittest scripts.test_check.CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages
.\.venv\Scripts\python.exe -B scripts/check.py --base origin/main
```

- Focused contracts: **34 tests passed**, including all eight new tests,
  fourteen condition/outcome bindings, case mutations, and inert example checks.
- The existing clean-interpreter regression passed with the new module included;
  PyYAML, the Markdown parser, and other site packages were unavailable there.
- Full gate: **465 tests run, 459 passed, six expected Windows skips** (57 helper,
  245 repository/tooling, and 163 plugin/contract tests). All twelve Agent Skills
  specifications, generated plugin build/source parity, and whitespace passed.
  Final log: ignored `dist/delivery-handoff-final-check.log`.
- Repository validation and skill-creator scaffold validation passed. The first
  optional scaffold invocation failed before validation because its reader used
  Windows cp1252; rerunning the same validator with Python UTF-8 mode passed.
  No source change was needed to manufacture a pass.
- All three changed Python files parsed with Python 3.9 grammar. This is not a
  native Python 3.9 runtime claim. Hosted CI supplies separately identified
  runtime/platform evidence on the implementation PR.
- Client metadata, adjacent skills, plugin template/version/prompts, dependency
  pins, published-source pins, and CI workflows have no diff from the execution
  baseline. Final record-only changes receive repository/link, documentation,
  and whitespace checks; packaged inputs are unchanged by those records.
- A pre-commit byte check found retained CRLF in the edited planning checklist.
  That changed canonical file was normalized to LF before staging; the refreshed
  full gate passed with the same 465-test counts and rebuilt source parity.
  This keeps tested package bytes aligned with Git's committed text; no unrelated
  file was normalized.

### Scoped review and handoff

Scope mode: **diff review** of this bounded implementation against the execution
baseline. Risk tier: **high** attention to authority, merge prerequisites, and
destructive-cleanup guidance, despite the planning-only runtime boundary.
Review completeness: **COMPLETE**. Decision: **APPROVE** (advisory); no actionable
findings. Completeness covers the inspected delta, not exhaustive defect or
model-behavior detection.

| Concern | Status | Inspected paths/config | Commands/evidence | Limitation |
| --- | --- | --- | --- | --- |
| Behavior, routing, readiness | reviewed | Planning entrypoint, guide, checklist, eight-criterion trace | Conditional-route tests; fourteen cases; ordinary-plan exclusion and unrun-versus-unknown decisions | Static instruction contracts |
| Authority and privacy | reviewed | Guide trust/owner rules, inert claim, unchanged adjacent skills | Shared trust tests; no-merge/advisory/publication-only assertions; no secrets or executable operation recipes | No universal injection-resistance claim |
| Freshness, concurrency, recovery | reviewed | Candidate/base/policy guards, named-ref cleanup, post-merge evidence | Changed-state, failed/missing checks, review holds, mismatch, dirty-work, and pending/failed closure cases | No real merge or recovery experiment used to validate the guide |
| Python practices and SOLID | reviewed | New cohesive unittest module, registry/subset additions | Standard library, explicit UTF-8 reads, bounded local fixtures/case mutations; no speculative interfaces or runtime operator | No application architecture change |
| Packaging and discovery | reviewed | Root planning skill, client metadata, plugin template, generated bundle | Twelve specifications, source parity, repository inventories, unchanged activation and prompts | Development guide is absent from public v1.12.0 |
| Portability and CI | reviewed | Changed Python and existing gate/clean-interpreter entrypoints | Full local gate, no-site-packages regression, Python 3.9 grammar | Native cross-platform results belong to matching hosted CI |
| Documentation | reviewed | README, CONTRIBUTING, changelog, roadmap, reassessment, plan | Native links/inventories, explicit historical/current states, scoped record validation | Does not establish wider usage demand or measured savings |
| UI, API, database, deployment | not applicable | Complete changed-path scope | No application UI, service, schema, dependency, deployment, or release action changed | Installed desktop behavior remains separate evidence |

Execution status: **IMPLEMENTED**. The implementation phase hands off the
verified diff for review/delivery. Any actual PR integration or cleanup is a
separate user-authorized operation outside these planning/execution skill
boundaries. No release, tag, public artifact replacement, model trial, or
behavioral certification is authorized by this record.
