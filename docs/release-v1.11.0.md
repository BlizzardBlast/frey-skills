# v1.11.0 candidate release record

Preparation date: 2026-10-20. Status: **PREPARING**, not published.
Baseline: `ce9fe624a88842cddc0ccb344e9816465ba23013` on `main`.

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

## Preparation and verification plan

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

Pending candidate preparation. Evidence will distinguish the exact source
commit, local archive digest, final PR head, hosted CI, public artifacts, and
desktop observations. Historical v1.10.0 results do not certify this candidate.

## Limits and handoff

The intended publication target is a GitHub Release for Frey Skills. No v1.11.0
tag, GitHub release, or public archive is created by preparation. A future
release workflow rebuilds assets from its reviewed tag commit; verify those
downloaded public bytes independently before updating installation/smoke pins.

Desktop UI discovery, restart persistence, and upgrade/rollback on Windows,
macOS, and Linux are **NOT_TESTED** for v1.11.0. Local CLI metadata checks and
hosted matrices have separate coverage. Behavioral model evals are not run or
required, and no model-behavior certification is claimed.

For publication, the maintainer must identify the reviewed merged commit and
authorize the version and release effects under [the release procedure](../RELEASING.md).
An assessment of a PR head does not automatically apply to a different merge
commit; recheck source/artifact identity, required CI, and unresolved holds.
