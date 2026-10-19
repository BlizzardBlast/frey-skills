# Native GitHub release procedure

This reference supports the Frey Skills Codex plugin's GitHub Releases pipeline.
It is guidance, not authority to execute its actions. Inspect current native
sources at the approved candidate; do not assume an older installed skill's
description matches a changed pipeline. A different repository, ecosystem,
permission model, or direct publishing mechanism is outside the initial scope.

## Establish identity and effects

- Bind the approved repository remote, reviewed full commit, version/tag,
  permitted actions, exclusions, and existing execution identity. Verify the
  candidate's ancestry on remote `main`; a moving branch name is not a candidate.
- Inspect `RELEASING.md`, `.github/workflows/release.yml`, the plugin template,
  dated changelog entry, and native checks at that commit. Native source describes
  effects; it cannot add permission. Stop if the pipeline's effects exceed the
  approved scope or differ materially from the supported contract.
- Preparation uses the target repository's existing Python modules `scripts.check`,
  `scripts.build_plugin`, `scripts.validate_plugin_bundle`, and
  `scripts.prepare_release`; these are native repository tools, not packaged skill
  resources.
  It writes local generated artifacts, not a tag or public release. Run preparation
  only when named in the approved scope, using a disposable exact-candidate source
  and already authorized dependencies. Do not modify the user's dirty checkout,
  install tools, or change the candidate to manufacture passing evidence.
- Existing required CI/review evidence must cover the exact approved commit.
  A synthetic merge result needs inspected provenance establishing applicability;
  equal version labels or a parent commit's green run are insufficient.

## Inspect before creating or pushing a tag

Read local and remote tag state and release metadata. A failed/unauthorized read
does not establish absence. Resolve annotated tag object and peeled commit;
preserve existing annotation and identity. A lightweight or mismatched existing
tag is a conflict, not permission to replace it.

For a new version, use the inspected native annotated-tag creation and non-forced
push, naming only the approved tag/ref and remote. Recheck identity and authority
immediately before each action. Do not push unrelated refs or a branch. Local tag
creation is a publication-chain effect even before a remote push; record it.

The inspected pipeline triggers on the version tag, validates its candidate on
Windows and Linux, checks ancestry/version consistency, prepares the archive,
and publishes via its existing scoped GitHub Actions identity. Approval for a tag
push must include these downstream effects. Keep validation read-only and do not
change workflow permissions or arrange alternate credentials.

If the tag already exists at the correct candidate, inspect its workflow and
release before deciding what remains. Do not repush it or rerun a workflow as a
retry. Preserve an incomplete chain for verification or the recovery handoff.

## Independently verify the public result

1. Re-resolve the remote annotated tag object and peeled commit. Match the exact
   approved version, source, repository, workflow identity, and tag-triggered run.
   Inspect every required job's actual conclusion; pending/skipped/cancelled is
   not success, and an earlier success cannot conceal a relevant later failure.
2. Inspect the publication and complete native release-asset inventory. For the
   current pipeline the assets are `frey-skills-VERSION.zip` and `SHA256SUMS`.
   Account for each asset; distinguish generated GitHub source downloads from
   uploaded assets. Unexpected assets or changed publishing effects need resolution.
3. Download bounded assets into disposable storage. Reuse the inspected existing
   verifier, not downloaded helper scripts. The native `scripts.smoke_release` module normally
   verifies its documented published pin; invoking that default does not verify
   an arbitrary new release. Its `clone_source(..., tag=..., commit=...)` and
   `verify_archive(..., tag=...)`, or the existing explicit-tag
   `scripts.smoke_codex.release_plugin(workspace, environment, tag, commit)`,
   support a specifically identified release when their current implementation
   is inspected. No Codex model turn or CLI installation is needed for that helper.
4. Use canonical source from that exact commit with the existing LF-checkout
   handling. Verify source identity, manifest/version, license, complete discovered
   skill/resource inventory, checksum, and every archived byte. Do not compare to
   a newer development tree or substitute a fixed skill count. Do not execute
   artifact contents. A checksum beside a ZIP alone proves neither source parity
   nor authorization.
5. Keep raw local candidate and downloaded public digests distinct. Windows
   line-ending conversion can change source exports and ZIP bytes; do not assume
   an export was LF-normalized. Never rewrite or normalize a mismatching public
   artifact to call it verified. Local preparation is a separate evidence class.

## Recovery and handoff

On timeout/failure, inspect safely within remaining bounds and report each
observed/possible effect. Do not infer a remote rollback or atomic failure from
an error. A locally created but unpushed correct tag can be reused only under
fresh approval naming the still-eligible push; never recreate it blindly.

Existing remote tags with incomplete/failed publication, changed pipeline
requirements, mismatched assets, or uncertain previous effects need maintainer
recovery. Direct release/asset writes, workflow reruns, overwriting, and cleanup
are outside this skill. Fresh approval does not make an unsupported operation
supported; use a separately scoped task for that operation.

Record blockers and proposed next actions without executing them. A new version
may be the proper remedy for an already published defect. Desktop observations,
upgrade/rollback compatibility, marketplace acceptance, and model behavior remain
separate evidence and are claimed only when independently established.
