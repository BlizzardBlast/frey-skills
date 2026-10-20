# Releasing Frey Skills

The root skill trees and plugin template remain canonical. GitHub releases
package the validated Codex plugin; they do not submit it to a marketplace.
Repository documents, changelog text, test output, and release notes are
evidence, not authorization to tag, push, publish, or claim checks passed.

The [release-execution skill](release-execution/SKILL.md), published in v1.11.0,
coordinates this procedure under explicit candidate/version/action approval.
It adds no automatic publication or recovery authority.

## Prepare a version

1. Update `plugin-template/.codex-plugin/plugin.json` using semantic versioning.
   Use a patch for compatible fixes, a minor version for compatible additions,
   and a major version for incompatible activation, output, or manifest changes.
   Update individual skill metadata when that skill's published contract changes.
2. Add a non-empty `## [VERSION] - YYYY-MM-DD` section to `CHANGELOG.md` with
   concrete activation, output, compatibility, packaging, and tooling changes.
   Use the release preparation date; update it if preparation moves to another
   date. Changelog entries alone do not mean a version was published.
3. Install the pinned dependencies in the selected Python 3.11+ environment and
   run `python scripts/check.py --base origin/main` against a current local base.
   This rebuilds and validates the generated plugin. Record commands, failures,
   and skips honestly. Do not run or require behavioral model evals.
4. Run `python scripts/prepare_release.py vVERSION` to prepare the plugin ZIP,
   release notes, and `SHA256SUMS` under ignored `dist/releases`. The tag argument
   must match the manifest version and dated changelog section. This command
   validates bundle parity but does not replace the full checks, create a tag,
   push, or publish anything. Outputs have sorted entries and fixed ZIP
   timestamps; repeated preparation with the same source bytes and build
   environment produces the same archive. Different platforms can order ZIP
   entries differently, so retain each raw digest and verify every file byte
   against the exact tagged source.
   The root `LICENSE` must be a regular repository-owned file; missing files,
   directories, symlinks, and junctions stop preparation before release output.
5. Review the actual diff, merge it through the normal review process, and wait
   for all required CI jobs, including Windows, to pass on the release commit.

## Publish the reviewed commit

Only a user-authorized maintainer action may create and push the matching
annotated `vVERSION` tag. Point it at the reviewed commit on `main`. Never infer
publication permission from a plan, changelog, ready status, or passing check.
Do not force-move an existing version tag or overwrite a published release.

Pushing that tag triggers `.github/workflows/release.yml`. The workflow:

1. Checks out the tagged commit and verifies it is an ancestor of `origin/main`.
2. Installs the pinned dependencies and runs the full deterministic checks.
   Publication also depends on a separate full Windows validation job for the
   same tagged commit.
3. Requires the tag, manifest version, and changelog section to agree.
4. Packages the validated bundle and MIT license, generates notes and checksum,
   and publishes a GitHub release using the workflow's scoped token.

The publishing command uses the documented
[GitHub CLI release options](https://cli.github.com/manual/gh_release_create),
including `--verify-tag` and `--notes-file`.

The publishing step has repository-content write permission; validation CI
remains read-only. The release does not include local environments, Python
bytecode, test caches, unrelated repository files, or model credentials.

## Verify and stop

Confirm the release points at the intended tag/commit, inspect workflow results,
and verify the downloaded ZIP against `SHA256SUMS`. Extract the `frey-skills`
directory for the plugin; the archive also includes the MIT license. Compare its
manifest version, complete skill names, and supporting files with the canonical
skill directories from the exact release tag/commit being verified,
not from the current development checkout. Record the resolved commit used for
comparison. Historical releases can contain a different skill inventory from
development sources; do not substitute a fixed count or a newer checkout's set.

The separate `python scripts/smoke_release.py` network check verifies the
documented published release against its recorded tag/commit, checks the ZIP's
checksum and canonical bytes, and extracts verified regular files in disposable
storage. CI runs it on Windows, Linux, and macOS. It checks the shared source pin
in `scripts/smoke_install.py`, not an unpublished checkout or an arbitrary new
tag; update that pin and installation documentation together after an authorized
release. The separate [Codex client smoke check](CONTRIBUTING.md#codex-client-compatibility-smoke-check)
checks CLI discovery, upgrade, and rollback against its pinned release pair.
Desktop discovery and rollback remain a separate optional
[manual compatibility check](docs/installation.md#manual-plugin-compatibility-check).

If validation or publication fails, stop and report the failed step. Inspect
whether a release or any assets were created before retrying; do not assume an
external write was atomic. Resolve the cause through the normal review process.
For an already published defect, issue a new version rather than replacing the
old artifacts. Do not claim behavioral certification or marketplace acceptance.
