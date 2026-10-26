# Research decision: ADRs4AI deliberation continuity (2026-10-26)

## Sources and level of evidence

- [ADRs4AI methodology](https://adrs.systems/): project description, examples,
  optional editor/client/MCP ecosystem, and rationale for durable deliberation.
- [ADRs4AI human–AI collaboration template](https://github.com/ADRs4AI/human-ai-collaboration-template-A):
  question/answer records and an ORRCF (options, recommendation, rationale,
  confidence, falsifier) format.
- [Martin Fowler on Architecture Decision Records](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
  and [AWS ADR process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html):
  short, repository-local decision history and superseding rather than
  rewriting accepted decisions.

These are methodology and practitioner sources, not comparative experiments
showing improved agent correctness, reduced hallucinations, or ROI.

## Fit to the existing repos

| Candidate concept | Already present | Smallest useful delta |
| --- | --- | --- |
| Options and discriminating rationale | `architecture-decision` compares feasible alternatives with evidence | Explain the recommendation in an auditable five-part human handoff |
| Revisit conditions | Proposed ADR already documents triggers | Distinguish observable falsifiers from impact/cost; name the alternative to revisit where possible |
| Confidence | `agent-brain` lessons label confidence and separate claims from independent proof | Require a *because*-clause for consequential architecture recommendations; no fake numeric calibration |
| Open questions | `PARTIAL/DEFERRED` already identifies smallest missing evidence | Add optional draft-local stable references, state, and owner for material follow-up |
| Decision provenance | Existing ADR status and review/owner boundary is explicit | Preserve claimed versus verified rulings and forbid fabricated answers |
| Verification provenance | Existing `NOT_RUN` and status gates | Make negative-space verification explicitly visible in the decision handoff |
| Persistent learning | `agent-brain` already has evidence, applicability, conflicts and supersession | No second memory schema or automatically promoted lesson |

## Adopted scope

Extend the *existing* read-only `architecture-decision` skill, its template,
checklist, and deterministic text-contract tests. The optional guidance is
loaded only for consequential decisions. Leave `implementation-plan` and
`implementation-execution` PR #49 additions intact, without changing their
status or authority contracts. Avoid a parallel decision skill or a new
`agent-brain` PR: the candidate capabilities are already represented in its
lesson template, and cross-repository duplication would add unmeasured cost.

## Rejected and deferred adaptations

- No upstream ADR parser, MCP server, phone client, editor extension, plugin,
  crew inbox, daemon, hosted memory, or new package dependency.
- No copying the upstream ADR template or adopting a new ADR status vocabulary;
  reuse local conventions and existing `COMPLETE/PARTIAL/BLOCKED` plus
  `PROPOSED/DEFERRED` rules.
- No required numeric confidence score or implicit human approval.
- No archiving whole chat transcripts, private source material, or proprietary
  reasoning into a shared vault; consent and source rights remain independent.
- No automated ADR writing, prior-ADR supersession, skill promotion, test run,
  approval, push, or merge from the read-only skill.

## Future checks, not claims of observed improvement

A later **authorized** evaluation could compare synthetic consequential,
trivial, and unresolved decisions. Check that the output (1) keeps the
five-part evidence chain when useful, (2) avoids unnecessary questions for
routine changes, (3) leaves deferred choices unresolved, (4) detects false
human acceptance and non-falsifiers, and (5) separates executed from unrun
verification. Deterministic contract tests here verify instruction presence
and resource wiring only; they cannot certify actual model behavior.
