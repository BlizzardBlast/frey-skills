#!/usr/bin/env python3
"""Check the pinned published plugin in a disposable directory (network opt-in)."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
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
from multiprocessing.connection import Connection
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


def _require_https(url: str) -> None:
    if urllib.parse.urlsplit(url).scheme != "https":
        raise ReleaseSmokeError("release downloads must remain on HTTPS")


class _HTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _require_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _download_file(url: str, destination: Path, limit: int) -> None:
    """Stream one asset; the supervising parent owns the total deadline."""
    _require_https(url)
    opener = urllib.request.build_opener(_HTTPSRedirectHandler())
    request = urllib.request.Request(url, headers={"User-Agent": "frey-skills-release-smoke"})
    with opener.open(request, timeout=30) as response, destination.open("xb") as output:
        _require_https(response.geturl())
        size = 0
        while True:
            chunk = response.read(min(64 * 1024, limit - size + 1))
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise ReleaseSmokeError("release download exceeded its size limit")
            output.write(chunk)


def _download_worker(url: str, destination: Path, limit: int, result: Connection) -> None:
    try:
        _download_file(url, destination, limit)
    except Exception as exc:
        # Keep the status smaller than a pipe buffer so join cannot wait on send.
        # Transport failures cross this process boundary as bounded diagnostic data.
        result.send(f"{type(exc).__name__}: {exc}"[:512])
    else:
        result.send(None)
    finally:
        result.close()


def download(url: str, destination: Path, limit: int, *, timeout: float = 60) -> None:
    """Enforce a total network deadline, then publish only a completed asset."""
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"download destination already exists: {destination}")
    # Spawn is portable and avoids forking a process that uses macOS proxy APIs.
    context = multiprocessing.get_context("spawn")
    deadline = time.monotonic() + timeout
    with tempfile.TemporaryDirectory(prefix=".release-download-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "asset"
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(target=_download_worker, args=(url, staged, limit, sender))
        try:
            process.start()
            sender.close()
            process.join(timeout=max(0, deadline - time.monotonic()))
            if process.is_alive() or time.monotonic() > deadline:
                raise ReleaseSmokeError("release download exceeded its time limit")
            if process.exitcode != 0:
                raise ReleaseSmokeError("release download worker failed without a result")
            try:
                if not receiver.poll():
                    raise ReleaseSmokeError("release download worker failed without a result")
                error = receiver.recv()
            except (EOFError, OSError) as exc:
                raise ReleaseSmokeError("release download worker failed without a result") from exc
            if error is not None:
                raise ReleaseSmokeError(error)
            with staged.open("rb") as source, destination.open("xb") as output:
                shutil.copyfileobj(source, output)
        finally:
            sender.close()
            receiver.close()
            if process.pid is not None:
                if process.is_alive():
                    process.kill()
                process.join(timeout=5)
                if process.is_alive():
                    raise ReleaseSmokeError("release download worker cleanup did not complete")
                process.close()


def expected_files(source: Path, *, tag: str | None = None) -> dict[str, bytes]:
    """Read the pinned sources as data; never execute downloaded helpers."""
    manifest_path = source / "plugin-template" / ".codex-plugin" / "plugin.json"
    license_path = source / "LICENSE"
    for path in (manifest_path, license_path):
        validate_source_path(path, source)
        if not path.is_file():
            raise ReleaseSmokeError(f"missing regular source file: {path.name}")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict) or manifest.get("version") != (tag or SOURCE_TAG).removeprefix("v"):
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


def clone_source(workspace: Path, environment: dict[str, str], *, tag: str | None = None, commit: str | None = None) -> Path:
    source = workspace / "source"
    # text=auto otherwise uses native CRLF on Windows even with autocrlf=false.
    run([
        "git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "clone", "--depth", "1", "--branch", tag or SOURCE_TAG,
        REPOSITORY_URL, str(source),
    ], workspace, environment)
    if run(["git", "rev-parse", "HEAD"], source, environment) != (commit or SOURCE_COMMIT):
        raise ReleaseSmokeError("release tag no longer matches its pinned commit")
    return source


def verify_archive(archive: Path, checksums: Path, source: Path, destination: Path, *, tag: str | None = None) -> str:
    """Validate all entries before writing only expected regular files."""
    if archive.stat().st_size > MAX_ARCHIVE_BYTES or checksums.stat().st_size > MAX_CHECKSUM_BYTES:
        raise ReleaseSmokeError("release assets exceeded their size limits")
    archive_name = f"frey-skills-{tag.removeprefix('v')}.zip" if tag else ARCHIVE_NAME
    checksum = re.fullmatch(
        rf"([0-9a-fA-F]{{64}})  {re.escape(archive_name)}\r?\n?",
        checksums.read_bytes().decode("utf-8"),
    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if checksum is None or checksum.group(1).lower() != digest:
        raise ReleaseSmokeError("SHA256SUMS does not match the pinned archive")
    expected = expected_files(source, tag=tag)
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
