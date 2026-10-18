#!/usr/bin/env python3
"""Run the repository's deterministic quality gates on any supported platform."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from scripts.repository_layout import SourcePathError, discover_skill_names
except ModuleNotFoundError:
    from repository_layout import SourcePathError, discover_skill_names


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("repository", "spec", "plugin", "whitespace")
CONTRACT_TESTS = (
    "scripts.test_build_plugin",
    "scripts.test_prepare_release",
    "scripts.test_implementation_execution_contract",
    "scripts.test_test_strategy_contract",
    "scripts.test_release_readiness_contract",
    "scripts.test_change_specification_contract",
    "scripts.test_skill_behavior_contracts",
    "scripts.test_content_trust_contracts",
)


def preflight(groups: tuple[str, ...]) -> list[str]:
    errors = []
    if sys.version_info < (3, 9):
        errors.append("Repository checks require Python 3.9 or newer.")
    if "repository" in groups and importlib.util.find_spec("yaml") is None:
        errors.append("Missing PyYAML. Install requirements-dev.txt into this interpreter.")
    if "spec" in groups:
        if sys.version_info < (3, 11):
            errors.append("The Agent Skills reference validator requires Python 3.11 or newer.")
        if importlib.util.find_spec("skills_ref") is None:
            errors.append("Missing skills-ref. Install requirements-spec.txt into this interpreter.")
    if any(group != "spec" for group in groups) and shutil.which("git") is None:
        errors.append("Git must be available on PATH.")
    if "repository" in groups and os.name == "posix" and shutil.which("ps") is None:
        errors.append("ps must be available on PATH for POSIX repository checks. Install your platform's process-status utility.")
    return errors


def group_commands(group: str) -> list[list[str]]:
    python = sys.executable
    if group == "repository":
        return [
            [python, "scripts/validate_repository.py"],
            [python, "-m", "unittest", "discover", "-s", "code-review/scripts", "-p", "test_*.py"],
            [python, "-m", "unittest", "scripts.test_validate_repository", "scripts.test_check", "scripts.test_workflow_contracts", "scripts.test_smoke_install", "scripts.test_smoke_release", "scripts.test_smoke_codex"],
        ]
    if group == "spec":
        return [
            [python, "-X", "utf8", "-m", "skills_ref.cli", "validate", str(REPOSITORY_ROOT / name)]
            for name in discover_skill_names(REPOSITORY_ROOT)
        ]
    if group == "plugin":
        return [
            [python, "-m", "unittest", *CONTRACT_TESTS],
            [python, "scripts/build_plugin.py", "--force", "dist/frey-skills"],
            [python, "scripts/validate_plugin_bundle.py", "dist/frey-skills"],
        ]
    return [["git", "diff", "--check"], ["git", "diff", "--cached", "--check"]]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", action="append", choices=GROUPS, help="Run only this group; repeat to select more.")
    parser.add_argument("--base", help="Also check committed whitespace from the merge base of this local Git ref.")
    args = parser.parse_args(argv)
    groups = tuple(group for group in GROUPS if args.group is None or group in args.group)
    if args.base is not None and "whitespace" not in groups:
        parser.error("--base requires the whitespace group")

    errors = preflight(groups)
    if errors:
        for error in errors:
            print(f"check.py: {error}", file=sys.stderr)
        print(f"Selected interpreter: {sys.executable}", file=sys.stderr)
        return 2

    try:
        environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
        commands = []
        for group in groups:
            current = group_commands(group)
            if not current:
                print(f"check.py: no canonical skills found for {group}", file=sys.stderr)
                return 2
            commands.extend(current)
        if args.base is not None:
            base = subprocess.run(
                ["git", "rev-parse", "--verify", "--end-of-options", f"{args.base}^{{commit}}"],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            if base.returncode:
                print(f"check.py: could not resolve local base ref {args.base!r}", file=sys.stderr)
                return base.returncode
            commands.append(["git", "diff", "--check", f"{base.stdout.strip()}...HEAD"])

        for command in commands:
            print(f"Running: {subprocess.list2cmdline(command)}", flush=True)
            result = subprocess.run(command, cwd=REPOSITORY_ROOT, env=environment, check=False)
            if result.returncode:
                print(f"check.py: check failed with exit code {result.returncode}; remaining checks were not run.", file=sys.stderr)
                return result.returncode
    except (OSError, SourcePathError) as exc:
        print(f"check.py: could not run check: {exc}", file=sys.stderr)
        return 2

    print(f"Deterministic checks passed: {', '.join(groups)}. Behavioral model evals were not run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
