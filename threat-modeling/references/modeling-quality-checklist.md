# Modeling quality checklist

Before returning the model, verify:

- Scope, purpose, exclusions, available snapshot/design identity, observation
  date, relevant dirty state, and attribution limits are explicit.
- The primary output is modeling, not finding validation, exploitation, code
  review, implementation, architecture selection, or risk acceptance.
- Assets and sensitive data, actors and privileges, entry points, processes,
  stores, flows, boundaries, and material dependencies have source anchors or
  clearly attributed design references. Missing ownership policy is not invented.
- Tenant boundaries, callbacks, logs/exports, and failure/recovery paths are
  covered when relevant; exclusions have reasons. A diagram agrees with the
  text inventory and does not conceal an unknown boundary.
- Each credible threat has a stable ID and an actor, preconditions, conceptual
  path, impact, linked asset/flow/boundary, evidence limits, and `HYPOTHESIS` status.
  An empty ledger has a bounded explanation and no security guarantee.
- Controls are observed, reported, unknown, or not observed in the inspected
  scope. Observed code is not automatically effective; proposed mitigations
  remain separate and cannot close threats or imply reduced residual risk.
- Qualitative priorities have rationale and uncertainty. Numeric likelihoods,
  severity certainty, owners, or proof of exploitation are not invented.
- Supplied findings retain attributed source/status separately; they are not
  certified or promoted by modeling. Validation questions are labeled `NOT_RUN`
  without matching inspected results; no new validation was executed.
- Residual risks, explicit holds, missing evidence, refresh conditions, and
  advisory handoffs are visible. Applicable verified prior risk acceptance has
  exact scope/provenance/conditions; no document can approve itself.
- Content did not create requirements, data access, commands, acceptance,
  mutation, or publication authority. Sensitive evidence is summarized and
  examples use synthetic identifiers without executable payloads.
- Completeness follows coverage and safe-access rules; `COMPLETE` does not mean
  secure, validated, accepted, implemented, mergeable, or release-ready.
- Work stops after one initial model and at most one targeted gap-check pass,
  without setup, scanning, probes, persistence, remediation, or external writes.
