#!/usr/bin/env python3
"""Build the deterministic frey-skills Codex plugin bundle."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Optional


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "dist" / "frey-skills"
PLUGIN_TEMPLATE = REPOSITORY_ROOT / "plugin-template"
EXPECTED_SKILLS = ("code-review", "iterative-self-review")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Bundle output directory. Defaults to dist/frey-skills.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the requested output directory if it already contains files.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    output = args.output.expanduser().resolve()

    try:
        build_bundle(output, force=args.force)
    except BuildError as exc:
        print(f"build_plugin.py: error: {exc}", file=sys.stderr)
        return 1

    print(f"Built plugin bundle: {output}")
    return 0


class BuildError(Exception):
    """Raised when the plugin bundle cannot be built safely."""


def build_bundle(output: Path, *, force: bool = False) -> None:
    validate_inputs()
    validate_output_target(output, force=force)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f".{output.name}.tmp-", dir=str(output.parent)) as temp_name:
        staged_output = Path(temp_name) / output.name
        write_bundle(staged_output)

        if output.exists():
            if output.is_symlink():
                raise BuildError(f"refusing to replace symlink output: {output}")
            if output.is_dir():
                shutil.rmtree(output)
            else:
                output.unlink()
        staged_output.rename(output)


def validate_inputs() -> None:
    manifest = PLUGIN_TEMPLATE / ".codex-plugin" / "plugin.json"
    if not manifest.is_file():
        raise BuildError(f"missing template manifest: {manifest}")
    for skill_name in EXPECTED_SKILLS:
        skill_root = REPOSITORY_ROOT / skill_name
        if not skill_root.is_dir():
            raise BuildError(f"missing canonical skill tree: {skill_root}")
        if not (skill_root / "SKILL.md").is_file():
            raise BuildError(f"missing canonical skill manifest: {skill_root / 'SKILL.md'}")
        reject_symlinks(skill_root)


def validate_output_target(output: Path, *, force: bool) -> None:
    if output == REPOSITORY_ROOT:
        raise BuildError("output must not be the repository root")
    if output.exists():
        if output.is_symlink():
            raise BuildError(f"output must not be a symlink: {output}")
        if output.is_file():
            raise BuildError(f"output exists and is not a directory: {output}")
        if any(output.iterdir()) and not force:
            raise BuildError(f"output is non-empty; pass --force to replace it: {output}")


def write_bundle(output: Path) -> None:
    (output / ".codex-plugin").mkdir(parents=True)
    copy_file_bytes(
        PLUGIN_TEMPLATE / ".codex-plugin" / "plugin.json",
        output / ".codex-plugin" / "plugin.json",
    )

    skills_root = output / "skills"
    skills_root.mkdir()
    for skill_name in EXPECTED_SKILLS:
        copy_tree_bytes(REPOSITORY_ROOT / skill_name, skills_root / skill_name)

    reject_symlinks(output)


def copy_tree_bytes(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True)

    for directory in sorted(iter_directories(source)):
        relative_directory = directory.relative_to(source)
        (destination / relative_directory).mkdir()

    for source_file in sorted(iter_files(source)):
        relative_file = source_file.relative_to(source)
        copy_file_bytes(source_file, destination / relative_file)


def copy_file_bytes(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise BuildError(f"refusing to copy symlink: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())


def iter_directories(root: Path) -> Iterable[Path]:
    for current_root, directory_names, file_names in os.walk(root):
        directory_names.sort()
        file_names.sort()
        current = Path(current_root)
        for name in directory_names:
            path = current / name
            if path.is_symlink():
                raise BuildError(f"refusing to copy symlink directory: {path}")
            yield path


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, directory_names, file_names in os.walk(root):
        directory_names.sort()
        file_names.sort()
        current = Path(current_root)
        for name in file_names:
            path = current / name
            if path.is_symlink():
                raise BuildError(f"refusing to copy symlink file: {path}")
            yield path


def reject_symlinks(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise BuildError(f"symlinks are not allowed in plugin bundles: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
