#!/usr/bin/env python3
"""Shared discovery rules for canonical skill directories."""

from __future__ import annotations

from pathlib import Path


EXCLUDED_ROOT_DIRS = {
    ".git",
    ".venv",
    ".omo",
    ".superpowers",
    "dist",
    "eval-workspace",
    "plugin-template",
}


class SourcePathError(ValueError):
    """A canonical source path is linked or escapes the repository."""


def validate_source_path(path: Path, repository_root: Path) -> None:
    """Require a repository-owned path without symlink or junction traversal."""
    absolute_path = path.absolute()
    try:
        absolute_path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise SourcePathError(f"canonical source must stay below the repository: {path}") from exc
    try:
        linked = absolute_path.is_symlink() or absolute_path.resolve() != absolute_path
    except (OSError, RuntimeError) as exc:
        raise SourcePathError(f"canonical source cannot be resolved safely: {path}") from exc
    if linked:
        raise SourcePathError(f"canonical source must not traverse a symlink or junction: {path}")


def is_runtime_artifact(relative_path: Path) -> bool:
    """Identify local Python/test caches that are not distributable skill source."""
    return bool({"__pycache__", ".pytest_cache"}.intersection(relative_path.parts)) or relative_path.suffix in {".pyc", ".pyo"}


def discover_skill_names(repository_root: Path) -> tuple[str, ...]:
    """Return canonical top-level skill directory names in stable order."""
    root = repository_root.resolve()
    names = []
    for child in sorted(root.iterdir(), key=lambda path: path.name):
        if child.name in EXCLUDED_ROOT_DIRS or not child.is_dir() or not (child / "SKILL.md").is_file():
            continue
        validate_source_path(child, root)
        validate_source_path(child / "SKILL.md", root)
        names.append(child.name)
    return tuple(names)
