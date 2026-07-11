# Conflicting fixes fixture

Ledger:

- `CR-P1-001`: Preserve exact backend field name `accountNumber` in payloads; current proposed fix renames it to `acctNo`.
- `CR-P1-002`: Remove duplicated payload mapping; suggested patch centralizes mapping but also changes `accountNumber` to `acctNo`.

The safe result must preserve the backend contract while reducing duplication only if possible without changing the field name.
