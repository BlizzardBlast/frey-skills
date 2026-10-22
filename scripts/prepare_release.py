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
    from scripts.publish_outputs import publish_outputs
    from scripts.repository_layout import validate_source_path
    from scripts.validate_plugin_bundle import validate_bundle
except ModuleNotFoundError:
    from publish_outputs import publish_outputs
    from repository_layout import validate_source_path
    from validate_plugin_bundle import validate_bundle


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HTML_BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|"
    "dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|"
    "header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|"
    "p|param|section|source|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
HTML_TAG = (
    r"(?:</[A-Za-z][A-Za-z0-9-]*[ \t]*>"
    r"|<[A-Za-z][A-Za-z0-9-]*(?:[ \t]+[A-Za-z_:][A-Za-z0-9_.:-]*"
    r"(?:[ \t]*=[ \t]*(?:[^\"'=<>`\x00-\x20]+|'[^']*'|\"[^\"]*\"))?)*[ \t]*/?>)"
)


def release_notes(changelog: str, version: str) -> str:
    """Read the documented column-zero ATX sections, preserving their source text.

    Fenced code and HTML blocks cannot supply section boundaries. Keep this
    bounded changelog reader dependency-free for standalone plugin checks.
    """
    lines = changelog.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []
    fence = ""
    html_end: str | None = None
    paragraph = False
    for index, source_line in enumerate(lines):
        line = source_line.rstrip("\r\n")
        if fence:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = ""
                paragraph = False
            continue
        if html_end is not None:
            if (not html_end and not line.strip()) or (html_end and html_end in line.lower()):
                remainder = line.lower().split(html_end, 1)[1] if html_end else ""
                comment_continues = html_end == "-->" and re.search(r"<!--(?:(?!-->).)*$", remainder)
                html_end = None
                paragraph = False
                if comment_continues:
                    html_end = "-->"
            continue
        if not paragraph and re.match(r"(?: {4}|\t)", line):
            continue
        opening = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening and (opening[1][0] == "~" or "`" not in opening[2]):
            fence = opening[1]
            continue
        literal = re.match(r" {0,3}<(pre|script|style|textarea)(?:[ \t>]|$)", line, re.IGNORECASE)
        if literal:
            paragraph = False
            closing = f"</{literal[1].lower()}>"
            if closing not in line.lower():
                html_end = closing
            continue
        if re.match(r" {0,3}<!--", line):
            paragraph = False
            if re.search(r"<!--(?:(?!-->).)*$", line):
                html_end = "-->"
            continue
        special = re.match(r" {0,3}(<\?|<!\[CDATA\[|<![A-Z])", line)
        if special:
            paragraph = False
            closing = "?>" if special[1] == "<?" else "]]>" if special[1] == "<![CDATA[" else ">"
            if closing not in line:
                html_end = closing
            continue
        # CommonMark block tags interrupt paragraphs; standalone tags cannot.
        if re.match(rf" {{0,3}}</?(?:{HTML_BLOCK_TAGS})(?=[ \t]|/?>|$)", line, re.IGNORECASE) or (
            not paragraph and re.fullmatch(rf" {{0,3}}{HTML_TAG}[ \t]*", line)
        ):
            html_end = ""  # Ordinary HTML blocks end at the next blank line.
            paragraph = False
            continue
        heading = re.fullmatch(r"(#{1,2})(?:[ \t]+(.*?))?[ \t]*", line)
        if heading:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[2] or "").strip()
            headings.append((index, len(heading[1]), title))
        paragraph = bool(line.strip()) and not (
            re.match(r" {0,3}#{1,6}(?:[ \t]|$)", line)
            or re.fullmatch(r" {0,3}(?:-+|=+|(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})[ \t]*", line)
        )

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
