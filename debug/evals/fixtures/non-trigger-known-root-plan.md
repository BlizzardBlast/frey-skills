# Known-root planning non-trigger fixture

User request: create an implementation plan for the confirmed session-expiry defect.

Established evidence:

- Tokens store expiry as Unix seconds.
- The current implementation compares expiry seconds with `Date.now()` milliseconds.
- The mismatch is the confirmed root cause.
- The user wants a repository-grounded plan before editing.

This should route to `implementation-plan`; repeating root-cause investigation would be redundant.
