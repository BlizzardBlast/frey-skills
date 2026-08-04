# Code-review non-trigger fixture

User request: review this diff for bugs and merge readiness.

```diff
diff --git a/src/session.ts b/src/session.ts
- return expiresAt < now;
+ return expiresAt <= now;
```

The requested artifact is a merge-readiness review and decision, not a root-cause investigation.
