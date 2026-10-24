#!/usr/bin/env python3
"""Regression tests for the generated plugin bundle builder and validator."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from unittest import mock

from scripts.repository_layout import discover_skill_names, is_runtime_artifact


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
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file() and not is_runtime_artifact(path.relative_to(root)))


@contextmanager
def module_attr(module: Any, name: str, value: Any) -> Iterator[None]:
    previous = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, previous)


class PluginBundleTests(unittest.TestCase):
    def test_canonical_manifest_respects_client_starter_prompt_limit(self) -> None:
        manifest_path = REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        # Keep prompts within the manifest loader's three-prompt limit.
        # Check the current template without rejecting historical release bytes.
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)

    def test_manifest_versions_keep_ascii_semver_contract(self) -> None:
        manifest = json.loads((REPOSITORY_ROOT / "plugin-template/.codex-plugin/plugin.json").read_bytes())
        valid_versions = (
            "0.0.0", "1.2.3", "10.20.30", "1.2.3-alpha.1", "1.2.3-0",
            "1.2.3-01a", "1.2.3+build.01", "1.2.3-rc.1+build.0123",
        )
        invalid_versions = ("01.2.3", "1.02.3", "1.2.03", "1.2.3-01", "1.2.3-alpha.01", "1.2.3+", "1.2")
        for version in valid_versions + invalid_versions:
            with self.subTest(version=version):
                manifest["version"] = version
                errors: list[str] = []
                self.validate_plugin_bundle.validate_manifest(manifest, errors)
                if version in valid_versions:
                    self.assertEqual(errors, [])
                else:
                    self.assertTrue(any("strict semantic versioning" in error for error in errors), errors)

    def test_manifest_versions_reject_unicode_digits(self) -> None:
        manifest = json.loads((REPOSITORY_ROOT / "plugin-template/.codex-plugin/plugin.json").read_bytes())
        for digit in ("\u0662", "\u06f2", "\uff12", "\u0968"):
            for version in (
                f"1{digit}.2.3", f"1.2{digit}.3", f"1.2.3{digit}",
                f"1.2.3-{digit}", f"1.2.3-rc.1{digit}", f"1.2.3-{digit}rc", f"1.2.3+build.{digit}",
            ):
                with self.subTest(version=version):
                    manifest["version"] = version
                    errors: list[str] = []
                    self.validate_plugin_bundle.validate_manifest(manifest, errors)
                    self.assertTrue(any("strict semantic versioning" in error for error in errors), errors)

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp_dir.name).resolve()
        self.output = self.temp_root / "frey-skills"
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
        fake_root = self.temp_root / "fake-repository"
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

    def test_owned_fixtures_support_aliased_system_temporary_directory(self) -> None:
        target = self.temp_root / "temporary-target"
        target.mkdir()
        alias = self.temp_root / "temporary-alias"
        self.make_symlink_or_skip(target, alias, target_is_directory=True)
        environment = {
            **os.environ,
            "TMPDIR": str(alias),
            "TMP": str(alias),
            "TEMP": str(alias),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        script = (
            "import os, sys, tempfile, unittest\n"
            "from pathlib import Path\n"
            "if Path(tempfile.gettempdir()) != Path(os.environ['TMPDIR']):\n"
            "    raise SystemExit('child did not use the aliased temporary directory')\n"
            "suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])\n"
            "result = unittest.TextTestRunner().run(suite)\n"
            "raise SystemExit(not result.wasSuccessful())\n"
        )
        tests = (
            "scripts.test_build_plugin.PluginBundleTests.test_build_discovers_new_canonical_skill_without_hardcoded_list",
            "scripts.test_implementation_execution_contract.ImplementationExecutionContractTests.test_dirty_fixture_contains_same_file_user_hunk",
            "scripts.test_implementation_execution_contract.ImplementationExecutionContractTests.test_fixture_setup_rejects_linked_destinations_and_parents",
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", script, *tests],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            encoding="utf-8",
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_nonforced_build_preserves_destinations_populated_during_staging(self) -> None:
        original_write = self.build_plugin.write_bundle
        for initial, created in (("missing", "directory"), ("empty", "directory"), ("missing", "file")):
            with self.subTest(initial=initial, created=created):
                output = self.temp_root / f"race-{initial}-{created}"
                if initial == "empty":
                    output.mkdir()
                sentinel = output / "concurrent.txt" if created == "directory" else output

                def stage_then_write(staging: Path) -> None:
                    original_write(staging)
                    if created == "directory":
                        output.mkdir(exist_ok=True)
                    sentinel.write_bytes(b"preserve concurrent work\n")

                with mock.patch.object(self.build_plugin, "write_bundle", side_effect=stage_then_write):
                    with self.assertRaises(self.build_plugin.BuildError):
                        self.build_plugin.build_bundle(output, force=False)
                self.assertEqual(sentinel.read_bytes(), b"preserve concurrent work\n")
                if created == "directory":
                    self.assertEqual({path.name for path in output.iterdir()}, {"concurrent.txt"})
                self.assertEqual(list(self.temp_root.glob(f".{output.name}.tmp-*")), [])

    def test_forced_build_restores_previous_bundle_when_publication_fails(self) -> None:
        self.build_plugin.build_bundle(self.output)
        before = {path: (self.output / path).read_bytes() for path in relative_files(self.output)}
        original = Path.rename

        def fail_staged_publication(source: Path, destination: Path) -> Path:
            if source.parent.name.startswith(f".{self.output.name}.tmp-"):
                raise PermissionError("injected publication failure")
            return original(source, destination)

        with mock.patch.object(Path, "rename", fail_staged_publication):
            with self.assertRaisesRegex(self.build_plugin.BuildError, "could not publish"):
                self.build_plugin.build_bundle(self.output, force=True)
        self.assertEqual({path: (self.output / path).read_bytes() for path in relative_files(self.output)}, before)

    def test_reserved_recovery_directory_is_reported_as_a_build_error(self) -> None:
        output = self.temp_root / ".frey-publish"
        self.assertEqual(self.build_plugin.main([str(output)]), 1)
        self.assertFalse(output.exists())

    def test_nonforced_build_accepts_empty_output_and_lexical_parent_segments(self) -> None:
        self.output.mkdir()
        sibling = self.temp_root / "sibling"
        sibling.mkdir()
        requested = sibling / ".." / self.output.name
        self.assertEqual(self.build_plugin.main([str(requested)]), 0)
        self.assertEqual(self.validate(), 0)
        self.build_plugin.build_bundle(requested, force=True)
        self.assertEqual(self.validate(), 0)

    def test_validator_accepts_safe_parent_segments_through_api_and_cli(self) -> None:
        self.build_plugin.build_bundle(self.output)
        sibling = self.temp_root / "existing"
        sibling.mkdir()
        requested = sibling / ".." / self.output.name
        self.assertEqual(self.validate_plugin_bundle.validate_bundle(requested), [])
        for argument in (requested, requested.relative_to(self.temp_root)):
            with self.subTest(argument=argument):
                result = subprocess.run(
                    [sys.executable, "-B", str(VALIDATE_SCRIPT), str(argument)],
                    cwd=self.temp_root, capture_output=True, encoding="utf-8", check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_link_before_parent_segment_preserves_both_candidate_destinations(self) -> None:
        for case, target_parts in (("same-parent", ("target",)), ("different-parent", ("external", "target"))):
            case_root = self.temp_root / case
            target = case_root.joinpath(*target_parts)
            target.mkdir(parents=True)
            link = case_root / "link"
            self.make_symlink_or_skip(target, link, target_is_directory=True)
            destinations = {case_root / "bundle", target.parent / "bundle"}
            before = {}
            for destination in destinations:
                destination.mkdir()
                sentinel = destination / "keep.txt"
                before[sentinel] = f"preserve {destination.relative_to(case_root).as_posix()}\n".encode("utf-8")
                sentinel.write_bytes(before[sentinel])
            requested = link / ".." / "bundle"
            for entrypoint in ("cli", "relative-cli", "api"):
                with self.subTest(case=case, entrypoint=entrypoint):
                    if entrypoint == "cli":
                        self.assertEqual(self.build_plugin.main([str(requested), "--force"]), 1)
                    elif entrypoint == "relative-cli":
                        result = subprocess.run(
                            [sys.executable, str(BUILD_SCRIPT), str(Path("link") / ".." / "bundle"), "--force"],
                            cwd=case_root, capture_output=True, encoding="utf-8", check=False,
                        )
                        self.assertEqual(result.returncode, 1, result.stderr)
                        self.assertIn("symlink or junction", result.stderr)
                    else:
                        with self.assertRaisesRegex(self.build_plugin.BuildError, "symlink or junction"):
                            self.build_plugin.build_bundle(requested, force=True)
                    self.assertEqual({path: path.read_bytes() for path in before}, before)
                    for destination in destinations:
                        self.assertEqual({path.name for path in destination.iterdir()}, {"keep.txt"})

    def assert_linked_outputs_are_rejected(self, *, junction: bool = False) -> None:
        target = self.temp_root / "linked-target"
        child = target / "child"
        child.mkdir(parents=True)
        sentinel = child / "keep.txt"
        sentinel.write_bytes(b"preserve linked target\n")
        link = self.temp_root / "output-link"
        if junction:
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.make_symlink_or_skip(target, link, target_is_directory=True)
        for destination in (link, link / "child", link / ".." / "bundle"):
            with self.subTest(destination=destination):
                self.assertEqual(self.build_plugin.main([str(destination), "--force"]), 1)
                with self.assertRaisesRegex(self.build_plugin.BuildError, "symlink or junction"):
                    self.build_plugin.build_bundle(destination, force=True)
                self.assertEqual(sentinel.read_bytes(), b"preserve linked target\n")
                self.assertEqual({path.name for path in target.iterdir()}, {"child"})
                self.assertEqual({path.name for path in child.iterdir()}, {"keep.txt"})

    def test_linked_output_and_parent_are_rejected_by_cli_and_api(self) -> None:
        self.assert_linked_outputs_are_rejected()

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_junction_output_and_parent_are_rejected_by_cli_and_api(self) -> None:
        self.assert_linked_outputs_are_rejected(junction=True)

    def test_runtime_caches_are_excluded_and_cannot_be_added_to_bundle(self) -> None:
        fake_root = self.create_fake_repository()
        skill = fake_root / "code-review"
        for relative in ("scripts/__pycache__/helper.pyc", ".pytest_cache/README.md", "scripts/helper.pyc"):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"local runtime cache")
        output = fake_root / "dist" / "frey-skills"
        with module_attr(self.build_plugin, "REPOSITORY_ROOT", fake_root), module_attr(
            self.build_plugin, "PLUGIN_TEMPLATE", fake_root / "plugin-template"
        ):
            self.assertEqual(self.build_plugin.main([str(output)]), 0)
        generated = output / "skills" / "code-review"
        self.assertFalse((generated / "scripts" / "__pycache__").exists())
        self.assertFalse((generated / ".pytest_cache").exists())
        self.assertFalse((generated / "scripts" / "helper.pyc").exists())
        errors: list[str] = []
        self.validate_plugin_bundle.compare_trees(skill, generated, "code-review", errors)
        self.assertEqual(errors, [])
        (generated / "scripts" / "helper.pyc").write_bytes(b"unexpected cache")
        self.validate_plugin_bundle.compare_trees(skill, generated, "code-review", errors)
        self.assertTrue(any("extra files" in error for error in errors))

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
        symlink_root = self.temp_root / "bundle-link"
        self.make_symlink_or_skip(self.output, symlink_root, target_is_directory=True)

        self.assertEqual(self.validate_plugin_bundle.main([str(symlink_root)]), 1)

    def assert_bundle_links_are_rejected_before_reads(self, *, junction: bool = False) -> None:
        self.assertEqual(self.build(), 0)
        for location in ("root", "root-parent-segment", "ancestor", "skill"):
            with self.subTest(location=location):
                if location in {"root", "root-parent-segment"}:
                    target, link = self.output, self.temp_root / "bundle-link"
                    candidate = link if location == "root" else link / ".." / self.output.name
                elif location == "ancestor":
                    target, link = self.temp_root, self.temp_root / "parent-link"
                    candidate = link / self.output.name
                else:
                    link = self.output / "skills" / "code-review"
                    target = self.temp_root / "external-skill"
                    link.resolve().relative_to(self.temp_root.resolve())
                    target.parent.resolve().relative_to(self.temp_root.resolve())
                    link.rename(target)
                    candidate = self.output
                if junction:
                    result = subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                else:
                    self.make_symlink_or_skip(target, link, target_is_directory=True)
                try:
                    with mock.patch.object(Path, "read_text", side_effect=AssertionError("linked bundle files must not be read")), mock.patch.object(
                        Path, "read_bytes", side_effect=AssertionError("linked bundle files must not be compared")
                    ):
                        errors = self.validate_plugin_bundle.validate_bundle(candidate)
                    self.assertTrue(any("symlink" in error for error in errors), errors)
                finally:
                    if junction:
                        link.rmdir()
                    else:
                        link.unlink()
                    if location == "skill":
                        target.resolve().relative_to(self.temp_root.resolve())
                        link.parent.resolve().relative_to(self.temp_root.resolve())
                        target.rename(link)

    def test_validator_rejects_linked_roots_ancestors_and_skills_before_reads(self) -> None:
        self.assert_bundle_links_are_rejected_before_reads()

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_validator_rejects_junction_roots_ancestors_and_skills_before_reads(self) -> None:
        self.assert_bundle_links_are_rejected_before_reads(junction=True)

    def test_build_rejects_symlink_output_before_resolving_or_replacing_it(self) -> None:
        target = self.temp_root / "real-output"
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

    def test_build_rejects_repository_ancestor_and_preserves_sources_and_siblings(self) -> None:
        fake_root = self.create_fake_repository()
        output = fake_root.parent
        sentinel = output / "sibling.txt"
        sentinel.write_bytes(b"preserve sibling\n")
        original = {path: (fake_root / path).read_bytes() for path in relative_files(fake_root)}

        with module_attr(self.build_plugin, "REPOSITORY_ROOT", fake_root), module_attr(
            self.build_plugin, "PLUGIN_TEMPLATE", fake_root / "plugin-template"
        ):
            for force in (False, True):
                with self.subTest(force=force), self.assertRaisesRegex(self.build_plugin.BuildError, "must not contain"):
                    self.build_plugin.build_bundle(output, force=force)
            self.assertEqual(self.build_plugin.main([str(output), "--force"]), 1)

        self.assertEqual(sentinel.read_bytes(), b"preserve sibling\n")
        self.assertEqual({path: (fake_root / path).read_bytes() for path in relative_files(fake_root)}, original)
        self.assertEqual({path.name for path in output.iterdir()}, {"fake-repository", "sibling.txt"})

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

            outside_source = self.temp_root / "outside-source-output"
            self.assertEqual(self.build_plugin.main([str(outside_source), "--force"]), 0)
        self.assertTrue((outside_source / ".codex-plugin" / "plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
