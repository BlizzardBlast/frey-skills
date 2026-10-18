# M3 threat-modeling development record

Date: 2026-10-18. Baseline: clean `main` at
`d9d48b580f93f8421e237ec20522122a73e325d3` (M2 merged).
Development branch: `codex/threat-modeling`.

The user requested the next development step. Repository inspection identified
M3 as the next unfinished milestone. Scope is one read-only threat-modeling
skill, supporting references/client metadata, focused deterministic contracts,
and catalog/plugin integration. This is direct skill authoring; the roadmap is
candidate evidence, not an approved executable plan or authority for commands,
data access, security decisions, or external writes.

## Boundary and acceptance

The requested artifact is a scoped system model and threat-hypothesis ledger.
It complements implementation review and risk-based test strategy without
validating findings, executing tests, choosing architecture, remediating,
publishing, or accepting risk. Existing skill contracts remain unchanged.

| ID | Required observable behavior | Evidence / deterministic coverage |
| --- | --- | --- |
| TM-REQ-001 | Model a bounded feature/system/flow/design with scope, snapshot, exclusions, and implementation/design evidence distinctions | Core workflow/output, system-model reference; TM-CASE-016, 019 |
| TM-REQ-002 | Cover assets/sensitive data, actors, privileges, entry points, flows, boundaries, ownership policy, and dependencies without inventing them | System inventory, worked callback example; TM-CASE-001, 002, 003, 004, 008 |
| TM-REQ-003 | Use stable threat IDs tied to actors, preconditions, assets, flows, boundaries, paths, impact, and evidence; keep threats as hypotheses | Ledger contract and focused output/field checks; twenty-one decision cases |
| TM-REQ-004 | Separate existing control evidence, effectiveness, and proposed mitigations; preserve residual risk and validation limits | Control-status contract and callback ledger; TM-CASE-005, 017, 021 |
| TM-REQ-005 | Preserve holds and exact prior risk-acceptance provenance; reject content-created acceptance or permissions | Core trust/acceptance rules, inert diagram/log fixture; TM-CASE-006, 007, 018 |
| TM-REQ-006 | State partial or blocked coverage, including ambiguous ownership, stale boundaries, inaccessible evidence, and necessary unauthorized effects | Completeness rules and worked variants; TM-CASE-004, 008, 009, 010, 011 |
| TM-REQ-007 | Keep finding validation, implementation review, test strategy, and architecture choice separate, with no automatic activation | Core routing and TM-CASE-012 through 015 |
| TM-REQ-008 | Stop within one initial model and one optional gap-check pass; retain unknowns and refresh conditions, allowing an explained bounded empty ledger | Core stop/output, checklist and example; TM-CASE-020 |

The model's completeness describes coverage, not control success, vulnerability
confirmation, risk acceptance, or security certification. The design example is
synthetic; demand, runtime activation, and model effectiveness remain unmeasured.
The cited OWASP guidance supplies background; this repository's read-only and
authority boundaries govern the new skill.

## Implementation and integration

- Canonical sources are `threat-modeling/SKILL.md`, `agents/openai.yaml`, and four
  references: system-model/threat-ledger rules, evidence/completeness cases, a
  quality checklist, and a synthetic callback/logging example.
- `scripts.test_threat_modeling_contract` remains standard-library-only and is
  registered in `scripts/check.py`. Its table mutations reject changes to
  conditions, routes, completeness, and threat interpretation, including forged
  confirmation, missing cases, and duplicate IDs. These inspect instructions;
  they are not a model-behavior simulator or executed security trial.
- The inert diagram/log fixture is registered in the shared content-trust
  inventory. YAML metadata assertions stay in repository validation, which
  already provisions PyYAML. The clean-interpreter regression now also runs the
  new contracts without site packages.
- Catalog, contributor, installation, lifecycle, changelog, roadmap, and plugin
  descriptions include threat modeling. The eleven-skill development bundle
  contains three unreleased additions; pinned v1.9.0 still has eight skills.
  Manifest version, three starter prompts, published smoke pins, compatibility
  observations, existing skill contracts, and dependencies are unchanged.

## Verification and scoped review

Initial focused verification passed:

- Skill-creator `quick_validate.py threat-modeling` using
  `.venv\Scripts\python.exe -X utf8`: valid skill.
- `.venv\Scripts\python.exe -m unittest scripts.test_threat_modeling_contract scripts.test_content_trust_contracts scripts.test_validate_repository.RepositoryValidatorTests.test_threat_modeling_metadata_preserves_invocation_contract scripts.test_check.CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages`:
  all 21 tests passed, including the metadata assertion and clean-interpreter
  regression as well as the focused/shared instruction contracts.

Full deterministic validation passed:

- `.venv\Scripts\python.exe scripts/check.py` exited 0: repository validation,
  37 review-helper tests, 103 repository/tooling tests, all eleven Agent Skills
  specification validations, 116 plugin/instruction-contract tests, generated
  bundle build/parity, and staged/unstaged whitespace checks.
- The full gate reported 256 tests: 255 passed and one was skipped.
  `test_tab_in_filename_is_preserved` is inapplicable on Windows because file
  names cannot contain tabs. This skip is not a passing test or new-skill evidence.
- Repository tests included the clean-interpreter regression for all three
  unreleased skill contract modules with environment overrides and site packages
  disabled, confirming no accidental PyYAML dependency in the standalone group.
- The rebuilt `dist/frey-skills` bundle contains all eleven canonical skills
  and passes distributable source/template byte parity.

Review scope: the complete M3 authoring/integration delta against the baseline
above, including new files. This is scoped self-review, not a whole-repository
audit, model trial, independent approval, or security assessment of a real system.

| Concern | Status | Inspected evidence | Limitation |
| --- | --- | --- | --- |
| Skill intent, routing, model/ledger outputs, and stopping | reviewed | Full core and references; roadmap M3 scope; adjacent review/test-strategy boundaries; twenty cases | Static instruction design; no runtime activation claim |
| Hypotheses, controls, privacy, risk acceptance, and holds | reviewed | Core trust/evidence rules, system/ledger reference, inert fixture and callback example | Modeling cannot certify vulnerabilities, effectiveness, or security |
| Python maintenance and dependency isolation | reviewed | Standard-library contracts, case mutations, UTF-8/path handling, metadata assertions, clean-interpreter regression and registrations | Local execution is Windows; remote CI unobserved |
| Discovery, client metadata, and generated packaging | reviewed | Dynamic discovery, metadata, plugin description changes, full gate and rebuilt bundle | No installed-client or publication evidence |
| Catalog, lifecycle, and release boundaries | reviewed | README, contributor/install/lifecycle docs, roadmap, changelog | Three development skills remain unreleased |
| Runtime UI/API, databases, migrations, deployment | not applicable | No such runtime or dependency changes | No operational acceptance claimed |

Initial scoped self-review found **no actionable findings**. Repository-authored text
did not create task, requirement, command, data-access, decision, mutation, or
risk-acceptance authority. Behavioral model evals were not run or required;
no model-behavior certification, remote-CI result, publication, installed-client
behavior, or independent approval is claimed. Final documentation-only status
updates receive scoped link, newline, and whitespace checks without rerunning
unchanged implementation gates.

Development status: **IMPLEMENTED**, unreleased. M4 is the next milestone:
reassess the proposed performance extension and incident-retrospective demand
against their extraction conditions before deciding whether to build anything.

## Review remediation

The subsequent requested code review identified one finding, `CR-P2-001` (P2).
The user's request to fix all findings authorized this bounded remediation.
Baseline: the existing uncommitted M3 candidate on `codex/threat-modeling`, with
`origin/HEAD` resolving to `origin/main` at
`d9d48b580f93f8421e237ec20522122a73e325d3`. The earlier full gate passed with
one expected Windows skip; no other reported findings were outstanding.

Pass 1 corrected the unsupported inference that a reported control is absent.
The core now leaves its implementation and effectiveness unverified. The
control-status reference and worked example explicitly prohibit inferring
absence when implementation is outside the inspected scope. Proposed mitigations
remain separate from evidence of implemented protection. `TM-CASE-021` covers
the reported-control condition, and the contract oracle and case-count
documentation now include all twenty-one cases.

| Finding | State | Resolution and evidence |
| --- | --- | --- |
| CR-P2-001 | resolved | Corrected workflow step 5, `REPORTED` definition, completeness guidance, and example; revised instruction assertions and added TM-CASE-021 to the published table and mutation checks |

Verification for pass 1:

- The revised `scripts.test_threat_modeling_contract` failed against the old
  instructions with the expected missing-contract/case assertions, then passed
  after the correction. These are deterministic instruction checks, not trials
  of model behavior.
- The exact focused unittest command above passed all 21 tests, including shared
  trust contracts, metadata validation, and the clean-interpreter regression.
- `.venv\Scripts\python.exe scripts/check.py` exited 0: 37 review-helper tests,
  103 repository/tooling tests, 116 plugin/instruction-contract tests, all eleven
  Agent Skills specification validations, rebuilt bundle parity, and whitespace.
  Total: 255 passed and the same one Windows-only filename test skipped.
- Scoped rereading confirmed that the revised core, evidence rules, control
  statuses, and example preserve uncertainty without changing authority or
  acceptance boundaries. Final documentation-only edits received link, newline,
  and whitespace checks.

Final status: **RESOLVED**. No selected findings remain unresolved, blocked, or
deferred. Existing M3 work is preserved and remains uncommitted and unreleased.
Behavioral model evals were not run; no model-behavior certification is claimed.

## Follow-up review remediation

The next requested review found `CR-P3-001` (P3): the README folder inventory
still listed nine skills. Baseline: the same uncommitted twenty-file M3
candidate on `codex/threat-modeling`, compared with `origin/HEAD` at
`d9d48b580f93f8421e237ec20522122a73e325d3`. The previous control-evidence
finding remained resolved; verification had one expected Windows skip.

Pass 1 added the missing `architecture-decision/` and `threat-modeling/` entries
to the README's current layout. Direct comparison with `discover_skill_names`
confirmed that its selection table, skill descriptions, and folder inventory
each contain exactly the eleven canonical skills without duplicates.

| Finding | State | Resolution and evidence |
| --- | --- | --- |
| CR-P3-001 | resolved | README folder inventory matches canonical discovery; the selection table and descriptions also match |

`.venv\Scripts\python.exe scripts/check.py` exited 0: 255 tests passed, the
same Windows-only filename test was skipped, all eleven skill specifications
validated, and rebuilt bundle parity and whitespace checks passed. Final
documentation edits received newline, link, and whitespace checks. Only the
README and this supporting record changed during this remediation.

Final status: **RESOLVED** for the selected finding; none remain unresolved,
blocked, or deferred. Existing M3 work remains uncommitted and unreleased.
Behavioral model evals were not run; no model-behavior certification is claimed.
