# Debugging Quality Checklist

Run this before finalizing any `debug` investigation.

## Scope and baseline

- [ ] The investigation mode is stated.
- [ ] The exact symptom and expected behavior are explicit.
- [ ] Environment, version, frequency, and first known occurrence are captured when available.
- [ ] Reproduction is labeled as reproduced, not reproduced, unavailable, or not required because equivalent evidence is sufficient.
- [ ] Existing dirty work or partial fixes are distinguished from the original symptom.

## Evidence integrity

- [ ] Observations, user reports, inferences, and assumptions are distinguishable.
- [ ] Claims are grounded in inspected code, configs, tests, logs, traces, commands, documentation, or history.
- [ ] No command, reproduction, path, value, log, or test result is invented.
- [ ] The investigation follows the causal chain to the earliest meaningful divergence.
- [ ] The final exception or failed assertion is not mislabeled as the root cause without causal evidence.

## Hypothesis integrity

- [ ] Material competing hypotheses appear in the ledger.
- [ ] Every hypothesis predicts observable behavior.
- [ ] Supporting and contradicting evidence are recorded.
- [ ] Discriminating checks separate plausible alternatives where possible.
- [ ] Rejected hypotheses remain visible.
- [ ] `CONFIRMED` is used only when the causal chain is established and alternatives are immaterial.

## Completeness and status

- [ ] Missing reproduction, credentials, telemetry, environment parity, or external access is reflected in completeness.
- [ ] `CONFIRMED` root-cause status is used only with `COMPLETE` investigation.
- [ ] `LIKELY` is paired with `PARTIAL` and names the missing confirmation.
- [ ] `BLOCKED` investigation maps to `UNRESOLVED`.
- [ ] `NOT_A_DEFECT` explains why the symptom occurs and which contract or boundary supports the conclusion.

## Handoff and safety

- [ ] The recommended next workflow matches the user's requested artifact.
- [ ] Post-fix verification targets the causal behavior, not merely a broad test run.
- [ ] No source, config, generated artifact, lockfile, database, branch, issue, PR, deployment, or external system was mutated.
- [ ] No speculative fix was applied to manufacture confirmation.
