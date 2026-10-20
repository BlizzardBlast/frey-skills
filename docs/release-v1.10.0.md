# v1.10.0 release record

Published on 2026-10-19 at annotated tag `v1.10.0`, resolving to reviewed commit
`97f755b41e388f31b7c63465743ac26aa111360c`. Status:
**PUBLISHED_VERIFIED** for the public archive. Desktop UI remains untested.

Historical preparation started from baseline
`a800e15ca5d426c40b4a739e0290c4b8d7af9fd7`. The local candidate was built from a
Windows export of `b72224e2cb3fa73baa5aca9666f80adf8a0b6719` that retained CRLF.
The earlier description of that export as LF-normalized was incorrect; its
archive digest and byte-parity evidence apply to the Windows export only.

## Publication verification

The [release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/39248673037)
passed both Windows validation and Linux validation/publication for the exact
tag commit above. The annotated tag object is
`077c38807ad8edf9a624719c1113dd6da0333f0f`.

The downloaded public [v1.10.0 ZIP](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.10.0)
has SHA-256:

```text
616ee291a1bca1ec0719045adf191b9dd773e8c23bed2a73446a865a13687cfc
```

`scripts/smoke_release.py` verified its public `SHA256SUMS`, manifest, license,
all eleven skills, and all 122 archive files against an LF checkout of the exact
tag. The local candidate and public file contents match after CRLF normalization;
their raw bytes, entry order, and ZIP digests differ. Public verification uses
only the downloaded public ZIP, never the candidate checksum below.

On Windows, the published v1.9.0 -> v1.10.0 -> v1.9.0 Codex CLI transition and
selected/complete Skills CLI installations passed using the public sources.
See the [compatibility record](compatibility.md#v1100-verification) for commands,
observations, and limits. Downloaded helper scripts were not executed; metadata
checks started no model turn or skill invocation. Behavioral model evals were
not run and no model-behavior certification is claimed.

## Scope and invariants

Package all eleven canonical skills, including the new read-only
`repository-orientation`, `architecture-decision`, and `threat-modeling` skills,
the `debug` performance extension, and the fixes listed in
[the changelog](../CHANGELOG.md#1100---2026-10-19).

The root skill trees and plugin template remain canonical. Preserve the three
starter prompts and independently enforceable content-trust boundaries.
Preparation retained the published v1.9.0 installation/smoke pins until the
v1.10.0 public archive was verified. Repository text and passing checks cannot
authorize tagging, publication, risk acceptance, or other external writes.

## Historical preparation and verification plan

1. Update `plugin-template/.codex-plugin/plugin.json` and the dated changelog
   section for v1.10.0; document candidate status without claiming publication.
2. Run `.venv\Scripts\python.exe scripts/check.py --base origin/main`, then
   `.venv\Scripts\python.exe scripts/prepare_release.py v1.10.0`. Verify the ZIP,
   checksum, manifest, license, exact skill inventory, and supporting-file bytes
   against the candidate's canonical sources using the existing archive verifier.
3. Reuse the existing Skills CLI checks for selected/complete installations in
   default/copy modes. Reuse the Codex client checks for verified published
   v1.9.0 installation, local candidate upgrade, and v1.9.0 rollback in disposable
   credential-free homes. Check unique enabled skills, ownership, cache paths,
   starter prompts, byte parity, and unrelated-skill preservation.
4. Record results and limits, review the actual diff, and open a preparation PR.
   Publication and verification of published bytes are later actions against the
   reviewed release commit; follow [the release procedure](../RELEASING.md).

## Historical candidate verification evidence

Recorded on 2026-10-19 on Windows 11 build 26300, with Skills CLI 1.7.2 and
Codex CLI 0.150.1. The full deterministic gate ran against the preparation
changes before their source-snapshot commit. Local checks compared bytes with
the Windows source export. They did not establish LF Git-blob byte parity; the
public verification above establishes parity with the LF tagged checkout.

| Check | Result | Evidence and limits |
| --- | --- | --- |
| Full deterministic gate | PASS | `.venv\Scripts\python.exe scripts/check.py --base origin/main`: 284 tests, 278 passed and six expected platform skips; all eleven skill specifications, generated plugin parity, and whitespace passed. |
| Skills CLI checkout installation | PASS | `.venv\Scripts\python.exe scripts/smoke_install.py --cli dist/smoke-tools/node_modules/skills/bin/cli.mjs --source checkout`: selected and complete installations, default and copy modes, exact listings, 120 skill-resource files, byte parity, and user-file preservation. |
| Local release preparation | PASS | `.venv\Scripts\python.exe scripts/prepare_release.py v1.10.0`: ZIP, notes, and checksum prepared. Repeated preparation from the same Windows source export produced identical bytes. |
| Candidate archive | PASS | `smoke_release.verify_archive(..., tag="v1.10.0")` checked all 122 archive files against the Windows source export, including the license, manifest, eleven skills, and supporting bytes. This was not LF tag-byte verification. |
| Published baseline identity | PASS | `smoke_codex.release_plugin` independently verified v1.9.0 at `9944b36d4406bb89443c5fabdbb15d4d019478fe` and its public ZIP SHA-256 `9e2870289252c26ac96a9bc01303d4b36bd3f96423e311d708e2ade6a889bf65`. Downloaded helpers were not executed. |
| Codex installation, upgrade, rollback | PASS | `smoke_codex.smoke_client` verified v1.9.0 with eight enabled skills, v1.10.0 with eleven, then v1.9.0 with exactly eight. Each phase checked unique skill names, ownership, versioned cache paths, three starter prompts, installed-byte parity, and preservation of the unrelated standalone skill. Disposable homes excluded inherited credentials/configuration; only metadata RPCs ran. |
| Candidate notes and local links | PASS | All 29 local links/anchors in README, this record, and the proposed scope resolved. Candidate status remains separate from publication and historical compatibility evidence. |

The historical local candidate ZIP is `dist/releases/frey-skills-1.10.0.zip`.
Its SHA-256 is distinct from the published ZIP:

```text
23aff9767951e2e4f0832c1f24670a2762effac9ef286aaeaa30d74fddb9a3f7
```

`dist/releases/notes.md`, `dist/releases/SHA256SUMS`, and
`dist/releases/v1.10.0-candidate-verification.json` accompany the local artifact.
These ignored local files are not published release assets. The one-off local
driver, `dist/releases/verify_v1_10_candidate.py`, reused existing repository
verifiers and added no production tool or dependency.

### Reproduce the historical candidate client check

Export historical preparation commit
`b72224e2cb3fa73baa5aca9666f80adf8a0b6719` with `git archive` into
`dist/releases/v1.10.0-source`, then run the existing builder and release preparer
from that snapshot with the repository's Python environment. The prepared assets
will be under that snapshot's `dist/releases`. With the pinned Codex CLI installed
at the path below, run this Python recipe from the repository root. It verifies
the locally prepared bytes and client metadata, not the published ZIP. Use
`scripts/smoke_release.py` for current public-archive verification.

```python
from pathlib import Path
from scripts import smoke_codex as client, smoke_release as release

root = Path.cwd()
source = root / "dist/releases/v1.10.0-source"
assets = source / "dist/releases"
cli = client.native_cli(root / "dist/codex-smoke-cli/node_modules/@openai/codex/bin/codex.js")
with client.temporary_workspace("frey candidate ") as workspace:
    home = workspace / "home"
    home.mkdir()
    environment = client.client_environment(home)
    Path(environment["CODEX_HOME"]).mkdir()
    assert client.run([*cli, "--version"], workspace, environment) == "codex-cli 0.150.1"
    release.verify_archive(
        assets / "frey-skills-1.10.0.zip", assets / "SHA256SUMS",
        source, workspace / "extracted", tag="v1.10.0",
    )
    previous, digest = client.release_plugin(
        workspace / "previous", environment, "v1.9.0",
        "9944b36d4406bb89443c5fabdbb15d4d019478fe",
    )
    client.smoke_client(cli, workspace, environment, previous, workspace / "extracted/frey-skills")
```

The recipe downloads only the pinned public baseline. It installs plugins only
inside its disposable project and client home. At preparation time, hosted CI's
client matrices covered older published releases; the unpublished candidate
transition had Windows-local evidence only. The current pinned matrices exercise
the published v1.9.0/v1.10.0 pair separately. Inspect matching CI jobs for hosted
evidence; historical candidate results do not substitute for those jobs.

## Desktop and publication limits

v1.10.0 desktop UI on Windows, macOS, and Linux is **NOT_TESTED**. Existing
[v1.9.0 observations](compatibility.md#v190-verification) apply only to v1.9.0.
CLI metadata checks do not establish desktop discovery, restart persistence,
prompt display, or model behavior. Behavioral model evals are not run or required;
no model-behavior certification is claimed.

After the machine checks pass, the optional Windows desktop checklist is:

1. Upgrade from verified v1.9.0 to published v1.10.0 and confirm all eleven skills
   appear once in plugin settings and the composer selector.
2. Fully restart the app; confirm discovery persists and the three starter prompts
   appear.
3. Roll back to v1.9.0 and confirm exactly eight plugin skills, then restore
   v1.10.0 and confirm unrelated installations remain intact.

Record maintainer observations with the release identity and date; do not
infer installed-byte parity or results on other desktop platforms.

Publication and public-archive verification are recorded above. The follow-up
pin update identifies that verified tag/commit; historical candidate checks did
not themselves authorize publication or establish these later results.

## Later development

At publication, the proposed release-execution scope was **PARTIAL / NOT_READY**
because target, approval/credential model, and ownership were open. The user
subsequently adopted those choices and authorized development. The current
[specification](release-execution-scope.md) and
[implementation plan](release-execution-implementation-plan.md) record that later
milestone separately. It is not part of published v1.10.0 and does not authorize
publication of any candidate.

Standalone performance and retrospective skills retain the
[M4 evidence gates](specialist-reassessment.md#specialist-dispositions).
