#!/usr/bin/env python3
"""Offline proof for client assertions, isolation, and bounded RPC cleanup."""

from __future__ import annotations

import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import smoke_codex as smoke


class ClientSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="client test café ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.codex_home = self.root / "home" / ".codex"
        self.extracted = self.root / "extracted"
        self.manifest = {
            "name": "frey-skills", "version": smoke.smoke_release.SOURCE_TAG.removeprefix("v"),
            "interface": {"defaultPrompt": ["One", "Two", "Three"]},
        }
        self.files = {
            ".codex-plugin/plugin.json": json.dumps(self.manifest).encode(),
            "skills/debug/SKILL.md": b"---\nname: debug\ndescription: Inert fixture.\n---\n",
            "skills/debug/references/café.md": "Supporting bytes: café\n".encode(),
            "skills/code-review/SKILL.md": b"---\nname: code-review\ndescription: Inert fixture.\n---\n",
        }
        self.installed = self.codex_home / "plugins" / "cache" / smoke.MARKETPLACE / "frey-skills" / self.manifest["version"]
        for root in (self.extracted, self.installed):
            for name, content in self.files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        self.plugin = {"plugin": {"marketplaceName": smoke.MARKETPLACE, "summary": {
            "id": f"frey-skills@{smoke.MARKETPLACE}", "name": "frey-skills", "localVersion": self.manifest["version"],
            "installed": True, "enabled": True, "interface": self.manifest["interface"],
        }}}
        self.listing = {"data": [{"cwd": str(self.project), "errors": [], "skills": [
            {"name": f"frey-skills:{name}", "enabled": True, "pluginId": self.plugin["plugin"]["summary"]["id"],
             "path": str(self.installed / "skills" / name / "SKILL.md")}
            for name in ("code-review", "debug")
        ]}]}

    def verify(self, plugin: dict | None = None, listing: dict | None = None) -> None:
        smoke.verify_metadata(self.plugin if plugin is None else plugin, self.listing if listing is None else listing,
                              self.extracted, self.project, self.codex_home)

    def test_verified_names_owner_enabled_paths_and_resource_bytes_pass(self) -> None:
        self.listing["data"][0]["skills"].append({"name": "debug", "pluginId": None, "path": "/unrelated"})
        self.verify()

    def test_wrong_version_disabled_uninstalled_and_missing_owner_fail(self) -> None:
        for key, value in (("localVersion", "1.8.1"), ("enabled", False), ("installed", False), ("id", None)):
            plugin = copy.deepcopy(self.plugin)
            plugin["plugin"]["summary"][key] = value
            with self.subTest(key=key), self.assertRaises(smoke.CodexSmokeError):
                self.verify(plugin=plugin)

    def test_missing_extra_duplicate_and_standalone_skills_cannot_pass(self) -> None:
        skills = self.listing["data"][0]["skills"]
        for wanted in (skills[:1], skills + [skills[0]], skills + [{**skills[0], "name": "frey-skills:extra"}],
                       [{**skill, "name": skill["name"].split(":")[1], "pluginId": None} for skill in skills]):
            listing = copy.deepcopy(self.listing)
            listing["data"][0]["skills"] = wanted
            with self.subTest(names=[skill["name"] for skill in wanted]), self.assertRaisesRegex(smoke.CodexSmokeError, "names differ"):
                self.verify(listing=listing)

    def test_disabled_wrong_owner_stale_external_and_relative_paths_fail(self) -> None:
        for key, value in (("enabled", False), ("pluginId", "another-plugin"), ("path", "relative/SKILL.md"),
                           ("path", str(self.extracted / "skills" / "debug" / "SKILL.md"))):
            listing = copy.deepcopy(self.listing)
            listing["data"][0]["skills"][1][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(smoke.CodexSmokeError):
                self.verify(listing=listing)
        stale = self.installed.parent / "1.8.1"
        shutil.copytree(self.installed, stale)
        listing = copy.deepcopy(self.listing)
        listing["data"][0]["skills"][1]["path"] = str(stale / "skills" / "debug" / "SKILL.md")
        with self.assertRaisesRegex(smoke.CodexSmokeError, "expected release"):
            self.verify(listing=listing)

    def test_wrong_project_load_errors_and_lost_prompts_fail(self) -> None:
        for key, value in (("cwd", "/another-project"), ("errors", [{"message": "fixture load failure"}])):
            listing = copy.deepcopy(self.listing)
            listing["data"][0][key] = value
            with self.subTest(key=key), self.assertRaises(smoke.CodexSmokeError):
                self.verify(listing=listing)
        self.plugin["plugin"]["summary"]["interface"] = {"defaultPrompt": ["One"]}
        with self.assertRaisesRegex(smoke.CodexSmokeError, "starter prompts"):
            self.verify()

    def test_previous_release_lost_prompts_fail(self) -> None:
        version = smoke.PREVIOUS_TAG.removeprefix("v")
        self.manifest["version"] = version
        for root in (self.extracted, self.installed):
            (root / ".codex-plugin" / "plugin.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        previous = self.installed.with_name(version)
        self.installed.rename(previous)
        self.installed = previous
        summary = self.plugin["plugin"]["summary"]
        summary["localVersion"] = version
        for skill in self.listing["data"][0]["skills"]:
            name = skill["name"].removeprefix("frey-skills:")
            skill["path"] = str(previous / "skills" / name / "SKILL.md")
        self.verify()
        summary["interface"] = {"defaultPrompt": ["One"]}
        with self.assertRaisesRegex(smoke.CodexSmokeError, "starter prompts"):
            self.verify()

    def test_changed_missing_and_extra_supporting_files_fail(self) -> None:
        resource = self.installed / "skills" / "debug" / "references" / "café.md"
        for content in (b"changed", None):
            if content is None:
                resource.unlink()
            else:
                resource.write_bytes(content)
            with self.subTest(content=content), self.assertRaisesRegex(smoke.CodexSmokeError, "bytes differ"):
                self.verify()
        resource.write_bytes(self.files["skills/debug/references/café.md"])
        (self.installed / "unexpected.pyc").write_bytes(b"cache")
        with self.assertRaisesRegex(smoke.CodexSmokeError, "bytes differ"):
            self.verify()

    def test_child_environment_has_no_inherited_credentials_or_configuration(self) -> None:
        inherited = {"OPENAI_API_KEY": "inert", "GH_TOKEN": "inert", "CODEX_HOME": "/real-home",
                     "CODEX_API_KEY": "inert", "NODE_OPTIONS": "inert", "HTTPS_PROXY": "inert",
                     "GIT_CONFIG_COUNT": "1", "APPDATA": "/real-appdata"}
        with mock.patch.dict(os.environ, inherited):
            before = dict(os.environ)
            environment = smoke.client_environment(self.root / "isolated")
            self.assertEqual(dict(os.environ), before)
        self.assertFalse(set(inherited) - {"CODEX_HOME", "APPDATA"} & environment.keys())
        self.assertEqual(environment["CODEX_HOME"], str(self.root / "isolated" / ".codex"))
        self.assertEqual(environment["APPDATA"], str(self.root / "isolated" / "AppData" / "Roaming"))

    def test_wrong_cli_and_archive_failure_stop_before_plugin_installation(self) -> None:
        entry = self.root / "codex.js"
        entry.write_bytes(b"inert")
        for version, error in (("codex-cli 0.0.0", None), (f"codex-cli {smoke.CLI_VERSION}", ValueError("archive mismatch"))):
            with self.subTest(version=version), mock.patch.object(smoke, "native_cli", return_value=["codex"]), mock.patch.object(
                smoke, "run", return_value=version
            ), mock.patch.object(smoke, "release_plugin", side_effect=error) as release, mock.patch.object(
                smoke, "smoke_client"
            ) as install, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                self.assertEqual(smoke.main(["--cli", str(entry)]), 1)
            install.assert_not_called()
            if error is None:
                release.assert_not_called()
            self.assertNotIn("compatibility passed", output.getvalue())

    def test_native_cli_requires_a_pinned_package_and_one_platform_binary(self) -> None:
        package = self.root / "@openai" / "codex"
        entry = package / "bin" / "codex.js"
        entry.parent.mkdir(parents=True)
        entry.write_bytes(b"inert")
        manifest = package / "package.json"
        manifest.write_text(json.dumps({"name": "@openai/codex", "version": "0.0.0"}), encoding="utf-8")
        with self.assertRaisesRegex(smoke.CodexSmokeError, "expected installed"):
            smoke.native_cli(entry)
        manifest.write_text(json.dumps({"name": "@openai/codex", "version": smoke.CLI_VERSION}), encoding="utf-8")
        with self.assertRaisesRegex(smoke.CodexSmokeError, "platform binary"):
            smoke.native_cli(entry)
        binary = "codex.exe" if os.name == "nt" else "codex"
        target = package.parent / "codex-fixture" / "vendor" / "fixture-triple" / "bin" / binary
        target.parent.mkdir(parents=True)
        target.write_bytes(b"inert")
        self.assertEqual(smoke.native_cli(entry), [str(target)])


class RpcTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="rpc test café ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.server = self.root / "server.py"
        self.record = self.root / "methods.jsonl"

    def server_code(self, behavior: str = "") -> list[str]:
        self.server.write_text(
            "import json, pathlib, subprocess, sys, time\n"
            f"record = pathlib.Path({str(self.record)!r})\n"
            "for line in sys.stdin:\n"
            "    message = json.loads(line)\n"
            "    with record.open('a', encoding='utf-8') as output:\n"
            "        output.write(json.dumps(message) + '\\n')\n"
            "    if 'id' not in message: continue\n"
            + behavior +
            "    print(json.dumps({'id': message['id'], 'result': {'method': message['method']}}), flush=True)\n",
            encoding="utf-8",
        )
        return [sys.executable, "-u", str(self.server)]

    def test_handshake_and_metadata_only_methods_do_not_start_threads_or_turns(self) -> None:
        plugin, skills = smoke.read_metadata(self.server_code(), self.root, smoke.client_environment(self.root), timeout=5)
        messages = [json.loads(line) for line in self.record.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([message["method"] for message in messages], ["initialize", "initialized", "plugin/read", "skills/list"])
        self.assertTrue(messages[0]["params"]["capabilities"]["experimentalApi"])
        self.assertTrue(messages[-1]["params"]["forceReload"])
        self.assertEqual(plugin, {"method": "plugin/read"})
        self.assertEqual(skills, {"method": "skills/list"})

    def test_rpc_errors_server_requests_bad_json_and_output_floods_fail(self) -> None:
        behaviors = (
            "    print(json.dumps({'id': message['id'], 'error': {'message': 'fixture'}}), flush=True)\n    continue\n",
            "    print(json.dumps({'id': 99, 'method': 'exec/request'}), flush=True)\n    continue\n",
            "    print('invalid JSON', flush=True)\n    continue\n",
            "    print('x' * 10000, file=sys.stderr, flush=True)\n    time.sleep(10)\n",
        )
        for behavior in behaviors:
            with self.subTest(behavior=behavior), mock.patch.object(smoke, "MAX_OUTPUT_BYTES", 2000):
                with self.assertRaises(ValueError):
                    smoke.read_metadata(self.server_code(behavior), self.root, smoke.client_environment(self.root), timeout=5)

    def test_timeout_and_success_clean_up_owned_descendants_with_inherited_handles(self) -> None:
        marker = self.root / "alive"
        child_code = f"import pathlib,time; p=pathlib.Path({str(marker)!r}); time.sleep(2); p.write_text('orphan'); time.sleep(30)"
        for hanging in (False, True):
            behavior = f"    if message['id'] == 1: subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
            if hanging:
                behavior += "    time.sleep(30)\n"
            start = time.monotonic()
            with self.subTest(hanging=hanging):
                if hanging:
                    with self.assertRaisesRegex(smoke.CodexSmokeError, "time limit"):
                        smoke.read_metadata(self.server_code(behavior), self.root, smoke.client_environment(self.root), timeout=0.5)
                else:
                    smoke.read_metadata(self.server_code(behavior), self.root, smoke.client_environment(self.root), timeout=5)
                self.assertLess(time.monotonic() - start, 7)
                time.sleep(2.1)
                self.assertFalse(marker.exists(), "owned child survived cleanup")

    def test_exited_parent_cannot_orphan_its_descendant(self) -> None:
        marker = self.root / "orphan"
        child = f"import pathlib,time; time.sleep(2); pathlib.Path({str(marker)!r}).write_text('alive'); time.sleep(5)"
        parent = f"import subprocess,sys; subprocess.Popen([sys.executable, '-c', {child!r}])"
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            with smoke.server_process([sys.executable, "-c", parent], self.root, smoke.client_environment(self.root), output, errors) as process:
                process.wait(timeout=5)
        time.sleep(2.1)
        self.assertFalse(marker.exists(), "descendant survived its exited parent")

    @unittest.skipUnless(os.name == "nt", "Windows job lifetime boundary")
    def test_killed_supervisor_terminates_server_and_descendant(self) -> None:
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            "TerminateProcess": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            getattr(kernel, name).argtypes = arguments
            getattr(kernel, name).restype = result

        server_pid, child_pid = self.root / "server.pid", self.root / "child.pid"
        child = f"import os,pathlib,time; pathlib.Path({str(child_pid)!r}).write_text(str(os.getpid()), encoding='ascii'); time.sleep(30)"
        server = (
            "import os,pathlib,subprocess,sys,time\n"
            f"pathlib.Path({str(server_pid)!r}).write_text(str(os.getpid()), encoding='ascii')\n"
            f"subprocess.Popen([sys.executable, '-B', '-c', {child!r}])\n"
            "time.sleep(30)\n"
        )
        supervisor = (
            "import sys,time\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})\n"
            "from scripts.smoke_codex import server_process, client_environment\n"
            f"root = Path({str(self.root)!r})\n"
            f"with server_process([sys.executable, '-B', '-c', {server!r}], root, client_environment(root), sys.stdout.buffer, sys.stderr.buffer):\n"
            "    time.sleep(30)\n"
        )
        handles = {}
        with tempfile.TemporaryFile() as output:
            # Bypass the Windows venv launcher so kill() targets the actual
            # supervisor that owns the Job Object, rather than its wrapper.
            process = subprocess.Popen([sys._base_executable, "-B", "-c", supervisor], stdout=output, stderr=output)
            try:
                deadline = time.monotonic() + 10
                while len(handles) < 2:
                    for path in (server_pid, child_pid):
                        if path in handles:
                            continue
                        try:
                            pid = int(path.read_text(encoding="ascii"))
                        except (FileNotFoundError, ValueError):
                            continue
                        handle = kernel.OpenProcess(0x00100001, False, pid)  # SYNCHRONIZE | PROCESS_TERMINATE
                        if not handle:
                            raise ctypes.WinError(ctypes.get_last_error())
                        handles[path] = handle
                    if len(handles) == 2:
                        break
                    self.assertIsNone(process.poll(), "supervisor exited before its descendants were ready")
                    self.assertLess(time.monotonic(), deadline, "server descendants did not become ready")
                    time.sleep(0.01)
                process.kill()
                process.wait(timeout=5)
                for path, handle in handles.items():
                    with self.subTest(process=path.name):
                        self.assertEqual(kernel.WaitForSingleObject(handle, 5000), 0,
                                         "owned process survived abrupt supervisor termination")
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                for handle in handles.values():
                    try:
                        if kernel.WaitForSingleObject(handle, 0) == 258:  # WAIT_TIMEOUT
                            if not kernel.TerminateProcess(handle, 1):
                                raise ctypes.WinError(ctypes.get_last_error())
                            self.assertEqual(kernel.WaitForSingleObject(handle, 5000), 0)
                    finally:
                        kernel.CloseHandle(handle)

    @unittest.skipUnless(os.name == "nt", "Windows file-sharing cleanup boundary")
    def test_transient_windows_handle_is_waited_for_and_permanent_lock_fails(self) -> None:
        with smoke.temporary_workspace("client-handle-test-") as workspace:
            handle = (workspace / "held").open("wb")
            timer = threading.Timer(0.2, handle.close)
            timer.start()
        timer.join(timeout=5)
        self.assertFalse(workspace.exists())
        handle = None
        try:
            with self.assertRaises(PermissionError):
                with smoke.temporary_workspace("client-locked-test-", cleanup_timeout=0.1) as workspace:
                    handle = (workspace / "held").open("wb")
        finally:
            if handle is not None:
                handle.close()
            shutil.rmtree(workspace)


if __name__ == "__main__":
    unittest.main()
