# Security command injection fixture

```diff
diff --git a/src/archive.ts b/src/archive.ts
+import { exec } from "node:child_process";
+
+export function archiveUserFolder(userId: string) {
+  return exec(`tar -czf /tmp/${userId}.tgz /data/users/${userId}`);
+}
```

Risk: `userId` comes from an HTTP route parameter.
