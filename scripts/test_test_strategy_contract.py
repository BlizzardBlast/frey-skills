#!/usr/bin/env python3
"""Regression tests for test-strategy structure and plugin discovery."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

import yaml


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
        self.assertNotIn("evaluation-playbook", SKILL_FILE.read_text(encoding="utf-8"))

    def test_skill_keeps_modes_statuses_and_read_only_boundary(self) -> None:
        content = SKILL_FILE.read_text(encoding="utf-8")
        for mode in (
            "change test strategy",
            "regression test strategy",
            "migration test strategy",
            "release test strategy",
        ):
            self.assertIn(f"`{mode}`", content)
        for value in ("COMPLETE", "PARTIAL", "BLOCKED", "READY", "READY_WITH_GAPS", "NOT_READY"):
            self.assertIn(f"`{value}`", content)
        self.assertIn("This skill is read-only", content)
        self.assertIn("A test strategy alone does not satisfy the executable-plan gate", content)
        self.assertIn("Never use `READY` with `PARTIAL` or `BLOCKED`", content)

    def test_agent_metadata_uses_boolean_policy_and_skill_prompt(self) -> None:
        data = yaml.safe_load(AGENT_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data["interface"]["display_name"], "Test Strategy")
        self.assertIn("$test-strategy", data["interface"]["default_prompt"])
        self.assertIs(data["policy"]["allow_implicit_invocation"], True)

    def test_manifest_keeps_test_strategy_discovery_contract(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.5.0")
        self.assertIn("test-strategy", manifest["keywords"])
        self.assertIn("risk-based-testing", manifest["keywords"])
        self.assertTrue(any("$test-strategy" in prompt for prompt in manifest["interface"]["defaultPrompt"]))

    def test_validator_rejects_missing_test_strategy_keyword(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["keywords"].remove("test-strategy")
        validator = load_module(VALIDATOR_PATH, "validate_plugin_bundle_test_strategy_contract")
        errors: list[str] = []
        validator.validate_manifest(manifest, errors)
        self.assertTrue(
            any("test-strategy" in error and "missing discovery keywords" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
