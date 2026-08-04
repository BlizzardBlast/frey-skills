#!/usr/bin/env python3
"""Regression tests for validate_repository.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "validate_repository.py"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


class RepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, path: str, content: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def write_valid_skill(self, name: str = "sample-skill") -> None:
        self.write(
            f"{name}/SKILL.md",
            "\n".join(
                [
                    "---",
                    f"name: {name}",
                    "description: Use when tests need a complete valid skill fixture.",
                    "---",
                    "",
                    "# Sample Skill",
                    "",
                    "Read references/guide.md and run scripts/helper.py.",
                    "Fixtures live in evals/fixtures/example.md.",
                    "",
                ]
            ),
        )
        self.write(f"{name}/references/guide.md", "# Guide\n")
        self.write(f"{name}/scripts/helper.py", "print('ok')\n")
        self.write(f"{name}/evals/fixtures/example.md", "# Fixture\n")
        self.write(
            f"{name}/agents/openai.yaml",
            "\n".join(
                [
                    "interface:",
                    '  display_name: "Sample Skill"',
                    '  short_description: "Valid fixture"',
                    '  default_prompt: "Use $sample-skill."',
                    "policy:",
                    "  allow_implicit_invocation: true",
                    "",
                ]
            ),
        )
        self.write(
            f"{name}/evals/evals.json",
            json.dumps(
                {
                    "version": 1,
                    "skill_name": name,
                    "evals": [
                        {
                            "id": "valid-eval",
                            "prompt": "Use this fixture.",
                            "expected_output": "The validator accepts it.",
                            "files": ["evals/fixtures/example.md"],
                            "assertions": ["it passes"],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

    def assert_validation_fails_with(self, expected: str) -> str:
        result = run_validator(self.repo)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        combined = result.stdout + result.stderr
        self.assertIn(expected, combined)
        return combined

    def test_valid_repository_passes(self) -> None:
        self.write("README.md", "# Valid Repository\n")
        self.write_valid_skill()

        result = run_validator(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_current_repository_passes(self) -> None:
        result = run_validator(REPOSITORY_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_frontmatter_yaml_fails(self) -> None:
        self.write(
            "broken-skill/SKILL.md",
            "---\nname: [unterminated\ndescription: broken\n---\n\n# Broken\n",
        )

        output = self.assert_validation_fails_with("broken-skill/SKILL.md")
        self.assertIn("frontmatter", output)

    def test_name_mismatch_and_invalid_name_fail(self) -> None:
        self.write(
            "bad_name/SKILL.md",
            "---\nname: bad_name\ndescription: Bad name fixture.\n---\n\n# Bad\n",
        )
        self.write(
            "mismatch-folder/SKILL.md",
            "---\nname: other-name\ndescription: Name mismatch fixture.\n---\n\n# Mismatch\n",
        )

        output = self.assert_validation_fails_with("name")
        self.assertIn("bad_name/SKILL.md", output)
        self.assertIn("mismatch-folder/SKILL.md", output)

    def test_bad_trailing_newline_fails(self) -> None:
        self.write_valid_skill()
        self.write("README.md", "# Missing trailing newline")

        output = self.assert_validation_fails_with("trailing newline")
        self.assertIn("README.md", output)

    def test_double_trailing_newline_fails(self) -> None:
        self.write_valid_skill()
        self.write("README.md", "# Extra trailing newline\n\n")

        output = self.assert_validation_fails_with("trailing newline")
        self.assertIn("README.md", output)

    def test_skill_over_500_lines_fails(self) -> None:
        body = "\n".join(f"Line {index}" for index in range(497))
        self.write(
            "long-skill/SKILL.md",
            "---\nname: long-skill\ndescription: Long skill fixture.\n---\n" + body + "\n",
        )

        output = self.assert_validation_fails_with("500 lines")
        self.assertIn("long-skill/SKILL.md", output)

    def test_missing_and_empty_description_fail(self) -> None:
        self.write("missing-description/SKILL.md", "---\nname: missing-description\n---\n\n# Missing\n")
        self.write(
            "empty-description/SKILL.md",
            "---\nname: empty-description\ndescription: '   '\n---\n\n# Empty\n",
        )

        output = self.assert_validation_fails_with("description")
        self.assertIn("missing-description/SKILL.md", output)
        self.assertIn("empty-description/SKILL.md", output)

    def test_unsupported_and_invalid_optional_frontmatter_fields_fail(self) -> None:
        self.write(
            "bad-frontmatter/SKILL.md",
            "---\n"
            "name: bad-frontmatter\n"
            "description: Invalid optional field fixture.\n"
            "compatibility: 123\n"
            "unknown-field: value\n"
            "---\n\n# Bad\n",
        )

        output = self.assert_validation_fails_with("bad-frontmatter/SKILL.md")
        self.assertIn("compatibility", output)
        self.assertIn("unsupported fields", output)

    def test_nested_metadata_value_fails(self) -> None:
        self.write(
            "bad-metadata/SKILL.md",
            "---\n"
            "name: bad-metadata\n"
            "description: Invalid metadata fixture.\n"
            "metadata:\n"
            "  nested:\n"
            "    value: invalid\n"
            "---\n\n# Bad\n",
        )

        output = self.assert_validation_fails_with("bad-metadata/SKILL.md")
        self.assertIn("must be a scalar", output)

    def test_missing_local_reference_fails(self) -> None:
        self.write(
            "referencing-skill/SKILL.md",
            "---\nname: referencing-skill\ndescription: Missing reference fixture.\n---\n\nSee references/missing.md.\n",
        )

        output = self.assert_validation_fails_with("references/missing.md")
        self.assertIn("referencing-skill/SKILL.md", output)

    def test_missing_dotted_local_reference_fails(self) -> None:
        self.write(
            "referencing-skill/SKILL.md",
            "---\nname: referencing-skill\ndescription: Missing dotted reference fixture.\n---\n\n"
            "See [the guide](./references/missing.md) and `./scripts/missing.py`.\n",
        )

        output = self.assert_validation_fails_with("references/missing.md")
        self.assertIn("scripts/missing.py", output)
        self.assertIn("referencing-skill/SKILL.md", output)

    def test_invalid_openai_metadata_fails(self) -> None:
        self.write_valid_skill("metadata-skill")
        self.write(
            "metadata-skill/agents/openai.yaml",
            "interface:\n  display_name: 123\npolicy:\n  allow_implicit_invocation: sometimes\n",
        )

        output = self.assert_validation_fails_with("agents/openai.yaml")
        self.assertIn("display_name", output)
        self.assertIn("allow_implicit_invocation", output)

    def test_invalid_and_missing_eval_fixture_fails(self) -> None:
        self.write_valid_skill("eval-skill")
        self.write(
            "eval-skill/evals/evals.json",
            json.dumps(
                {
                    "skill_name": "wrong-skill",
                    "evals": [
                        {
                            "id": "",
                            "prompt": "Prompt exists.",
                            "expected_output": "Expected exists.",
                            "files": ["evals/fixtures/missing.md"],
                            "assertions": [],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        output = self.assert_validation_fails_with("evals/evals.json")
        self.assertIn("skill_name", output)
        self.assertIn("evals/fixtures/missing.md", output)

    def test_eval_version_and_duplicate_ids_fail(self) -> None:
        self.write_valid_skill("eval-skill")
        self.write(
            "eval-skill/evals/evals.json",
            json.dumps(
                {
                    "version": 2,
                    "skill_name": "eval-skill",
                    "evals": [
                        {
                            "id": "duplicate",
                            "prompt": "First prompt.",
                            "expected_output": "First output.",
                            "files": ["evals/fixtures/example.md"],
                            "assertions": ["first assertion"],
                        },
                        {
                            "id": "duplicate",
                            "prompt": "Second prompt.",
                            "expected_output": "Second output.",
                            "files": ["evals/fixtures/example.md"],
                            "assertions": ["second assertion"],
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        output = self.assert_validation_fails_with("version must equal 1")
        self.assertIn("duplicates 'duplicate'", output)

    def test_python_and_extensionless_text_files_require_trailing_newlines(self) -> None:
        self.write_valid_skill()
        self.write("scripts/helper.py", "print('missing newline')")
        self.write("LICENSE", "missing newline")

        output = self.assert_validation_fails_with("trailing newline")
        self.assertIn("scripts/helper.py", output)
        self.assertIn("LICENSE", output)

    def test_valid_eval_scorecard_passes(self) -> None:
        self.write_valid_skill("scorecard-skill")
        self.write(
            "scorecard-skill/evals/scorecards/gpt.json",
            json.dumps(
                {
                    "version": 1,
                    "skill_name": "scorecard-skill",
                    "model": "example-model",
                    "product_surface": "example-surface",
                    "run_date": "2026-08-04",
                    "skill_commit": "abc123",
                    "results": [
                        {
                            "eval_id": "valid-eval",
                            "case_type": "trigger",
                            "trials": 10,
                            "triggers": 9,
                            "accepted_activation": 9,
                            "assertion_passes": 9,
                            "assertion_denominator": 9,
                            "automatic_failures": 0,
                            "result": "pass",
                            "notes": "Accepted manual run.",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        result = run_validator(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_eval_scorecard_fails(self) -> None:
        self.write_valid_skill("scorecard-skill")
        self.write(
            "scorecard-skill/evals/scorecards/gpt.json",
            json.dumps(
                {
                    "version": 1,
                    "skill_name": "scorecard-skill",
                    "model": "example-model",
                    "product_surface": "example-surface",
                    "run_date": "2026-08-04",
                    "skill_commit": "abc123",
                    "results": [
                        {
                            "eval_id": "wrong-id",
                            "case_type": "trigger",
                            "trials": 9,
                            "triggers": 9,
                            "accepted_activation": 9,
                            "assertion_passes": 9,
                            "assertion_denominator": 9,
                            "automatic_failures": 0,
                            "result": "pass",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        output = self.assert_validation_fails_with("trials must equal 10")
        self.assertIn("missing eval IDs", output)
        self.assertIn("unknown eval IDs", output)

    def test_eval_scorecard_rejects_impossible_count_relationships(self) -> None:
        self.write_valid_skill("scorecard-skill")
        self.write(
            "scorecard-skill/evals/scorecards/gpt.json",
            json.dumps(
                {
                    "version": 1,
                    "skill_name": "scorecard-skill",
                    "model": "example-model",
                    "product_surface": "example-surface",
                    "run_date": "2026-08-04",
                    "skill_commit": "abc123",
                    "results": [
                        {
                            "eval_id": "valid-eval",
                            "case_type": "trigger",
                            "trials": 9,
                            "triggers": 9,
                            "accepted_activation": 9,
                            "assertion_passes": 10,
                            "assertion_denominator": 9,
                            "automatic_failures": 10,
                            "result": "fail",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        output = self.assert_validation_fails_with(
            "assertion_passes must not exceed assertion_denominator"
        )
        self.assertIn("automatic_failures must not exceed trials", output)

    def test_eval_scorecard_allows_failure_counts_at_trial_boundary(self) -> None:
        self.write_valid_skill("scorecard-skill")
        self.write(
            "scorecard-skill/evals/scorecards/gpt.json",
            json.dumps(
                {
                    "version": 1,
                    "skill_name": "scorecard-skill",
                    "model": "example-model",
                    "product_surface": "example-surface",
                    "run_date": "2026-08-04",
                    "skill_commit": "abc123",
                    "results": [
                        {
                            "eval_id": "valid-eval",
                            "case_type": "trigger",
                            "trials": 10,
                            "triggers": 10,
                            "accepted_activation": 10,
                            "assertion_passes": 10,
                            "assertion_denominator": 10,
                            "automatic_failures": 10,
                            "result": "fail",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        result = run_validator(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_eval_skill_name_fails(self) -> None:
        self.write_valid_skill("eval-skill")
        self.write(
            "eval-skill/evals/evals.json",
            json.dumps(
                {
                    "evals": [
                        {
                            "id": "missing-skill-name",
                            "prompt": "Prompt exists.",
                            "expected_output": "Expected exists.",
                            "files": ["evals/fixtures/example.md"],
                            "assertions": ["assertion exists"],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )

        output = self.assert_validation_fails_with("evals/evals.json")
        self.assertIn("skill_name", output)


if __name__ == "__main__":
    unittest.main()
