#!/usr/bin/env python3
"""Exercise the pinned Skills CLI in disposable Codex projects (network opt-in)."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from scripts.build_plugin import BuildError, copy_tree_bytes, iter_files, reject_symlinks
    from scripts.repository_layout import SourcePathError, discover_skill_names
except ModuleNotFoundError:
    from build_plugin import BuildError, copy_tree_bytes, iter_files, reject_symlinks
    from repository_layout import SourcePathError, discover_skill_names


ROOT = Path(__file__).resolve().parents[1]
CLI_VERSION = "1.7.2"
SOURCE_TAG = "v1.8.1"
SOURCE_COMMIT = "8fc076daa84782761d3ebf99f8f8902785119796"
REPOSITORY_URL = "https://github.com/BlizzardBlast/frey-skills"
SOURCE_URL = f"{REPOSITORY_URL}/tree/{SOURCE_TAG}"


class SmokeError(ValueError):
    """An installer command or installed-file assertion failed."""


def run(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
    print(f"Running: {subprocess.list2cmdline(command)}", flush=True)
    result = subprocess.run(
        command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180, check=False,
    )
    if result.returncode:
        raise SmokeError(f"command failed ({result.returncode}):\n{(result.stdout + result.stderr)[-8000:]}")
    return result.stdout.strip()


def isolated_environment(home_dir: Path) -> dict[str, str]:
    environment = dict(os.environ)
    # Only child processes receive these paths; the caller's home is unchanged.
    for name in ("CODEX_HOME", "CLAUDE_CONFIG_DIR", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS"):
        environment.pop(name, None)
    environment.update({
        "HOME": str(home_dir), "USERPROFILE": str(home_dir),
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


def smoke_source(cli: list[str], source: str, expected: dict[str, bytes], workspace: Path) -> None:
    for mode in ("default", "copy"):
        case = workspace / mode
        project = case / "project with spaces"
        home_dir = case / "home"
        project.mkdir(parents=True)
        sentinel = home_dir / ".agents" / "skills" / "preserve" / "SKILL.md"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"Disposable user skill must survive project installation.\n")
        home_before = {path.relative_to(home_dir): path.read_bytes() for path in home_dir.rglob("*") if path.is_file()}
        environment = isolated_environment(home_dir)
        options = ["--agent", "codex", "--yes"] + (["--copy"] if mode == "copy" else [])
        # --list must discover the source without creating project installation files.
        run([*cli, "add", source, "--list"], project, environment)
        if any(project.iterdir()):
            raise SmokeError("listing skills wrote to the disposable project")
        selected = {path: data for path, data in expected.items() if path.startswith("code-review/")}
        if not selected:
            raise SmokeError("the documented code-review selection is absent from the source")
        run([*cli, "add", source, "--skill", "code-review", *options], project, environment)
        verify_install(project, selected)
        run([*cli, "add", source, "--skill", "*", *options], project, environment)
        verify_install(project, expected)
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
