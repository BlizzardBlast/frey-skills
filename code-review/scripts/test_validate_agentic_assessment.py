"""Synthetic structural tests; no model, live repo, or AWS calls."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

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
            "schema_version": self.catalog["schema_version"],
            "catalog_version": self.catalog["catalog_version"],
            "catalog_sha256": module.catalog_sha256(self.catalog),
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

    def test_catalog_content_changes_require_new_digest(self):
        report = self.report()
        for field, replacement in (("question", "A different question?"), ("risk", "low"), ("area", "different")):
            catalog = copy.deepcopy(self.catalog)
            catalog["criteria"][0][field] = replacement
            with self.subTest(field=field), self.assertRaisesRegex(module.AssessmentError, "catalog_sha256"):
                module.validate_assessment(report, catalog)

    def test_catalog_digest_is_canonical_and_required(self):
        report = self.report()
        catalog = {key: self.catalog[key] for key in reversed(self.catalog)}
        self.assertEqual(module.catalog_sha256(catalog), report["catalog_sha256"])
        module.validate_assessment(report, catalog)
        report.pop("catalog_sha256")
        with self.assertRaises(module.AssessmentError):
            module.validate_assessment(report, self.catalog)

    def test_file_identity_changes_without_no_follow(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            replacement = Path(directory) / "replacement.json"
            source.write_text('{"value":1}', encoding="utf-8")
            replacement.write_text('{"value":2}', encoding="utf-8")
            original_open = os.open

            def replace_before_open(path, flags):
                source.unlink()
                replacement.rename(source)
                return original_open(path, flags)

            # Simulate Windows (no O_NOFOLLOW). Both files are regular and the
            # same size, so only opened-file identity detects the replacement.
            with mock.patch.object(module.os, "O_NOFOLLOW", 0, create=True):
                with mock.patch.object(module.os, "open", side_effect=replace_before_open):
                    with self.assertRaisesRegex(module.AssessmentError, "input changed"):
                        module.read_json(source)

    def test_file_identity_unavailable_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            source.write_text("{}", encoding="utf-8")
            previous = source.stat()
            with mock.patch.object(module.os, "fstat", return_value=SimpleNamespace(
                st_mode=previous.st_mode, st_size=previous.st_size,
                st_dev=previous.st_dev, st_ino=0,
            )):
                with self.assertRaisesRegex(module.AssessmentError, "identity unavailable"):
                    module.read_json(source)

    def test_cli_prints_current_digest(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--print-catalog-sha256"],
            capture_output=True, text=True, check=False, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), module.catalog_sha256(self.catalog))

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


    def test_uncertain_and_inapplicable_preserve_inspected_evidence(self):
        for status in ("not_reviewed", "not_applicable"):
            report = self.report()
            report["assessments"][self.ids[0]].update(
                status=status,
                reason="Deployment proof unavailable" if status == "not_reviewed" else "No tools are configured",
                evidence=[{"source": "src/agent.py@abc:12", "observation": "Reviewed local configuration"}],
            )
            with self.subTest(status=status):
                module.validate_assessment(report, self.catalog)

    def test_uncertain_evidence_without_reason_is_invalid(self):
        report = self.report()
        report["assessments"][self.ids[0]].update(
            status="not_reviewed", reason="",
            evidence=[{"source": "src/agent.py@abc:12", "observation": "Reviewed local configuration"}],
        )
        with self.assertRaises(module.AssessmentError):
            module.validate_assessment(report, self.catalog)

    def test_nonregular_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(module.AssessmentError):
                module.read_json(Path(directory))
            if hasattr(os, "mkfifo"):
                fifo = Path(directory) / "source.fifo"
                os.mkfifo(fifo)
                with self.assertRaises(module.AssessmentError):
                    module.read_json(fifo)

    def test_actual_read_limit_catches_stale_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "expanded.json"
            file.write_bytes(b"x" * (module.MAX_BYTES + 1))
            identity = file.stat()
            with mock.patch.object(module.os, "fstat", return_value=SimpleNamespace(
                st_mode=stat.S_IFREG, st_size=0,
                st_dev=identity.st_dev, st_ino=identity.st_ino,
            )):
                with self.assertRaisesRegex(module.AssessmentError, "size limit"):
                    module.read_json(file)

    def test_rejects_control_characters_in_untrusted_diagnostics(self):
        secret_key = "HIDDEN_SECRET\n\x1b[31m"
        with self.assertRaises(module.AssessmentError) as duplicate:
            module.unique_object([(secret_key, 1), (secret_key, 2)])
        self.assertNotIn("HIDDEN_SECRET", str(duplicate.exception))
        self.assertNotIn("\x1b", str(duplicate.exception))

        report = self.report()
        report["assessments"][secret_key] = report["assessments"][self.ids[0]]
        with self.assertRaises(module.AssessmentError) as unexpected:
            module.validate_assessment(report, self.catalog)
        self.assertNotIn("HIDDEN_SECRET", str(unexpected.exception))
        self.assertNotIn("\x1b", str(unexpected.exception))

    def test_cli_from_simulated_installed_skill_outside_source_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_root = root / "plugin with spaces" / "skills" / "code-review"
            scripts_dir = skill_root / "scripts"
            references_dir = skill_root / "references"
            scripts_dir.mkdir(parents=True)
            references_dir.mkdir()
            installed_script = scripts_dir / SCRIPT.name
            shutil.copy2(SCRIPT, installed_script)
            shutil.copy2(module.CATALOG, references_dir / module.CATALOG.name)
            consumer = root / "unrelated consumer"
            consumer.mkdir()
            (consumer / "assessment.json").write_text(json.dumps(self.report()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(installed_script), "assessment.json"],
                cwd=consumer, capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Structure valid", result.stdout)

    def test_json_parser_value_error_becomes_assessment_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unexpected-number.json"
            path.write_text("{}", encoding="utf-8")
            with mock.patch.object(module.json, "loads", side_effect=ValueError("unexpected numeric conversion")):
                with self.assertRaisesRegex(module.AssessmentError, "invalid numeric value"):
                    module.read_json(path)

    def test_oversized_json_integer_has_controlled_cli_error(self):
        if not hasattr(sys, "get_int_max_str_digits") or sys.get_int_max_str_digits() == 0:
            self.skipTest("Python integer digit restriction is unavailable or disabled")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized-number.json"
            path.write_text('{"value":' + ("9" * 10000) + "}", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Invalid agentic assessment: cannot read valid JSON:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertNotIn("ValueError", result.stderr)

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
