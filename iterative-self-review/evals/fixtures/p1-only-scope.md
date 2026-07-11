# P1-only scope fixture

User scope: fix only P1.

| ID        | Severity | Location            | Evidence                                             | Impact                  | Remediation               | Verification               |
| --------- | -------- | ------------------- | ---------------------------------------------------- | ----------------------- | ------------------------- | -------------------------- |
| CR-P1-001 | P1       | `src/session.ts:8`  | expired tokens are accepted when `expiresAt === now` | auth bypass at boundary | use `<=` expiration check | focused auth boundary test |
| CR-P2-002 | P2       | `src/session.ts:20` | duplicated date parsing                              | maintainability drift   | extract helper            | unit tests                 |
| CR-P3-003 | P3       | `src/session.ts:27` | variable name is vague                               | readability             | rename local              | typecheck                  |
