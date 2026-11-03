#!/usr/bin/env python3
"""Validate the shape of an opt-in agentic architecture assessment (not evidence truth)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

CATALOG = Path(__file__).resolve().parents[1] / "references" / "agentic-architecture-criteria.json"
MAX_BYTES = 2_000_000
STATUSES = frozenset({"compliant", "partially_compliant", "non_compliant", "not_applicable", "not_reviewed"})
ITEM_FIELDS = frozenset({"status", "evidence", "reason", "gap", "remediation"})


class AssessmentError(ValueError):
    """Invalid catalog or assessment input."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise AssessmentError("duplicate JSON key (name omitted to protect log output)")
        obj[key] = value
    return obj


def read_json(path: Path) -> Any:
    try:
        # Reject pipes, devices, directories and symlinks before opening. An
        # opened descriptor is checked again to detect a replaced path.
        inspected = path.lstat()
        if not stat.S_ISREG(inspected.st_mode):
            raise AssessmentError("input must be a regular file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise AssessmentError("input must be a regular file")
            # O_NOFOLLOW is unavailable on some platforms, including Windows.
            # Verify the opened file is the one inspected, failing closed when
            # file identity is unavailable rather than trusting a path race.
            if not inspected.st_ino or not opened.st_ino:
                raise AssessmentError("input file identity unavailable")
            if (inspected.st_dev, inspected.st_ino) != (opened.st_dev, opened.st_ino):
                raise AssessmentError("input changed between inspection and open")
            if opened.st_size > MAX_BYTES:
                raise AssessmentError("input exceeds size limit")
            payload = stream.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise AssessmentError("input exceeds size limit")
        return json.loads(payload.decode("utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise AssessmentError(f"cannot read valid JSON: {exc}") from exc


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_keys(obj: Any, expected: set[str] | frozenset[str], label: str) -> None:
    if not isinstance(obj, dict) or set(obj) != set(expected):
        raise AssessmentError(f"{label}: expected keys {sorted(expected)}")


def validate_catalog(catalog: Any) -> list[str]:
    require_keys(catalog, {"schema_version", "catalog_version", "criteria"}, "catalog")
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 2:
        raise AssessmentError("unsupported catalog schema_version")
    if not nonempty(catalog["catalog_version"]):
        raise AssessmentError("invalid catalog_version")
    criteria = catalog["criteria"]
    if not isinstance(criteria, list) or not criteria:
        raise AssessmentError("catalog criteria must be nonempty")
    ids: list[str] = []
    for index, item in enumerate(criteria):
        require_keys(item, {"id", "area", "risk", "question"}, f"criterion {index}")
        if not all(nonempty(item[field]) for field in ("id", "area", "question")):
            raise AssessmentError(f"criterion {index}: empty field")
        if item["risk"] not in ("high", "medium", "low"):
            raise AssessmentError(f"criterion {index}: invalid risk")
        if item["id"] in ids:
            raise AssessmentError(f"duplicate criterion ID: {item['id']}")
        ids.append(item["id"])
    return ids


def catalog_sha256(catalog: Any) -> str:
    """Digest canonical criteria data, unaffected by JSON formatting/key order."""
    encoded = json.dumps(
        catalog, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_assessment(report: Any, catalog: Any) -> None:
    ids = validate_catalog(catalog)
    require_keys(report, {"schema_version", "catalog_version", "catalog_sha256", "scope", "assessments"}, "report")
    if type(report["schema_version"]) is not int or report["schema_version"] != catalog["schema_version"]:
        raise AssessmentError("report schema_version differs from catalog")
    if report["catalog_version"] != catalog["catalog_version"]:
        raise AssessmentError("report catalog_version differs from catalog")
    if report["catalog_sha256"] != catalog_sha256(catalog):
        raise AssessmentError("report catalog_sha256 differs from current criteria")
    if not nonempty(report["scope"]):
        raise AssessmentError("report scope is missing")
    results = report["assessments"]
    if not isinstance(results, dict) or set(results) != set(ids):
        # Report keys are untrusted: never echo unknown keys into terminal logs.
        raise AssessmentError("assessments must contain exactly the catalog IDs")

    for criterion_id in ids:
        item = results[criterion_id]
        require_keys(item, ITEM_FIELDS, criterion_id)
        status = item["status"]
        if not isinstance(status, str) or status not in STATUSES:
            raise AssessmentError(f"{criterion_id}: invalid status")
        evidence = item["evidence"]
        if not isinstance(evidence, list) or len(evidence) > 30:
            raise AssessmentError(f"{criterion_id}: evidence must be a bounded list")
        for index, record in enumerate(evidence):
            require_keys(record, {"source", "observation"}, f"{criterion_id} evidence {index}")
            if not nonempty(record["source"]) or not nonempty(record["observation"]):
                raise AssessmentError(f"{criterion_id}: blank evidence reference")
        if any(not isinstance(item[field], str) for field in ("reason", "gap", "remediation")):
            raise AssessmentError(f"{criterion_id}: reason, gap and remediation must be strings")
        if status == "compliant":
            valid = bool(evidence) and not any(item[key].strip() for key in ("reason", "gap", "remediation"))
        elif status in ("partially_compliant", "non_compliant"):
            valid = bool(evidence) and nonempty(item["gap"]) and nonempty(item["remediation"]) and not item["reason"].strip()
        else:
            # Uncertain/inapplicable conclusions can retain verified inspection
            # references while explaining why no definitive judgment follows.
            valid = nonempty(item["reason"]) and not item["gap"].strip() and not item["remediation"].strip()
        if not valid:
            raise AssessmentError(f"{criterion_id}: required fields conflict with status {status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", type=Path, help="Local JSON report to validate (read-only)")
    parser.add_argument(
        "--print-catalog-sha256", action="store_true",
        help="Print the current canonical catalog digest for a new report",
    )
    args = parser.parse_args(argv)
    if args.print_catalog_sha256 and args.report is not None:
        parser.error("a report path cannot accompany --print-catalog-sha256")
    if not args.print_catalog_sha256 and args.report is None:
        parser.error("provide a report path or --print-catalog-sha256")
    try:
        catalog = read_json(CATALOG)
        validate_catalog(catalog)
        if args.print_catalog_sha256:
            print(catalog_sha256(catalog))
            return 0
        report = read_json(args.report)
        validate_assessment(report, catalog)
    except (AssessmentError, TypeError) as exc:
        print(f"Invalid agentic assessment: {exc}", file=sys.stderr)
        return 1
    print(f"Structure valid for {len(catalog['criteria'])} catalog criteria; evidence not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
