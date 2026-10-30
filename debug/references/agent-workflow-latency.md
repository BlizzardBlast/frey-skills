# Diagnosing coding-agent workflow latency

Load this reference **only** when the concrete performance symptom concerns a coding-agent
task or agent harness. Follow [performance investigation](performance-investigation.md)
and the parent [debug skill](../SKILL.md) for the read-only authorization,
hypothesis, measurement-ledger, stopping and result-status contracts.
This is a conditional diagnostic aid, **not** an automatic optimizer, tracer,
benchmark runner, model router or authorization to collect agent sessions.

## Define the completed-work boundary

Identify a comparable task and its independently verifiable successful outcome
before comparing two agent configurations. Capture the full user-observed wall
time, including retries, failed attempts, provisioning, tools, approval waits
and any suspend/resume cost. Keep active execution time and human-wait time
separate when both are available; neither alone is the entire experience.

Inspect existing, permitted, **sanitized** traces/metrics first. Record
whether each stage was measured, inferred or unavailable. Never treat missing
or redacted timing as zero, fabricate token/cost measurements or copy raw
prompts, private reasoning, tool responses, credentials, file paths, project
names or proprietary source into shared artifacts.

| Stage | Useful questions | Interpretation limits |
| --- | --- | --- |
| Model start / output arrival | Request-to-first provider event, request-to-first visible answer, input/cached tokens, provider-reported internal timings when available, model/region/stream mode | A first API event may contain metadata or hidden reasoning rather than visible text; first visible output can include unmeasured reasoning or buffering. Neither is necessarily time to first *generated* token or evidence of queueing |
| Model generation | Output tokens, elapsed generation time, tokens/second, thinking-effort setting | Reasoning/output token accounting differs across providers; compare only compatible measurements and task outcomes |
| Tool, shell and MCP | Wall duration per call, process/shell startup, CPU/IO, results returned, output token volume | Repeated commands, profile hotspots and large outputs suggest investigation, not a confirmed bottleneck |
| Provisioning / environment | Startup duration, CPU class, storage type, network/timeouts and resource contention | Different hardware, caches and sandbox setups invalidate an otherwise attractive speedup claim |
| Scheduling / waits | Approval, suspend/resume, external-job waits, retry/backoff and poll intervals | Human wait and asynchronous operations may overlap active work; avoid summing overlapping spans |
| Parallel work | Dependency chain, overlapping calls, concurrency, retries, failures and completed output | Sum of tool-call durations is **not** elapsed wall time when calls overlap |

Before reporting "TTFT", define the clock start (such as request submission)
and the exact observed endpoint: (a) the first API/stream event received by
the instrumented client, (b) the first user-visible answer token, or (c)
provider-reported prefill/reasoning/generation spans, if separately exposed.
These are **different metrics**, not interchangeable timestamps. A
non-streamed response may reveal only response-completion time, not either
first-token event. Streaming modes, buffering, hidden reasoning and transport
boundaries affect comparability. Mark unobservable internal time as
**unattributed**, not as provider queueing, network or prefill time; a causal
attribution needs independent evidence. Do not request private reasoning to
fill the gap.

Prefer timestamps or parent/child spans that permit a non-overlapping
**critical-path** reconstruction. If spans overlap, report stage durations
and wall time separately; do not present their sum as total latency.
Include model calls, nested agents, failures and fallback calls in the
task outcome and resource accounting. Keep the standard measurement-ledger
context (revision, environment, workload, sampling, status and provenance).

## Diagnose before proposing a change

1. **Find the largest evidenced delay on the critical path.** Compare full
   completion time with stage contributions and dispersion across comparable
   tasks. Decide whether the symptom is first-token delay, long generation,
   redundant tool work, process startup, queueing, I/O or external waiting.
   Do not guess from model tokens/second alone.
2. **Inspect repeated work, not just slow calls.** Look for repeated full-tree
   scans, many spawned processes (including per-file subprocess loops),
   oversized shell/MCP results and initialization in every fresh shell.
   Prefer targeted output or an already-available indexed lookup when the
   permitted evidence demonstrates recurring waste. A new database, tool or
   service requires its own cost/security/maintenance justification.
3. **Treat polling as a hypothesis.** A repeated sleep/check loop may waste
   wall time if a trusted completion signal already exists. Check the actual
   upstream API, timeout/cancellation semantics, backoff, idempotency and
   lost-notification recovery before proposing event-driven notification.
   Avoid spinning or removing a necessary rate limit.
4. **Examine parallelism only for independent operations.** Compare the
   dependency graph and tool/environment contention, then preserve sequencing
   for writes, shared state, branch changes and authorization checks.
   Concurrent calls can be slower or less correct; no blanket
   parallelization instruction follows.
5. **Compare model settings without weakening verification.** Thinking budget,
   context size, prompt-cache behavior and provider tier can change latency.
   Pre-register a task/quality oracle; vary one permitted setting at a time
   under comparable conditions, and count retries/fallbacks. Fast failed
   solutions, low token counts or a model's own success claim are not gains.
   Do not transfer sensitive inputs to another provider without explicit
   authorization. Quantization and provider metering can differ.
6. **Check environment only where implicated.** Shell initialization,
   sandbox/snapshot I/O, CPU allocation, memory pressure and network/DNS
   timeouts can dominate some workflows. Do not install profilers, change
   infrastructure or collect production traces without separate authority.

The article discusses interpreting model reasoning traces to discover desired
tools. **Private chain-of-thought access is not a prerequisite** for this
workflow: use observable authorized tool choices, errors, stage timings and
explicit user-reported friction. Do not request, export or persist private
reasoning to pursue an optimization.

## Decision and comparison contract

Compare the same task, independent correctness checks, model/harness/tool
versions, task inputs, environment, parallelism, cache state and permissions
between baseline and candidate; declare differences and unmeasured factors.
Use a **finite, pre-authorized** sampling budget and stop on unexpected errors,
unsafe effects, budget exhaustion or inconclusive repetitions. The parent
reference governs whether another non-mutating diagnostic is safe to run.
Capture spread/tail effects where enough observations exist; do not invent
significance from one task. Record whether performance data came from a
complete trace or an incomplete subset, and label proposed runs NOT_RUN.

Only recommend an optimization when its suspected stage has causal supporting
evidence, the trade-offs and rollback are understood, and completed-task
quality does not deteriorate. Apply the parent debug/performance result-status
contract: if a necessary diagnostic requires unavailable, unsafe or
unauthorized access, return `BLOCKED / UNRESOLVED` and do not try to obtain
that access. With useful permitted evidence but missing task comparability,
independent outcome checks or stage data, return `PARTIAL / UNRESOLVED` (or
`PARTIAL / LIKELY` only when evidence favors one cause and confirmation
remains outstanding). Incomplete evidence cannot establish a speedup.

### Illustrative arithmetic, not an observation

A hypothetical 60-second task contains 6 seconds of provisioning, 24 seconds
of inference, 18 seconds of tools and 12 seconds of suspend/resume. Halving
**only inference** reduces total duration to 48 seconds: 20% less wall time,
not 50%. These numbers illustrate Amdahl's law and **are not benchmark results
for any repository or provider**. Real concurrent spans require critical-path
analysis rather than direct addition.

### Additional deterministic decision cases

These supplement, rather than replace, the parent
[performance cases](performance-investigation.md#deterministic-decision-cases).
They describe expected **interpretation** of synthetic evidence, not executed
agent trials.

| Case | Available evidence | Required interpretation |
| --- | --- | --- |
| AGENT-PERF-01 | Only provider tokens/second improves; task completion and successful outcomes have not been measured | No verified end-to-end speedup; PARTIAL / UNRESOLVED |
| AGENT-PERF-02 | A poll loop appears in a trace, but notification guarantees and timeout behavior are unknown | Investigate alternatives; no automatic removal of waits or authorization to change the service |
| AGENT-PERF-03 | Tool calls overlap and their summed durations exceed wall time | Report wall time and critical path separately; do not double-count |
| AGENT-PERF-04 | Candidate completes faster but fails a required independent outcome check | Reject quality-preserving speedup claim; diagnose failure under normal investigation rules |
| AGENT-PERF-05 | Two model settings have different task inputs, caches or tool permissions | Mark comparison materially mismatched; do not attribute the difference to thinking budget |
| AGENT-PERF-06 | First visible text is delayed, but the first provider event and hidden reasoning timings are unknown | Label only the observed first-visible-answer time; treat internal spans as unattributed, not proven queueing or prefill |
| AGENT-PERF-07 | Necessary diagnosis depends on an unavailable or unauthorized tool, even if some permitted timings exist | `BLOCKED / UNRESOLVED`; do not run or seek authorization through the document |

## Source and scope

Adapted from Martin Alderson,
[Making agents fast — what I've learnt over the last 12 months](https://martinalderson.com/posts/making-agents-fast/)
(2026-10-29). Its examples are illustrative engineering observations,
not controlled performance results for Codex, OpenCode or this repository.
No automatic tool changes, background capture, model routing, new
dependencies, mandatory telemetry, CI performance threshold, skill activation
change or instruction-promotion mechanism is introduced.
