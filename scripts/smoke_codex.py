#!/usr/bin/env python3
"""Check pinned Codex plugin discovery, upgrade, and rollback (network opt-in)."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
import zlib
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator

try:
    from scripts import smoke_release
    from scripts.build_plugin import BuildError, reject_symlinks
    from scripts.repository_layout import discover_skill_names
    from scripts.smoke_install import isolated_environment, run, stop_process_tree
except ModuleNotFoundError:
    import smoke_release
    from build_plugin import BuildError, reject_symlinks
    from repository_layout import discover_skill_names
    from smoke_install import isolated_environment, run, stop_process_tree


CLI_VERSION = "0.150.1"
PREVIOUS_TAG = "v1.8.1"
PREVIOUS_COMMIT = "8fc076daa84782761d3ebf99f8f8902785119796"
MARKETPLACE = "frey-smoke"
MAX_OUTPUT_BYTES = 2 * 1024 * 1024


class CodexSmokeError(ValueError):
    """Client metadata did not prove the expected installed release."""


@contextmanager
def temporary_workspace(prefix: str, *, cleanup_timeout: float = 5) -> Iterator[Path]:
    temporary = tempfile.TemporaryDirectory(prefix=prefix)
    try:
        yield Path(temporary.name).resolve()
    finally:
        deadline = time.monotonic() + cleanup_timeout
        while True:
            try:
                temporary.cleanup()
                break
            except PermissionError as exc:
                # A terminated Windows helper can retain an inherited file
                # handle briefly after the job reports zero active processes.
                if os.name != "nt" or exc.winerror != 32 or time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)


def native_cli(entry: Path) -> list[str]:
    # Own the native server directly: a Node wrapper can exit while its child
    # still holds Windows project handles, masking assertion/cleanup failures.
    entry = entry.resolve()
    package = json.loads((entry.parents[1] / "package.json").read_bytes())
    if package.get("name") != "@openai/codex" or package.get("version") != CLI_VERSION:
        raise CodexSmokeError(f"expected installed @openai/codex@{CLI_VERSION}")
    binary = "codex.exe" if os.name == "nt" else "codex"
    candidates = list(entry.parents[2].glob(f"codex-*/vendor/*/bin/{binary}"))
    if len(candidates) != 1 or not candidates[0].is_file():
        raise CodexSmokeError("expected one installed Codex platform binary")
    return [str(candidates[0].resolve())]


def client_environment(home_dir: Path) -> dict[str, str]:
    # Allow only OS essentials and the explicitly isolated paths/settings. Do not
    # pass provider keys, auth tokens, proxies, or inherited Codex configuration.
    allowed = {
        "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR",
        "HOME", "USERPROFILE", "XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME",
        "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_TERMINAL_PROMPT", "GCM_INTERACTIVE",
        "DISABLE_TELEMETRY", "DO_NOT_TRACK", "CI", "NO_COLOR",
    }
    environment = {key: value for key, value in isolated_environment(home_dir).items() if key.upper() in allowed}
    environment.update({
        "CODEX_HOME": str(home_dir / ".codex"),
        "APPDATA": str(home_dir / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home_dir / "AppData" / "Local"),
    })
    return environment


def release_plugin(workspace: Path, environment: dict[str, str], tag: str, commit: str) -> tuple[Path, str]:
    workspace.mkdir()
    source = smoke_release.clone_source(workspace, environment, tag=tag, commit=commit)
    archive_name = f"frey-skills-{tag.removeprefix('v')}.zip"
    base = f"{smoke_release.REPOSITORY_URL}/releases/download/{tag}"
    archive, checksums = workspace / archive_name, workspace / "SHA256SUMS"
    smoke_release.download(f"{base}/SHA256SUMS", checksums, smoke_release.MAX_CHECKSUM_BYTES)
    smoke_release.download(f"{base}/{archive_name}", archive, smoke_release.MAX_ARCHIVE_BYTES)
    extracted = workspace / "extracted"
    digest = smoke_release.verify_archive(archive, checksums, source, extracted, tag=tag)
    return extracted / "frey-skills", digest


@contextmanager
def server_process(command: list[str], project: Path, environment: dict[str, str], output: BinaryIO, errors: BinaryIO) -> Iterator[subprocess.Popen[bytes]]:
    options = dict(cwd=project, env=environment, stdin=subprocess.PIPE, stdout=output, stderr=errors)
    if os.name != "nt":
        process = subprocess.Popen(command, start_new_session=True, **options)
        try:
            yield process
        finally:
            stop_process_tree(process)
            if process.stdin is not None:
                process.stdin.close()
        return

    # Assign a suspended process before it can create helpers. Terminating its
    # Job Object then owns every descendant even if an intermediate parent exits.
    import ctypes
    from ctypes import wintypes

    class ThreadEntry(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD), ("id", wintypes.DWORD),
                    ("owner", wintypes.DWORD), ("priority", wintypes.LONG),
                    ("delta", wintypes.LONG), ("flags", wintypes.DWORD)]

    class JobAccounting(ctypes.Structure):
        _fields_ = [("user", ctypes.c_int64), ("kernel", ctypes.c_int64),
                    ("period_user", ctypes.c_int64), ("period_kernel", ctypes.c_int64),
                    ("faults", wintypes.DWORD), ("total", wintypes.DWORD),
                    ("active", wintypes.DWORD), ("terminated", wintypes.DWORD)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateJobObjectW": ([wintypes.LPVOID, wintypes.LPCWSTR], wintypes.HANDLE),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID], wintypes.BOOL),
        "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
        "Thread32First": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        "Thread32Next": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        "OpenThread": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        "ResumeThread": ([wintypes.HANDLE], wintypes.DWORD),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        getattr(kernel, name).argtypes = arguments
        getattr(kernel, name).restype = result
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    process, assigned = None, False
    try:
        process = subprocess.Popen(command, creationflags=0x00000004, **options)  # CREATE_SUSPENDED
        if not kernel.AssignProcessToJobObject(job, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        assigned = True
        snapshot = kernel.CreateToolhelp32Snapshot(4, 0)  # TH32CS_SNAPTHREAD
        if snapshot == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            entry = ThreadEntry()
            entry.size = ctypes.sizeof(entry)
            found = kernel.Thread32First(snapshot, ctypes.byref(entry))
            while found and entry.owner != process.pid:
                found = kernel.Thread32Next(snapshot, ctypes.byref(entry))
            if not found:
                raise CodexSmokeError("cannot find the suspended server thread")
            thread = kernel.OpenThread(2, False, entry.id)  # THREAD_SUSPEND_RESUME
            if not thread:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                if kernel.ResumeThread(thread) == 0xFFFFFFFF:
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                kernel.CloseHandle(thread)
        finally:
            kernel.CloseHandle(snapshot)
        yield process
    finally:
        try:
            if assigned:
                if not kernel.TerminateJobObject(job, 1):
                    raise ctypes.WinError(ctypes.get_last_error())
                deadline = time.monotonic() + 5
                accounting = JobAccounting()
                while True:
                    if not kernel.QueryInformationJobObject(job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
                        raise ctypes.WinError(ctypes.get_last_error())
                    if not accounting.active:
                        break
                    if time.monotonic() >= deadline:
                        raise CodexSmokeError("server job cleanup exceeded its time limit")
                    time.sleep(0.01)
            elif process is not None:
                process.kill()
            if process is not None:
                process.wait(timeout=5)
        finally:
            kernel.CloseHandle(job)
            if process is not None and process.stdin is not None:
                process.stdin.close()


def read_metadata(cli: list[str], project: Path, environment: dict[str, str], *, timeout: float = 60) -> tuple[dict, dict]:
    """Use a fresh stdio server and only the three fixed metadata RPC methods."""
    deadline = time.monotonic() + timeout
    with temporary_workspace("frey-rpc-") as temporary:
        output_path, error_path = temporary / "stdout", temporary / "stderr"
        with output_path.open("wb") as output, error_path.open("wb") as errors, output_path.open("rb") as stdout:
            return _read_metadata(cli, project, environment, deadline, stdout, output, errors)


def _read_metadata(cli: list[str], project: Path, environment: dict[str, str], deadline: float, stdout: BinaryIO, output: BinaryIO, stderr: BinaryIO) -> tuple[dict, dict]:
    # The reader owns a separate file description, so reading cannot move the
    # child's write offset on either Windows or POSIX.
    with server_process([*cli, "app-server"], project, environment, output, stderr) as process:
        return _metadata_requests(process, project, deadline, stdout, stderr)


def _metadata_requests(process: subprocess.Popen[bytes], project: Path, deadline: float, stdout: BinaryIO, stderr: BinaryIO) -> tuple[dict, dict]:
    pending = b""

    def send(message: dict) -> None:
        assert process.stdin is not None
        process.stdin.write(json.dumps(message).encode("utf-8") + b"\n")
        process.stdin.flush()

    def request(identifier: int, method: str, params: dict) -> dict:
        nonlocal pending
        send({"id": identifier, "method": method, "params": params})
        while time.monotonic() < deadline:
            # Regular output files avoid unbounded pipe-reader cleanup when
            # a descendant inherits handles. Read only complete JSON lines.
            if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > MAX_OUTPUT_BYTES:
                raise CodexSmokeError("app-server output exceeded its size limit")
            chunk = stdout.read(MAX_OUTPUT_BYTES + 1)
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise CodexSmokeError("malformed app-server message")
                if "id" in message:
                    if "method" in message or message["id"] != identifier:
                        raise CodexSmokeError("unexpected app-server request or response")
                    if "error" in message or not isinstance(message.get("result"), dict):
                        raise CodexSmokeError(f"app-server {method} failed")
                    return message["result"]
            if process.poll() is not None:
                raise CodexSmokeError(f"app-server exited before {method} completed")
            time.sleep(0.01)
        raise CodexSmokeError(f"app-server {method} exceeded its time limit")

    request(1, "initialize", {
        "clientInfo": {"name": "frey_skills_smoke", "version": "1.0.0"},
        "capabilities": {"experimentalApi": True},
    })
    send({"method": "initialized", "params": {}})
    plugin = request(2, "plugin/read", {
        "pluginName": "frey-skills", "marketplacePath": str(project / ".agents" / "plugins" / "marketplace.json"),
    })
    skills = request(3, "skills/list", {"cwds": [str(project)], "forceReload": True})
    return plugin, skills


def verify_metadata(plugin: dict, listing: dict, extracted: Path, project: Path, codex_home: Path) -> None:
    manifest = json.loads((extracted / ".codex-plugin" / "plugin.json").read_bytes())
    version = manifest["version"]
    detail = plugin.get("plugin", {})
    summary = detail.get("summary", {})
    if (summary.get("name"), summary.get("localVersion"), summary.get("installed"), summary.get("enabled")) != (
        "frey-skills", version, True, True,
    ) or detail.get("marketplaceName") != MARKETPLACE or not summary.get("id"):
        raise CodexSmokeError("plugin is absent, disabled, or has the wrong installed version/marketplace")
    # 1.8.1's known prompt-limit defect is deliberately excluded from the
    # baseline check; the current release must retain every published prompt.
    if version == smoke_release.SOURCE_TAG.removeprefix("v"):
        if (summary.get("interface") or {}).get("defaultPrompt") != manifest["interface"]["defaultPrompt"]:
            raise CodexSmokeError("current release starter prompts differ from its manifest")
    entries = listing.get("data", [])
    if len(entries) != 1 or entries[0].get("cwd") != str(project) or entries[0].get("errors") != []:
        raise CodexSmokeError("skill discovery returned the wrong project or load errors")
    names = {f"frey-skills:{name}" for name in discover_skill_names(extracted / "skills")}
    skills = [skill for skill in entries[0].get("skills", []) if (
        str(skill.get("name", "")).startswith("frey-skills:") or skill.get("pluginId") == summary.get("id")
    )]
    actual = [skill.get("name") for skill in skills]
    if set(actual) != names or len(actual) != len(names) or not names:
        raise CodexSmokeError("plugin skill names differ (missing, extra, or duplicate entries)")
    roots = set()
    for skill in skills:
        path = Path(skill.get("path", ""))
        if not path.is_absolute():
            raise CodexSmokeError("plugin skill path must be absolute")
        path = path.resolve(strict=True)
        if skill.get("enabled") is not True or skill.get("pluginId") != summary.get("id"):
            raise CodexSmokeError("plugin skill is disabled or has the wrong owner")
        try:
            relative = path.relative_to((codex_home / "plugins" / "cache").resolve())
        except ValueError as exc:
            raise CodexSmokeError("plugin skill is outside the isolated cache") from exc
        name = skill["name"].removeprefix("frey-skills:")
        if version not in relative.parts or path.parts[-3:] != ("skills", name, "SKILL.md"):
            raise CodexSmokeError("plugin skill path does not identify the expected release")
        roots.add(path.parents[2])
    if len(roots) != 1:
        raise CodexSmokeError("plugin skills resolve to different installed roots")
    installed = roots.pop()
    reject_symlinks(installed)
    expected = {path.relative_to(extracted): path.read_bytes() for path in extracted.rglob("*") if path.is_file()}
    actual_files = {path.relative_to(installed): path.read_bytes() for path in installed.rglob("*") if path.is_file()}
    if actual_files != expected:
        raise CodexSmokeError("installed plugin bytes differ from the verified archive")


def smoke_client(cli: list[str], workspace: Path, environment: dict[str, str], previous: Path, current: Path) -> None:
    project = workspace / "project with spaces"
    project.mkdir()
    catalog = project / ".agents" / "plugins" / "marketplace.json"
    catalog.parent.mkdir(parents=True)
    plugins = project / "plugins"
    plugins.mkdir()
    for label, source in (("previous", previous), ("current", current)):
        shutil.copytree(source, plugins / label)
    sentinel = Path(environment["HOME"]) / ".agents" / "skills" / "frey-preserve" / "SKILL.md"
    sentinel.parent.mkdir(parents=True)
    sentinel_bytes = b"---\nname: frey-preserve\ndescription: Inert preservation fixture.\n---\nDo nothing.\n"
    sentinel.write_bytes(sentinel_bytes)
    for phase, label, source in (("install", "previous", previous), ("upgrade", "current", current), ("rollback", "previous", previous)):
        catalog.write_text(json.dumps({
            "name": MARKETPLACE,
            "plugins": [{"name": "frey-skills", "source": {"source": "local", "path": f"./plugins/{label}"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}],
        }) + "\n", encoding="utf-8")
        if phase == "install":
            run([*cli, "plugin", "marketplace", "add", str(project), "--json"], project, environment)
        run([*cli, "plugin", "add", f"frey-skills@{MARKETPLACE}", "--json"], project, environment)
        plugin, listing = read_metadata(cli, project, environment)
        verify_metadata(plugin, listing, source, project, Path(environment["CODEX_HOME"]))
        if sentinel.read_bytes() != sentinel_bytes:
            raise CodexSmokeError("client changed the unrelated user skill")
        version = json.loads((source / ".codex-plugin" / "plugin.json").read_bytes())["version"]
        count = len(discover_skill_names(source / "skills"))
        print(f"PASS {phase}: version {version}; {count} enabled plugin skills; isolated cache byte parity.", flush=True)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True, help=f"Installed @openai/codex@{CLI_VERSION}/bin/codex.js entry point.")
    args = parser.parse_args(argv)
    try:
        if not shutil.which("git") or not args.cli.is_file():
            raise CodexSmokeError("Git and the installed Codex CLI entry point are required")
        cli = native_cli(args.cli)
        with temporary_workspace("frey codex café ") as workspace:
            home_dir = workspace / "home"
            home_dir.mkdir()
            environment = client_environment(home_dir)
            Path(environment["CODEX_HOME"]).mkdir()
            if run([*cli, "--version"], workspace, environment) != f"codex-cli {CLI_VERSION}":
                raise CodexSmokeError(f"expected Codex CLI {CLI_VERSION}")
            releases = []
            for tag, commit in ((PREVIOUS_TAG, PREVIOUS_COMMIT), (smoke_release.SOURCE_TAG, smoke_release.SOURCE_COMMIT)):
                extracted, digest = release_plugin(workspace / tag, environment, tag, commit)
                releases.append(extracted)
                print(f"Verified {tag} at {commit}; SHA256: {digest}", flush=True)
            smoke_client(cli, workspace, environment, *releases)
        print("Codex client compatibility passed. Desktop UI and behavioral model evals were not run.")
        return 0
    except (OSError, ValueError, RuntimeError, BuildError, subprocess.SubprocessError, zipfile.BadZipFile, zlib.error) as exc:
        print(f"smoke_codex.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
