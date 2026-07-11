# Review-then-fix handoff fixture

User request: review the diff, then fix anything found.

```diff
diff --git a/src/UserMenu.tsx b/src/UserMenu.tsx
@@
+export function UserMenu({ onLogout }: { onLogout: () => void }) {
+  const logOutNow = onLogout;
+  return (
+    <div className="menu">
+      <div className="logout-button" onClick={logOutNow}>
+        Logout
+      </div>
+    </div>
+  );
+}
```

Expected review evidence:

- P2: the clickable `div` is not keyboard accessible and does not expose button semantics.
- P3: `logOutNow` adds indirection without clarity.
- The skill must not edit this fixture or source code. It should complete the review ledger first, decide `COMMENT`, and hand the remediation ledger to `iterative-self-review`.
