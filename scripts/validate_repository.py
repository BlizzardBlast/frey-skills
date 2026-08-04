#!/usr/bin/env python3
"""Validate repository-level skill metadata and source hygiene."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

try:
    from scripts.repository_layout import discover_skill_names
except ModuleNotFoundError:
    from repository_layout import discover_skill_names


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_PATTERN = re.compile(r"(?<![\w./-])(?:\./)?((?:references|scripts|evals)/[^\s`\"'<>]+)")
ALLOWED_SKILL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
}
REFERENCE_SUFFIXES = {".json", ".md", ".yaml", ".yml"}
TEXT_SUFFIXES = {".cfg", ".ini", ".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
TEXT_FILENAMES = {".gitattributes", ".gitignore", "LICENSE"}
EXCLUDED_DIRS = {".git", "dist", "eval-workspace", ".superpowers", ".omo"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root,
        help="Repository root to validate. Defaults to this script's repository.",
    )
    return parser.parse_args(argv)


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[str] = []

    def add_error(self, path: Path, message: str) -> None:
        try:
            display_path = path.resolve().relative_to(self.root)
        except ValueError:
            display_path = path
        self.errors.append(f"{display_path}: {message}")

    def validate(self) -> int:
        if not self.root.exists() or not self.root.is_dir():
            self.add_error(self.root, "root does not exist or is not a directory")
            return 1

        for skill_dir in self.discover_skill_dirs():
            self.validate_skill(skill_dir)
        self.validate_source_trailing_newlines()

        if self.errors:
            for error in self.errors:
                print(error, file=sys.stderr)
            return 1

        print(f"Repository validation passed: {self.root}")
        return 0

    def discover_skill_dirs(self) -> list[Path]:
        return [self.root / name for name in discover_skill_names(self.root)]

    def validate_skill(self, skill_dir: Path) -> None:
        skill_file = skill_dir / "SKILL.md"
        text = self.read_text(skill_file)
        if text is None:
            return

        self.validate_skill_line_count(skill_file, text)
        frontmatter = self.parse_frontmatter(skill_file, text)
        if frontmatter is not None:
            self.validate_skill_metadata(skill_dir, skill_file, frontmatter)
        self.validate_local_references(skill_dir)
        self.validate_openai_metadata(skill_dir)
        self.validate_evals(skill_dir)
        self.validate_eval_scorecards(skill_dir)

    def read_text(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self.add_error(path, f"must be valid UTF-8: {exc}")
        except OSError as exc:
            self.add_error(path, f"could not be read: {exc}")
        return None

    def read_json(self, path: Path) -> Any | None:
        text = self.read_text(path)
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            self.add_error(path, f"invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}")
            return None

    def validate_skill_line_count(self, path: Path, text: str) -> None:
        if len(text.splitlines()) > 500:
            self.add_error(path, "must be 500 lines or fewer")

    def parse_frontmatter(self, path: Path, text: str) -> dict[str, Any] | None:
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            self.add_error(path, "SKILL.md must start with YAML frontmatter delimited by ---")
            return None

        end_index: int | None = None
        for index, line in enumerate(lines[1:], start=1):
            if line == "---":
                end_index = index
                break
        if end_index is None:
            self.add_error(path, "frontmatter closing --- delimiter is missing")
            return None

        raw_frontmatter = "\n".join(lines[1:end_index])
        try:
            loaded = yaml.safe_load(raw_frontmatter)
        except yaml.YAMLError as exc:
            self.add_error(path, f"frontmatter YAML could not be parsed: {exc}")
            return None

        if not isinstance(loaded, dict):
            self.add_error(path, "frontmatter must parse to an object")
            return None
        return loaded

    def validate_skill_metadata(self, skill_dir: Path, skill_file: Path, metadata: dict[str, Any]) -> None:
        name = metadata.get("name")
        description = metadata.get("description")

        if not isinstance(name, str) or not name.strip():
            self.add_error(skill_file, "frontmatter name must be a non-empty string")
        else:
            if len(name) > 64:
                self.add_error(skill_file, "frontmatter name must be 64 characters or fewer")
            if not NAME_PATTERN.fullmatch(name):
                self.add_error(
                    skill_file,
                    "frontmatter name must match ^[a-z0-9]+(?:-[a-z0-9]+)*$",
                )
            if name != skill_dir.name:
                self.add_error(skill_file, f"frontmatter name {name!r} must equal folder name {skill_dir.name!r}")

        if not isinstance(description, str) or not description.strip():
            self.add_error(skill_file, "frontmatter description must be a non-empty string")
        elif len(description) > 1024:
            self.add_error(skill_file, "frontmatter description must be 1024 characters or fewer")

        unknown_fields = sorted(set(metadata) - ALLOWED_SKILL_FIELDS)
        if unknown_fields:
            self.add_error(
                skill_file,
                "frontmatter contains unsupported fields: " + ", ".join(unknown_fields),
            )

        license_value = metadata.get("license")
        if license_value is not None and (not isinstance(license_value, str) or not license_value.strip()):
            self.add_error(skill_file, "frontmatter license must be a non-empty string when provided")

        compatibility = metadata.get("compatibility")
        if compatibility is not None:
            if not isinstance(compatibility, str):
                self.add_error(skill_file, "frontmatter compatibility must be a string")
            elif len(compatibility) > 500:
                self.add_error(skill_file, "frontmatter compatibility must be 500 characters or fewer")

        allowed_tools = metadata.get("allowed-tools")
        if allowed_tools is not None and not isinstance(allowed_tools, str):
            self.add_error(skill_file, "frontmatter allowed-tools must be a string")

        metadata_value = metadata.get("metadata")
        if metadata_value is not None:
            if not isinstance(metadata_value, dict):
                self.add_error(skill_file, "frontmatter metadata must be an object")
            else:
                for key, value in metadata_value.items():
                    if not isinstance(key, str) or not key.strip():
                        self.add_error(skill_file, "frontmatter metadata keys must be non-empty strings")
                    if isinstance(value, (dict, list)) or value is None:
                        self.add_error(
                            skill_file,
                            f"frontmatter metadata value for {key!r} must be a scalar",
                        )

    def validate_local_references(self, skill_dir: Path) -> None:
        for source_file in self.iter_skill_text_files(skill_dir):
            text = self.read_text(source_file)
            if text is None:
                continue
            for reference in self.extract_local_references(text):
                self.validate_skill_relative_path(
                    skill_dir=skill_dir,
                    source_file=source_file,
                    relative_path=reference,
                    label="local reference",
                )

    def iter_skill_text_files(self, skill_dir: Path) -> Iterable[Path]:
        for path in self.walk_files(skill_dir):
            if path.suffix in REFERENCE_SUFFIXES:
                yield path

    def extract_local_references(self, text: str) -> set[str]:
        references: set[str] = set()
        for match in REFERENCE_PATTERN.finditer(text):
            references.add(match.group(1).rstrip(".,;:)]}"))
        return references

    def validate_skill_relative_path(
        self,
        *,
        skill_dir: Path,
        source_file: Path,
        relative_path: str,
        label: str,
    ) -> bool:
        if not relative_path or relative_path.startswith("/"):
            self.add_error(source_file, f"{label} {relative_path!r} must be relative to the skill directory")
            return False
        target = (skill_dir / relative_path).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError:
            self.add_error(source_file, f"{label} {relative_path!r} must stay below the skill directory")
            return False
        if not target.exists():
            self.add_error(source_file, f"{label} {relative_path!r} does not exist")
            return False
        return True

    def validate_openai_metadata(self, skill_dir: Path) -> None:
        metadata_file = skill_dir / "agents" / "openai.yaml"
        if not metadata_file.exists():
            return

        text = self.read_text(metadata_file)
        if text is None:
            return
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            self.add_error(metadata_file, f"YAML could not be parsed: {exc}")
            return
        if not isinstance(data, dict):
            self.add_error(metadata_file, "must parse to an object")
            return

        interface = data.get("interface")
        if not isinstance(interface, dict):
            self.add_error(metadata_file, "interface must be an object")
            interface = {}
        for key in ("display_name", "short_description", "default_prompt"):
            value = interface.get(key)
            if not isinstance(value, str) or not value.strip():
                self.add_error(metadata_file, f"interface.{key} must be a non-empty string")

        policy = data.get("policy")
        if not isinstance(policy, dict):
            self.add_error(metadata_file, "policy must be an object")
            policy = {}
        if not isinstance(policy.get("allow_implicit_invocation"), bool):
            self.add_error(metadata_file, "policy.allow_implicit_invocation must be a boolean")

    def validate_evals(self, skill_dir: Path) -> None:
        evals_file = skill_dir / "evals" / "evals.json"
        if not evals_file.exists():
            return

        data = self.read_json(evals_file)
        if data is None:
            return
        if not isinstance(data, dict):
            self.add_error(evals_file, "must parse to an object")
            return

        version = data.get("version")
        if version != 1:
            self.add_error(evals_file, "version must equal 1")

        skill_name = data.get("skill_name")
        if not isinstance(skill_name, str) or not skill_name.strip():
            self.add_error(evals_file, "skill_name must be a non-empty string")
        elif skill_name != skill_dir.name:
            self.add_error(evals_file, f"skill_name must equal folder name {skill_dir.name!r}")

        evals = data.get("evals")
        if not isinstance(evals, list) or not evals:
            self.add_error(evals_file, "evals must be a non-empty list")
            return

        seen_eval_ids: set[str] = set()
        for index, eval_case in enumerate(evals):
            label = f"evals[{index}]"
            if not isinstance(eval_case, dict):
                self.add_error(evals_file, f"{label} must be an object")
                continue
            for key in ("id", "prompt", "expected_output"):
                value = eval_case.get(key)
                if not isinstance(value, str) or not value.strip():
                    self.add_error(evals_file, f"{label}.{key} must be a non-empty string")

            eval_id = eval_case.get("id")
            if isinstance(eval_id, str) and eval_id.strip():
                if eval_id in seen_eval_ids:
                    self.add_error(evals_file, f"{label}.id duplicates {eval_id!r}")
                else:
                    seen_eval_ids.add(eval_id)
            files = eval_case.get("files")
            if not isinstance(files, list):
                self.add_error(evals_file, f"{label}.files must be a list")
            else:
                for file_index, relative_path in enumerate(files):
                    if not isinstance(relative_path, str) or not relative_path.strip():
                        self.add_error(evals_file, f"{label}.files[{file_index}] must be a non-empty string")
                        continue
                    self.validate_skill_relative_path(
                        skill_dir=skill_dir,
                        source_file=evals_file,
                        relative_path=relative_path,
                        label=f"{label}.files[{file_index}]",
                    )
            assertions = eval_case.get("assertions")
            if not isinstance(assertions, list) or not assertions:
                self.add_error(evals_file, f"{label}.assertions must be a non-empty list")
            else:
                for assertion_index, assertion in enumerate(assertions):
                    if not isinstance(assertion, str) or not assertion.strip():
                        self.add_error(
                            evals_file,
                            f"{label}.assertions[{assertion_index}] must be a non-empty string",
                        )

    def validate_eval_scorecards(self, skill_dir: Path) -> None:
        evals_file = skill_dir / "evals" / "evals.json"
        scorecards_dir = skill_dir / "evals" / "scorecards"
        if not evals_file.is_file() or not scorecards_dir.is_dir():
            return

        evals_data = self.read_json(evals_file)
        if not isinstance(evals_data, dict):
            return
        eval_cases = evals_data.get("evals")
        if not isinstance(eval_cases, list):
            return
        expected_ids = {
            case.get("id")
            for case in eval_cases
            if isinstance(case, dict) and isinstance(case.get("id"), str) and case.get("id")
        }

        for scorecard_file in sorted(scorecards_dir.glob("*.json")):
            data = self.read_json(scorecard_file)
            if not isinstance(data, dict):
                self.add_error(scorecard_file, "must parse to an object")
                continue
            if data.get("version") != 1:
                self.add_error(scorecard_file, "version must equal 1")
            if data.get("skill_name") != skill_dir.name:
                self.add_error(scorecard_file, f"skill_name must equal {skill_dir.name!r}")
            for key in ("model", "product_surface", "run_date", "skill_commit"):
                value = data.get(key)
                if not isinstance(value, str) or not value.strip():
                    self.add_error(scorecard_file, f"{key} must be a non-empty string")

            results = data.get("results")
            if not isinstance(results, list) or not results:
                self.add_error(scorecard_file, "results must be a non-empty list")
                continue

            seen_ids: set[str] = set()
            for index, result in enumerate(results):
                label = f"results[{index}]"
                if not isinstance(result, dict):
                    self.add_error(scorecard_file, f"{label} must be an object")
                    continue
                eval_id = result.get("eval_id")
                if not isinstance(eval_id, str) or not eval_id.strip():
                    self.add_error(scorecard_file, f"{label}.eval_id must be a non-empty string")
                elif eval_id in seen_ids:
                    self.add_error(scorecard_file, f"{label}.eval_id duplicates {eval_id!r}")
                else:
                    seen_ids.add(eval_id)

                if result.get("case_type") not in {"trigger", "non-trigger"}:
                    self.add_error(scorecard_file, f"{label}.case_type must be trigger or non-trigger")
                if result.get("trials") != 10:
                    self.add_error(scorecard_file, f"{label}.trials must equal 10")
                numeric_fields = (
                    "triggers",
                    "accepted_activation",
                    "assertion_passes",
                    "assertion_denominator",
                    "automatic_failures",
                )
                numeric_values: dict[str, int] = {}
                for key in numeric_fields:
                    value = result.get(key)
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 10:
                        self.add_error(scorecard_file, f"{label}.{key} must be an integer from 0 to 10")
                    else:
                        numeric_values[key] = value

                case_type = result.get("case_type")
                triggers = numeric_values.get("triggers")
                accepted_activation = numeric_values.get("accepted_activation")
                assertion_passes = numeric_values.get("assertion_passes")
                assertion_denominator = numeric_values.get("assertion_denominator")
                automatic_failures = numeric_values.get("automatic_failures")

                if case_type in {"trigger", "non-trigger"} and triggers is not None:
                    expected_accepted = triggers if case_type == "trigger" else 10 - triggers
                    if accepted_activation is not None and accepted_activation != expected_accepted:
                        self.add_error(
                            scorecard_file,
                            f"{label}.accepted_activation must equal {expected_accepted} for its case type",
                        )
                if (
                    accepted_activation is not None
                    and assertion_denominator is not None
                    and assertion_denominator != accepted_activation
                ):
                    self.add_error(
                        scorecard_file,
                        f"{label}.assertion_denominator must equal accepted_activation",
                    )

                recorded_result = result.get("result")
                if recorded_result not in {"pass", "fail"}:
                    self.add_error(scorecard_file, f"{label}.result must be pass or fail")
                elif all(
                    value is not None
                    for value in (
                        accepted_activation,
                        assertion_passes,
                        assertion_denominator,
                        automatic_failures,
                    )
                ):
                    computed_pass = (
                        accepted_activation >= 9
                        and assertion_passes == assertion_denominator
                        and automatic_failures == 0
                    )
                    expected_result = "pass" if computed_pass else "fail"
                    if recorded_result != expected_result:
                        self.add_error(
                            scorecard_file,
                            f"{label}.result must be {expected_result!r} for the recorded counts",
                        )

                notes = result.get("notes")
                if notes is not None and not isinstance(notes, str):
                    self.add_error(scorecard_file, f"{label}.notes must be a string when provided")

            missing_ids = sorted(expected_ids - seen_ids)
            extra_ids = sorted(seen_ids - expected_ids)
            if missing_ids:
                self.add_error(scorecard_file, "missing eval IDs: " + ", ".join(missing_ids))
            if extra_ids:
                self.add_error(scorecard_file, "unknown eval IDs: " + ", ".join(extra_ids))

    def validate_source_trailing_newlines(self) -> None:
        for path in self.walk_files(self.root):
            if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_FILENAMES:
                continue
            self.validate_exactly_one_trailing_newline(path)

    def validate_exactly_one_trailing_newline(self, path: Path) -> None:
        try:
            content = path.read_bytes()
        except OSError as exc:
            self.add_error(path, f"could not be read: {exc}")
            return
        if not content.endswith(b"\n") or content.endswith(b"\n\n"):
            self.add_error(path, "must end with exactly one trailing newline")

    def walk_files(self, root: Path) -> Iterable[Path]:
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                children = sorted(current.iterdir(), key=lambda path: path.name, reverse=True)
            except OSError as exc:
                self.add_error(current, f"could not be listed: {exc}")
                continue
            for child in children:
                if child.is_dir():
                    if child.name not in EXCLUDED_DIRS:
                        stack.append(child)
                elif child.is_file():
                    yield child


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return Validator(args.root).validate()


if __name__ == "__main__":
    raise SystemExit(main())
