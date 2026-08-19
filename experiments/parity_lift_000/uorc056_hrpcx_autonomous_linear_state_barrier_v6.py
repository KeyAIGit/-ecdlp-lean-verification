#!/usr/bin/env python3
"""Exact arithmetic replay for the H-RPCX autonomous linear-state barrier V6.

The mathematical theorem is stated in the accompanying note. This program verifies
secp256k1's multiplicative-order certificate and instantiates the resulting state
dimension bounds. It also reports the same quantity on small toy instances whenever
the subgroup order differs from the field characteristic.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sympy import factorint, isprime

PROFILE_ID = "UORC-056-HRPCX-AUTONOMOUS-LINEAR-STATE-BARRIER-V6"

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

K = (N - 1) // 6
K_FACTORS = {
    2: 5,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}

TOY_INSTANCES = (
    ("toy-p43-n31", 43, 31),
    ("toy-p67-n79", 67, 79),
    ("toy-p79-n67", 79, 67),
    ("toy-p127-n127-anomalous", 127, 127),
    ("toy-p163-n139", 163, 139),
    ("heldout-p61-n61-anomalous", 61, 61),
    ("heldout-p211-n199", 211, 199),
    ("heldout-p991-n1009", 991, 1009),
    ("heldout-p2089-n2143", 2089, 2143),
)


def factor_product(factors: dict[int, int]) -> int:
    out = 1
    for prime, exponent in factors.items():
        out *= prime**exponent
    return out


def multiplicative_order_mod_prime(base: int, modulus: int) -> int:
    """Return ord_modulus(base), assuming modulus prime and base nonzero."""
    if not isprime(modulus):
        raise ValueError(("modulus must be prime", modulus))
    base %= modulus
    if base == 0:
        raise ValueError(("base is zero modulo modulus", base, modulus))
    order = modulus - 1
    for prime, exponent in factorint(order).items():
        for _ in range(exponent):
            if order % prime == 0 and pow(base, order // prime, modulus) == 1:
                order //= prime
            else:
                break
    if pow(base, order, modulus) != 1:
        raise AssertionError(("order verification failed", base, modulus, order))
    return int(order)


def secp_certificate() -> dict[str, object]:
    assert isprime(N)
    assert factor_product(N_MINUS_ONE_FACTORS) == N - 1
    assert factor_product(K_FACTORS) == K
    assert all(isprime(q) for q in N_MINUS_ONE_FACTORS)
    assert pow(P, K, N) == 1

    witnesses: dict[str, int] = {}
    for q in K_FACTORS:
        residue = pow(P, K // q, N)
        if residue == 1:
            raise AssertionError(("nonminimal embedding degree", q))
        witnesses[str(q)] = residue

    return {
        "p": P,
        "n": N,
        "embedding_degree": K,
        "embedding_degree_bit_length": K.bit_length(),
        "embedding_degree_log2": math.log2(K),
        "embedding_degree_factorization": {str(q): e for q, e in K_FACTORS.items()},
        "order_certificate": {
            "p_to_K_mod_n": pow(P, K, N),
            "p_to_K_over_q_mod_n": witnesses,
        },
        "state_lower_bounds": {
            "linear_state_over_Fp_dimension_at_least": K,
            "affine_state_over_Fp_dimension_at_least": K - 1,
            "mobius_state_extension_degree_at_least": (K + 1) // 2,
            "general_linear_state_over_Fp_to_d": "d*r >= K",
            "general_affine_state_over_Fp_to_d": "d*(r+1) >= K",
        },
    }


def toy_profile(name: str, p: int, n: int) -> dict[str, object]:
    if not isprime(p) or not isprime(n):
        raise AssertionError((name, "p and n must be prime"))
    if p == n:
        return {
            "name": name,
            "p": p,
            "n": n,
            "status": "excluded_anomalous_characteristic",
            "reason": "n=p, so p-primary unipotent or translation cycles are not governed by ord_n(p)",
        }
    order = multiplicative_order_mod_prime(p, n)
    return {
        "name": name,
        "p": p,
        "n": n,
        "status": "covered",
        "ord_n_p": order,
        "linear_dimension_lower_bound": order,
        "affine_dimension_lower_bound": order - 1,
        "mobius_extension_degree_lower_bound": (order + 1) // 2,
    }


def run() -> dict[str, object]:
    secp = secp_certificate()
    toys = [toy_profile(*item) for item in TOY_INSTANCES]
    covered = [item for item in toys if item["status"] == "covered"]
    excluded = [item for item in toys if item["status"] != "covered"]

    return {
        "profile_id": PROFILE_ID,
        "status": "proved_paper_theorem_with_exact_secp_order_certificate",
        "model": {
            "target": "exact canonical parity along an odd prime-order cycle",
            "state_update": "one fixed linear or affine map over F_(p^d)",
            "decoder": "arbitrary deterministic decoder",
            "required_behavior": "the state trace decodes the complete parity word exactly",
        },
        "paper_theorem": {
            "linear": "an r-dimensional linear state over F_(p^d) requires d*r >= ord_n(p)",
            "affine": "an r-dimensional affine state over F_(p^d) requires d*(r+1) >= ord_n(p)",
            "proof_route": [
                "exact parity on an odd cycle has no nontrivial rotational period",
                "therefore any deterministic exact state trace has an orbit of length n",
                "the cyclic linear subspace has an operator of order n",
                "a primitive n-th root over F_p has minimal-polynomial degree ord_n(p)",
            ],
        },
        "secp256k1": secp,
        "toy_profiles": toys,
        "aggregate": {
            "covered_instances": len(covered),
            "excluded_anomalous_instances": len(excluded),
            "minimum_covered_linear_bound": min(item["linear_dimension_lower_bound"] for item in covered),
            "maximum_covered_linear_bound": max(item["linear_dimension_lower_bound"] for item in covered),
        },
        "decision": {
            "polylog_dimension_fixed_linear_update_state_possible_for_secp256k1": False,
            "polylog_dimension_fixed_affine_update_state_possible_for_secp256k1": False,
            "arbitrary_nonlinear_decoder_changes_this_boundary": False,
            "nonlinear_coordinate_dependent_update_closed": False,
            "query_dependent_update_closed": False,
            "high_degree_low_DAG_size_direct_evaluator_closed": False,
            "general_HPCX_refuted": False,
        },
        "claim_boundary": {
            "proved": "fixed autonomous linear or affine update states require exponential base-field dimension on secp256k1",
            "not_proved": [
                "no polynomial-time parity algorithm exists",
                "no nonlinear state update works",
                "no direct arithmetic circuit works",
                "no CM, Miller, theta, or p-adic random-access evaluator works",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
