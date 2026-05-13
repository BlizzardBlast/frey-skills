#!/usr/bin/env python3
"""Regression tests for collect_review_context.py."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("collect_review_context.py")
SPEC = importlib.util.spec_from_file_location("collect_review_context", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load collect_review_context module from {SCRIPT}")

COLLECT_REVIEW_CONTEXT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COLLECT_REVIEW_CONTEXT)


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


class CollectReviewContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        run(["git", "init", "-q"], self.repo)
        run(["git", "config", "user.email", "review@example.com"], self.repo)
        run(["git", "config", "user.name", "Review Tests"], self.repo)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def git(self, *args: str) -> None:
        run(["git", *args], self.repo)

    def write(self, path: str, content: bytes | str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")

    def commit_all(self, message: str) -> None:
        self.git("add", ".")
        self.git("commit", "-q", "-m", message)

    def collect(self, *args: str) -> dict[str, object]:
        result = run(["python3", str(SCRIPT), *args], self.repo)
        return json.loads(result.stdout)

    def run_collect(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def files_by_path(self, data: dict[str, object]) -> dict[str, dict[str, object]]:
        files = data["files"]
        self.assertIsInstance(files, list)
        return {str(item["path"]): item for item in files}

    def test_working_tree_includes_untracked_files(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        self.write("tracked.txt", "one\ntwo\n")
        self.write("untracked.txt", "new\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "working-tree")
        self.assertEqual(data["overall_totals"]["files"], 2)
        self.assertEqual(files["tracked.txt"]["status"], "M")
        self.assertEqual(files["untracked.txt"]["status"], "?")
        self.assertEqual(files["untracked.txt"]["added_lines"], 1)
        self.assertEqual(files["untracked.txt"]["deleted_lines"], 0)

    def test_staged_mode_excludes_untracked_files(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        self.write("tracked.txt", "one\ntwo\n")
        self.git("add", "tracked.txt")
        self.write("untracked.txt", "new\n")

        data = self.collect("--staged")
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "staged")
        self.assertEqual(sorted(files), ["tracked.txt"])

    def test_range_mode_uses_requested_refs(self) -> None:
        self.write("base.txt", "base\n")
        self.commit_all("initial")
        self.write("added.txt", "added\n")
        self.commit_all("add file")

        data = self.collect("--base", "HEAD~1", "--head", "HEAD")
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "range")
        self.assertEqual(files["added.txt"]["status"], "A")
        self.assertEqual(files["added.txt"]["added_lines"], 1)

    def test_rename_stats_are_preserved(self) -> None:
        self.write("old.txt", "a\nb\nc\n")
        self.commit_all("initial")
        self.git("mv", "old.txt", "new.txt")
        self.write("new.txt", "a\nb\nc\nd\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(files["new.txt"]["status"], "R")
        self.assertEqual(files["new.txt"]["previous_path"], "old.txt")
        self.assertEqual(files["new.txt"]["added_lines"], 1)
        self.assertEqual(files["new.txt"]["deleted_lines"], 0)

    def test_copy_parser_records_previous_path_and_stats(self) -> None:
        changes = COLLECT_REVIEW_CONTEXT.parse_name_status("C100\0old.txt\0copy.txt\0")
        stats = COLLECT_REVIEW_CONTEXT.parse_numstat("3\t0\t\0old.txt\0copy.txt\0")

        self.assertEqual(changes[0]["status"], "C")
        self.assertEqual(changes[0]["previous_path"], "old.txt")
        self.assertEqual(changes[0]["path"], "copy.txt")
        self.assertEqual(stats["copy.txt"]["added_lines"], 3)
        self.assertEqual(stats["old.txt"]["deleted_lines"], 0)

    def test_binary_untracked_file_has_binary_stats(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        self.write("image.bin", b"\x00\x01binary")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertTrue(files["image.bin"]["binary"])
        self.assertIsNone(files["image.bin"]["added_lines"])
        self.assertIsNone(files["image.bin"]["deleted_lines"])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support is unavailable")
    def test_untracked_symlink_is_not_followed_for_stats(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        target = self.repo.parent / "outside.txt"
        target.write_text("outside\ncontent\n", encoding="utf-8")
        os.symlink(target, self.repo / "link.txt")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(files["link.txt"]["status"], "?")
        self.assertEqual(files["link.txt"]["added_lines"], 1)
        self.assertFalse(files["link.txt"]["binary"])

    def test_max_files_truncates_but_keeps_overall_totals(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        self.write("a.txt", "a\n")
        self.write("b.txt", "b\n")
        self.write("c.txt", "c\n")

        data = self.collect("--max-files", "2")

        self.assertTrue(data["truncated"])
        self.assertEqual(data["omitted_files"], 1)
        self.assertEqual(data["included_totals"]["files"], 2)
        self.assertEqual(data["overall_totals"]["files"], 3)
        self.assertEqual(data["overall_totals"]["added_lines"], 3)

    def test_default_output_omits_generated_at(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")

        data = self.collect()

        self.assertNotIn("generated_at", data)

    def test_generated_at_is_opt_in(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")

        data = self.collect("--include-generated-at")

        self.assertIn("generated_at", data)

    def test_output_refuses_to_overwrite_without_force(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        output_path = self.repo / "review-context.json"
        output_path.write_text("keep me\n", encoding="utf-8")

        result = self.run_collect("--output", str(output_path))

        self.assertEqual(result.returncode, 3)
        self.assertEqual(output_path.read_text(encoding="utf-8"), "keep me\n")
        self.assertIn("Use --force to overwrite", result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "working-tree")

    def test_output_force_overwrites_existing_file(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        output_path = self.repo / "review-context.json"
        output_path.write_text("replace me\n", encoding="utf-8")

        result = self.run_collect("--output", str(output_path), "--force")

        self.assertEqual(result.returncode, 0)
        written = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(written["mode"], "working-tree")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support is unavailable")
    def test_output_force_refuses_symlink_target(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        target = self.repo.parent / "outside.json"
        target.write_text("outside\n", encoding="utf-8")
        output_path = self.repo / "review-context.json"
        os.symlink(target, output_path)

        result = self.run_collect("--output", str(output_path), "--force")

        self.assertEqual(result.returncode, 3)
        self.assertEqual(target.read_text(encoding="utf-8"), "outside\n")
        self.assertIn("symbolic link", result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "working-tree")


if __name__ == "__main__":
    unittest.main()
