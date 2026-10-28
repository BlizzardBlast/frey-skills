#!/usr/bin/env python3
"""Exercise the pinned Skills CLI in disposable Codex projects (network opt-in)."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from scripts.process_tree import owned_process, stop_process_tree
    from scripts.build_plugin import BuildError, copy_tree_bytes, iter_files, reject_symlinks
    from scripts.repository_layout import SourcePathError, discover_skill_names
except ModuleNotFoundError:
    from process_tree import owned_process, stop_process_tree
    from build_plugin import BuildError, copy_tree_bytes, iter_files, reject_symlinks
    from repository_layout import SourcePathError, discover_skill_names


ROOT = Path(__file__).resolve().parents[1]
CLI_VERSION = "1.7.2"
SOURCE_TAG = "v1.14.0"
SOURCE_COMMIT = "45ac0b73ed2fe05f849e919beec78225d84e3266"
REPOSITORY_URL = "https://github.com/BlizzardBlast/frey-skills"
SOURCE_URL = f"{REPOSITORY_URL}/tree/{SOURCE_TAG}"
MAX_OUTPUT_BYTES = 2 * 1024 * 1024


class SmokeError(ValueError):
    """An installer command or installed-file assertion failed."""




def run(command: list[str], cwd: Path, environment: dict[str, str], *, timeout: float = 180) -> str:
    print(f"Running: {subprocess.list2cmdline(command)}", flush=True)
    # Regular files avoid pipe readers waiting for descendants to close handles.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        with owned_process(command, cwd, environment, stdout, stderr, stdin=subprocess.DEVNULL) as process:
            deadline = time.monotonic() + timeout
            while True:
                if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > MAX_OUTPUT_BYTES:
                    raise SmokeError("command output exceeded its size limit")
                returncode = process.poll()
                if returncode is not None:
                    # Recheck after exit: a short-lived process may fill its output
                    # between the size check and poll. Never read an oversized file.
                    if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > MAX_OUTPUT_BYTES:
                        raise SmokeError("command output exceeded its size limit")
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                time.sleep(min(0.02, remaining))
        # Cleanup owns descendants even if the immediate child exited first.
        # Check their final writes before reading either output file.
        if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > MAX_OUTPUT_BYTES:
            raise SmokeError("command output exceeded its size limit")
        if returncode:
            tails = []
            for stream in (stdout, stderr):
                end = stream.seek(0, os.SEEK_END)
                stream.seek(max(0, end - 8000))
                tails.append(stream.read().decode("utf-8", errors="replace"))
            raise SmokeError(f"command failed ({returncode}):\n{''.join(tails)[-8000:]}")
        stdout.seek(0)
        content = stdout.read(MAX_OUTPUT_BYTES + 1)
        if len(content) > MAX_OUTPUT_BYTES:
            raise SmokeError("command output exceeded its size limit")
        return content.decode("utf-8", errors="replace").strip()


def isolated_environment(home_dir: Path) -> dict[str, str]:
    allowed = {
        "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR",
        "LANG", "LC_ALL", "LC_CTYPE", "PYTHONUTF8", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE",
    }
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    # Only child processes receive these paths; the caller's home is unchanged.
    environment.update({
        "HOME": str(home_dir), "USERPROFILE": str(home_dir),
        "APPDATA": str(home_dir / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home_dir / "AppData" / "Local"),
        "XDG_CONFIG_HOME": str(home_dir / ".config"),
        "XDG_STATE_HOME": str(home_dir / ".state"),
        "XDG_CACHE_HOME": str(home_dir / ".cache"),
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never",
        "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1", "CI": "1",
        "NO_COLOR": "1",
    })
    return environment


def skill_files(root: Path, names: tuple[str, ...]) -> dict[str, bytes]:
    files = {}
    for name in names:
        skill = root / name
        reject_symlinks(skill)
        for path in iter_files(skill):
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def verify_install(project: Path, expected: dict[str, bytes]) -> None:
    installed = project / ".agents" / "skills"
    reject_symlinks(installed)
    expected_names = {path.split("/", 1)[0] for path in expected}
    actual_names = {path.name for path in installed.iterdir()} if installed.is_dir() else set()
    if actual_names != expected_names:
        raise SmokeError(f"skill set differs: expected {sorted(expected_names)}, got {sorted(actual_names)}")
    # Inspect every installed file, including unexpected caches or other additions.
    actual = {
        path.relative_to(installed).as_posix(): path.read_bytes()
        for path in installed.rglob("*") if path.is_file()
    }
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(path for path in expected.keys() & actual.keys() if expected[path] != actual[path])
    if missing or extra or changed:
        raise SmokeError(f"installed files differ: missing={missing}, extra={extra}, changed={changed}")


def verify_listing(output: str, expected: set[str]) -> None:
    # CLI 1.7.2 rejects --list --json. Its name rows have four spaces after
    # the frame; description rows have six. Strip ANSI cursor/color controls.
    plain = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", output).replace("\r", "")
    listing = plain.partition("Available Skills")[2]
    names = re.findall(r"^[|\u2502] {4}(\S[^\r\n]*?)[ \t]*$", listing, re.MULTILINE)
    if set(names) != expected or len(names) != len(expected):
        raise SmokeError(f"discovery differs: expected {sorted(expected)}, got {sorted(names)}")


def smoke_source(cli: list[str], source: str, expected: dict[str, bytes], workspace: Path) -> None:
    selected = {path: data for path, data in expected.items() if path.startswith("code-review/")}
    if not selected:
        raise SmokeError("the documented code-review selection is absent from the source")
    names = {path.split("/", 1)[0] for path in expected}
    for mode in ("default", "copy"):
        options = ["--agent", "codex", "--yes"] + (["--copy"] if mode == "copy" else [])
        for label, selection, wanted in (("selected", "code-review", selected), ("complete", "*", expected)):
            case = workspace / mode / label
            project = case / "project with spaces"
            home_dir = case / "home"
            project.mkdir(parents=True)
            sentinel = home_dir / ".agents" / "skills" / "preserve" / "SKILL.md"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_bytes(b"Disposable user skill must survive project installation.\n")
            home_before = {path.relative_to(home_dir): path.read_bytes() for path in home_dir.rglob("*") if path.is_file()}
            environment = isolated_environment(home_dir)
            output = run([*cli, "add", source, "--list"], project, environment)
            if any(project.iterdir()):
                raise SmokeError("listing skills wrote to the disposable project")
            verify_listing(output, names)
            run([*cli, "add", source, "--skill", selection, *options], project, environment)
            verify_install(project, wanted)
            reject_symlinks(home_dir)
            home_after = {path.relative_to(home_dir): path.read_bytes() for path in home_dir.rglob("*") if path.is_file()}
            if home_before != home_after:
                raise SmokeError("project installation changed the disposable user's files")
        print(f"Verified {mode} installation: {len(expected)} files; selected skill and complete skill set.", flush=True)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True, help=f"Installed skills@{CLI_VERSION}/bin/cli.mjs entry point.")
    parser.add_argument("--source", action="append", choices=("checkout", "pinned"), help="Repeat to select sources; default: both. Pinned needs public GitHub access.")
    args = parser.parse_args(argv)
    try:
        node = shutil.which("node")
        if not node or not args.cli.is_file():
            raise SmokeError("Node.js and an installed Skills CLI entry point are required")
        cli = [node, str(args.cli.resolve())]
        with tempfile.TemporaryDirectory(prefix="frey smoke café ") as temporary:
            workspace = Path(temporary).resolve()
            home_dir = workspace / "home"
            home_dir.mkdir()
            environment = isolated_environment(home_dir)
            if run([*cli, "--version"], workspace, environment) != CLI_VERSION:
                raise SmokeError(f"expected Skills CLI {CLI_VERSION}")
            for source_kind in dict.fromkeys(args.source or ("checkout", "pinned")):
                source_root = workspace / f"{source_kind}-source"
                if source_kind == "checkout":
                    source_root.mkdir()
                    for name in discover_skill_names(ROOT):
                        reject_symlinks(ROOT / name)
                        copy_tree_bytes(ROOT / name, source_root / name)
                    source = str(source_root)
                else:
                    if not shutil.which("git"):
                        raise SmokeError("Git is required for the pinned source check")
                    run(["git", "clone", "--depth", "1", "--branch", SOURCE_TAG, REPOSITORY_URL, str(source_root)], workspace, environment)
                    if run(["git", "rev-parse", "HEAD"], source_root, environment) != SOURCE_COMMIT:
                        raise SmokeError("documented release tag no longer matches its expected commit")
                    source = SOURCE_URL
                names = discover_skill_names(source_root)
                if not names:
                    raise SmokeError(f"no canonical skills found in {source_kind}")
                smoke_source(cli, source, skill_files(source_root, names), workspace / source_kind)
        print("Installation smoke checks passed. Behavioral model evals were not run.")
        return 0
    except (OSError, ValueError, BuildError, SourcePathError, subprocess.SubprocessError) as exc:
        print(f"smoke_install.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
