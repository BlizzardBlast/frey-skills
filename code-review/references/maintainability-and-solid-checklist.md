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

## Finding guidance

Make maintainability findings concrete: identify the future change or defect risk, name the coupling/cohesion problem, and suggest the smallest refactor that reduces risk without changing behavior. Avoid recommending factories, interfaces, or patterns unless they remove a demonstrated dependency or invalid state.
