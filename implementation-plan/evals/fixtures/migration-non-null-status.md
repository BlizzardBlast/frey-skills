# Database migration planning fixture

User intent: plan making `users.status` non-null in production.

Repository evidence:

- `db/schema.sql` defines `users.status VARCHAR(32) NULL`.
- `src/users/readUser.ts` already treats missing status as `"pending"`.
- `src/users/createUser.ts` explicitly writes a non-null status for new users.
- `db/migrations/` contains timestamped SQL migrations.
- Production contains historical rows where `users.status IS NULL`.
- Deployments are rolling: old and new application instances can coexist for several minutes.
- The previous application version may still update other user columns, but repository evidence shows it does not write `status` during those updates.

Constraints:

- Avoid downtime.
- Preserve compatibility during the rolling deployment.
- Provide a rollback story for application changes and identify any database step that is not safely reversible.
