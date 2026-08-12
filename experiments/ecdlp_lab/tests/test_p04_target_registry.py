from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.target_registry import (
    PRIVATE_TARGET_PATH,
    PRIVATE_TARGET_VECTOR_SHA256,
    PUBLIC_TARGET_PATH,
    PUBLIC_TARGET_VECTOR_SHA256,
    TargetRegistryError,
    known_target_vector_sha256s,
    load_target_pair,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


class P04TargetRegistryTests(unittest.TestCase):
    def test_fixed_pair_is_byte_and_semantically_authorized(self) -> None:
        pair = load_target_pair(repo_root=REPO_ROOT)
        self.assertEqual(pair.public_target_vector_sha256, PUBLIC_TARGET_VECTOR_SHA256)
        self.assertEqual(pair.private_target_vector_sha256, PRIVATE_TARGET_VECTOR_SHA256)
        self.assertEqual(
            pair.private_payload["public_target_vector_sha256"],
            pair.public_target_vector_sha256,
        )
        self.assertEqual(pair.private_payload["expected_scalar"], 1)
        self.assertEqual(pair.public_payload["target"], pair.public_payload["generator"])
        self.assertEqual(
            known_target_vector_sha256s(), frozenset({PUBLIC_TARGET_VECTOR_SHA256})
        )

    def test_records_are_copy_out_and_private_identity_is_not_campaign_authority(self) -> None:
        pair = load_target_pair(repo_root=REPO_ROOT)
        public = pair.public_record
        private = pair.private_record
        public["public_payload"]["target"][0] = 0
        private["private_payload"]["expected_scalar"] = 2
        self.assertEqual(pair.public_payload["target"][0], 3665)
        self.assertEqual(pair.private_payload["expected_scalar"], 1)
        self.assertNotIn(PRIVATE_TARGET_VECTOR_SHA256, known_target_vector_sha256s())

    def test_raw_drift_is_rejected_before_target_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (PUBLIC_TARGET_PATH, PRIVATE_TARGET_PATH):
                source = REPO_ROOT.joinpath(*relative.split("/"))
                destination = root.joinpath(*relative.split("/"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            public = root.joinpath(*PUBLIC_TARGET_PATH.split("/"))
            public.write_bytes(public.read_bytes() + b"\n")
            with self.assertRaisesRegex(TargetRegistryError, "raw target bytes drifted"):
                load_target_pair(repo_root=root)

    def test_fixed_target_locator_rejects_symlink_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            public = root.joinpath(*PUBLIC_TARGET_PATH.split("/"))
            public.parent.mkdir(parents=True, exist_ok=True)
            outside_file = Path(outside) / "target.json"
            shutil.copy2(REPO_ROOT.joinpath(*PUBLIC_TARGET_PATH.split("/")), outside_file)
            try:
                public.symlink_to(outside_file)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks unavailable: {error}")
            with self.assertRaises(TargetRegistryError):
                load_target_pair(repo_root=root)


if __name__ == "__main__":
    unittest.main()
