# Competing hypotheses fixture

User intent: investigate why valid sessions are rejected after login.

Evidence:

- A cache module changed in the same release.
- Disabling the cache does not change the failure.
- The token payload stores `expiresAt` as Unix seconds.
- `isExpired.ts` compares `expiresAt < Date.now()`.
- Converting `Date.now()` to seconds makes the failing example behave correctly.
- The same token succeeds in the previous version, which used `Math.floor(Date.now() / 1000)`.

The investigation must test the attractive recent-cache explanation instead of assuming recency proves causation.
