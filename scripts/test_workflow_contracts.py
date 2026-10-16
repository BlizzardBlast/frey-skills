#!/usr/bin/env python3
"""Deterministic checks of CI coverage and version-tag publication boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def read_workflow(self, name: str) -> dict:
        return yaml.load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    def test_windows_runs_all_gates_with_read_only_ci_permissions(self) -> None:
        ci = self.read_workflow("ci.yml")
        self.assertEqual(ci["permissions"], {"contents": "read"})
        windows = ci["jobs"]["windows"]
        self.assertEqual(windows["runs-on"], "windows-latest")
        commands = [step["run"] for step in windows["steps"] if "run" in step]
        self.assertIn("python scripts/check.py --base origin/main", commands)
        self.assertTrue(any("requirements-dev.txt" in command and "requirements-spec.txt" in command for command in commands))
        self.assertNotIn("permissions", windows)

    def test_publication_runs_only_on_version_tags_after_validation(self) -> None:
        workflow = self.read_workflow("release.yml")
        self.assertEqual(workflow["on"], {"push": {"tags": ["v*"]}})
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        publish = workflow["jobs"]["publish"]
        self.assertEqual(publish["needs"], "windows")
        windows = workflow["jobs"]["windows"]
        self.assertEqual(windows["runs-on"], "windows-latest")
        self.assertNotIn("permissions", windows)
        self.assertIn("python scripts/check.py --base origin/main", [step.get("run", "") for step in windows["steps"]])
        self.assertEqual(publish["permissions"], {"contents": "write"})
        steps = publish["steps"]
        commands = [step.get("run", "") for step in steps]
        main_check = next(i for i, command in enumerate(commands) if "git merge-base --is-ancestor HEAD origin/main" in command)
        checks = commands.index("python scripts/check.py --base origin/main")
        prepare = next(i for i, command in enumerate(commands) if "scripts/prepare_release.py" in command)
        write = next(i for i, command in enumerate(commands) if "gh release create" in command)
        self.assertLess(main_check, checks)
        self.assertLess(checks, prepare)
        self.assertLess(prepare, write)
        self.assertIn("--verify-tag", commands[write])
        self.assertIn("--notes-file dist/releases/notes.md", commands[write])
        self.assertEqual(steps[prepare]["env"]["RELEASE_TAG"], "${{ github.ref_name }}")
        self.assertEqual(steps[write]["env"]["GH_TOKEN"], "${{ github.token }}")
        for i, step in enumerate(steps):
            if i != write:
                self.assertNotIn("GH_TOKEN", step.get("env", {}))
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")


if __name__ == "__main__":
    unittest.main()
