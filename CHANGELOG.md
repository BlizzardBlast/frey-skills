# Changelog

Entries describe versioned repository changes. The GitHub Releases page records
which versions have actually been published. Skill activation, structured
output fields, and trust contracts are unchanged in 1.8.1 and 1.8.2.

## Unreleased

### Added

- Pinned Codex CLI metadata compatibility checks on Windows, Linux, and macOS
  for verified published v1.8.1 installation, v1.8.2 upgrade, and v1.8.1 rollback.
  Checks require enabled, uniquely named plugin skills, correct ownership and
  versioned cache paths, installed byte parity, and current starter prompts.
  Disposable client homes exclude inherited credentials. Offline regressions
  cover false-positive metadata, resource drift, RPC failures, deadlines, and
  owned descendant cleanup without model turns or behavioral evals.

### Changed

- Installation examples and cross-platform smoke checks now pin the published
  v1.8.2 tag and commit. Recorded Windows Codex CLI discovery and rollback
  results identify the verified archives. Separate Windows desktop screenshot
  evidence covers installation, upgrade, rollback, final restoration to v1.8.2,
  and all seven enabled plugin-settings entries; composer-selector discovery,
  restart persistence, starter-prompt UI, and other desktop platforms remain
  explicitly untested.

## [1.8.2] - 2026-10-17

### Added

- Published Codex plugin archive smoke checks on Windows, Linux, and macOS,
  verifying the pinned tag/commit, checksum, manifest, license, skill set, and
  supporting-file bytes before extraction in disposable storage. Offline tests
  cover altered, missing, extra, duplicate, unsafe, and oversized artifacts,
  network failures, and preservation of existing extraction destinations.
- A separate manual plugin discovery and rollback compatibility checklist that
  records client-specific results without claiming behavioral certification.
- A README skill-selection table and installation guide covering version-pinned
  skill sources, the Codex plugin archive, verification, upgrades, and rollback.
- A macOS Python 3.12 CI job running the full deterministic validation set.
- Installation smoke checks on Windows, Linux, and macOS using the pinned Skills
  CLI, isolated project/user directories, and byte parity for selected and
  complete skill installations from the checkout and documented release tag in
  default and copy modes. Offline assertion tests cover incomplete installs,
  altered resources, installer failures, version mismatches, and timeouts.

### Fixed

- The Codex plugin offers three starter prompts, within the client's supported
  limit, so the manifest loader accepts the complete prompt list. All seven
  packaged skills remain available with unchanged activation and output contracts.
- Published archive downloads enforce their total deadline outside blocking
  network I/O, terminate and reap timed-out workers, and discard partial files.
  Real slow-stream and blocked-connection regression tests cover this boundary.
- POSIX repository validation preflights its `ps` prerequisite and reports
  missing setup before running checks; contributor setup documents the utility.
- Selected and complete installation smoke checks use independent empty projects
  so an earlier install cannot hide an omitted wildcard skill.
- Discovery checks verify the exact listed skill names, including missing,
  extra, and duplicate results, against the pinned CLI's output format.
- Timed-out smoke commands terminate their owned process trees and collect
  output through temporary files with bounded cleanup waits. A real nested
  subprocess test covers inherited output handles and descendant termination.

## [1.8.1] - 2026-10-16

### Added

- A platform-neutral deterministic validation runner with dependency preflight,
  selectable gate groups, failure propagation, and optional committed
  whitespace checks against a local comparison base.
- A Windows Python 3.12 CI job running the full deterministic validation set.
- A worked example covering specification, planning, test strategy, execution,
  read-only review, scoped remediation, and user approval boundaries.
- Version-tagged GitHub release publication with a validated plugin ZIP,
  version-matched notes, and SHA-256 checksum. Publication is triggered only by
  pushing an authorized matching tag from a commit on `main`.

### Fixed

- The legacy fixture setup helper creates only new, unlinked destinations and
  preserves existing files and directories instead of resetting them.
- Canonical source discovery, build, and parity validation reject linked skill
  roots and template paths before packaging external files or replacing output.
- The review-context helper resolves range refs to commit IDs before diffing;
  invalid or option-shaped refs fail without writing unexpected files.
- Review-context collection covers the full repository from nested directories,
  including untracked siblings and repositories with `diff.relative` enabled.
- Review-context collection before the first commit supports both SHA-1 and
  SHA-256 repositories without writing Git objects.
- Test subprocesses use the selected Python interpreter rather than a separate
  `python` or `python3` from PATH.
- Filesystem tests retain space/Unicode coverage on Windows and tab-containing
  filename coverage on platforms that support it. Parser tests cover control
  characters on every platform.
- Symlink tests report unavailable Windows privileges as explicit skips and use
  owned temporary targets.
- Test fixtures resolve owned temporary roots so validation also works when the
  system temporary directory is reached through a symlink or junction.
- Repository hygiene checks exclude the local virtual environment and caches.
- Validator diagnostics use consistent forward-slash paths and apply the same
  single-trailing-newline rule to LF and CRLF files.
- Specification validation uses UTF-8 mode on Windows.
- Validation runner output and Python child processes use UTF-8 even with a
  non-UTF-8 parent environment and non-ASCII repository paths.
- Whitespace validation covers both staged and unstaged changes.
- Forced plugin builds reject outputs that contain canonical sources, including
  repository ancestors, before replacing any files.
- Plugin builds reject output symlinks, junctions, and linked parents before
  resolution. Non-forced builds preserve data created during staging.
- Output validation inspects raw path components before collapsing `..`, so a
  linked component cannot redirect a forced build to a different directory.
- Non-forced review-context writes publish atomically without overwriting a
  concurrent writer; unsupported hard-link operations fail safely.
- Release packaging requires a regular repository-owned `LICENSE` and rejects
  symlinks, junctions, directories, and missing license files before output.
- The code-review context helper emits UTF-8 JSON and errors even when its
  output is redirected on Windows; decoded JSON fields are unchanged.
- Plugin packaging excludes Python bytecode and local test caches. Distributable
  source files still match canonical sources byte-for-byte, and unexpected
  caches in a generated bundle fail parity validation.

### Validation policy

Only deterministic repository, specification, contract, packaging, and
whitespace checks are supported. Behavioral model evals were not run, and no
model-behavior certification is claimed.

## 1.8.0 baseline

The existing source baseline at commit `06ea512` contains seven skills:
`debug`, `change-specification`, `implementation-plan`, `test-strategy`,
`implementation-execution`, `code-review`, and `iterative-self-review`.
It includes repository-wide content-trust contracts and deterministic plugin
build/parity validation. This entry does not claim a historical published
release or behavioral model trial.
