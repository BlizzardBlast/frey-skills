# Recorded plugin compatibility

The current published release is v1.11.0; see the separate
[v1.11.0 verification](#v1110-verification) for its public archive, CLI checks,
and desktop coverage limits. The maintainer-reported Windows desktop results
below apply to v1.9.0 only.

Historical v1.8.1/v1.8.2 checks were recorded on 2026-10-17 with Windows 11
build 26300 and Codex CLI 0.150.1.
CLI and app-server metadata results are recorded separately from the
[Windows desktop observations](#windows-desktop-observations) below. Desktop
installation, upgrade, rollback, final restoration, and the plugin-settings skill list have
screenshot evidence. For those historical checks, composer-selector discovery
and restart persistence remain **NOT_TESTED**.

## Verified releases

| Release | Tag commit | Plugin ZIP SHA-256 |
| --- | --- | --- |
| [v1.8.1](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.8.1) | `8fc076daa84782761d3ebf99f8f8902785119796` | `53efeb0114629c2d66ef0b5ca90cdcc6ea1e8e1aee59563b43a54f67864e44c4` |
| [v1.8.2](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.8.2) | `11720d09c41c63f853f24ff6839eed167db6717e` | `7ee0ef9f99a04c4f5be6a2cad35db8966b77f670161269f8d6994b9ba169e00e` |
| [v1.9.0](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.9.0) | `9944b36d4406bb89443c5fabdbb15d4d019478fe` | `9e2870289252c26ac96a9bc01303d4b36bd3f96423e311d708e2ade6a889bf65` |
| [v1.10.0](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.10.0) | `97f755b41e388f31b7c63465743ac26aa111360c` | `616ee291a1bca1ec0719045adf191b9dd773e8c23bed2a73446a865a13687cfc` |
| [v1.11.0](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.11.0) | `7e7a535ca9f19fc8514c368cb00d5c4e8288dfcf` | `8f6f1d36d213cd8c49094708a4af9e46551212e89135d8fc654e47c6781d8897` |

Each ZIP matches its published `SHA256SUMS` and the tagged manifest, license,
skill set, and supporting-file bytes. The client checks use the downloaded
published archives. The historical v1.10.0 Windows candidate retained CRLF and
had a different digest. The v1.11.0 Windows candidate instead has matching file
contents but different ZIP entry ordering and a different raw digest. Both are
kept separate from the public-archive results below.

## Original manual CLI results

| Check | Result | Observation |
| --- | --- | --- |
| Install v1.8.1 through a local marketplace | PASS | Installed and enabled at version 1.8.1; seven plugin skills discovered once each. |
| Upgrade to v1.8.2 through the same marketplace | PASS | Installed and enabled at version 1.8.2; seven plugin skills resolve to the new version's cache. |
| v1.8.2 starter prompts | PASS | All three prompts survive manifest parsing; the earlier prompt-limit warning is absent. |
| Roll back v1.8.2 to v1.8.1 | PASS | Installed version and all seven plugin skill paths return to 1.8.1. |
| Windows desktop plugin directory and skill selector | NOT_TESTED | Not exercised in the original CLI run; subsequent Windows desktop observations are recorded separately below. |
| macOS and Linux manual client discovery and rollback | NOT_TESTED | No matching local clients were exercised in the original manual check; see automated results below. |

The seven names returned by `skills/list` are `frey-skills:change-specification`,
`frey-skills:code-review`, `frey-skills:debug`,
`frey-skills:implementation-execution`, `frey-skills:implementation-plan`,
`frey-skills:iterative-self-review`, and `frey-skills:test-strategy`.
Assertions use the plugin namespace and version-specific cache paths so
pre-existing standalone user skills cannot satisfy the plugin check.

## Method and limits

Use a disposable consuming project and a separate child-process `CODEX_HOME`
for config and cache. Preserve both extracted releases. Configure its local
marketplace using the [installation guide](installation.md#install-the-codex-plugin-zip).
Record `codex --version`, then use these metadata-only commands:

```text
codex plugin marketplace add <disposable-project> --json
codex plugin add frey-skills@frey-local --json
codex plugin list --marketplace frey-local --json
```

Start a fresh `codex app-server` process for each version. Send `initialize`
with `experimentalApi: true`, acknowledge with `initialized`, then inspect
`skills/list` with the disposable project's `cwds` and `forceReload: true`.
Use `plugin/read` with the local `marketplacePath` to inspect the parsed version
and starter prompts. Change only the marketplace entry's `source.path`, repeat
installation, and start another process for upgrade and rollback.

The child clients have no copied authentication credentials. The app-server's
featured remote catalog warmup emitted an authentication or network warning;
the local plugin install, metadata requests, and skill discovery succeeded.
Existing standalone user skills can still be read by the client; the checks
isolate plugin config/cache and do not change those user skills.

No thread, model turn, skill invocation, or behavioral model eval was run.
These observations do not certify model behavior. Cross-platform CI installation
and archive smoke checks remain separate file-integrity evidence; repeat the
[manual desktop check](installation.md#manual-plugin-compatibility-check) for
the client surface you use.

## Automated CLI compatibility

The initial `scripts/smoke_codex.py` checks used the v1.8.1/v1.8.2 pair below
and pinned Codex CLI 0.150.1. Current pins are recorded in the v1.11.0 section.
Those checks verified each archive before installation and compared installed
bytes, enabled skill ownership, unique names, versioned cache paths, and v1.8.2
starter prompts. Every phase used a fresh metadata-only app-server in the same
disposable client home. Inherited credentials and Codex settings were excluded;
the unrelated user-skill fixture survived, and the owned server tree was stopped.

| Surface | Result | Evidence |
| --- | --- | --- |
| Windows CLI 0.150.1 | PASS | Local automated install, upgrade, and rollback on 2026-10-17; both published ZIP digests above matched and all seven installed skills retained byte parity. |
| Linux CLI 0.150.1 | PASS | [Hosted Ubuntu check](https://github.com/BlizzardBlast/frey-skills/actions/runs/39034359545/job/117401091810) on 2026-10-17; install, upgrade, rollback, and all seven skills passed. |
| macOS CLI 0.150.1 | PASS | [Hosted macOS check](https://github.com/BlizzardBlast/frey-skills/actions/runs/39034359545/job/117401091797) on 2026-10-17; install, upgrade, rollback, and all seven skills passed. |
| Windows desktop (manual) | PARTIAL | User-supplied screenshots establish installation, upgrade, rollback, final restoration, and seven enabled plugin-settings entries; see the separate observations below for remaining limits. |

See [Contributing](../CONTRIBUTING.md#codex-client-compatibility-smoke-check) for
the exact command and isolation/deadline details. CLI evidence does not establish
desktop UI compatibility or certify model activation or behavior.

## Windows desktop observations

Recorded on 2026-10-17 on Windows 11 build 26300. Local package metadata
identified the installed `OpenAI.Codex` package as `26.1013.4894.0`; the app's
own About version was not captured. The maintainer supplied nine screenshots
across installation at v1.8.1, upgrade to v1.8.2, rollback to v1.8.1, and final
restoration to v1.8.2 using the same disposable local marketplace. Both published
archives were reverified against the release identities and digests above before
the check.

| Desktop check | Result | Observed evidence |
| --- | --- | --- |
| Local marketplace and plugin entry | PASS | The directory shows Frey Desktop Check and Frey Skills; later installed-plugin settings show an Uninstall control and the matching marketplace identity. |
| Install v1.8.1 | PASS | Plugin About shows version 1.8.1 and the prepared v1.8.1 source directory. |
| Upgrade to v1.8.2 | PASS | Plugin About changes to version 1.8.2 and the prepared v1.8.2 source directory under the same marketplace. |
| Roll back to v1.8.1 | PASS | Plugin About returns to version 1.8.1 and the previous source directory. |
| Plugin-settings skill list | PASS | All seven packaged skills appear once each with enabled toggles in every phase, including Iterative Self-Review. |
| Composer skill selector | NOT_TESTED | The supplied screenshots show plugin settings rather than the composer selector. |
| Discovery persists after a full app restart | NOT_TESTED | The screenshots do not establish a completed quit/reopen sequence, and the maintainer has not separately confirmed it. |
| Desktop starter-prompt display | NOT_TESTED | No starter-prompt UI was captured; CLI manifest-parsing evidence remains separate. |
| Final return to v1.8.2 after rollback | PASS | Plugin About again shows version 1.8.2 and the prepared v1.8.2 source directory under the same marketplace; all seven plugin-settings entries are enabled. |
| Unrelated plugin and standalone-skill preservation | NOT_TESTED | No complete desktop before/after inventory was supplied. |

These results summarize user-observed UI state rather than automated desktop
actions or desktop installed-byte parity. Raw screenshots, temporary filenames,
personal source paths, and unrelated UI details are omitted from this record.
macOS and Linux desktop surfaces remain **NOT_TESTED**. No skill invocation or
behavioral model eval was used to establish these observations, and no
model-behavior certification is claimed.

## v1.9.0 verification

Checked on 2026-10-18 on Windows with Codex CLI 0.150.1 and Skills CLI 1.7.2.
The [release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/39085573043)
passed both Windows validation and Linux validation/publication for the tag
commit above. The downloaded public archive, rather than a locally prepared
Windows ZIP, supplies the digest and bytes for the results below.

| Check | Result | Observed evidence |
| --- | --- | --- |
| Published v1.9.0 archive | PASS | `smoke_release.py` verified the tag/commit, SHA256SUMS, manifest, LICENSE, all eight skills, and supporting-file byte parity against an LF checkout of the tag. |
| Skills CLI installations | PASS | `smoke_install.py` verified selected and complete eight-skill installations from both the checkout and v1.9.0 source pin, in default and copy modes, with exact listings and byte parity. |
| Install v1.8.2 | PASS | Seven uniquely named, enabled plugin skills resolve to the isolated 1.8.2 cache. |
| Upgrade to v1.9.0 | PASS | Eight uniquely named, enabled plugin skills resolve to the isolated 1.9.0 cache, including `frey-skills:release-readiness`. |
| Roll back to v1.8.2 | PASS | Exactly seven plugin skills resolve to 1.8.2; the eighth skill is absent. |
| Starter prompts and preservation | PASS | Both versions retain their three prompts, installed files match their verified public archives, and the unrelated standalone skill fixture survives every phase. |
| v1.9.0 Windows desktop UI | PASS (maintainer-reported) | On 2026-10-18 the maintainer confirmed completing the proposed Windows desktop checklist successfully; see the report below. Historical v1.8.x screenshots remain separate evidence. |

The archive and CLI rows record local Windows results. The installation/archive
and Codex client CI matrices are configured to repeat the same pinned checks on Windows,
Linux, and macOS; inspect the matching commit's jobs in the
[CI workflow history](https://github.com/BlizzardBlast/frey-skills/actions/workflows/ci.yml)
for hosted evidence. The metadata checks use disposable credential-free homes
and fresh app-server processes. Those checks ran no model turn, skill invocation,
or behavioral model eval, and no model-behavior certification is claimed.

### Maintainer-reported Windows desktop check

On 2026-10-18 the maintainer responded to the proposed three-step Windows
desktop checklist: "I have done it myself. It works."

The confirmed checklist covered:

1. Upgrade from v1.8.2 to v1.9.0 and confirm all eight skills appear in plugin
   settings and the composer selector.
2. Fully restart the app, confirm skill discovery persists, and confirm the three
   starter prompts appear.
3. Roll back to v1.8.2 and verify seven skills, restore v1.9.0, and confirm
   unrelated installations remain intact.

This is a maintainer-reported pass for that Windows checklist. No new
screenshots, desktop app build, or per-step captures accompanied the report;
do not infer the app build from the historical v1.8.x observations. This report
does not establish desktop installed-byte parity or model behavior. macOS and
Linux desktop UI remain **NOT_TESTED**. Behavioral model evals were not run,
and no model-behavior certification is claimed.

## v1.10.0 verification

Checked on 2026-10-19 on Windows 11 build 26300 with Codex CLI 0.150.1 and
Skills CLI 1.7.2. The [release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/39248673037)
passed Windows validation and Linux validation/publication at the tag commit
above. These results use the downloaded public archives. The earlier Windows
candidate retained CRLF and a different digest; it is historical candidate
evidence, not the public artifact used below.

| Check | Result | Observed evidence |
| --- | --- | --- |
| Public v1.10.0 archive | PASS | `scripts/smoke_release.py` verified the tag/commit, public checksum, manifest, license, all eleven skills, and every supporting byte in all 122 files against an LF tagged checkout. |
| Skills CLI installations | PASS | `scripts/smoke_install.py --cli dist/smoke-tools/node_modules/skills/bin/cli.mjs` verified selected and complete eleven-skill installations from both checkout and the v1.10.0 source pin, in default and copy modes, with exact listings, 120 skill-resource files, byte parity, and user-file preservation. |
| Install v1.9.0 | PASS | `scripts/smoke_codex.py --cli dist/codex-smoke-cli/node_modules/@openai/codex/bin/codex.js` discovered exactly eight enabled plugin skills in the isolated 1.9.0 cache. |
| Upgrade to v1.10.0 | PASS | Exactly eleven enabled plugin skills resolve to 1.10.0, including `repository-orientation`, `architecture-decision`, and `threat-modeling`. |
| Roll back to v1.9.0 | PASS | Exactly eight plugin skills resolve to 1.9.0; the three additions are absent. |
| Starter prompts, ownership, and preservation | PASS | Each phase retained three starter prompts, correct plugin ownership and versioned paths, installed public-archive byte parity, and the unrelated standalone skill fixture. |
| v1.10.0 desktop UI | NOT_TESTED | No Windows, macOS, or Linux desktop observation was supplied for this version. Historical v1.9.0 maintainer observations do not establish v1.10.0 UI compatibility. |

Commands used the repository's Python environment and disposable child homes;
the three metadata RPCs ran no model turn or skill invocation. No real agent
installation was modified. Behavioral model evals were not run, and no
model-behavior certification is claimed.

These archive and CLI rows are historical local Windows observations. At that
pin update, the installation, archive, and Codex client matrices were configured
for those published pins on Windows, Linux, and macOS; inspect that exact
pin-update commit's jobs for hosted evidence.
See the [release record](release-v1.10.0.md) for public and historical candidate
identities, and keep the [optional desktop checklist](installation.md#manual-plugin-compatibility-check)
separate from those automated checks.

## v1.11.0 verification

Checked on 2026-10-20 on Windows with Python 3.12.14, Codex CLI 0.150.1,
and Skills CLI 1.7.2. The
[release workflow](https://github.com/BlizzardBlast/frey-skills/actions/runs/39348469828)
passed Windows validation and Linux validation/publication for
`7e7a535ca9f19fc8514c368cb00d5c4e8288dfcf`. Archive and Codex transition
results below use the downloaded public ZIPs. The Skills CLI row distinguishes
checkout installations from the identified published source pin.

| Check | Result | Observed evidence |
| --- | --- | --- |
| Public v1.11.0 archive | PASS | `scripts/smoke_release.py` verified the annotated release's exact commit, public checksum, manifest, license, all twelve skills, and all 126 archive files against an LF tagged checkout. ZIP SHA-256 is `8f6f1d36d213cd8c49094708a4af9e46551212e89135d8fc654e47c6781d8897`. |
| Skills CLI installations | PASS | `scripts/smoke_install.py --cli dist/smoke-tools/node_modules/skills/bin/cli.mjs` checked checkout and v1.11.0 source-pin installations: selected/complete skill sets, default/copy modes, exact listings, 124 skill-resource files, byte parity, and user-file preservation. |
| Install v1.10.0 | PASS | `scripts/smoke_codex.py --cli dist/codex-smoke-cli/node_modules/@openai/codex/bin/codex.js` discovered exactly eleven enabled plugin skills in the isolated 1.10.0 cache. Its public archive was independently verified against the commit/digest in the release table above. |
| Upgrade to v1.11.0 | PASS | Exactly twelve enabled plugin skills resolve to 1.11.0, including `frey-skills:release-execution`; installed bytes match the public archive. |
| Roll back to v1.10.0 | PASS | Exactly eleven plugin skills resolve to 1.10.0; `release-execution` is absent. |
| Starter prompts, ownership, and preservation | PASS | Each phase retained its three starter prompts, correct plugin ownership and versioned cache paths, installed public-archive byte parity, and the unrelated standalone skill fixture. |
| v1.11.0 desktop UI | NOT_TESTED | No Windows, macOS, or Linux desktop observations were supplied for this release. Historical desktop results do not transfer to it. |

The commands used the repository's Python environment and disposable,
credential-free child homes. Downloaded helpers were not executed. Metadata
RPCs started no model turn or skill invocation; behavioral model evals were not
run, and no model-behavior certification is claimed.

These rows are local Windows observations. The existing installation/archive
and Codex client CI matrices now target the verified v1.11.0 source/archive and
the published v1.10.0/v1.11.0 transition on Windows, Linux, and macOS. Inspect
the exact pin-update commit's jobs for hosted evidence rather than extending
the local result to another platform. See the
[release record](release-v1.11.0.md) for independent public and candidate ZIP
identities. The [desktop checklist](installation.md#manual-plugin-compatibility-check)
remains optional and separate.
