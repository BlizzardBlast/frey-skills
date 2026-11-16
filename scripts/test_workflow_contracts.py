#!/usr/bin/env python3
"""Deterministic checks of CI coverage and version-tag publication boundaries."""

from __future__ import annotations

import re
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from scripts import smoke_codex, smoke_install, smoke_release


ROOT = Path(__file__).resolve().parents[1]

# PR-related events have different permissions and lifecycle semantics.
# Their introduction requires an explicit security and CI-cost policy review.
PR_RELATED_EVENTS = frozenset({
    "pull_request",
    "pull_request_target",
    "pull_request_review",
    "pull_request_review_comment",
    "issue_comment",
})


def pr_related_workflows(directory: Path) -> dict[str, set[str]]:
    """Inventory PR-related workflow triggers; exempt release-only workflows."""
    discovered: dict[str, set[str]] = {}
    paths = sorted((*directory.glob("*.yml"), *directory.glob("*.yaml")))
    for path in paths:
        workflow = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if not isinstance(workflow, dict):
            raise ValueError(f"Invalid workflow document: {path.name}")
        triggers = workflow.get("on")
        if isinstance(triggers, dict):
            event_names = set(triggers)
        elif isinstance(triggers, list):
            event_names = set(triggers)
        elif isinstance(triggers, str):
            event_names = {triggers}
        else:
            raise ValueError(f"Unsupported event declaration: {path.name}")
        relevant = event_names & PR_RELATED_EVENTS
        if relevant:
            discovered[path.name] = relevant
    return discovered


class WorkflowContractTests(unittest.TestCase):
    def read_workflow(self, name: str) -> dict:
        return yaml.load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    def assert_ci_is_read_only(self, ci: dict) -> None:
        self.assertEqual(ci["permissions"], {"contents": "read"})
        for name, job in ci["jobs"].items():
            self.assertNotIn("permissions", job, f"Unexpected job override: {name}")

    def test_pr_related_workflow_inventory_requires_reviewed_policy(self) -> None:
        self.assertEqual(
            pr_related_workflows(ROOT / ".github" / "workflows"),
            {"ci.yml": {"pull_request"}},
        )

    def test_pr_related_workflow_inventory_catches_new_events_and_yaml_forms(self) -> None:
        with TemporaryDirectory() as temporary:
            workflows = Path(temporary)
            (workflows / "release.yml").write_text(
                "on:\n  push:\n    tags: [v*]\n", encoding="utf-8"
            )
            for event in sorted(PR_RELATED_EVENTS):
                with self.subTest(event=event):
                    candidate = workflows / "unreviewed.yaml"
                    candidate.write_text(
                        f"on:\n  {event}:\n    types: [opened]\n", encoding="utf-8"
                    )
                    self.assertEqual(
                        pr_related_workflows(workflows),
                        {"unreviewed.yaml": {event}},
                    )
                    candidate.unlink()
            for syntax in ("on: [pull_request]\n", "on: pull_request\n"):
                with self.subTest(syntax=syntax):
                    candidate = workflows / "inline.yml"
                    candidate.write_text(syntax, encoding="utf-8")
                    self.assertEqual(
                        pr_related_workflows(workflows),
                        {"inline.yml": {"pull_request"}},
                    )
                    candidate.unlink()

    def test_ci_rejects_permission_escalation_in_every_job(self) -> None:
        ci = self.read_workflow("ci.yml")
        self.assertEqual(
            set(ci["jobs"]),
            {
                "validate", "agent-skills-spec", "plugin-bundle", "windows",
                "macos", "installation", "codex-client", "whitespace",
            },
        )
        self.assert_ci_is_read_only(ci)
        for grant in ({"contents": "write"}, {"contents": "read", "actions": "write"}):
            with self.subTest(grant=grant):
                unsafe = deepcopy(ci)
                unsafe["permissions"] = grant
                with self.assertRaises(AssertionError):
                    self.assert_ci_is_read_only(unsafe)
        for name in ci["jobs"]:
            with self.subTest(job=name):
                unsafe = deepcopy(ci)
                unsafe["jobs"][name]["permissions"] = {"contents": "write"}
                with self.assertRaises(AssertionError):
                    self.assert_ci_is_read_only(unsafe)

    def test_every_executable_action_is_pinned_to_a_full_commit(self) -> None:
        for filename in ("ci.yml", "release.yml"):
            for name, job in self.read_workflow(filename)["jobs"].items():
                for step in job["steps"]:
                    if "uses" in step:
                        with self.subTest(workflow=filename, job=name, action=step["uses"]):
                            self.assertRegex(step["uses"], r"^[^@\s]+/[^@\s]+@[0-9a-f]{40}$")

    def test_validation_requirements_have_no_floating_runtime_dependencies(self) -> None:
        expected = {
            "requirements-dev.txt": {"PyYAML", "markdown-it-py", "mdurl"},
            "requirements-spec.txt": {"skills-ref", "click", "strictyaml", "python-dateutil", "six"},
        }
        for filename, names in expected.items():
            actual = set()
            for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
                if not line or line.startswith("#"):
                    continue
                if line.startswith("skills-ref @ "):
                    self.assertRegex(line, r"^skills-ref @ git\+https://github.com/agentskills/agentskills\.git@[0-9a-f]{40}#subdirectory=skills-ref$")
                    actual.add("skills-ref")
                else:
                    self.assertRegex(line, r"^[A-Za-z0-9_.-]+==[0-9][A-Za-z0-9_.+-]*$")
                    actual.add(line.split("==")[0])
            self.assertEqual(actual, names)

    def test_draft_prs_are_skipped_until_ready_without_skipping_main_ci(self) -> None:
        ci = self.read_workflow("ci.yml")
        self.assertEqual(
            ci["on"]["pull_request"]["types"],
            ["opened", "reopened", "synchronize", "ready_for_review", "converted_to_draft"],
        )
        self.assertEqual(
            ci["concurrency"]["group"],
            "ci-${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.event_name == 'push' && github.ref || github.run_id }}",
        )
        self.assertEqual(ci["on"]["push"]["branches"], ["main"])
        self.assertIn("workflow_dispatch", ci["on"])
        self.assertEqual(
            ci["concurrency"]["cancel-in-progress"],
            "${{ github.event_name == 'pull_request' }}",
        )
        expected_gate = (
            "github.event_name != 'pull_request' || "
            "!github.event.pull_request.draft || "
            "github.event.action == 'ready_for_review'"
        )
        for name, job in ci["jobs"].items():
            with self.subTest(job=name):
                self.assertEqual(" ".join(job["if"].split()), expected_gate)

    def test_python_39_uses_a_compatible_runner(self) -> None:
        job = self.read_workflow("ci.yml")["jobs"]["validate"]
        self.assertEqual(set(job["strategy"]["matrix"]["python-version"]), {"3.9", "3.12"})
        self.assertEqual(job["runs-on"], "${{ matrix.python-version == '3.9' && 'ubuntu-24.04' || 'ubuntu-latest' }}")

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

    def test_release_guide_requires_the_candidate_skill_inventory(self) -> None:
        guide = (ROOT / "RELEASING.md").read_text(encoding="utf-8")
        self.assertIn("exact release tag/commit", guide)
        self.assertIn("not from the current development checkout", guide)
        self.assertNotIn("expected seven canonical skills", guide)
        self.assertNotIn("current discovered", guide)

    def test_codex_client_matrix_is_pinned_and_has_no_credentials(self) -> None:
        job = self.read_workflow("ci.yml")["jobs"]["codex-client"]
        self.assertEqual(job["runs-on"], "${{ matrix.os }}")
        self.assertEqual(set(job["strategy"]["matrix"]["os"]), {"ubuntu-latest", "windows-latest", "macos-latest"})
        self.assertEqual(job["timeout-minutes"], "15")
        self.assertNotIn("permissions", job)
        steps = job["steps"]
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        commands = [step["run"] for step in steps if "run" in step]
        self.assertEqual(len(commands), 2)
        self.assertIn(f"@openai/codex@{smoke_codex.CLI_VERSION}", commands[0])
        self.assertIn("--ignore-scripts", commands[0])
        self.assertEqual(commands[1], 'python scripts/smoke_codex.py --cli "${{ runner.temp }}/frey-codex-cli/node_modules/@openai/codex/bin/codex.js"')
        self.assertTrue(any("checkout candidate" in step.get("name", "") for step in steps))
        for step in steps:
            self.assertNotIn("env", step)

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
