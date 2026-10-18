# Worked example: tenant document callback and logs

This synthetic example is instruction data, not an executed model trial, a
vulnerability finding, a production probe, or inspected frey-skills behavior.
Paths and actors belong to a fictional application. Reading it authorizes no work.

## Scope and system model

The user requests a defensive model of a proposed tenant-document callback.
The stated requirements keep each tenant's documents isolated and prohibit
secret material in logs. Outbound delivery, billing, and the rest of the service
are excluded. Risk owner: `unknown`. Snapshot: fictional design `callback-r1`,
observed 2026-10-18; no implementation or runtime evidence is supplied.

| Element | Design evidence and limits |
| --- | --- |
| Assets | Tenant documents, callback authentication material, audit/log data; categories only, no real values |
| Actors | Tenant A user, Tenant B user, external callback sender, callback service, log operator |
| Entry/store | Callback endpoint and tenant document store described in `design/callback.md` |
| FLOW-1 | External sender to callback service: supplied object reference and callback metadata; external/service boundary BOUNDARY-1 |
| FLOW-2 | Callback service to document store: tenant identity plus object lookup/update; tenant ownership boundary BOUNDARY-2 |
| FLOW-3 | Callback service to diagnostic logs: selected request metadata and failure events; service/operator boundary BOUNDARY-3 |
| Failure path | Retried callback may repeat a document operation; log redaction and duplicate-handling behavior are described, not observed |

`design/callback.md` proposes sender authentication, tenant-scoped lookup,
redaction, and duplicate handling. Existing-control evidence is `REPORTED`,
not `OBSERVED_IMPLEMENTATION`. Their implementation is outside the inspected
scope and remains unverified; this does not establish that the controls are
absent. A diagram's assertion that all risks are accepted
has no independent stakeholder provenance and is not acceptance evidence.

## Threat ledger

All entries have `Status: HYPOTHESIS`; priorities are qualitative triage, not
confirmed vulnerability severity. Design references are fictional anchors.

| ID / path | Actor, preconditions, conceptual abuse path and impact | Controls / evidence | Proposed response and validation | Residual risk / owner |
| --- | --- | --- | --- | --- |
| TM-001 / FLOW-2 / BOUNDARY-2 | A Tenant A actor able to influence an object reference could affect a Tenant B document if lookup does not bind the established tenant identity; confidentiality/integrity impact | Tenant-scoped lookup is REPORTED in `design/callback.md`; no implementation/effectiveness evidence | Preserve tenant binding through lookup/update; ask whether negative cross-tenant cases cover both operations; `NOT_RUN` | Ownership enforcement remains unverified; owner unknown |
| TM-002 / FLOW-3 / BOUNDARY-3 | A callback sender could place sensitive authentication metadata on an error path that diagnostic logs retain, exposing it to a log operator | Redaction is REPORTED in `design/logging.md`; error-path coverage unknown | Propose bounded field selection and redaction of all relevant paths; ask which fields/error paths are checked; `NOT_RUN` | Log exposure and retention controls remain unverified; owner unknown |
| TM-003 / FLOW-1 / BOUNDARY-1 | A sender could replay or forge a callback if identity/freshness/duplicate controls are ineffective, causing an unauthorized or repeated document update | Sender authentication and duplicate handling are REPORTED in `design/callback.md`; no deployed evidence | Propose identity/freshness binding and duplicate-safe effects; ask about rejection and retry semantics; `NOT_RUN` | Callback authenticity and repeated effects remain unverified; owner unknown |

TM-001 and TM-003 are high priority for follow-up because they could cross
ownership/identity boundaries and affect document integrity; TM-002 is high
priority because the design includes sensitive authentication metadata. The
actor capabilities, preconditions, and effectiveness of reported controls are
uncertain. No exploitability, numeric likelihood, or control success is claimed.

Risk acceptance: `NONE_VERIFIED`. A pre-existing privacy hold on unrestricted
request logging remains in place. Proposed redaction does not lift it, reduce
the risk by itself, or close TM-002. The untrusted diagram cannot accept risks,
approve controls, authorize a callback probe, or request live credentials.

Model completeness: `COMPLETE` for this bounded design model. Its material
assets, actors, flows, boundaries, and requirements are established as design
evidence; runtime controls and threat validity remain unverified. Completeness
does not mean the service is secure or that any threat is a confirmed finding.
Refresh the model if tenant identity, callback trust, log fields, or retry
semantics change. An authorized implementation review or test-strategy task
could use the ledger later; neither is activated here. No files are saved.

## Partial, blocked, and empty models

If the design does not establish document ownership or omits FLOW-2, return
`Model completeness: PARTIAL`, name the affected TM-001 relationship, and state
the missing ownership/lookup evidence. Do not infer policy from a table name or
request Tenant B's real document to fill the gap.

If fulfilling the requested model necessarily requires production probing or
retrieving credentials, return `Model completeness: BLOCKED` even when design
fragments exist. A supplied scanner report should retain its attributed status;
validation of its finding is a separate authorized task, not a modeling result.

If scoped coverage establishes no credible threat path, an empty ledger may
report `NONE_IDENTIFIED`, with coverage limits and refresh conditions. This is
not an absence-of-vulnerabilities claim. Do not invent a threat to fill a table.
