#!/usr/bin/env python3
"""Exact secp256k1 source-rank defect certificate for UORC-056 C31A.

C31 proves characteristic-zero half-source rank `(n-1)/2` and finds full rank
on five frozen base fields.  C31A checks the actual secp256k1 constants and
proves a finite-characteristic exception: both 2 modulo the subgroup order n
and 2 modulo the field prime p have exact order `(n-1)/2`.  Consequently the
multiplicative source spectrum has exactly two explicitly forced odd character
zeros, so the secp256k1 half-source matrix has nullity at least two.

The package does not prove that the nullity is exactly two.  Additional zeros
would be governed by the remaining odd character sums.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import sympy as sp

PROFILE_ID = "UORC-056-SECP-SOURCE-DEFECT-C31A"
DEFAULT_OUTPUT = Path("/tmp/uorc056_secp_source_defect_result.json")
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def payload_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("digest", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def exact_order_prime_modulus(value: int, modulus: int) -> tuple[int, dict[int, int]]:
    if not sp.isprime(modulus):
        raise ValueError("modulus must be prime")
    factors = {int(q): int(e) for q, e in sp.factorint(modulus - 1).items()}
    order = modulus - 1
    for prime, exponent in factors.items():
        for _ in range(exponent):
            if order % prime == 0 and pow(value, order // prime, modulus) == 1:
                order //= prime
            else:
                break
    if pow(value, order, modulus) != 1:
        raise AssertionError("computed order does not annihilate the element")
    for prime in sp.factorint(order):
        if pow(value, order // int(prime), modulus) == 1:
            raise AssertionError("computed order was not minimal")
    return order, factors


def parity_sign(residue: int, modulus: int) -> int:
    value = residue % modulus
    if value == 0:
        raise ValueError("zero residue has no nonzero canonical parity sign")
    return -1 if value & 1 else 1


def sign_matrix(order: int) -> list[list[int]]:
    half = (order - 1) // 2
    return [
        [parity_sign(column * pow(row, -1, order), order) for column in range(1, half + 1)]
        for row in range(1, half + 1)
    ]


def rank_mod(matrix: Sequence[Sequence[int]], modulus: int) -> int:
    if not matrix:
        return 0
    rows = [[int(value) % modulus for value in row] for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0])
    rank = 0
    for column in range(column_count):
        pivot = next((index for index in range(rank, row_count) if rows[index][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, modulus)
        rows[rank] = [value * inverse % modulus for value in rows[rank]]
        for index in range(row_count):
            if index == rank or rows[index][column] == 0:
                continue
            factor = rows[index][column]
            rows[index] = [
                (left - factor * right) % modulus
                for left, right in zip(rows[index], rows[rank])
            ]
        rank += 1
        if rank == min(row_count, column_count):
            break
    return rank


def secp_certificate() -> dict[str, Any]:
    if not sp.isprime(SECP_P) or not sp.isprime(SECP_N):
        raise AssertionError("secp constants lost primality")
    half = (SECP_N - 1) // 2
    if half % 2:
        raise AssertionError("half order must be even for the forced odd characters")

    order_mod_n, factors_n_minus_1 = exact_order_prime_modulus(2, SECP_N)
    order_mod_p, factors_p_minus_1 = exact_order_prime_modulus(2, SECP_P)
    if order_mod_n != half or order_mod_p != half:
        raise AssertionError("the two exact orders no longer equal the half order")

    quarter = half // 2
    if pow(2, quarter, SECP_N) != SECP_N - 1:
        raise AssertionError("2^(half/2) was not -1 modulo n")
    if pow(2, quarter, SECP_P) != SECP_P - 1:
        raise AssertionError("2^(half/2) was not -1 modulo p")

    kernel_size = (SECP_N - 1) // order_mod_n
    if kernel_size != 2:
        raise AssertionError("character evaluation kernel did not have size two")

    value_mod_p_squared = pow(2, quarter, SECP_P * SECP_P)
    p_squared_divides = (value_mod_p_squared + 1) % (SECP_P * SECP_P) == 0

    return {
        "p": SECP_P,
        "n": SECP_N,
        "half_dimension": half,
        "half_dimension_bit_length": half.bit_length(),
        "factorization_n_minus_1": {str(q): e for q, e in sorted(factors_n_minus_1.items())},
        "factorization_p_minus_1": {str(q): e for q, e in sorted(factors_p_minus_1.items())},
        "order_of_2_mod_n": order_mod_n,
        "order_of_2_mod_p": order_mod_p,
        "orders_equal_half_dimension": True,
        "two_to_half_half_mod_n": SECP_N - 1,
        "two_to_half_half_mod_p": SECP_P - 1,
        "evaluation_map_kernel_size": kernel_size,
        "characters_with_chi_2_equal_inverse_2": kernel_size,
        "those_characters_are_odd": True,
        "forced_zero_eigenvalues": kernel_size,
        "half_source_nullity_lower_bound": kernel_size,
        "half_source_rank_upper_bound": half - kernel_size,
        "p_squared_divides_two_to_half_half_plus_one": p_squared_divides,
        "exact_nullity_proved": False,
        "additional_zero_source": (
            "Additional zeros may occur if other odd weighted character sums vanish modulo p."
        ),
    }


def small_witnesses() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for order in sp.primerange(5, 80):
        half = (order - 1) // 2
        if half % 2 or sp.n_order(2, order) != half:
            continue
        matrix = sign_matrix(order)
        for modulus in sp.primerange(order + 2, 400):
            if sp.n_order(2, modulus) != half:
                continue
            rank = rank_mod(matrix, modulus)
            rows.append(
                {
                    "n": int(order),
                    "p": int(modulus),
                    "half_dimension": int(half),
                    "rank": int(rank),
                    "nullity": int(half - rank),
                }
            )
    if not rows:
        raise AssertionError("small witness corpus is empty")
    if any(row["nullity"] < 2 for row in rows):
        raise AssertionError("forced two-dimensional defect failed on a witness")
    return rows


def run() -> dict[str, Any]:
    secp = secp_certificate()
    witnesses = small_witnesses()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "finite_characteristic_theorem": {
            "group": "U=(Z/nZ)^*, |U|=n-1=2m",
            "source_function": "epsilon(a)=(-1)^canonical(a)",
            "hypotheses": [
                "ord_n(2)=m",
                "ord_p(2)=m",
                "m is even",
                "p and n are distinct odd primes",
            ],
            "character_count": (
                "The evaluation map chi -> chi(2) has image size m and kernel size 2."
            ),
            "forced_characters": (
                "Exactly two characters satisfy chi(2)=1/2 in the algebraic closure of F_p."
            ),
            "oddness": (
                "Since -1=2^(m/2) modulo n and 2^(m/2)=-1 modulo p, both characters are odd."
            ),
            "zero_identity": (
                "For odd chi, lambda_chi=2*chi(2)*H_chi and "
                "n*chi(2)*H_chi=(1-2*chi(2))*W_chi. Thus chi(2)=1/2 forces lambda_chi=0."
            ),
            "conclusion": (
                "The full source convolution and the half-source matrix have nullity at least two over F_p."
            ),
        },
        "secp256k1": secp,
        "small_exact_replay": {
            "pairs": len(witnesses),
            "all_nullities_at_least_two": True,
            "all_screened_nullities_exactly_two": all(row["nullity"] == 2 for row in witnesses),
            "rows": witnesses,
        },
        "decision": {
            "c31_characteristic_zero_rank_retracted": False,
            "c31_frozen_full_rank_retracted": False,
            "secp_base_field_full_rank": False,
            "secp_base_field_rank_defect_proved": True,
            "secp_base_field_nullity_lower_bound": 2,
            "secp_base_field_exact_rank_proved": False,
            "fixed_dictionary_dimension_reduction_found": 2,
            "subroot_fixed_dictionary_found": False,
            "nonlinear_anchor_propagation_found": False,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "scientific_boundary": (
            "The package proves a two-dimensional forced defect, not exact rank. "
            "It does not construct a sub-root dictionary or a nonlinear parity evaluator."
        ),
        "successor": "PUBLIC-ANCHOR-FIXED-G-NONLINEAR-PROPAGATION-082",
    }
    payload["digest"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(stable_json(payload), encoding="utf-8")
    print(stable_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
