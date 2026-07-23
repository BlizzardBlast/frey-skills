# Feature planning fixture

User intent: plan adding an optional `preferredName` field to profile editing. Do not implement it.

Available repository snapshot:

- `src/profile/types.ts` exports `Profile` with `id` and `fullName`.
- `src/profile/updateProfile.ts` sends `{ fullName }` to `PUT /api/profile` and parses the returned `Profile`.
- `src/profile/ProfileForm.tsx` renders and submits the `fullName` field.
- `src/profile/ProfileForm.test.tsx` covers initial rendering, successful submit, and server validation errors.
- `server/routes/profile.ts` validates `PUT /api/profile`, accepts `fullName`, persists it, and returns the updated profile.
- `server/db/profile.ts` maps database column `full_name` to API field `fullName`.
- `server/db/migrations/` contains ordered SQL migrations for profile schema changes.
- External clients also consume `PUT /api/profile` and the returned profile payload.

Constraints:

- `preferredName` must be optional.
- Existing clients that do not send or read `preferredName` must continue working.
- No unrelated profile refactor is requested.
