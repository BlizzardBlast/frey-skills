"""Fault injection for local publication, rollback, and concurrent publishers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.publish_outputs import publish_outputs


class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.staging = self.root / "staging"
        self.staging.mkdir()
        self.targets = tuple(self.root / name for name in ("archive.zip", "notes.md", "SHA256SUMS"))
        for target in self.targets:
            target.write_bytes(b"old " + target.name.encode())
            (self.staging / target.name).write_bytes(b"new " + target.name.encode())

    def test_success_replaces_complete_set_and_preserves_unrelated_files(self) -> None:
        unrelated = self.root / "unrelated"
        unrelated.write_bytes(b"keep")
        publish_outputs(self.staging, self.targets, replace=True)
        for target in self.targets:
            self.assertEqual(target.read_bytes(), b"new " + target.name.encode())
        self.assertEqual(unrelated.read_bytes(), b"keep")
        self.assertFalse((self.root / ".frey-publish").exists())

    def test_failure_at_each_backup_or_publication_rename_restores_complete_set(self) -> None:
        original = Path.rename
        for fail_at in range(1, 7):
            with self.subTest(rename=fail_at):
                calls = 0

                def fail_once(source: Path, destination: Path) -> Path:
                    nonlocal calls
                    calls += 1
                    if calls == fail_at:
                        raise PermissionError("injected rename failure")
                    return original(source, destination)

                with mock.patch.object(Path, "rename", fail_once), self.assertRaises(PermissionError):
                    publish_outputs(self.staging, self.targets, replace=True)
                for target in self.targets:
                    self.assertEqual(target.read_bytes(), b"old " + target.name.encode())
                    self.assertEqual((self.staging / target.name).read_bytes(), b"new " + target.name.encode())
                self.assertFalse((self.root / ".frey-publish").exists())

    def test_failed_first_publication_leaves_no_partial_artifact_set(self) -> None:
        for target in self.targets:
            target.unlink()
        original = Path.rename

        def fail_checksum(source: Path, destination: Path) -> Path:
            if source == self.staging / "SHA256SUMS":
                raise PermissionError("injected final publication failure")
            return original(source, destination)

        with mock.patch.object(Path, "rename", fail_checksum), self.assertRaises(PermissionError):
            publish_outputs(self.staging, self.targets, replace=True)
        self.assertFalse(any(target.exists() for target in self.targets))

    def test_failed_rollback_retains_backups_and_blocks_another_publication(self) -> None:
        original = Path.rename

        def fail_publication_and_restore(source: Path, destination: Path) -> Path:
            if destination == self.targets[0]:
                raise PermissionError("injected publication and rollback failure")
            return original(source, destination)

        with mock.patch.object(Path, "rename", fail_publication_and_restore):
            with self.assertRaisesRegex(OSError, "rollback incomplete.*frey-publish"):
                publish_outputs(self.staging, self.targets, replace=True)
        previous = self.root / ".frey-publish" / "previous"
        self.assertEqual((previous / "archive.zip").read_bytes(), b"old archive.zip")
        with self.assertRaisesRegex(OSError, "recovery required"):
            publish_outputs(self.staging, self.targets, replace=True)

    def test_nonforced_publication_preserves_an_existing_target(self) -> None:
        with self.assertRaises(FileExistsError):
            publish_outputs(self.staging, self.targets, replace=False)
        self.assertEqual(self.targets[0].read_bytes(), b"old archive.zip")

    def test_existing_publication_lock_preserves_all_outputs(self) -> None:
        (self.root / ".frey-publish").mkdir()
        with self.assertRaisesRegex(OSError, "publication active"):
            publish_outputs(self.staging, self.targets, replace=True)
        for target in self.targets:
            self.assertEqual(target.read_bytes(), b"old " + target.name.encode())

    def test_interruption_retains_originals_for_manual_recovery(self) -> None:
        original = Path.rename

        def interrupt_publication(source: Path, destination: Path) -> Path:
            if source.parent == self.staging:
                raise KeyboardInterrupt()
            return original(source, destination)

        with mock.patch.object(Path, "rename", interrupt_publication), self.assertRaises(KeyboardInterrupt):
            publish_outputs(self.staging, self.targets, replace=True)
        for target in self.targets:
            self.assertEqual((self.root / ".frey-publish" / "previous" / target.name).read_bytes(),
                             b"old " + target.name.encode())

    def test_cleanup_failure_reports_published_set_and_keeps_recovery_backups(self) -> None:
        with mock.patch("scripts.publish_outputs.shutil.rmtree", side_effect=PermissionError("inert cleanup failure")):
            with self.assertRaisesRegex(OSError, "published outputs; previous-output cleanup required"):
                publish_outputs(self.staging, self.targets, replace=True)
        for target in self.targets:
            self.assertEqual(target.read_bytes(), b"new " + target.name.encode())
            self.assertEqual((self.root / ".frey-publish" / "previous" / target.name).read_bytes(),
                             b"old " + target.name.encode())


if __name__ == "__main__":
    unittest.main()
