# Recorded plugin compatibility

Checked on 2026-10-17 with Windows 11 build 26300 and Codex CLI 0.150.1.
These results cover the CLI and its app-server metadata discovery. The desktop
plugin directory, skill selector, and restart flow remain **NOT_TESTED**.

## Verified releases

| Release | Tag commit | Plugin ZIP SHA-256 |
| --- | --- | --- |
| [v1.8.1](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.8.1) | `8fc076daa84782761d3ebf99f8f8902785119796` | `53efeb0114629c2d66ef0b5ca90cdcc6ea1e8e1aee59563b43a54f67864e44c4` |
| [v1.8.2](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.8.2) | `11720d09c41c63f853f24ff6839eed167db6717e` | `7ee0ef9f99a04c4f5be6a2cad35db8966b77f670161269f8d6994b9ba169e00e` |

Each ZIP matches its published `SHA256SUMS` and the tagged manifest, license,
skill set, and supporting-file bytes. The client checks use the downloaded
published archives. A locally prepared Windows archive had different line
endings and a different digest; it is excluded from the results below.

## Original manual CLI results

| Check | Result | Observation |
| --- | --- | --- |
| Install v1.8.1 through a local marketplace | PASS | Installed and enabled at version 1.8.1; seven plugin skills discovered once each. |
| Upgrade to v1.8.2 through the same marketplace | PASS | Installed and enabled at version 1.8.2; seven plugin skills resolve to the new version's cache. |
| v1.8.2 starter prompts | PASS | All three prompts survive manifest parsing; the earlier prompt-limit warning is absent. |
| Roll back v1.8.2 to v1.8.1 | PASS | Installed version and all seven plugin skill paths return to 1.8.1. |
| Windows desktop plugin directory and skill selector | NOT_TESTED | Native desktop UI interaction and restart were unavailable in this run. |
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

`scripts/smoke_codex.py` repeats installation, upgrade, and rollback with the
same published release pair and pinned Codex CLI 0.150.1. It verifies each archive
before installation and compares installed bytes, enabled skill ownership,
unique names, versioned cache paths, and v1.8.2 starter prompts. Every phase uses
a fresh metadata-only app-server in the same disposable client home. Inherited
credentials and Codex settings are excluded. The unrelated user-skill fixture
must survive, and the owned server tree is stopped after success or failure.

| Surface | Result | Evidence |
| --- | --- | --- |
| Windows CLI 0.150.1 | PASS | Local automated install, upgrade, and rollback on 2026-10-17; both published ZIP digests above matched and all seven installed skills retained byte parity. |
| Linux CLI 0.150.1 | NOT_TESTED | The CI matrix is configured; no successful run has been recorded here yet. |
| macOS CLI 0.150.1 | NOT_TESTED | The CI matrix is configured; no successful run has been recorded here yet. |
| Desktop UI | NOT_TESTED | Native desktop controls and restart remain unavailable in this session. |

See [Contributing](../CONTRIBUTING.md#codex-client-compatibility-smoke-check) for
the exact command and isolation/deadline details. CLI evidence does not establish
desktop UI compatibility or certify model activation or behavior.
