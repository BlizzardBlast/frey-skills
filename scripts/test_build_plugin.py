#!/usr/bin/env python3
"""Regression tests for the generated plugin bundle builder and validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPOSITORY_ROOT / "scripts" / "build_plugin.py"
VALIDATE_SCRIPT = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"
EXPECTED_SKILLS = ("code-review", "iterative-self-review")


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


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

    def test_build_creates_expected_layout_manifest_and_byte_parity(self) -> None:
        self.assertEqual(self.build(), 0)

        manifest_path = self.output / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "frey-skills")
        self.assertEqual(manifest["version"], "1.0.0")
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

    def test_validator_detects_tampered_bundled_skill(self) -> None:
        self.assertEqual(self.build(), 0)
        skill_file = self.output / "skills" / "code-review" / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nTampered.\n", encoding="utf-8")

        self.assertEqual(self.validate(), 1)


if __name__ == "__main__":
    unittest.main()
