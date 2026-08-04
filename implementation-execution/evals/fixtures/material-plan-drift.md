# Material plan drift fixture

Approved plan:

1. Rename an internal mapper while preserving the public JSON field `accountNumber`.
2. Run contract tests.

Repository evidence now shows the only available implementation requires changing the public JSON field to `acctNo`. No compatibility alias or versioned contract exists.

Execution must stop rather than change the contract.
