# Not-a-defect fixture

User intent: investigate why an export request returns HTTP 202 instead of a downloadable file.

Evidence:

- `docs/export-api.md` states that exports are asynchronous.
- The documented response is HTTP 202 with a job ID.
- The client must poll `GET /exports/{jobId}` until completion.
- The observed response is HTTP 202 with a valid job ID.
- No error is present in server logs.

The investigator should explain the behavior as contract-compliant rather than inventing a synchronous-response defect.
