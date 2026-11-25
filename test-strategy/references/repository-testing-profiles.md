# Repository Testing Profiles

Use these profiles to decide which risks, layers, data, environments, and residual concerns materially apply. Include only relevant concerns and mark missing evidence explicitly.

## Frontend and accessibility

Inspect component ownership, state/query/route contracts, forms, loading/error/empty states, hydration, browser APIs, and generated routes.

Consider:

- semantic controls, keyboard flow, focus, labels, ARIA, and screen-reader-visible feedback;
- client/server validation consistency;
- optimistic updates, retry, stale cache, and cancellation behavior;
- responsive and browser-specific boundaries;
- component or integration tests for observable behavior rather than implementation detail.

## Backend and APIs

Inspect request/response validation, authn/authz, tenancy, idempotency, pagination, error semantics, retries, timeouts, cancellation, and downstream dependencies.

Consider contract tests, service integration tests, permission matrices, partial failure, duplicate requests, rate limits, and observability without secret or PII leakage.

## Databases and migrations

Inspect schemas, constraints, defaults, indexes, backfills, retained data, transactions, rollout ordering, and old/new application coexistence.

Consider representative historical data, null and enum transitions, idempotent and resumable backfills, lock behavior, rollback limits, compatibility matrices, and post-migration data verification.

## Monorepos and toolchains

Inspect workspace boundaries, package exports, generated artifacts, path aliases, task graphs, cache inputs/outputs, lockfiles, supported runtimes, and publication contracts.

Consider focused package tests, cross-package contract tests, build reproducibility, code generation parity, cache invalidation, and installation from a clean environment.

## CI and release pipelines

Inspect required checks, artifact identity, environment scoping, permissions, secrets, reports, feature flags, deployment order, smoke checks, and rollback paths.

Consider failure-path tests for skipped or flaky checks, artifact promotion, environment-specific configuration, canary verification, and production-safe observability checks.

## Dependencies and framework upgrades

Inspect peer and runtime compatibility, removed or deprecated APIs, configuration changes, native bindings, install scripts, generated files, and bundle/runtime impact.

Consider clean-install verification, compatibility matrices, focused migrated-API tests, broader build/type confidence, and rollback or version pinning.

## Authentication, authorization, privacy, and sensitive data

Inspect every trust boundary, permission enforcement point, tenant isolation, data storage, logging, error handling, audit trails, and secret handling.

Consider positive and negative permission cases, confused-deputy paths, object-level authorization, sensitive-data redaction, and safe failure behavior.

## Jobs, queues, retries, and distributed systems

Inspect scheduling, ordering, deduplication, idempotency, retry policy, timeouts, cancellation, dead-letter handling, concurrency, and partial failure.

Consider duplicate delivery, out-of-order messages, worker restart, poison messages, retry exhaustion, race conditions, and recovery evidence.

## Git-backed published state and concurrent agents (conditional)

Use this profile **only** when the changed system actually publishes, reads, or synchronizes Git refs or treats Git history as authoritative application state. Ordinary Git usage in a project, routine PR review, or a monorepo alone does not trigger it. First inspect the existing Git implementation, tests, host and backend contract; distinguish local `update-ref` from remote push/fetch semantics. Do not assume all Git servers provide Pando's consistency model.

- **Same-ref updates:** identify the expected previous tip and the publisher's atomic compare-and-swap or lease check (such as `git update-ref <ref> <new> <old>` locally, or an appropriately constrained remote push). A stale competing writer must not silently overwrite another writer. Verify which outcomes are observable and which need reconciliation.
- **Independent refs and cross-ref reads:** allow independent branches to progress unless a documented cross-ref invariant needs coordination. This applies to read-only consumers as well as publishers. Do not infer a repository-wide point-in-time snapshot from individually observed refs; explicitly test any required multi-ref consistency rather than globally serializing all writers by default.
- **Publication and acknowledgment:** distinguish prepared Git objects, successfully published refs, confirmed rejection, and an uncertain outcome after a timeout or lost reply. A failed subprocess acknowledgment is not proof the ref update failed. Check the exact intended ref and commit where trusted observations permit; a ref that has moved *again* cannot by itself prove whether the original publication happened. Do not blindly retry a possibly successful write or claim certainty without evidence.
- **Fetch and recovery:** after an acknowledged publication, verify that a separate reader can fetch the intended tip **and every required reachable object** under the documented visibility contract. Include interrupted transfers, retry, or stale-cache cases only if those paths exist. Preserve independent changes and uncommitted local work during recovery.
- **Deterministic verification:** for material races, prefer disposable real-Git repositories, explicit scheduling barriers, and fault injection immediately before/after publication over sleeps or random stress alone. Keep unit tests for isolated rules; use bounded integration or protocol conformance checks where mocked operations cannot prove Git behavior. State which interleavings and backend guarantees were actually exercised.

| Case | Condition | Observable test-strategy decision |
| --- | --- | --- |
| `GIT-CASE-001` | Changed behavior neither reads nor writes Git refs and does not rely on Git history as application state | Use ordinary risk selection; do not add Git-specific scenarios |
| `GIT-CASE-002` | Two agents target one ref | A stale expected-OID update is rejected and earlier committed work survives |
| `GIT-CASE-003` | Independent refs change during a multi-ref read | Check documented consistency needs; do not assume a repository-wide snapshot |
| `GIT-CASE-004` | Publication acknowledgment is lost | Reconcile the intended ref/commit; an unresolved outcome must not prompt blind retry |
| `GIT-CASE-005` | A new ref is acknowledged before a reader fetches | Verify the intended tip and reachable objects from an independent reader |
| `GIT-CASE-006` | A read-only consumer combines refs that can advance independently | Test required cross-ref consistency and read-time interleavings even without writes by the consumer |

This is a **conditional test-design reference**, not a requirement to run Git commands, build a Git server, install OpenAI's Git fork, adopt Pando, add formal verification, or enable hosted CI. Model designs and production claims in [OpenAI's Pando article](https://openai.com/index/scaling-git-at-openai/) (2026-11-02) motivate failure modes, but are not evidence of this repository's performance or guarantees. Respect the parent skill's read-only and evidence/readiness boundaries.

## AI model-mediated application behavior (conditional)

Apply this profile **only when the system under test** makes behavior-affecting model calls, delegates actions to an AI agent, or relies on model-selected tools. Using a coding assistant to *write ordinary application code* does not activate this profile. Inspect relevant runtime entry points, provider settings, tool permissions, and existing tests before choosing scenarios; do not assume live model access or a particular agent framework. **This is read-only test planning:** specify proposed scenarios, expected outcomes, oracles, and residual gaps; do not execute tests, change fixtures, or contact providers under this profile.

- **Independent outcome and grader integrity:** Specify expected behavior and an oracle independent of model control; where applicable, plan checks of resulting artifacts, observable state, and authorized side effects using deterministic assertions or qualified independent human review. An agent's success claim, generated test, or green self-reported log is not an independent oracle. Distinguish authorized task inputs and immutable public scoring rubrics from protected evaluation answers whose premature disclosure would invalidate the result. Plan checks against premature disclosure and unauthorized changes to authoritative graders, expected outputs, or scoring state; public task information alone does not compromise independence. Include hypothetical grader/fixture tampering or shortcut scenarios only for isolated synthetic or authorized environments; if the agent can influence the only scorer, mark correctness unverified.
- **Untrusted inputs and authority:** If the workflow consumes repository content, retrieved pages, tool responses, or model-produced text, design applicable prompt-injection, false-tool-output, scope-escalation, unauthorized-write, and cross-user-disclosure scenarios. Specify expected enforcement-point denials regardless of model output; do not probe live targets.
- **Failure and abstention:** Specify scenarios for malformed/empty responses, timeouts, provider errors, refusals, partial tool failures, and bounded retries where applicable. Define expected conservative fallback or explicit uncertainty, truthful provenance, and failure observability without logging prompts, credentials, or sensitive user material.
- **Repeated observations for variable behavior:** When a material outcome depends on nondeterministic model responses or variable response times, plan multiple independent attempts per representative case, with a justified sample size and budget, reset task context where appropriate, fixed relevant inputs/configuration, and an explicit independent scoring rubric. Before observing outcomes, define inclusion and exclusion rules, retry and timeout limits, and reporting denominators appropriate to the risk and budget. Retain genuine failures and timeouts in the applicable outcome denominator; do not exclude genuine model failures because of poor performance. Document invalid samples under the predefined rules and report deviations separately. Distinguish first-attempt outcomes from retry-assisted outcomes; record attempted, failed, timed-out and excluded runs with reasons rather than selecting favorable examples. Report observed outcome counts and latency distributions where measurable, with sample-size limitations. A single successful attempt does not establish repeatable reliability. Include plausible but unsupported claims and user-visible uncertainty in the rubric when factual accuracy matters; a fluent answer is not evidence of correctness. Preserve any critical-failure rule separately from aggregate scores. If repeated evidence is unavailable or not authorized, record the residual uncertainty rather than claiming reliability. This guidance is informed by the TLDR Design (2026-11-25) summary of [The AI Problems Nobody Has Solved Yet](https://uxforai.com/p/the-ai-problems-nobody-has-solved-yet); it does not establish any measured model result.
- **Point-in-time evaluation (only for historical replay or forecasting):** Define the decision cutoff, including timezone and boundary semantics, and the information that was actually available then. Plan checks for revised documents, publication versus availability timestamps, cached or retrieved content, tool responses, and labels revealed after the cutoff. Use versioned as-of fixtures and an independent oracle that reveals outcomes only after a prediction is recorded; include a negative case where an apparently old document contains a later revision. Date-filtered search and a prompt telling a model to ignore future knowledge do not establish temporal isolation: model training, fine-tuning, retrieval, or task selection may still expose outcomes. If that exposure cannot be ruled out, report retrospective results as potentially contaminated, not as verified forecasting skill; prefer prospective, sealed predictions when strict historical isolation is not feasible. This is conditional test planning, not authorization to fetch archives, run models, or add forecasting infrastructure. [Epochal Time Portal](https://epochal.com/blog/introducing-time-portal) and [ExAnte](https://aclanthology.org/2026.eacl-long.72/) motivate these controls, not a provider dependency or a performance claim.
- **Matched efficiency comparisons:** Only when model, adapter, prompt, or harness configuration is being compared, state exactly which model, adapter, prompt, or harness setting changes between arms. If multiple settings vary, call it a **bundled configuration comparison**, not proof of a single factor. Keep tasks, data snapshots, authorization, grading criteria, and budgets comparable; hold unrelated settings fixed wherever possible and record each arm's actual configuration and deviations. Specify representative and held-out tasks, independently verified outcomes and critical failures, and complete-run retries, tool calls, token use, elapsed time, and monetary cost **only where observable**. A provider benchmark or fewer tokens alone cannot prove improvement, and unmatched harness/task results are not a fair comparison.
- **Orchestration comparisons (only when comparing agent topology or context strategy):** Compare a continuous-context single agent, a single agent with a prespecified fresh-context restart and bounded handoff, and the proposed parallel or planner/executor configuration when those arms are feasible and relevant. Keep the underlying model, effort, task inputs, permissions, independent oracles and aggregate resource limits comparable for topology-only claims; treat differing planner/executor models as a bundled configuration comparison. Freeze restart triggers, handoff contents, task decomposition, concurrency and stopping rules before observing results; reset workspace and task state between independent runs. Within a run, preserve only authorized task state across restarts and keep protected oracle data out of handoffs. Where handoffs cross agent, tool, provider or trust boundaries, plan recipient-specific authorization checks for each transfer; disclose only the minimum task data permitted for that recipient and purpose. Treat model-generated handoff content as untrusted evidence, not instruction or transferable authority. Plan positive controls for permitted minimized handoffs and negative controls for unauthorized disclosure and scope escalation through handoffs; require denial at the actual enforcement boundary regardless of model output. Count aggregate work across all agents, including planning, coordination, context reconstruction, reconciliation, review, retries and failed branches; distinguish elapsed wall-clock time from total work. Compare independently verified task success and final deliverable quality separately from rubric scores, and report cost per verified success only if the monetary cost numerator is observable and the verified-success denominator is observable and positive. Report zero observed monetary charges as zero, distinguish them from unknown or unmeasured costs, and do not infer zero resource consumption from zero monetary charges. Report zero verified successes with the observed costs and outcome counts; the cost-per-success ratio is undefined when there are no verified successes. Report missing arms, incomplete accounting, and critical failures; do not infer a topology advantage from faster completion alone or from comparison only against a stale-context baseline. The TLDR AI (2026-11-25) summary of [Swarms Do Not Yet Raise the Roof](https://www.paradigm3.org/research/swarms) motivates a fresh-context control (full methodology not independently inspected); [Harvey's post-training research](https://www.harvey.ai/blog/applying-the-harvey-tenet-training-recipe-to-us-open-weight-models) motivates separating rubric and deliverable quality. Neither establishes an advantage for the assessed system. This is test design, not a mandate to build orchestration or run experiments.

| Case | Condition | Observable test-strategy decision |
| --- | --- | --- |
| `AI-CASE-001` | Change has no runtime model or agent dependency | Use ordinary risk selection; do not add AI-agent-specific scenarios |
| `AI-CASE-002` | Agent claims success or passing tests | Specify independent oracles for required artifacts and permitted effects |
| `AI-CASE-003` | Agent can access protected evaluation answers prematurely or alter authoritative scoring without authorization | Plan protection against premature disclosure and unauthorized scoring changes; mark affected correctness unverified if independence cannot be established |
| `AI-CASE-004` | Model, tool or retrieved content is untrusted input | Specify injection and unauthorized-action boundary scenarios |
| `AI-CASE-005` | Provider or model returns an error or invalid response | Specify conservative, observable failure and abstention scenarios |
| `AI-CASE-006` | Comparing a model, adapter or agent harness | Define varied configuration, fixed task controls, independent quality oracles, and measurable total work |
| `AI-CASE-007` | Historical replay or forecasting depends on information available at a cutoff | Specify temporal isolation, later-revision rejection and withheld outcomes; qualify results when leakage cannot be excluded |
| `AI-CASE-008` | Agent reads authorized task inputs or an immutable public rubric | Allow intended visibility; verify outcome independence without requiring unnecessary secrecy |
| `AI-CASE-009` | Material outcome varies across model attempts or response times | Plan independent repeated observations, report failures and uncertainty, and do not infer reliability from a single success |

These are **conditional test-design decisions**, not permission to run model evaluations, modify graders, collect transcripts, contact providers, buy tokens, or create CI jobs. Preserve the parent skill's read-only scope and the repository's policy against requiring behavioral model evaluations as a merge gate. Use synthetic/public or specifically authorized data. If material outcome verification is unavailable, record the blocked or unverified scenario under existing readiness rules rather than asserting a pass. The [METR capability update](https://metr.org/blog/2026-11-20-q4-2026-capability-update/) motivates checking reward hacking; [Hugging Face harness-adapter research](https://huggingface.co/blog/harness-adapters-at-scale) motivates matched model/harness comparisons. Neither source establishes a result for the repository being assessed.

## Performance and resilience

Inspect latency-sensitive paths, resource limits, query plans, memory use, connection pools, backpressure, caching, and dependency failure.

Consider representative load, thresholds grounded in requirements, degradation behavior, timeout budgets, recovery, and observability. Do not invent performance targets.

## Observability and incident recovery

Inspect logs, metrics, traces, alerts, correlation identifiers, dashboards, runbooks, rollback, and data repair paths.

Consider whether failures are detectable, actionable, safely diagnosable, and recoverable. Observability checks supplement behavior tests; they do not replace them.
