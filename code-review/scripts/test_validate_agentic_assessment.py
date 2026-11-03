"""Synthetic structural tests; no model, live repo, or AWS calls."""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_agentic_assessment.py")
SPEC = importlib.util.spec_from_file_location("validate_agentic_assessment", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class AgenticAssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = module.read_json(module.CATALOG)
        cls.ids = module.validate_catalog(cls.catalog)

    def report(self):
        return {
            "schema_version": 1,
            "catalog_version": self.catalog["catalog_version"],
            "scope": "synthetic repository @ fixed commit: no runtime access",
            "assessments": {
                criterion_id: {
                    "status": "not_reviewed", "evidence": [],
                    "reason": "source evidence unavailable", "gap": "", "remediation": "",
                }
                for criterion_id in self.ids
            },
        }

    def test_catalog_has_unique_nonempty_original_criteria(self):
        self.assertEqual(len(self.ids), 10)
        self.assertEqual(len(self.ids), len(set(self.ids)))
        self.assertTrue(all(i.startswith("AA-") for i in self.ids))

    def test_valid_all_statuses_with_independent_evidence(self):
        report = self.report()
        sample = list(report["assessments"].values())
        sample[0].update(status="compliant", evidence=[{"source": "src/agent.py@abc:10", "observation": "verified policy guard"}], reason="")
        sample[1].update(status="partially_compliant", evidence=[{"source": "tests/test_guard.py@abc:20", "observation": "only happy path covered"}], reason="", gap="missing negative case", remediation="add negative test")
        sample[2].update(status="non_compliant", evidence=[{"source": "src/tools.py@abc:42", "observation": "tool executes without permission check"}], reason="", gap="missing authz", remediation="enforce per-call authz")
        sample[3].update(status="not_applicable", reason="no durable state in this stateless workload")
        module.validate_assessment(report, self.catalog)

    def test_missing_extra_and_unknown_status_fail(self):
        for mutation in (
            lambda r: r["assessments"].pop(self.ids[0]),
            lambda r: r["assessments"].update({"AA-UNKNOWN-999": r["assessments"][self.ids[0]]}),
            lambda r: r["assessments"][self.ids[0]].update(status="unknown"),
            lambda r: r.update(catalog_version="wrong"),
            lambda r: r.update(scope="  "),
        ):
            report = self.report()
            mutation(report)
            with self.subTest(mutation=mutation), self.assertRaises(module.AssessmentError):
                module.validate_assessment(report, self.catalog)

    def test_unsubstantiated_definitive_findings_fail(self):
        for status in ("compliant", "partially_compliant", "non_compliant"):
            report = self.report()
            report["assessments"][self.ids[0]].update(status=status, reason="")
            with self.subTest(status=status), self.assertRaises(module.AssessmentError):
                module.validate_assessment(report, self.catalog)

    def test_non_reviewed_and_not_applicable_need_reason(self):
        for status in ("not_reviewed", "not_applicable"):
            report = self.report()
            report["assessments"][self.ids[0]].update(status=status, reason="")
            with self.subTest(status=status), self.assertRaises(module.AssessmentError):
                module.validate_assessment(report, self.catalog)

    def test_missing_gap_or_remediation_fails(self):
        report = self.report()
        report["assessments"][self.ids[0]].update(status="non_compliant", reason="", evidence=[{"source": "file:1", "observation": "missing boundary"}], gap="missing authorization")
        with self.assertRaises(module.AssessmentError):
            module.validate_assessment(report, self.catalog)

    def test_blank_or_malformed_evidence_fails(self):
        report = self.report()
        report["assessments"][self.ids[0]].update(status="compliant", reason="", evidence=[{"source": "file:1", "observation": "   "}])
        with self.assertRaises(module.AssessmentError):
            module.validate_assessment(report, self.catalog)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "duplicate.json"
            file.write_text('{"status":"compliant","status":"not_reviewed"}', encoding="utf-8")
            with self.assertRaises(module.AssessmentError):
                module.read_json(file)

    def test_duplicate_catalog_criteria_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["criteria"].append(copy.deepcopy(catalog["criteria"][0]))
        with self.assertRaises(module.AssessmentError):
            module.validate_catalog(catalog)

    def test_bounded_input_size(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "huge.json"
            file.write_bytes(b"x" * (module.MAX_BYTES + 1))
            with self.assertRaises(module.AssessmentError):
                module.read_json(file)


if __name__ == "__main__":
    unittest.main()
