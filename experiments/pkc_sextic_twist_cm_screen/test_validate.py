#!/usr/bin/env python3
"""Fault-injection tests for the sextic-twist CM replay validator."""

from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "pkc_sextic_twist_cm_validator",
    HERE / "validate.py",
)
if VALIDATOR_SPEC is None or VALIDATOR_SPEC.loader is None:
    raise RuntimeError("could not load sextic-twist validator")
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]


class ValidatorFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline: Document = json.loads(
            (HERE / "artifact.json").read_text(encoding="utf-8")
        )

    def replay(self, document: Document) -> None:
        encoded = validator.canonical_bytes(document)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "artifact.json").write_bytes(encoded)
            (root / "artifact.sha256").write_text(
                hashlib.sha256(encoded).hexdigest() + "\n",
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                validator.validate(root)

    def expect_rejected(self, mutation: Mutation, message: str) -> None:
        document = copy.deepcopy(self.baseline)
        mutation(document)
        with self.assertRaises(SystemExit) as raised:
            self.replay(document)
        self.assertIn(message, str(raised.exception))

    def test_committed_artifact_replays(self) -> None:
        self.replay(copy.deepcopy(self.baseline))

    def test_claim_boundary_is_semantic(self) -> None:
        self.expect_rejected(
            lambda document: document.__setitem__("claim_boundary", "broader claim"),
            "claim boundary drift",
        )

    def test_disposition_cannot_promote_route(self) -> None:
        self.expect_rejected(
            lambda document: document.__setitem__("disposition", "route_promoted"),
            "scientific disposition drift",
        )

    def test_experiment_authorization_cannot_be_enabled(self) -> None:
        self.expect_rejected(
            lambda document: document.__setitem__("experiments_authorized", True),
            "experiment authorization must remain false",
        )

    def test_smooth_log2_is_recomputed(self) -> None:
        self.expect_rejected(
            lambda document: document["smooth_part"].__setitem__("log2", "0.0"),
            "smooth-part log2 mismatch",
        )

    def test_smooth_factorization_is_not_self_certifying(self) -> None:
        def mutate(document: Document) -> None:
            factors = document["smooth_part"]["factorization"]
            factors["2"] += 1
            value = int(document["smooth_part"]["value"]) * 2
            document["smooth_part"]["value"] = str(value)
            document["smooth_part"]["log2"] = format(math.log2(value), ".15f")

        self.expect_rejected(mutate, "smooth-part factorization drift")

    def test_relation_log2_is_recomputed(self) -> None:
        self.expect_rejected(
            lambda document: document["relation_yield_screen"][0].__setitem__(
                "log2_divisor", "0.0"
            ),
            "relation-yield log2 divisor mismatch",
        )

    def test_hasse_bound_flag_is_recomputed(self) -> None:
        self.expect_rejected(
            lambda document: document["hasse_uniqueness_certificate"].__setitem__(
                "q_gt_four_sqrt_p", False
            ),
            "Hasse certificate flag drift",
        )

    def test_hasse_theorem_cannot_be_broadened(self) -> None:
        self.expect_rejected(
            lambda document: document["hasse_uniqueness_certificate"].__setitem__(
                "theorem", "This proves a useful ECDLP mechanism."
            ),
            "Hasse theorem statement drift",
        )

    def test_hasse_scalar_is_recomputed(self) -> None:
        self.expect_rejected(
            lambda document: document["hasse_uniqueness_certificate"].__setitem__(
                "q_squared", "1"
            ),
            "Hasse certificate field drift: q_squared",
        )

    def test_hasse_point_witness_is_recomputed(self) -> None:
        self.expect_rejected(
            lambda document: document["hasse_uniqueness_certificate"][
                "point_witnesses"
            ][0].__setitem__("cofactor_multiple_is_identity", True),
            "Hasse point witnesses drift",
        )


if __name__ == "__main__":
    unittest.main()
