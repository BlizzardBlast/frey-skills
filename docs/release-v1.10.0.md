# v1.10.0 release candidate

Prepared on 2026-10-19 from baseline
`a800e15ca5d426c40b4a739e0290c4b8d7af9fd7` on `main`.
Status: **PREPARING**. This record describes a candidate, not publication.

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

Pending execution. Do not treat the plan above as passing evidence.

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

`release-execution` remains a proposed workflow. Its next gate is a requirements
and acceptance-criteria specification for a concrete release target, explicit
authorization and credential boundaries, exact candidate identity, publication
verification, and recovery after partial failure. This candidate does not add
that skill or approve its operational design. Standalone performance and
retrospective skills retain the [M4 evidence gates](specialist-reassessment.md#specialist-dispositions).
