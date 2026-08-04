# Plan Conformance and Deviation Rules

## Step states

- `not started`: no objective-relevant implementation exists.
- `in progress`: part of the objective exists but required work or verification remains.
- `completed`: the objective is satisfied and required verification supports it.
- `blocked`: safe execution cannot continue.
- `skipped by plan`: the approved plan explicitly excludes or conditions out the step.
- `deferred by user`: the user explicitly postpones the step.

## Ledger template

| Step | Plan objective | Status | Changed paths | Verification | Deviation |
| ---- | -------------- | ------ | ------------- | ------------ | --------- |
| PLAN-01 | Add behavior | completed | `src/file` | focused test passed | none |

Keep original plan numbering when possible. Do not hide pre-existing edits inside `Changed paths`; label them as baseline state.

## Minor deviations

Proceed only when repository evidence preserves the plan objective and invariants: moved canonical files, renamed symbols with unchanged contracts, equivalent verification commands, different existing test locations, or local structural details with unchanged behavior.

## Material deviations

Stop when execution requires public or serialized contract changes; a new dependency, service, package, architecture, or trust boundary; unsafe migration or rollout ordering; invalid security, privacy, authorization, data, or compatibility assumptions; unrelated cleanup; unresolved canonical ownership; unavailable required verification without equivalent evidence; unauthorized irreversible or external action; or redesign of a supposedly completed continuation step.

Material deviation output:

```text
Execution status: BLOCKED
Recommended next action: refine the plan with implementation-plan
```
