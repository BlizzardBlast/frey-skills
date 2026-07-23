# Refactor planning fixture

User intent: plan a refactor that removes duplicated money parsing without changing observable behavior.

Current code:

- `src/money/index.ts` publicly exports `parseMoney` from `src/money/parseMoney.ts`.
- `src/money/parseMoney.ts` trims input, rejects invalid decimal syntax, and returns integer cents.
- `src/orders/normalizeOrder.ts` contains a private copy of equivalent parsing logic.
- `src/invoices/normalizeInvoice.ts` contains another private copy with the same accepted/rejected examples.
- `src/money/parseMoney.test.ts`, `src/orders/normalizeOrder.test.ts`, and `src/invoices/normalizeInvoice.test.ts` assert the current behavior.
- Other packages import `parseMoney` through `src/money/index.ts`.

Constraints:

- Preserve the `parseMoney` export and current accepted/rejected input behavior.
- Do not introduce a new package or abstraction layer.
- The requested outcome is only to remove duplicated parsing behavior safely.
