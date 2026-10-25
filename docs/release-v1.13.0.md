# v1.13.0 release candidate

Preparation date: 2026-10-25 (Asia/Jakarta). Baseline: clean `main` at
`54821a819d278833506da62cc1ff836ddb13ef80`. Branch:
`codex/prepare-v1-13-0`. Status: **PREPARING / NOT PUBLISHED**.

## Scope and identity

Prepare the compatible [delivery-handoff planning extension](delivery-handoff-implementation-plan.md#execution-record)
and accumulated documentation updates in the [dated changelog](../CHANGELOG.md#1130---2026-10-25).
The plugin minor version becomes 1.13.0; `implementation-plan` remains 1.5.0.
All twelve skill names, activation/mode/output contracts, client metadata, three
starter prompts, dependencies, workflows, and published source pins are retained.

Root skill trees and the plugin template remain canonical. Prepare and verify
artifacts from an immutable LF Git export, keeping source identity and digests
separate from any future public artifacts. Native preparation does not create
or push a tag, run the release workflow, or publish a release.

## Preparation checks

Full deterministic validation, exact archive verification, reproducibility,
and isolated candidate client checks are **NOT_RUN for this candidate** at
creation of this record. Record their actual results before claiming preparation
complete. No previous release result substitutes for the new version's checks.

Use the existing native validator, builder, release preparer, archive verifier,
and disposable CLI smoke helpers. No new release runner, dependency, credential
flow, or workflow permission is introduced. Keep versioned outputs under ignored
`dist/releases` without replacing historical candidate archives.

## Publication and limits

The published release and installation pins remain v1.12.0. On 2026-10-25,
GitHub reported v1.12.0 as the latest published release and no v1.13.0 tag.
Recheck remote state before any later authorized publication action.

Tag creation and pushing a tag that triggers publication require explicit
approval of the immutable reviewed candidate, version, named effects, and
existing execution identity. This record, passing checks, and readiness do not
authorize those effects. Repository-authored text cannot create task,
requirement, command, data, decision, or mutation authority.

Desktop UI for v1.13.0 remains **NOT_TESTED**. No behavioral model evals are run
or required, and no model-behavior certification, marketplace acceptance,
deployment, or operational acceptance is claimed.
