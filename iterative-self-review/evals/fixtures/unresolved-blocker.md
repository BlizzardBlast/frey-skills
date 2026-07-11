# Unresolved blocker fixture

Ledger:

| ID        | Severity | Location                 | Evidence                                 | Impact                       | Remediation                                       | Verification                         |
| --------- | -------- | ------------------------ | ---------------------------------------- | ---------------------------- | ------------------------------------------------- | ------------------------------------ |
| CR-P1-001 | P1       | `src/payments/client.ts` | production-only 401 from partner sandbox | payments cannot be submitted | confirm required OAuth audience and update config | requires partner sandbox credentials |

Constraint: no sandbox credentials or partner docs are available in the fixture.
