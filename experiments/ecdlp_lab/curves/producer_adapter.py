"""Hash-frozen, bounded access to legacy P1 producer arithmetic.

Only arithmetic primitives are adapted.  The P1 catalog search and its
million-attempt point derivation are intentionally neither imported nor exposed.
All P02 search loops and their global counters live in ``generate_ci_catalog``.
"""

from __future__ import annotations

from math import isqrt
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import sha256_file
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import (
    Curve,
    candidate_orders_from_hasse_bsgs,
    derive_integer,
    glv_parameters,
    is_prime,
    prime_factors,
    tonelli_shanks,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
P1_ARITHMETIC_PATH = (
    REPO_ROOT / "experiments/ml_structure_probe/p1_toy_scaling/curve_math.py"
)
P1_ARITHMETIC_SHA256 = (
    "c18d954aa637198cfc43ce54819448cc41bc12678a00f4e8fa1ba8e9fc661dd2"
)


def verify_p1_arithmetic() -> None:
    """Fail closed if the audited producer dependency has changed."""

    if sha256_file(P1_ARITHMETIC_PATH) != P1_ARITHMETIC_SHA256:
        raise RuntimeError("frozen P1 curve arithmetic digest mismatch")


def certified_prime_full_order(curve: Curve, point: tuple[int, int]) -> int | None:
    """Return a Hasse-unique prime full order, or ``None``.

    A prime that merely annihilates a point is not enough.  The uniqueness
    inequality proves that no second positive multiple can lie in the Hasse
    interval, thereby identifying the full curve order.
    """

    hasse_upper = curve.p + 1 + isqrt(4 * curve.p)
    for order in candidate_orders_from_hasse_bsgs(curve, point):
        if (
            is_prime(order)
            and 2 * order > hasse_upper
            and curve.scalar_mul(order, point) is None
        ):
            return order
    return None


__all__ = [
    "Curve",
    "candidate_orders_from_hasse_bsgs",
    "certified_prime_full_order",
    "derive_integer",
    "glv_parameters",
    "is_prime",
    "prime_factors",
    "tonelli_shanks",
    "verify_p1_arithmetic",
]
