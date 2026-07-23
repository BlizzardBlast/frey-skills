# Plan-refinement fixture

User intent: review and tighten this implementation plan before editing.

Repository evidence:

- `src/accounts/api.ts` serializes `accountNumber` in requests and responses.
- `src/accounts/types.ts` exposes `accountNumber` in the public `Account` type.
- `docs/account-api.md` documents `accountNumber` as part of the external API.
- No compatibility alias for `acctNo` exists.

Proposed plan from the user:

1. Rename `accountNumber` to `acctNo` in the shared type.
2. Update the frontend mapper.
3. Remove duplicate mapping code.
4. Run the tests.

Constraint: the external API contract must not change as part of this cleanup.
