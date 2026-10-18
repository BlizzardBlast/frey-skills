#!/usr/bin/env python3
"""Regression tests for collect_review_context.py."""

from __future__ import annotations

import errno
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from threading import Barrier
from typing import Any, Iterator
from unittest import mock


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
        self.repo = Path(self.temp_dir.name).resolve()
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
        result = run([sys.executable, str(SCRIPT), *args], self.repo)
        return json.loads(result.stdout)

    def run_collect(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
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

    def test_working_tree_without_commits_uses_empty_tree_and_includes_untracked(self) -> None:
        self.write("fresh file.txt", "one\ntwo\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "working-tree")
        self.assertEqual(data["base"], "EMPTY_TREE")
        self.assertEqual(data["head"], "WORKTREE")
        self.assertEqual(files["fresh file.txt"]["status"], "?")
        self.assertEqual(files["fresh file.txt"]["added_lines"], 2)

    def test_unborn_object_formats_preserve_scope_without_writing_git_objects(self) -> None:
        for object_format in ("sha1", "sha256"):
            for scenario in ("empty", "untracked", "staged", "mixed"):
                with self.subTest(object_format=object_format, scenario=scenario):
                    repo = self.repo / f"{object_format}-{scenario}"
                    repo.mkdir()
                    run(["git", "init", "-q", f"--object-format={object_format}"], repo)
                    sample = repo / "sample.txt"
                    expected_files = {}
                    if scenario != "empty":
                        sample.write_text("one\n", encoding="utf-8")
                        expected_files["sample.txt"] = ("?", 1)
                    if scenario in {"staged", "mixed"}:
                        run(["git", "add", "sample.txt"], repo)
                        expected_files["sample.txt"] = ("A", 1)
                    if scenario == "mixed":
                        sample.write_text("one\ntwo\n", encoding="utf-8")
                        (repo / "untracked.txt").write_text("new\n", encoding="utf-8")
                        expected_files = {"sample.txt": ("A", 2), "untracked.txt": ("?", 1)}

                    objects = repo / ".git" / "objects"
                    objects_before = {
                        path.relative_to(objects): path.read_bytes()
                        for path in objects.rglob("*") if path.is_file()
                    }
                    result = run([sys.executable, str(SCRIPT)], repo)
                    data = json.loads(result.stdout)
                    files = self.files_by_path(data)

                    self.assertEqual(data["mode"], "working-tree")
                    self.assertEqual(data["base"], "EMPTY_TREE")
                    self.assertEqual(data["head"], "WORKTREE")
                    self.assertEqual(set(files), set(expected_files))
                    for name, (status, added_lines) in expected_files.items():
                        self.assertEqual(files[name]["status"], status)
                        self.assertEqual(files[name]["added_lines"], added_lines)
                        self.assertEqual(files[name]["deleted_lines"], 0)
                        self.assertTrue(files[name]["stats_available"])
                    self.assertEqual(data["overall_totals"]["files"], len(expected_files))
                    self.assertEqual(
                        {path.relative_to(objects): path.read_bytes()
                         for path in objects.rglob("*") if path.is_file()},
                        objects_before,
                    )

    def test_working_tree_without_commits_includes_staged_files(self) -> None:
        self.write("staged.txt", "one\n")
        self.git("add", "staged.txt")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "working-tree")
        self.assertEqual(data["base"], "EMPTY_TREE")
        self.assertEqual(files["staged.txt"]["status"], "A")
        self.assertEqual(files["staged.txt"]["added_lines"], 1)

    def test_working_tree_without_commits_includes_staged_and_unstaged_content(self) -> None:
        self.write("mixed.txt", "staged\n")
        self.git("add", "mixed.txt")
        self.write("mixed.txt", "staged\nunstaged\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(files["mixed.txt"]["status"], "A")
        self.assertEqual(files["mixed.txt"]["added_lines"], 2)

    def test_working_tree_without_commits_includes_staged_and_untracked_files(self) -> None:
        self.write("staged.txt", "staged\n")
        self.git("add", "staged.txt")
        self.write("untracked.txt", "untracked\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertEqual(sorted(files), ["staged.txt", "untracked.txt"])
        self.assertEqual(files["staged.txt"]["status"], "A")
        self.assertEqual(files["untracked.txt"]["status"], "?")

    def test_working_tree_without_commits_reports_staged_binary_file(self) -> None:
        self.write("image.bin", b"\x00\x01binary")
        self.git("add", "image.bin")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertTrue(files["image.bin"]["binary"])
        self.assertIsNone(files["image.bin"]["added_lines"])
        self.assertIsNone(files["image.bin"]["deleted_lines"])

    def test_staged_without_commits_labels_empty_tree_to_index(self) -> None:
        self.write("staged.txt", "one\n")
        self.git("add", "staged.txt")

        data = self.collect("--staged")
        files = self.files_by_path(data)

        self.assertEqual(data["mode"], "staged")
        self.assertEqual(data["base"], "EMPTY_TREE")
        self.assertEqual(data["head"], "INDEX")
        self.assertEqual(files["staged.txt"]["status"], "A")
        self.assertEqual(files["staged.txt"]["added_lines"], 1)

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

    def test_invalid_range_refs_fail_without_writing_or_reporting_empty_scope(self) -> None:
        self.write("tracked.txt", "before\n")
        self.commit_all("initial")
        self.write("tracked.txt", "changed\n")
        self.write("unexpected...HEAD", b"preserve existing bytes\n")
        before = {path.relative_to(self.repo): path.read_bytes() for path in self.repo.rglob("*")
                  if path.is_file() and ".git" not in path.relative_to(self.repo).parts}
        for base, head in (
            ("--output=unexpected", "HEAD"), ("HEAD", "--output=unexpected"),
            ("missing-ref", "HEAD"), ("HEAD", "missing-ref"), ("HEAD:tracked.txt", "HEAD"),
        ):
            with self.subTest(base=base, head=head):
                result = self.run_collect(f"--base={base}", f"--head={head}")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("Error:", result.stderr)
                after = {path.relative_to(self.repo): path.read_bytes() for path in self.repo.rglob("*")
                         if path.is_file() and ".git" not in path.relative_to(self.repo).parts}
                self.assertEqual(after, before)

    def test_nested_invocation_matches_root_for_every_mode_and_relative_diff_config(self) -> None:
        self.write("tracked.txt", "base\n")
        self.write("nested/tracked.txt", "base\n")
        self.commit_all("initial")
        self.write("committed.txt", "new commit\n")
        self.commit_all("second")
        self.write("tracked.txt", "staged change\n")
        self.git("add", "tracked.txt")
        self.write("nested/tracked.txt", "unstaged change\n")
        self.write("outside.txt", "root untracked\n")
        self.write("nested/inside.txt", "nested untracked\n")
        self.git("config", "diff.relative", "true")
        for args in ((), ("--staged",), ("--base", "HEAD~1", "--head", "HEAD")):
            with self.subTest(args=args):
                expected = self.collect(*args)
                result = run([sys.executable, str(SCRIPT), *args], self.repo / "nested")
                self.assertEqual(json.loads(result.stdout), expected)
        files = self.files_by_path(self.collect())
        self.assertEqual(set(files), {"tracked.txt", "nested/tracked.txt", "outside.txt", "nested/inside.txt"})
        self.assertTrue(all(item["stats_available"] for item in files.values()))

    def test_nested_unborn_repository_includes_root_and_nested_untracked_files(self) -> None:
        self.write("staged.txt", "staged\n")
        self.git("add", "staged.txt")
        self.write("outside.txt", "root untracked\n")
        self.write("nested/inside.txt", "nested untracked\n")
        expected = self.collect()
        result = run([sys.executable, str(SCRIPT)], self.repo / "nested")
        self.assertEqual(json.loads(result.stdout), expected)
        files = self.files_by_path(expected)
        self.assertEqual(set(files), {"staged.txt", "outside.txt", "nested/inside.txt"})
        self.assertTrue(all(item["stats_available"] for item in files.values()))

    @unittest.skipIf(os.name == "nt", "Trailing whitespace in directory names requires a POSIX filesystem")
    def test_whitespace_roots_preserve_scope_for_every_mode(self) -> None:
        def git(root: Path, *args: str) -> None:
            run(["git", "-c", "user.email=review@example.com", "-c", "user.name=Review Tests", *args], root)

        for index, suffix in enumerate((" ", "\t", "\r", "\n", "\r\n", "\u00a0")):
            with self.subTest(suffix=repr(suffix)):
                parent = self.repo / f"root-{index}"
                requested = parent / ("repo" + suffix)
                sibling = parent / "repo"
                for root, label in ((requested, "requested"), (sibling, "unrelated")):
                    root.mkdir(parents=True)
                    git(root, "init", "-q")
                    (root / "baseline.txt").write_bytes(b"baseline\n")
                    git(root, "add", ".")
                    git(root, "commit", "-qm", "initial")
                    (root / f"{label}-committed.txt").write_bytes(b"committed\n" * 3)
                    git(root, "add", ".")
                    git(root, "commit", "-qm", "second")
                    (root / f"{label}-staged.txt").write_bytes(b"staged\n" * 2)
                    git(root, "add", ".")
                    (root / f"{label}-untracked.txt").write_bytes(b"untracked\n")
                nested = requested / "nested"
                nested.mkdir()
                cases = (
                    ((), "working-tree", {"requested-staged.txt", "requested-untracked.txt"}, 3),
                    (("--staged",), "staged", {"requested-staged.txt"}, 2),
                    (("--base", "HEAD^", "--head", "HEAD"), "range", {"requested-committed.txt"}, 3),
                )
                for args, mode, paths, added_lines in cases:
                    with self.subTest(mode=mode):
                        result = run([sys.executable, str(SCRIPT), *args], nested)
                        data = json.loads(result.stdout)
                        files = self.files_by_path(data)
                        self.assertEqual(data["git_root"], requested.name)
                        self.assertEqual(data["mode"], mode)
                        self.assertEqual(set(files), paths)
                        self.assertTrue(all(item["stats_available"] for item in files.values()))
                        self.assertEqual(data["overall_totals"]["files"], len(paths))
                        self.assertEqual(data["overall_totals"]["added_lines"], added_lines)
                        self.assertEqual(data["overall_totals"]["unknown_stats_files"], 0)

    @unittest.skipIf(os.name == "nt", "Trailing whitespace in directory names requires a POSIX filesystem")
    def test_whitespace_root_without_sibling_matches_root_and_nested_invocation(self) -> None:
        root = self.repo / "repo \t\r\n"
        nested = root / "nested"
        nested.mkdir(parents=True)
        run(["git", "init", "-q"], root)
        (root / "requested.txt").write_bytes(b"requested\n")
        expected = json.loads(run([sys.executable, str(SCRIPT)], root).stdout)
        actual = json.loads(run([sys.executable, str(SCRIPT)], nested).stdout)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["git_root"], root.name)
        self.assertEqual(set(self.files_by_path(actual)), {"requested.txt"})
        self.assertEqual(actual["overall_totals"]["added_lines"], 1)

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

    def test_type_change_parser_keeps_status_and_stats(self) -> None:
        changes = COLLECT_REVIEW_CONTEXT.parse_name_status("T\0script.sh\0")
        stats = COLLECT_REVIEW_CONTEXT.parse_numstat("0\t0\tscript.sh\0")

        self.assertEqual(changes[0]["status"], "T")
        self.assertEqual(changes[0]["path"], "script.sh")
        self.assertEqual(stats["script.sh"]["added_lines"], 0)
        self.assertEqual(stats["script.sh"]["deleted_lines"], 0)

    def test_malformed_name_status_raises_context_parse_error(self) -> None:
        for payload in ("M\0", "M\0file.txt"):
            with self.subTest(payload=payload):
                with self.assertRaises(COLLECT_REVIEW_CONTEXT.ContextParseError):
                    COLLECT_REVIEW_CONTEXT.parse_name_status(payload)

    def test_malformed_numstat_raises_context_parse_error(self) -> None:
        bad_payloads = (
            "1\t0\t\0old.txt\0",
            "x\t0\tbad-count.txt\0",
            "1\ty\tbad-count.txt\0",
            "1\t0\t",
            "1\t0\tfile.txt",
        )

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(COLLECT_REVIEW_CONTEXT.ContextParseError):
                    COLLECT_REVIEW_CONTEXT.parse_numstat(payload)

    def test_main_returns_2_for_context_parse_error(self) -> None:
        original_run_git = COLLECT_REVIEW_CONTEXT.run_git
        original_argv = sys.argv

        def fake_run_git(args: list[str], *, cwd: Path | None = None) -> str:
            if args == ["rev-parse", "--show-toplevel"]:
                return str(self.repo) + "\n"
            if "--name-status" in args:
                return "M\0"
            if "--numstat" in args:
                return ""
            return original_run_git(args, cwd=cwd)

        try:
            COLLECT_REVIEW_CONTEXT.run_git = fake_run_git
            sys.argv = ["collect_review_context.py", "--staged"]
            with redirect_stderr(io.StringIO()):
                code = COLLECT_REVIEW_CONTEXT.main()
        finally:
            COLLECT_REVIEW_CONTEXT.run_git = original_run_git
            sys.argv = original_argv

        self.assertEqual(code, 2)

    def assert_path_is_preserved(self, unusual_path: str) -> None:
        self.write(unusual_path, "one\n")
        self.commit_all("initial")
        self.write(unusual_path, "one\ntwo\n")

        data = self.collect()
        files = self.files_by_path(data)

        self.assertIn(unusual_path, files)
        self.assertEqual(files[unusual_path]["added_lines"], 1)

    def test_unusual_paths_are_preserved(self) -> None:
        self.assert_path_is_preserved("dir/space unicode-β.txt")

    @unittest.skipIf(os.name == "nt", "Windows filenames cannot contain tabs")
    def test_tab_in_filename_is_preserved(self) -> None:
        self.assert_path_is_preserved("dir/space tab\tunicode-β.txt")

    def test_control_characters_in_path_are_preserved_by_parsers(self) -> None:
        path = "dir/tab\tline\nunicode-β.txt"
        changes = COLLECT_REVIEW_CONTEXT.parse_name_status(f"M\0{path}\0")
        stats = COLLECT_REVIEW_CONTEXT.parse_numstat(f"1\t0\t{path}\0")
        self.assertEqual(changes[0]["path"], path)
        self.assertEqual(stats[path]["added_lines"], 1)

    @unittest.skipIf(os.name == "nt", "Windows filenames cannot contain carriage returns or newlines")
    def test_git_control_character_paths_are_preserved_end_to_end(self) -> None:
        self.write("baseline.txt", "baseline\n")
        self.commit_all("initial")
        paths = ("carriage\rreturn.txt", "paired\r\nreturn.txt", "line\nreturn.txt")
        expected = {path: index for index, path in enumerate(paths, 1)}
        for path, count in expected.items():
            self.write(path, "line\n" * count)

        def assert_scope(*args: str) -> None:
            data = self.collect(*args)
            files = self.files_by_path(data)
            self.assertEqual(set(files), set(expected))
            self.assertEqual(data["overall_totals"]["added_lines"], sum(expected.values()))
            self.assertEqual(data["overall_totals"]["unknown_stats_files"], 0)
            for path, count in expected.items():
                self.assertTrue(files[path]["stats_available"])
                self.assertEqual(files[path]["added_lines"], count)

        assert_scope()
        self.git("add", ".")
        assert_scope("--staged")
        assert_scope()
        self.git("commit", "-qm", "add control-character paths")
        assert_scope("--base", "HEAD^", "--head", "HEAD")

    @unittest.skipIf(os.name == "nt", "Windows filenames cannot contain carriage returns or newlines")
    def test_git_rename_preserves_control_characters_in_both_paths(self) -> None:
        old_path = "old\rname.txt"
        new_path = "new\r\nname.txt"
        self.write(old_path, "same contents\n")
        self.commit_all("initial")
        self.git("mv", old_path, new_path)

        def assert_rename(*args: str) -> None:
            data = self.collect(*args)
            self.assertEqual(len(data["files"]), 1)
            change = data["files"][0]
            self.assertEqual(change["path"], new_path)
            self.assertEqual(change["previous_path"], old_path)
            self.assertEqual(change["status"], "R")
            self.assertTrue(change["stats_available"])
            self.assertEqual((change["added_lines"], change["deleted_lines"]), (0, 0))

        assert_rename("--staged")
        assert_rename()
        self.git("commit", "-qm", "rename control-character path")
        assert_rename("--base", "HEAD^", "--head", "HEAD")

    @unittest.skipIf(os.name == "nt", "Non-UTF-8 filename bytes require a POSIX filesystem")
    def test_non_utf8_git_paths_fail_without_replacement_aliases(self) -> None:
        self.write("baseline.txt", "baseline\n")
        self.commit_all("initial")
        raw_path = os.fsdecode(b"bad-\xff.txt")
        replacement_path = "bad-\ufffd.txt"
        try:
            self.write(raw_path, "one\n")
        except OSError as exc:
            if exc.errno == errno.EILSEQ:
                self.skipTest("The filesystem rejects non-UTF-8 filename bytes")
            raise
        self.write(replacement_path, "other\nfile\nthree\n")
        output = self.repo / "review-context.json"
        output.write_bytes(b"preserve existing output\n")

        def assert_rejected(*args: str) -> None:
            result = self.run_collect(*args, "--output", str(output), "--force")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Git output is not valid UTF-8", result.stderr)
            self.assertIn("filename identity", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(output.read_bytes(), b"preserve existing output\n")

        assert_rejected()
        self.git("add", ".")
        assert_rejected("--staged")
        assert_rejected()
        self.git("commit", "-qm", "add distinct byte paths")
        assert_rejected("--base", "HEAD^", "--head", "HEAD")
        self.assertEqual((self.repo / raw_path).read_bytes(), b"one\n")
        self.assertEqual((self.repo / replacement_path).read_bytes(), b"other\nfile\nthree\n")

    def test_non_utf8_git_output_never_publishes_context(self) -> None:
        output = self.repo / "review-context.json"
        output.write_bytes(b"preserve existing output\n")

        def git_output(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
            if "--show-toplevel" in args:
                stdout = str(self.repo).encode("utf-8") + b"\n"
            elif "--verify" in args:
                stdout = b"1" * 40 + b"\n"
            elif "--name-status" in args:
                stdout = b"M\0bad-\xff.txt\0"
            else:
                raise AssertionError(f"Unexpected Git command: {args!r}")
            return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr=b"")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(COLLECT_REVIEW_CONTEXT.subprocess, "run", side_effect=git_output), \
                mock.patch.object(sys, "argv", [str(SCRIPT), "--output", str(output), "--force"]), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = COLLECT_REVIEW_CONTEXT.main()

        self.assertEqual(code, 2)
        self.assertIn("Git output is not valid UTF-8", stderr.getvalue())
        self.assertIn("filename identity", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(output.read_bytes(), b"preserve existing output\n")

    def test_redirected_output_uses_utf8_with_an_ascii_default(self) -> None:
        self.write("unicode-β.txt", "one\n")
        output = self.repo / "context-β.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(output)],
            cwd=self.repo,
            env={**os.environ, "PYTHONIOENCODING": "ascii"},
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("β", result.stdout)
        self.assertIn("β", result.stderr)
        self.assertIn("unicode-β.txt", self.files_by_path(json.loads(result.stdout)))
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), json.loads(result.stdout))

    def make_symlink_or_skip(self, target: Path, link: Path, *, target_is_directory: bool = False) -> None:
        try:
            os.symlink(target, link, target_is_directory=target_is_directory)
        except NotImplementedError as exc:
            self.skipTest(f"symlinks are unavailable: {exc}")
        except OSError as exc:
            if getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows symlink creation requires Developer Mode or the symlink privilege")
            raise

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
        with tempfile.TemporaryDirectory() as outside_directory:
            target = Path(outside_directory).resolve() / "outside.txt"
            target.write_text("outside\ncontent\n", encoding="utf-8")
            self.make_symlink_or_skip(target, self.repo / "link.txt")

            data = self.collect()
            files = self.files_by_path(data)

            self.assertEqual(files["link.txt"]["status"], "?")
            self.assertEqual(files["link.txt"]["added_lines"], 1)
            self.assertFalse(files["link.txt"]["binary"])

    def test_linked_parent_never_opens_untracked_contents(self) -> None:
        with tempfile.TemporaryDirectory() as outside_directory:
            for label, target in (("inside", self.repo / "real"), ("outside", Path(outside_directory).resolve())):
                with self.subTest(target=label):
                    target.mkdir(exist_ok=True)
                    (target / "private.txt").write_text("synthetic\nprivate\ncontents\n", encoding="utf-8")
                    link = self.repo / f"{label}-link"
                    self.make_symlink_or_skip(target, link, target_is_directory=True)
                    try:
                        candidate = f"{label}-link/private.txt"
                        with mock.patch.object(COLLECT_REVIEW_CONTEXT, "run_git", return_value=candidate + "\0"), mock.patch.object(
                            Path, "open", side_effect=AssertionError("linked contents must not be opened")
                        ) as opened:
                            changes = COLLECT_REVIEW_CONTEXT.collect_untracked_changes(self.repo)
                        opened.assert_not_called()
                        self.assertEqual(changes[0]["path"], candidate)
                        self.assertFalse(changes[0]["stats_available"])
                        self.assertIsNone(changes[0]["added_lines"])
                        self.assertIsNone(changes[0]["deleted_lines"])
                    finally:
                        if os.name == "nt":
                            link.rmdir()
                        else:
                            link.unlink()

    @unittest.skipUnless(os.name == "nt", "Windows directory junction regression")
    def test_untracked_junction_retains_unknown_stats_without_reading_target(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        with tempfile.TemporaryDirectory() as outside_directory:
            target = Path(outside_directory).resolve()
            private = target / "private-β.txt"
            private.write_bytes(b"synthetic\nexternal\ncontents\n")
            link = self.repo / "linked directory"
            run(["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)], self.repo)
            try:
                candidate = "linked directory/private-β.txt"
                data = self.collect()
                files = self.files_by_path(data)
                self.assertIn(candidate, files)
                self.assertEqual(files[candidate]["status"], "?")
                self.assertFalse(files[candidate]["stats_available"])
                self.assertIsNone(files[candidate]["added_lines"])
                self.assertIsNone(files[candidate]["deleted_lines"])
                self.assertEqual(data["overall_totals"]["unknown_stats_files"], 1)
                self.assertEqual(data["included_totals"]["unknown_stats_files"], 1)
                with mock.patch.object(Path, "open", side_effect=AssertionError("junction target must not be opened")) as opened:
                    changes = COLLECT_REVIEW_CONTEXT.collect_untracked_changes(self.repo)
                opened.assert_not_called()
                self.assertFalse(changes[0]["stats_available"])
            finally:
                link.rmdir()
            self.assertEqual(private.read_bytes(), b"synthetic\nexternal\ncontents\n")

    def test_untracked_paths_outside_root_never_open_contents(self) -> None:
        with tempfile.TemporaryDirectory() as outside_directory:
            outside = Path(outside_directory).resolve() / "outside.txt"
            outside.write_text("synthetic private contents\n", encoding="utf-8")
            for candidate in (str(outside), "../outside.txt"):
                with self.subTest(path=candidate), mock.patch.object(
                    COLLECT_REVIEW_CONTEXT, "run_git", return_value=candidate + "\0"
                ), mock.patch.object(Path, "open", side_effect=AssertionError("outside contents must not be opened")) as opened:
                    changes = COLLECT_REVIEW_CONTEXT.collect_untracked_changes(self.repo)
                opened.assert_not_called()
                self.assertFalse(changes[0]["stats_available"])

    def test_unavailable_stats_are_reported_without_changing_copy_detection(self) -> None:
        original_run_git = COLLECT_REVIEW_CONTEXT.run_git

        def fake_run_git(args: list[str], *, cwd: Path | None = None) -> str:
            if args == ["rev-parse", "--show-toplevel"]:
                return str(self.repo) + "\n"
            if "--name-status" in args:
                return "M\0known.txt\0M\0unknown.txt\0"
            if "--numstat" in args:
                return "1\t0\tknown.txt\0"
            return original_run_git(args, cwd=cwd)

        try:
            COLLECT_REVIEW_CONTEXT.run_git = fake_run_git
            data = COLLECT_REVIEW_CONTEXT.collect_context(
                base=None,
                head=None,
                staged=True,
                max_files=500,
                include_generated_at=False,
            )
        finally:
            COLLECT_REVIEW_CONTEXT.run_git = original_run_git

        files = self.files_by_path(data)
        self.assertTrue(files["known.txt"]["stats_available"])
        self.assertFalse(files["unknown.txt"]["stats_available"])
        self.assertEqual(data["included_totals"]["unknown_stats_files"], 1)
        self.assertEqual(data["overall_totals"]["unknown_stats_files"], 1)

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

    def test_max_files_uses_risk_priority_then_changed_lines_then_path(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        self.write(".github/workflows/build.yml", "ci\n")
        self.write("auth/login.py", "auth\n")
        self.write("docs/readme.md", "doc\n")
        self.write("infra/main.tf", "infra\n")
        self.write("migrations/001_init.sql", "m1\nm2\n")
        self.write("package-lock.json", "lock\n")
        self.write("security/policy.md", "sec\n")

        data = self.collect("--max-files", "4")

        self.assertTrue(data["truncated"])
        self.assertEqual(data["overall_totals"]["files"], 7)
        self.assertEqual(
            [item["path"] for item in data["files"]],
            [
                "migrations/001_init.sql",
                "auth/login.py",
                "security/policy.md",
                "infra/main.tf",
            ],
        )
        self.assertEqual(data["included_totals"]["files"], 4)
        self.assertEqual(data["included_totals"]["added_lines"], 5)
        self.assertEqual(data["overall_totals"]["added_lines"], 8)

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

    def test_concurrent_output_creation_is_preserved_and_reports_cli_write_failure(self) -> None:
        output_path = self.repo / "review-context.json"
        original_temporary_file = tempfile.NamedTemporaryFile

        def create_concurrent_output(*args: Any, **kwargs: Any) -> Any:
            output_path.write_bytes(b"preserve concurrent work\n")
            return original_temporary_file(*args, **kwargs)

        data = {"mode": "working-tree"}
        with mock.patch.object(
            COLLECT_REVIEW_CONTEXT.tempfile, "NamedTemporaryFile", side_effect=create_concurrent_output
        ), mock.patch.object(COLLECT_REVIEW_CONTEXT, "collect_context", return_value=data), mock.patch.object(
            sys, "argv", [str(SCRIPT), "--output", str(output_path)]
        ), redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            result = COLLECT_REVIEW_CONTEXT.main()
        self.assertEqual(result, 3)
        self.assertEqual(json.loads(stdout.getvalue()), data)
        self.assertIn("Use --force", stderr.getvalue())
        self.assertEqual(output_path.read_bytes(), b"preserve concurrent work\n")
        self.assertEqual(list(self.repo.glob(".review-context.json.*.tmp")), [])

    def test_simultaneous_nonforced_writers_publish_exactly_one_complete_output(self) -> None:
        output_path = self.repo / "review-context.json"
        staged = Barrier(2, timeout=10)
        original_temporary_file = tempfile.NamedTemporaryFile

        @contextmanager
        def synchronized_staging(*args: Any, **kwargs: Any) -> Iterator[Any]:
            with original_temporary_file(*args, **kwargs) as handle:
                yield handle
            staged.wait()

        with mock.patch.object(
            COLLECT_REVIEW_CONTEXT.tempfile, "NamedTemporaryFile", side_effect=synchronized_staging
        ), ThreadPoolExecutor(max_workers=2) as executor:
            attempts = {
                text: executor.submit(COLLECT_REVIEW_CONTEXT.write_output_file, text, output_path, force=False)
                for text in ("first writer", "second writer")
            }
            errors = {text: future.exception(timeout=20) for text, future in attempts.items()}
        winners = [text for text, error in errors.items() if error is None]
        failures = [error for error in errors.values() if error is not None]
        self.assertEqual(len(winners), 1, errors)
        self.assertEqual(len(failures), 1, errors)
        self.assertIsInstance(failures[0], COLLECT_REVIEW_CONTEXT.OutputWriteError)
        self.assertEqual(output_path.read_text(encoding="utf-8"), winners[0] + "\n")
        self.assertEqual(list(self.repo.glob(".review-context.json.*.tmp")), [])

    def test_nonforced_output_fails_safely_when_atomic_publication_is_unavailable(self) -> None:
        output_path = self.repo / "review-context.json"
        with mock.patch.object(COLLECT_REVIEW_CONTEXT.os, "link", side_effect=OSError("hard links unavailable")):
            with self.assertRaisesRegex(COLLECT_REVIEW_CONTEXT.OutputWriteError, "hard links unavailable"):
                COLLECT_REVIEW_CONTEXT.write_output_file("summary", output_path, force=False)
        self.assertFalse(output_path.exists())
        self.assertEqual(list(self.repo.glob(".review-context.json.*.tmp")), [])

    def test_output_refuses_directory_target_even_with_force(self) -> None:
        self.write("tracked.txt", "one\n")
        self.commit_all("initial")
        output_path = self.repo / "review-context"
        output_path.mkdir()

        for args in (
            ("--output", str(output_path)),
            ("--output", str(output_path), "--force"),
        ):
            with self.subTest(args=args):
                result = self.run_collect(*args)

                self.assertEqual(result.returncode, 3)
                self.assertIn("output path is a directory", result.stderr)
                self.assertNotIn("Use --force to overwrite", result.stderr)
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
        with tempfile.TemporaryDirectory() as outside_directory:
            target = Path(outside_directory).resolve() / "outside.json"
            target.write_text("outside\n", encoding="utf-8")
            output_path = self.repo / "review-context.json"
            self.make_symlink_or_skip(target, output_path)

            result = self.run_collect("--output", str(output_path), "--force")

            self.assertEqual(result.returncode, 3)
            self.assertEqual(target.read_text(encoding="utf-8"), "outside\n")
            self.assertIn("symbolic link", result.stderr)
            self.assertEqual(json.loads(result.stdout)["mode"], "working-tree")


if __name__ == "__main__":
    unittest.main()
