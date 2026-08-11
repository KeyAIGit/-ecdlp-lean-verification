from __future__ import annotations

import hashlib
import unittest

from experiments.ecdlp_lab.core.canonical import (
    StrictJSONError,
    canonical_json_bytes,
    derive_id,
    sha256_json,
    strict_loads,
)


class CanonicalJSONTests(unittest.TestCase):
    def test_canonical_bytes_are_a_fixpoint(self) -> None:
        value = {"é": "雪", "z": [3, 2, 1], "a": True}
        encoded = canonical_json_bytes(value)
        self.assertEqual(encoded, '{"a":true,"z":[3,2,1],"é":"雪"}'.encode())
        self.assertEqual(canonical_json_bytes(strict_loads(encoded)), encoded)
        self.assertEqual(sha256_json(value), hashlib.sha256(encoded).hexdigest())

    def test_semantic_id_excludes_its_self_reference(self) -> None:
        first = {"work_unit_id": "old", "curve": "toy", "seed": 7}
        second = {"work_unit_id": "different", "curve": "toy", "seed": 7}
        first_id = derive_id("WU-", first, excluded=("work_unit_id",))
        self.assertEqual(first_id, derive_id("WU-", second, excluded=("work_unit_id",)))
        self.assertRegex(first_id, r"^WU-[0-9A-F]{32}$")

    def test_duplicate_keys_are_rejected_before_decoding(self) -> None:
        with self.assertRaisesRegex(StrictJSONError, "duplicate JSON key"):
            strict_loads('{"record_kind":"first","record_kind":"second"}')

    def test_nonfinite_numbers_are_rejected(self) -> None:
        for literal in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(literal=literal):
                with self.assertRaisesRegex(StrictJSONError, "non-finite"):
                    strict_loads('{"value":' + literal + "}")

    def test_json_floats_are_rejected(self) -> None:
        for literal in ("1.0", "1e0", "-0.0"):
            with self.subTest(literal=literal):
                with self.assertRaisesRegex(StrictJSONError, "floating-point"):
                    strict_loads('{"value":' + literal + "}")

    def test_integer_negative_zero_is_rejected(self) -> None:
        with self.assertRaisesRegex(StrictJSONError, "negative zero"):
            strict_loads('{"value":-0}')

    def test_in_memory_floats_cannot_enter_hashed_bytes(self) -> None:
        for value in (1.25, float("nan"), float("inf"), -0.0):
            with self.subTest(value=value):
                with self.assertRaisesRegex(StrictJSONError, "floating-point"):
                    canonical_json_bytes({"value": value})


if __name__ == "__main__":
    unittest.main()
