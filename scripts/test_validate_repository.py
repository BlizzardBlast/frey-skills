#!/usr/bin/env python3
"""Regression tests for validate_repository.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


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
        self.repo = Path(self.temp_dir.name).resolve()

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
        self.write("README.md", "# Valid Repository\n\n## Choose a skill\n\n[Sample](sample-skill/SKILL.md)\n\n## Available Skills\n\n### sample-skill\n\n## Skill Structure\n\n```text\nsample-skill/\n```\n")
        self.write_valid_skill()

        result = run_validator(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_broken_root_document_links_and_missing_catalog_entries_fail(self) -> None:
        self.write_valid_skill()
        self.write("README.md", "# Missing catalog\n\n[Broken](missing.md#missing)\n")
        output = self.assert_validation_fails_with("invalid local Markdown link")
        self.assertIn("Choose a skill inventory", output)
        self.assertIn("Available Skills inventory", output)
        self.assertIn("Current layout inventory", output)

    def test_current_repository_passes(self) -> None:
        result = run_validator(REPOSITORY_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_orientation_metadata_preserves_invocation_contract(self) -> None:
        metadata_path = REPOSITORY_ROOT / "repository-orientation" / "agents" / "openai.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))

        self.assertIs(metadata["policy"]["allow_implicit_invocation"], True)
        self.assertIn("$repository-orientation", metadata["interface"]["default_prompt"])

    def test_architecture_decision_metadata_preserves_invocation_contract(self) -> None:
        metadata_path = REPOSITORY_ROOT / "architecture-decision" / "agents" / "openai.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))

        self.assertIs(metadata["policy"]["allow_implicit_invocation"], True)
        self.assertIn("$architecture-decision", metadata["interface"]["default_prompt"])

    def test_threat_modeling_metadata_preserves_invocation_contract(self) -> None:
        metadata_path = REPOSITORY_ROOT / "threat-modeling" / "agents" / "openai.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))

        self.assertIs(metadata["policy"]["allow_implicit_invocation"], True)
        self.assertIn("$threat-modeling", metadata["interface"]["default_prompt"])

    def test_release_execution_metadata_preserves_discovery_and_scoped_authority(self) -> None:
        metadata_path = REPOSITORY_ROOT / "release-execution" / "agents" / "openai.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        self.assertIs(metadata["policy"]["allow_implicit_invocation"], True)
        self.assertIn("$release-execution", metadata["interface"]["default_prompt"])
        self.assertIn("specifically authorized publication action", metadata["interface"]["default_prompt"])

    def test_local_environment_and_test_caches_are_not_source(self) -> None:
        self.write_valid_skill()
        for relative in (".venv/Lib/third_party.py", "__pycache__/local.txt", ".pytest_cache/README.md"):
            self.write(relative, "not repository source; no trailing newline")
        result = run_validator(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_hygiene_rejects_external_links_and_cycles_without_traversal(self) -> None:
        self.write_valid_skill()
        with tempfile.TemporaryDirectory() as external_directory:
            external = Path(external_directory).resolve()
            (external / "dummy.txt").write_bytes(b"must not read external bytes")
            links = ((self.repo / "external-source", external), (self.repo / "cycle", self.repo))
            for link, target in links:
                try:
                    link.symlink_to(target, target_is_directory=True)
                except (NotImplementedError, OSError) as exc:
                    self.skipTest(f"symlinks are not supported here: {exc}")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(self.repo)],
                capture_output=True, encoding="utf-8", check=False, timeout=20,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("symlink or junction", result.stderr)
            self.assertNotIn("must end with exactly one trailing newline", result.stderr)
            self.assertEqual((external / "dummy.txt").read_bytes(), b"must not read external bytes")

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

    def test_crlf_endings_have_the_same_single_newline_rule(self) -> None:
        self.write_valid_skill()
        path = self.repo / "NOTES.md"
        path.write_bytes(b"# Valid CRLF\r\n")
        result = run_validator(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path.write_bytes(b"# Extra CRLF\r\n\r\n")
        self.assert_validation_fails_with("NOTES.md: must end with exactly one trailing newline")

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

    def test_non_string_frontmatter_keys_report_diagnostics_without_tracebacks(self) -> None:
        self.write("later-skill/SKILL.md", "---\nname: later-skill\n---\n\n# Later\n")
        for key in ("true", "42", "null", "2026-10-21"):
            with self.subTest(key=key):
                self.write(
                    "bad-frontmatter/SKILL.md",
                    "---\nname: bad-frontmatter\ndescription: Invalid key fixture.\n"
                    f"{key}: value\nunknown-field: value\n---\n\n# Bad\n",
                )
                output = self.assert_validation_fails_with("bad-frontmatter/SKILL.md: frontmatter keys must be strings")
                self.assertIn("later-skill/SKILL.md: frontmatter description", output)
                self.assertNotIn("Traceback", output)

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

    def test_markdown_skill_links_accept_fragments_encoding_and_reference_syntax(self) -> None:
        self.write_valid_skill()
        self.write("sample-skill/references/guide.md", "# Guide\n\n## Details\n")
        self.write("sample-skill/references/guide file.md", "# Guide\n")
        skill = self.repo / "sample-skill/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\n"
            "[Details](references/guide.md#details)\n"
            "[Encoded](references/%67uide.md#details)\n"
            "[`references/guide.md#details`](references/guide.md#details)\n"
            "[Reference][guide]\n\n[guide]: <references/guide file.md#guide>\n",
            encoding="utf-8",
        )
        # A link inside a supporting document is relative to that document.
        self.write("sample-skill/references/index.md", "[Nested](guide.md#details)\n")
        result = run_validator(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        skill.write_text(
            "---\nname: sample-skill\ndescription: Use when testing reference definitions.\n---\n\n"
            "[guide]: references/%67uide.md#details\n\n[Guide][guide]\n", encoding="utf-8",
        )
        result = run_validator(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_markdown_skill_links_retain_missing_anchor_and_traversal_guards(self) -> None:
        self.write_valid_skill()
        self.write("outside.md", "# Outside the packaged skill\n")
        skill = self.repo / "sample-skill/SKILL.md"
        original = skill.read_text(encoding="utf-8")
        for link, expected in (
            ("[Missing](references/guide.md#missing)", "heading anchor does not exist"),
            ("[Missing](references/missing.md)", "target does not exist"),
            ("[Escape](references/../../outside.md)", "must stay below the skill directory"),
            ("[Escape](references/%2e%2e/%2e%2e/outside.md)", "must stay below the skill directory"),
            ("[Escape](references/%2e%2e/%2e%2e/%2e%2e/outside.md)", "must stay below the repository"),
        ):
            with self.subTest(link=link):
                skill.write_text(original + "\n" + link + "\n", encoding="utf-8")
                self.assert_validation_fails_with(expected)

    def test_bare_references_keep_literal_filename_and_metadata_guards(self) -> None:
        self.write_valid_skill()
        self.write("sample-skill/references/literal%67.md", "# Literal percent filename\n")
        self.write("sample-skill/references/guide#part.md", "# Literal hash filename\n")
        skill = self.repo / "sample-skill/SKILL.md"
        original = skill.read_text(encoding="utf-8")
        valid = original + "\nRead `references/literal%67.md` and `references/guide#part.md`.\n"
        skill.write_text(valid, encoding="utf-8")
        result = run_validator(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for content, expected in (
            (valid + "\nRead `references/missing.md`.\n", "references/missing.md"),
            (original.replace("---\n\n#", "metadata:\n  guide: references/missing.md\n---\n\n#"), "references/missing.md"),
        ):
            with self.subTest(content=content):
                skill.write_text(content, encoding="utf-8")
                self.assert_validation_fails_with(expected)
        skill.write_text(original, encoding="utf-8")
        self.write("sample-skill/agents/openai.yaml", (self.repo / "sample-skill/agents/openai.yaml").read_text(encoding="utf-8") + "example: references/missing.md\n")
        self.assert_validation_fails_with("references/missing.md")

    def test_hidden_link_destinations_and_definitions_retain_literal_path_guards(self) -> None:
        self.write_valid_skill()
        self.write('outside.md', '# Outside the skill\n')
        skill = self.repo / 'sample-skill/SKILL.md'
        original = skill.read_text(encoding='utf-8')
        for path in ('references/missing.md', 'references/../../outside.md'):
            examples = []
            for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
                examples.extend((
                    f'Example <{tag}>[Example]({path})</{tag}>',
                    f'Example <{tag}>![Example]({path})</{tag}>',
                    f'Example <{tag}>\n\n[guide]: {path}\n\n</{tag}>',
                ))
            examples.extend((
                f'<!-- closed --> <!--\n\n[guide]: {path}\n\n--> ',
                f'> <!-- closed --> <!--\n>\n> [guide]: {path}',
            ))
            for example in examples:
                with self.subTest(path=path, example=example):
                    skill.write_text(original + '\n' + example + '\n', encoding='utf-8')
                    output = self.assert_validation_fails_with(f"local reference '{path}'")
                    self.assertIn('does not exist' if 'missing' in path else 'must stay below', output)

    def test_hidden_literal_paths_and_visible_links_on_the_same_line_stay_distinct(self) -> None:
        self.write_valid_skill()
        self.write('sample-skill/references/literal%67#part.md', '# Literal filename\n')
        skill = self.repo / 'sample-skill/SKILL.md'
        original = skill.read_text(encoding='utf-8')
        hidden = '[Example](references/literal%67#part.md)'
        visible = '[Visible](references/%67uide.md#guide) [Ref][guide]'
        for example in (f'Example <code>{hidden}</code> {visible}',
                        f'{visible} Example <code>{hidden}</code>',
                        f'Example <title>\n\n{hidden}\n\n</title>\n\n{visible}',
                        f'<!-- closed --> <!--\n\n{hidden}\n\n--> {visible}'):
            with self.subTest(example=example):
                skill.write_text(original + '\n' + example + '\n\n[guide]: references/%67uide.md#guide\n', encoding='utf-8')
                result = run_validator(self.repo)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_eval_and_scorecard_files_require_json_objects(self) -> None:
        self.write("later-skill/SKILL.md", "---\nname: later-skill\n---\n\n# Later\n")
        for relative_path in ("evals/evals.json", "evals/scorecards/fixture.json"):
            self.write_valid_skill("eval-skill")
            path = f"eval-skill/{relative_path}"
            for value in (None, [], False, 7, "invalid"):
                with self.subTest(path=path, value=value):
                    self.write(path, json.dumps(value) + "\n")
                    output = self.assert_validation_fails_with(f"{path}: must parse to an object")
                    self.assertIn("later-skill/SKILL.md: frontmatter description", output)
                    self.assertNotIn("Traceback", output)

    def test_null_eval_definition_cannot_hide_invalid_scorecards(self) -> None:
        self.write_valid_skill("eval-skill")
        evals_path = "eval-skill/evals/evals.json"
        valid_evals = (self.repo / evals_path).read_text(encoding="utf-8")
        scorecard_path = "eval-skill/evals/scorecards/fixture.json"
        self.write(scorecard_path, "{}\n")
        self.write(evals_path, "null\n")

        self.assert_validation_fails_with(f"{evals_path}: must parse to an object")

        self.write(evals_path, valid_evals)
        self.assert_validation_fails_with(f"{scorecard_path}: results must be a non-empty list")

    def test_json_scorecards_require_an_eval_definition(self) -> None:
        self.write_valid_skill("eval-skill")
        (self.repo / "eval-skill/evals/evals.json").unlink()
        self.write("eval-skill/evals/scorecards/fixture.json", "{}\n")

        self.assert_validation_fails_with(
            "eval-skill/evals/scorecards: JSON scorecards require an evals/evals.json definition"
        )

        self.write("later-skill/SKILL.md", "---\nname: later-skill\n---\n\n# Later\n")
        output = self.assert_validation_fails_with("JSON scorecards require an evals/evals.json definition")
        self.assertIn("later-skill/SKILL.md: frontmatter description", output)

    def test_missing_eval_definition_is_allowed_without_json_scorecards(self) -> None:
        self.write_valid_skill("eval-skill")
        (self.repo / "eval-skill/evals/evals.json").unlink()

        for readme_only in (False, True):
            with self.subTest(readme_only=readme_only):
                if readme_only:
                    self.write("eval-skill/evals/scorecards/README.md", "# Legacy scorecards\n")
                result = run_validator(self.repo)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_malformed_scorecard_enums_report_diagnostics_without_tracebacks(self) -> None:
        self.write_valid_skill("scorecard-skill")
        row = {
            "eval_id": "valid-eval",
            "case_type": "trigger",
            "trials": 10,
            "triggers": 10,
            "accepted_activation": 10,
            "assertion_passes": 10,
            "assertion_denominator": 10,
            "automatic_failures": 0,
            "result": "pass",
            "notes": 42,
        }
        scorecard = {
            "version": 1,
            "skill_name": "scorecard-skill",
            "model": "inert-fixture",
            "product_surface": "schema-test",
            "run_date": "2026-10-21",
            "skill_commit": "fixture",
            "results": [row],
        }
        for field in ("case_type", "result"):
            original = row[field]
            for value in ([], {}, None, True, 7, "unknown"):
                with self.subTest(field=field, value=value):
                    row[field] = value
                    self.write("scorecard-skill/evals/scorecards/fixture.json", json.dumps(scorecard) + "\n")
                    output = self.assert_validation_fails_with(f"results[0].{field} must be")
                    self.assertIn("scorecard-skill/evals/scorecards/fixture.json:", output)
                    self.assertIn("results[0].notes must be a string", output)
                    self.assertNotIn("Traceback", output)
            row[field] = original

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
