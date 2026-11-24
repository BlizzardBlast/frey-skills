# Risk and Scenario Rules

Use this reference to prioritize coverage and keep risks traceable to scenarios.

## Risk prioritization

Prioritize with evidence, not invented scores. Consider:

- user, data, financial, security, operational, and compatibility impact;
- how directly the change touches the behavior;
- known defect or incident history;
- likelihood, marked `unknown` when evidence is unavailable;
- detectability before users are affected;
- reversibility and recovery cost;
- concurrency, rollout, and external dependency exposure.

Use `critical`, `high`, `medium`, or `low`. Explain the reason for critical and high priorities.

## Traceability

Every critical or high risk must map to at least one scenario or an explicit blocked-coverage statement. Every scenario must map back to one or more risk IDs and an observable contract.

Do not create scenarios only to satisfy a matrix. Remove duplicates that exercise the same contract, state, data shape, and failure mode without adding confidence.

## Scenario selection

Prefer scenarios that cover distinct material dimensions:

- core success contracts;
- minimum, maximum, empty, null, malformed, and unsupported input;
- state transitions and invalid transitions;
- authorization and tenant boundaries;
- partial failure, timeout, retry, cancellation, and recovery;
- duplicate, concurrent, and out-of-order operations;
- old/new version compatibility;
- migration, rollback, and representative historical data;
- keyboard, focus, semantic, and assistive-technology behavior;
- dependency degradation and failure observability.

Use pairwise or representative selection when exhaustive combinations add little risk reduction. State which dimensions were sampled.

## Layer selection

Choose the smallest layer that can prove the contract reliably:

- unit tests for isolated deterministic rules;
- component tests for UI behavior and accessibility boundaries;
- contract tests for stable producer/consumer shapes;
- integration tests for persistence, services, jobs, and cross-module behavior;
- end-to-end tests for critical journeys that require the assembled system;
- migration tests for data transitions and compatibility;
- smoke tests for deployment identity and critical availability;
- exploratory testing for complex or poorly modeled interactions;
- production-safe observability checks for staged rollout evidence.

Avoid duplicating every scenario at every layer. Use broader layers for cross-boundary confidence, not for logic already proven cheaply.

## Human usability evidence (conditional)

When the change materially affects a user journey and its success depends on
discoverability, comprehension, or human effort, distinguish functional
verification from formative usability observation. Routine visual fixes,
internal APIs, and deterministic behavior alone do not require participant
research.

- Ground the goal and observable success condition in authorized requirements.
  For a prototype, record its version, linked states, simulated behavior and
  limitations; do not infer production behavior from it.
- Propose outcome-oriented tasks, representative users and a defined starting
  state. Avoid naming the controls or prescribing the navigation sequence.
  Define timing start/end and how unaided, assisted and abandoned attempts
  will be recorded when effort is relevant.
- Use synthetic/minimized data, a safe environment and consented,
  non-identifying observations. Do not prescribe external uploads, recordings,
  recruitment, production mutations or telemetry without explicit authority.
- Plan evidence for task completion, observable confusion/errors and
  moderator assistance; include time on task only where meaningful. For
  comparisons, keep task, starting state and success criteria comparable and
  report learning/order effects and sample limits.
- Keep required functional, accessibility and security checks independent.
  An automated E2E script, screenshot review, or simulated agent participant
  can supplement review but cannot prove human discoverability, comprehension
  or measured human task time.
- Mark unavailable participant or prototype evidence explicitly; do not
  claim that research ran. Optional formative evidence is not a universal
  merge/release gate. If human evidence is an accepted requirement or is
  material to a critical/high-risk decision, apply the parent skill's
  completeness/readiness rules and record the blocked coverage.

| Example condition | Observable strategy decision |
| --- | --- |
| A changed onboarding journey must be understood unaided | Propose a goal-based participant task and separate functional/accessibility checks |
| A scripted E2E test completes an onboarding journey | Count it as functional evidence, not a human usability result |
| No participants are available for optional formative research | Record the gap without inventing results or automatically blocking release |
| A required human usability acceptance measure cannot be assessed | Record blocked evidence and apply the existing readiness rules |

Research basis: [Loop11 — Figma prototype usability testing](https://www.loop11.com/figma-prototype-usability-testing/).
This is test-strategy guidance, not permission to execute research or change
the approved specification.

## Data and environments

For each required dataset or environment, state:

- ownership and provisioning path;
- representative characteristics;
- sensitive-data restrictions;
- reset, isolation, and cleanup behavior;
- service and configuration dependencies;
- whether availability is confirmed, assumed, or blocked.

Do not prescribe production data copying without an approved privacy-safe process.

## Automation candidates

Prioritize automation when the scenario is high-risk, repeatable, deterministic, frequently executed, and maintainable at the chosen layer.

Keep manual or exploratory coverage when automation would be unstable, unsafe, prohibitively expensive, or unable to assess the relevant human or visual behavior. Explain the tradeoff.

## Entry and exit criteria

Entry criteria should describe the minimum stable code, environment, data, dependency, and observability conditions needed to begin meaningful testing.

Exit criteria should be tied to risk:

- critical and high-priority scenarios completed with accepted results;
- no unresolved blocking defect in the requested scope;
- required migration, rollback, or compatibility evidence recorded;
- residual risks explicitly accepted by the responsible decision-maker;
- blocked checks and evidence limits visible.

Do not define exit solely as a coverage percentage or a test count.
