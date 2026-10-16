#!/usr/bin/env python3
"""Offline regression proof for installation smoke assertions and isolation."""

from __future__ import annotations

import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import smoke_install


class InstallationSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.skills = self.project / ".agents" / "skills"
        self.expected = {
            "code-review/SKILL.md": b"---\nname: code-review\n---\n",
            "code-review/references/guide.md": b"Guide\n",
            "code-review/scripts/helper.py": b"# Inert helper\n",
            "code-review/agents/openai.yaml": b"interface: {}\n",
            "debug/SKILL.md": b"---\nname: debug\n---\n",
        }
        for path, data in self.expected.items():
            destination = self.skills / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)

    def test_complete_install_preserves_supporting_resources(self) -> None:
        smoke_install.verify_install(self.project, self.expected)

    def test_missing_extra_and_changed_resources_fail(self) -> None:
        for relative in ("code-review/SKILL.md", "code-review/references/guide.md", "code-review/scripts/helper.py", "code-review/agents/openai.yaml"):
            target = self.skills / relative
            original = target.read_bytes()
            with self.subTest(missing=relative), self.assertRaisesRegex(smoke_install.SmokeError, "missing="):
                target.unlink()
                smoke_install.verify_install(self.project, self.expected)
            target.write_bytes(original)
            with self.subTest(changed=relative), self.assertRaisesRegex(smoke_install.SmokeError, "changed="):
                target.write_bytes(b"different version\n")
                smoke_install.verify_install(self.project, self.expected)
            target.write_bytes(original)
        extra = self.skills / "code-review" / "unexpected.pyc"
        extra.write_bytes(b"cache")
        with self.assertRaisesRegex(smoke_install.SmokeError, "extra=.*unexpected.pyc"):
            smoke_install.verify_install(self.project, self.expected)

    def test_missing_or_unselected_skill_fails(self) -> None:
        with self.assertRaisesRegex(smoke_install.SmokeError, "skill set differs"):
            smoke_install.verify_install(self.root / "empty", self.expected)
        with self.assertRaisesRegex(smoke_install.SmokeError, "skill set differs"):
            smoke_install.verify_install(self.project, {key: value for key, value in self.expected.items() if key.startswith("code-review/")})

    def test_environment_isolates_home_and_disables_telemetry_without_mutating_caller(self) -> None:
        with mock.patch.dict(os.environ, {"HOME": "original", "USERPROFILE": "original", "CODEX_HOME": "original", "GIT_CONFIG_COUNT": "1"}):
            before = dict(os.environ)
            isolated = smoke_install.isolated_environment(self.root)
            self.assertEqual(dict(os.environ), before)
        self.assertEqual(isolated["HOME"], str(self.root))
        self.assertEqual(isolated["USERPROFILE"], str(self.root))
        self.assertNotIn("CODEX_HOME", isolated)
        self.assertNotIn("GIT_CONFIG_COUNT", isolated)
        self.assertEqual(isolated["DISABLE_TELEMETRY"], "1")
        self.assertEqual(isolated["DO_NOT_TRACK"], "1")
        self.assertEqual(isolated["GIT_CONFIG_GLOBAL"], os.devnull)

    def test_installer_failure_is_reported_with_a_timeout_and_no_shell_or_stdin(self) -> None:
        with mock.patch.object(smoke_install.subprocess, "run", return_value=subprocess.CompletedProcess([], 9, "partial", "failure")) as run:
            with self.assertRaisesRegex(smoke_install.SmokeError, "command failed \\(9\\)"):
                smoke_install.run(["node", "cli.mjs"], self.root, {})
        self.assertEqual(run.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(run.call_args.kwargs["timeout"], 180)
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_zero_exit_without_installed_files_cannot_pass(self) -> None:
        with mock.patch.object(smoke_install, "run", return_value=""), self.assertRaisesRegex(smoke_install.SmokeError, "skill set differs"):
            smoke_install.smoke_source(["node", "cli.mjs"], "source", self.expected, self.root / "case")

    def test_listing_must_not_install_any_files(self) -> None:
        def write_during_listing(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            (cwd / "unexpected.txt").write_text("unexpected", encoding="utf-8")
            return ""

        with mock.patch.object(smoke_install, "run", side_effect=write_during_listing), self.assertRaisesRegex(smoke_install.SmokeError, "listing skills wrote"):
            smoke_install.smoke_source(["node", "cli.mjs"], "source", self.expected, self.root / "case")

    def test_wrong_cli_version_stops_before_source_access(self) -> None:
        cli = self.root / "cli.mjs"
        cli.write_text("// inert fixture\n", encoding="utf-8")
        with mock.patch.object(smoke_install.shutil, "which", return_value="node"), mock.patch.object(
            smoke_install, "run", return_value="0.0.0"
        ) as run, mock.patch.object(smoke_install, "discover_skill_names") as discover, redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(smoke_install.main(["--cli", str(cli)]), 1)
        self.assertEqual(run.call_count, 1)
        discover.assert_not_called()
        self.assertIn("expected Skills CLI", errors.getvalue())

    def test_project_installation_must_not_change_user_files(self) -> None:
        def install_and_change_home(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            if "--list" in command:
                return ""
            selection = command[command.index("--skill") + 1]
            for path, data in self.expected.items():
                if selection == "*" or path.startswith(f"{selection}/"):
                    destination = cwd / ".agents" / "skills" / path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
            (Path(environment["HOME"]) / "unexpected.txt").write_text("unexpected", encoding="utf-8")
            return ""

        with mock.patch.object(smoke_install, "run", side_effect=install_and_change_home), self.assertRaisesRegex(smoke_install.SmokeError, "changed the disposable user's files"):
            smoke_install.smoke_source(["node", "cli.mjs"], "source", self.expected, self.root / "case")

    def test_moved_release_tag_stops_before_installation(self) -> None:
        cli = self.root / "cli.mjs"
        cli.write_text("// inert fixture\n", encoding="utf-8")
        with mock.patch.object(smoke_install.shutil, "which", return_value="tool"), mock.patch.object(
            smoke_install, "run", side_effect=[smoke_install.CLI_VERSION, "", "different-commit"]
        ), mock.patch.object(smoke_install, "smoke_source") as install, redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(smoke_install.main(["--cli", str(cli), "--source", "pinned"]), 1)
        install.assert_not_called()
        self.assertIn("release tag no longer matches", errors.getvalue())

    def test_timeout_returns_failure_without_a_success_claim(self) -> None:
        cli = self.root / "cli.mjs"
        cli.write_text("// inert fixture\n", encoding="utf-8")
        with mock.patch.object(smoke_install.shutil, "which", return_value="node"), mock.patch.object(
            smoke_install, "run", side_effect=subprocess.TimeoutExpired("node", 180)
        ), redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(smoke_install.main(["--cli", str(cli)]), 1)
        self.assertNotIn("checks passed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
