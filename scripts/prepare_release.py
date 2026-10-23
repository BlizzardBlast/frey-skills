#!/usr/bin/env python3
"""Prepare version-matched release notes and a validated plugin archive locally."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

try:
    from scripts.documentation import LiteralHTML, parse
    from scripts.publish_outputs import publish_outputs
    from scripts.repository_layout import validate_source_path
    from scripts.validate_plugin_bundle import validate_bundle
except ModuleNotFoundError:
    from documentation import LiteralHTML, parse
    from publish_outputs import publish_outputs
    from repository_layout import validate_source_path
    from validate_plugin_bundle import validate_bundle


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def release_notes(changelog: str, version: str) -> str:
    """Read the documented column-zero ATX sections, preserving their source text.

    Share CommonMark block context with repository documentation validation.
    """
    lines = changelog.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []
    tokens, _ = parse(changelog)
    literal = LiteralHTML()
    quoted = 0
    comment_until = 0
    for index, token in enumerate(tokens):
        if token.type == "blockquote_open":
            quoted += 1
        elif token.type == "blockquote_close":
            quoted -= 1
        if quoted or token.map is None or token.map[0] < comment_until:
            continue
        # Preserve exclusion of comments reopened on an HTML block's closing line.
        if not literal.tags and token.type == "html_block" and token.content.lstrip().startswith("<!--") and re.search(
            r"<!--(?:(?!-->).)*$", token.content, re.DOTALL
        ):
            comment_until = token.map[1]
            while comment_until < len(lines):
                line = lines[comment_until]
                comment_until += 1
                if "-->" in line and not re.search(r"<!--(?:(?!-->).)*$", line.split("-->", 1)[1]):
                    break
            literal.feed("".join(lines[token.map[0]:comment_until]))
        elif token.type == "html_block":
            literal.feed(token.content)
        for child in token.children or []:
            if child.type == "html_inline":
                literal.feed(child.content)
        if token.type == "heading_open" and token.level == 0 and token.tag in {"h1", "h2"} and not literal.tags:
            start = token.map[0]
            if lines[start].startswith("#"):
                headings.append((start, int(token.tag[1]), tokens[index + 1].content.strip()))

    matching = [position for position, (_, level, title) in enumerate(headings)
                if level == 2 and re.match(rf"\[{re.escape(version)}\](?:[ \t]|$)", title)]
    if not matching:
        raise ValueError(f"CHANGELOG.md needs a non-empty dated section for {version}")
    if len(matching) != 1:
        raise ValueError(f"CHANGELOG.md must contain exactly one section for {version}")
    position = matching[0]
    start, _, title = headings[position]
    dated = re.fullmatch(rf"\[{re.escape(version)}\] - ([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})", title)
    if dated is None:
        raise ValueError(f"CHANGELOG.md needs a non-empty dated section for {version}")
    try:
        date.fromisoformat(dated[1])
    except ValueError as exc:
        raise ValueError(f"CHANGELOG.md has an invalid calendar date for {version}") from exc
    end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
    notes = "".join(lines[start + 1:end]).strip()
    if not notes:
        raise ValueError(f"CHANGELOG.md needs a non-empty dated section for {version}")
    return notes


def prepare_release(tag: str) -> tuple[Path, Path, Path]:
    root = REPOSITORY_ROOT.resolve()
    manifest_path = root / "plugin-template" / ".codex-plugin" / "plugin.json"
    changelog_path = root / "CHANGELOG.md"
    validate_source_path(manifest_path, root)
    validate_source_path(changelog_path, root)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
        raise ValueError("the plugin manifest must have a stable semantic version")
    if tag != f"v{version}":
        raise ValueError(f"tag must match the plugin manifest: v{version}")

    changelog = changelog_path.read_text(encoding="utf-8")
    notes_content = release_notes(changelog, version)

    bundle = root / "dist" / "frey-skills"
    errors = validate_bundle(bundle)
    if errors:
        raise ValueError("plugin validation failed: " + "; ".join(errors))

    license_path = root / "LICENSE"
    if license_path.is_symlink() or not license_path.is_file() or license_path.resolve() != license_path:
        raise ValueError("LICENSE must be a regular repository-owned file, not a symlink or junction")
    license_bytes = license_path.read_bytes()

    output = root / "dist" / "releases"
    if output.resolve() != output:
        raise ValueError("release output must not traverse a symlink or junction")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"frey-skills-{version}.zip"
    notes = output / "notes.md"
    checksums = output / "SHA256SUMS"
    if any(path.is_symlink() or path.is_dir() for path in (archive, notes, checksums)):
        raise ValueError("release files must not be symlinks or directories")

    with tempfile.TemporaryDirectory(prefix=".release-", dir=output) as staging_directory:
        staging = Path(staging_directory)
        staged_archive = staging / archive.name
        files = [(license_path, "LICENSE")]
        files.extend(
            (path, "frey-skills/" + path.relative_to(bundle).as_posix())
            for path in sorted(bundle.rglob("*"), key=lambda item: item.relative_to(bundle).as_posix()) if path.is_file()
        )
        with zipfile.ZipFile(staged_archive, "w", compression=zipfile.ZIP_DEFLATED) as packaged:
            for path, name in files:
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                info.create_system = 3
                packaged.writestr(info, license_bytes if path == license_path else path.read_bytes())
        digest = hashlib.sha256(staged_archive.read_bytes()).hexdigest()
        (staging / notes.name).write_bytes(
            (notes_content + "\n\nDeterministic validation only; behavioral model evals were not run and no model-behavior certification is claimed.\n").encode("utf-8")
        )
        (staging / checksums.name).write_bytes(f"{digest}  {archive.name}\n".encode("utf-8"))
        publish_outputs(staging, (archive, notes, checksums), replace=True)
    return archive, notes, checksums


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Stable tag matching the plugin manifest, for example v1.8.1.")
    args = parser.parse_args(argv)
    try:
        outputs = prepare_release(args.tag)
    except (OSError, ValueError) as exc:
        print(f"prepare_release.py: {exc}", file=sys.stderr)
        return 1
    for path in outputs:
        print(f"Prepared: {path}")
    print("Local artifacts only; nothing was tagged, pushed, or published.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
