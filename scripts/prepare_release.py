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
from pathlib import Path

try:
    from scripts.validate_plugin_bundle import validate_bundle
except ModuleNotFoundError:
    from validate_plugin_bundle import validate_bundle


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def prepare_release(tag: str) -> tuple[Path, Path, Path]:
    root = REPOSITORY_ROOT.resolve()
    manifest = json.loads((root / "plugin-template" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise ValueError("the plugin manifest must have a stable semantic version")
    if tag != f"v{version}":
        raise ValueError(f"tag must match the plugin manifest: v{version}")

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}\s*\n(.*?)(?=^## |\Z)", changelog, re.MULTILINE | re.DOTALL)
    if match is None or not match.group(1).strip():
        raise ValueError(f"CHANGELOG.md needs a non-empty dated section for {version}")

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
            for path in sorted(bundle.rglob("*")) if path.is_file()
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
            (match.group(1).strip() + "\n\nDeterministic validation only; behavioral model evals were not run and no model-behavior certification is claimed.\n").encode("utf-8")
        )
        (staging / checksums.name).write_bytes(f"{digest}  {archive.name}\n".encode("utf-8"))
        for target in (archive, notes, checksums):
            (staging / target.name).replace(target)
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
