#!/usr/bin/env python3
"""Offline regression proof for downloaded plugin integrity and safe extraction."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import stat
import subprocess
import tempfile
import unittest
import urllib.error
import warnings
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import check, smoke_release


class ReleaseArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="release test café ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "source"
        template = self.source / "plugin-template" / ".codex-plugin"
        template.mkdir(parents=True)
        repository = Path(__file__).resolve().parents[1]
        manifest = json.loads((repository / "plugin-template" / ".codex-plugin" / "plugin.json").read_bytes())
        manifest["version"] = smoke_release.SOURCE_TAG.removeprefix("v")
        self.files = {
            "LICENSE": b"Fixture MIT license\n",
            "frey-skills/.codex-plugin/plugin.json": json.dumps(manifest).encode("utf-8"),
            "frey-skills/skills/first/SKILL.md": b"---\nname: first\ndescription: Use when testing archives.\n---\n",
            "frey-skills/skills/first/scripts/helper.py": b"raise SystemExit('must not execute downloaded helpers')\n",
            "frey-skills/skills/second/SKILL.md": b"---\nname: second\ndescription: Use when testing resources.\n---\n",
            "frey-skills/skills/second/references/café.md": "Supporting bytes: café\n".encode("utf-8"),
        }
        for name, content in self.files.items():
            relative = name.removeprefix("frey-skills/skills/") if name.startswith("frey-skills/skills/") else (
                "plugin-template/.codex-plugin/plugin.json" if name.endswith("plugin.json") else name
            )
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        self.archive = self.root / smoke_release.ARCHIVE_NAME
        self.checksums = self.root / "SHA256SUMS"
        self.destination = self.root / "extracted"
        self.write_archive()

    def update_checksum(self) -> None:
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksums.write_bytes(f"{digest}  {smoke_release.ARCHIVE_NAME}\n".encode("utf-8"))

    def write_archive(self, files: dict[str, bytes] | None = None, extra: tuple[str | zipfile.ZipInfo, bytes] | None = None) -> None:
        with zipfile.ZipFile(self.archive, "w", compression=zipfile.ZIP_DEFLATED) as packaged:
            for name, content in (self.files if files is None else files).items():
                packaged.writestr(name, content)
            if extra is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    packaged.writestr(*extra)
        self.update_checksum()

    def verify(self) -> str:
        return smoke_release.verify_archive(self.archive, self.checksums, self.source, self.destination)

    def test_release_extracts_exact_files_and_resources_without_executing_helpers(self) -> None:
        sentinel = self.root / "preserve.txt"
        sentinel.write_bytes(b"preserve")
        digest = self.verify()
        actual = {path.relative_to(self.destination).as_posix(): path.read_bytes() for path in self.destination.rglob("*") if path.is_file()}
        self.assertEqual(actual, self.files)
        self.assertEqual(digest, hashlib.sha256(self.archive.read_bytes()).hexdigest())
        self.assertEqual(sentinel.read_bytes(), b"preserve")

    def test_checksum_mismatch_wrong_filename_and_ambiguous_records_fail_before_extraction(self) -> None:
        valid = self.checksums.read_bytes()
        for checksum in (b"0" * 64 + b"  " + self.archive.name.encode() + b"\n", valid.replace(b".zip", b".other"), valid + valid, b"", b"\xff"):
            with self.subTest(checksum=checksum):
                self.checksums.write_bytes(checksum)
                with self.assertRaises(ValueError):
                    self.verify()
                self.assertFalse(self.destination.exists())

    def test_recomputed_checksum_cannot_hide_changed_resource_or_license_bytes(self) -> None:
        for name in ("LICENSE", "frey-skills/skills/second/references/café.md"):
            with self.subTest(name=name):
                files = {**self.files, name: b"X" * len(self.files[name])}
                self.write_archive(files)
                with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "bytes differ"):
                    self.verify()
                self.assertFalse(self.destination.exists())

    def test_missing_manifest_skill_license_and_extra_unsafe_entries_cannot_extract(self) -> None:
        for missing in ("LICENSE", "frey-skills/.codex-plugin/plugin.json", "frey-skills/skills/second/SKILL.md"):
            with self.subTest(missing=missing):
                self.write_archive({name: content for name, content in self.files.items() if name != missing})
                with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "file set differs"):
                    self.verify()
                self.assertFalse(self.destination.exists())
        for name in ("../escape", "/escape", "C:/escape", "frey-skills\\skills\\escape", "LICENSE:stream", "frey-skills/skills/first/__pycache__/extra.pyc", "frey-skills/skills/FIRST/SKILL.md", "frey-skills/"):
            with self.subTest(extra=name):
                self.write_archive(extra=(name, b"unexpected"))
                with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "file set differs"):
                    self.verify()
                self.assertFalse(self.destination.exists())
        self.assertFalse((self.root / "escape").exists())

    def test_duplicate_entries_and_nonregular_file_metadata_are_rejected(self) -> None:
        self.write_archive(extra=("LICENSE", self.files["LICENSE"]))
        with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "duplicate"):
            self.verify()
        for kind in (stat.S_IFLNK, stat.S_IFIFO, stat.S_IFDIR):
            with self.subTest(kind=kind):
                info = zipfile.ZipInfo("LICENSE")
                info.create_system = 3
                info.external_attr = (kind | 0o644) << 16
                self.write_archive({name: content for name, content in self.files.items() if name != "LICENSE"}, extra=(info, self.files["LICENSE"]))
                with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "regular files"):
                    self.verify()
                self.assertFalse(self.destination.exists())

    def test_wrong_size_and_invalid_zip_fail_before_extraction(self) -> None:
        self.write_archive({**self.files, "LICENSE": b"wrong size"})
        with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "file size differs"):
            self.verify()
        self.archive.write_bytes(b"invalid ZIP")
        self.update_checksum()
        with self.assertRaises(zipfile.BadZipFile):
            self.verify()
        self.assertFalse(self.destination.exists())

    def test_source_version_mismatch_and_invalid_manifest_are_not_accepted(self) -> None:
        path = self.source / "plugin-template" / ".codex-plugin" / "plugin.json"
        original = json.loads(path.read_bytes())
        for change, error in (({"version": "0.0.0"}, "version"), ({"skills": "../elsewhere"}, "invalid source manifest")):
            with self.subTest(change=change):
                path.write_text(json.dumps({**original, **change}), encoding="utf-8")
                with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, error):
                    self.verify()
                self.assertFalse(self.destination.exists())

    def test_existing_destination_is_preserved(self) -> None:
        self.destination.mkdir()
        sentinel = self.destination / "keep.txt"
        sentinel.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            self.verify()
        self.assertEqual(list(self.destination.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"keep")

    def test_asset_size_limits_apply_before_parsing(self) -> None:
        with mock.patch.object(smoke_release, "MAX_ARCHIVE_BYTES", 1):
            with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "size limits"):
                self.verify()
        with mock.patch.object(smoke_release, "MAX_CHECKSUM_BYTES", 1):
            with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, "size limits"):
                self.verify()
        self.assertFalse(self.destination.exists())

    def test_full_runner_verifies_downloads_and_removes_its_temporary_files(self) -> None:
        paths = []

        def run(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            if "clone" in command:
                source = Path(command[-1])
                paths.append(source.parent)
                self.assertNotEqual(environment["HOME"], str(Path.home()))
                shutil.copytree(self.source, source)
                return ""
            return smoke_release.SOURCE_COMMIT

        def download(url: str, destination: Path, limit: int) -> None:
            name = "SHA256SUMS" if url.endswith("/SHA256SUMS") else smoke_release.ARCHIVE_NAME
            self.assertEqual(url, f"{smoke_release.RELEASE_URL}/{name}")
            shutil.copyfile(self.root / name, destination)

        with mock.patch.object(smoke_release.shutil, "which", return_value="git"), mock.patch.object(
            smoke_release, "run", side_effect=run
        ), mock.patch.object(smoke_release, "download", side_effect=download) as downloads, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(smoke_release.main([]), 0)
        self.assertEqual(downloads.call_count, 2)
        self.assertIn("2 skills", output.getvalue())
        self.assertIn("smoke check passed", output.getvalue())
        self.assertEqual(len(paths), 1)
        self.assertFalse(paths[0].exists())

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_real_clone_uses_lf_bytes_even_with_crlf_checkout_defaults(self) -> None:
        home_dir = self.root / "home"
        home_dir.mkdir()
        environment = smoke_release.isolated_environment(home_dir)
        (self.source / ".gitattributes").write_bytes(b"* text=auto\n")
        for args in (
            ["init", "--quiet"],
            ["-c", "core.autocrlf=false", "-c", "core.eol=lf", "add", "--all"],
            ["-c", "user.name=Smoke Test", "-c", "user.email=smoke@example.invalid", "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Fixture"],
            ["tag", "vfixture"],
        ):
            subprocess.run(["git", *args], cwd=self.source, env=environment, check=True, capture_output=True)
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.source, env=environment, check=True, capture_output=True, text=True).stdout.strip()
        workspace = self.root / "clone workspace"
        workspace.mkdir()
        environment.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.eol", "GIT_CONFIG_VALUE_0": "crlf"})
        with mock.patch.object(smoke_release, "REPOSITORY_URL", str(self.source)), mock.patch.object(
            smoke_release, "SOURCE_TAG", "vfixture"
        ), mock.patch.object(smoke_release, "SOURCE_COMMIT", commit), redirect_stdout(io.StringIO()):
            cloned = smoke_release.clone_source(workspace, environment)
        self.assertEqual((cloned / "LICENSE").read_bytes(), self.files["LICENSE"])
        self.assertEqual((cloned / "second" / "references" / "café.md").read_bytes(), self.files["frey-skills/skills/second/references/café.md"])


class DownloadAndRunnerTests(unittest.TestCase):
    def test_download_limits_time_size_and_https_without_overwriting_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "asset"
            for payload, limit, times, url, error in (
                (b"too large", 2, [0, 0], "https://example.invalid/asset", "size limit"),
                (b"slow", 100, [0, 61], "https://example.invalid/asset", "time limit"),
                (b"plain", 100, [0], "http://example.invalid/asset", "HTTPS"),
            ):
                with self.subTest(error=error):
                    response = mock.MagicMock(wraps=io.BytesIO(payload))
                    response.__enter__.return_value = response
                    response.geturl = mock.Mock(return_value=url)
                    with mock.patch.object(smoke_release.urllib.request, "urlopen", return_value=response) as opened, mock.patch.object(
                        smoke_release.time, "monotonic", side_effect=times
                    ):
                        with self.assertRaisesRegex(smoke_release.ReleaseSmokeError, error):
                            smoke_release.download("https://example.invalid/asset", destination, limit)
                    self.assertEqual(opened.call_args.kwargs["timeout"], 30)
                    destination.unlink()
            destination.write_bytes(b"keep")
            with mock.patch.object(smoke_release.urllib.request, "urlopen"):
                with self.assertRaises(FileExistsError):
                    smoke_release.download("https://example.invalid/asset", destination, 100)
            self.assertEqual(destination.read_bytes(), b"keep")

    def test_successful_download_retains_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "asset"
            response = mock.MagicMock(wraps=io.BytesIO(b"archive bytes"))
            response.__enter__.return_value = response
            response.geturl = mock.Mock(return_value="https://example.invalid/asset")
            with mock.patch.object(smoke_release.urllib.request, "urlopen", return_value=response):
                smoke_release.download("https://example.invalid/asset", destination, 13)
            self.assertEqual(destination.read_bytes(), b"archive bytes")

    def test_tag_mismatch_stops_before_download_and_never_claims_success(self) -> None:
        with mock.patch.object(smoke_release.shutil, "which", return_value="git"), mock.patch.object(
            smoke_release, "run", side_effect=["cloned", "wrong commit"]
        ), mock.patch.object(smoke_release, "download") as download, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
            result = smoke_release.main([])
        self.assertEqual(result, 1)
        download.assert_not_called()
        self.assertNotIn("passed", output.getvalue())
        self.assertIn("pinned commit", errors.getvalue())

    def test_network_and_archive_failures_return_failure_without_a_success_claim(self) -> None:
        for failure in (urllib.error.URLError("offline"), TimeoutError("timed out"), zipfile.BadZipFile("corrupt")):
            with self.subTest(failure=failure), mock.patch.object(smoke_release.shutil, "which", return_value="git"), mock.patch.object(
                smoke_release, "run", side_effect=["cloned", smoke_release.SOURCE_COMMIT]
            ), mock.patch.object(smoke_release, "download", side_effect=failure), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(smoke_release.main([]), 1)
            self.assertNotIn("passed", output.getvalue())
            self.assertIn("smoke_release.py:", errors.getvalue())

    def test_offline_regressions_are_in_the_repository_gate(self) -> None:
        commands = check.group_commands("repository")
        self.assertTrue(any("scripts.test_smoke_release" in command for command in commands))


if __name__ == "__main__":
    unittest.main()
