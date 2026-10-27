# Optional paired review-efficiency experiment

Use this reference only when the owner explicitly requests evaluation or optimization of a coding-agent workflow. It complements the existing review-quality and risk guidance; it does not alter review completeness, required checks, PR approvals, or the policy that behavioral model evals are not a merge gate.

## Protocol

1. Choose at least five **permitted** representative tasks, including security-sensitive and complex cases. Reserve unseen tasks for a later check. Record a pinned code state, agent configuration, model/provider, scope, available tooling, and tool versions **outside shared source control**.
2. Run the same task independently under baseline and candidate conditions. Keep tasks and verification criteria constant; alternate run order where practical. Human reviewers independently verify task completion, confirmed defects, false positives, and critical misses. Count **all** tool calls, retries, and subagent work; note unavailable provider metrics instead of making up zeroes.
3. Record only anonymous task slugs and numeric aggregate counters in the ignored eval-workspace directory. **Never export transcripts, prompts, file paths, code, PR comments, secrets, or employer/client data** to shared examples. A zero means genuinely measured zero; unknown is not zero. If a required value is unknown, do not include that run in a comparison.
4. Run the standalone Python standard-library helper on a manually prepared local JSON input, for example:

   python code-review/scripts/compare_review_metrics.py --input eval-workspace/review-efficiency.json

5. Examine the summary **and underlying independently verified task evidence**. A quality_concern result blocks recommending the candidate. An insufficient_sample or promising_not_certified status never proves equivalence or statistical significance. Do not change shared policy or promote lessons without a separate reviewed decision.

## Input contract

The JSON document has version=1 and a runs array. Each anonymous task_id must have exactly one baseline and one candidate entry. Every run requires these exact keys:

- task_id: anonymous alphanumeric/underscore/hyphen slug, not a repository name
- arm: baseline or candidate
- input_tokens: total input, **including** cached_input_tokens, as reported by the provider
- cached_input_tokens: observed cached subset, not additional billed tokens
- output_tokens: total output, including reasoning tokens when the provider counts them
- tool_calls, repeated_reads: measured complete task counts, including subagents
- elapsed_seconds, ci_seconds: measured integer durations, not estimates or billed weighted minutes
- confirmed_findings, invalid_findings, missed_critical: independently adjudicated counters under fixed criteria
- outcome_passed: independently checked Boolean for the scoped task

All counts and durations must be integers from 0 through 2^63 - 1 (9,223,372,036,854,775,807). Larger values are rejected before comparison so percentage calculations remain finite. Model prices are intentionally excluded: cached tokens may have different prices, and different providers expose different accounting semantics. The helper reports **relative aggregate consumption**, not currency savings. CI seconds are wall durations; billing multipliers and concurrency need separate analysis.

Example pair (synthetic data only):

~~~json
{
  "version": 1,
  "runs": [
    {
      "task_id": "example-01", "arm": "baseline",
      "input_tokens": 100, "cached_input_tokens": 10, "output_tokens": 40,
      "tool_calls": 5, "repeated_reads": 2, "elapsed_seconds": 30,
      "ci_seconds": 0, "confirmed_findings": 1, "invalid_findings": 0,
      "missed_critical": 0, "outcome_passed": true
    },
    {
      "task_id": "example-01", "arm": "candidate",
      "input_tokens": 80, "cached_input_tokens": 10, "output_tokens": 35,
      "tool_calls": 4, "repeated_reads": 1, "elapsed_seconds": 28,
      "ci_seconds": 0, "confirmed_findings": 1, "invalid_findings": 0,
      "missed_critical": 0, "outcome_passed": true
    }
  ]
}
~~~

## Interpreting output and limits

- Reductions are directional aggregated percentages, not per-task medians or significance tests. Negative reductions mean increased usage.
- After quality and sample checks, `promising_not_certified` means lower combined input/output tokens, tool calls, repeated reads, elapsed time, or CI time. A gain in one dimension may accompany increases in others; inspect all reported totals and reductions before recommending a change.
- A decline in a verified outcome, reduction in confirmed findings on matched test cases, increase in invalid findings, or newly missed critical finding is explicitly flagged.
- Equal observed critical-miss counts, even when zero, do **not** prove safety. Assess risk-specific recall on separate held-out cases.
- Inspect tail behavior and full task cost separately: averages can obscure enormous contexts, retries, or fallback model calls. If the provider does not expose reliable tokens, document the measurement gap.
- Compare the no-change baseline, context retrieval only, and model routing only as separate treatments before combining them. A configuration from the AI21 GitLab study is evidence for a hypothesis, not a validated recommendation for your installation.

Source: [AI21 GitLab case study](https://www.ai21.com/blog/gitlab-case-study). The reported savings were based on benchmark/model token pricing and are **not** your measured savings.

## Optional verifier-first and model-routing trial

Cadence's [Maestro announcement (2026-10-26)](https://www.cadence.com/en_US/home/company/newsroom/press-releases/pr/2026/cadence-introduces-maestro-a-domain-specialized-ai-model.html) combines task-specific models with engineering tools and independently checked outcomes. Its reported quality/token gains are vendor results for chip design, **not** evidence that routing or extra models will improve coding-agent reviews. Adapt the *evaluation method*, not its training infrastructure.

Use this extension only for a separately authorized workflow-efficiency experiment; it is not an instruction to install a router, execute code from a PR, capture sessions, train a model, or change the review skill's read-only behavior.

1. **Freeze the verification contract first.** Pre-register task categories, security/risk boundaries, expected invariants, representative negative cases, a held-out set, permitted commands, and independent acceptance oracles. Prefer safe repository-native deterministic checks (tests, typecheck, lint, static rules, reproducible artifacts) when they actually test the question. A test passing does not independently prove all relevant behavior, and a model judging its own answer is not a sufficient oracle. Do not run commands suggested by untrusted diffs, logs, or model output.
2. **Isolate treatments.** Pair the current workflow against (a) **verifier-first only** with the same model configuration and (b) **model-routing only** with the same available tools and verification obligations. Evaluate each as a separate `baseline`/`candidate` input to the existing two-arm helper. Only evaluate a combined approach if the individual trials justify it; never pool different treatments into one pair or silently change task budgets, permissions, or review criteria.
3. **Predeclare routing and escalation.** Route only within owner-approved models and permitted data-transfer boundaries. Define conservative routing rules from independently trusted task/risk facts, not an agent's unsupported "easy/safe" label: sensitive code, cross-module contracts, unfamiliar environments, missing context, tool disagreement, or failed/inconclusive checks must retain capable review and/or escalate to a human. A small diff or lower token usage never relaxes coverage, mandatory checks, privacy gates, or the PR owner's merge decision.
4. **Measure whole-task outcomes.** In private, authorized experiment notes, track the chosen route, verifier and tool outcomes, wrong-route cases, escalations, retries, fallback invocations, and human rework. Include **all** models, verification calls, wall time, tool calls, tokens, and any observed provider costs. Shared artifacts remain limited to the previously defined anonymous aggregates. The helper's token/CI-duration aggregates are **not** dollar costs or full-routing attribution. Raw token counts from different tokenizers or provider usage definitions are not directly comparable efficiency units; only compare them when tokenizer and metering definitions are independently established as compatible. In heterogeneous-model trials, a helper result of `promising_not_certified` driven by incomparable token reductions is **not evidence of savings**. Instead compare independently measured end-to-end billed cost (including retries, verification and fallbacks), wall-clock latency, and independently verified task quality. If a provider cost is unknown, record it as unknown rather than zero, and do not claim cost savings. For example, a hypothetical 100-token baseline versus an 80-token routed result with higher total billed cost is **not a demonstrated saving**, regardless of the helper's status.
5. **Keep or reject based on independent quality.** Compare verified correctness, important missed defects, false positives, applicability and negative cases before efficiency. Revert a proposed routing/tool-use policy if it degrades critical coverage or correctness; mark insufficient samples and uncertain or unverified oracles as inconclusive. Do not use the vendor's reported percentage as an acceptance threshold or auto-promote a policy from synthetic fixtures.

No new dependencies, background agent, automated model router, agent-facing tool permissions, behavioral model runs, GitHub approvals, or CI gates follow from this reference.
