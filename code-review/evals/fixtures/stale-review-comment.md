# Stale review comment fixture

Old review comment:

> `src/Login.tsx:18` should add `aria-label` to the icon-only submit button.

Current code:

```tsx
export function LoginSubmit() {
  return (
    <button type='submit' aria-label='Sign in'>
      <Icon name='arrow-right' aria-hidden='true' />
    </button>
  );
}
```
