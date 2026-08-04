# Complete plan execution fixture

Approved plan:

1. Add an optional `middleName` field to `src/profile.ts` without changing existing required fields.
2. Update `src/profile.test.ts` for profiles with and without `middleName`.
3. Run `python test_runner.py`.

Repository:

- `src/profile.ts` defines `Profile` with required `firstName` and `lastName`.
- `src/profile.test.ts` validates the existing shape.
- `test_runner.py` runs the focused tests.
- The plan is complete and no unrelated files are dirty.
