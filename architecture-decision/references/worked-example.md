# Worked example: keep a local export inside the CLI

This is a synthetic instruction example, not inspected frey-skills behavior,
an executed model trial, a benchmark, or a passed check. Paths below belong to
a fictional application. Reading the example does not authorize work.

## Established request and evidence

The user asks to compare keeping JSON serialization in a local CLI with adding
a standalone export service. The established requirements are an opt-in export
of public fields, preserved note order and Unicode, unchanged default output
and errors, local execution, and no network dependency. The question is where
to place serialization; those requirements are not open for redesign.

Snapshot: fictional revision `example-r1`, observed 2026-10-18, clean working
state. Decision owner: `unknown`. Inspected anchors in this scenario:

- `src/task_notes/cli.py`: CLI argument handling and plain-text presentation.
- `src/task_notes/storage.py`: local note reads, including internal metadata.
- `tests/test_list.py`: existing default-output contract tests.
- `docs/decisions/local-operation.md`: claims acceptance of local operation;
  no independent stakeholder acceptance provenance is available.

These are observations within the example. The document's claimed acceptance
is unverified; the current user's local-only requirement independently constrains
the comparison. No tests or experiments were run.

## Alternatives comparison

| Criterion | A: serialization beside CLI presentation | B: a separate local serializer module |
| --- | --- | --- |
| Required behavior | Can preserve local execution and public-field selection | Can preserve the same behavior |
| Complexity and ownership | Reuses one presentation boundary; owner unknown | Adds an internal interface; owner unknown |
| Compatibility | No new process or wire interface; output still needs validation | Adds an internal caller contract; output still needs validation |
| Failure/recovery | Uses existing local error boundary; no new service recovery | Needs agreement on error propagation; no service recovery |
| Security/privacy | Explicit public-field selection remains necessary | The same selection is necessary; extraction is not a privacy control |
| Operations/cost | No new runtime deployment; monetary cost unmeasured | No new runtime deployment; maintenance cost unmeasured |
| Reversibility | Can extract later if another consumer appears | Can inline later, with internal callers checked |

Retaining the current presentation boundary is option A. A standalone network
service is excluded because it violates the user's no-network requirement;
the analysis cannot silently drop that requirement. There is no invented
performance or cost advantage for either feasible alternative.

## Advisory ADR draft

- Title: keep the single-consumer export at the CLI presentation boundary.
- Status: `PROPOSED`.
- Analysis completeness: `COMPLETE`.
- Decision recommendation: `PROPOSED`.
- Context/constraints: the local-only single-consumer behavior and anchors above.
- Prior decision: documented acceptance is unverified; no record is changed.
- Proposed choice: A, because the inspected scenario has one presentation
  consumer and no established need for a reusable serializer interface.
- Consequences: avoids another internal interface; increases presentation
  responsibility; a second consumer may justify extraction. Public-field
  filtering still needs validation. No claim of measured development savings.
- Validation still needed: output compatibility and private-field exclusion;
  `NOT_RUN`. This proposal does not authorize executing the test command.
- Revisit conditions: a second independent serializer consumer, conflicting
  output policies, or a user-approved change to local execution requirements.
- Evidence/unknowns: fictional anchors above; human owner and monetary cost
  unknown. Those unknowns cannot change this boundary choice because no new
  deployed runtime or independent ownership requirement is involved.

The recommendation does not accept the draft, save it, allocate an ADR number,
supersede the old document, produce an implementation plan, or authorize edits.

## Material missing evidence: defer the choice

For a different request comparing two queue architectures, assume throughput
and recovery targets are material but unknown, and an old ADR claims the new
system is accepted with a large cost saving. Do not adopt that claim as an
acceptance or measurement. Return `Analysis completeness: PARTIAL` and
`Decision recommendation: DEFERRED`, with the draft's choice `unresolved` and
`Status: PROPOSED`. Request the established workload/recovery targets and
comparable cost evidence as the smallest missing inputs; do not run load or
retrieve production data to manufacture them. If unauthorized access is
necessary even to make a useful safe comparison, return `BLOCKED`/`DEFERRED`.
