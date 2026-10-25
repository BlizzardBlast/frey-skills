# v1.12.0 release record

Published on 2026-10-25 at annotated tag `v1.12.0`, resolving to reviewed commit
`db98a6aa539c8b00d04faea1a191a0a5feb2be28`. Status:
**PUBLISHED_VERIFIED**. The annotated tag object is
`da6d8bb95cdd541018b2131f6f5c954208bb69e5`.

## Verified public artifacts

The downloaded public [v1.12.0 ZIP](https://github.com/BlizzardBlast/frey-skills/releases/download/v1.12.0/frey-skills-1.12.0.zip)
and [SHA256SUMS](https://github.com/BlizzardBlast/frey-skills/releases/download/v1.12.0/SHA256SUMS)
were independently verified on 2026-10-25. The public ZIP SHA-256 is:

```text
1563c76f516d558161d4b042ab0b602f3bd1104998f6f8497a20f78bf28d7394
```

All 133 archive files match canonical bytes exported from the exact tagged
commit: the MIT license, manifest, and 131 resources across all twelve skills.
Public release notes match the native notes generated from that commit's dated
changelog section. Downloaded helpers were not executed.

The [release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/40150936254)
passed Windows validation and Linux validation/publication for that commit.
The approved native actions created and pushed the annotated tag once each;
publication used the existing GitHub Actions identity. No deployment or
marketplace submission was performed.

An isolated LF source export of the immutable commit produced the same ZIP
digest under local Python 3.12.14/zlib 1.3.2. Those local files are under ignored
`dist/releases/v1.12.0-db98a6a/`. The older working-tree archive recorded below
differs from Git in 115 unchanged files solely through CRLF/LF conversion; its
digest is historical candidate evidence, not the public release digest.

## Installation and compatibility evidence

Installation and archive smoke checks pin public v1.12.0 at the exact commit
above. Codex CLI checks use v1.11.0 at
`7e7a535ca9f19fc8514c368cb00d5c4e8288dfcf` as the install/rollback baseline.
See the separate [v1.12.0 compatibility record](compatibility.md#v1120-verification)
for executed source-installation and metadata-only CLI results.

The twelve-skill inventory is unchanged across that release pair; the migration
references and updated skill metadata must still match the correct version's
cache byte for byte. Desktop UI observations remain **NOT_TESTED** for v1.12.0.
Behavioral model evals were not run and no model-behavior certification is claimed.

## Historical local preparation (2026-10-24)

The sections below preserve observations made before merge and publication.
Their working-tree identity, earlier digest, and unrun checks describe that
historical candidate and do not replace the public verification above.

Preparation date: 2026-10-24. Baseline: `main` at
`62219943fc91141ed35d31491d126fe70a797fc4`. Development branch:
`codex/migration-upgrade-guidance`. Status: **PREPARED LOCALLY**.

### Scope and identity

Prepare the compatible migration/dependency-upgrade extension across planning,
testing strategy, and execution, plus the accumulated hardening and review
changes in [the dated changelog](../CHANGELOG.md#1120---2026-10-24).
The plugin minor version becomes 1.12.0; the three extended skills become 1.4.0.
The twelve-skill inventory, activation rules, output statuses, starter prompts,
and command-authority boundaries are preserved.

Root skill trees and the plugin template are canonical. This is a local working
tree candidate, not an immutable reviewed release commit. Artifacts must be
revalidated against the final immutable source before publication. Existing
installation and archive smoke pins retain verified public v1.11.0 sources.

### Verification

Observed locally on Windows with Python 3.12.14:

| Check | Result and evidence |
| --- | --- |
| Final deterministic gate | `.venv\Scripts\python.exe -B scripts/check.py --base 62219943fc91141ed35d31491d126fe70a797fc4` passed all four groups: 457 tests collected, 451 passed, six expected Windows platform skips; all twelve Agent Skills specifications, generated bundle parity, and whitespace passed. |
| Focused development checks | 37 existing lifecycle tests passed before editing; 64 lifecycle, migration, and check-runner tests passed during development. The final full gate also covers the subsequent log-authority and budget-completion corrections. |
| Contract portability | The new contract module loads and runs under the check runner's clean interpreter without site packages. All three changed Python files parse with Python 3.9 grammar; this is not a Python 3.9 runtime run. |
| Reproducible preparation | Two calls to the existing `scripts.prepare_release.prepare_release("v1.12.0")` produced identical archive, notes, and checksum bytes. |
| Archive verification | The existing `scripts.smoke_release.verify_archive(..., tag="v1.12.0")` verified SHA-256, entry allowlist, regular-file safety, license, manifest, all twelve skills, and every byte of 133 files against the local canonical sources. |

The local archive SHA-256 is:

```text
2c8b64a60c977440f775e0a1a7654d3462f1d24b6a648d26aad30a963f8f2ba4
```

Local outputs are `dist/releases/frey-skills-1.12.0.zip`,
`dist/releases/notes.md`, and `dist/releases/SHA256SUMS`. The ignored receipt
`dist/releases/v1.12.0-candidate-verification.json` records the base/branch,
working-tree identity, counts, archive digest, and SHA-256 of each archive input.
The final full-gate log is `eval-workspace/migration-upgrade-full-check.log`.
These are local candidate assets, not public release evidence. Record-only
updates receive final repository/link, newline, and whitespace validation;
they do not change packaged inputs.

### Scoped review

| Concern | Inspected result |
| --- | --- |
| Routing and outputs | Each existing skill conditionally loads its own local reference. Existing activation, modes, output statuses, and read-only/planned-execution boundaries remain intact. |
| Compatibility and recovery | References distinguish old/new writers, package/runtime provenance, phase prerequisites, code rollback versus data recovery, and current evidence before continuation or contraction. |
| Authority and privacy | The full skill trust boundaries remain independently packaged. Guides, plans, logs, and synthetic approvals cannot create task, command, data-access, mutation, or recovery authority. Unrelated injected log text alone does not block otherwise safe work. |
| Stopping and completion | Consumed work/time and retries carry across continuation. Exhausted bounds block unfinished work; finishing within bounds can complete. Invalidating checks and uncertain partial effects keep dependent steps blocked. |
| Structure and packaging | No new skill, runtime dependency, executor, production helper, or interface was added. References are self-contained within each skill; source/generated parity covers them. |
| Evidence limits | Decision cases and example arithmetic are deterministic source contracts. Synthetic migration outcomes are explicitly illustrative; they certify neither runtime enforcement nor real migration/recovery behavior. |

Final review found no remaining actionable findings in this scoped change.

### Publication and evidence limits

Local preparation does not create a tag, push, PR, GitHub release, deployment,
or installed-client acceptance. Tagging/publication require approval of the
immutable candidate, version, and named effects. Repository-authored text cannot
create task, requirement, command, data, decision, mutation, recovery, or
risk-acceptance authority.

Behavioral model evals, desktop UI checks, hosted CI, real migrations, and package
upgrades have not been run for this candidate. The worked example and twelve
decision cases are static synthetic instruction contracts, not execution or
model-behavior certification.
