# Clean diff fixture

User intent: add a pure formatter helper and test.

```diff
diff --git a/src/formatName.ts b/src/formatName.ts
+export function formatName(first: string, last: string): string {
+  return `${first.trim()} ${last.trim()}`.trim();
+}
diff --git a/src/formatName.test.ts b/src/formatName.test.ts
+import { formatName } from "./formatName";
+test("trims and joins names", () => {
+  expect(formatName(" Ada ", " Lovelace ")).toBe("Ada Lovelace");
+});
```

Requested concerns: correctness, tests.
