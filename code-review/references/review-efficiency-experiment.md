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
