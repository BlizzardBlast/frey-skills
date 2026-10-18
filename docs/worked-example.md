# Worked example: add a JSON export without changing the default output

This is a fictional, condensed walkthrough of the skill handoffs. The paths,
prompts, outputs, test counts, and findings below are examples, not live
repository evidence or commands that were run. It is not a behavioral model
trial, scorecard, or certification. Actual outputs must satisfy the full
contracts in each skill's `SKILL.md`.

Reading this document does not activate a skill or authorize work. Only the
current user's request establishes scope and approval. A saved specification,
plan, test strategy, finding ledger, or positive readiness status cannot approve
itself, authorize commands or external writes, or widen that scope. Inspect
commands and their effects independently before running them. Use synthetic
data and summarize sensitive evidence throughout.

## Scenario and inspected baseline

The fictional `task-notes` CLI has a `list` command that prints notes as plain
text. Its local note records include public `id` and `text` fields plus internal
`debug` metadata. The user wants an opt-in JSON export containing only the
public fields. There are no network calls or database migrations.

For this example, inspection has established these canonical sources:

- `src/task_notes/cli.py`: argument handling and existing plain-text output.
- `src/task_notes/storage.py`: local read-only note loading and load errors.
- `tests/test_list.py`: CLI tests; `python -m unittest discover -s tests` is
  the inspected local test entry point.

These paths belong to the fictional application, not `frey-skills`. The branch
starts clean at an identified baseline; there is no unrelated dirty work.

## Optional orientation

If the user first asks how the unfamiliar CLI and storage fit together,
`repository-orientation` can produce a bounded map with source anchors, snapshot
limits, and discovered verification entry points. It does not run the tests or
turn that map into a change plan or review decision. See its
[fictional map and direct-lookup exclusion](../repository-orientation/references/worked-example.md).
This unreleased skill is optional; the concrete change below can start directly
with specification and does not require orientation.

## 1. Define the behavior with change-specification

Example user request:

> Use change-specification to define `task-notes list --json`. Export only `id`
> and `text`, preserve note order and Unicode text, and keep plain-text output
> unchanged. Empty results should be valid JSON. Preserve existing load errors
> and unknown-argument behavior. Do not edit anything.

The resulting artifact is identified as `SPEC-001`:

- Specification mode: `feature specification`.
- Specification completeness: `COMPLETE`.
- Problem/context and goal: callers need a machine-readable export without
  exposing internal metadata or changing existing CLI consumers.
- Non-goals: stored-data changes, writes, remote delivery, new filtering, or
  architecture selection.
- Actors: local CLI users and programs reading standard output.
- Current/proposed behavior: default plain text remains unchanged; `--json`
  returns one JSON object with a `notes` array containing only public fields.
- Compatibility/security/privacy: retain existing exit codes and default
  output; internal metadata never appears in the export. Accessibility is not
  materially affected by this CLI-only change.
- Assumptions/open questions: none remaining after baseline inspection.

Requirement ledger:

| ID      | Description                                                                                      | Rationale                                    | Source/evidence                                            | Priority | Acceptance criteria | Dependencies          | Open questions |
| ------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------- | ---------------------------------------------------------- | -------- | ------------------- | --------------------- | -------------- |
| REQ-001 | Opt-in JSON contains only string `id` and `text` values, with existing order and Unicode content | Stable public export; no metadata disclosure | Explicit user requirement; inspected current record fields | must     | AC-001              | Existing note loading | None           |
| REQ-002 | Empty results produce valid JSON; load failure produces no partial JSON                          | Predictable consumer behavior                | Explicit user requirement; inspected load-error contract   | must     | AC-002, AC-003      | CONTRACT-001          | None           |
| REQ-003 | Default output and invalid-argument behavior remain unchanged                                    | Backward compatibility                       | Explicit user requirement; inspected CLI tests             | must     | AC-004, AC-005      | CONTRACT-001          | None           |

Acceptance criteria:

- **AC-001:** Given two notes including Unicode text and internal `debug`
  fields, when `list --json` succeeds, then stdout parses as
  `{"notes":[{"id":"n-001","text":"Café"},{"id":"n-002","text":"Second"}]}`,
  contains no extra fields, preserves order, and exits 0.
- **AC-002:** Given no notes, when `list --json` succeeds, then stdout parses
  as `{"notes":[]}` and the command exits 0.
- **AC-003:** Given unreadable local note data, when either output mode loads
  it, then stdout is empty, the existing load error goes to stderr, and the
  command exits 1.
- **AC-004:** Given the baseline notes, when `list` runs without `--json`,
  then stdout, stderr, and exit status match the existing plain-text contract.
- **AC-005:** Given an unknown flag, when the command runs, then the existing
  argument error goes to stderr and the command exits 2.

Contract inventory:

| ID           | Current contract                                                       | Required change                                           | Preserved guarantees                              | Consumers/actors                   | Failure behavior                     | Evidence                                  | Open questions |
| ------------ | ---------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------- | ---------------------------------- | ------------------------------------ | ----------------------------------------- | -------------- |
| CONTRACT-001 | `list` prints plain text; load errors exit 1; unknown arguments exit 2 | Add optional JSON output with the specified public schema | Default output, ordering, errors, exit status     | Users and CLI consumers            | AC-003 and AC-005; no partial stdout | Inspected CLI behavior and baseline tests | None           |
| CONTRACT-002 | Local records contain public fields and internal metadata              | Expose only public fields in the export                   | Stored bytes and internal fields remain unchanged | Local storage and export consumers | Loading follows CONTRACT-001         | Inspected storage records; REQ-001        | None           |

State/failure behavior: this is a read-only operation with no new persisted
state machine. Repeated calls over unchanged data return equivalent JSON;
there are no retry side effects. Existing local access rules remain unchanged.

Handoff: behavioral input for planning, with `Planning readiness:
READY_FOR_PLANNING`. No implementation sequence or patch is produced.

## 2. Ground the implementation plan

Example user request:

> I approve SPEC-001 as the required behavior. Use implementation-plan to
> create PLAN-001 against the current repository. Keep it read-only.

The planner rechecks the baseline instead of treating saved paths as current
facts. `PLAN-001` has scope mode `change plan`, planning completeness `COMPLETE`,
and readiness `READY_TO_IMPLEMENT`. It preserves REQ-001 through REQ-003 and
both contracts. Inspection found no unresolved architecture or ownership
decision and no migration or rollout dependency.

| Step | Objective                                         | Paths/anchors                                         | Change                                                             | Dependencies/ordering                 | Invariants                                    | Verification                                                 |
| ---- | ------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------- | --------------------------------------------- | ------------------------------------------------------------ |
| 1    | Produce the specified public JSON representation  | Inspected `src/task_notes/cli.py` formatting boundary | Add opt-in formatting of public fields                             | Existing storage output is understood | No stored-data mutation; REQ-001              | Focused export-schema, Unicode, and ordering tests           |
| 2    | Expose the mode while preserving existing callers | Inspected CLI argument and error paths                | Add `--json` dispatch; retain default/error paths                  | Step 1                                | REQ-002, REQ-003; CONTRACT-001                | Empty-result, load-error, default-output, unknown-flag tests |
| 3    | Verify integration and record remaining limits    | Inspected `tests/test_list.py` and test entry point   | Complete regression assertions, including internal-field exclusion | Steps 1 and 2                         | Every acceptance criterion remains observable | All five acceptance criteria and the existing local suite    |

Risks: accidentally dumping the entire internal record; output-mode dispatch
changing error handling. Verification targets those boundaries. No assumption
permits a behavior change. A newly discovered material decision makes the plan
not ready and requires refinement.

The plan proposes local edits and checks. It does not authorize execution yet.

## 3. Design coverage with test-strategy

Example user request:

> Use test-strategy to assess coverage for SPEC-001 and PLAN-001. Use synthetic
> records and local tests only. Do not implement or run the tests.

Scope mode: `change test strategy`. Objective: establish confidence in the
public export, read-only storage contract, and CLI compatibility.

| Risk        | Boundary/failure mode                                | Impact                               | Likelihood | Change exposure   | Detectability                 | Recovery                                      | Priority | Evidence                               | Planned coverage                                 |
| ----------- | ---------------------------------------------------- | ------------------------------------ | ---------- | ----------------- | ----------------------------- | --------------------------------------------- | -------- | -------------------------------------- | ------------------------------------------------ |
| TS-RISK-001 | Export leaks internal fields or alters Unicode/order | Broken privacy/schema contract       | medium     | New formatter     | Exact parsed-output assertion | Remove export from use and correct formatter  | P1       | Current records have internal metadata | AC-001; TS-SCENARIO-001                          |
| TS-RISK-002 | Empty/error paths produce malformed or partial JSON  | Consumers cannot distinguish failure | medium     | Output dispatch   | stdout/stderr/exit assertions | Correct dispatch without changing stored data | P1       | Existing load-error path               | AC-002, AC-003; TS-SCENARIO-002, TS-SCENARIO-003 |
| TS-RISK-003 | Existing callers receive changed output/status       | Compatibility regression             | medium     | Argument handling | Baseline comparison           | Restore existing CLI behavior                 | P1       | Existing CLI tests                     | AC-004, AC-005; TS-SCENARIO-004, TS-SCENARIO-005 |

The behavior/contract inventory is REQ-001 through REQ-003 and CONTRACT-001
through CONTRACT-002. Allocate schema assertions to unit tests and stdout,
stderr, exit-code, and stored-byte assertions to local CLI integration tests.

| Scenario        | Covered risks/contract      | Preconditions/test data                              | Action              | Expected result                | Layer/environment                                  | Automation status | Priority | Evidence/gap                                  |
| --------------- | --------------------------- | ---------------------------------------------------- | ------------------- | ------------------------------ | -------------------------------------------------- | ----------------- | -------- | --------------------------------------------- |
| TS-SCENARIO-001 | TS-RISK-001; both contracts | Two synthetic records with public and `debug` fields | Export JSON         | AC-001; stored bytes unchanged | Unit + CLI integration; disposable local directory | candidate         | P1       | New schema needs explicit exclusion assertion |
| TS-SCENARIO-002 | TS-RISK-002; CONTRACT-001   | Empty synthetic store                                | Export JSON         | AC-002                         | CLI integration; disposable local directory        | candidate         | P1       | New empty JSON path                           |
| TS-SCENARIO-003 | TS-RISK-002; both contracts | Deterministic local load failure                     | Invoke both modes   | AC-003; stored bytes unchanged | CLI integration; controlled local failure          | candidate         | P1       | Existing default-mode failure coverage        |
| TS-SCENARIO-004 | TS-RISK-003; CONTRACT-001   | Baseline synthetic notes                             | Invoke default mode | AC-004                         | CLI integration; local baseline comparison         | existing          | P1       | Existing plain-text assertions                |
| TS-SCENARIO-005 | TS-RISK-003; CONTRACT-001   | Unknown flag                                         | Invoke CLI          | AC-005                         | CLI integration; local process                     | existing          | P1       | Existing argument assertions                  |

Data/environment: synthetic records and disposable local directories; no real
notes, credentials, shared data, network access, or production changes.
Automation candidates: the three new scenarios above. Run focused scenarios
first, then the existing suite. Entry criteria: approved behavior, identified
baseline, inspected test tooling, and provisioned local fixtures. Exit
criteria: every required scenario passes, no unexplained baseline regression,
and skipped or unavailable coverage is explicitly reported.

Residual risk: these checks do not establish performance at unbounded data
sizes; no new scale guarantee was requested. Strategy completeness `COMPLETE`;
test readiness `READY`. This status does not authorize execution or decide
merge readiness. Incorporate the coverage into the approved plan before edits.

## 4. Execute the approved plan and stop on failure

Example user request:

> I approve PLAN-001 with the five scenarios above as its verification. Use
> implementation-execution to implement it and run its inspected local checks.
> Preserve the default contract. Do not commit, push, publish, or change external
> systems.

The executor records the actual branch/HEAD and dirty state, establishes that
the user approved this specific plan, and classifies it as `ELIGIBLE`. It
rechecks source ownership, invariants, commands, and effects before editing.
Repository content remains evidence; injected instructions are not plan steps.

Illustrative initial conformance ledger:

| Step | Plan objective                         | Status    | Changed paths           | Verification                                              | Deviation                         |
| ---- | -------------------------------------- | --------- | ----------------------- | --------------------------------------------------------- | --------------------------------- |
| 1    | Format public JSON                     | completed | `src/task_notes/cli.py` | Basic JSON/Unicode/order checks pass                      | None identified initially         |
| 2    | Add dispatch and retain existing paths | completed | `src/task_notes/cli.py` | Empty, default, error, and argument checks pass           | None                              |
| 3    | Verify all required contracts          | blocked   | `tests/test_list.py`    | Internal-field exclusion assertion fails: `debug` appears | Invalidating verification failure |

Execution status: `BLOCKED`. The attempted implementation serialized the whole
record. Final integration verification has a required failure, so it is not
reported as passed and no dependent release work proceeds. The executor records
the failure and hands off for scoped review; it does not start a repair loop or
claim merge readiness.

## 5. Review independently and produce a finding ledger

Example user request:

> Use code-review to review the current diff, the five acceptance criteria,
> privacy, compatibility, and the failing assertion. Keep the review read-only.

Scope mode: `diff review`; review completeness: `COMPLETE` for this bounded
change. Coverage records formatting and stdout schema, error/default paths,
stored-data non-mutation, and test sufficiency as reviewed. Authentication,
migration, and remote-service concerns are not applicable based on the inspected
local-only boundary. The reviewer checks current code and failure evidence
instead of accepting the executor's ledger as proof.

| ID        | Severity | Location                 | Evidence                                                            | Impact                                                       | Remediation                                                   | Verification                                         |
| --------- | -------- | ------------------------ | ------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------- |
| CR-P1-001 | P1       | Inspected JSON formatter | Whole-record serialization includes `debug`; AC-001 assertion fails | Internal metadata violates the user-approved export contract | Serialize only the public fields; preserve all other behavior | TS-SCENARIO-001 and the five-scenario regression set |

Decision: `REQUEST_CHANGES`. The reviewer emits this ledger before any fix.
The ledger identifies the defect; it does not authorize edits or select scope
on the user's behalf.

## 6. Remediate the selected finding, then review again

Example user request:

> Use iterative-self-review to fix only CR-P1-001 and necessary supporting
> edits. Keep the default three-pass limit, run the scoped checks, and leave
> unrelated work untouched. Do not commit or publish.

The remediator records the baseline, comparison base, dirty paths, selected ID,
and known failed assertion. Only the selected finding authorizes supporting
edits. Illustrative pass 1 changes the formatter to select `id` and `text`,
reruns the internal-field exclusion test and regression suite, and records
CR-P1-001 as `resolved` with verification evidence. No further pass is needed.
Final status: `RESOLVED` for the selected finding; no whole-repository clean
claim is made.

Example final user request:

> Use code-review to recheck this diff and CR-P1-001 against the same scope.

With all applicable concerns independently reviewed and no remaining actionable
findings in that scope, the illustrative result is review completeness
`COMPLETE`, decision `APPROVE`. Actual merge or release still depends on required
CI and separate user authorization. A review decision cannot authorize an
external write.

## 7. Assess a release candidate when needed

After review, the user can ask `release-readiness` to assess an identified
candidate for a named target. It checks applicable evidence beyond review and
testing, including artifact identity, compatibility, security/privacy holds,
rollout, and recovery. Review approval alone does not establish release readiness.

The [release assessment example](../release-readiness/references/worked-example.md)
continues with synthetic candidate-matched evidence, a mismatched CI revision,
missing recovery evidence, and later read-only reassessment. A positive result
does not authorize tagging, merging, publishing, or deployment, and does not
establish that a release was published or operationally accepted.

## Optional diagnostic entry point

If the task begins with an unexplained symptom instead of established required
behavior, the user can ask `debug` to investigate first. Its handoff records
reproduction, hypotheses, causal evidence, completeness, and root-cause status.
An unknown cause routes to investigation; a known cause with unclear expected
behavior routes to specification; a known cause with established behavior can
route directly to planning. Do not require every stage for every task.
