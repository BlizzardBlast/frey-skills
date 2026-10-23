"""Offline regression tests for opt-in aggregate comparison."""

import importlib.util
import json
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
        pairs = [(run(str(i), "baseline"), run(str(i), "candidate", input_tokens=10)) for i in range(5)]
        pairs[0][1]["missed_critical"] = 1
        self.assertEqual(review_metrics.compare(pairs)["status"], "quality_concern")
        self.assertEqual(review_metrics.compare(pairs)["quality_flags"]["new_critical_misses"], 1)

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
