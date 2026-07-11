# Ordinary implementation non-trigger fixture

User request: implement a one-off UI copy change without using iterative self-review.

```diff
diff --git a/src/EmptyState.tsx b/src/EmptyState.tsx
@@
-  return <p>No records.</p>;
+  return <p>No transactions yet.</p>;
```

Expected activation semantics:

- This is an ordinary implementation request, not a provided issue ledger, repeated remediation request, post-review repair, or explicit invocation.
- `iterative-self-review` must not activate.
- A response may discuss the implementation normally, but it should not create a baseline/pass ledger or start a bounded remediation loop.
