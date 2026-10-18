# Install, upgrade, and roll back Frey Skills

Choose skill folders through the Skills CLI or the complete Codex plugin ZIP.
Use one route for a given skill in an agent to avoid duplicate names. Neither
route requires model credentials or behavioral model evals.

The versioned examples target the published eight-skill v1.9.0 release.
`repository-orientation` is unreleased and is available only in development
sources that contain it; it is not included in that pinned release or its ZIP.

## Install skill folders

Install Node.js with npm and Git, then run these commands from the project that
will use the skills. The Skills CLI's [upstream guide](https://github.com/vercel-labs/skills#readme)
documents its supported agents, installation scopes, and options.

To pin the installer as well, replace `npx skills` with `npx skills@1.7.2`,
the CLI version used to verify these examples.

CI exercises this pinned CLI against the documented source tag and the current
checkout on Windows, Linux, and macOS. It checks selected and complete skill
installations in default and copy modes, including supporting-file byte parity.
See [Contributing](../CONTRIBUTING.md#installation-smoke-checks) to run the checks.
This coverage does not test agent discovery, activation, or model behavior.

List the eight skills at the versioned source without installing them:

```bash
npx skills add https://github.com/BlizzardBlast/frey-skills/tree/v1.9.0 --list
```

Install interactively, choosing the skills, target agent, and scope:

```bash
npx skills add https://github.com/BlizzardBlast/frey-skills/tree/v1.9.0
```

For example, install only `code-review` for Codex in the current project:

```bash
npx skills add https://github.com/BlizzardBlast/frey-skills/tree/v1.9.0 --skill code-review --agent codex
```

Add `--global` for user scope. Use `--copy` if your environment cannot create
the installer's symlinks. Other agents can be selected in the interactive
installer or with their upstream agent identifier.

The `tree/v1.9.0` URL selects that Git tag. For a commit pin, replace `v1.9.0`
with the full commit SHA. The shorthand `BlizzardBlast/frey-skills` follows the
default branch. `owner/repo@name` selects a skill in the Skills CLI; it is not
the version-pin syntax.

### Verify the installation

Confirm the selected skill folders contain `SKILL.md` and any adjacent
`references/`, `scripts/`, or `agents/` resources. Codex project installations
use `.agents/skills/`; user installations use `~/.agents/skills/`. Restart
Codex if the new skills do not appear in its skill selector, following the
[official skill discovery guidance](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

Use the [README selector](../README.md#choose-a-skill) to choose a workflow.
For example, explicitly invoke `$code-review` for a read-only review; invoke
`iterative-self-review` only when you intend to authorize scoped remediation.
Discovery and file checks do not certify model activation or behavior.

### Upgrade or roll back skill folders

1. Record the current source tag or commit, selected skills, agent, scope, and
   installation method. Preserve any local edits before replacing files.
2. Read the target version's [release notes](https://github.com/BlizzardBlast/frey-skills/releases).
3. Re-run `skills add` with that version's `tree/TAG` URL and the same skill,
   agent, scope, and copy/symlink choices. Review any overwrite prompt.
4. Verify the installed files and discovery again.

Rollback uses the same process with the previously recorded tag or commit.
For example, roll back from v1.9.0 to v1.8.2 with:

```bash
npx skills add https://github.com/BlizzardBlast/frey-skills/tree/v1.8.2 --skill code-review --agent codex
```

Choose a different target tag for an upgrade. If no previous release was
installed, restore the setup recorded before installation instead.
Use an explicit target rather than a bulk update command when you need to
control the Frey Skills version. To uninstall only this example's project
skill, use `npx skills remove code-review --agent codex`; add `--global` if
that was its installation scope.

## Install the Codex plugin ZIP

CI checks the published ZIP on Windows, Linux, and macOS, including its checksum,
manifest, license, complete skill set, and byte parity with the pinned release's
sources. To repeat this file check in a repository checkout, run
`python scripts/smoke_release.py` with Python 3.11+ and Git. It uses disposable
directories and does not install the plugin. Agent discovery and rollback remain
a separate manual compatibility check below.

Download `frey-skills-1.9.0.zip` and `SHA256SUMS` from the
[v1.9.0 release](https://github.com/BlizzardBlast/frey-skills/releases/tag/v1.9.0).
Compare the archive's SHA-256 digest with its filename's entry in `SHA256SUMS`:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath ./frey-skills-1.9.0.zip
```

On macOS or Linux, use:

```bash
shasum -a 256 frey-skills-1.9.0.zip
```

Stop if the checksum differs. Extract the archive to a new version-specific
directory. It contains `LICENSE` and a `frey-skills/` folder with
`.codex-plugin/plugin.json` and `skills/`. Confirm the manifest version is
`1.9.0` and `skills/` contains these eight directories:

```text
change-specification
code-review
debug
implementation-execution
implementation-plan
iterative-self-review
release-readiness
test-strategy
```

Keep the extracted folder in a stable location. Local Codex plugins are
installed through a marketplace source. For example, in your consuming
project, extract under `plugins/frey-skills-1.9.0/`, then add this entry to
that project's `.agents/plugins/marketplace.json`:

```json
{
  "name": "frey-local",
  "interface": { "displayName": "Frey Local" },
  "plugins": [
    {
      "name": "frey-skills",
      "source": {
        "source": "local",
        "path": "./plugins/frey-skills-1.9.0/frey-skills"
      },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity"
    }
  ]
}
```

Merge the entry into an existing catalog rather than replacing its other
plugins. The path is relative to the consuming project's root. Restart the
desktop app, choose **Frey Local** in the Plugins Directory, and install
**Frey Skills**. See the [official local-plugin instructions](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually)
for personal catalogs and client-specific setup.

This catalog is optional setup in your own project. Frey Skills does not ship
a marketplace catalog or submit the plugin to the public directory.

### Upgrade or roll back the plugin

Verify and extract the target release into a new directory, then change only
the Frey Skills entry's `source.path` to that version's extracted `frey-skills`
folder. Retain the previous directory for rollback. Restart the desktop app
and verify the plugin's skills are discoverable. To roll back, restore the
previous path and restart again, as described in the official local-plugin
instructions above. Do not edit Codex's installed plugin cache directly.

### Manual plugin compatibility check

See the [recorded client results](compatibility.md) for the tested release pair,
client version, archive digests, and remaining coverage limits.

The separate [Codex CLI smoke check](../CONTRIBUTING.md#codex-client-compatibility-smoke-check)
automates metadata discovery, upgrade, and rollback in disposable client homes
on Windows, Linux, and macOS. Its results do not replace the desktop checks below.

Use a disposable consuming project and your normal local-plugin installation
flow above. This is an optional client compatibility check, separate from the
automated archive checks and deterministic merge gates. It requires no model
prompts, provider credentials, paid tokens, or behavioral evals.

1. Record the operating system, Codex client version, target release tag and
   commit, verified ZIP digest, and the previous plugin path/version if one
   exists. Keep the previous extracted directory for rollback.
2. Install the verified archive through that project's local marketplace entry,
   then restart the client as described above. Confirm **Frey Skills** appears
   and its skill selector lists each of the eight packaged skills once. Use one
   installation route to avoid duplicate skill names. Inspect discovery only;
   do not invoke a skill to establish this result.
3. If upgrading from an older installed release, change only the Frey Skills
   entry's `source.path` back to its recorded previous directory, restart, and
   confirm the previous manifest version and skill list are restored. Preserve
   unrelated marketplace entries and user skills. With only the first release
   available, mark cross-version rollback **NOT_TESTED**; restoring the recorded
   pre-install setup is a separate check.
4. Record discovery and rollback independently as **PASS**, **FAIL**, or
   **NOT_TESTED**, with the observed client/version and any limitation. A passing
   archive check cannot substitute for either manual result, and neither result
   certifies skill activation or model behavior.
