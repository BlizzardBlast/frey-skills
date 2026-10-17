#!/usr/bin/env python3
"""Check the pinned published plugin in a disposable directory (network opt-in)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

try:
    from scripts.build_plugin import BuildError, iter_files, reject_symlinks
    from scripts.repository_layout import discover_skill_names, validate_source_path
    from scripts.smoke_install import REPOSITORY_URL, SOURCE_COMMIT, SOURCE_TAG, isolated_environment, run
    from scripts.validate_plugin_bundle import validate_manifest
except ModuleNotFoundError:
    from build_plugin import BuildError, iter_files, reject_symlinks
    from repository_layout import discover_skill_names, validate_source_path
    from smoke_install import REPOSITORY_URL, SOURCE_COMMIT, SOURCE_TAG, isolated_environment, run
    from validate_plugin_bundle import validate_manifest


ARCHIVE_NAME = f"frey-skills-{SOURCE_TAG.removeprefix('v')}.zip"
RELEASE_URL = f"{REPOSITORY_URL}/releases/download/{SOURCE_TAG}"
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_CHECKSUM_BYTES = 16 * 1024


class ReleaseSmokeError(ValueError):
    """The downloaded release differs from its pinned canonical sources."""


def download(url: str, destination: Path, limit: int) -> None:
    """Bound each public download by size, socket timeout, and elapsed time."""
    request = urllib.request.Request(url, headers={"User-Agent": "frey-skills-release-smoke"})
    deadline = time.monotonic() + 60
    with urllib.request.urlopen(request, timeout=30) as response, destination.open("xb") as output:
        if urllib.parse.urlsplit(response.geturl()).scheme != "https":
            raise ReleaseSmokeError("release downloads must remain on HTTPS")
        size = 0
        while True:
            chunk = response.read(min(64 * 1024, limit - size + 1))
            if time.monotonic() > deadline:
                raise ReleaseSmokeError("release download exceeded its time limit")
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise ReleaseSmokeError("release download exceeded its size limit")
            output.write(chunk)


def expected_files(source: Path) -> dict[str, bytes]:
    """Read the pinned sources as data; never execute downloaded helpers."""
    manifest_path = source / "plugin-template" / ".codex-plugin" / "plugin.json"
    license_path = source / "LICENSE"
    for path in (manifest_path, license_path):
        validate_source_path(path, source)
        if not path.is_file():
            raise ReleaseSmokeError(f"missing regular source file: {path.name}")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict) or manifest.get("version") != SOURCE_TAG.removeprefix("v"):
        raise ReleaseSmokeError("source manifest version does not match the pinned release")
    errors: list[str] = []
    validate_manifest(manifest, errors)
    if errors:
        raise ReleaseSmokeError("invalid source manifest: " + "; ".join(errors))
    names = discover_skill_names(source)
    if not names:
        raise ReleaseSmokeError("no canonical skills found in the pinned source")
    expected = {
        "LICENSE": license_path.read_bytes(),
        "frey-skills/.codex-plugin/plugin.json": manifest_bytes,
    }
    for name in names:
        skill = source / name
        reject_symlinks(skill)
        for path in iter_files(skill):
            expected[f"frey-skills/skills/{path.relative_to(source).as_posix()}"] = path.read_bytes()
    return expected


def clone_source(workspace: Path, environment: dict[str, str]) -> Path:
    source = workspace / "source"
    # text=auto otherwise uses native CRLF on Windows even with autocrlf=false.
    run([
        "git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "clone", "--depth", "1", "--branch", SOURCE_TAG,
        REPOSITORY_URL, str(source),
    ], workspace, environment)
    if run(["git", "rev-parse", "HEAD"], source, environment) != SOURCE_COMMIT:
        raise ReleaseSmokeError("release tag no longer matches its pinned commit")
    return source


def verify_archive(archive: Path, checksums: Path, source: Path, destination: Path) -> str:
    """Validate all entries before writing only expected regular files."""
    if archive.stat().st_size > MAX_ARCHIVE_BYTES or checksums.stat().st_size > MAX_CHECKSUM_BYTES:
        raise ReleaseSmokeError("release assets exceeded their size limits")
    checksum = re.fullmatch(
        rf"([0-9a-fA-F]{{64}})  {re.escape(ARCHIVE_NAME)}\r?\n?",
        checksums.read_bytes().decode("utf-8"),
    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if checksum is None or checksum.group(1).lower() != digest:
        raise ReleaseSmokeError("SHA256SUMS does not match the pinned archive")
    expected = expected_files(source)
    contents = {}
    with zipfile.ZipFile(archive) as packaged:
        entries = packaged.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ReleaseSmokeError("archive file set differs from the pinned source (missing, extra, or duplicate entries)")
        for entry in entries:
            # An exact source allowlist excludes traversal, absolute paths, alternate
            # separators, unexpected directories, caches, and Windows drive/ADS paths.
            mode = entry.external_attr >> 16
            if entry.orig_filename != entry.filename or stat.S_IFMT(mode) not in (0, stat.S_IFREG) or entry.flag_bits & 1:
                raise ReleaseSmokeError("archive must contain only unencrypted regular files")
            if entry.file_size != len(expected[entry.filename]):
                raise ReleaseSmokeError(f"archive file size differs from pinned source: {entry.filename}")
        for entry in entries:
            content = packaged.read(entry)
            if content != expected[entry.filename]:
                raise ReleaseSmokeError(f"archive bytes differ from pinned source: {entry.filename}")
            contents[entry.filename] = content
    destination = destination.absolute()
    if destination.resolve() != destination:
        raise ReleaseSmokeError("extraction destination must not traverse a symlink or junction")
    destination.mkdir()  # Require a fresh directory; preserve any existing destination.
    for name, content in contents.items():
        target = destination.joinpath(*name.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(content)
    return digest


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    try:
        if not shutil.which("git"):
            raise ReleaseSmokeError("Git is required for the pinned source check")
        with tempfile.TemporaryDirectory(prefix="frey release café ") as temporary:
            workspace = Path(temporary).resolve()
            home_dir = workspace / "home"
            home_dir.mkdir()
            environment = isolated_environment(home_dir)
            source = clone_source(workspace, environment)
            archive, checksums = workspace / ARCHIVE_NAME, workspace / "SHA256SUMS"
            download(f"{RELEASE_URL}/SHA256SUMS", checksums, MAX_CHECKSUM_BYTES)
            download(f"{RELEASE_URL}/{ARCHIVE_NAME}", archive, MAX_ARCHIVE_BYTES)
            destination = workspace / "extracted"
            digest = verify_archive(archive, checksums, source, destination)
            names = discover_skill_names(destination / "frey-skills" / "skills")
            print(f"Verified {SOURCE_TAG} at {SOURCE_COMMIT}: {len(names)} skills, manifest, LICENSE, and supporting-file byte parity.")
            print(f"SHA256: {digest}  {ARCHIVE_NAME}")
        print("Published plugin smoke check passed. Agent discovery and behavioral model evals were not run.")
        return 0
    except (OSError, ValueError, RuntimeError, BuildError, subprocess.SubprocessError, zipfile.BadZipFile, zlib.error) as exc:
        print(f"smoke_release.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
