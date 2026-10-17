#!/usr/bin/env python3
"""Deterministic checks of CI coverage and version-tag publication boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from scripts import smoke_install, smoke_release


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def read_workflow(self, name: str) -> dict:
        return yaml.load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    def test_windows_and_macos_run_all_gates_with_read_only_ci_permissions(self) -> None:
        ci = self.read_workflow("ci.yml")
        self.assertEqual(ci["permissions"], {"contents": "read"})
        for platform in ("windows", "macos"):
            with self.subTest(platform=platform):
                job = ci["jobs"][platform]
                self.assertEqual(job["runs-on"], f"{platform}-latest")
                self.assertNotIn("permissions", job)
                commands = [step["run"] for step in job["steps"] if "run" in step]
                self.assertIn("python scripts/check.py --base origin/main", commands)
                self.assertTrue(any("requirements-dev.txt" in command and "requirements-spec.txt" in command for command in commands))
                checkout = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/checkout@"))
                self.assertEqual(checkout["with"]["fetch-depth"], "0")
                python_setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
                self.assertEqual(python_setup["with"]["python-version"], "3.12")

    def test_installation_covers_all_platforms_with_a_pinned_cli_and_no_credentials(self) -> None:
        ci = self.read_workflow("ci.yml")
        installation = ci["jobs"]["installation"]
        self.assertEqual(installation["runs-on"], "${{ matrix.os }}")
        self.assertEqual(set(installation["strategy"]["matrix"]["os"]), {"ubuntu-latest", "windows-latest", "macos-latest"})
        self.assertNotIn("permissions", installation)
        self.assertEqual(installation["timeout-minutes"], "15")
        steps = installation["steps"]
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        node_setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-node@"))
        self.assertEqual(node_setup["with"]["node-version"], "24")
        commands = [step["run"] for step in steps if "run" in step]
        self.assertEqual(len(commands), 3)
        self.assertIn(f"skills@{smoke_install.CLI_VERSION}", commands[0])
        self.assertIn("--ignore-scripts", commands[0])
        self.assertEqual(commands[1], 'python scripts/smoke_install.py --cli "${{ runner.temp }}/frey-smoke-cli/node_modules/skills/bin/cli.mjs"')
        self.assertEqual(commands[2], "python scripts/smoke_release.py")

    def test_installation_guide_matches_the_smoke_test_pins(self) -> None:
        guide = (ROOT / "docs" / "installation.md").read_text(encoding="utf-8")
        self.assertIn(f"npx skills@{smoke_install.CLI_VERSION}", guide)
        self.assertIn(f"npx skills add {smoke_install.SOURCE_URL} --list", guide)
        self.assertIn(f"npx skills add {smoke_install.SOURCE_URL} --skill code-review --agent codex", guide)
        self.assertIn(f"{smoke_release.ARCHIVE_NAME}", guide)
        self.assertIn(f"{smoke_release.RELEASE_URL.rsplit('/download/', 1)[0]}/tag/{smoke_install.SOURCE_TAG}", guide)

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
