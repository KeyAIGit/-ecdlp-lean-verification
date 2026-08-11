#!/usr/bin/env python3
"""Toy-only structural checks for PARITY-LIFT-000.

No real curve, public key, wallet, or production-sized discrete-log instance is
accepted by this program. It validates identities in tiny odd cyclic groups.
"""
from __future__ import annotations

import cmath
import json
import math
from pathlib import Path

TOY_ODD_ORDERS = (3, 5, 7, 11, 13, 17, 19, 31, 43, 67, 101, 127)


def scalar_parity(k: int) -> int:
    return k & 1


def neg_scalar(n: int, k: int) -> int:
    return (-k) % n


def kummer_class(n: int, k: int) -> tuple[int, int]:
    """Toy quotient class identifying k and -k."""
    a = k % n
    b = (-a) % n
    return min(a, b), max(a, b)


def parity_peel(n: int, encoded_scalar: int) -> tuple[int, int]:
    """One exact parity-oracle reduction step in a tiny odd cyclic group."""
    if n not in TOY_ODD_ORDERS:
        raise ValueError("only the frozen toy orders are allowed")
    q = encoded_scalar % n
    bit = scalar_parity(q)
    next_q = (pow(2, -1, n) * (q - bit)) % n
    assert next_q == (q - bit) // 2
    return bit, next_q


def recover_toy(n: int, encoded_scalar: int) -> tuple[int, list[int]]:
    q = encoded_scalar % n
    bits: list[int] = []
    while q:
        bit, q = parity_peel(n, q)
        bits.append(bit)
    return sum(bit << i for i, bit in enumerate(bits)), bits


def verify_order(n: int) -> dict[str, object]:
    assert n in TOY_ODD_ORDERS

    for k in range(1, n):
        nk = neg_scalar(n, k)
        assert scalar_parity(nk) == 1 - scalar_parity(k)
        assert kummer_class(n, k) == kummer_class(n, nk)

    alternating = [0]
    for _ in range(n):
        alternating.append(1 - alternating[-1])
    assert alternating[n] != alternating[0]

    max_steps = 0
    for k in range(n):
        recovered, bits = recover_toy(n, k)
        assert recovered == k
        max_steps = max(max_steps, len(bits))

    coeffs = []
    for j in range(n):
        direct = sum(
            ((-1) ** k) * cmath.exp(-2j * math.pi * j * k / n)
            for k in range(n)
        )
        closed = 2 / (1 + cmath.exp(-2j * math.pi * j / n))
        assert abs(direct - closed) < 1e-8 * max(1.0, abs(closed))
        assert abs(closed) > 0
        coeffs.append(abs(closed))

    return {
        "n": n,
        "negation_complement_checked": n - 1,
        "kummer_collision_witness": {
            "k": 1,
            "minus_k": n - 1,
            "same_class": list(kummer_class(n, 1)),
            "parities": [1, 0],
        },
        "global_alternation_closes": False,
        "all_toy_scalars_recovered": n,
        "maximum_oracle_calls": max_steps,
        "fourier_nonzero_coefficients": n,
        "largest_fourier_coefficient": max(coeffs),
    }


def main() -> None:
    payload = {
        "scope": "frozen tiny odd cyclic groups only",
        "theorems_screened": [
            "scalarParity_neg",
            "scalarParity_not_factor_through_Kummer",
            "no_global_alternating_translation_observable",
            "parityOracle_recovers_dlog",
            "parity_fourier_has_full_support",
        ],
        "toy_odd_orders": [verify_order(n) for n in TOY_ODD_ORDERS],
        "claim_boundary": [
            "Arithmetic identity checks are not evidence that a parity oracle exists.",
            "No production-sized group or external public key is accepted.",
            "The general proofs are recorded separately in notes/PARITY_LIFT_000.md.",
        ],
    }
    out = Path(__file__).with_name("parity_lift_000_results.json")
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
