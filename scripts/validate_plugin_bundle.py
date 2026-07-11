#!/usr/bin/env python3
"""Validate the generated frey-skills Codex plugin bundle."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Optional


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = ("code-review", "iterative-self-review")
EXPECTED_AUTHOR_URL = "https://github.com/BlizzardBlast"
EXPECTED_REPOSITORY_URL = "https://github.com/BlizzardBlast/frey-skills"
DISALLOWED_TOP_LEVEL_FIELDS = {"apps", "mcpServers", "hooks", "marketplace"}
DISALLOWED_INTERFACE_FIELDS = {"brandColor", "composerIcon", "logo", "logoDark", "screenshots"}
ALLOWED_TOP_LEVEL_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "interface",
}
ALLOWED_AUTHOR_FIELDS = {"name", "url", "email"}
ALLOWED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "defaultPrompt",
}
REQUIRED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "defaultPrompt",
}
REQUIRED_KEYWORDS = {"agent-skills", "codex", "code-review", "iterative-review", "review", "self-review", "writing"}
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Path to the generated plugin bundle root.")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    bundle = args.bundle.expanduser().resolve()
    errors = validate_bundle(bundle)
    if errors:
        print("Plugin bundle validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Plugin bundle validation passed: {bundle}")
    return 0


def validate_bundle(bundle: Path) -> list[str]:
    errors: list[str] = []
    if not bundle.is_dir():
        return [f"bundle path is not a directory: {bundle}"]

    validate_no_symlinks(bundle, errors)
    manifest = load_manifest(bundle, errors)
    if manifest is not None:
        validate_manifest(manifest, errors)
    validate_skill_layout(bundle, errors)
    validate_skill_parity(bundle, errors)
    return errors


def load_manifest(bundle: Path, errors: list[str]) -> Optional[dict[str, Any]]:
    manifest_path = bundle / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        errors.append("missing .codex-plugin/plugin.json")
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f".codex-plugin/plugin.json must be valid JSON: line {exc.lineno}, column {exc.colno}")
        return None
    except OSError as exc:
        errors.append(f"could not read .codex-plugin/plugin.json: {exc}")
        return None
    if not isinstance(manifest, dict):
        errors.append(".codex-plugin/plugin.json must contain a JSON object")
        return None
    return manifest


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    validate_no_todo_placeholders(manifest, "$", errors)

    for field in sorted(set(manifest) - ALLOWED_TOP_LEVEL_FIELDS):
        errors.append(f"plugin.json field {field!r} is not allowed in this generated bundle")
    for field in sorted(DISALLOWED_TOP_LEVEL_FIELDS & set(manifest)):
        errors.append(f"plugin.json must not declare {field!r}; this plugin ships skills only")

    require_exact_string(manifest, "name", "frey-skills", errors)
    require_exact_string(manifest, "version", "1.0.0", errors)
    version = manifest.get("version")
    if isinstance(version, str) and SEMVER_PATTERN.fullmatch(version) is None:
        errors.append("plugin.json field 'version' must use strict semantic versioning")
    require_non_empty_string(manifest, "description", errors)
    require_exact_string(manifest, "homepage", EXPECTED_REPOSITORY_URL, errors)
    require_exact_string(manifest, "repository", EXPECTED_REPOSITORY_URL, errors)
    require_exact_string(manifest, "license", "MIT", errors)
    require_exact_string(manifest, "skills", "./skills/", errors)
    validate_keywords(manifest.get("keywords"), errors)
    validate_author(manifest.get("author"), errors)
    validate_interface(manifest.get("interface"), errors)


def validate_author(author: Any, errors: list[str]) -> None:
    if not isinstance(author, dict):
        errors.append("plugin.json field 'author' must be an object")
        return
    for field in sorted(set(author) - ALLOWED_AUTHOR_FIELDS):
        errors.append(f"plugin.json field 'author.{field}' is not allowed")
    require_exact_string(author, "name", "BlizzardBlast", errors, prefix="author")
    require_exact_string(author, "url", EXPECTED_AUTHOR_URL, errors, prefix="author")


def validate_keywords(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append("plugin.json field 'keywords' must be a non-empty array of strings")
        return
    missing = sorted(REQUIRED_KEYWORDS - set(value))
    if missing:
        errors.append(f"plugin.json field 'keywords' is missing discovery keywords: {', '.join(missing)}")


def validate_interface(interface: Any, errors: list[str]) -> None:
    if not isinstance(interface, dict):
        errors.append("plugin.json field 'interface' must be an object")
        return
    for field in sorted(set(interface) - ALLOWED_INTERFACE_FIELDS):
        errors.append(f"plugin.json field 'interface.{field}' is not allowed")
    for field in sorted(DISALLOWED_INTERFACE_FIELDS & set(interface)):
        errors.append(f"plugin.json must not declare visual asset field 'interface.{field}'")
    for field in sorted(REQUIRED_INTERFACE_FIELDS):
        if field == "capabilities":
            continue
        if field == "defaultPrompt":
            continue
        require_non_empty_string(interface, field, errors, prefix="interface")

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) and item.strip() for item in capabilities
    ):
        errors.append("plugin.json field 'interface.capabilities' must be an array of strings")
    else:
        missing = sorted({"Review", "Write"} - set(capabilities))
        if missing:
            errors.append(f"plugin.json field 'interface.capabilities' must include: {', '.join(missing)}")

    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts:
        errors.append("plugin.json field 'interface.defaultPrompt' must be a non-empty array")
    else:
        for index, prompt in enumerate(prompts):
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"plugin.json field 'interface.defaultPrompt[{index}]' must be a non-empty string")
            elif len(prompt) > 128:
                errors.append(f"plugin.json field 'interface.defaultPrompt[{index}]' must be 128 characters or fewer")


def validate_skill_layout(bundle: Path, errors: list[str]) -> None:
    skills_root = bundle / "skills"
    if not skills_root.is_dir():
        errors.append("missing skills/ directory")
        return
    actual_skills = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
    expected_skills = sorted(EXPECTED_SKILLS)
    if actual_skills != expected_skills:
        errors.append(
            "skills/ must contain exactly these directories: "
            f"{', '.join(expected_skills)}; found: {', '.join(actual_skills) or '(none)'}"
        )
    for skill_name in EXPECTED_SKILLS:
        skill_file = skills_root / skill_name / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing expected skill file: skills/{skill_name}/SKILL.md")


def validate_skill_parity(bundle: Path, errors: list[str]) -> None:
    for skill_name in EXPECTED_SKILLS:
        source = REPOSITORY_ROOT / skill_name
        generated = bundle / "skills" / skill_name
        if not generated.is_dir():
            continue
        compare_trees(source, generated, f"skills/{skill_name}", errors)


def compare_trees(source: Path, generated: Path, label: str, errors: list[str]) -> None:
    source_dirs = relative_directories(source)
    generated_dirs = relative_directories(generated)
    if source_dirs != generated_dirs:
        errors.append(f"{label} directory layout does not match canonical source")

    source_files = relative_files(source)
    generated_files = relative_files(generated)
    if source_files != generated_files:
        missing = sorted(source_files - generated_files)
        extra = sorted(generated_files - source_files)
        if missing:
            errors.append(f"{label} is missing files: {format_paths(missing)}")
        if extra:
            errors.append(f"{label} contains extra files: {format_paths(extra)}")
        return

    for relative_file in sorted(source_files):
        if not filecmp.cmp(source / relative_file, generated / relative_file, shallow=False):
            errors.append(f"{label}/{relative_file.as_posix()} differs from canonical source")


def validate_no_symlinks(bundle: Path, errors: list[str]) -> None:
    for path in bundle.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlinks are not allowed in plugin bundles: {path.relative_to(bundle).as_posix()}")


def validate_no_todo_placeholders(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        if "[TODO:" in value or "TODO_PLACEHOLDER" in value:
            errors.append(f"plugin.json value {path} contains a TODO placeholder")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_no_todo_placeholders(item, f"{path}[{index}]", errors)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_no_todo_placeholders(item, f"{path}.{key}", errors)


def require_exact_string(
    payload: dict[str, Any],
    key: str,
    expected: str,
    errors: list[str],
    *,
    prefix: Optional[str] = None,
) -> None:
    value = payload.get(key)
    field = f"{prefix}.{key}" if prefix else key
    if value != expected:
        errors.append(f"plugin.json field '{field}' must be {expected!r}")


def require_non_empty_string(
    payload: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    prefix: Optional[str] = None,
) -> None:
    value = payload.get(key)
    field = f"{prefix}.{key}" if prefix else key
    if not isinstance(value, str) or not value.strip():
        errors.append(f"plugin.json field '{field}' must be a non-empty string")


def relative_files(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


def relative_directories(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*") if path.is_dir() and not path.is_symlink()}


def format_paths(paths: Iterable[Path]) -> str:
    return ", ".join(path.as_posix() for path in paths)


if __name__ == "__main__":
    raise SystemExit(main())
