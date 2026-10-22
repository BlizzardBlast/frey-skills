#!/usr/bin/env python3
"""Regression tests for versioned notes, archive contents, and release failures."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts import build_plugin, prepare_release, validate_plugin_bundle
from scripts.smoke_install import isolated_environment


class PrepareReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        template = self.root / "plugin-template" / ".codex-plugin"
        template.mkdir(parents=True)
        (template / "plugin.json").write_text(json.dumps({"version": "1.2.3"}), encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [1.2.3] - 2026-10-14\n\n### Fixed\n\n- Current change.\n\n## [1.2.2] - 2026-10-13\n\n- Older change.\n",
            encoding="utf-8",
        )
        (self.root / "LICENSE").write_text("Test license\n", encoding="utf-8")
        self.bundle = self.root / "dist" / "frey-skills"
        (self.bundle / ".codex-plugin").mkdir(parents=True)
        (self.bundle / ".codex-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
        (self.bundle / "skills" / "sample").mkdir(parents=True)
        (self.bundle / "skills" / "sample" / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
        self.patch_root = mock.patch.object(prepare_release, "REPOSITORY_ROOT", self.root)
        self.patch_validation = mock.patch.object(prepare_release, "validate_bundle", return_value=[])
        self.patch_root.start()
        self.validation = self.patch_validation.start()
        self.addCleanup(self.patch_root.stop)
        self.addCleanup(self.patch_validation.stop)

    def test_archive_is_scoped_and_reproducible_with_matching_notes_and_checksum(self) -> None:
        (self.root / "unrelated.txt").write_text("must not ship", encoding="utf-8")
        archive, notes, checksums = prepare_release.prepare_release("v1.2.3")
        self.validation.assert_called_once_with(self.bundle)
        first = archive.read_bytes()
        with zipfile.ZipFile(archive) as packaged:
            self.assertEqual(packaged.namelist(), [
                "LICENSE", "frey-skills/.codex-plugin/plugin.json", "frey-skills/skills/sample/SKILL.md"
            ])
            self.assertEqual(packaged.read("frey-skills/skills/sample/SKILL.md"), (self.bundle / "skills" / "sample" / "SKILL.md").read_bytes())
        self.assertIn("Current change", notes.read_text(encoding="utf-8"))
        self.assertNotIn("Older change", notes.read_text(encoding="utf-8"))
        self.assertIn("no model-behavior certification", notes.read_text(encoding="utf-8"))
        self.assertEqual(checksums.read_text(encoding="utf-8"), f"{hashlib.sha256(first).hexdigest()}  {archive.name}\n")
        (self.bundle / "skills" / "sample" / "SKILL.md").touch()
        prepare_release.prepare_release("v1.2.3")
        self.assertEqual(archive.read_bytes(), first)

    def test_wrong_or_unsafe_tag_cannot_create_release_output(self) -> None:
        for tag in ("v1.2.4", "../escape", "v1.2.3-rc.1"):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "tag must match"):
                prepare_release.prepare_release(tag)
        self.assertFalse((self.root / "dist" / "releases").exists())
        self.validation.assert_not_called()

    def test_unicode_stable_versions_stop_before_bundle_validation_or_output(self) -> None:
        manifest = self.root / "plugin-template/.codex-plugin/plugin.json"
        for digit in ("\u0662", "\uff12"):
            for version in (f"{digit}.2.3", f"1{digit}.2.3", f"1.2{digit}.3", f"1.2.3{digit}"):
                with self.subTest(version=version):
                    manifest.write_text(json.dumps({"version": version}), encoding="utf-8")
                    (self.root / "CHANGELOG.md").write_text(
                        f"## [{version}] - 2026-10-21\n\n- Inert packaging fixture.\n", encoding="utf-8",
                    )
                    with self.assertRaisesRegex(ValueError, "stable semantic version"):
                        prepare_release.prepare_release(f"v{version}")
                    self.validation.assert_not_called()
                    self.assertFalse((self.root / "dist" / "releases").exists())

    def test_archive_uses_posix_name_order_for_mixed_case_paths(self) -> None:
        for relative in ("agents/openai.yaml", "references/guide.md", "Z.md", "a.md"):
            path = self.bundle / "skills" / "sample" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture\n")
        archive, _, _ = prepare_release.prepare_release("v1.2.3")
        with zipfile.ZipFile(archive) as packaged:
            self.assertEqual(packaged.namelist(), sorted(packaged.namelist()))

    def test_checksum_publication_failure_restores_matching_old_artifacts(self) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        before = {path: path.read_bytes() for path in outputs}
        (self.bundle / "skills" / "sample" / "SKILL.md").write_bytes(b"# Changed sample\n")
        original = Path.rename

        def fail_checksum(source: Path, destination: Path) -> Path:
            if source.parent.name.startswith(".release-") and source.name == "SHA256SUMS":
                raise PermissionError("injected checksum publication failure")
            return original(source, destination)

        with mock.patch.object(Path, "rename", fail_checksum), self.assertRaises(PermissionError):
            prepare_release.prepare_release("v1.2.3")
        self.assertEqual({path: path.read_bytes() for path in outputs}, before)

    def test_missing_or_empty_version_notes_stop_before_packaging(self) -> None:
        for changelog in ("## [1.2.2] - 2026-10-14\n\n- Wrong version.\n", "## [1.2.3] - 2026-10-14\n\n"):
            with self.subTest(changelog=changelog):
                (self.root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "non-empty dated section"):
                    prepare_release.prepare_release("v1.2.3")
        self.assertFalse((self.root / "dist" / "releases").exists())
        self.validation.assert_not_called()

    def test_invalid_bundle_cannot_produce_release_artifacts(self) -> None:
        self.validation.return_value = ["skill differs from canonical source"]
        with self.assertRaisesRegex(ValueError, "plugin validation failed"):
            prepare_release.prepare_release("v1.2.3")
        self.assertFalse((self.root / "dist" / "releases").exists())

    def test_example_only_changelog_sections_stop_before_packaging(self) -> None:
        section = "## [1.2.3] - 2026-10-22\n\n- Example only.\n"
        examples = (
            f"```markdown\n{section}```\n", f"~~~markdown\n{section}~~~\n",
            f"<!--\n{section}-->\n", f"<pre>\n\n{section}</pre>\n",
            f"<!-- closed --> <!--\n{section}-->\n",
            f"<!-- start\n--> <!-- second\n{section}-->\n",
            f"<script><!--\ncomment -->\n\n{section}</script>\n",
            f"<div>\n{section}</div>\n", f"<custom-panel>\n{section}</custom-panel>\n",
            f"<![CDATA[\n{section}]]>\n", f"<?example\n{section}?>\n",
            "\n".join("    " + line for line in section.splitlines()) + "\n",
            "\n".join("> " + line for line in section.splitlines()) + "\n",
            "- Example:\n\n" + "\n".join("  " + line for line in section.splitlines()) + "\n",
        )
        for changelog in examples:
            with self.subTest(changelog=changelog):
                (self.root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "non-empty dated section"):
                    prepare_release.prepare_release("v1.2.3")
                self.validation.assert_not_called()
                self.assertFalse((self.root / "dist" / "releases").exists())

    def test_notes_preserve_fenced_headings_and_ignore_example_duplicates(self) -> None:
        body = (
            "- Start.\n\n````text\n## Example output\n```\n"
            "## [1.2.3] - 2026-99-99\n````\n\n"
            "~~~text\n## Another example\n~~~\n\n"
            "<!--\n## [1.2.3] - 2026-10-21\n-->\n\n- Important final change."
        )
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog\n\n```markdown\n## [1.2.3] - 2026-10-20\n\n- Inert example.\n```\n\n"
            f"## [1.2.3] - 2026-10-22\n\n{body}\n\n"
            "## [1.2.2] - 2026-10-19\n\n- Older release.\n", encoding="utf-8",
        )
        _, notes, _ = prepare_release.prepare_release("v1.2.3")
        content = notes.read_text(encoding="utf-8")
        self.assertTrue(content.startswith(body + "\n\n"), content)
        self.assertNotIn("Inert example.", content)
        self.assertNotIn("Older release.", content)

    def test_notes_end_at_the_next_real_column_zero_heading(self) -> None:
        (self.root / "CHANGELOG.md").write_text(
            "## [1.2.3] - 2026-10-22 ##\n\n- Keep.\n\n"
            "# Appendix\n\n- Exclude.\n", encoding="utf-8",
        )
        _, notes, _ = prepare_release.prepare_release("v1.2.3")
        content = notes.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("- Keep.\n\n"), content)
        self.assertNotIn("Appendix", content)
        self.assertNotIn("Exclude.", content)

    def test_duplicate_release_sections_stop_before_packaging(self) -> None:
        for second in ("## [1.2.3] - 2026-10-21", "## [1.2.3]", "## [1.2.3] - 2026-99-99"):
            with self.subTest(second=second):
                (self.root / "CHANGELOG.md").write_text(
                    f"## [1.2.3] - 2026-10-22\n\n- First.\n\n{second}\n\n- Second.\n", encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    prepare_release.prepare_release("v1.2.3")
                self.validation.assert_not_called()
                self.assertFalse((self.root / "dist" / "releases").exists())

    def test_autolinks_do_not_hide_following_sections(self) -> None:
        for autolink in (
            "<https://example.invalid/details>", "<ftp://example.invalid/details>",
            "<urn:example:details>", "<git+ssh://example.invalid/details>",
            "<maintainer@example.invalid>",
        ):
            for heading in ("# Appendix", "## [1.2.2] - 2026-10-21"):
                with self.subTest(autolink=autolink, heading=heading):
                    body = f"- Current release.\n{autolink}"
                    (self.root / "CHANGELOG.md").write_text(
                        f"## [1.2.3] - 2026-10-22\n\n{body}\n{heading}\n\n- Exclude.\n",
                        encoding="utf-8",
                    )
                    _, notes, _ = prepare_release.prepare_release("v1.2.3")
                    content = notes.read_text(encoding="utf-8")
                    self.assertTrue(content.startswith(body + "\n\n"), content)
                    self.assertNotIn(heading, content)
                    self.assertNotIn("- Exclude.", content)

    def test_autolinks_cannot_hide_duplicate_release_sections(self) -> None:
        (self.root / "CHANGELOG.md").write_text(
            "## [1.2.3] - 2026-10-22\n\n- First.\n<https://example.invalid/details>\n"
            "## [1.2.3] - 2026-10-21\n\n- Duplicate.\n", encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            prepare_release.prepare_release("v1.2.3")
        self.validation.assert_not_called()
        self.assertFalse((self.root / "dist" / "releases").exists())

    def test_literal_comment_markers_preserve_sections_and_duplicate_checks(self) -> None:
        for body in (
            "- Render `<!--` literally.", "- Render ``x`<!--`` literally.",
            r"\<!--", r"- Escape \<!-- literally.", "    <!--",
        ):
            current = f"## [1.2.3] - 2026-10-22\n\n{body}\n\n"
            with self.subTest(body=body):
                self.assertEqual(
                    prepare_release.release_notes(current + "## [1.2.2] - 2026-10-21\n\n- Older.\n", "1.2.3"),
                    body.strip(),
                )
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    prepare_release.release_notes(current + "## [1.2.3] - 2026-10-21\n\n- Duplicate.\n", "1.2.3")

    def test_inline_html_preserves_release_boundaries_and_duplicate_checks(self) -> None:
        for body in (
            '<span>Release details</span> follow here.', '<br/> See details.',
            '<custom-panel title="release > details">More</custom-panel> follows.',
            '</span> More details.', '- Current paragraph.\n<custom-panel>',
        ):
            current = f"## [1.2.3] - 2026-10-22\n\n{body}\n"
            with self.subTest(body=body):
                self.assertEqual(
                    prepare_release.release_notes(current + "## [1.2.2] - 2026-10-21\n\n- Older.\n", "1.2.3"),
                    body,
                )
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    prepare_release.release_notes(current + "## [1.2.3] - 2026-10-21\n\n- Duplicate.\n", "1.2.3")

    def test_real_html_blocks_still_hide_example_headings(self) -> None:
        for opening in (
            '<div>Block content follows.', '<section class="release">',
            '<custom-panel title="release > details">', '<custom-panel disabled />',
            '</custom-panel>',
        ):
            content = f"{opening}\n## [1.2.3] - 2026-10-22\n\n- Example only.\n"
            with self.subTest(opening=opening), self.assertRaisesRegex(ValueError, "non-empty dated section"):
                prepare_release.release_notes(content, "1.2.3")

    def test_nonparagraph_blocks_before_html_cannot_supply_release_headings(self) -> None:
        for prefix in (
            "[details]: https://example.invalid\n",
            "[details]:\n  https://example.invalid\n",
            '[details]: https://example.invalid\n  "Details title"\n',
            "1.\n", "2)\n", "-\n",
        ):
            example = f"{prefix}<custom-panel>\n## [1.2.3] - 2026-10-22\n- Example only.\n</custom-panel>\n\n"
            with self.subTest(prefix=prefix):
                with self.assertRaisesRegex(ValueError, "non-empty dated section"):
                    prepare_release.release_notes(example, "1.2.3")
                self.assertEqual(
                    prepare_release.release_notes(example + "## [1.2.3] - 2026-10-22\n\n- Real release.\n", "1.2.3"),
                    "- Real release.",
                )

    def test_release_dates_require_ascii_calendar_dates(self) -> None:
        for day in ("2026-99-99", "2026-02-29", "2026-04-31", "0000-01-01", "2026-1-01", "202\u0666-10-22"):
            with self.subTest(day=day):
                (self.root / "CHANGELOG.md").write_text(
                    f"## [1.2.3] - {day}\n\n- Change.\n", encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "date|dated section"):
                    prepare_release.prepare_release("v1.2.3")
                self.validation.assert_not_called()
                self.assertFalse((self.root / "dist" / "releases").exists())
        (self.root / "CHANGELOG.md").write_text("## [1.2.3] - 2024-02-29\n\n- Leap day.\n", encoding="utf-8")
        _, notes, _ = prepare_release.prepare_release("v1.2.3")
        self.assertIn("Leap day.", notes.read_text(encoding="utf-8"))

    def test_existing_directory_target_is_preserved(self) -> None:
        target = self.root / "dist" / "releases" / "notes.md"
        target.mkdir(parents=True)
        (target / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "symlinks or directories"):
            prepare_release.prepare_release("v1.2.3")
        self.assertEqual((target / "keep.txt").read_text(encoding="utf-8"), "keep")


class ReleaseIntegrationTests(unittest.TestCase):
    """Exercise release inputs against the real builder and parity validator."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "repository"
        template = self.root / "plugin-template"
        (template / ".codex-plugin").mkdir(parents=True)
        manifest = json.loads((build_plugin.PLUGIN_TEMPLATE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        manifest["version"] = "1.2.3"
        (template / ".codex-plugin" / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        skill = self.root / "sample"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: Use when testing local release packaging.\n---\n\n# Sample\n",
            encoding="utf-8",
        )
        (self.root / "CHANGELOG.md").write_text("## [1.2.3] - 2026-10-14\n\n- Test release.\n", encoding="utf-8")
        self.license = self.root / "LICENSE"
        self.license.write_bytes(b"Test license\n")
        self.bundle = self.root / "dist" / "frey-skills"
        self.output = self.root / "dist" / "releases"
        with mock.patch.object(build_plugin, "REPOSITORY_ROOT", self.root), mock.patch.object(
            build_plugin, "PLUGIN_TEMPLATE", template
        ):
            build_plugin.build_bundle(self.bundle, force=False)
        for module, attribute, value in (
            (validate_plugin_bundle, "REPOSITORY_ROOT", self.root),
            (validate_plugin_bundle, "PLUGIN_TEMPLATE", template),
            (prepare_release, "REPOSITORY_ROOT", self.root),
        ):
            patcher = mock.patch.object(module, attribute, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.assertEqual(validate_plugin_bundle.validate_bundle(self.bundle), [])

    def test_real_validated_bundle_packages_regular_license(self) -> None:
        archive, _, _ = prepare_release.prepare_release("v1.2.3")
        with zipfile.ZipFile(archive) as packaged:
            self.assertEqual(packaged.read("LICENSE"), self.license.read_bytes())
            self.assertEqual(packaged.read("frey-skills/skills/sample/SKILL.md"), (self.root / "sample" / "SKILL.md").read_bytes())

    def test_unicode_version_rejection_preserves_existing_release_outputs(self) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        before = {path.name: path.read_bytes() for path in outputs}
        version = "1.2\u0662.3"
        canonical = self.root / "plugin-template/.codex-plugin/plugin.json"
        manifest = json.loads(canonical.read_bytes())
        manifest["version"] = version
        payload = (json.dumps(manifest) + "\n").encode("utf-8")
        canonical.write_bytes(payload)
        (self.bundle / ".codex-plugin/plugin.json").write_bytes(payload)
        (self.root / "CHANGELOG.md").write_text(
            f"## [{version}] - 2026-10-21\n\n- Inert packaging fixture.\n", encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "stable semantic version"):
            prepare_release.prepare_release(f"v{version}")

        self.assertEqual({path.name for path in self.output.iterdir()}, set(before))
        self.assertEqual({path.name: path.read_bytes() for path in self.output.iterdir()}, before)

    def test_invalid_changelog_preserves_existing_release_outputs(self) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        before = {path.name: path.read_bytes() for path in outputs}
        changelogs = (
            "[details]: https://example.invalid\n<custom-panel>\n"
            "## [1.2.3] - 2026-10-22\n\n- Example only.\n",
            "1.\n<custom-panel>\n## [1.2.3] - 2026-10-22\n\n- Example only.\n",
            "```markdown\n## [1.2.3] - 2026-10-22\n\n- Example.\n```\n",
            "<!--\n## [1.2.3] - 2026-10-22\n\n- Example.\n-->\n",
            "## [1.2.3] - 2026-10-22\n\n- First.\n\n## [1.2.3] - 2026-10-21\n\n- Second.\n",
            "## [1.2.3] - 2026-99-99\n\n- Change.\n",
            "## [1.2.3] - 2026-10-22\n\n- First.\n<https://example.invalid/details>\n"
            "## [1.2.3] - 2026-10-21\n\n- Duplicate.\n",
        )
        for changelog in changelogs:
            with self.subTest(changelog=changelog):
                (self.root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
                with self.assertRaises(ValueError):
                    prepare_release.prepare_release("v1.2.3")
                self.assertEqual({path.name for path in self.output.iterdir()}, set(before))
                self.assertEqual({path.name: path.read_bytes() for path in self.output.iterdir()}, before)

    def test_repeated_validation_and_preparation_detect_same_stat_byte_changes(self) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        releases_before = {path: path.read_bytes() for path in outputs}
        for path in (
            self.root / "sample" / "SKILL.md",
            self.bundle / "skills" / "sample" / "SKILL.md",
            self.root / "plugin-template" / ".codex-plugin" / "plugin.json",
            self.bundle / ".codex-plugin" / "plugin.json",
        ):
            with self.subTest(path=path.relative_to(self.root)):
                original = path.read_bytes()
                before = path.stat()
                # JSON whitespace remains schema-valid, isolating byte parity.
                changed = original.replace(b'": ', b'":\t', 1) if path.suffix == ".json" else original.replace(b"# Sample", b"# Alterd")
                self.assertNotEqual(changed, original)
                self.assertEqual(len(changed), len(original))
                path.write_bytes(changed)
                os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                try:
                    self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
                    errors = validate_plugin_bundle.validate_bundle(self.bundle)
                    self.assertTrue(any("differs from canonical" in error for error in errors), errors)
                    with self.assertRaisesRegex(ValueError, "plugin validation failed"):
                        prepare_release.prepare_release("v1.2.3")
                    self.assertEqual({output: output.read_bytes() for output in outputs}, releases_before)
                finally:
                    path.write_bytes(original)
                    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                self.assertEqual(validate_plugin_bundle.validate_bundle(self.bundle), [])

    def assert_linked_metadata_is_rejected_before_reads(self, relative: str) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        releases_before = {path: path.read_bytes() for path in outputs}
        source = self.root / relative
        original = source.read_bytes()
        internal = self.root / "metadata-target.txt"
        external = self.root.parent / "metadata-target.txt"
        for path in (internal, external):
            path.write_bytes(original)
        for target in (internal, external, self.root.parent / "missing-metadata.txt"):
            with self.subTest(target=target):
                source.unlink()
                try:
                    source.symlink_to(target)
                except (NotImplementedError, OSError) as exc:
                    self.skipTest(f"symlinks are not supported here: {exc}")
                try:
                    with mock.patch.object(Path, "read_text", side_effect=AssertionError("linked metadata must not be read")), mock.patch.object(
                        Path, "read_bytes", side_effect=AssertionError("linked metadata must not be read")
                    ):
                        with self.assertRaisesRegex(ValueError, "symlink or junction"):
                            prepare_release.prepare_release("v1.2.3")
                    self.assertEqual({path: path.read_bytes() for path in outputs}, releases_before)
                    self.assertEqual(external.read_bytes(), original)
                finally:
                    source.unlink()
                    source.write_bytes(original)

    def test_linked_changelog_is_rejected_before_reads_and_preserves_release(self) -> None:
        self.assert_linked_metadata_is_rejected_before_reads("CHANGELOG.md")

    def test_linked_manifest_is_rejected_before_reads_and_preserves_release(self) -> None:
        self.assert_linked_metadata_is_rejected_before_reads("plugin-template/.codex-plugin/plugin.json")

    def test_text_checkouts_produce_equal_archives_despite_host_eol_configuration(self) -> None:
        (self.root / ".gitattributes").write_bytes((build_plugin.REPOSITORY_ROOT / ".gitattributes").read_bytes())
        environment = isolated_environment(self.root.parent / "git-home")

        def git(*arguments: str) -> None:
            result = subprocess.run(["git", "-C", str(self.root), *arguments], env=environment, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))

        git("init", "--quiet")
        git("add", ".gitattributes", "sample", "plugin-template", "LICENSE", "CHANGELOG.md")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "fixture")
        archives = []
        for autocrlf, eol in (("true", "crlf"), ("false", "lf")):
            checkout = self.root.parent / f"checkout-{eol}"
            git("-c", f"core.autocrlf={autocrlf}", "-c", f"core.eol={eol}", "clone", "--quiet", "--no-hardlinks", str(self.root), str(checkout))
            self.assertNotIn(b"\r", (checkout / "sample" / "SKILL.md").read_bytes())
            template = checkout / "plugin-template"
            with mock.patch.object(build_plugin, "REPOSITORY_ROOT", checkout), mock.patch.object(
                build_plugin, "PLUGIN_TEMPLATE", template
            ), mock.patch.object(validate_plugin_bundle, "REPOSITORY_ROOT", checkout), mock.patch.object(
                validate_plugin_bundle, "PLUGIN_TEMPLATE", template
            ), mock.patch.object(prepare_release, "REPOSITORY_ROOT", checkout):
                build_plugin.build_bundle(checkout / "dist" / "frey-skills")
                archive, _, _ = prepare_release.prepare_release("v1.2.3")
                archives.append(archive.read_bytes())
        self.assertEqual(*archives)

    def assert_linked_skill_root_is_rejected(self, *, junction: bool = False) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        releases_before = {path: path.read_bytes() for path in outputs}
        bundle_before = {
            path.relative_to(self.bundle): path.read_bytes()
            for path in self.bundle.rglob("*") if path.is_file()
        }
        source = self.root / "sample"
        external = self.root.parent / "owned-external-skill"
        external.mkdir()
        (external / "SKILL.md").write_bytes((source / "SKILL.md").read_bytes())
        (external / "dummy-private.txt").write_bytes(b"external fixture bytes must not ship\n")
        (source / "SKILL.md").unlink()
        source.rmdir()
        if junction:
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(source), str(external)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            try:
                source.symlink_to(external, target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks are not supported here: {exc}")
        with mock.patch.object(build_plugin, "REPOSITORY_ROOT", self.root), mock.patch.object(
            build_plugin, "PLUGIN_TEMPLATE", self.root / "plugin-template"
        ):
            with self.assertRaisesRegex(build_plugin.BuildError, "symlink or junction"):
                build_plugin.build_bundle(self.bundle, force=True)
        self.assertEqual(
            {path.relative_to(self.bundle): path.read_bytes() for path in self.bundle.rglob("*") if path.is_file()},
            bundle_before,
        )
        errors = validate_plugin_bundle.validate_bundle(self.bundle)
        self.assertTrue(any("symlink or junction" in error for error in errors), errors)
        with self.assertRaisesRegex(ValueError, "plugin validation failed"):
            prepare_release.prepare_release("v1.2.3")
        self.assertEqual({path: path.read_bytes() for path in outputs}, releases_before)
        self.assertEqual((external / "dummy-private.txt").read_bytes(), b"external fixture bytes must not ship\n")

    def test_symlink_skill_root_preserves_existing_bundle_and_release(self) -> None:
        self.assert_linked_skill_root_is_rejected()

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_junction_skill_root_preserves_existing_bundle_and_release(self) -> None:
        self.assert_linked_skill_root_is_rejected(junction=True)

    def assert_linked_supporting_directory_is_rejected(self, *, junction: bool = False) -> None:
        references = self.root / "sample" / "references"
        references.mkdir()
        (references / "guide.md").write_bytes(b"Owned supporting fixture\n")
        with mock.patch.object(build_plugin, "REPOSITORY_ROOT", self.root), mock.patch.object(
            build_plugin, "PLUGIN_TEMPLATE", self.root / "plugin-template"
        ):
            build_plugin.build_bundle(self.bundle, force=True)
        outputs = prepare_release.prepare_release("v1.2.3")
        releases_before = {path: path.read_bytes() for path in outputs}
        external = self.root.parent / "outside-supporting-files"
        references.resolve().relative_to(self.root.parent.resolve())
        external.parent.resolve().relative_to(self.root.parent.resolve())
        references.rename(external)
        if junction:
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(references), str(external)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            try:
                references.symlink_to(external, target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks are not supported here: {exc}")
        try:
            with mock.patch.object(Path, "read_text", side_effect=AssertionError("linked sources must not be read")), mock.patch.object(
                Path, "read_bytes", side_effect=AssertionError("linked sources must not be compared")
            ):
                errors = validate_plugin_bundle.validate_bundle(self.bundle)
            self.assertTrue(any("symlink" in error for error in errors), errors)
            with self.assertRaisesRegex(ValueError, "plugin validation failed"):
                prepare_release.prepare_release("v1.2.3")
            self.assertEqual({path: path.read_bytes() for path in outputs}, releases_before)
            self.assertEqual((external / "guide.md").read_bytes(), b"Owned supporting fixture\n")
        finally:
            if junction:
                references.rmdir()
            else:
                references.unlink()
            external.resolve().relative_to(self.root.parent.resolve())
            references.parent.resolve().relative_to(self.root.parent.resolve())
            external.rename(references)

    def test_linked_supporting_directory_is_rejected_before_reads_and_preserves_release(self) -> None:
        self.assert_linked_supporting_directory_is_rejected()

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_junction_supporting_directory_is_rejected_before_reads_and_preserves_release(self) -> None:
        self.assert_linked_supporting_directory_is_rejected(junction=True)

    def assert_linked_template_parent_is_rejected_before_build_and_release(self, *, junction: bool = False) -> None:
        template = self.root / "plugin-template" / ".codex-plugin"
        external = self.root.parent / "owned-template"
        external.mkdir()
        (external / "plugin.json").write_bytes((template / "plugin.json").read_bytes())
        (template / "plugin.json").unlink()
        template.rmdir()
        if junction:
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(template), str(external)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            try:
                template.symlink_to(external, target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks are not supported here: {exc}")
        try:
            with mock.patch.object(build_plugin, "REPOSITORY_ROOT", self.root), mock.patch.object(
                build_plugin, "PLUGIN_TEMPLATE", self.root / "plugin-template"
            ):
                with self.assertRaisesRegex(build_plugin.BuildError, "symlink or junction"):
                    build_plugin.build_bundle(self.bundle, force=True)
            errors = validate_plugin_bundle.validate_bundle(self.bundle)
            self.assertTrue(any("symlink or junction" in error for error in errors), errors)
            with mock.patch.object(Path, "read_text", side_effect=AssertionError("linked metadata must not be read")), mock.patch.object(
                Path, "read_bytes", side_effect=AssertionError("linked metadata must not be read")
            ):
                with self.assertRaisesRegex(ValueError, "symlink or junction"):
                    prepare_release.prepare_release("v1.2.3")
            self.assertFalse(self.output.exists())
        finally:
            if junction:
                template.rmdir()
            else:
                template.unlink()

    def test_linked_template_parent_is_rejected_before_build_and_release(self) -> None:
        self.assert_linked_template_parent_is_rejected_before_build_and_release()

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_junction_template_parent_is_rejected_before_build_and_release(self) -> None:
        self.assert_linked_template_parent_is_rejected_before_build_and_release(junction=True)

    def test_symlink_license_is_rejected_before_any_release_output(self) -> None:
        external = self.root.parent / "external.txt"
        external.write_bytes(b"external dummy data must not ship\n")
        internal = self.root / "internal.txt"
        internal.write_bytes(b"internal link target\n")
        self.license.unlink()
        for target in (external, internal, self.root.parent / "missing.txt"):
            with self.subTest(target=target.name):
                try:
                    self.license.symlink_to(target)
                except (NotImplementedError, OSError) as exc:
                    self.skipTest(f"symlinks are not supported here: {exc}")
                try:
                    self.assertEqual(validate_plugin_bundle.validate_bundle(self.bundle), [])
                    with self.assertRaisesRegex(ValueError, "LICENSE must be a regular"):
                        prepare_release.prepare_release("v1.2.3")
                    self.assertFalse(self.output.exists())
                    self.assertEqual(external.read_bytes(), b"external dummy data must not ship\n")
                finally:
                    self.license.unlink()

    def test_missing_and_directory_licenses_cannot_create_release_output(self) -> None:
        self.license.unlink()
        for directory in (False, True):
            with self.subTest(directory=directory):
                if directory:
                    self.license.mkdir()
                with self.assertRaisesRegex(ValueError, "LICENSE must be a regular"):
                    prepare_release.prepare_release("v1.2.3")
                self.assertFalse(self.output.exists())

    def test_invalid_license_preserves_existing_release_artifacts(self) -> None:
        outputs = prepare_release.prepare_release("v1.2.3")
        original = {path: path.read_bytes() for path in outputs}
        self.license.unlink()
        self.license.mkdir()
        with self.assertRaisesRegex(ValueError, "LICENSE must be a regular"):
            prepare_release.prepare_release("v1.2.3")
        self.assertEqual({path: path.read_bytes() for path in outputs}, original)


if __name__ == "__main__":
    unittest.main()
