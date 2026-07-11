# Three-pass limit fixture

Ledger:

- `CR-P2-001`: A generated snapshot alternates property order every time the formatter and generator run in different orders.

Observed passes:

1. Formatter sorts alphabetically and generator restores schema order.
2. Schema order fixes generator check but formatter fails.
3. Formatter passes and generator fails again.

Expected behavior: stop at the default pass limit and report the unresolved tool-order conflict.
