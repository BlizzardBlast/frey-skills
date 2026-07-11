# Ledger remediation fixture

Incoming issue:

| ID        | Severity | Location         | Evidence                                                 | Impact                         | Remediation                    | Verification                             |
| --------- | -------- | ---------------- | -------------------------------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------------- |
| CR-P1-001 | P1       | `src/total.ts:2` | empty arrays throw because `reduce` has no initial value | checkout with no items crashes | provide an initial accumulator | unit test for empty and non-empty arrays |

Current code:

```ts
export function total(items: number[]) {
  return items.reduce((sum, item) => sum + item);
}
```
