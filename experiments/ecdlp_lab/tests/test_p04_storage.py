from __future__ import annotations

import concurrent.futures
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.orchestration import storage
from experiments.ecdlp_lab.orchestration.storage import (
    ArtifactCorrupt,
    ArtifactExists,
    ArtifactStore,
    StorageError,
    StorageUnavailable,
    WriterLockBusy,
)


@unittest.skipUnless(
    storage.storage_primitives_available(),
    "safe POSIX dirfd/flock storage primitives required",
)
class P04ArtifactStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "artifacts"
        self.store = ArtifactStore(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_create_only_canonical_json_and_digest_bound_read(self) -> None:
        value = {"z": [3, 2, 1], "a": {"ok": True}}
        retained = self.store.create_json("receipts/one.json", value)
        expected = b'{"a":{"ok":true},"z":[3,2,1]}'
        self.assertEqual((self.root / retained.relative_path).read_bytes(), expected)
        self.assertEqual(retained.sha256, hashlib.sha256(expected).hexdigest())
        self.assertEqual(retained.size_bytes, len(expected))
        self.assertEqual(
            self.store.read_json(
                retained.relative_path,
                expected_sha256=retained.sha256,
            ),
            value,
        )
        self.assertEqual(
            sorted(path.name for path in (self.root / "receipts").iterdir()),
            ["one.json"],
        )

    def test_duplicate_create_never_replaces_first_value(self) -> None:
        first = self.store.create_bytes("receipts/fixed.bin", b"first")
        with self.assertRaises(ArtifactExists):
            self.store.create_bytes("receipts/fixed.bin", b"second")
        self.assertEqual(
            self.store.read_bytes(
                "receipts/fixed.bin", expected_sha256=first.sha256
            ),
            b"first",
        )

    def test_concurrent_create_has_one_semantic_winner(self) -> None:
        contenders = (b"alpha", b"beta")

        def retain(payload: bytes):
            try:
                return self.store.create_bytes("races/unit.json", payload)
            except ArtifactExists as error:
                return error

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = tuple(executor.map(retain, contenders))
        winners = [
            outcome for outcome in outcomes if not isinstance(outcome, Exception)
        ]
        losers = [
            outcome for outcome in outcomes if isinstance(outcome, ArtifactExists)
        ]
        self.assertEqual(len(winners), 1, outcomes)
        self.assertEqual(len(losers), 1, outcomes)
        retained = self.store.read_bytes("races/unit.json")
        self.assertIn(retained, contenders)
        self.assertEqual(winners[0].sha256, hashlib.sha256(retained).hexdigest())

    def test_path_traversal_noncanonical_and_reserved_paths_are_rejected(self) -> None:
        invalid = (
            "",
            "/absolute",
            "../escape",
            "a/../escape",
            "a/./file",
            "a//file",
            "a\\file",
            ".locks/forged",
            "nested/.locks/forged",
        )
        for relative_path in invalid:
            with self.subTest(relative_path=relative_path):
                with self.assertRaises(StorageError):
                    self.store.create_bytes(relative_path, b"x")
        self.assertFalse((self.base / "escape").exists())

    def test_symlink_parent_and_final_component_never_escape(self) -> None:
        outside = self.base / "outside"
        outside.mkdir()
        linked_parent = self.root / "linked-parent"
        try:
            linked_parent.symlink_to(outside, target_is_directory=True)
        except OSError as error:  # pragma: no cover - unusual POSIX mount policy.
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaises(StorageError):
            self.store.create_bytes("linked-parent/escape", b"owned")
        self.assertFalse((outside / "escape").exists())

        outside_file = outside / "target"
        outside_file.write_bytes(b"outside")
        (self.root / "linked-file").symlink_to(outside_file)
        with self.assertRaises(ArtifactExists):
            self.store.create_bytes("linked-file", b"replacement")
        with self.assertRaises(StorageError):
            self.store.read_bytes("linked-file")
        self.assertEqual(outside_file.read_bytes(), b"outside")

    def test_symlink_root_is_rejected(self) -> None:
        real = self.base / "real-root"
        real.mkdir()
        linked = self.base / "linked-root"
        try:
            linked.symlink_to(real, target_is_directory=True)
        except OSError as error:  # pragma: no cover - unusual POSIX mount policy.
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaises(StorageError):
            ArtifactStore(linked)

    def test_replaced_root_identity_is_rejected(self) -> None:
        original = self.base / "original-root"
        replacement = self.base / "replacement-root"
        identity_bound = ArtifactStore(original)
        original.rename(self.base / "moved-root")
        replacement.mkdir()
        replacement.rename(original)
        with self.assertRaises(StorageError):
            identity_bound.create_bytes("must-not-land", b"x")
        self.assertFalse((original / "must-not-land").exists())

    def test_hardlinked_or_digest_mismatched_artifact_is_rejected(self) -> None:
        original = self.root / "original"
        original.write_bytes(b"payload")
        os.link(original, self.root / "second-link")
        with self.assertRaises(ArtifactCorrupt):
            self.store.read_bytes("original")

        safe = self.store.create_bytes("safe", b"safe")
        wrong = "0" * 64
        self.assertNotEqual(wrong, safe.sha256)
        with self.assertRaises(ArtifactCorrupt):
            self.store.read_bytes("safe", expected_sha256=wrong)
        with self.assertRaises(StorageError):
            self.store.read_bytes("safe", expected_sha256="A" * 64)

    def test_noncanonical_torn_and_oversized_json_fail_closed(self) -> None:
        (self.root / "spaced.json").write_bytes(b'{"a": 1}')
        with self.assertRaises(ArtifactCorrupt):
            self.store.read_json("spaced.json")
        (self.root / "torn.json").write_bytes(b'{"a":')
        with self.assertRaises(ArtifactCorrupt):
            self.store.read_json("torn.json")

        bounded = ArtifactStore(self.root, max_artifact_bytes=3)
        (self.root / "large").write_bytes(b"four")
        with self.assertRaises(ArtifactCorrupt):
            bounded.read_bytes("large")
        with self.assertRaises(StorageError):
            bounded.create_bytes("too-large", b"four")

    def test_writer_lock_is_nonblocking_and_name_is_bounded(self) -> None:
        with self.store.writer_lock("campaign"):
            with self.assertRaises(WriterLockBusy):
                with self.store.writer_lock("campaign"):
                    self.fail("a second writer acquired the same lock")
        with self.store.writer_lock("campaign"):
            pass
        for invalid in ("", "Upper", "../escape", "x" * 65):
            with self.subTest(name=invalid):
                with self.assertRaises(StorageError):
                    with self.store.writer_lock(invalid):
                        pass

    def test_jsonl_append_is_canonical_locked_fsynced_and_torn_safe(self) -> None:
        first = self.store.append_jsonl(
            "logs/events.jsonl", {"z": 2, "a": 1}, lock_name="events"
        )
        second = self.store.append_jsonl(
            "logs/events.jsonl", {"sequence": 1}, lock_name="events"
        )
        expected_first = b'{"a":1,"z":2}\n'
        expected_second = b'{"sequence":1}\n'
        self.assertEqual(first.offset, 0)
        self.assertEqual(first.size_bytes, len(expected_first))
        self.assertEqual(first.sha256, hashlib.sha256(expected_first).hexdigest())
        self.assertEqual(second.offset, len(expected_first))
        self.assertEqual(
            (self.root / "logs/events.jsonl").read_bytes(),
            expected_first + expected_second,
        )

        (self.root / "logs/torn.jsonl").write_bytes(b'{"sequence":0}')
        with self.assertRaises(ArtifactCorrupt):
            self.store.append_jsonl(
                "logs/torn.jsonl", {"sequence": 1}, lock_name="torn"
            )
        self.assertEqual(
            (self.root / "logs/torn.jsonl").read_bytes(), b'{"sequence":0}'
        )

    def test_log_limits_and_exact_types_are_rejected(self) -> None:
        bounded = ArtifactStore(
            self.root,
            max_log_bytes=32,
            max_log_record_bytes=16,
        )
        with self.assertRaises(StorageError):
            bounded.append_jsonl("log", {"padding": "x" * 32}, lock_name="log")
        bounded.append_jsonl("log", {"x": 1}, lock_name="log")
        with self.assertRaises(StorageError):
            while True:
                bounded.append_jsonl("log", {"x": 1}, lock_name="log")
        with self.assertRaises(StorageError):
            ArtifactStore(self.root, max_artifact_bytes=True)
        with self.assertRaises(StorageError):
            self.store.create_bytes("bad-type", bytearray(b"x"))


class P04StorageAvailabilityTests(unittest.TestCase):
    def test_missing_flock_or_dirfd_primitives_fail_before_storage_use(self) -> None:
        with tempfile.TemporaryDirectory() as raw, patch.object(
            storage, "_fcntl", None
        ):
            with self.assertRaises(StorageUnavailable):
                ArtifactStore(Path(raw) / "artifacts")


if __name__ == "__main__":
    unittest.main()
