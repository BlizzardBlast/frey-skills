# Verification failure fixture

Approved plan:

1. Change `src/rules.ts`.
2. Run `python test_runner.py`.

The edit can be applied, but the focused verification exits non-zero with a newly failing assertion caused by the change.

The skill must not return `IMPLEMENTED` or claim tests passed.
