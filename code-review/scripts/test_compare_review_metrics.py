"""Offline regression tests for opt-in aggregate comparison."""

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("compare_review_metrics.py")
SPEC = importlib.util.spec_from_file_location("review_metrics", MODULE)
assert SPEC is not None and SPEC.loader is not None
review_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review_metrics)


def run(task, arm, **overrides):
    record = {
        "task_id": task, "arm": arm, "outcome_passed": True,
        "input_tokens": 100, "cached_input_tokens": 20,
        "output_tokens": 40, "tool_calls": 10, "repeated_reads": 4,
        "elapsed_seconds": 60, "ci_seconds": 15,
        "confirmed_findings": 2, "invalid_findings": 0, "missed_critical": 0,
    }
    record.update(overrides)
    return record


class ComparisonTests(unittest.TestCase):
    def test_good_candidate_needs_minimum_sample(self):
        pairs = [(run(str(i), "baseline"), run(str(i), "candidate", input_tokens=60)) for i in range(4)]
        self.assertEqual(review_metrics.compare(pairs)["status"], "insufficient_sample")
        pairs.append((run("last", "baseline"), run("last", "candidate", input_tokens=60)))
        result = review_metrics.compare(pairs)
        self.assertEqual(result["status"], "promising_not_certified")
        self.assertEqual(result["reductions_percent"]["input_tokens"], 40.0)

    def test_quality_regressions_block_promotion(self):
        for change, flag in (
            ({"missed_critical": 1}, "new_critical_misses"),
            ({"outcome_passed": False}, "worse_task_outcomes"),
            ({"confirmed_findings": 1}, "fewer_verified_findings"),
            ({"invalid_findings": 1}, "more_invalid_findings"),
        ):
            with self.subTest(flag=flag):
                pairs = [(run(str(i), "baseline"), run(str(i), "candidate", ci_seconds=0)) for i in range(5)]
                pairs[0][1].update(change)
                result = review_metrics.compare(pairs)
                self.assertEqual(result["status"], "quality_concern")
                self.assertEqual(result["quality_flags"][flag], 1)

    def test_ci_tool_and_read_savings_count_as_efficiency_gains(self):
        for field in ("ci_seconds", "tool_calls", "repeated_reads"):
            with self.subTest(field=field):
                pairs = [(run(str(i), "baseline"), run(str(i), "candidate", **{field: 0})) for i in range(5)]
                result = review_metrics.compare(pairs)
                self.assertEqual(result["status"], "promising_not_certified")
                self.assertEqual(result["reductions_percent"][field], 100.0)
                self.assertFalse(any(result["quality_flags"].values()))
                self.assertEqual(review_metrics.compare(pairs[:4])["status"], "insufficient_sample")

    def test_unchanged_or_worse_efficiency_is_not_a_gain(self):
        for changes in ({}, {"ci_seconds": 30}, {"tool_calls": 20}, {"repeated_reads": 8}):
            with self.subTest(changes=changes):
                pairs = [(run(str(i), "baseline"), run(str(i), "candidate", **changes)) for i in range(5)]
                self.assertEqual(review_metrics.compare(pairs)["status"], "no_observed_efficiency_gain")

    def test_counter_limits_apply_to_every_field(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            for field in review_metrics.FIELDS:
                for value in (2**63, 10**400):
                    with self.subTest(field=field, value=value):
                        path.write_text(json.dumps({"version": 1, "runs": [
                            run("task", "baseline", **{field: value}), run("task", "candidate"),
                        ]}), encoding="utf-8")
                        with self.assertRaises(review_metrics.InvalidMetrics):
                            review_metrics.load_pairs(path)

    def test_cli_accepts_counter_boundaries_and_rejects_overflow_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            for value in (0, 2**63 - 1, 2**63, 10**400):
                with self.subTest(value=value):
                    path.write_text(json.dumps({"version": 1, "runs": [
                        run("task", "baseline"),
                        run("task", "candidate", **dict.fromkeys(review_metrics.FIELDS, value)),
                    ]}), encoding="utf-8")
                    result = subprocess.run(
                        [sys.executable, "-B", str(MODULE), "--input", str(path)],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertNotIn("Traceback", result.stderr)
                    if value <= 2**63 - 1:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        for reduction in json.loads(result.stdout)["reductions_percent"].values():
                            self.assertTrue(reduction is None or math.isfinite(reduction))
                    else:
                        self.assertEqual(result.returncode, 2)
                        self.assertIn("Invalid aggregate metrics:", result.stderr)
                        self.assertEqual(result.stdout, "")

    def test_strict_schema_rejects_sensitive_or_fake_fields(self):
        for extra in ({"raw_prompt": "secret"}, {"outcome_passed": 1}, {"input_tokens": -1}):
            record = run("task", "baseline", **extra)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "metrics.json"
                path.write_text(json.dumps({"version": 1, "runs": [record, run("task", "candidate")]}))
                with self.assertRaises(review_metrics.InvalidMetrics):
                    review_metrics.load_pairs(path)

    def test_unpaired_duplicate_and_oversize_rejected(self):
        for runs in ([run("a", "baseline")], [run("a", "baseline"), run("a", "baseline")]):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "metrics.json"
                path.write_text(json.dumps({"version": 1, "runs": runs}))
                with self.assertRaises(review_metrics.InvalidMetrics):
                    review_metrics.load_pairs(path)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            path.write_bytes(b"x" * (review_metrics.MAX_BYTES + 1))
            with self.assertRaises(review_metrics.InvalidMetrics):
                review_metrics.load_pairs(path)


if __name__ == "__main__":
    unittest.main()
