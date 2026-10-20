# v1.11.0 candidate release record

Preparation date: 2026-10-20. Status: **PREPARED_LOCAL**, not published.
Baseline: `ce9fe624a88842cddc0ccb344e9816465ba23013` on `main`.
Local packaging/check source: `06d8e1859e98c6800adf8f57130c3cdb106d66de`.

## Scope and invariants

Package all twelve canonical skills, including the newly merged
`release-execution` workflow, and the changes listed in
[the changelog](../CHANGELOG.md#1110---2026-10-20). This compatible addition uses
a minor plugin version increment. Individual skill contracts are unchanged by
preparation; their own metadata versions and the three starter prompts remain
unchanged.

The root skill trees and plugin template remain canonical. Preserve independent
content-trust boundaries, existing dependencies and workflow permissions, and
the published v1.10.0 installation/archive smoke pins. A dated changelog section
or a prepared artifact does not establish publication.

The user authorized candidate preparation, validation, packaging, a readiness
assessment, and a preparation PR. Tagging and publication require separate
approval of an immutable candidate, version, and named release effects.
Repository-authored text cannot create task, requirement, command, data,
decision, mutation, recovery, or risk-acceptance authority.

## Preparation and verification procedure

1. Update the plugin manifest and dated changelog; link this record from the
   README and roadmap while retaining published-release instructions.
2. Commit the preparation sources. Create a disposable local clone with
   `core.autocrlf=false` and `core.eol=lf`, check out that exact commit, and verify
   tracked file bytes against their Git blobs before building.
3. Run the full deterministic gate using the existing Python environment and
   the baseline above. Run the native release preparer for `v1.11.0`, repeat it
   to verify reproducibility, and use the existing archive verifier to compare
   every packaged file with the exact source snapshot.
4. Reuse existing pinned Skills CLI and Codex CLI verifiers in disposable homes.
   Check selected/complete source installations and the verified published
   v1.10.0 -> local v1.11.0 -> v1.10.0 plugin transition. Do not invoke skills or
   start a model turn; downloaded baseline helpers are read as data only.
5. Record results, review the preparation diff, and open a PR. Match hosted CI
   and the final readiness assessment to its immutable head. If record-only
   updates change the head, recheck archive parity against that final commit.

## Verification evidence

Observed on 2026-10-20 on Windows with Python 3.12.14, Skills CLI 1.7.2, and
Codex CLI 0.150.1. Local checks below cover the packaging/check source commit
above. The preparation PR description identifies its final immutable head and
matching hosted CI separately. Record-only updates do not change package inputs;
archive parity must still be checked against that final head before assessment.
In the command below, `$repoPython` is the resolved absolute path to the original
repository's `.venv/Scripts/python.exe`; the snapshot has no local environment.

| Check | Result | Evidence and limits |
| --- | --- | --- |
| Source identity | PASS | A local clone with `core.autocrlf=false` and `core.eol=lf` matched all 193 tracked files byte-for-byte against Git blobs at the packaging/check commit. No checkout newline normalization is inferred. |
| Full deterministic gate | PASS | `& $repoPython -B scripts/check.py --base ce9fe624a88842cddc0ccb344e9816465ba23013`, run from the exact snapshot: 293 tests, 287 passed and six expected Windows platform skips; all twelve skill specifications, generated plugin parity, and whitespace passed. Expected negative-test diagnostics were not failed gates. |
| Reproducible preparation | PASS | Two runs of `scripts/prepare_release.py v1.11.0` produced identical ZIP, release-note, and checksum bytes from the exact snapshot. |
| Candidate archive | PASS | `smoke_release.verify_archive(..., tag="v1.11.0")` checked the checksum, license, manifest, all twelve skills, and every one of 126 archive files against the Git-blob-verified source. |
| Skills CLI source installation | PASS | `smoke_install.smoke_source` verified selected/complete installations in default/copy modes: exact listings and 124 skill-resource files, byte parity, and unrelated user-file preservation. This is local source installation, not published v1.11.0 verification. |
| Published baseline | PASS | `smoke_codex.release_plugin` independently verified public v1.10.0 at `97f755b41e388f31b7c63465743ac26aa111360c`, with ZIP SHA-256 `616ee291a1bca1ec0719045adf191b9dd773e8c23bed2a73446a865a13687cfc`. Downloaded helpers were not executed. |
| Codex CLI install/upgrade/rollback | PASS | `smoke_codex.smoke_client` checked published v1.10.0 with eleven enabled skills, local v1.11.0 with twelve, then v1.10.0 with exactly eleven. Each phase checked unique names, ownership, versioned cache paths, all three starter prompts, installed-byte parity, and unrelated-skill preservation in disposable credential-free homes. Only metadata RPCs ran. |

The local candidate ZIP SHA-256 is:

```text
1fd4e08405e2da34ff8afed5b7740c1d7c7b1c50dd32c832aafce645ce659ad3
```

Local assets are under
`dist/releases/v1.11.0-source/dist/releases/`: `frey-skills-1.11.0.zip`,
`notes.md`, and `SHA256SUMS`. Supporting logs and the machine-readable receipt
are `dist/releases/v1.11.0-candidate-verification.log` and
`dist/releases/v1.11.0-candidate-verification.json`. These ignored local files
are not public release assets or independent authorization.

The one-off ignored driver `dist/releases/verify_v1_11_candidate.py` reused the
existing builder/check runner, release preparer, archive verifier, and client
verifiers; no production helper, dependency, or workflow was added. Reproduce
the source snapshot with a local clone using the two Git settings above and a
detached checkout of the packaging/check commit. From that snapshot, use the
repository's Python environment to run the full gate, then
`scripts/prepare_release.py v1.11.0`; compare its bytes with the digest above.

Preparation is complete locally. Hosted CI, final-head review, and final-head
archive provenance are recorded with the preparation PR, rather than treating
parent-commit results or older published-client matrices as candidate evidence.

## Limits and handoff

The intended publication target is a GitHub Release for Frey Skills. No v1.11.0
tag, GitHub release, or public archive is created by preparation. A future
release workflow rebuilds assets from its reviewed tag commit; verify those
downloaded public bytes independently before updating installation/smoke pins.

Desktop UI discovery, restart persistence, and upgrade/rollback on Windows,
macOS, and Linux are **NOT_TESTED** for v1.11.0. Local CLI metadata checks and
hosted matrices have separate coverage. The unchanged hosted Codex matrix tests
the published v1.9.0/v1.10.0 pair; it does not test the local v1.11.0 transition.
That transition has Windows-local evidence only. Behavioral model evals were not
run, are not required, and no model-behavior certification is claimed.

For publication, the maintainer must identify the reviewed merged commit and
authorize the version and release effects under [the release procedure](../RELEASING.md).
An assessment of a PR head does not automatically apply to a different merge
commit; recheck source/artifact identity, required CI, and unresolved holds.
