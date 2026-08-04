# Existing ledger remediation non-trigger fixture

User request: fix this already-triaged issue using iterative self-review.

| ID        | Severity | Location         | Evidence                                                 | Impact                         | Remediation                    | Verification                             |
| --------- | -------- | ---------------- | -------------------------------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------------- |
| CR-P1-001 | P1       | `src/total.ts:2` | empty arrays throw because `reduce` has no initial value | checkout with no items crashes | provide an initial accumulator | unit test for empty and non-empty arrays |

The diagnosis and remediation are already established. This request belongs to `iterative-self-review`, not `debug`.
