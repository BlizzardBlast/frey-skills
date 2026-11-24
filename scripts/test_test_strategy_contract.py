#!/usr/bin/env python3
"""Regression tests for test-strategy structure and plugin discovery."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "test-strategy"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
AGENT_FILE = SKILL_ROOT / "agents" / "openai.yaml"
MANIFEST_PATH = REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json"
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"


EXPECTED_GIT_CASES = {
    "GIT-CASE-001": (
        "Changed behavior neither reads nor writes Git refs and does not rely on Git "
        "history as application state",
        "Use ordinary risk selection; do not add Git-specific scenarios",
    ),
    "GIT-CASE-002": (
        "Two agents target one ref",
        "A stale expected-OID update is rejected and earlier committed work survives",
    ),
    "GIT-CASE-003": (
        "Independent refs change during a multi-ref read",
        "Check documented consistency needs; do not assume a repository-wide snapshot",
    ),
    "GIT-CASE-004": (
        "Publication acknowledgment is lost",
        "Reconcile the intended ref/commit; an unresolved outcome must not prompt blind retry",
    ),
    "GIT-CASE-005": (
        "A new ref is acknowledged before a reader fetches",
        "Verify the intended tip and reachable objects from an independent reader",
    ),
    "GIT-CASE-006": (
        "A read-only consumer combines refs that can advance independently",
        "Test required cross-ref consistency and read-time interleavings even without "
        "writes by the consumer",
    ),
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestStrategyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_content = SKILL_FILE.read_text(encoding="utf-8")

    def test_skill_structure_and_intentional_no_evals_contract(self) -> None:
        self.assertTrue(SKILL_FILE.is_file())
        self.assertTrue(AGENT_FILE.is_file())
        for reference in (
            "repository-testing-profiles.md",
            "risk-and-scenario-rules.md",
            "strategy-quality-checklist.md",
        ):
            self.assertTrue((SKILL_ROOT / "references" / reference).is_file())
        self.assertFalse((SKILL_ROOT / "evals").exists())
        self.assertNotIn("evaluation-playbook", self.skill_content)

    def test_skill_keeps_modes_statuses_and_read_only_boundary(self) -> None:
        for mode in (
            "change test strategy",
            "regression test strategy",
            "migration test strategy",
            "release test strategy",
        ):
            self.assertIn(f"`{mode}`", self.skill_content)
        for value in (
            "COMPLETE",
            "PARTIAL",
            "BLOCKED",
            "READY",
            "READY_WITH_GAPS",
            "NOT_READY",
        ):
            self.assertIn(f"`{value}`", self.skill_content)
        self.assertIn("This skill is read-only", self.skill_content)
        self.assertIn("Never use `READY` with `PARTIAL` or `BLOCKED`", self.skill_content)

    def test_skill_keeps_activation_and_routing_boundaries(self) -> None:
        for boundary in (
            "Implementing tests or production code",
            "Running tests or verification commands as the primary task",
            "Debugging an unknown root cause",
            "Creating a general implementation plan",
            "Reviewing a diff or deciding merge readiness",
            "General release readiness beyond testing concerns",
        ):
            self.assertIn(boundary, self.skill_content)
        self.assertIn(
            "A test strategy alone does not satisfy the executable-plan gate",
            self.skill_content,
        )
        self.assertIn(
            "this skill does not decide merge readiness",
            self.skill_content,
        )

    def test_skill_keeps_risk_and_scenario_traceability_contracts(self) -> None:
        for field in (
            "Behavior or boundary",
            "Failure mode",
            "Impact",
            "Likelihood",
            "Change exposure",
            "Detectability",
            "Recovery",
            "Priority",
            "Evidence",
            "Planned coverage",
        ):
            self.assertIn(f"`{field}`", self.skill_content)
        for field in (
            "Covered risks",
            "Contract or behavior",
            "Preconditions",
            "Test data",
            "Action",
            "Expected result",
            "Test layer",
            "Environment",
            "Automation status",
            "Priority",
            "Evidence or gap",
        ):
            self.assertIn(f"`{field}`", self.skill_content)
        self.assertIn(
            "Material risks and observable contracts are traceable to prioritized scenarios",
            self.skill_content,
        )

    def test_skill_keeps_output_and_completion_contracts(self) -> None:
        for section in (
            "Scope mode",
            "Test objective and scope",
            "Risk matrix",
            "Behavior and contract inventory",
            "Test-layer allocation",
            "Scenario catalogue",
            "Test data and environment requirements",
            "Automation candidates",
            "Execution order",
            "Entry and exit criteria",
            "Residual risk",
            "Strategy completeness: COMPLETE|PARTIAL|BLOCKED",
            "Test readiness: READY|READY_WITH_GAPS|NOT_READY",
        ):
            self.assertIn(f"`{section}`", self.skill_content)
        self.assertIn("No repository or external-system mutation was performed", self.skill_content)
        self.assertIn("Missing context and blocked checks are honest", self.skill_content)

    def assert_git_case_contract(self, profile: str) -> None:
        marker = "## Git-backed published state and concurrent agents (conditional)\n"
        self.assertEqual(profile.count(marker), 1)
        section = profile.split(marker, 1)[1].split("\n## ", 1)[0]
        rows = [row for row in section.splitlines() if row.startswith("|")]
        self.assertEqual(
            rows[:2],
            [
                "| Case | Condition | Observable test-strategy decision |",
                "| --- | --- | --- |",
            ],
        )
        cases: dict[str, tuple[str, str]] = {}
        for row in rows[2:]:
            self.assertTrue(row.startswith("| ") and row.endswith(" |"), row)
            cells = [" ".join(cell.split()) for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 3, row)
            case, condition, decision = cells
            self.assertRegex(case, r"^`GIT-CASE-\d{3}`$")
            case_id = case.strip("`")
            self.assertNotIn(case_id, cases)
            cases[case_id] = (condition, decision)
        self.assertEqual(cases, EXPECTED_GIT_CASES)

    def test_git_ref_consistency_profile_is_conditional_and_traceable(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Git-backed published state and concurrent agents (conditional)", profile)
        for boundary in (
            "only** when the changed system actually publishes",
            "Do not assume all Git servers provide Pando's consistency model",
            "This applies to read-only consumers as well as publishers",
            "a failed subprocess acknowledgment is not proof",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary.casefold(), profile.casefold())
        self.assert_git_case_contract(profile)

    def test_git_case_contract_rejects_missing_duplicate_and_modified_cases(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        rows = [row for row in profile.splitlines() if row.startswith("| `GIT-CASE-")]
        self.assertEqual(len(rows), len(EXPECTED_GIT_CASES))
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            for index in (1, 2):
                changed = cells.copy()
                changed[index] = "Different condition" if index == 1 else "Unsafe decision"
                replacement = "| " + " | ".join(changed) + " |"
                with self.subTest(case=cells[0], field=index), self.assertRaises(AssertionError):
                    self.assert_git_case_contract(profile.replace(row, replacement, 1))

            mutations = (
                profile.replace(row, "", 1),
                profile.replace(row, row + "\n" + row, 1),
                profile.replace(row, row[:-2] + " | extra |", 1),
                profile.replace(row, row.replace(cells[0], "`GIT-CASE-999`", 1), 1),
            )
            for index, mutated in enumerate(mutations):
                with self.subTest(case=cells[0], mutation=index), self.assertRaises(
                    AssertionError
                ):
                    self.assert_git_case_contract(mutated)

        same_ref = rows[1]
        contradictory = same_ref.replace(
            "is rejected and earlier committed work survives",
            "is allowed (not rejected) and earlier committed work survives",
        )
        self.assertNotEqual(contradictory, same_ref)
        with self.assertRaises(AssertionError):
            self.assert_git_case_contract(profile.replace(same_ref, contradictory, 1))

    def test_agent_metadata_keeps_discovery_contract(self) -> None:
        content = AGENT_FILE.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^\s*display_name:\s*['\"]?Test Strategy['\"]?\s*$")
        self.assertIn("$test-strategy", content)
        self.assertRegex(content, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        self.assertNotRegex(content, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_manifest_keeps_test_strategy_discovery_contract(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for keyword in ("test-strategy", "risk-based-testing", "testing"):
            self.assertIn(keyword, manifest["keywords"])
        self.assertTrue(
            any("$test-strategy" in prompt for prompt in manifest["interface"]["defaultPrompt"])
        )

    def test_validator_rejects_missing_test_strategy_keywords(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_plugin_bundle_test_strategy_contract")
        original = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for keyword in ("test-strategy", "risk-based-testing", "testing"):
            with self.subTest(keyword=keyword):
                manifest = json.loads(json.dumps(original))
                manifest["keywords"].remove(keyword)
                errors: list[str] = []
                validator.validate_manifest(manifest, errors)
                self.assertTrue(
                    any(keyword in error and "missing discovery keywords" in error for error in errors),
                    errors,
                )


if __name__ == "__main__":
    unittest.main()
