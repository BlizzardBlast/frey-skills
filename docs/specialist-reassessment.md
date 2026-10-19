# M4 specialist reassessment and debug performance extension

Date: 2026-10-19. Baseline: clean `main` at
`8554932221064dd82c99404c468b85a8e531f43a` after PR #27.
Development branch: `codex/debug-performance-investigation`.

The user requested the next development step. The roadmap identified M4:
reassess performance guidance and retrospective demand after M1-M3. This bounded
work extends an existing skill and records the specialist decisions below.
The roadmap and research are evidence, not approval for commands, sensitive
access, experiments, new operational workflows, or external writes.

## Evidence inspected and limits

- At the baseline, `debug` instructions covered causal tracing, competing
  hypotheses, external failures, bounded sampling, and read-only diagnostics.
  Its profiles mentioned timing and resource contention but lacked a performance measurement
  ledger and explicit comparison rules.
- `test-strategy` already covers performance test selection; it does not diagnose
  a symptom. `architecture-decision` compares established alternatives, and
  `implementation-plan` sequences changes after behavior/cause are established.
  The extension reuses diagnosis rather than duplicating those outputs.
- Repository documentation and fixtures contain synthetic design/evaluation
  examples, not recurring maintainer performance or retrospective task reports.
  The connected GitHub issue search
  `repo:BlizzardBlast/frey-skills is:issue`, on the date above, returned no issues.
  This is a bounded evidence check, not evidence of absent demand. Private tasks,
  usage analytics, and maintainer capacity were not inspected or inferred.
- Google's [monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/)
  separates outcome populations and relates latency to demand and resource
  pressure. Brendan Gregg's [active benchmarking method](https://www.brendangregg.com/activebenchmarking.html)
  emphasizes understanding the work and its actual limiter. These sources were
  refreshed on 2026-10-19; they inform interpretation, not permission to run load.
- Google's [postmortem guidance](https://sre.google/sre-book/postmortem-culture/),
  refreshed on the same date, supports a distinct incident-learning artifact.
  It does not establish recurring demand or an owner for a frey-skills workflow.

## Specialist dispositions

| Decision | Disposition | Evidence and consequence | Revisit gate |
| --- | --- | --- | --- |
| M4-PERF-EXTEND | EXTEND `debug` | Measurement provenance/comparability and bounded discriminating checks fit the existing symptom, hypothesis, and causal-result artifact. Implement the conditional reference and contracts, preserving the four modes and read-only authority. | Reassess after sanitized real tasks expose a concrete missing diagnostic contract. |
| M4-PERF-DEFER | DEFER standalone `performance-investigation` | No qualifying recurring task records were found in the inspected sources. A separate runner or baseline workflow would add a boundary without demonstrated extraction need. | At least two sanitized maintainer-reported tasks must show why the measurement artifact cannot be expressed clearly through `debug` and its reference. |
| M4-RETRO-DEFER | DEFER `incident-retrospective` | The post-incident artifact is distinct, but recurring sanitized requests, evidence access, and maintenance ownership remain unestablished. Do not turn this into an active incident-response workflow. | Repeated authorized retrospective requests demonstrate the gap; establish sanitized inputs, output boundaries, and maintenance ownership before authoring. |

The extension adds no canonical skill, runtime dependency, profiler, benchmark
runner, command, activation policy, client requirement, or release action.
The portfolio remains eleven skills. The two deferred candidates are not
rejected permanently; they have explicit evidence gates instead of a schedule.

## Required behavior and acceptance

| ID | Required observable behavior | Authoring and deterministic coverage |
| --- | --- | --- |
| PERF-REQ-001 | Route concrete performance symptoms through existing modes and load the reference before choosing diagnostics | Core route, profile, conditional-mode contract |
| PERF-REQ-002 | Record workload, environment/revision, units/boundary, sampling, cache/warmup, outcomes, provenance, and comparison limits without inventing observations | Measurement ledger and field contract |
| PERF-REQ-003 | Reject material confounders and changed outcome populations as proof of speedup; distinguish averages from tail latency | Comparison rules, PERF-CASE-001/004/005, fast-error arithmetic |
| PERF-REQ-004 | Keep a hotspot or timing change separate from confirmed causality and preserve existing completeness/result semantics | PERF-CASE-002/008/009, causal-evidence contract |
| PERF-REQ-005 | Require existing command authority and minimized evidence; do not install tools, generate production load, use secrets, or change shared state | Bounded proposal, PERF-CASE-006/010, command/data contract |
| PERF-REQ-006 | Declare finite sample/time/load/resource limits and stop on exhaustion or unsafe effects without automatic extension | PERF-CASE-003/007, budget/stopping contract |
| PERF-REQ-007 | Distinguish observed results from unrun proposals, sourced reports from proof, and synthetic examples from real benchmarks | Ledger execution status, PERF-CASE-010, illustration contract |
| PERF-REQ-008 | Keep specialist extraction demand-dependent, preserve the eleven-skill inventory, and validate distributable source parity | Disposition record, registry, metadata/specification checks, plugin build/parity |

## Implementation and validation record

Authoring includes the conditional reference, core route and version update,
profile/checklist guidance, README and contributor documentation, focused
standard-library contracts, gate registration, changelog, and roadmap record.
The measurement ledger lives within the existing baseline/evidence output;
no new investigation mode or root-cause status is introduced.

Focused validation passed:

- `.venv\Scripts\python.exe -B -S -E -m unittest scripts.test_debug_performance_contract scripts.test_skill_behavior_contracts scripts.test_content_trust_contracts scripts.test_check.CheckTests.test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages`:
  all 32 tests passed, including all eight new tests, the shared instruction/trust
  contracts, and clean-interpreter loading of the plugin contracts. Site packages
  and Python environment overrides were disabled for this focused run.
- The new module parsed with Python 3.9 grammar. This is a syntax check, not a
  Python 3.9 runtime result.

Full deterministic validation passed:

- `.venv\Scripts\python.exe -B scripts/check.py --base origin/main` exited 0.
  `origin/main` resolved to the baseline above. The runner reported 46 helper
  tests, 105 repository/tooling tests, and 133 plugin/instruction-contract tests:
  **284 tests run, 278 passed, six expected platform skips**.
- All eleven Agent Skills specifications passed. The generated bundle was
  rebuilt from canonical sources and passed parity, including the new debug
  reference. Staged, unstaged, and committed-range whitespace checks passed.
- The six helper skips cover filesystem/platform capabilities unavailable on
  this Windows environment. They are not passes. This milestone's runtime
  verification is local Windows/Python 3.12; no new hosted CI or native Linux/macOS
  result is claimed.

Scoped self-review covered the complete M4 delta, including new files, against
the baseline above. It is not independent approval or a repository-wide audit.

| Concern | Status | Inspected evidence | Limit |
| --- | --- | --- | --- |
| Purpose, discovery, routing and output | reviewed | Core entrypoint, conditional reference, four existing modes and output/result rules, README | Static instructions; no model activation claim |
| Measurement and causal correctness | reviewed | Workload/context ledger, outcome separation, budget rules, ten cases, arithmetic illustration and mutation contracts | No real application measurement or speedup evidence |
| Security, privacy and stopping | reviewed | Existing trust boundary, command provenance, blocked effects, sensitive-evidence minimization, bounded proposals and case outcomes | No claim of universal injection resistance |
| Python, design and portability | reviewed | Small standard-library contract module, registry, clean-interpreter tests and Python 3.9 grammar | Runtime execution is local Windows/Python 3.12 |
| Packaging and documentation | reviewed | Eleven-skill discovery/specification results, generated reference parity, README, contributor guidance, changelog and roadmap | Development-only extension; no publication or installed-client claim |
| Runtime API, database, deployment and dependencies | not applicable | No such implementation or dependency change in this delta | No operational acceptance implied |

The self-review found **no remaining actionable findings** in this scoped delta.
Repository-authored text cannot create task, requirement, command, data-access,
decision, mutation, or risk-acceptance authority. No benchmark, production probe,
profiler, model trial, or installed-client test has been run for this extension;
no model-behavior certification is claimed. Final documentation-only status
updates receive scoped link, newline, and whitespace checks rather than repeating
unchanged implementation gates.

M4 development status: **IMPLEMENTED**, unreleased. The specialist reassessment
is complete; the disposition gates below remain open for future requests.

## Next gate

Do not create the deferred specialists automatically. For performance extraction,
collect only authorized, sanitized task summaries: task/provenance, requested
artifact, constraints, evidence limits, and why the existing extension could not
express the result. Do not copy private traces, customer data, credentials, raw
transcripts, or repository source into those summaries. Synthetic cases and
deterministic checks do not count as maintainer-reported usage.

Retrospective reconsideration needs recurring stabilized-incident synthesis
requests and an explicit evidence/privacy/ownership boundary. An incident whose
cause remains unknown must retain that uncertainty. A future release executor
or other operational workflow remains separately scoped and cannot gain
authority from this reassessment or a positive readiness result.
