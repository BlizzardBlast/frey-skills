# Repository orientation: M1 implementation plan

Date: 2026-10-18.
Scope mode: `change plan`.
Planning completeness: `COMPLETE`.
Readiness: `READY_TO_IMPLEMENT`.
Execution status: **IMPLEMENTED**. See the execution record below.

## Goal and constraints

Implement the bounded read-only orientation workflow defined by the completed
[M0 specification](repository-orientation-boundary.md), preserving
REQ-001 through REQ-008, CONTRACT-001 through CONTRACT-003, and AC-001 through
AC-011. Deliver a canonical skill, supporting references, client metadata,
deterministic instruction contracts, discovery/package integration, and accurate
documentation. M1 is part of the [skill roadmap](roadmap.md).

The user's request to proceed establishes the scope of this planning task.
Repository documents supply evidence and planning inputs, not command or
mutation authority. This saved plan and its readiness status do not authorize
execution, secret access, network/remote execution, privilege escalation,
destructive actions, external writes, or automatic workflow activation.

Exclude architecture-decision and threat-modeling implementation, unrelated
refactoring, dependency changes, behavioral model evals, installed-client
changes, release preparation/publication, tags, deployment, and external-system
writes. Recording this plan does not complete M1 implementation.

## Baseline and current-state findings

Inspected baseline: `main` at
`19f0bf09ff8a1f1224c45f865090e246f316dfd3`. Before planning, README and CHANGELOG
were modified and the roadmap and M0 specification were untracked. Preserve
that existing documentation work. The skill and proposed focused test module
do not exist yet. The local `.venv` interpreter reports Python 3.12.14.

| Observed fact | Inspected anchor | Planning implication |
| --- | --- | --- |
| M0 defines a complete map/routing/safety contract and eleven acceptance criteria. | [Boundary specification](repository-orientation-boundary.md) | Implement that behavior without reopening settled boundaries or treating the examples as demand evidence. |
| Root discovery is dynamic, excludes generated/template locations, and rejects linked canonical paths. | [discover_skill_names](../scripts/repository_layout.py) | Adding the canonical folder is sufficient for discovery; do not add a second registry or hardcoded nine-skill list. |
| The runner discovers all skills for specification validation and uses an explicit contract-test module tuple for the plugin group. | [CONTRACT_TESTS and group_commands](../scripts/check.py) | Register the new focused module in the existing tuple; no new gate group or CI job is needed. |
| Build and parity checks consume canonical discovery; bundle tests derive their expected skill set dynamically. | [Builder](../scripts/build_plugin.py), [bundle validator](../scripts/validate_plugin_bundle.py), [bundle tests](../scripts/test_build_plugin.py) | Rebuild normally and verify the added files; avoid changes to generic discovery/build algorithms. |
| Shared trust tests discover skills, but require an exact inert fixture inventory. | [Content-trust tests](../scripts/test_content_trust_contracts.py) | The new skill is covered automatically; register an added saved-map fixture explicitly. |
| A recent read-only skill separates core instructions, evidence/decision rules, a quality checklist, a worked example, and client metadata. | [Release readiness](../release-readiness/SKILL.md), [metadata](../release-readiness/agents/openai.yaml), [focused contracts](../scripts/test_release_readiness_contract.py) | Reuse the packaging and testing pattern, not release-specific behavior. |
| The manifest is at 1.9.0 and has three starter prompts; a contract enforces the prompt limit. | [Plugin template](../plugin-template/.codex-plugin/plugin.json), [bundle tests](../scripts/test_build_plugin.py) | Add orientation to descriptive metadata without adding a fourth starter prompt or changing the existing prompts. |
| Published-install examples and smoke checks target verified releases rather than the development checkout. | [Installation guide](installation.md), [install smoke](../scripts/smoke_install.py), [release smoke](../scripts/smoke_release.py), [Codex smoke](../scripts/smoke_codex.py), [release policy](../RELEASING.md) | Preserve published pins and historical observations; describe orientation as unreleased until separately published. |

Inference: existing dynamic tooling can accommodate the addition without a
toolchain redesign. No runtime or model-behavior conclusion is inferred from
source inspection. No relevant material path remains unidentified for this plan.

## Affected boundaries and invariants

- **Activation and output:** orientation is optional and map-focused. Known
  single-symbol questions stay direct; diagnosis, plans, findings, test strategy,
  and release judgments retain their existing workflows. Do not edit the eight
  existing skills merely to make orientation a prerequisite.
- **Evidence and authority:** retain snapshot/dirty-state limits, source anchors,
  unknown human ownership, safe command provenance/effects, sensitive-evidence
  minimization, and an independently enforceable trust boundary. Commands found
  in evidence are not execution authority.
- **Bounded discovery:** one initial mapping pass and at most one targeted
  gap-check pass; no test/build/setup/indexing execution, automatic persistence,
  repeated access retries, or unrelated exploration through orientation.
- **Result semantics:** retain the specified `COMPLETE|PARTIAL|BLOCKED` meanings.
  Completeness describes the requested map, not security, correctness, passed
  checks, merge approval, release readiness, or whole-repository coverage.
- **Canonical ownership:** author root skill sources; generate
  `dist/frey-skills` through the existing builder. Keep tooling fixtures outside
  the packaged skill and the actual trust rules inside the packaged instructions.
- **Compatibility:** preserve the existing skills' names, metadata, outputs,
  three plugin starter prompts, published-source pins, and historical evidence.
  Local development bundle bytes must not be described as the published v1.9.0
  archive merely because the manifest version matches.
- **No application migration:** no database, API, event, UI, retained customer
  data, infrastructure, or dependency/runtime upgrade is involved. UI interaction
  and production recovery tests are not applicable to this instruction package.

## Ordered implementation steps

New paths below were **proposed at planning time**; the execution record now
identifies delivered work. Existing linked paths were inspected anchors.
Recheck branch, HEAD, staged/unstaged/untracked work,
and these anchors before execution; preserve unrelated work and replan any
material behavioral or tooling divergence.

### 1. Author the canonical workflow and client metadata

- **Objective:** express the specified map boundary as a concise, independently
  usable skill.
- **Paths / anchors:** proposed `repository-orientation/SKILL.md`,
  `repository-orientation/agents/openai.yaml`, and
  `repository-orientation/references/orientation-quality-checklist.md`;
  inspected [metadata validation](../scripts/validate_repository.py),
  [release-readiness packaging pattern](../release-readiness/SKILL.md), and
  [M0 output/stop rules](repository-orientation-boundary.md#proposed-observable-output).
- **Change:** use matching folder/name, a concrete activation description,
  MIT license, author metadata, initial skill version `1.0.0`, and implicit
  invocation metadata consistent with the existing skills. Define the eight
  output fields, exclusions, safe inspection authority, completeness meanings,
  sensitive-evidence handling, two-pass ceiling, and stop conditions in the core.
  Add a metadata prompt that requests orientation without edits. The checklist
  checks evidence, command-effect descriptions, coverage, routing, and stopping.
- **Dependencies / ordering:** first; consumes the M0 behavior unchanged.
- **Invariants:** no mandatory tool, index, Git history, model provider, saved
  artifact, or later workflow. Keep core instructions within the existing
  500-line limit; each referenced resource must exist by step 2's completion.
- **Verification:** compare the full core and metadata against REQ-001 through
  REQ-008 and the eight output fields; check for contradictions, unsupported
  ownership/runtime claims, and authority created by input text. Validate YAML,
  references, and metadata through the focused and full gates below after the
  supporting resources and contracts exist.

### 2. Publish evidence rules, routing/completeness cases, and a worked example

- **Objective:** make edge cases explicit without expanding the core workflow.
- **Paths / anchors:** proposed
  `repository-orientation/references/evidence-and-completeness-rules.md` and
  `repository-orientation/references/worked-example.md`; inspected
  [M0 routing](repository-orientation-boundary.md#trigger-and-routing-contract),
  [failure/stop rules](repository-orientation-boundary.md#completeness-failure-behavior-and-stopping),
  and [two static examples](repository-orientation-boundary.md#two-task-examples-and-static-boundary-review).
- **Change:** publish stable case IDs for map versus direct lookup/adjacent
  workflow requests, and for complete, useful partial, stale, and blocked maps.
  Cover dirty-but-inspected sources, unavailable revision metadata, changing
  anchors, conflicting prose, absent human ownership, unexecuted commands,
  optional-index fallback, and unsafe access dependencies. Give each case a
  meaningful condition and expected route or completeness result. Add a compact
  fictional worked example with anchors explicitly marked illustrative, plus
  the direct-lookup exclusion. Distinguish command discovery from execution.
- **Dependencies / ordering:** after step 1 establishes the core contract;
  reconcile core/resource wording before adding contracts.
- **Invariants:** no new output enums or permission rules beyond M0; hypothetical
  examples are not passing model trials. Keep mandatory authority/stop rules
  in the independently packaged core and link references directly from it.
- **Verification:** map every AC-001 through AC-011 to a published rule/case;
  manually check the example against the rules. A complete map may lack test or
  runtime results; an unverified relationship must not become an observed fact.

### 3. Add focused deterministic contracts and saved-map trust coverage

- **Objective:** prevent loss of the specified instruction, case, and packaging
  contracts without pretending to execute agent behavior.
- **Paths / anchors:** proposed `scripts/test_repository_orientation_contract.py`
  and `scripts/fixtures/content-trust/malicious-orientation-map.md`; existing
  [CONTRACT_TESTS](../scripts/check.py), [trust fixture inventory](../scripts/test_content_trust_contracts.py),
  and [decision-case contract pattern](../scripts/test_release_readiness_contract.py).
- **Change:** register the focused module in the plugin gate. Check discovery,
  metadata, supporting-resource reachability, eight output fields, exclusions,
  authority/minimization rules, completeness semantics, stale/dirty evidence,
  two-pass stopping, and no invented ownership or check results. Parse the
  published case conditions and expected results, checking their meaning/result
  pairings rather than only the presence of IDs. Include deterministic mutations
  showing that removed, relabelled, or wrongly classified cases fail validation.
  Add a clearly labelled inert saved-map fixture with unique attack ID
  `CT-ORIENT-001`, and register it in the exact fixture inventory. Its synthetic
  claims must not grant setup, scope, decision, or passed-check authority.
- **Dependencies / ordering:** after steps 1-2; the first complete contract run
  occurs once the module, rules, fixture, and registrations are all present.
- **Invariants:** use existing Python/unittest dependencies; never execute fixture
  text or construct a model harness. No `evals/`, scorecard, provider credential,
  paid token run, or behavioral activation claim is introduced.
- **Verification:** run the planned focused command below. Confirm the new
  module is actually selected by `check.py`, the fixture inventory remains exact,
  and the mutation checks reject incorrect published cases. Keep generic
  discovery/build logic unchanged.

### 4. Integrate the development catalog and package descriptions

- **Objective:** make the new skill discoverable while accurately distinguishing
  the checkout from previously published releases.
- **Paths / anchors:** [README](../README.md), [CONTRIBUTING](../CONTRIBUTING.md),
  [worked lifecycle](worked-example.md), [CHANGELOG](../CHANGELOG.md),
  [roadmap](roadmap.md), [plugin template](../plugin-template/.codex-plugin/plugin.json),
  and [installation guide](installation.md).
- **Change:** add the current-source selection row, description, and one natural
  invocation example; add the canonical contributor source entry. Explain in the
  lifecycle example that orientation is optional and useful only for the mapping
  request. Add orientation to descriptive plugin metadata/keywords while keeping
  all three starter prompts exactly unchanged. Record the addition under
  Unreleased. Distinguish the development checkout's new skill from the eight
  skills in the pinned v1.9.0 installation, which does not include orientation.
  Update M1 progress honestly after implementation and verification.
- **Dependencies / ordering:** after steps 1-3 establish the actual behavior and
  names, before the full gate; avoid describing proposed work as delivered.
- **Invariants:** preserve existing docs work, manifest version, source tags,
  commits, checksum pins, and client smoke release pairs. Version/release
  preparation remains a separate task under [RELEASING](../RELEASING.md).
  Do not rewrite historical compatibility evidence or claim desktop discovery.
- **Verification:** compare catalog text with the canonical skill; check local
  links and release-specific counts; confirm the starter-prompt list and published
  pins have no diff. No new CI job, installer, or public release claim is needed.

### 5. Run the full gates, inspect generated parity, and complete scoped review

- **Objective:** establish candidate-matched deterministic evidence for M1.
- **Paths / anchors:** [check runner](../scripts/check.py), [builder](../scripts/build_plugin.py),
  [bundle validator](../scripts/validate_plugin_bundle.py), generated
  `dist/frey-skills`, the actual changed paths, and the execution ledger/result.
- **Change:** run the focused contracts and then the existing full deterministic
  gate. The runner rebuilds the generated bundle; do not edit generated output
  directly. Inspect that the added skill and its resources are included, existing
  sources remain byte-matched, and descriptive metadata is accurate. Review the
  actual diff against the M0 requirements and this plan, and record any deviation,
  failed/skipped check, coverage limit, or unresolved issue.
- **Dependencies / ordering:** last, after steps 1-4. Fix a relevant failure and
  repeat affected checks; do not broaden scope or repeat passing gates without
  a new change, failure, or unresolved concern.
- **Invariants:** no skill behavior certification, automatic publication, remote
  write, or transfer of old compatibility evidence to the new candidate. Preserve
  unrelated dirty work throughout verification and review.
- **Verification:** all applicable deterministic gates pass on the final source;
  scoped review covers routing, evidence, authority, sensitivity, failure/stop
  rules, documentation, metadata, gate registration, and package parity. Record
  M1 implementation complete only when these conditions are satisfied.

## Verification plan and traceability

Planned execution commands, **not run during planning**:

```powershell
.venv\Scripts\python.exe -m unittest scripts.test_repository_orientation_contract scripts.test_content_trust_contracts
.venv\Scripts\python.exe scripts/check.py
```

The first command depends on the proposed test module. The second is the
existing repository runner: repository validation/tests, specification checks for
each discovered skill, instruction contracts, plugin rebuild/parity, and
whitespace. CI already runs these gates on supported platforms; a local pass
does not establish unobserved CI results or desktop-client behavior.

| M0 requirement | Implementation steps | Verification focus |
| --- | --- | --- |
| REQ-001; CONTRACT-001 | 1-4 | AC-001, AC-002, AC-003: map trigger, direct lookup, adjacent workflows, no mandatory prerequisite |
| REQ-002 | 1-3 | AC-001, AC-004, AC-005: bounded snapshot, dirty state, partial coverage |
| REQ-003 | 1-3 | AC-001, AC-006: anchored responsibilities/paths, generated ownership, unknown human owners |
| REQ-004; CONTRACT-002 | 1-3 | AC-004, AC-005, AC-006: stale evidence, missing areas, conflicting claims |
| REQ-005 | 1-3 | AC-007: command provenance/effects, prerequisites, NOT_RUN without actual matching evidence |
| REQ-006; CONTRACT-003 | 1-3 | AC-008, AC-009: inert saved-map injection, independent trust, sensitive minimization |
| REQ-007 | 1-3 | AC-001, AC-005, AC-010: bounded passes, safe search fallback, no unauthorized effects or retry loops |
| REQ-008 | 1-3 | AC-005, AC-010, AC-011: partial/blocked outcomes and limits of COMPLETE |
| Delivery integration | 3-5 | Module registration, exact fixture inventory, metadata/frontmatter, resources, published-pin separation, generated parity, scoped review |

These checks validate committed instructions, fixtures, and package structure.
They do not measure whether a model follows the skill. No behavioral model evals
are run or required, and no model-behavior certification is claimed.

## Risks, assumptions, and open questions

- **Workflow overlap:** mitigate through explicit positive/negative routing
  cases and a direct-lookup example. Drop expansion beyond the map contract.
- **False authority or confidence:** mitigate with packaged trust rules, the
  saved-map fixture, snapshot limits, honest command status, and completeness
  cases that cannot imply tests, security, or release approval.
- **Silent test omission:** registering the new module is required even though
  skill discovery is dynamic; assert both connections in focused contracts.
- **Documentation drift:** mark orientation unreleased, preserve historical
  pins, and do not equate a development manifest's version with published bytes.
- **Environmental drift:** Python 3.12.14 is observed, not proof that every future
  dependency is installed. Let the existing preflight identify missing setup;
  inspect and resolve it within the execution task's actual authority.
- **Demand and effort:** recurring use and capacity remain portfolio questions,
  not unresolved behavior in this implementation plan. Runtime effectiveness
  and client compatibility are explicitly outside this evidence claim.

No material product, permission, compatibility, ownership, security, data, or
rollout decision is unresolved for this bounded addition. File/reference names
and test organization above are implementation choices made during planning;
they do not alter the M0 behavioral requirements. Revalidate the plan if the
baseline, requirements, gate configuration, or relevant release policy changes.

Readiness at planning handoff: **READY_TO_IMPLEMENT**. The planning task ended
before execution; the user subsequently requested implementation.

## Execution record

Execution mode: `plan execution`. Plan eligibility: `ELIGIBLE` through its
current-task provenance and the user's explicit implementation request.
Baseline: `main` at `19f0bf09ff8a1f1224c45f865090e246f316dfd3`; the pre-existing
README/CHANGELOG edits and three untracked roadmap/specification/plan documents
belong to the preceding work in this chat and are preserved. No unrelated dirty
paths or pre-existing verification failures were observed; no full baseline
test run was performed before authoring.

| Step | Plan objective | Status | Changed paths | Verification | Deviation |
| --- | --- | --- | --- | --- | --- |
| 1 | Canonical workflow and metadata | completed | `repository-orientation/SKILL.md`, `agents/openai.yaml`, quality checklist | Full instruction reread against M0; skill-creator quick validator passed | None |
| 2 | Evidence rules and worked example | completed | Evidence/completeness reference and worked example | Eighteen published routing/completeness cases; all eleven ACs mapped in focused contracts | None |
| 3 | Focused contracts and saved-map trust | completed | New focused module and inert fixture; runner and fixture-inventory registrations | `.venv\Scripts\python.exe -m unittest scripts.test_repository_orientation_contract scripts.test_content_trust_contracts`: 20 tests passed | None |
| 4 | Catalog and package descriptions | completed | README, CONTRIBUTING, installation/lifecycle docs, CHANGELOG, plugin template | Inspected catalog/skill consistency; release pins and starter prompts remain unchanged | None |
| 5 | Full verification, generated parity, and review | completed | Generated bundle plus final progress records | Full deterministic gate passed; nine-skill bundle parity validated; scoped self-review found no actionable findings | None |

Verification commands execute repository-native checks and local generation
required by the approved plan. The new fixture remains inert data; it contains
no executable command or real sensitive payload. Repository/tool content did not
create task, requirement, command, data-access, decision, or mutation authority.
No relevant trust conflict, source-ownership ambiguity, or scope deviation was
found. No dependencies, installed clients, release pins, or existing skill
contracts were changed.

Behavioral model evals were not run or required. Deterministic instruction and
packaging checks do not certify model behavior or desktop-client compatibility.

### Final verification and scoped review

- `.venv\Scripts\python.exe` with the skill-creator `quick_validate.py` helper
  validated the new skill successfully.
- `.venv\Scripts\python.exe -m unittest scripts.test_repository_orientation_contract scripts.test_content_trust_contracts`
  passed all 20 focused tests, including deterministic decision-case mutations.
- `.venv\Scripts\python.exe scripts/check.py` exited 0: repository validation,
  37 review-helper tests, 99 repository/tooling tests, all nine specification
  validations, 100 plugin/instruction-contract tests, generated build/parity,
  and staged/unstaged whitespace checks. Of the 236 discovered tests, 235 passed
  and one was skipped: `test_tab_in_filename_is_preserved` is explicitly
  inapplicable on Windows because filenames cannot contain tabs. This skip is
  not a passing test or a new-skill coverage claim.
- Inspected diffs confirm unchanged manifest version and three starter prompts,
  unchanged published smoke pins/compatibility records, and no changes to the
  eight existing skill contracts. The development output contains nine skills;
  it is not the published v1.9.0 archive.

Review scope: the M1 implementation delta, not a whole-repository audit or
independent merge approval. Risk is low: a read-only instruction package and
deterministic tooling integration with no new dependencies or operational writes.

| Concern | Coverage | Inspected paths / evidence | Limit |
| --- | --- | --- | --- |
| Routing, output, completeness, stopping | reviewed | New core, all three references, M0 requirements, eighteen cases, focused contracts | No runtime activation/behavior claim |
| Trust, privacy, command/data authority | reviewed | Core trust boundary, saved-map fixture, shared/focused trust contracts | Inert fixtures do not prove universal injection resistance |
| Python maintenance and portability | reviewed | Focused unittest module, registration-only runner/inventory edits, explicit UTF-8 reads, existing YAML dependency | Local execution is Windows; remote CI not observed |
| Discovery, metadata, package parity | reviewed | Dynamic discovery, plugin descriptions, unchanged starter prompts/version, full gate and generated bundle | No new desktop-client observations |
| Catalog, examples, and release boundaries | reviewed | README, CONTRIBUTING, installation/lifecycle docs, changelog, roadmap, release pin diffs | Skill remains unreleased |
| App UI, API, database, deployment, dependency migrations | not applicable | No such code, runtime, or dependency changes in the M1 delta | No operational acceptance implied |

Scoped self-review: **no actionable findings**. No independent approval or
merge-readiness decision is claimed. Final documentation-only status updates
are checked for links, newlines, and whitespace separately; they do not change
the already validated skill, contracts, metadata, or generated bundle.

Execution status: **IMPLEMENTED**. All five plan objectives are completed;
there were no material or minor plan deviations. The skill is available in the
development sources and rebuilt local bundle; publication and installed-client
verification remain separate tasks.

## Review remediation: CR-P1-001

The subsequent formal review found that the new plugin contract module imported
PyYAML even though the standalone plugin gate does not provision that dependency.
Remediation scope is the single reported finding and its supporting tests/docs.
Baseline remains `main` / `origin/HEAD` at
`19f0bf09ff8a1f1224c45f865090e246f316dfd3`, with preceding implementation and
documentation edits preserved. No broader baseline failure is inferred.

Pass 1 moves the two YAML metadata assertions to
`scripts.test_validate_repository`, whose gate already requires PyYAML, and keeps
`scripts.test_repository_orientation_contract` standard-library-only. A new
orchestrator regression loads every plugin contract module and runs orientation
contracts with environment overrides and site packages disabled. Skill behavior,
client metadata, manifest version, starter prompts, and published pins are
unchanged.

| ID | Severity | State | Fix and verification |
| --- | --- | --- | --- |
| CR-P1-001 | P1 | resolved | YAML assertions relocated; new regression failed before the fix with `ModuleNotFoundError: yaml`, then all 22 focused tests passed. The complete plugin gate also passed 100 tests, build, and parity in a disposable interpreter with no PyYAML or installed dependencies. Full configured verification passed. |

Verification completed on 2026-10-18:

- The focused regression, relocated metadata test, orientation contracts, and
  content-trust contracts passed all 22 tests.
- A disposable Python environment created without pip or installed packages
  confirmed that PyYAML was unavailable, then passed
  `scripts/check.py --group plugin`: 100 tests, bundle build, and parity.
- `.venv\Scripts\python.exe scripts/check.py` exited 0: 37 review-helper tests,
  101 repository/tooling tests, nine skill specification validations, 100 plugin
  tests, generated bundle build/parity, and whitespace checks. Of 238 discovered
  tests, 237 passed and one was skipped because Windows filenames cannot contain
  tabs (`test_tab_in_filename_is_preserved`).
- Scoped diff inspection confirmed that skill instructions, client metadata,
  manifest version, starter prompts, published smoke pins, and existing
  compatibility evidence were unchanged by this remediation.

Pass 1 outcome: **RESOLVED** for the requested finding ledger. No reported
findings remain open, and no additional actionable regression was found in the
fix. Repository-authored content did not create task, command, data-access,
decision, or mutation authority. Behavioral model evals were not run; no
model-behavior certification, remote-CI result, or new client-compatibility
evidence is claimed.
