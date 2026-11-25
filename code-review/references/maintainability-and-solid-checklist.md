# Maintainability and SOLID Checklist

Use this for maintainability, design, cohesion, dependency, complexity, or SOLID-specific review concerns.

## Pragmatic SOLID lens

- Single responsibility: prefer cohesive modules with one reason to change; do not split code only to match terminology.
- Open/closed: prefer extension points only where variation is real and likely; avoid speculative abstractions.
- Liskov substitution: check caller-visible behavior and invariants, especially in inheritance, strategy, or interface-like code.
- Interface segregation: prefer small caller-shaped APIs when broad APIs force unrelated dependencies or mocks.
- Dependency inversion: depend on stable boundaries where volatility or testability demands it; do not add indirection for its own sake.

## Maintainability signals

- Hidden coupling across layers, packages, feature flags, generated code, or globals.
- Duplicated business rules that can drift.
- Boolean prop or option explosions that create invalid states.
- Long functions where validation, transformation, side effects, and rendering are tangled.
- Error handling that obscures the cause or makes recovery ambiguous.
- Tests coupled to implementation details instead of observable behavior.

## Cross-change consistency (conditional)

Apply when a change introduces or alters a shared rule, helper, contract, generator,
or repeated migration pattern with plausible related implementations. This is
particularly useful for work accumulated across independent agent sessions.
Do not require a repository-wide audit for an isolated change.

- Establish the intended invariant and its owner from inspected contracts,
  accepted decisions, existing implementations and tests. Search relevant
  callers and parallel implementations by behavior, not only by symbol name.
  A newly introduced helper is not automatically the canonical implementation.
- When a shared abstraction changes, inspect affected existing consumers and
  equivalent earlier implementations for incompatible semantics, missed
  adoption or duplicated rules. Compare relevant inputs, outputs, side
  effects and failure behavior; textual similarity alone is insufficient.
- For generated code, inspect the canonical generator and inputs as well as
  relevant output; verify reproducibility and independently grounded behavior
  where applicable. A clean regeneration diff does not prove semantic parity.
- Distinguish intentional domain variation, compatibility constraints and
  incidental duplication from an evidenced inconsistency. Prefer the smallest
  change that preserves ownership, dependency direction and behavior; do not
  force unrelated modules to share a premature abstraction.
- Record inspected consumers, search limits, the demonstrated mismatch and
  missing evidence in the existing coverage matrix and finding ledger. Treat
  unrelated pre-existing debt as out of scope unless the current change makes
  it a concrete risk. Missing material coverage follows the existing review
  completeness rules; neither a clean local diff nor passing tests proves
  repository-wide consistency.

Research motivation: [Legacy Modernization with LLMs: Is a large translation
consistent with itself?](https://tomassetti.me/legacy-modernization-llms-large-translation-consistency/)
describes drift and duplicated helpers across independent translation sessions.
This conditional review guidance is an adaptation, not a universal defect-rate
claim or a new repository-wide enforcement gate.

## Finding guidance

Make maintainability findings concrete: identify the future change or defect risk, name the coupling/cohesion problem, and suggest the smallest refactor that reduces risk without changing behavior. Avoid recommending factories, interfaces, or patterns unless they remove a demonstrated dependency or invalid state.
