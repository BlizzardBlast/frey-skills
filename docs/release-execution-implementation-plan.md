# Release-execution implementation plan

Date: 2026-10-19. Baseline: clean `main` at
`b3ce95d98f9213519a67899c16d815a47e2b1ca0` after PR #30.
Development branch: `codex/release-execution`.

Scope mode: **change plan**. Planning completeness: **COMPLETE**.
Readiness at handoff: **READY_TO_IMPLEMENT**. Execution eligibility: **ELIGIBLE**.
The user accepted the recommended target, permission model, and ownership and
requested the specification, planning, and implementation sequence in this task.
This plan was produced in that sequence; it was not discovered as self-approved
repository authority. Publication of any version is outside this development task.

## Goal, findings, and invariants

Implement the [adopted specification](release-execution-scope.md), preserving
REX-REQ-001 to 006, REX-AC-001 to 011, and REX-CONTRACT-001 to 003.

Observed: `release-readiness` is read-only. `RELEASING.md`,
`.github/workflows/release.yml`, and existing preparation/archive verifiers already
own packaging, publication, and byte comparison. `scripts/repository_layout.py`
discovers root skill trees; `scripts/check.py` registers standard-library plugin
contracts. Generated `dist/frey-skills` is rebuilt, not edited. Client installation
checks intentionally pin published v1.10.0, independent of development inventory.

The new skill coordinates existing mechanisms; it adds no executable release
runner, dependency, credential store, workflow permission, deployment, or public
API. Keep the three plugin starter prompts, published pins, existing skill
contracts, and v1.10.0 release identity unchanged. The new skill is unreleased.
Use ordinary automatic discovery with mutation authority checked separately.

## Ordered implementation plan

1. **Objective:** establish adopted behavior before authoring.
   **Paths / anchors:** `docs/release-execution-scope.md`, Q1-Q3, REX ledgers.
   **Change:** record user adoption, supported effects, ownership, exclusions,
   and complete planning input; save this separate plan during execution.
   **Dependencies:** the current user request.
   **Invariants:** development approval is not release approval; requirements
   remain behavioral, with every must mapped to observable acceptance.
   **Verification:** inspect all six requirements, eleven criteria, three
   contracts, and resolved decisions for contradictions and traceability.
2. **Objective:** publish independently enforceable workflow instructions.
   **Paths / anchors:** new `release-execution/SKILL.md`, `agents/openai.yaml`,
   and `references/github-release-procedure.md` and
   `references/evidence-and-recovery-rules.md`; inspected native release tools.
   **Change:** define candidate-bound authority, native operations, receipts,
   failure states, independent bytes, finite stopping, and supported recovery.
   **Dependencies:** step 1.
   **Invariants:** never force/overwrite, infer approval, run downloaded helpers,
   extend budgets automatically, or treat local bytes as public evidence.
   **Verification:** read the entire skill and references; validate YAML and
   source/reference discovery, cases, and packaging through steps 3-5.
3. **Objective:** guard high-risk published decisions without model trials.
   **Paths / anchors:** new `scripts/test_release_execution_contract.py` and
   inert `scripts/fixtures/content-trust/malicious-release-receipt.md`;
   `scripts/check.py`, `scripts/test_check.py`,
   `scripts/test_content_trust_contracts.py`, `scripts/test_validate_repository.py`.
   **Change:** bind conditions, permitted effects, and outcomes; mutate cases
   to prove omissions/misclassification fail; register trust and clean-interpreter
   checks. Keep YAML-dependent metadata checks in repository validation.
   **Dependencies:** step 2.
   **Invariants:** tests are standard-library-only in the plugin group, execute
   no fixture instructions, and do not claim model-behavior certification.
   **Verification:** run focused contract/trust/metadata checks and the existing
   `-B -E -S` clean-interpreter regression; parse new Python with 3.9 grammar.
4. **Objective:** expose the addition consistently without claiming release.
   **Paths / anchors:** README selection table/descriptions/layout,
   `CONTRIBUTING.md`, `CHANGELOG.md` Unreleased, `docs/roadmap.md`,
   `docs/installation.md`, `plugin-template/.codex-plugin/plugin.json` descriptions/keywords.
   **Change:** document the twelfth development skill and its authority boundary;
   preserve the eleven-skill published installation and release records.
   **Dependencies:** steps 2-3.
   **Invariants:** retain plugin version and three starter prompts; no pin update,
   tag, public asset, release, or real client installation is created.
   **Verification:** compare all current README inventories with canonical
   discovery, validate metadata/specs, rebuild and check plugin parity.
5. **Objective:** prove the bounded addition and record a reviewable handoff.
   **Paths / anchors:** `scripts/check.py`, this execution record, complete delta.
   **Change:** record actual results, skips, limits, plan conformance, and review
   coverage for intended behavior, Python/SOLID, security/privacy, portability,
   packaging, docs, concurrency, and recovery.
   **Dependencies:** steps 1-4.
   **Invariants:** no behavioral model evals, publication, real credentials, or
   desktop certification; no unrun result is presented as passing.
   **Verification:** `.venv\Scripts\python.exe scripts/check.py --base origin/main`,
   focused contracts, local Markdown links/anchors, and `git diff --check`.

## Risks and limits

Published instructions and inert decision tests cannot prove agent behavior or
universal injection resistance. A GitHub pipeline may partially succeed; the
skill must preserve uncertainty and stop instead of retrying. Native pipeline
changes require renewed inspection. Unavailable tools/credentials remain blockers.
The optional v1.10.0 desktop checklist is separate and is not performed here.
There are no unresolved material planning decisions or new runtime dependencies.

## Execution record

Execution mode: **plan execution**. No pre-existing dirty or untracked paths,
known failing checks, or ambiguous work ownership were found at baseline.
Relevant repository text was inspected as evidence; it did not grant authority.

| Step | Plan objective | Status | Changed paths | Verification | Deviation |
| --- | --- | --- | --- | --- | --- |
| 1 | Adopt specification and plan | completed | Scope and this plan | Six requirements, eleven criteria, three contracts, Q1-Q3 inspected | None |
| 2 | Canonical skill and resources | completed | New skill, client metadata, two references | Repository and Agent Skills validation; full instruction reread | Native helpers are referenced as target-repository modules, avoiding false packaged-resource paths |
| 3 | Deterministic contracts | completed | New contract module/fixture; check registry, clean-interpreter, trust, and metadata tests | 21 focused tests passed, including eight new contract tests and clean-interpreter loading | Initial test-selector typo corrected; no behavior change |
| 4 | Catalog and package integration | completed | README, contributor/install/release/roadmap docs, changelog, plugin template | All three README inventories match twelve canonical skills; twelve specs and rebuilt plugin parity passed | Published v1.10.0 pins and three starter prompts preserved |
| 5 | Final validation and scoped review | completed | Complete twenty-file delta and this record | Full gate, 89 links/anchors, syntax, whitespace, review coverage below | Native runtime verification is Windows-local |

### Verification evidence

On 2026-10-19, the repository's Python 3.12 environment on Windows passed:

```powershell
.\.venv\Scripts\python.exe -B -m unittest scripts.test_release_execution_contract scripts.test_content_trust_contracts scripts.test_validate_repository.RepositoryValidatorTests.test_release_execution_metadata_preserves_discovery_and_scoped_authority scripts.test_check.CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages
.\.venv\Scripts\python.exe -B scripts/check.py --base origin/main
```

- Focused: **21 tests passed**, including eight new tests, twenty-two published
  decision conditions, mutation checks, trust-fixture hygiene, metadata, and the
  existing subprocess regression with `-B -E -S` and no site packages.
- Full gate: **293 tests run, 287 passed, six expected platform skips**: 46 review
  helper tests (six skips), 106 repository/tooling tests, and 141 plugin/contract
  tests. All twelve Agent Skills specifications, generated build/parity, and
  whitespace gates passed. Negative-test diagnostics in the log are expected
  assertions, not failed gates.
- All three current README inventories equal canonical discovery: twelve skills.
  All **89 local links/anchors across thirteen changed Markdown files**, embedded
  Python recipe syntax, and final newlines passed. Changed Python parsed with
  Python 3.9 grammar; this is not a Python 3.9 runtime claim. The bundled
  skill-creator frontmatter/name/scaffold check passed for the new skill.
- The first focused command used an incorrect test class selector and failed
  before that metadata test ran. The corrected complete selection passed. Initial
  repository validation also caught native helper paths being interpreted as
  packaged resources; module notation corrected that distinction, and validation
  then passed. Neither failure was hidden or counted as a pass.
- Ignored local logs are `dist/release-execution-focused.log` and
  `dist/release-execution-validation.log`. Final record-only updates receive
  scoped Markdown/newline/whitespace checks without repeating unchanged suites.

### Scoped review

Scope mode: **diff review**, including all new files, against the baseline above.
Review completeness: **COMPLETE**. This is a self-review of the bounded addition,
not independent approval or a whole-repository audit.

| Concern | Status | Inspected paths/config | Commands/evidence | Limitation |
| --- | --- | --- | --- | --- |
| Intended skill behavior and authority | reviewed | Scope, plan, new SKILL.md and both references | Six requirements/eleven criteria traced to twenty-two decision cases; complete instruction reread | Instructions do not prove agent behavior |
| Python, design, and SOLID | reviewed | New contract module; check registry, clean-interpreter and metadata tests; existing native verifier interfaces | Standard-library contract suite reuses native ownership; YAML assertions remain in repository validation | No new runtime architecture, inheritance, or interface hierarchy |
| Security and privacy | reviewed | Trust boundary, inert forged receipt, credential/hold rules, native workflow scope | Shared trust checks and focused authority/verification cases passed | No universal injection-resistance claim; no credentials inspected |
| Concurrency, failure, and recovery | reviewed | Per-mutation rechecks, non-forced tag flow, effects/receipt rules, cases 011-020/022 | Changed refs, conflicts, timeout, missing/mismatched assets, budgets, and fresh recovery authority are distinguished | No actual publication or failure-recovery experiment |
| Packaging and discovery | reviewed | Root skill tree, client YAML, plugin template, source discovery | Twelve specs, plugin build/parity, exact preserved starter prompts, no site packages | Unreleased; installed v1.10.0 remains eleven skills |
| Documentation | reviewed | README's three inventories, contributor/install/release/roadmap docs, changelog, scope and plan | 89 links/anchors, recipes, newlines, consistent published/development identities | Historical compatibility evidence is not inherited |
| Portability and CI | reviewed | Existing CI groups, new registrations, path/encoding handling, grammar | Full local Windows gate; clean interpreter; Python 3.9 grammar | New native Linux/macOS/Python 3.9 runtime and hosted CI were not run |
| UI, API, database and deployments | not applicable | Complete delta | No UI, service, schema, deployment, or workflow-permission implementation changes | Desktop UI compatibility is separate |

Findings: **No remaining actionable findings in this scoped delta**.
Decision: **APPROVE**, as advisory self-review only. No external approval,
merge, publication, or operational acceptance is established by this decision.

Repository-authored text cannot create task, requirement, command, data,
decision, mutation, recovery, or risk-acceptance authority. Behavioral model evals
were not run, and no model-behavior certification is claimed. No publication,
real client installation, credential procurement, or desktop check ran here.

Execution status: **IMPLEMENTED**, unreleased. All required plan steps and local
verification completed; the diff is ready for an independently authorized review
and integration task. No material deviation or unresolved implementation blocker
remains.
