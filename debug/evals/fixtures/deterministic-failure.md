# Deterministic failure fixture

User intent: investigate why checkout crashes for an empty cart. Do not edit code.

```ts
export function total(items: number[]) {
  return items.reduce((sum, item) => sum + item);
}
```

Evidence:

- `total([2, 3])` returns `5`.
- `total([])` throws `TypeError: Reduce of empty array with no initial value`.
- The caller permits an empty cart and expects total `0`.
- No parsing, network, or database work occurs in this function.
