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

    def test_linked_template_parent_is_rejected_before_build_and_release(self) -> None:
        template = self.root / "plugin-template" / ".codex-plugin"
        external = self.root.parent / "owned-template"
        external.mkdir()
        (external / "plugin.json").write_bytes((template / "plugin.json").read_bytes())
        (template / "plugin.json").unlink()
        template.rmdir()
        try:
            template.symlink_to(external, target_is_directory=True)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlinks are not supported here: {exc}")
        with mock.patch.object(build_plugin, "REPOSITORY_ROOT", self.root), mock.patch.object(
            build_plugin, "PLUGIN_TEMPLATE", self.root / "plugin-template"
        ):
            with self.assertRaisesRegex(build_plugin.BuildError, "symlink or junction"):
                build_plugin.build_bundle(self.bundle, force=True)
        errors = validate_plugin_bundle.validate_bundle(self.bundle)
        self.assertTrue(any("symlink or junction" in error for error in errors), errors)
        with self.assertRaisesRegex(ValueError, "plugin validation failed"):
            prepare_release.prepare_release("v1.2.3")
        self.assertFalse(self.output.exists())

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
