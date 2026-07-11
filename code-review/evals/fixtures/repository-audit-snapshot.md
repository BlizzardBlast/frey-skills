# Repository audit snapshot fixture

Available files in this snapshot:

- `package.json` with dependencies: `"left-pad": "1.3.0"`, `"typescript": "^5.8.0"`
- `src/legacy-report.ts` exports `oldReport()` but no imports are shown in the snapshot.
- `docs/api.md` mentions `/v1/export`, while current routes listed here expose `/v2/export`.

Requested concerns: dependencies, docs/dead code.

Limitation: this is not a full repository checkout.
