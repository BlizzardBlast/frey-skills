#!/usr/bin/env python3
"""Regression tests for test-strategy structure and plugin discovery."""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "test-strategy"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
AGENT_FILE = SKILL_ROOT / "agents" / "openai.yaml"
MANIFEST_PATH = REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json"
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"


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
