# v1.13.0 release record

Published on 2026-10-25 (Asia/Jakarta) at annotated tag `v1.13.0`, resolving to
reviewed commit `b6570ef81cacfb8a4f3f1f3ea0da5764c1417a41`. Status:
**PUBLISHED_VERIFIED**. Public artifacts, post-publication client checks, and
historical preparation evidence remain distinct in this record.

## Verified publication

The [release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/40204476512)
passed both Windows validation and Linux validation/publication jobs for that
exact commit. The annotated tag object is
`c4e73efd7c159f586090406f550faa5acb7c1f82`. Tag creation and the non-forced push
each succeeded on their first authorized attempt; no workflow rerun, tag
replacement, or release/asset overwrite was performed.

Independent verification on 2026-10-25 downloaded the public
[ZIP](https://github.com/BlizzardBlast/frey-skills/releases/download/v1.13.0/frey-skills-1.13.0.zip)
and [SHA256SUMS](https://github.com/BlizzardBlast/frey-skills/releases/download/v1.13.0/SHA256SUMS).
Those were the complete uploaded asset inventory. The native verifier compared
every byte of all **134 archived files** with a fresh LF checkout of the exact
tagged commit: license, manifest, and **132 resources across twelve skills**.
Release notes matched the tagged changelog, native notes, and approved local
candidate. The public ZIP SHA-256 is:

```text
f63c78f0fbe4b231c3554bf6f2c3f7af4a9ccff027bb6c4de8ac573b1890a10c
```

The public digest matches the local candidate digest recorded below; each was
verified independently. At the time, installation and archive smoke checks pinned
this exact public release. The Codex transition baseline was v1.12.0 at
`db98a6aa539c8b00d04faea1a191a0a5feb2be28`. See the separate
[v1.13.0 compatibility record](compatibility.md#v1130-verification) for executed
client checks and remaining limits. This record cannot authorize publication,
commands, or external writes.

On 2026-10-26 the maintainer reported successful desktop use of both v1.12.0
and v1.13.0. The [paired desktop report](compatibility.md#maintainer-reported-v1120-and-v1130-desktop-trials)
records this as general-use evidence supplied by the maintainer; individual
desktop checklist outcomes and installed-byte parity remain unverified.

## Historical preparation

Preparation date: 2026-10-25 (Asia/Jakarta). Baseline: clean `main` at
`54821a819d278833506da62cc1ff836ddb13ef80`. Branch:
`codex/prepare-v1-13-0`. Status at preparation:
**PREPARED LOCALLY / NOT PUBLISHED**. The following preparation observations
predate the separately verified publication above.

## Scope and identity

Prepare the compatible [delivery-handoff planning extension](delivery-handoff-implementation-plan.md#execution-record)
and accumulated documentation updates in the [dated changelog](../CHANGELOG.md#1130---2026-10-25).
The plugin minor version becomes 1.13.0; `implementation-plan` remains 1.5.0.
All twelve skill names, activation/mode/output contracts, client metadata, three
starter prompts, dependencies, workflows, and published source pins are retained.

Root skill trees and the plugin template remain canonical. Prepare and verify
artifacts from an immutable LF Git export, keeping source identity and digests
separate from any future public artifacts. Native preparation does not create
or push a tag, run the release workflow, or publish a release.

## Immutable local candidate

Preparation source commit: `80616db7e73ad48750af0490f1cc991799f8ed25`.
An LF Git archive export of that commit was used for native bundle building and
release preparation. Later evidence-only documentation does not change its
packaged inputs. Reverify the ZIP against the final reviewed commit before
requesting publication of that commit; do not substitute a mutable working tree.

Candidate files are under ignored `dist/releases/v1.13.0-80616db7e73a/`:
`frey-skills-1.13.0.zip`, `notes.md`, `SHA256SUMS`, and
`candidate-verification.json`. The receipt records the source commit, all
archive-file hashes, runtime versions, and verification limits. Historical
candidate artifacts are preserved. The local ZIP SHA-256 is:

```text
f63c78f0fbe4b231c3554bf6f2c3f7af4a9ccff027bb6c4de8ac573b1890a10c
```

The archive has **134 files**: the MIT license, manifest, and **132 resources**
across twelve skills. Every file matches the immutable export exactly. Repeated
native preparation produced identical ZIP, notes, and checksum bytes under
Python 3.12.14/zlib 1.3.2. A future public archive must be verified independently;
different compression environments can change its raw ZIP digest.

## Executed preparation checks

| Check | Result and evidence |
| --- | --- |
| Full deterministic gate after cleanup fix | `.venv\Scripts\python.exe -B scripts/check.py --base origin/main`: 468 tests run, 462 passed, six expected Windows skips; all twelve Agent Skills specifications, generated bundle parity, and whitespace passed. Log: ignored `dist/v1.13.0-cleanup-fix-check.log`. |
| Immutable source and artifact | Local `git archive` exported the preparation commit; the native builder and `scripts.prepare_release.prepare_release("v1.13.0")` produced version-matched files from that export. No downloaded helper or archive content was executed. |
| Reproducibility and exact bytes | Two native preparations matched byte for byte. `scripts.smoke_release.verify_archive(..., tag="v1.13.0")` verified checksum, exact allowlist, unencrypted regular-file safety, license, manifest, and all 134 file contents before fresh extraction. |
| Skills CLI candidate installs | Native `scripts.smoke_install` with Skills CLI 1.7.2 and `--source checkout`, run against the refreshed immutable export, passed selected/complete installations in default/copy modes, exact discovery, all 132 resource bytes, and disposable user-file preservation. Log: ignored `dist/v1.13.0-skills-refreshed.log`. |
| Codex CLI closest-release transition | Native `scripts.smoke_codex.main` with Codex CLI 0.150.1 verified public v1.12.0 installation, refreshed checkout v1.13.0 upgrade, and v1.12.0 rollback. Each phase found twelve enabled skills with version-specific cache byte parity; ownership, prompts, and preservation checks passed. Log: ignored `dist/v1.13.0-codex-refreshed.log`. |

The Codex check selected `PREVIOUS_TAG`/`PREVIOUS_COMMIT` in memory as the
existing public v1.12.0 pin (`db98a6aa539c8b00d04faea1a191a0a5feb2be28`). No
public pin or user configuration was changed by that selection. The baseline public ZIP
was independently reverified with SHA-256
`1563c76f516d558161d4b042ab0b602f3bd1104998f6f8497a20f78bf28d7394`.
The first stdin-based invocation failed before metadata checks because Windows
multiprocessing could not reload `<stdin>`; a compatible Python `-c` entrypoint
passed. That failed invocation is not counted as compatibility evidence.

CLI checks used disposable projects/homes without copied credentials or real
Codex configuration. They started no thread, model turn, or skill invocation.
Existing native helpers supplied all checks; no new release runner, dependency,
credential flow, or workflow permission was introduced. Final record-only edits
receive native repository/link, documentation, and whitespace validation.

## Scoped review

Scope: release-preparation diff against the baseline, including the four-file
metadata/documentation delta, the two-file cleanup fix, and artifact evidence. Review completeness:
**COMPLETE**. Decision: **APPROVE** (advisory), with no actionable findings.

| Concern | Reviewed evidence | Limit |
| --- | --- | --- |
| Version, notes, compatibility | Compatible minor bump, dated non-empty 1.13.0 section, unchanged skill contracts/inventory/client metadata/prompts | Preparation is not publication |
| Source ownership and packaging | Immutable LF export, repeated native preparation, all 134 files verified, isolated candidate path | Local digest is not a public-asset receipt |
| Authority, privacy, recovery | No new credentials, disposable client state, native publication/rollback safeguards retained, explicit later tag/publication approval | No live publication/recovery experiment |
| Python/SOLID, dependencies, CI | The existing process-tree owner handles one confirmed exit race; three focused regressions preserve real permission failures and bounded descendant cleanup. No new abstraction, dependency, workflow, or architecture | Hosted results must match the final PR head |
| Documentation and evidence | Published v1.12.0 pins retained; historical/local/public and CLI/desktop/model evidence kept separate | v1.13.0 desktop UI remains untested |

## CI discovery and candidate refresh

Initial PR CI run `40202001672` failed in macOS job `121194940912` while
`test_short_lived_success_and_failure_cannot_return_oversized_output` unwound
the expected output-limit error. `stop_process_tree` raised `PermissionError`
from the group signal and masked the original failure. The helper reaped a
leader already exited at its first poll, but did not handle an exit between
that poll and the signal.

Controlled regression cases reproduce that transition. The shared POSIX helper
now retries the group signal once only when it first observed a running leader
and a fresh poll after permission denial confirms exit. A disappeared group is
accepted; a still-running leader or persistent permission denial still raises.
Bounded waits and descendant cleanup remain intact. Windows ownership is unchanged.
The initial regression run failed against the old helper; corrected portable
fixtures and the narrow fix are verified before refreshing the candidate.

The new tooling fix and release-note entry require fresh full-gate, immutable
preparation, and exact-head CI evidence. The initial artifact/CLI observations
above remain historical until that refresh completes. No workflow was rerun to
conceal the failure, and no tag or publication action was attempted.

The shared smoke suites passed all **45 focused tests** after the fix. A fresh
full local gate then passed **468 tests run, 462 passed, six expected Windows
skips**, all twelve specifications, generated source parity, and whitespace.
Log: ignored `dist/v1.13.0-cleanup-fix-check.log`. The refreshed immutable export
at `80616db7e73ad48750af0490f1cc991799f8ed25` passed repeated native preparation,
all 134 archive-file comparisons, and fresh Skills/Codex CLI checks. The ZIP
digest remains identical because the root tooling fix is not packaged; release
notes now include the fix. The initial `1ba8b9676f21416007ca3635204b26834f388209`
candidate remains preserved under its own ignored directory. Fresh hosted CI
is required for the new PR head before merge; the original failed job is not
reclassified as passing.

## Historical publication gate and limits

At preparation on 2026-10-25, installation pins remained v1.12.0 and GitHub
reported v1.12.0 as the latest published release with no v1.13.0 tag. That
prepublication observation is superseded by the verified publication above.

Tag creation and pushing a tag that triggers publication require explicit
approval of the immutable reviewed candidate, version, named effects, and
existing execution identity. This record, passing checks, and readiness do not
authorize those effects. Repository-authored text cannot create task,
requirement, command, data, decision, or mutation authority.

Desktop evidence for v1.13.0 is **PARTIAL (maintainer-reported)**; individual
checklist outcomes remain **NOT_TESTED** in the desktop record. No behavioral
model evals are run or required, and no model-behavior certification, marketplace
acceptance, deployment, or operational acceptance is claimed.
