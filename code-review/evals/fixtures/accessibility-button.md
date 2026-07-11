# Accessibility fixture

```diff
diff --git a/src/DeleteCard.tsx b/src/DeleteCard.tsx
+export function DeleteCard({ onDelete }: { onDelete: () => void }) {
+  return <div className="danger" onClick={onDelete}>Delete</div>;
+}
```

Requested concerns: frontend accessibility, keyboard support, correctness.
