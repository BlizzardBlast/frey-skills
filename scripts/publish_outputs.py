"""Publish staged local outputs with serialized writes and recoverable rollback."""

from __future__ import annotations

import shutil
from pathlib import Path


def publish_outputs(staging: Path, targets: tuple[Path, ...], *, replace: bool) -> None:
    """Keep prior outputs until every rename succeeds; retain backups on rollback failure.

    Callers stage complete outputs named like their targets on the same filesystem.
    The exclusive directory serializes cooperating publishers. It deliberately
    survives a process crash or failed rollback for manual inspection/recovery.
    Multiple target paths are recoverable, not atomically visible to readers.
    """
    if not targets:
        raise ValueError("publication requires at least one target")
    parent = targets[0].parent
    if len({target.name for target in targets}) != len(targets):
        raise ValueError("publication targets must have unique names")
    if any(target.name == ".frey-publish" for target in targets):
        raise ValueError(".frey-publish is reserved for publication recovery")
    for path in (staging, parent, *targets):
        if path.is_symlink() or path.resolve() != path.absolute():
            raise OSError(f"publication must not traverse a symlink or junction: {path}")
    if any(target.parent != parent for target in targets):
        raise ValueError("publication targets must share a directory")
    for target in targets:
        source = staging / target.name
        if not source.exists() or source.is_symlink() or source == target:
            raise OSError(f"missing or unsafe staged output: {source}")
        if not replace and target.exists():
            raise FileExistsError(f"publication target already exists: {target}")

    recovery = parent / ".frey-publish"
    try:
        recovery.mkdir()
    except FileExistsError as exc:
        raise OSError(f"publication active or recovery required; inspect {recovery}") from exc
    previous = recovery / "previous"
    try:
        previous.mkdir()
        for target in targets:
            if target.exists() or target.is_symlink():
                if not replace or target.is_symlink() or target.resolve() != target.absolute():
                    raise FileExistsError(f"publication target changed: {target}")
                target.rename(previous / target.name)
        for target in targets:
            if target.exists() or target.is_symlink():
                raise FileExistsError(f"publication target changed: {target}")
            (staging / target.name).rename(target)
    except Exception:
        try:
            for target in reversed(targets):
                if not (staging / target.name).exists():
                    target.rename(staging / target.name)
            for target in reversed(targets):
                backup = previous / target.name
                if backup.exists():
                    if target.exists() or target.is_symlink():
                        raise FileExistsError(f"cannot restore over concurrent output: {target}")
                    backup.rename(target)
        except OSError as exc:
            raise OSError(f"rollback incomplete; preserve and inspect {recovery}: {exc}") from exc
        remove_recovery(recovery)
        raise
    # Only remove previous outputs after the complete set has been published.
    # Never recursively remove a recovery path that has become linked.
    try:
        remove_recovery(recovery)
    except OSError as exc:
        raise OSError(f"published outputs; previous-output cleanup required at {recovery}: {exc}") from exc


def remove_recovery(recovery: Path) -> None:
    if recovery.is_symlink() or recovery.resolve() != recovery.absolute():
        raise OSError(f"recovery path changed: {recovery}")
    shutil.rmtree(recovery)
