#!/usr/bin/env python3
"""Exact modular replay for the public secp256k1 n-torsion embedding degree.

The factorization of n-1 is the one recorded in notes/PRIMALITY.md. This file
checks its product and proves the exact order of p modulo n, conditional only on
the primality of the recorded factors. A separate downloadable recursive Lucas
certificate verifies those factor primality claims without probabilistic tests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FACTORS = {
    2: 6,
    3: 1,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    product = 1
    for prime, exponent in FACTORS.items():
        product *= prime**exponent
    if product != N - 1:
        raise AssertionError("n-1 factorization product mismatch")

    order = (N - 1) // 6
    if pow(P, order, N) != 1:
        raise AssertionError("candidate order does not annihilate p mod n")

    order_factors = dict(FACTORS)
    order_factors[2] -= 1
    order_factors[3] -= 1
    order_factors = {q: e for q, e in order_factors.items() if e}
    for prime in order_factors:
        if pow(P, order // prime, N) == 1:
            raise AssertionError("candidate order is not minimal")

    if pow(P, order // 2, N) != N - 1:
        raise AssertionError("half-order value is not -1")

    payload = {
        "curve": "secp256k1",
        "p": P,
        "n": N,
        "n_minus_one_factorization": FACTORS,
        "factorization_source": "notes/PRIMALITY.md",
        "embedding_degree": order,
        "embedding_degree_formula": "(n-1)/6",
        "embedding_degree_bit_length": order.bit_length(),
        "minimality_prime_divisor_checks": len(order_factors),
        "p_to_half_embedding_degree_mod_n": N - 1,
        "all_modular_checks_passed": True,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
