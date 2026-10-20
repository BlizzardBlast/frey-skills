#!/usr/bin/env python3
"""Regression tests for validation orchestration and dependency failures."""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts import check


class CheckTests(unittest.TestCase):
    def test_missing_dependencies_stop_before_any_command(self) -> None:
        with mock.patch.object(check.importlib.util, "find_spec", return_value=None), mock.patch.object(
            check.shutil, "which", return_value="git"
        ), mock.patch.object(check.subprocess, "run") as run, redirect_stderr(io.StringIO()) as errors:
            result = check.main([])
        self.assertEqual(result, 2)
        run.assert_not_called()
        self.assertIn("requirements-dev.txt", errors.getvalue())
        self.assertIn("requirements-spec.txt", errors.getvalue())
        self.assertIn(sys.executable, errors.getvalue())

    def test_spec_requires_python_311_but_core_checks_keep_python_39_support(self) -> None:
        with mock.patch.object(check.sys, "version_info", (3, 9)), mock.patch.object(
            check.importlib.util, "find_spec", return_value=object()
        ), mock.patch.object(check.shutil, "which", return_value="git"):
            self.assertEqual(check.preflight(("repository", "plugin")), [])
            self.assertEqual(len(check.preflight(("spec",))), 1)
            self.assertIn("Python 3.11", check.preflight(("spec",))[0])

    def test_groups_check_only_their_own_dependencies(self) -> None:
        with mock.patch.object(check.importlib.util, "find_spec", return_value=None), mock.patch.object(
            check.shutil, "which", return_value="git"
        ):
            self.assertEqual(check.preflight(("plugin", "whitespace")), [])
        with mock.patch.object(check.shutil, "which", return_value=None):
            self.assertIn("Git", check.preflight(("whitespace",))[0])

    def test_plugin_contracts_load_and_new_skill_contracts_run_without_site_packages(self) -> None:
        script = (
            "import importlib.util\nimport unittest\nfrom scripts import check\n"
            "assert importlib.util.find_spec('yaml') is None, 'PyYAML must be unavailable'\n"
            "loader = unittest.TestLoader()\n"
            "loader.loadTestsFromNames(check.CONTRACT_TESTS)\n"
            "if loader.errors:\n"
            "    raise SystemExit('\\n'.join(loader.errors))\n"
            "suite = loader.loadTestsFromNames((\n"
            "    'scripts.test_repository_orientation_contract',\n"
            "    'scripts.test_architecture_decision_contract',\n"
            "    'scripts.test_threat_modeling_contract',\n"
            "    'scripts.test_release_execution_contract',\n"
            "))\n"
            "result = unittest.TextTestRunner().run(suite)\n"
            "raise SystemExit(not result.wasSuccessful())\n"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-E", "-S", "-X", "utf8", "-c", script],
            cwd=check.REPOSITORY_ROOT,
            capture_output=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_posix_ps_stops_before_any_repository_command(self) -> None:
        with mock.patch.object(check, "os", SimpleNamespace(name="posix", environ=os.environ)), mock.patch.object(
            check.importlib.util, "find_spec", return_value=object()
        ), mock.patch.object(check.shutil, "which", side_effect=lambda name: "/tools/git" if name == "git" else None), mock.patch.object(
            check.subprocess, "run"
        ) as run, redirect_stderr(io.StringIO()) as errors, redirect_stdout(io.StringIO()) as output:
            result = check.main(["--group", "repository"])
        self.assertEqual(result, 2)
        run.assert_not_called()
        self.assertIn("ps must be available on PATH", errors.getvalue())
        self.assertNotIn("checks passed", output.getvalue())

    def test_ps_requirement_is_scoped_to_posix_repository_checks(self) -> None:
        for platform in ("posix", "nt"):
            for group in check.GROUPS:
                with self.subTest(platform=platform, group=group), mock.patch.object(
                    check, "os", SimpleNamespace(name=platform)
                ), mock.patch.object(check.sys, "version_info", (3, 12)), mock.patch.object(
                    check.importlib.util, "find_spec", return_value=object()
                ), mock.patch.object(check.shutil, "which", side_effect=lambda name: "/tools/git" if name == "git" else None):
                    errors = check.preflight((group,))
                if platform == "posix" and group == "repository":
                    self.assertEqual(len(errors), 1)
                    self.assertIn("ps must be available on PATH", errors[0])
                else:
                    self.assertEqual(errors, [])

    def test_failed_check_stops_remaining_checks_and_never_claims_success(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)
        ) as run, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
            result = check.main(["--group", "plugin"])
        self.assertEqual(result, 7)
        self.assertEqual(run.call_count, 1)
        self.assertNotIn("checks passed", output.getvalue())
        self.assertIn("remaining checks were not run", errors.getvalue())

    def test_missing_executable_reports_failure_without_success(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check.subprocess, "run", side_effect=OSError("missing executable")
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
            result = check.main(["--group", "whitespace"])
        self.assertEqual(result, 2)
        self.assertIn("could not run check", errors.getvalue())
        self.assertNotIn("checks passed", output.getvalue())

    def test_selected_groups_are_deduplicated_and_run_from_repository_root(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
        ) as run, redirect_stdout(io.StringIO()) as output:
            result = check.main(["--group", "whitespace", "--group", "whitespace"])
        self.assertEqual(result, 0)
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["git", "diff", "--check"], ["git", "diff", "--cached", "--check"]
        ])
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["cwd"], check.REPOSITORY_ROOT)
            self.assertFalse(call.kwargs["check"])
        self.assertIn("Behavioral model evals were not run", output.getvalue())

    def test_spec_validates_every_discovered_skill_with_selected_interpreter(self) -> None:
        with mock.patch.object(check, "discover_skill_names", return_value=("existing", "new-skill")):
            commands = check.group_commands("spec")
        self.assertEqual([command[-1] for command in commands], [
            str(check.REPOSITORY_ROOT / "existing"), str(check.REPOSITORY_ROOT / "new-skill")
        ])
        for command in commands:
            self.assertEqual(command[:6], [sys.executable, "-X", "utf8", "-m", "skills_ref.cli", "validate"])

    def test_empty_skill_discovery_is_a_failure(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check, "discover_skill_names", return_value=()
        ), mock.patch.object(check.subprocess, "run") as run, redirect_stderr(io.StringIO()) as errors:
            result = check.main(["--group", "spec"])
        self.assertEqual(result, 2)
        run.assert_not_called()
        self.assertIn("no canonical skills", errors.getvalue())

    def test_unsafe_skill_source_fails_before_running_commands(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check, "discover_skill_names", side_effect=check.SourcePathError("linked canonical source")
        ), mock.patch.object(check.subprocess, "run") as run, redirect_stderr(io.StringIO()) as errors:
            result = check.main(["--group", "spec"])
        self.assertEqual(result, 2)
        run.assert_not_called()
        self.assertIn("linked canonical source", errors.getvalue())

    def test_missing_base_fails_before_build_or_other_checks(self) -> None:
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check.subprocess, "run", return_value=subprocess.CompletedProcess([], 128, stdout="")
        ) as run, redirect_stderr(io.StringIO()) as errors:
            result = check.main(["--base", "missing"])
        self.assertEqual(result, 128)
        self.assertEqual(run.call_count, 1)
        self.assertIn("could not resolve local base", errors.getvalue())

    def test_base_is_resolved_with_option_terminator_before_diff(self) -> None:
        sha = "a" * 40
        results = [subprocess.CompletedProcess([], 0, stdout=sha + "\n")]
        results.extend(subprocess.CompletedProcess([], 0) for _ in range(3))
        with mock.patch.object(check, "preflight", return_value=[]), mock.patch.object(
            check.subprocess, "run", side_effect=results
        ) as run, redirect_stdout(io.StringIO()):
            result = check.main(["--group", "whitespace", "--base=--malicious-ref=value"])
        self.assertEqual(result, 0)
        self.assertEqual(run.call_args_list[0].args[0], [
            "git", "rev-parse", "--verify", "--end-of-options", "--malicious-ref=value^{commit}"
        ])
        self.assertEqual(run.call_args_list[-1].args[0], ["git", "diff", "--check", f"{sha}...HEAD"])

    def test_base_requires_whitespace_and_invalid_groups_never_run_commands(self) -> None:
        for args in (["--group", "unknown"], ["--group", "plugin", "--base", "HEAD"]):
            with self.subTest(args=args), mock.patch.object(check.subprocess, "run") as run, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    check.main(args)
                self.assertEqual(raised.exception.code, 2)
                run.assert_not_called()

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_real_git_rejects_staged_and_unstaged_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            subprocess.run(["git", "init", "--quiet", str(root)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "core.whitespace", "blank-at-eol"], check=True)
            path = root / "sample.txt"
            path.write_bytes(b"clean\n")
            subprocess.run(["git", "add", "sample.txt"], cwd=root, check=True)
            for staged in (False, True):
                with self.subTest(staged=staged):
                    path.write_bytes(b"trailing whitespace \n")
                    if staged:
                        subprocess.run(["git", "add", "sample.txt"], cwd=root, check=True)
                    with mock.patch.object(check, "REPOSITORY_ROOT", root), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                        result = check.main(["--group", "whitespace"])
                    self.assertNotEqual(result, 0)
                    self.assertNotIn("checks passed", output.getvalue())
            path.write_bytes(b"clean\n")
            subprocess.run(["git", "add", "sample.txt"], cwd=root, check=True)
            with mock.patch.object(check, "REPOSITORY_ROOT", root), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(check.main(["--group", "whitespace"]), 0)

    def test_real_subprocess_uses_utf8_for_parent_and_children_with_unicode_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "repository-\u03b2"
            root.mkdir()
            child = root / "echo.py"
            child.write_text("import sys\nprint(sys.argv[1])\nprint(sys.argv[1], file=sys.stderr)\n", encoding="utf-8")
            script = (
                "import sys\nfrom pathlib import Path\nfrom scripts import check\n"
                "check.REPOSITORY_ROOT = Path(sys.argv[1])\n"
                "check.preflight = lambda groups: []\n"
                "check.group_commands = lambda group: [[sys.executable, 'echo.py', str(check.REPOSITORY_ROOT)]]\n"
                "raise SystemExit(check.main(['--group', 'repository']))\n"
            )
            environment = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
            result = subprocess.run(
                [sys.executable, "-c", script, str(root)], cwd=check.REPOSITORY_ROOT,
                env=environment, capture_output=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(root), result.stdout)
            self.assertIn(str(root), result.stderr)
            self.assertIn("checks passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
