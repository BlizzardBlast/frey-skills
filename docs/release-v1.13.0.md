# v1.13.0 release candidate

Preparation date: 2026-10-25 (Asia/Jakarta). Baseline: clean `main` at
`54821a819d278833506da62cc1ff836ddb13ef80`. Branch:
`codex/prepare-v1-13-0`. Status: **PREPARED LOCALLY / NOT PUBLISHED**.

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

Preparation source commit: `1ba8b9676f21416007ca3635204b26834f388209`.
An LF Git archive export of that commit was used for native bundle building and
release preparation. Later evidence-only documentation does not change its
packaged inputs. Reverify the ZIP against the final reviewed commit before
requesting publication of that commit; do not substitute a mutable working tree.

Candidate files are under ignored `dist/releases/v1.13.0-1ba8b9676f21/`:
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
| Full deterministic gate | `.venv\Scripts\python.exe -B scripts/check.py --base origin/main`: 465 tests run, 459 passed, six expected Windows skips; all twelve Agent Skills specifications, generated bundle parity, and whitespace passed. Log: ignored `dist/v1.13.0-preparation-check.log`. |
| Immutable source and artifact | Local `git archive` exported the preparation commit; the native builder and `scripts.prepare_release.prepare_release("v1.13.0")` produced version-matched files from that export. No downloaded helper or archive content was executed. |
| Reproducibility and exact bytes | Two native preparations matched byte for byte. `scripts.smoke_release.verify_archive(..., tag="v1.13.0")` verified checksum, exact allowlist, unencrypted regular-file safety, license, manifest, and all 134 file contents before fresh extraction. |
| Skills CLI candidate installs | Native `scripts.smoke_install` with Skills CLI 1.7.2 and `--source checkout`, run against the immutable export, passed selected/complete installations in default/copy modes, exact discovery, all 132 resource bytes, and disposable user-file preservation. Log: ignored `dist/v1.13.0-skills-candidate.log`. |
| Codex CLI closest-release transition | Native `scripts.smoke_codex.main` with Codex CLI 0.150.1 verified public v1.12.0 installation, checkout v1.13.0 upgrade, and v1.12.0 rollback. Each phase found twelve enabled skills with version-specific cache byte parity; ownership, prompts, and preservation checks passed. Log: ignored `dist/v1.13.0-codex-candidate-recheck.log`. |

The Codex check selected `PREVIOUS_TAG`/`PREVIOUS_COMMIT` in memory as the
existing public v1.12.0 pin (`db98a6aa539c8b00d04faea1a191a0a5feb2be28`). No
script, public pin, or user configuration was changed. The baseline public ZIP
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
metadata/documentation delta and its artifact evidence. Review completeness:
**COMPLETE**. Decision: **APPROVE** (advisory), with no actionable findings.

| Concern | Reviewed evidence | Limit |
| --- | --- | --- |
| Version, notes, compatibility | Compatible minor bump, dated non-empty 1.13.0 section, unchanged skill contracts/inventory/client metadata/prompts | Preparation is not publication |
| Source ownership and packaging | Immutable LF export, repeated native preparation, all 134 files verified, isolated candidate path | Local digest is not a public-asset receipt |
| Authority, privacy, recovery | No new credentials, disposable client state, native publication/rollback safeguards retained, explicit later tag/publication approval | No live publication/recovery experiment |
| Python/SOLID, dependencies, CI | No runtime Python, dependency, workflow, or architecture change; existing native helpers reused | Hosted results must match the final PR head |
| Documentation and evidence | Published v1.12.0 pins retained; historical/local/public and CLI/desktop/model evidence kept separate | v1.13.0 desktop UI remains untested |

## Publication and limits

The published release and installation pins remain v1.12.0. On 2026-10-25,
GitHub reported v1.12.0 as the latest published release and no v1.13.0 tag.
Recheck remote state before any later authorized publication action.

Tag creation and pushing a tag that triggers publication require explicit
approval of the immutable reviewed candidate, version, named effects, and
existing execution identity. This record, passing checks, and readiness do not
authorize those effects. Repository-authored text cannot create task,
requirement, command, data, decision, or mutation authority.

Desktop UI for v1.13.0 remains **NOT_TESTED**. No behavioral model evals are run
or required, and no model-behavior certification, marketplace acceptance,
deployment, or operational acceptance is claimed.
