#!/usr/bin/env python3
"""Shared discovery rules for canonical skill directories."""

from __future__ import annotations

from pathlib import Path


EXCLUDED_ROOT_DIRS = {
    ".git",
    ".omo",
    ".superpowers",
    "dist",
    "eval-workspace",
    "plugin-template",
}


def discover_skill_names(repository_root: Path) -> tuple[str, ...]:
    """Return canonical top-level skill directory names in stable order."""
    root = repository_root.resolve()
    return tuple(
        child.name
        for child in sorted(root.iterdir(), key=lambda path: path.name)
        if child.is_dir()
        and child.name not in EXCLUDED_ROOT_DIRS
        and (child / "SKILL.md").is_file()
    )
