#!/usr/bin/env python3
"""Exact multiplicative-order replay for the secp256k1 pairing embedding degree.

The embedding degree of the prime-order subgroup is ord_n(p), the least positive k
such that n divides p^k-1.  This script verifies a complete factorization of n-1,
primality of every listed factor, and the standard order certificate:

    p^K = 1 mod n,
    p^(K/q) != 1 mod n for every prime q | K.

Thus ord_n(p)=K=(n-1)/6.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sympy import isprime

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

N_MINUS_ONE_FACTORS = {
    2: 6,
    3: 1,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}

EMBEDDING_DEGREE = (N - 1) // 6
EMBEDDING_FACTORS = {
    2: 5,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}


def product(factors: dict[int, int]) -> int:
    out = 1
    for prime, exponent in factors.items():
        out *= prime**exponent
    return out


def replay() -> dict[str, object]:
    assert isprime(N)
    assert product(N_MINUS_ONE_FACTORS) == N - 1
    assert product(EMBEDDING_FACTORS) == EMBEDDING_DEGREE
    assert all(isprime(q) for q in N_MINUS_ONE_FACTORS)

    terminal = pow(P, EMBEDDING_DEGREE, N)
    assert terminal == 1

    witnesses: dict[str, int] = {}
    for q in EMBEDDING_FACTORS:
        residue = pow(P, EMBEDDING_DEGREE // q, N)
        assert residue != 1
        witnesses[str(q)] = residue

    return {
        "profile_id": "UORC-056-SECP256K1-EMBEDDING-DEGREE",
        "status": "proved_by_exact_order_certificate",
        "p": P,
        "n": N,
        "n_minus_one_factorization": {str(q): e for q, e in N_MINUS_ONE_FACTORS.items()},
        "embedding_degree": EMBEDDING_DEGREE,
        "embedding_degree_bit_length": EMBEDDING_DEGREE.bit_length(),
        "embedding_degree_log2": math.log2(EMBEDDING_DEGREE),
        "embedding_degree_factorization": {str(q): e for q, e in EMBEDDING_FACTORS.items()},
        "certificate": {
            "p_to_K_mod_n": terminal,
            "p_to_K_over_q_mod_n": witnesses,
        },
        "conclusion": "ord_n(p)=(n-1)/6, so a finite-field pairing target containing mu_n needs extension degree K",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = replay()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
