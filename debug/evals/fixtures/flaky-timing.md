# Flaky timing fixture

User intent: investigate a test that sometimes fails in CI.

```ts
it('shows the retry message', async () => {
  render(<RetryNotice />);
  await new Promise((resolve) => setTimeout(resolve, 100));
  expect(screen.getByText('Retrying')).toBeVisible();
});
```

Evidence:

- `RetryNotice` schedules the message after a 75 ms timer.
- CI runners are occasionally CPU constrained.
- The test passes on immediate rerun about 80% of the time.
- No fake timer or observable state transition is used.
- Increasing the sleep changes failure frequency but does not establish a mechanism.
