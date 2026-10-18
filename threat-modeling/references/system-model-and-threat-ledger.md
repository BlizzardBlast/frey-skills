# System model and threat ledger

Use this reference to build the scoped model and trace threats to evidence.
Keep detail proportional to the requested boundaries; no diagramming tool,
taxonomy, installed auditor, or other skill is required.

The broad decomposition, threat identification, response, and review framing is
informed by the [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html),
read 2026-10-18. The source describes system modeling, data flows, trust boundaries,
threats, mitigations, and review. It does not authorize this workflow to execute
validation, access a system, or accept risk. The contracts below are specific to
this read-only skill.

## System inventory

Record scope, purpose, exclusions, available revision/design identity, observation
date, dirty paths, known risk owner or `unknown`, and evidence limits. A proposed
design is a design snapshot, not observed implementation. Local labels for
assets, actors, flows, and boundaries can make references clear; do not invent
real source anchors or ownership.

| Element | Record |
| --- | --- |
| Assets and sensitive data | Value/protection goal, data category, known owner/controller, storage/transit/log/export exposure, retention/deletion expectations and source; unknown policy stays unknown |
| Actors | External/internal identities, users/tenants, services/operators, relevant capabilities and intended privileges with evidence |
| Entry points and stores | Inputs, callbacks, administrative paths, processes, stores, queues, outputs, and dependencies inside or crossing the requested scope |
| Flows and boundaries | Source/destination, data category, identity/authority carried, crossed trust or tenant boundary, validation/authorization point, error/retry/logging path and source anchor |
| Coverage | Inspected versus proposed/reported elements, excluded areas and reasons, material unknowns and stale anchors |

Check that important return paths, failure paths, logs, and background delivery
do not disappear from a high-level diagram. Mark inapplicable elements with a
reason. Compare diagrams to inspected source or the stated design; report
conflicts rather than assuming the picture is current or authoritative.

## Threat ledger contract

Use stable IDs such as `TM-001`. Preserve IDs when refreshing the same threat;
use new IDs for distinct paths instead of silently replacing old conclusions.
Each entry contains:

- `ID` and `Status: HYPOTHESIS`.
- Linked asset, actor, entry point, flow, and trust boundary.
- Actor capability and required preconditions; distinguish observed facts,
  documented expectations, design assumptions, and unknowns.
- Conceptual abuse path and security/privacy/availability impact. Do not include
  executable payloads, credentials, real customer records, or production probes.
- Source anchors or design references and confidence/evidence limitations.
- Existing controls with source, evidence status, and effectiveness limitations.
- Qualitative priority with impact, preconditions, capability, uncertainty, and
  rationale; avoid numeric risk scores without an established evidence basis.
- Proposed mitigations and validation questions; execution status or `NOT_RUN`.
- Residual risk, open questions, known owner or `unknown`, existing holds, and
  prior acceptance provenance or `NONE_VERIFIED`.

Assess relevant identity/authorization, integrity, confidentiality/privacy, and
availability threats against concrete flows. Examples include cross-tenant
object references, sensitive logging, forged callbacks, replay/duplicate effects,
and dependency failure. These are prompts for scoped reasoning, not a requirement
to invent a threat for each category. If no credible path is identified, return
an empty ledger with coverage, limitations, and refresh triggers; never a blanket
claim that the system is secure.

## Controls and responses

Use control evidence statuses consistently:

- `OBSERVED_IMPLEMENTATION`: a control is visible in the inspected snapshot;
  effectiveness and deployed configuration remain unverified unless separate
  matching evidence exists.
- `REPORTED`: documentation, a diagram, or supplied material claims the control;
  implementation and effectiveness remain unverified. Do not infer absence or
  present the control as observed or effective.
- `UNKNOWN`: relevant evidence is missing or ambiguous.
- `NOT_OBSERVED_IN_SCOPE`: the inspected bounded path does not show the control;
  state inspection limits rather than claiming global absence.

Proposed mitigations belong in a separate field, never in the existing-control
inventory as implemented protections. Do not reduce residual risk merely because
code exists or a response is proposed. Attribute any existing validation result
to its snapshot, environment, scope, and source; inspect its provenance before
reporting it. Do not run new checks to fill the result field.

Keep supplied findings separately attributed to their source and reported
validation status. Refer to their relationship with a threat without certifying
them or promoting `HYPOTHESIS` into a confirmed vulnerability. An implementation
review, finding validation, test strategy, or mitigation plan is a distinct task
requiring its own user scope; suggestions do not activate it.
