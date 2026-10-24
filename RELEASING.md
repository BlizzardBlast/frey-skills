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
   Use ASCII digits for numeric version components. Local release preparation
   requires a stable `MAJOR.MINOR.PATCH` version.
2. Add a non-empty `## [VERSION] - YYYY-MM-DD` section to `CHANGELOG.md` with
   concrete activation, output, compatibility, packaging, and tooling changes.
   Use exactly one column-zero version heading and a valid ASCII calendar date.
   Fenced examples and HTML blocks cannot supply section headings. Literal HTML
   containers, including inline-opened containers and `title`, cannot supply or
   end a section before their closing tags. Example content inside a release
   section is preserved; the next eligible column-zero H1/H2 ends it.
   URI autolinks do not hide following headings or duplicate version sections.
   Code spans and escaped tags or comment markers after an HTML comment closes
   remain literal; active reopened comments and HTML containers still exclude
   example headings until their closers.
   Release preparation uses the repository's pinned CommonMark parser, including
   block boundaries after reference definitions and empty lists. Install the
   development requirements before invoking preparation directly.
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
   push, or publish anything. Outputs use relative POSIX-name ordering, fixed ZIP
   metadata, and LF text checkouts through `.gitattributes`. Identical source
   bytes and Python/zlib build environments produce the same archive across
   platforms. Different compression versions can still change raw ZIP bytes;
   retain each digest and verify every file byte against the exact tagged source.
   The root `LICENSE` must be a regular repository-owned file; missing files,
   directories, symlinks, and junctions stop preparation before release output.
   Bundle and release-file publication retain prior outputs until all renames
   succeed and restore them on an ordinary publication failure. Cooperating
   writers serialize through `.frey-publish` in the output parent. A crash,
   failed rollback, or cleanup error can leave this directory for recovery;
   stop and inspect its `previous/` backups and current outputs before removing
   the lock or retrying. The release-file set is recoverable, not atomically
   visible across multiple paths; concurrent readers must wait for completion.
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
checks CLI discovery, upgrade, and rollback against its pinned release pair and
a freshly built checkout candidate in separate disposable projects. The
candidate transition uses the pinned previous release as its baseline, avoiding
reuse of an installed candidate cache when development retains a version number.
Desktop discovery and rollback remain a separate optional
[manual compatibility check](docs/installation.md#manual-plugin-compatibility-check).

If validation or publication fails, stop and report the failed step. Inspect
whether a release or any assets were created before retrying; do not assume an
external write was atomic. Resolve the cause through the normal review process.
For an already published defect, issue a new version rather than replacing the
old artifacts. Do not claim behavioral certification or marketplace acceptance.
