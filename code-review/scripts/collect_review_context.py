#!/usr/bin/env python3
"""Collect deterministic git review context as JSON.

This helper performs deterministic scope discovery only. It is not a substitute
for inspecting the actual diff and any relevant complete files during review.

Output semantics:
        - `mode`: one of `range`, `staged`, or `working-tree`.
        - `git_root`: repository directory name (not an absolute local path).
        - `base` / `head`: labels describing the compared refs.
        - `truncated` / `omitted_files`: whether `files` was capped by `--max-files`.
        - `included_totals`: stats for the returned `files` list (may be truncated).
        - `overall_totals`: stats for the full diff scope before truncation.
        - `files`: per-file status and line stats. In working-tree mode,
            untracked files are included with status `?`.
        - `generated_at`: optional wall-clock timestamp, included only with
            `--include-generated-at`.

Range semantics:
        When both `--base` and `--head` are supplied, diff scope uses three-dot
        syntax (`base...head`), i.e. changes from merge-base(base, head) to head.

Examples:
        python3 scripts/collect_review_context.py
        python3 scripts/collect_review_context.py --staged
        python3 scripts/collect_review_context.py --base origin/main --head HEAD
        python3 scripts/collect_review_context.py --include-generated-at
        python3 scripts/collect_review_context.py --base origin/main --head HEAD --output review-context.json
        python3 scripts/collect_review_context.py --output review-context.json --force
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git {' '.join(args)} failed: {error}")
    return result.stdout


class OutputWriteError(RuntimeError):
    pass


class ContextParseError(RuntimeError):
    pass


def git_has_head() -> bool:
    try:
        run_git(["rev-parse", "--verify", "--quiet", "HEAD"])
    except RuntimeError:
        return False
    return True


def stat_untracked_file(path: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        return {
            "added_lines": 1,
            "deleted_lines": 0,
            "binary": False,
        }

    try:
        with path.open("rb") as handle:
            added_lines = 0
            saw_data = False
            last_byte = b""

            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break

                saw_data = True
                if b"\0" in chunk:
                    return {
                        "added_lines": None,
                        "deleted_lines": None,
                        "binary": True,
                    }

                added_lines += chunk.count(b"\n")
                last_byte = chunk[-1:]
    except OSError:
        return None

    if saw_data and last_byte != b"\n":
        added_lines += 1

    return {
        "added_lines": added_lines,
        "deleted_lines": 0,
        "binary": False,
    }


def collect_untracked_changes(git_root_path: Path) -> list[dict[str, Any]]:
    paths = _split_nul(run_git(["ls-files", "--others", "--exclude-standard", "-z"]))
    changes: list[dict[str, Any]] = []

    for path in paths:
        stat = stat_untracked_file(git_root_path / path)
        change = {
            "path": path,
            "status": "?",
            "previous_path": None,
            "added_lines": None,
            "deleted_lines": None,
            "binary": False,
            "stats_available": False,
        }

        if stat is not None:
            change.update(stat)
            change["stats_available"] = True

        changes.append(change)

    return changes


def _split_nul(text: str) -> list[str]:
    if text and not text.endswith("\0"):
        raise ContextParseError("incomplete NUL record: missing terminator")

    fields = text.split("\0")
    if fields and fields[-1] == "":
        fields = fields[:-1]
    return fields


def parse_name_status(text: str) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    fields = _split_nul(text)
    i = 0

    while i < len(fields):
        raw_status = fields[i]
        i += 1
        if not raw_status:
            raise ContextParseError("malformed name-status record: missing status")

        status = raw_status[0] if raw_status else "?"

        previous_path: str | None = None
        path: str

        if status in {"R", "C"}:
            if i + 1 >= len(fields):
                raise ContextParseError(
                    f"incomplete name-status rename/copy record for status {raw_status!r}"
                )
            previous_path = fields[i]
            path = fields[i + 1]
            i += 2
        else:
            if i >= len(fields):
                raise ContextParseError(
                    f"incomplete name-status record for status {raw_status!r}"
                )
            path = fields[i]
            i += 1

        if not path or (status in {"R", "C"} and not previous_path):
            raise ContextParseError(
                f"malformed name-status record for status {raw_status!r}: missing path"
            )

        changes.append(
            {
                "path": path,
                "status": status,
                "previous_path": previous_path,
                "added_lines": None,
                "deleted_lines": None,
                "binary": False,
                "stats_available": False,
            }
        )
    return changes


def _parse_numstat_header(header: str) -> tuple[str, str, str] | None:
    if "\t" not in header:
        return None

    parts = header.split("\t", 2)
    if len(parts) < 3:
        return None

    return parts[0], parts[1], parts[2]


def _consume_numstat_paths(path: str, fields: list[str], index: int) -> tuple[str, str | None, int]:
    previous_path: str | None = None

    if path != "":
        return path, previous_path, index

    # In -z mode, rename/copy numstat records provide paths as separate NUL fields.
    if index + 1 >= len(fields):
        raise ContextParseError("incomplete numstat rename/copy record")

    previous_path = fields[index]
    path = fields[index + 1]
    if not previous_path or not path:
        raise ContextParseError("malformed numstat rename/copy record: missing path")
    return path, previous_path, index + 2


def _build_numstat_stat(added_raw: str, deleted_raw: str) -> dict[str, Any]:
    if added_raw == "-" or deleted_raw == "-":
        return {
            "added_lines": None,
            "deleted_lines": None,
            "binary": True,
        }

    try:
        added = int(added_raw)
        deleted = int(deleted_raw)
    except ValueError:
        raise ContextParseError(
            f"invalid numstat counts: added={added_raw!r}, deleted={deleted_raw!r}"
        )

    if added < 0 or deleted < 0:
        raise ContextParseError(
            f"invalid numstat counts: added={added_raw!r}, deleted={deleted_raw!r}"
        )

    return {
        "added_lines": added,
        "deleted_lines": deleted,
        "binary": False,
    }


def parse_numstat(text: str) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    fields = _split_nul(text)
    i = 0

    while i < len(fields):
        header = fields[i]
        i += 1
        if not header:
            raise ContextParseError("malformed numstat record: missing header")

        parsed = _parse_numstat_header(header)
        if parsed is None:
            raise ContextParseError(f"malformed numstat record: {header!r}")

        added_raw, deleted_raw, path = parsed

        path, previous_path, i = _consume_numstat_paths(path, fields, i)
        if not path:
            raise ContextParseError("malformed numstat record: missing path")

        stat = _build_numstat_stat(added_raw, deleted_raw)

        stats[path] = stat
        if previous_path:
            stats[previous_path] = stat

    return stats


def changed_line_count(change: dict[str, Any]) -> int:
    return sum(
        value
        for value in (change.get("added_lines"), change.get("deleted_lines"))
        if isinstance(value, int)
    )


def risk_priority(path: str) -> int:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    parts = [part for part in lowered.split("/") if part]
    name = parts[-1] if parts else lowered

    if "migrations" in parts:
        return 0

    if any(part in {"auth", "authentication", "permission", "permissions"} for part in parts):
        return 1

    if any(part == "security" or part.startswith("security-") for part in parts):
        return 2

    if (
        any(
            part in {
                "deploy",
                "deployment",
                "deployments",
                "infra",
                "infrastructure",
                "k8s",
                "kubernetes",
                "terraform",
                "helm",
            }
            for part in parts
        )
        or name in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}
    ):
        return 3

    if (
        lowered.startswith(".github/workflows/")
        or lowered.startswith(".circleci/")
        or name in {"gitlab-ci.yml", ".gitlab-ci.yml", "azure-pipelines.yml"}
    ):
        return 4

    if (
        name.endswith(".lock")
        or name in {
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "composer.lock",
            "poetry.lock",
            "pipfile.lock",
            "gemfile.lock",
            "go.mod",
            "go.sum",
            "cargo.toml",
            "cargo.lock",
            "requirements.txt",
            "pyproject.toml",
        }
    ):
        return 5

    return 6


def truncation_sort_key(change: dict[str, Any]) -> tuple[int, int, str]:
    return (
        risk_priority(str(change["path"])),
        -changed_line_count(change),
        str(change["path"]),
    )


def build_totals(changes: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "files": len(changes),
        "added_lines": sum(
            item["added_lines"] for item in changes if isinstance(item.get("added_lines"), int)
        ),
        "deleted_lines": sum(
            item["deleted_lines"] for item in changes if isinstance(item.get("deleted_lines"), int)
        ),
        "binary_files": sum(1 for item in changes if item.get("binary")),
        "unknown_stats_files": sum(1 for item in changes if not item.get("stats_available")),
    }


def collect_context(
    *,
    base: str | None,
    head: str | None,
    staged: bool,
    max_files: int,
    include_generated_at: bool,
) -> dict[str, Any]:
    git_root_path = Path(run_git(["rev-parse", "--show-toplevel"]).strip())
    git_root = git_root_path.name
    has_head = git_has_head()

    if base and head:
        mode = "range"
        diff_target = f"{base}...{head}"
        name_status = run_git(["diff", "-z", "--name-status", "--find-renames", diff_target])
        numstat = run_git(["diff", "-z", "--numstat", "--find-renames", diff_target])
        base_ref, head_ref = base, head
    elif staged:
        mode = "staged"
        name_status = run_git(["diff", "--cached", "-z", "--name-status", "--find-renames"])
        numstat = run_git(["diff", "--cached", "-z", "--numstat", "--find-renames"])
        base_ref, head_ref = ("HEAD" if has_head else "EMPTY_TREE"), "INDEX"
    else:
        mode = "working-tree"
        if has_head:
            name_status = run_git(["diff", "-z", "--name-status", "--find-renames", "HEAD"])
            numstat = run_git(["diff", "-z", "--numstat", "--find-renames", "HEAD"])
            base_ref = "HEAD"
        else:
            name_status = ""
            numstat = ""
            base_ref = "EMPTY_TREE"
        head_ref = "WORKTREE"

    changes = parse_name_status(name_status)
    stats = parse_numstat(numstat)

    for change in changes:
        path = change["path"]
        stat = stats.get(path)

        if stat is None and change.get("previous_path"):
            stat = stats.get(change["previous_path"])

        if stat is None:
            continue

        change["added_lines"] = stat["added_lines"]
        change["deleted_lines"] = stat["deleted_lines"]
        change["binary"] = stat["binary"]
        change["stats_available"] = True

    if mode == "working-tree":
        changes.extend(collect_untracked_changes(git_root_path))

    changes.sort(key=lambda item: item["path"])

    overall_totals = build_totals(changes)

    truncated = False
    omitted_files = 0
    if len(changes) > max_files:
        truncated = True
        omitted_files = len(changes) - max_files
        changes = sorted(changes, key=truncation_sort_key)[:max_files]

    result = {
        "mode": mode,
        "git_root": git_root,
        "base": base_ref,
        "head": head_ref,
        "truncated": truncated,
        "omitted_files": omitted_files,
        "included_totals": build_totals(changes),
        "overall_totals": overall_totals,
        "files": changes,
    }

    if include_generated_at:
        # Optional wall-clock metadata. Excluded by default to keep output deterministic.
        from datetime import datetime, timezone

        result["generated_at"] = datetime.now(timezone.utc).isoformat()

    return result


def write_output_file(output: str, out_path: Path, *, force: bool) -> None:
    if out_path.is_symlink():
        raise OutputWriteError(f"output file is a symbolic link: {out_path}")

    if out_path.exists() and not out_path.is_file():
        if out_path.is_dir():
            raise OutputWriteError(f"output path is a directory: {out_path}")
        raise OutputWriteError(f"output path exists and is not a regular file: {out_path}")

    if out_path.exists() and not force:
        raise OutputWriteError(f"output file already exists: {out_path}. Use --force to overwrite it.")

    temp_path: Path | None = None
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            dir=out_path.parent,
            prefix=f".{out_path.name}.",
            suffix=".tmp",
            encoding="utf-8",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(output + "\n")

        os.replace(temp_path, out_path)
    except OSError as err:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise OutputWriteError(f"failed to write output file {out_path}: {err}") from err


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Collect a deterministic git diff summary for code reviews. "
            "Outputs structured JSON to stdout. This is deterministic scope "
            "discovery only, not a substitute for inspecting the actual diff "
            "and relevant complete files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes:\n"
            "  0  Success.\n"
            "  2  Invalid arguments, git command failure, or diff parse failure.\n"
            "  3  Output file write failure.\n\n"
            "Examples:\n"
            "  python3 scripts/collect_review_context.py\n"
            "  python3 scripts/collect_review_context.py --staged\n"
            "  python3 scripts/collect_review_context.py --base origin/main --head HEAD\n"
            "  python3 scripts/collect_review_context.py --output review-context.json --force"
        ),
    )
    parser.add_argument(
        "--base",
        help=(
            "Base ref for range mode (e.g., origin/main). "
            "When combined with --head, uses merge-base diff semantics via base...head."
        ),
    )
    parser.add_argument(
        "--head",
        help=(
            "Head ref for range mode (e.g., HEAD). "
            "When combined with --base, uses merge-base diff semantics via base...head."
        ),
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Review staged changes only (index vs HEAD).",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=500,
        help="Maximum number of files to include in output (default: 500).",
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional output file path for JSON (stdout still receives JSON). "
            "Refuses to overwrite existing files unless --force is set."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow --output to overwrite an existing file.",
    )
    parser.add_argument(
        "--include-generated-at",
        action="store_true",
        help=(
            "Include wall-clock generated_at timestamp metadata. "
            "Disabled by default to keep output deterministic."
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if (args.base and not args.head) or (args.head and not args.base):
        parser.error("--base and --head must be provided together.")

    if args.staged and (args.base or args.head):
        parser.error("--staged cannot be combined with --base/--head.")

    if args.max_files <= 0:
        parser.error("--max-files must be a positive integer.")

    try:
        data = collect_context(
            base=args.base,
            head=args.head,
            staged=args.staged,
            max_files=args.max_files,
            include_generated_at=args.include_generated_at,
        )
    except (RuntimeError, ContextParseError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    output = json.dumps(data, indent=2, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        try:
            write_output_file(output, out_path, force=args.force)
        except OutputWriteError as err:
            print(f"Error: {err}", file=sys.stderr)
            print(output)
            return 3

        print(f"Wrote review context to {out_path}", file=sys.stderr)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
