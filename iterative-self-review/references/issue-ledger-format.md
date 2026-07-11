# Issue Ledger Format

Use this compact ledger when accepting issues from `code-review` or from the user.

## Incoming ledger

| ID | Severity | Location | Evidence | Impact | Remediation | Verification | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CR-P1-001 | P1 | `path/file.ts:42` | observed failing branch | user-visible failure | smallest safe fix | focused test/build/manual check | unresolved |

## Pass update

For each pass, record:

- IDs attempted.
- Files edited.
- Verification run and result.
- State changes.
- New risks or blockers discovered.

## Final wording

Avoid absolute cleanliness claims. Prefer:

- `RESOLVED for the requested ledger scope`
- `PARTIAL: CR-P2-002 remains unresolved because...`
- `BLOCKED: CR-P1-001 cannot be verified because...`
