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

try:
    from scripts.repository_layout import SourcePathError, discover_skill_names, is_runtime_artifact, validate_source_path
except ModuleNotFoundError:
    from repository_layout import SourcePathError, discover_skill_names, is_runtime_artifact, validate_source_path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "dist" / "frey-skills"
PLUGIN_TEMPLATE = REPOSITORY_ROOT / "plugin-template"


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

    try:
        output = validate_output_path(args.output)
        build_bundle(output, force=args.force)
    except BuildError as exc:
        print(f"build_plugin.py: error: {exc}", file=sys.stderr)
        return 1

    print(f"Built plugin bundle: {output}")
    return 0


class BuildError(Exception):
    """Raised when the plugin bundle cannot be built safely."""


def build_bundle(output: Path, *, force: bool = False) -> None:
    output = validate_output_path(output)
    try:
        validate_inputs()
        validate_output_target(output, force=force)
    except SourcePathError as exc:
        raise BuildError(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f".{output.name}.tmp-", dir=str(output.parent)) as temp_name:
        staged_output = Path(temp_name) / output.name
        write_bundle(staged_output)

        validate_output_path(output)
        try:
            if force:
                if output.is_dir():
                    shutil.rmtree(output)
                elif output.exists():
                    output.unlink()
            else:
                # rmdir refuses populated directories, including files added during staging.
                try:
                    output.rmdir()
                except FileNotFoundError:
                    pass
            # A directory rename cannot replace a populated directory or a regular file.
            staged_output.rename(output)
        except OSError as exc:
            raise BuildError(f"could not publish bundle at {output}: {exc}") from exc


def validate_output_path(output: Path) -> Path:
    """Inspect raw components for links before collapsing parent segments."""
    try:
        expanded = output.expanduser()
        tail = expanded.parts[1:] if expanded.anchor else expanded.parts
        # Normalize only the anchor (or current directory), never the raw tail.
        absolute = Path(os.path.abspath(expanded.anchor or os.curdir)).joinpath(*tail)
        candidate = Path()
        for part in absolute.parts:
            candidate = candidate.parent if part == ".." else candidate / part
            if candidate.is_symlink() or candidate.resolve() != candidate:
                raise BuildError(f"output must not traverse a symlink or junction: {output}")
    except (OSError, RuntimeError) as exc:
        raise BuildError(f"output cannot be resolved safely: {output}: {exc}") from exc
    return candidate


def validate_inputs() -> None:
    manifest = PLUGIN_TEMPLATE / ".codex-plugin" / "plugin.json"
    validate_source_path(manifest, REPOSITORY_ROOT)
    if not manifest.is_file():
        raise BuildError(f"missing template manifest: {manifest}")
    skill_names = discover_skill_names(REPOSITORY_ROOT)
    if not skill_names:
        raise BuildError(f"no canonical skill trees found below {REPOSITORY_ROOT}")
    for skill_name in skill_names:
        skill_root = REPOSITORY_ROOT / skill_name
        if not skill_root.is_dir():
            raise BuildError(f"missing canonical skill tree: {skill_root}")
        if not (skill_root / "SKILL.md").is_file():
            raise BuildError(f"missing canonical skill manifest: {skill_root / 'SKILL.md'}")
        reject_symlinks(skill_root)


def validate_output_target(output: Path, *, force: bool) -> None:
    repository_root = REPOSITORY_ROOT.resolve()
    resolved_output = output.resolve()
    default_output = repository_root / "dist" / "frey-skills"
    protected_sources = [repository_root, PLUGIN_TEMPLATE.resolve()]
    protected_sources.extend(
        (repository_root / skill_name).resolve()
        for skill_name in discover_skill_names(REPOSITORY_ROOT)
    )

    if any(is_relative_to(source, resolved_output) for source in protected_sources):
        raise BuildError(f"output must not contain the repository or canonical sources: {output}")
    if is_relative_to(resolved_output, repository_root) and resolved_output != default_output:
        raise BuildError(f"output inside the source root is only allowed at {default_output}: {output}")
    if output.exists():
        if output.is_symlink():
            raise BuildError(f"output must not be a symlink: {output}")
        if output.is_file():
            raise BuildError(f"output exists and is not a directory: {output}")
        if any(output.iterdir()) and not force:
            raise BuildError(f"output is non-empty; pass --force to replace it: {output}")


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def write_bundle(output: Path) -> None:
    (output / ".codex-plugin").mkdir(parents=True)
    copy_file_bytes(
        PLUGIN_TEMPLATE / ".codex-plugin" / "plugin.json",
        output / ".codex-plugin" / "plugin.json",
    )

    skills_root = output / "skills"
    skills_root.mkdir()
    for skill_name in discover_skill_names(REPOSITORY_ROOT):
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
        directory_names[:] = [name for name in directory_names if not is_runtime_artifact((Path(current_root) / name).relative_to(root))]
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
        directory_names[:] = [name for name in directory_names if not is_runtime_artifact((Path(current_root) / name).relative_to(root))]
        directory_names.sort()
        file_names.sort()
        current = Path(current_root)
        for name in file_names:
            path = current / name
            if path.is_symlink():
                raise BuildError(f"refusing to copy symlink file: {path}")
            if not is_runtime_artifact(path.relative_to(root)):
                yield path


def reject_symlinks(root: Path) -> None:
    if root.is_symlink() or root.resolve() != root.absolute():
        raise BuildError(f"symlinks and junctions are not allowed in plugin bundles: {root}")
    for path in root.rglob("*"):
        if path.is_symlink() or path.resolve() != path.absolute():
            raise BuildError(f"symlinks are not allowed in plugin bundles: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
