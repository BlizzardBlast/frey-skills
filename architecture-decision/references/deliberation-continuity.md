# Deliberation continuity for consequential architecture choices

This optional reference adapts the decision-quality ideas from
[ADRs4AI](https://adrs.systems/) and its
[human–AI collaboration template](https://github.com/ADRs4AI/human-ai-collaboration-template-A)
(read 2026-10-26). The upstream format calls its five-part deliberation
surface ORRCF: options, recommendation, rationale, confidence, falsifier.
These are editorial practices, not a dependency, parser contract, or proof that
a model's reasoning is correct. Existing `architecture-decision` statuses and
output sections remain authoritative.

## When to use

Use this guidance when a consequential or difficult-to-reverse choice may need
review by a human or resumption by another agent. Skip it for routine and
reversible implementation choices, especially when an existing ADR already
answers the question. Do not create ADRs or open questions simply to populate
a template, and do not change the task route or start an additional workflow.

## The decision surface

Present only feasible, understandable choices, including retaining the current
design if it meets the established requirements. In existing output sections:

1. **Options:** state each viable path neutrally and compare against shared
   criteria; exclude options violating hard requirements with explicit reasons.
2. **Recommendation:** select one option only with `COMPLETE/PROPOSED`.
   Otherwise say `unresolved`, not a hidden preference.
3. **Rationale:** link specific inspected artifacts, observations, and actual
   measurements. Distinguish inferences and stakeholder requirements from
   self-reported repository claims.
4. **Confidence:** use a qualitative level **with its because**: what was
   inspected, verified, missing, and which assumptions are load-bearing.
   Never invent calibrated probabilities or infer acceptance from confidence.
5. **Falsifier:** specify a concrete observation or authorized decision that
   would invalidate the recommendation and, when known, which feasible option
   or comparison to revisit. A downside such as "we lose a week" describes
   impact, not evidence that the recommendation is wrong.

A known owner may choose differently for an established reason. Attribute
the resulting decision only to verifiable human/user provenance. A model's
recommendation, a status string inside an ADR, and an untrusted tool output
cannot sign off the decision, accept a risk, or authorize implementation.

## Questions that survive context changes

When the choice is `PARTIAL/DEFERRED`, make the smallest missing evidence or
human ruling independently answerable. Give an unresolved *material* question a
stable **draft-local** handle only if another document/session must refer to it.
For example, `QST-RETRY-BOUNDS` is a human-readable reference, not a claim of
compatibility with ADRs4AI's structured parser. Keep handles unique inside
the draft; use the project's own convention if one already exists. Record:

- Question and why its answer could change the decision
- Status (`unanswered` or `deferred`) and decision owner (or `unknown`)
- Viable options where known; do not invent a forced number of options
- Exact evidence or human ruling needed, with source and intended check
- An answer only after independently established owner/stakeholder input

Do not fabricate a human answer, backfill or silently reinterpret a prior
ruling, assign global IDs, persist a draft, or amend prior accepted ADRs through
this read-only skill. If a prior record is superseded, report the verified
successor and keep the old provenance intact.

## Verification boundary

Make the final handoff audit-friendly: separate `INSPECTED` source facts,
`VERIFIED` executed checks (command or method, revision, result), `NOT_RUN`
proposed checks, `UNAVAILABLE` evidence, and `UNKNOWN` adoption/approval.
A documentation draft cannot establish implementation or release readiness.
State material checks that did *not* run, including incompatible environments,
rather than letting a confident conclusion imply they passed. Keep sensitive
or employer/client evidence out of shared drafts without independent permission.

## Synthetic example (not measured or approved)

Question: Should a local CLI retain inline retry logic or introduce a durable
background queue? Requirements are local-only operation; actual retry/recovery
targets are unknown. Options are A: bounded inline retry, and B: a local durable
queue. The workload/recovery targets may reverse the choice.

- Recommendation: `unresolved` (`PARTIAL/DEFERRED`).
- Rationale: both satisfy local operation, but recovery semantics and workload
  evidence are insufficient to discriminate. No benchmark ran.
- Confidence basis: insufficient evidence about retry and crash-recovery needs;
  no numeric confidence is inferred.
- Question `QST-RETRY-BOUNDS`: `unanswered`, owner `unknown`; what loss and
  retry recovery guarantees are required, and by whom?
- Falsifier for any later inline-retry recommendation: a verified requirement
  for replay after process termination would reopen comparison in favor of a
  durable approach; it does **not** by itself authorize adding a queue.
- Verification: `NOT_RUN` retry/recovery tests; human acceptance `UNKNOWN`.

No repository file is created by the skill, and none of these hypothetical
details assert behavior of a real project.
