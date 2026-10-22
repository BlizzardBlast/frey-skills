# Changelog

Entries describe versioned repository changes. The GitHub Releases page records
which versions have actually been published. Skill activation, structured
output fields, and trust contracts are unchanged in 1.8.1 and 1.8.2.

## Unreleased

### Fixed

- Release preparation reuses the pinned CommonMark parser for section boundaries,
  excluding HTML examples after reference definitions and empty lists. Its tests
  now run in the repository gate; standalone plugin checks retain their
  standard-library-only dependencies.
- Markdown anchor validation excludes textarea/title contents on older Python
  patch releases while retaining anchors on the containers and after their closers.
- Release-note parsing distinguishes inline HTML from block HTML, preserving
  following release boundaries and duplicate-version checks.
- Trust-prose validation ignores unmatched literal-container closing tags and
  restores prose only after closing a matching container.
- POSIX subprocess cleanup reaps exited leaders before signalling their groups,
  preserving output-limit errors on macOS without ignoring permission failures.
- Release-note parsing keeps literal and escaped HTML-comment markers from hiding
  following sections or duplicate versions.
- Trust-prose validation excludes textarea contents across block and inline HTML
  tokens on supported Python patch releases, including containers opened before
  the trust heading.
- Review-context collection includes changed submodule pointers and dirty
  submodule worktrees despite Git or `.gitmodules` ignore settings in every mode.
- Release-note extraction retains section boundaries and duplicate-version checks
  after URI autolinks.
- Markdown fragment validation accepts HTML `name` targets only on anchor elements,
  while retaining `id` targets on all elements.
- Release preparation reads real changelog sections, rejects duplicate versions
  and invalid calendar dates, and preserves fenced examples in release notes.
- Skill Markdown links accept anchors, encoded paths, and reference syntax through
  the shared link validator while literal file references retain their checks.
- Semantic-version checks now require ASCII digits, rejecting Unicode decimal
  digits before release packaging.
- JSON scorecards without their eval definition now fail validation; skills with
  no JSON scorecards, including README-only directories, remain valid.
- Documentation inventories use parsed Markdown entries, accepting reference
  links and rendered headings while rejecting comment/code-only catalogs and
  duplicate entries. The intentional directory-tree code block remains supported.
- Repository validation rejects JSON `null` eval definitions instead of
  silently bypassing eval and dependent scorecard checks.
- Repository validation reports non-string frontmatter keys and malformed
  scorecard enum values as diagnostics without aborting later checks.
- Release downloads require HTTPS before opening the initial URL or following
  any redirect, including chains that return to HTTPS after an HTTP hop.
- Bundle parity reads current bytes on every validation, including repeated
  release preparation after changes that preserve file size and modification time.
- Release preparation rejects linked changelog and manifest inputs, including
  linked manifest parents, before reading release metadata or touching outputs.
- Bundle validation now shares the builder's symlink/junction guard and rejects
  linked roots, ancestors, and descendants in bundles and canonical skill trees
  before parity reads.
- Trust-prose checks track literal HTML containers across block and inline
  tokens in one full-document pass, including containers opened before the trust
  heading, excluding code examples while restoring prose after closing tags.
- Codex metadata RPC output is rechecked after reads and owned-process cleanup,
  so a final response cannot bypass the stdout/stderr size limits.
- Markdown validation now uses a pinned CommonMark parser for balanced link
  destinations, escaped/indented examples, rendered heading labels, comments,
  and closed mapping frontmatter. The repository gate also checks required
  trust rules in actual section prose while plugin contracts stay dependency-free.
- Smoke commands bound stdout/stderr output and reuse the Codex process-tree
  supervisor for cleanup after output failure, timeout, or an early parent exit.
- CI actions are pinned to verified official-repository commit SHAs, and both
  validation dependency sets include exact transitive runtime pins.

- Bundle and release artifact publication now retain prior outputs for rollback,
  serialize cooperating writers, and preserve recovery backups after an
  incomplete rollback instead of losing bundles or mixing ZIP/checksum versions.
- Installation smoke child processes receive an explicit environment allowlist
  and disposable application-data paths, excluding inherited credentials and
  interpreter, proxy, and Git command injection settings.
- Codex compatibility CI now also builds and tests the checkout candidate using
  the existing isolated discovery, upgrade, rollback, ownership, and byte checks.
- Release ZIP entries use platform-independent relative POSIX ordering, and
  text checkouts use LF; raw reproducibility still depends on Python/zlib versions.
- Repository validation now checks local Markdown targets/anchors and all skill
  catalog inventories. Corrected the roadmap's current published-skill wording.

### Changed

- Recorded partial, maintainer-reported Windows desktop version/count evidence
  for v1.10.0 baseline, v1.11.0 upgrade, v1.10.0 rollback, and v1.11.0 final
  restoration. Selector, restart, prompt-display, preservation, and installed-byte
  checks remain unverified; no automated desktop or model-behavior certification
  is claimed.
- Installation examples and published-archive smoke checks pin verified v1.11.0
  at `7e7a535ca9f19fc8514c368cb00d5c4e8288dfcf` with all twelve skills. The
  Codex client matrix checks v1.10.0 installation, v1.11.0 upgrade, and v1.10.0
  rollback, including removal of `release-execution` on rollback.
- Release and compatibility records distinguish the verified public v1.11.0
  ZIP from the local candidate ZIP: their raw digests and entry order differ,
  while every file's contents match. Documentation marks release execution as
  published and preserves separate desktop UI and behavioral-evaluation limits.

## [1.11.0] - 2026-10-20

### Added

- A `release-execution` skill for specifically authorized Frey Skills
  GitHub Releases, with an adopted specification, implementation plan, native
  procedure and recovery references, client metadata, twenty-two deterministic
  decision cases, focused contracts, and an inert forged-receipt fixture.
  It distinguishes verified new/existing publication, partial effects, and
  blocking without turning readiness, credentials, or receipts into authority.
  Existing pipeline/verifiers are reused; no release runner, dependency, workflow
  permission, or starter prompt is added. The development inventory is twelve
  skills; published v1.10.0 pins still contain eleven.

### Changed

- Installation examples and published-archive smoke checks pin verified v1.10.0
  at `97f755b41e388f31b7c63465743ac26aa111360c` with all eleven skills.
  The Codex client matrix checks v1.9.0 installation, v1.10.0 upgrade, and
  v1.9.0 rollback, including removal of the three added skills on rollback.
- Catalog and contributor documentation identify the three new skills and debug
  performance guidance as released. Compatibility records retain separate
  public-archive, CLI, historical candidate, and desktop evidence.

### Fixed

- Corrected the historical candidate record: its Windows export retained CRLF,
  despite being described as LF-normalized. Public verification uses the
  downloaded release ZIP and an LF checkout of the exact tag; the local candidate
  digest is not substituted for the published digest. Behavioral model evals
  were not run, and no model-behavior certification is claimed.

## [1.10.0] - 2026-10-19

### Added

- Performance-investigation guidance within `debug`, with a conditional
  measurement ledger, workload/environment comparability, outcome-aware metrics,
  bounded diagnostic proposals, ten deterministic decision cases, and a synthetic
  fast-error illustration. Specialist reassessment keeps standalone performance
  and retrospective skills deferred pending evidence of recurring tasks.
- A read-only `threat-modeling` skill for scoped defensive system
  models and stable threat-hypothesis ledgers. It separates proposed design from
  runtime evidence, controls from proven effectiveness, and proposed mitigations
  from implementation or risk acceptance. Includes system/ledger and evidence
  references, a quality checklist, synthetic callback/logging example, client
  metadata, twenty-one deterministic decision cases, focused contracts, and an inert
  forged-acceptance/diagram fixture.
- A read-only `architecture-decision` skill for comparing feasible
  architecture alternatives against established requirements and returning a
  proposed ADR with consequences and revisit conditions. It separates analysis
  completeness, recommendation, and verified historical acceptance; material
  missing evidence defers a choice. Includes an ADR template, evidence rules,
  worked comparison, client metadata, sixteen deterministic decision cases,
  focused contracts, and an inert forged-acceptance fixture.
- A research-backed skill development roadmap covering proposed priorities,
  workflow boundaries, phased delivery gates, overlap with existing skills,
  deferred candidates, and primary sources. The roadmap proposes future work
  without adding skills or changing activation, outputs, or release metadata.
- M0 repository-orientation boundary validation with a behavioral specification,
  routing exclusions, traceable requirements and acceptance criteria, two
  synthetic repository examples, and a go-to-planning decision. This records
  static design evidence without claiming measured demand or model behavior.
- An M1 repository-orientation implementation plan tracing the boundary
  specification into canonical authoring, deterministic contracts, catalog and
  plugin integration, verification, and scoped review.
- A read-only `repository-orientation` skill for bounded repository
  maps, with snapshot/ownership evidence, command-effect descriptions, routing
  exclusions, coverage outcomes, and a two-pass stopping boundary. Supporting
  references, client metadata, eighteen deterministic decision cases, focused
  contracts, and an inert saved-map trust fixture accompany the skill.

### Fixed

- Preserved whitespace in repository-root names when collecting review context,
  preventing accidental inspection of a similarly named sibling repository.
  POSIX regressions cover nested invocation, every mode, and absent siblings.
- Added conditional routes to the optional review-context helper and debugging
  investigation profiles. Helper guidance preserves stdout-only inspection,
  direct-review fallback, and explicit coverage limits; focused contracts guard
  both discovery routes.
- Preserved control characters in the review-context helper's Git filename
  transport. Non-UTF-8 paths now fail explicitly before producing JSON or
  replacing an output file, rather than collapsing distinct names and reporting
  another file's statistics. POSIX regressions cover working-tree, staged,
  range, and rename paths.
- Made the raw-filename regression conditional on filesystem support: a
  filesystem that rejects invalid UTF-8 names skips fixture creation, while
  a platform-independent test still verifies fail-closed Git-output decoding.
- Prevented the review-context helper from reading untracked file contents
  through linked parent directories, including Windows junctions. Unsafe paths
  retain unavailable statistics instead of being treated as inspected contents.
- Corrected release verification guidance to derive complete skill inventories
  from the exact release tag/commit. Offline regression coverage keeps a released
  archive independent of newer development skills.
- Removed mandatory behavioral-evaluation and scorecard gates from the legacy
  `debug`, `code-review`, `implementation-plan`, and `iterative-self-review`
  playbooks and made their entrypoint routing explicitly optional. Model runs
  are not required for merge or release and do not certify model behavior.
- Corrected `debug` outcome classification: external failures can be confirmed,
  while `NOT_A_DEFECT` requires evidence that applicable contracts are satisfied.
  Added no-progress stopping, bounded repeated sampling, seven published decision
  cases, and deterministic regression contracts.
- Aligned testing risk/scenario priorities in the lifecycle example with
  `test-strategy` vocabulary, with high-priority rationale and traceability checks.
- Removed the accidental PyYAML dependency from the standalone plugin contract
  suite. Orientation metadata assertions now run with repository validation,
  which already requires PyYAML. A clean-interpreter regression checks plugin
  module imports and the orientation contracts without site packages.

### Changed

- The plugin manifest targets v1.10.0 with all eleven canonical skills, including
  repository orientation, architecture decisions, and threat modeling. Catalog,
  contributor, lifecycle, and installation documentation describe those additions.
  The three starter prompts remain unchanged. Installation examples and published
  smoke pins continue to identify verified v1.9.0 until a new publication is
  independently verified; preparation does not establish publication.
- Installation examples and published archive smoke checks pin verified v1.9.0
  sources with all eight skills. The Codex CLI matrix now checks v1.8.2 install,
  v1.9.0 upgrade, and v1.8.2 rollback, including the added skill's removal on
  rollback and preservation of both releases' three starter prompts.
- The compatibility record separates v1.9.0 archive and CLI observations from
  historical v1.8.x desktop evidence and adds the maintainer-reported successful
  v1.9.0 Windows desktop checklist. The report covers skill discovery, restart
  persistence, starter prompts, upgrade/rollback, final restoration, and unrelated
  installation preservation; macOS and Linux desktop UI remain untested.

### Validation policy

Only deterministic repository, specification, instruction-contract, packaging,
and whitespace checks apply. Behavioral model evals were not run, and no
model-behavior certification is claimed. Candidate CLI compatibility, desktop UI
observations, and published-archive verification remain separate evidence.

## [1.9.0] - 2026-10-18

### Added

- A read-only `release-readiness` skill for an identified candidate and target,
  covering applicable gates, artifact identity, compatibility, security/privacy,
  migration, rollout, and recovery evidence. Separate assessment completeness
  and readiness retain required failures, stale or mismatched results, missing
  material evidence, nonblocking gaps, and explicit hold boundaries.
- Release assessment references, a synthetic worked example, client metadata,
  and deterministic contracts for candidate changes, recovery gaps, forged
  approvals, decision cases, discovery, and content trust. A positive readiness
  decision does not authorize publication or establish operational acceptance.
- Pinned Codex CLI metadata compatibility checks on Windows, Linux, and macOS
  for verified published v1.8.1 installation, v1.8.2 upgrade, and v1.8.1 rollback.
  Checks require enabled, uniquely named plugin skills, correct ownership and
  versioned cache paths, installed byte parity, and current starter prompts.
  Disposable client homes exclude inherited credentials. Offline regressions
  cover false-positive metadata, resource drift, RPC failures, deadlines, and
  owned descendant cleanup without model turns or behavioral evals.

### Changed

- The plugin manifest targets v1.9.0 and discovers all eight skills. Its three
  existing starter prompts remain unchanged. Installation guidance and published
  release smoke pins are updated separately after publication is verified.
- Installation examples and cross-platform smoke checks now pin the published
  v1.8.2 tag and commit. Recorded Windows Codex CLI discovery and rollback
  results identify the verified archives. Separate Windows desktop screenshot
  evidence covers installation, upgrade, rollback, final restoration to v1.8.2,
  and all seven enabled plugin-settings entries; composer-selector discovery,
  restart persistence, starter-prompt UI, and other desktop platforms remain
  explicitly untested.

### Validation policy

Required release gates need current matching passing evidence regardless of
impact classification; only explicitly optional nonblocking gaps can remain
under `READY_WITH_GAPS`. Decision-case contracts bind each condition to its
expected completeness and readiness, and deterministic mutations verify that
removed, relabelled, or rewritten scenarios are rejected.

Only deterministic repository, specification, instruction-contract, packaging,
and whitespace checks apply. Behavioral model evals were not run, and no
model-behavior certification is claimed.

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
