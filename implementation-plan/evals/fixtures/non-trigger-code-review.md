# Code review non-trigger fixture

User request: review this diff for merge readiness and tell me whether to approve it.

```diff
diff --git a/src/button.tsx b/src/button.tsx
+export function Action({ onClick }: { onClick: () => void }) {
+  return <div onClick={onClick}>Run</div>;
+}
```

This is a code-review request, not an implementation-planning request.
