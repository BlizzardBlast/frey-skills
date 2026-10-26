#!/usr/bin/env python3
"""Offline regression proof for installation smoke assertions and isolation."""

from __future__ import annotations

import io
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import process_tree, smoke_install


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

    def test_command_failure_includes_exit_code_and_output(self) -> None:
        with self.assertRaisesRegex(smoke_install.SmokeError, "(?s)command failed \\(9\\).*failure"):
            smoke_install.run(
                [sys.executable, "-c", "import sys; print('failure'); sys.exit(9)"],
                self.root, dict(os.environ), timeout=10,
            )

    def test_environment_excludes_credentials_injection_and_real_user_paths(self) -> None:
        inherited = {key: "inert" for key in (
            "GITHUB_TOKEN", "GH_TOKEN", "OPENAI_API_KEY", "AWS_SECRET_ACCESS_KEY", "CUSTOM_SECRET",
            "NODE_OPTIONS", "PYTHONPATH", "GIT_SSH_COMMAND", "HTTPS_PROXY", "NPM_CONFIG_USERCONFIG",
        )}
        inherited.update({"PATH": "fixture-path", "SYSTEMROOT": "fixture-system", "APPDATA": "real-home"})
        with mock.patch.dict(os.environ, inherited, clear=True):
            environment = smoke_install.isolated_environment(self.root)
            self.assertEqual(dict(os.environ), inherited)
        for key in inherited.keys() - {"PATH", "SYSTEMROOT", "APPDATA"}:
            self.assertNotIn(key, environment)
        self.assertEqual(environment["PATH"], "fixture-path")
        self.assertEqual(environment["SYSTEMROOT"], "fixture-system")
        self.assertEqual(environment["APPDATA"], str(self.root / "AppData" / "Roaming"))

    def test_command_output_is_utf8_and_arguments_are_not_shell_code(self) -> None:
        argument = "caf\u00e9;$()&literal"
        output = smoke_install.run(
            [sys.executable, "-X", "utf8", "-c",
             "import sys; assert sys.stdin.read() == ''; print(sys.argv[1])", argument],
            self.root, dict(os.environ), timeout=10,
        )
        self.assertEqual(output, argument)

    def test_posix_cleanup_reaps_exited_leader_and_preserves_permission_failures(self) -> None:
        for denied in (False, True):
            with self.subTest(permission_denied=denied):
                process = mock.Mock(pid=123)
                process.poll.return_value = 0

                def signal_group(pid: int, sig: int) -> None:
                    if not process.poll.called or denied:
                        raise PermissionError("unreaped leader or inaccessible descendants")

                with mock.patch.object(process_tree, "os") as platform, \
                     mock.patch.object(process_tree, "signal") as signals, \
                     mock.patch.object(process_tree, "_macos_group_has_running_members", return_value=True):
                    platform.name = "posix"
                    platform.killpg.side_effect = signal_group
                    if denied:
                        with self.assertRaises(PermissionError):
                            process_tree.stop_process_tree(process)
                    else:
                        process_tree.stop_process_tree(process)
                    platform.killpg.assert_called_once_with(process.pid, signals.SIGKILL)
                process.kill.assert_not_called()
                process.wait.assert_called_once_with(timeout=5)

    def test_macos_snapshot_distinguishes_zombies_from_live_descendants(self) -> None:
        for output, expected in (
            ("", False),
            ("123 Z\n", False),
            ("123 Z\n123 R+\n", True),
            ("123 S\n", True),
            ("124 S\n", False),
        ):
            with self.subTest(output=output):
                completed = subprocess.CompletedProcess(args=["ps"], returncode=0, stdout=output, stderr="")
                with mock.patch.object(process_tree.subprocess, "run", return_value=completed) as run:
                    self.assertEqual(process_tree._macos_group_has_running_members(123), expected)
                    self.assertEqual(
                        run.call_args.args[0], ["/bin/ps", "-A", "-o", "pgid=", "-o", "stat="]
                    )
                    self.assertEqual(
                        run.call_args.kwargs["env"], {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}
                    )

        for failure in (
            subprocess.CompletedProcess(args=["ps"], returncode=1, stdout="", stderr="denied"),
            subprocess.CompletedProcess(args=["ps"], returncode=0, stdout="bad row\n", stderr=""),
        ):
            with self.subTest(failure=failure), mock.patch.object(
                process_tree.subprocess, "run", return_value=failure
            ), self.assertRaises(process_tree.ProcessCleanupError):
                process_tree._macos_group_has_running_members(123)

        with mock.patch.object(
            process_tree.subprocess, "run", side_effect=subprocess.TimeoutExpired(["ps"], 5)
        ), self.assertRaises(process_tree.ProcessCleanupError):
            process_tree._macos_group_has_running_members(123)

    def test_macos_process_inspection_ignores_inherited_path_and_credentials(self) -> None:
        completed = subprocess.CompletedProcess(args=["/bin/ps"], returncode=0, stdout="", stderr="")
        with mock.patch.dict(
            os.environ, {"PATH": "/untrusted/shadow", "GITHUB_TOKEN": "synthetic-credential"},
            clear=True,
        ):
            with mock.patch.object(
                process_tree.subprocess, "run", return_value=completed
            ) as run:
                self.assertFalse(process_tree._macos_group_has_running_members(123))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][0], "/bin/ps")
        self.assertEqual(
            run.call_args.kwargs["env"], {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}
        )
        self.assertNotIn("GITHUB_TOKEN", run.call_args.kwargs["env"])

    @unittest.skipUnless(sys.platform == "darwin", "macOS executable shadowing test")
    def test_macos_process_inspection_does_not_execute_shadow_ps(self) -> None:
        shadow = self.root / "ps"
        shadow.write_text(
            '#!/bin/sh\nprintf hijacked > "$0.marker"\n',
            encoding="utf-8",
        )
        shadow.chmod(0o755)
        marker = self.root / "ps.marker"
        with mock.patch.dict(
            os.environ, {"PATH": str(self.root), "GITHUB_TOKEN": "synthetic-credential"}
        ):
            # An impossible group ID avoids dependence on live processes.
            self.assertFalse(process_tree._macos_group_has_running_members(2147483647))
        self.assertFalse(marker.exists(), "shadow executable ran during cleanup")

    def test_macos_exited_group_permission_denial_only_ignored_when_empty(self) -> None:
        for exited_during_signal in (False, True):
            for group_live in (False, True):
                with self.subTest(raced=exited_during_signal, live=group_live):
                    process = mock.Mock(pid=123)
                    process.poll.side_effect = [None, 0, 0] if exited_during_signal else [0, 0, 0]
                    with mock.patch.object(process_tree, "os") as platform, \
                         mock.patch.object(process_tree, "sys") as system, \
                         mock.patch.object(process_tree, "signal") as signals, \
                         mock.patch.object(
                             process_tree, "_macos_group_has_running_members", return_value=group_live
                         ) as group_probe:
                        platform.name = "posix"
                        system.platform = "darwin"
                        platform.killpg.side_effect = PermissionError("already exited")
                        if group_live:
                            with self.assertRaises(PermissionError):
                                process_tree.stop_process_tree(process)
                        else:
                            process_tree.stop_process_tree(process)
                        self.assertEqual(platform.killpg.call_count, 2 if exited_during_signal else 1)
                        group_probe.assert_called_once_with(123)
                    process.wait.assert_called_once_with(timeout=5)
                    process.kill.assert_not_called()

    @unittest.skipUnless(sys.platform == "darwin", "macOS real process-group check")
    def test_macos_live_descendant_prevents_ignoring_group_signal_denial(self) -> None:
        marker = self.root / "owned-child.pid"
        parent_code = (
            "import subprocess,sys,time; from pathlib import Path; "
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], "
            "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
            f"Path({str(marker)!r}).write_text(str(child.pid)); "
            "time.sleep(30)"
        )
        leader = subprocess.Popen(
            [sys.executable, "-c", parent_code],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        real_killpg = os.killpg
        try:
            deadline = time.monotonic() + 5
            while not marker.is_file() and time.monotonic() < deadline:
                self.assertIsNone(leader.poll(), "fixture parent terminated unexpectedly")
                time.sleep(0.02)
            self.assertTrue(marker.is_file(), "fixture child did not start")
            child_pid = int(marker.read_text(encoding="utf-8"))
            self.assertEqual(os.getpgid(child_pid), leader.pid)
            self.assertTrue(process_tree._macos_group_has_running_members(leader.pid))
            with mock.patch.object(
                process_tree.os, "killpg", side_effect=PermissionError("simulated EPERM")
            ) as denied:
                with self.assertRaisesRegex(PermissionError, "simulated EPERM"):
                    process_tree.stop_process_tree(leader)
                denied.assert_called_once_with(leader.pid, signal.SIGKILL)
            self.assertTrue(process_tree._macos_group_has_running_members(leader.pid))
        finally:
            try:
                real_killpg(leader.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            leader.wait(timeout=5)

    @unittest.skipUnless(sys.platform == "darwin", "macOS real process-group check")
    def test_macos_exited_leader_with_live_descendant_preserves_signal_denial(self) -> None:
        marker = self.root / "orphaned-child.pid"
        parent_code = (
            "import subprocess,sys; from pathlib import Path; "
            "child = subprocess.Popen([sys.executable, '-B', '-c', 'import time; time.sleep(30)'], "
            "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
            f"Path({str(marker)!r}).write_text(str(child.pid))"
        )
        leader = subprocess.Popen(
            [sys.executable, "-B", "-c", parent_code],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        real_killpg = os.killpg
        try:
            self.assertEqual(leader.wait(timeout=5), 0)
            self.assertTrue(marker.is_file(), "leader exited before recording descendant")
            child_pid = int(marker.read_text(encoding="utf-8"))
            self.assertEqual(os.getpgid(child_pid), leader.pid)
            with mock.patch.object(
                process_tree, "_macos_group_has_running_members",
                wraps=process_tree._macos_group_has_running_members,
            ) as group_probe:
                with mock.patch.object(
                    process_tree.os, "killpg", side_effect=PermissionError("simulated EPERM")
                ) as denied:
                    with self.assertRaisesRegex(PermissionError, "simulated EPERM"):
                        process_tree.stop_process_tree(leader)
                    denied.assert_called_once_with(leader.pid, signal.SIGKILL)
                group_probe.assert_called_once_with(leader.pid)
            self.assertTrue(process_tree._macos_group_has_running_members(leader.pid))
        finally:
            try:
                real_killpg(leader.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if leader.poll() is None:
                leader.kill()
            leader.wait(timeout=5)

    @unittest.skipUnless(sys.platform == "darwin", "macOS real process-group check")
    def test_macos_exited_group_may_ignore_simulated_signal_denial(self) -> None:
        leader = subprocess.Popen(
            [sys.executable, "-c", "pass"], start_new_session=True,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            leader.wait(timeout=5)
            self.assertFalse(process_tree._macos_group_has_running_members(leader.pid))
            with mock.patch.object(
                process_tree.os, "killpg", side_effect=PermissionError("simulated EPERM")
            ) as denied:
                process_tree.stop_process_tree(leader)
                denied.assert_called_once_with(leader.pid, signal.SIGKILL)
        finally:
            if leader.poll() is None:
                leader.kill()
            leader.wait(timeout=5)

    def test_short_lived_success_and_failure_cannot_return_oversized_output(self) -> None:
        for stream in ("stdout", "stderr"):
            for exit_code in (0, 9):
                command = [sys.executable, "-B", "-c",
                           f"import sys; sys.{stream}.write('x' * (3 * 1024 * 1024)); sys.exit({exit_code})"]
                with self.subTest(stream=stream, exit=exit_code):
                    with self.assertRaisesRegex(smoke_install.SmokeError, "output exceeded its size limit"):
                        smoke_install.run(command, self.root, smoke_install.isolated_environment(self.root), timeout=10)

    def test_posix_cleanup_reaps_a_leader_that_exits_during_group_signal(self) -> None:
        for retry_result in (None, ProcessLookupError()):
            with self.subTest(group_disappeared=isinstance(retry_result, ProcessLookupError)):
                process = mock.Mock(pid=123)
                process.poll.side_effect = [None, 0, 0]
                with mock.patch.object(process_tree, "os") as platform, mock.patch.object(process_tree, "signal") as signals:
                    platform.name = "posix"
                    platform.killpg.side_effect = [PermissionError("leader exited during signal"), retry_result]
                    process_tree.stop_process_tree(process)
                    self.assertEqual(platform.killpg.call_count, 2)
                    platform.killpg.assert_has_calls([mock.call(process.pid, signals.SIGKILL)] * 2)
                process.kill.assert_not_called()
                process.wait.assert_called_once_with(timeout=5)

    def test_posix_cleanup_does_not_retry_permission_denial_for_a_running_leader(self) -> None:
        process = mock.Mock(pid=123)
        process.poll.return_value = None
        with mock.patch.object(process_tree, "os") as platform, mock.patch.object(process_tree, "signal"):
            platform.name = "posix"
            platform.killpg.side_effect = PermissionError("inaccessible live group")
            with self.assertRaises(PermissionError):
                process_tree.stop_process_tree(process)
            self.assertEqual(platform.killpg.call_count, 1)
        process.kill.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=5)

    def test_posix_cleanup_preserves_permission_denial_after_reaping_race(self) -> None:
        process = mock.Mock(pid=123)
        process.poll.side_effect = [None, 0, 0]
        with mock.patch.object(process_tree, "os") as platform, mock.patch.object(process_tree, "signal"):
            platform.name = "posix"
            platform.killpg.side_effect = [PermissionError("leader exited during signal"), PermissionError("inaccessible descendants")]
            with self.assertRaisesRegex(PermissionError, "inaccessible descendants"):
                process_tree.stop_process_tree(process)
            self.assertEqual(platform.killpg.call_count, 2)
        process.kill.assert_not_called()
        process.wait.assert_called_once_with(timeout=5)

    def test_continuous_output_stops_the_owned_tree_before_the_time_limit(self) -> None:
        parent_marker, child_marker = self.root / "parent.pid", self.root / "child.pid"
        child = "import sys,time\nwhile True:\n sys.stdout.buffer.write(b'x' * 65536); sys.stdout.flush(); time.sleep(0.001)\n"
        parent = (
            "import os,subprocess,sys,time; from pathlib import Path; "
            f"Path({str(parent_marker)!r}).write_text(str(os.getpid())); "
            f"child = subprocess.Popen([sys.executable, '-B', '-c', {child!r}]); "
            f"Path({str(child_marker)!r}).write_text(str(child.pid)); time.sleep(30)"
        )
        started = time.monotonic()
        with self.assertRaisesRegex(smoke_install.SmokeError, "output exceeded its size limit"):
            smoke_install.run([sys.executable, "-B", "-c", parent], self.root,
                              smoke_install.isolated_environment(self.root), timeout=20)
        self.assertLess(time.monotonic() - started, 12)
        for marker in (parent_marker, child_marker):
            self.assertTrue(marker.is_file(), "owned fixture process did not start")
            self.assert_process_stopped(int(marker.read_text()))

    def test_successful_parent_exit_also_stops_its_descendants(self) -> None:
        child_marker = self.root / "child.pid"
        parent = (
            "import subprocess,sys,time; from pathlib import Path; "
            "child = subprocess.Popen([sys.executable, '-B', '-c', 'import time; time.sleep(30)']); "
            f"Path({str(child_marker)!r}).write_text(str(child.pid)); time.sleep(0.2)"
        )
        smoke_install.run([sys.executable, "-B", "-c", parent], self.root,
                          smoke_install.isolated_environment(self.root), timeout=10)
        self.assert_process_stopped(int(child_marker.read_text()))

    def assert_process_stopped(self, pid: int) -> None:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
            kernel.WaitForSingleObject.restype = wintypes.DWORD
            kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
            kernel.CloseHandle.restype = wintypes.BOOL
            handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
            if handle:
                try:
                    self.assertEqual(kernel.WaitForSingleObject(handle, 3000), 0)
                finally:
                    kernel.CloseHandle(handle)
            else:
                self.assertEqual(ctypes.get_last_error(), 87)  # No such PID.
        else:
            # A killed orphan may remain a zombie briefly; it cannot run or hold output.
            deadline = time.monotonic() + 3
            while True:
                result = subprocess.run(
                    ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True,
                    text=True, timeout=5, check=False,
                )
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertFalse(result.stderr.strip(), result.stderr)
                if not result.stdout.strip() or result.stdout.strip().startswith("Z"):
                    return
                if time.monotonic() >= deadline:
                    self.fail(f"owned process {pid} still runs: {result.stdout}")
                time.sleep(0.05)

    def test_real_timeout_stops_descendants_without_waiting_for_inherited_output(self) -> None:
        parent_marker = self.root / "parent.pid"
        child_marker = self.root / "child.pid"
        child = "import time; print('child output', flush=True); time.sleep(30)"
        parent = (
            "import os,subprocess,sys,time; from pathlib import Path; "
            f"Path({str(parent_marker)!r}).write_text(str(os.getpid())); "
            f"child = subprocess.Popen([sys.executable, '-c', {child!r}]); "
            f"Path({str(child_marker)!r}).write_text(str(child.pid)); time.sleep(30)"
        )
        started = time.monotonic()
        stopped = set()
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                smoke_install.run([sys.executable, "-c", parent], self.root, dict(os.environ), timeout=3)
            self.assertLess(time.monotonic() - started, 12)
            for marker in (parent_marker, child_marker):
                self.assertTrue(marker.is_file(), "nested-process fixture did not start")
                pid = int(marker.read_text())
                self.assert_process_stopped(pid)
                stopped.add(pid)
        finally:
            # Keep the fixture bounded even if a future implementation regresses.
            for marker in (parent_marker, child_marker):
                if marker.is_file():
                    pid = int(marker.read_text())
                    if pid in stopped:
                        continue
                    if os.name == "nt":
                        taskkill = Path(os.environ["SystemRoot"]) / "System32" / "taskkill.exe"
                        subprocess.run([str(taskkill), "/PID", str(pid), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False)
                    else:
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

    def test_zero_exit_without_installed_files_cannot_pass(self) -> None:
        def no_install(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            return self.listing() if "--list" in command else ""

        with mock.patch.object(smoke_install, "run", side_effect=no_install), self.assertRaisesRegex(smoke_install.SmokeError, "skill set differs"):
            smoke_install.smoke_source(["node", "cli.mjs"], "source", self.expected, self.root / "case")

    def listing(self, names: tuple[str, ...] = ("code-review", "debug")) -> str:
        return "o  Available Skills\n|\n" + "\n".join(
            f"|    {name}\n|\n|      Description mentioning code-review and debug.\n" for name in names
        ) + "\n\u2014  Use --skill <name> to install specific skills\n"

    def install_files(self, command: list[str], cwd: Path, environment: dict[str, str]) -> str:
        if "--list" in command:
            return self.listing()
        selection = command[command.index("--skill") + 1]
        for path, data in self.expected.items():
            if selection == "*" or path.startswith(f"{selection}/"):
                destination = cwd / ".agents" / "skills" / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        return ""

    def test_wildcard_must_install_the_previously_selected_skill_from_scratch(self) -> None:
        def omit_code_review_from_wildcard(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            if "--skill" in command and command[command.index("--skill") + 1] == "*":
                target = cwd / ".agents" / "skills" / "debug" / "SKILL.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(self.expected["debug/SKILL.md"])
                return ""
            return self.install_files(command, cwd, environment)

        with mock.patch.object(smoke_install, "run", side_effect=omit_code_review_from_wildcard):
            with self.assertRaisesRegex(smoke_install.SmokeError, "skill set differs"):
                smoke_install.smoke_source(["unused-cli"], "source", self.expected, self.root / "case")

    def test_listing_rejects_empty_missing_extra_and_duplicate_skill_names(self) -> None:
        outputs = ("", "No skills found", self.listing(("debug",)),
                   self.listing(("debug", "code-review", "extra")),
                   self.listing(("debug", "code-review", "invalid_name")),
                   self.listing(("debug", "code-review", "invalid name")),
                   self.listing(("debug", "code-review", "debug")))
        for index, output in enumerate(outputs):
            with self.subTest(output=output), mock.patch.object(smoke_install, "run", return_value=output) as run:
                with self.assertRaisesRegex(smoke_install.SmokeError, "discovery differs"):
                    smoke_install.smoke_source(["unused-cli"], "source", self.expected, self.root / f"case-{index}")
                self.assertEqual(run.call_count, 1)

    def test_listing_accepts_framing_color_and_description_mentions(self) -> None:
        for frame in ("|", "\u2502"):
            output = self.listing().replace("|", frame).replace("code-review\n", "\x1b[36mcode-review\x1b[0m\n")
            smoke_install.verify_listing(output, {"code-review", "debug"})

    def test_each_selection_and_mode_starts_with_an_empty_project(self) -> None:
        projects = []

        def check_fresh_project(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
            if "--skill" in command:
                self.assertFalse(any(cwd.iterdir()))
                projects.append(cwd)
            return self.install_files(command, cwd, environment)

        with mock.patch.object(smoke_install, "run", side_effect=check_fresh_project):
            smoke_install.smoke_source(["unused-cli"], "source", self.expected, self.root / "case")
        self.assertEqual(len(set(projects)), 4)

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
                return self.listing()
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
