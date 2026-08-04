# Dirty plan-owned work fixture

Approved plan:

1. Add optional `middleName` support to `src/profile.ts`.
2. Update `src/profile.test.ts`.
3. Run focused verification.

The setup script creates a pre-existing unrelated user hunk in `src/profile.ts`, which is a plan-owned path. Execution must inspect and classify existing hunks, preserve the unrelated user hunk byte-for-byte, and stop if its ownership cannot be established safely.
