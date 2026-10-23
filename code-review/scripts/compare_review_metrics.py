#!/usr/bin/env python3
"""Compare opt-in, sanitized paired code-review metrics without reading agent logs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FIELDS = (
    "input_tokens", "cached_input_tokens", "output_tokens", "tool_calls",
    "repeated_reads", "elapsed_seconds", "ci_seconds",
    "confirmed_findings", "invalid_findings", "missed_critical",
)
KEYS = set(FIELDS) | {"task_id", "arm", "outcome_passed"}
ARM_NAMES = ("baseline", "candidate")
MAX_BYTES = 1_000_000


class InvalidMetrics(ValueError):
    """A submitted aggregate is malformed or incomplete."""


def load_pairs(path: Path) -> list[tuple[dict, dict]]:
    try:
        with path.open("rb") as source:
            raw = source.read(MAX_BYTES + 1)
    except OSError as exc:
        raise InvalidMetrics("cannot read the local metrics file") from exc
    if len(raw) > MAX_BYTES:
        raise InvalidMetrics("input exceeds the 1 MB limit")
    try:
        document = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise InvalidMetrics("input must be UTF-8 JSON") from exc
    if not isinstance(document, dict) or set(document) != {"version", "runs"}:
        raise InvalidMetrics("expected only version and runs at the document root")
    if type(document["version"]) is not int or document["version"] != 1:
        raise InvalidMetrics("unsupported metrics schema version")
    runs = document["runs"]
    if not isinstance(runs, list) or not 1 <= len(runs) <= 1000:
        raise InvalidMetrics("runs must contain between 1 and 1000 entries")
    groups: dict[str, dict[str, dict]] = {}
    for record in runs:
        if not isinstance(record, dict) or set(record) != KEYS:
            raise InvalidMetrics("each run must contain exactly the documented aggregate fields")
        task_id = record["task_id"]
        if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", task_id):
            raise InvalidMetrics("task_id must be a short, anonymous slug")
        arm = record["arm"]
        if arm not in ARM_NAMES:
            raise InvalidMetrics("arm must be baseline or candidate")
        if type(record["outcome_passed"]) is not bool:
            raise InvalidMetrics("outcome_passed must be a boolean")
        if any(type(record[k]) is not int or record[k] < 0 for k in FIELDS):
            raise InvalidMetrics("aggregate counts and durations must be nonnegative integers")
        if record["cached_input_tokens"] > record["input_tokens"]:
            raise InvalidMetrics("cached input cannot exceed total input tokens")
        group = groups.setdefault(task_id, {})
        if arm in group:
            raise InvalidMetrics("duplicate task_id and arm")
        group[arm] = record
    if any(set(group) != set(ARM_NAMES) for group in groups.values()):
        raise InvalidMetrics("each task must have exactly one baseline and one candidate")
    return [(group["baseline"], group["candidate"]) for group in groups.values()]


def compare(pairs: list[tuple[dict, dict]], min_pairs: int = 5) -> dict:
    sums = {
        arm: {key: sum(pair[index][key] for pair in pairs) for key in FIELDS}
        for index, arm in enumerate(ARM_NAMES)
    }
    failures = {
        "new_critical_misses": sum(c["missed_critical"] > b["missed_critical"] for b, c in pairs),
        "worse_task_outcomes": sum(b["outcome_passed"] and not c["outcome_passed"] for b, c in pairs),
        "fewer_verified_findings": sum(c["confirmed_findings"] < b["confirmed_findings"] for b, c in pairs),
        "more_invalid_findings": sum(c["invalid_findings"] > b["invalid_findings"] for b, c in pairs),
    }
    reductions = {}
    for key in ("input_tokens", "output_tokens", "tool_calls", "repeated_reads", "elapsed_seconds", "ci_seconds"):
        baseline = sums["baseline"][key]
        candidate = sums["candidate"][key]
        reductions[key] = round(100 * (baseline - candidate) / baseline, 2) if baseline else None
    if any(failures.values()):
        status = "quality_concern"
    elif len(pairs) < min_pairs:
        status = "insufficient_sample"
    elif (
        sums["candidate"]["input_tokens"] + sums["candidate"]["output_tokens"]
        < sums["baseline"]["input_tokens"] + sums["baseline"]["output_tokens"]
        or sums["candidate"]["elapsed_seconds"] < sums["baseline"]["elapsed_seconds"]
    ):
        status = "promising_not_certified"
    else:
        status = "no_observed_efficiency_gain"
    return {
        "paired_tasks": len(pairs), "status": status, "quality_flags": failures,
        "totals": sums, "reductions_percent": reductions,
        "caveat": "Self-reported aggregates are not independent verification, causal proof, or a merge gate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Local sanitized JSON file; never raw agent logs")
    parser.add_argument("--min-pairs", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.min_pairs <= 500:
        parser.error("--min-pairs must be between 1 and 500")
    try:
        result = compare(load_pairs(args.input), args.min_pairs)
    except InvalidMetrics as exc:
        print(f"Invalid aggregate metrics: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
