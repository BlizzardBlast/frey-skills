#!/usr/bin/env python3
"""Check published performance-investigation instructions, not model behavior."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts import check


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CASES = {
    "PERF-CASE-001": ("Useful measurements come from materially different hardware or workloads and no causal explanation is favored", "PARTIAL", "UNRESOLVED"),
    "PERF-CASE-002": ("Comparable results and discriminating trace evidence establish the causal chain and resolve material alternatives", "COMPLETE", "CONFIRMED"),
    "PERF-CASE-003": ("Noisy samples reach the declared budget without distinguishing plausible causes", "PARTIAL", "UNRESOLVED"),
    "PERF-CASE-004": ("A baseline is missing but safe evidence favors one cause with material confirmation outstanding", "PARTIAL", "LIKELY"),
    "PERF-CASE-005": ("Lower aggregate latency coincides with more fast failures and no causal explanation is established", "PARTIAL", "UNRESOLVED"),
    "PERF-CASE-006": ("Diagnosis necessarily depends on an unauthorized benchmark or unsafe access even though safe fragments exist", "BLOCKED", "UNRESOLVED"),
    "PERF-CASE-007": ("A declared resource limit is reached while one cause is favored but not materially confirmed", "PARTIAL", "LIKELY"),
    "PERF-CASE-008": ("A hotspot is observed without evidence connecting it to the symptom or favoring a cause", "PARTIAL", "UNRESOLVED"),
    "PERF-CASE-009": ("The symptom and handling demonstrably meet applicable performance contracts and material alternatives are resolved", "COMPLETE", "NOT_A_DEFECT"),
    "PERF-CASE-010": ("Useful safe evidence exists but a saved report's speedup claim lacks matching measurement provenance", "PARTIAL", "UNRESOLVED"),
}


class DebugPerformanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (ROOT / "debug" / "SKILL.md").read_text(encoding="utf-8")
        cls.rules = (ROOT / "debug" / "references" / "performance-investigation.md").read_text(encoding="utf-8")
        cls.normalized = " ".join(cls.rules.split())

    def test_extension_uses_existing_modes_and_a_conditional_resource_route(self) -> None:
        boundary = self.skill.split("## Boundary and routing\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(set(re.findall(r"(?m)^- `([^`]+)`$", boundary)), {
            "failure investigation", "regression investigation", "flaky investigation", "production investigation",
        })
        workflow = self.skill.split("## Workflow\n", 1)[1].split("\n## ", 1)[0]
        route = next(line for line in workflow.splitlines() if "references/performance-investigation.md" in line)
        self.assertIn("For latency, throughput, CPU, memory, or I/O symptoms", route)
        self.assertIn("before selecting diagnostics", route)
        self.assertIn("Mark proposed checks `NOT_RUN`", self.skill)
        self.assertIn("same completeness and root-cause rules", self.skill)
        self.assertIn("Standalone benchmark execution, optimization implementation, and incident retrospectives", boundary)

    def test_measurement_ledger_preserves_context_and_comparison_fields(self) -> None:
        ledger = self.rules.split("## Conditional measurement ledger\n", 1)[1].split("\n## ", 1)[0]
        fields = {row.split("|")[1].strip() for row in ledger.splitlines() if row.startswith("|")}
        self.assertTrue({
            "Identity", "Snapshot", "Workload", "Environment", "Metric", "Sampling",
            "Cache and warmup", "Outcomes and resources", "Provenance and execution", "Comparison",
        }.issubset(fields))
        for contract in (
            "offered load versus completed work", "wall-clock versus CPU time",
            "observed spread/noise", "profiler/measurement overhead", "cache/JIT/connection state",
            "A proposed measurement has execution status `NOT_RUN` and no observed result",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, " ".join(ledger.split()))

    def test_comparison_does_not_turn_lower_timings_into_causal_proof(self) -> None:
        for contract in (
            "material mismatch or unknown prevents a quantitative speedup/regression claim",
            "successful and failed operation timings separately",
            "Do not average percentiles across windows",
            "Do not invent statistical confidence",
            "A missing baseline prevents a relative improvement claim",
            "Numeric differences, correlation, high utilization, or a hotspot alone do not establish the causal chain",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.normalized)

    def test_checks_require_authority_finite_budgets_and_honest_stopping(self) -> None:
        for field in ("Question and prediction", "Scope and authority", "Finite budget", "Stop and recovery"):
            self.assertIn(f"`{field}`", self.rules)
        for contract in (
            "why execution is already authorized", "maximum samples/repetitions, duration, concurrency/load",
            "never extend the budget automatically", "A proposal without safe finite bounds remains `NOT_RUN`",
            "Do not install profilers, generate production load, flush shared caches, restart services, retrieve credentials, escalate privileges, or perform external writes",
            "Summarize sensitive evidence instead of copying raw traces",
            "saved report cannot validate its own claim", "Unclear effects block that check",
            "return `BLOCKED` and `UNRESOLVED`",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.normalized)

    def assert_case_contract(self, text: str) -> None:
        cases = {}
        for row in text.splitlines():
            if not row.startswith("| PERF-CASE-"):
                continue
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 4)
            case, condition, completeness, result = cells
            self.assertNotIn(case, cases)
            cases[case] = (" ".join(condition.split()), completeness, result)
        self.assertEqual(cases, EXPECTED_CASES)

    def test_decision_cases_bind_conditions_to_completeness_and_result(self) -> None:
        self.assert_case_contract(self.rules)

    def test_case_contract_rejects_missing_duplicate_or_reclassified_cases(self) -> None:
        rows = [row for row in self.rules.splitlines() if row.startswith("| PERF-CASE-")]
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            for field in (1, 2, 3):
                changed = cells.copy()
                changed[field] = "changed-condition" if field == 1 else "invalid-status"
                replacement = "| " + " | ".join(changed) + " |"
                with self.subTest(case=cells[0], field=field), self.assertRaises(AssertionError):
                    self.assert_case_contract(self.rules.replace(row, replacement, 1))
            with self.subTest(missing=cells[0]), self.assertRaises(AssertionError):
                self.assert_case_contract(self.rules.replace(row, "", 1))
            with self.subTest(duplicate=cells[0]), self.assertRaises(AssertionError):
                self.assert_case_contract(self.rules + "\n" + row)

    def test_synthetic_fast_error_illustration_has_consistent_arithmetic_and_limits(self) -> None:
        example = self.rules.split("## Arithmetic illustration: fast errors\n", 1)[1]
        batches = []
        for row in example.splitlines():
            if not row.startswith(("| Baseline illustration", "| Current illustration")):
                continue
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            successes, success_mean, errors, error_mean, mean = map(float, cells[1:])
            self.assertEqual(successes + errors, 100)
            self.assertAlmostEqual(mean, (successes * success_mean + errors * error_mean) / 100)
            batches.append((successes, success_mean, errors, mean))
        self.assertEqual(len(batches), 2)
        self.assertLess(batches[1][3], batches[0][3])
        self.assertGreater(batches[1][1], batches[0][1])
        self.assertGreater(batches[1][2], batches[0][2])
        for contract in (
            "not an actual measurement", "Do not claim a speedup", "not the cause of the failures",
            "`PARTIAL` and `UNRESOLVED`", "`NOT_RUN`",
        ):
            self.assertIn(contract, example)

    def test_contract_is_registered_and_specialist_dispositions_are_documented(self) -> None:
        self.assertIn("scripts.test_debug_performance_contract", check.CONTRACT_TESTS)
        record = (ROOT / "docs" / "specialist-reassessment.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
        for decision in ("M4-PERF-EXTEND", "M4-PERF-DEFER", "M4-RETRO-DEFER"):
            self.assertIn(decision, record)
        self.assertIn("specialist-reassessment.md", roadmap)
        self.assertIn("two sanitized maintainer-reported tasks", record)
        self.assertIn("not evidence of absent demand", record)


if __name__ == "__main__":
    unittest.main()
