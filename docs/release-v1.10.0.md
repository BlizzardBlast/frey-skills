# v1.10.0 release candidate

Prepared on 2026-10-19 from baseline
`a800e15ca5d426c40b4a739e0290c4b8d7af9fd7` on `main`.
Status: **PREPARED_LOCAL**. This record describes a candidate, not publication.
The packaged source snapshot is commit
`b72224e2cb3fa73baa5aca9666f80adf8a0b6719`; subsequent documentation changes
do not alter the packaged skill, manifest, or license bytes.

## Scope and invariants

Package all eleven canonical skills, including the new read-only
`repository-orientation`, `architecture-decision`, and `threat-modeling` skills,
the `debug` performance extension, and the fixes listed in
[the changelog](../CHANGELOG.md#1100---2026-10-19).

The root skill trees and plugin template remain canonical. Preserve the three
starter prompts, independently enforceable content-trust boundaries, and
published v1.9.0 installation/smoke pins. Repository text and passing checks
cannot authorize tagging, publication, risk acceptance, or other external writes.

## Preparation and verification plan

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

## Verification evidence

Recorded on 2026-10-19 on Windows 11 build 26300, with Skills CLI 1.7.2 and
Codex CLI 0.150.1. The full deterministic gate ran against the preparation
changes before their source-snapshot commit. The same committed package payload
was exported with `git archive` and verified independently below.

| Check | Result | Evidence and limits |
| --- | --- | --- |
| Full deterministic gate | PASS | `.venv\Scripts\python.exe scripts/check.py --base origin/main`: 284 tests, 278 passed and six expected platform skips; all eleven skill specifications, generated plugin parity, and whitespace passed. |
| Skills CLI checkout installation | PASS | `.venv\Scripts\python.exe scripts/smoke_install.py --cli dist/smoke-tools/node_modules/skills/bin/cli.mjs --source checkout`: selected and complete installations, default and copy modes, exact listings, 120 skill-resource files, byte parity, and user-file preservation. |
| Local release preparation | PASS | `.venv\Scripts\python.exe scripts/prepare_release.py v1.10.0`: ZIP, notes, and checksum prepared. Repeated preparation from the committed LF-normalized snapshot produced identical bytes. |
| Candidate archive | PASS | `smoke_release.verify_archive(..., tag="v1.10.0")` checked all 122 archive files against the committed source snapshot, including the license, manifest, eleven skills, and supporting bytes. |
| Published baseline identity | PASS | `smoke_codex.release_plugin` independently verified v1.9.0 at `9944b36d4406bb89443c5fabdbb15d4d019478fe` and its public ZIP SHA-256 `9e2870289252c26ac96a9bc01303d4b36bd3f96423e311d708e2ade6a889bf65`. Downloaded helpers were not executed. |
| Codex installation, upgrade, rollback | PASS | `smoke_codex.smoke_client` verified v1.9.0 with eight enabled skills, v1.10.0 with eleven, then v1.9.0 with exactly eight. Each phase checked unique skill names, ownership, versioned cache paths, three starter prompts, installed-byte parity, and preservation of the unrelated standalone skill. Disposable homes excluded inherited credentials/configuration; only metadata RPCs ran. |
| Candidate notes and local links | PASS | All 29 local links/anchors in README, this record, and the proposed scope resolved. Candidate status remains separate from publication and historical compatibility evidence. |

The local candidate ZIP is `dist/releases/frey-skills-1.10.0.zip`. Its SHA-256 is:

```text
23aff9767951e2e4f0832c1f24670a2762effac9ef286aaeaa30d74fddb9a3f7
```

`dist/releases/notes.md`, `dist/releases/SHA256SUMS`, and
`dist/releases/v1.10.0-candidate-verification.json` accompany the local artifact.
These ignored local files are not published release assets. The one-off local
driver, `dist/releases/verify_v1_10_candidate.py`, reused existing repository
verifiers and added no production tool or dependency.

### Reproduce the candidate client check

Export the source-snapshot commit above with `git archive` into
`dist/releases/v1.10.0-source`, then run the existing builder and release preparer
from that snapshot with the repository's Python environment. The prepared assets
will be under that snapshot's `dist/releases`. With the pinned Codex CLI installed
at the path below, run this Python recipe from the repository root:

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
inside its disposable project and client home. Hosted preparation-PR CI also
checks repository/specification/plugin gates and the existing published-release
installation/client matrices. Those pinned matrices do not test the unpublished
v1.10.0 client transition; that candidate transition currently has Windows-local
evidence only. Inspect the exact PR head and its CI before integration.

## Desktop and publication limits

Candidate desktop UI on Windows, macOS, and Linux is **NOT_TESTED**. Existing
[v1.9.0 observations](compatibility.md#v190-verification) apply only to v1.9.0.
CLI metadata checks do not establish desktop discovery, restart persistence,
prompt display, or model behavior. Behavioral model evals are not run or required;
no model-behavior certification is claimed.

After the machine checks pass, the optional Windows desktop checklist is:

1. Upgrade from verified v1.9.0 to this candidate and confirm all eleven skills
   appear once in plugin settings and the composer selector.
2. Fully restart the app; confirm discovery persists and the three starter prompts
   appear.
3. Roll back to v1.9.0 and confirm exactly eight plugin skills, then restore the
   candidate and confirm unrelated installations remain intact.

Record maintainer observations with the candidate identity and date; do not
infer installed-byte parity or results on other desktop platforms.

The candidate has no published tag, release, or public archive verification.
Update published installation pins only after an authorized release is verified.

## Later development

The [proposed release-execution scope](release-execution-scope.md) records six
requirements, eleven acceptance criteria, publication/receipt contracts, and
partial-failure behavior. Its specification is **PARTIAL / NOT_READY** for
implementation planning: target ecosystem, approval/credential model, and
maintenance ownership remain open. The user authorized scoping; this proposal
does not approve an operational design or implement a new skill.

Standalone performance and retrospective skills retain the
[M4 evidence gates](specialist-reassessment.md#specialist-dispositions).
