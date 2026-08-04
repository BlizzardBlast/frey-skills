#!/usr/bin/env python3
"""Regression tests for implementation-execution packaging and eval fixtures."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json"
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"
FIXTURE_SETUP = REPOSITORY_ROOT / "implementation-execution" / "evals" / "fixtures" / "setup_repository.py"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImplementationExecutionContractTests(unittest.TestCase):
    def test_manifest_keeps_execution_discovery_contract(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertIn("implementation-execution", manifest["keywords"])
        self.assertIn("plan-execution", manifest["keywords"])
        self.assertIn(
            "Execute this approved plan with $implementation-execution.",
            manifest["interface"]["defaultPrompt"],
        )

        validator = load_module(VALIDATOR_PATH, "validate_plugin_bundle_contract")
        self.assertIn("implementation-execution", validator.REQUIRED_KEYWORDS)

    def test_disposable_repository_setup_is_deterministic(self) -> None:
        cases = (
            "complete-plan-execution",
            "partial-implementation-continuation",
            "material-plan-drift",
            "unrelated-dirty-work",
            "generated-source-ownership",
            "verification-failure",
            "dirty-plan-owned-work",
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for case in cases:
                with self.subTest(case=case):
                    destination = root / case
                    subprocess.run(
                        ["python", str(FIXTURE_SETUP), case, str(destination)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    self.assertTrue((destination / ".git").is_dir())
                    status = subprocess.run(
                        ["git", "status", "--short"],
                        cwd=destination,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                    if case in {"unrelated-dirty-work", "dirty-plan-owned-work"}:
                        self.assertTrue(status.strip())
                    else:
                        self.assertEqual(status, "")

    def test_dirty_fixture_preserves_same_file_user_hunk(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "repo"
            subprocess.run(
                ["python", str(FIXTURE_SETUP), "dirty-plan-owned-work", str(destination)],
                check=True,
                capture_output=True,
                text=True,
            )
            profile = (destination / "src" / "profile.ts").read_text(encoding="utf-8")
            self.assertIn("// unrelated user hunk", profile)


if __name__ == "__main__":
    unittest.main()
