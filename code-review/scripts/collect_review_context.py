#!/usr/bin/env python3
"""Collect deterministic git review context as JSON.

Output semantics:
    - `included_totals`: stats for the returned `files` list (may be truncated).
    - `overall_totals`: stats for the full diff scope before truncation.
    - `generated_at`: optional wall-clock timestamp, included only with
        `--include-generated-at`.

Examples:
  python3 scripts/collect_review_context.py
  python3 scripts/collect_review_context.py --staged
  python3 scripts/collect_review_context.py --base origin/main --head HEAD
    python3 scripts/collect_review_context.py --include-generated-at
  python3 scripts/collect_review_context.py --base origin/main --head HEAD --output review-context.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
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


def _split_nul(text: str) -> list[str]:
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
            continue

        status = raw_status[0] if raw_status else "?"

        previous_path: str | None = None
        path: str

        if status in {"R", "C"}:
            if i + 1 >= len(fields):
                break
            previous_path = fields[i]
            path = fields[i + 1]
            i += 2
        else:
            if i >= len(fields):
                break
            path = fields[i]
            i += 1

        changes.append(
            {
                "path": path,
                "status": status,
                "previous_path": previous_path,
                "added_lines": None,
                "deleted_lines": None,
                "binary": False,
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
        raise ValueError("incomplete numstat rename/copy record")

    previous_path = fields[index]
    path = fields[index + 1]
    return path, previous_path, index + 2


def _build_numstat_stat(added_raw: str, deleted_raw: str) -> dict[str, Any] | None:
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
        return None

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
        parsed = _parse_numstat_header(header)
        if parsed is None:
            continue

        added_raw, deleted_raw, path = parsed

        try:
            path, previous_path, i = _consume_numstat_paths(path, fields, i)
        except ValueError:
            break

        stat = _build_numstat_stat(added_raw, deleted_raw)
        if stat is None:
            continue

        stats[path] = stat
        if previous_path:
            stats[previous_path] = stat

    return stats


def collect_context(
    *,
    base: str | None,
    head: str | None,
    staged: bool,
    max_files: int,
    include_generated_at: bool,
) -> dict[str, Any]:
    git_root = Path(run_git(["rev-parse", "--show-toplevel"]).strip()).name

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
        base_ref, head_ref = "HEAD", "INDEX"
    else:
        mode = "working-tree"
        name_status = run_git(["diff", "-z", "--name-status", "--find-renames", "HEAD"])
        numstat = run_git(["diff", "-z", "--numstat", "--find-renames", "HEAD"])
        base_ref, head_ref = "HEAD", "WORKTREE"

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

    changes.sort(key=lambda item: item["path"])

    overall_files = len(changes)
    overall_added_total = sum(
        item["added_lines"] for item in changes if isinstance(item.get("added_lines"), int)
    )
    overall_deleted_total = sum(
        item["deleted_lines"] for item in changes if isinstance(item.get("deleted_lines"), int)
    )
    overall_binary_total = sum(1 for item in changes if item.get("binary"))

    truncated = False
    omitted_files = 0
    if len(changes) > max_files:
        truncated = True
        omitted_files = len(changes) - max_files
        changes = changes[:max_files]

    added_total = sum(
        item["added_lines"] for item in changes if isinstance(item.get("added_lines"), int)
    )
    deleted_total = sum(
        item["deleted_lines"] for item in changes if isinstance(item.get("deleted_lines"), int)
    )
    binary_total = sum(1 for item in changes if item.get("binary"))

    result = {
        "mode": mode,
        "git_root": git_root,
        "base": base_ref,
        "head": head_ref,
        "truncated": truncated,
        "omitted_files": omitted_files,
        "included_totals": {
            "files": len(changes),
            "added_lines": added_total,
            "deleted_lines": deleted_total,
            "binary_files": binary_total,
        },
        "overall_totals": {
            "files": overall_files,
            "added_lines": overall_added_total,
            "deleted_lines": overall_deleted_total,
            "binary_files": overall_binary_total,
        },
        "files": changes,
    }

    if include_generated_at:
        # Optional wall-clock metadata. Excluded by default to keep output deterministic.
        from datetime import datetime, timezone

        result["generated_at"] = datetime.now(timezone.utc).isoformat()

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Collect a deterministic git diff summary for code reviews. "
            "Outputs structured JSON to stdout."
        )
    )
    parser.add_argument("--base", help="Base ref for range mode (e.g., origin/main)")
    parser.add_argument("--head", help="Head ref for range mode (e.g., HEAD)")
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
        help="Optional output file path for JSON (stdout still receives JSON).",
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
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    output = json.dumps(data, indent=2, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote review context to {out_path}", file=sys.stderr)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
