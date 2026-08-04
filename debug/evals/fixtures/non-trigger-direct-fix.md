# Direct-fix non-trigger fixture

User request: implement the known boundary fix now. Do not investigate it again.

```ts
export function isExpired(expiresAt: number, now: number) {
  return expiresAt < now;
}
```

Confirmed requirement: a token expiring exactly at `now` is expired, so the comparison must use `<=`.

This is a direct implementation request with an established cause and requirement, not a debugging request.
