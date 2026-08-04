#!/usr/bin/env python3
"""Regression tests for the generated plugin bundle builder and validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from scripts.repository_layout import discover_skill_names


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPOSITORY_ROOT / "scripts" / "build_plugin.py"
VALIDATE_SCRIPT = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"
EXPECTED_SKILLS = discover_skill_names(REPOSITORY_ROOT)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


@contextmanager
def module_attr(module: Any, name: str, value: Any) -> Iterator[None]:
    previous = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, previous)


class PluginBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self.temp_dir.name) / "frey-skills"
        self.build_plugin = load_module(BUILD_SCRIPT, "build_plugin")
        self.validate_plugin_bundle = load_module(VALIDATE_SCRIPT, "validate_plugin_bundle")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def build(self, *extra_args: str) -> int:
        return self.build_plugin.main([str(self.output), *extra_args])

    def validate(self) -> int:
        return self.validate_plugin_bundle.main([str(self.output)])

    def make_symlink_or_skip(self, target: Path, link: Path, *, target_is_directory: bool = False) -> None:
        try:
            link.symlink_to(target, target_is_directory=target_is_directory)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlinks are not supported here: {exc}")

    def assert_tampered_bundle_is_rejected(self, tamper: Any) -> None:
        if self.output.exists():
            shutil.rmtree(self.output)
        self.assertEqual(self.build(), 0)
        tamper(self.output)
        self.assertEqual(self.validate(), 1)

    def create_fake_repository(self) -> Path:
        fake_root = Path(self.temp_dir.name) / "fake-repository"
        fake_code_review = fake_root / "code-review"
        fake_implementation_plan = fake_root / "implementation-plan"
        fake_iterative = fake_root / "iterative-self-review"
        fake_template = fake_root / "plugin-template" / ".codex-plugin"
        fake_code_review.mkdir(parents=True)
        fake_implementation_plan.mkdir(parents=True)
        fake_iterative.mkdir(parents=True)
        fake_template.mkdir(parents=True)
        (fake_code_review / "SKILL.md").write_text("code review skill\n", encoding="utf-8")
        (fake_implementation_plan / "SKILL.md").write_text("implementation plan skill\n", encoding="utf-8")
        (fake_iterative / "SKILL.md").write_text("iterative review skill\n", encoding="utf-8")
        (fake_template / "plugin.json").write_text("{}", encoding="utf-8")
        return fake_root

    def test_build_creates_expected_layout_manifest_and_byte_parity(self) -> None:
        self.assertEqual(self.build(), 0)

        manifest_path = self.output / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "frey-skills")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("apps", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertEqual(set(path.name for path in (self.output / "skills").iterdir()), set(EXPECTED_SKILLS))

        for skill_name in EXPECTED_SKILLS:
            source = REPOSITORY_ROOT / skill_name
            generated = self.output / "skills" / skill_name
            self.assertEqual(relative_files(generated), relative_files(source))
            for relative_path in relative_files(source):
                self.assertEqual(
                    (generated / relative_path).read_bytes(),
                    (source / relative_path).read_bytes(),
                    f"{skill_name}/{relative_path} should be copied byte-for-byte",
                )

        self.assertEqual(self.validate(), 0)

    def test_build_rejects_non_empty_output_without_force(self) -> None:
        self.output.mkdir(parents=True)
        (self.output / "existing.txt").write_text("do not remove me\n", encoding="utf-8")

        self.assertEqual(self.build(), 1)
        self.assertEqual((self.output / "existing.txt").read_text(encoding="utf-8"), "do not remove me\n")

        self.assertEqual(self.build("--force"), 0)
        self.assertFalse((self.output / "existing.txt").exists())
        self.assertTrue((self.output / ".codex-plugin" / "plugin.json").is_file())

    def test_build_discovers_new_canonical_skill_without_hardcoded_list(self) -> None:
        fake_root = self.create_fake_repository()
        extra_skill = fake_root / "extra-skill"
        extra_skill.mkdir()
        (extra_skill / "SKILL.md").write_text("extra skill\n", encoding="utf-8")
        output = fake_root / "dist" / "frey-skills"

        with module_attr(self.build_plugin, "REPOSITORY_ROOT", fake_root), module_attr(
            self.build_plugin, "PLUGIN_TEMPLATE", fake_root / "plugin-template"
        ):
            self.assertEqual(self.build_plugin.main([str(output), "--force"]), 0)

        self.assertTrue((output / "skills" / "extra-skill" / "SKILL.md").is_file())

    def test_validator_detects_tampered_manifest(self) -> None:
        self.assertEqual(self.build(), 0)
        manifest_path = self.output / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = "9.9.9"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        self.assertEqual(self.validate(), 1)

    def test_validator_detects_tampered_bundled_skill(self) -> None:
        self.assertEqual(self.build(), 0)
        skill_file = self.output / "skills" / "code-review" / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nTampered.\n", encoding="utf-8")

        self.assertEqual(self.validate(), 1)

    def test_validator_rejects_symlink_bundle_root_before_resolving_it(self) -> None:
        self.assertEqual(self.build(), 0)
        symlink_root = Path(self.temp_dir.name) / "bundle-link"
        self.make_symlink_or_skip(self.output, symlink_root, target_is_directory=True)

        self.assertEqual(self.validate_plugin_bundle.main([str(symlink_root)]), 1)

    def test_build_rejects_symlink_output_before_resolving_or_replacing_it(self) -> None:
        target = Path(self.temp_dir.name) / "real-output"
        target.mkdir()
        (target / "keep.txt").write_text("keep me\n", encoding="utf-8")
        self.make_symlink_or_skip(target, self.output, target_is_directory=True)

        self.assertEqual(self.build("--force"), 1)
        self.assertEqual((target / "keep.txt").read_text(encoding="utf-8"), "keep me\n")

    def test_validator_rejects_extra_generated_root_and_manifest_entries(self) -> None:
        tamper_cases = (
            lambda bundle: (bundle / "marketplace.json").write_text("{}", encoding="utf-8"),
            lambda bundle: (bundle / "assets").mkdir(),
            lambda bundle: (bundle / ".codex-plugin" / "marketplace.json").write_text("{}", encoding="utf-8"),
            lambda bundle: (bundle / ".codex-plugin" / "extra.json").write_text("{}", encoding="utf-8"),
        )

        for tamper in tamper_cases:
            with self.subTest(tamper=tamper):
                self.assert_tampered_bundle_is_rejected(tamper)

    def test_validator_rejects_noncanonical_entries_at_skills_root(self) -> None:
        tamper_cases = (
            lambda bundle: (bundle / "skills" / "README.md").write_text("not allowed\n", encoding="utf-8"),
            lambda bundle: (bundle / "skills" / "extra-skill").mkdir(),
        )

        for tamper in tamper_cases:
            with self.subTest(tamper=tamper):
                self.assert_tampered_bundle_is_rejected(tamper)

        def add_symlink(bundle: Path) -> None:
            self.make_symlink_or_skip(bundle / "skills" / "code-review", bundle / "skills" / "skill-link", target_is_directory=True)

        self.assert_tampered_bundle_is_rejected(add_symlink)

    def test_build_rejects_force_output_at_canonical_skill_tree_without_deleting_it(self) -> None:
        fake_root = self.create_fake_repository()
        fake_code_review = fake_root / "code-review"

        with module_attr(self.build_plugin, "REPOSITORY_ROOT", fake_root), module_attr(
            self.build_plugin, "PLUGIN_TEMPLATE", fake_root / "plugin-template"
        ):
            self.assertEqual(self.build_plugin.main([str(fake_code_review), "--force"]), 1)

        self.assertTrue((fake_code_review / "SKILL.md").is_file())
        self.assertEqual((fake_code_review / "SKILL.md").read_text(encoding="utf-8"), "code review skill\n")

    def test_build_rejects_force_output_inside_source_root_unless_it_is_dist(self) -> None:
        fake_root = self.create_fake_repository()

        with module_attr(self.build_plugin, "REPOSITORY_ROOT", fake_root), module_attr(
            self.build_plugin, "PLUGIN_TEMPLATE", fake_root / "plugin-template"
        ):
            unsafe_inside_source = fake_root / "scratch-output"
            self.assertEqual(self.build_plugin.main([str(unsafe_inside_source), "--force"]), 1)

            default_dist_output = fake_root / "dist" / "frey-skills"
            self.assertEqual(self.build_plugin.main([str(default_dist_output), "--force"]), 0)
            self.assertTrue((default_dist_output / ".codex-plugin" / "plugin.json").is_file())

            outside_source = Path(self.temp_dir.name) / "outside-source-output"
            self.assertEqual(self.build_plugin.main([str(outside_source), "--force"]), 0)
        self.assertTrue((outside_source / ".codex-plugin" / "plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
