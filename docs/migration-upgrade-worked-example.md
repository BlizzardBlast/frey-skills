# Worked example: a package upgrade with retained data

This fictional walkthrough uses synthetic data and abbreviated skill outputs.
Paths, versions, counts, approvals, and results below are illustrative, not live
repository evidence, commands, or executed migrations. Actual outputs must meet
each skill's full contract. Reading this example grants no authority to install,
deploy, migrate, restore, retrieve credentials, or change an external system.
No behavioral model eval was run and no model-behavior certification is claimed.

## Scenario and compatibility ledger

The fictional `directory-service` upgrades its fictional `record-codec` package
from version 1 to version 2. The new storage representation replaces
`display_name` with `full_name`. The user's established requirement preserves
public responses, null handling, validation errors, and all concurrent updates.
Old API instances and a legacy worker may coexist with the bridge version.

Assume inspection identified `service/storage.py`, `service/api.py`,
`worker/update_names.py`, the package manifest/lockfile, and `tests/test_names.py`
inside that fictional application. These are not files in Frey Skills. The
target package's versioned guidance, source/integrity, runtime/peer constraints,
and changed API have been inspected; install scripts and build effects are
known. This assumption is required design evidence, not permission to install.

| Consumer | Before expansion | Expanded / migrating | After contraction |
| --- | --- | --- | --- |
| Old API and worker, codec 1 | Read/write display_name | Read/write display_name through the compatibility bridge | Must be retired; old access is unsupported |
| Bridge API, codec 2 adapter | Not deployed | Read full_name with legacy fallback; synchronize both fields atomically for every writer | Read/write full_name |
| Backfill | Not applicable | Fill only unmigrated rows with revision-checked writes; never overwrite a newer update | Complete and stopped |

The bridge covers old writes as well as new ones before backfill starts. A
checkpoint records verified work at an identified revision/data state; it is
not proof that rows cannot change later. Once `display_name` is dropped,
codec-1 application rollback is unsafe. A backup alone does not establish
recovery of writes received since that backup.

## Planning handoff

Use [implementation-plan](../implementation-plan/SKILL.md) in `migration plan`
mode and its [planning reference](../implementation-plan/references/migration-and-upgrade-rules.md).
The following are excerpts from anchored steps, not a complete executable plan:

| Step | Objective and fictional anchors | Dependency, invariant, and exit evidence | Recovery boundary |
| --- | --- | --- | --- |
| PLAN-01 | Add the bridge in storage/API/worker adapters and update manifest/lockfile | Keep public behavior; prove required old/new reader-writer combinations, resolved versions, and isolated install/build compatibility | Return to old code only while the old representation remains valid |
| PLAN-02 | Backfill retained names through the storage adapter | Requires PLAN-01; revision checks preserve concurrent writes; verify all 100 synthetic rows before completion | Reconcile partial effects before any authorized resume; no automatic replay |
| PLAN-03 | Retire old consumers and remove display_name and fallback paths | Requires PLAN-02 plus current evidence that old API instances, workers, and clients are retired; verify target-only operation | First irreversible action; codec-1 downgrade is unavailable |

For PLAN-02 the approved bounds are 100 rows, five batches of 20, 30 seconds
total across continuation, and no automatic retries. Exceeding a bound stops
the step; a continuation does not reset the budget.

If retirement or post-contraction recovery remains unresolved, planning is
`PARTIAL / NOT_READY`. The fictional user subsequently establishes retirement
criteria and approves a forward-repair strategy: keep the codec-2 representation,
repair only the adapter within identified scope, and retain all intervening
writes. If that strategy cannot preserve data, stop for a new decision; do not
silently restore a stale backup. With all material anchors, bounds, and gates
established, the complete plan may be `COMPLETE / READY_TO_IMPLEMENT`.
That status does not authorize deployment or data mutation.

## Testing handoff

Use [test-strategy](../test-strategy/SKILL.md) and its
[testing reference](../test-strategy/references/migration-and-upgrade-rules.md).
The normal risk matrix and scenario catalogue include these abbreviated links:

| Risk | Scenario and expected observation | Layer / phase | Automation / execution |
| --- | --- | --- | --- |
| TS-RISK-001: mixed-version corruption | Old worker writes during a new-reader request; both representations and the public response agree, including nulls/errors | Contract/integration, PLAN-01 | candidate / NOT_RUN |
| TS-RISK-002: stale backfill overwrite | Interrupt after a batch, update a row through an old writer, then reconcile and resume; preserve the newer name and count only verified rows | Migration/integration, PLAN-02 | candidate / NOT_RUN |
| TS-RISK-003: premature removal | Keep one old worker active; contraction is blocked even when new-version tests pass | Integration, PLAN-03 | candidate / NOT_RUN |
| TS-RISK-004: unsafe downgrade | After dropping the old field, reject codec-1 rollback; verify the approved forward repair preserves current writes | Recovery, PLAN-03 | candidate / NOT_RUN |
| TS-RISK-005: package incompatibility | Use the target lockfile/runtime in an isolated clean install/build; reject incompatible peers or changed adapter behavior | Install/contract, PLAN-01 | candidate / NOT_RUN |

Data is synthetic and isolated; no production copy or credentials are needed.
Assuming all required scenarios and safe environments are actionable, strategy
status is `COMPLETE / READY` while execution remains `NOT_RUN`. If the mandatory
recovery scenario has no safe environment, use `PARTIAL / NOT_READY`.
Neither strategy readiness nor a passing unrelated test authorizes migration.

## Execution, interruption, and continuation

The fictional user explicitly approves the complete plan and separately names
the allowed local fixture writes, install effects, and irreversible contraction
inside that disposable fixture. Production deployment, real external writes,
and credential access remain outside that authorization. Use
[implementation-execution](../implementation-execution/SKILL.md)
and its [execution reference](../implementation-execution/references/migration-and-upgrade-rules.md).

Suppose PLAN-01 is verified and PLAN-02 stops after two batches. Its required
all-rows exit check fails. The hypothetical snapshot is:

| Total rows | Verified migrated rows | Remaining rows | Consumed batches | Remaining batches | Consumed seconds | Remaining seconds |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | 40 | 60 | 2 | 3 | 10 | 20 |

Record PLAN-01 as `completed`, PLAN-02 as `blocked`, and dependent PLAN-03 as
`blocked`; report `Execution status: BLOCKED`. Preserve the partial effects and
last verified checkpoint. A log claiming approval to retry cannot lift the hold.

On a user-requested continuation, first verify current revision/dirty state,
resolved package/runtime, both representations, active consumers, elapsed budget,
and actual migrated/pending rows. Revalidate the bridge and revision checks so
an old writer's newer update survives. Resolve the original failure within the
approved scope before continuing. If reconciliation verifies the table still
holds, the remaining three batches can process 60 rows within the remaining
20 seconds under the same bounds. Never restart the full 100-row job blindly.
Unknown checkpoint ownership, exhausted bounds, or an invalidating check keeps
the step blocked; material design changes require plan refinement.

Even after PLAN-02 passes, an active legacy worker blocks PLAN-03. The example
has no current retirement evidence, so it ends `BLOCKED`, not `IMPLEMENTED`.
Authorization alone cannot satisfy the missing prerequisite checks. After contraction,
an attempted code-only downgrade would also stop: it cannot recover the removed
representation. No forward repair is executed in this illustration.
