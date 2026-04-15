#!/usr/bin/env python3
"""Collect deterministic git review context as JSON.

Examples:
  python3 scripts/collect_review_context.py
  python3 scripts/collect_review_context.py --staged
  python3 scripts/collect_review_context.py --base origin/main --head HEAD
  python3 scripts/collect_review_context.py --base origin/main --head HEAD --output review-context.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git {' '.join(args)} failed: {error}")
    return result.stdout


def parse_name_status(text: str) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        raw_status = parts[0]
        status = raw_status[0] if raw_status else "?"

        previous_path: str | None = None
        path: str

        if status in {"R", "C"} and len(parts) >= 3:
            previous_path = parts[1]
            path = parts[2]
        else:
            path = parts[1]

        changes.append(
            {
                "path": path,
                "status": status,
                "previous_path": previous_path,
                "added_lines": 0,
                "deleted_lines": 0,
                "binary": False,
            }
        )
    return changes


def parse_numstat(text: str) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 3:
            continue

        added_raw, deleted_raw = parts[0], parts[1]
        path = parts[-1]

        if added_raw == "-" or deleted_raw == "-":
            stats[path] = {
                "added_lines": None,
                "deleted_lines": None,
                "binary": True,
            }
            continue

        try:
            added = int(added_raw)
            deleted = int(deleted_raw)
        except ValueError:
            continue

        stats[path] = {
            "added_lines": added,
            "deleted_lines": deleted,
            "binary": False,
        }
    return stats


def collect_context(
    *,
    base: str | None,
    head: str | None,
    staged: bool,
    max_files: int,
) -> dict[str, Any]:
    git_root = run_git(["rev-parse", "--show-toplevel"]).strip()

    if base and head:
        mode = "range"
        diff_target = f"{base}...{head}"
        name_status = run_git(["diff", "--name-status", "--find-renames", diff_target])
        numstat = run_git(["diff", "--numstat", "--find-renames", diff_target])
        base_ref, head_ref = base, head
    elif staged:
        mode = "staged"
        name_status = run_git(["diff", "--cached", "--name-status", "--find-renames"])
        numstat = run_git(["diff", "--cached", "--numstat", "--find-renames"])
        base_ref, head_ref = "HEAD", "INDEX"
    else:
        mode = "working-tree"
        name_status = run_git(["diff", "--name-status", "--find-renames", "HEAD"])
        numstat = run_git(["diff", "--numstat", "--find-renames", "HEAD"])
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

    return {
        "mode": mode,
        "git_root": git_root,
        "base": base_ref,
        "head": head_ref,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truncated": truncated,
        "omitted_files": omitted_files,
        "totals": {
            "files": len(changes),
            "added_lines": added_total,
            "deleted_lines": deleted_total,
            "binary_files": binary_total,
        },
        "files": changes,
    }


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
