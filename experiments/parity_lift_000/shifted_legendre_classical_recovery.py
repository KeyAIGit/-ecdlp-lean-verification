#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

FROZEN_ORDERS = (397, 433, 1093, 1249, 3469, 4021)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def qchar(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-binary value")


def run_case(prime: int) -> dict[str, object]:
    sequence = [qchar(value, prime) for value in range(prime)]

    correlation_checks = 0
    for shift in range(prime):
        correlation = sum(
            sequence[x] * sequence[(x + shift) % prime]
            for x in range(prime)
        )
        expected = prime - 1 if shift == 0 else -1
        if correlation != expected:
            raise AssertionError("shifted Legendre autocorrelation failed")
        correlation_checks += 1

    rng = random.Random(0xC041 + prime)
    hamming_checks = 0
    expected_hamming = (prime + 3) // 2
    for _ in range(min(2000, prime * 2)):
        left = rng.randrange(prime)
        right = rng.randrange(prime - 1)
        if right >= left:
            right += 1
        distance = sum(
            sequence[(x + left) % prime] != sequence[(x + right) % prime]
            for x in range(prime)
        )
        if distance != expected_hamming:
            raise AssertionError("shifted Legendre Hamming distance failed")
        hamming_checks += 1

    affine_checks = 0
    for _ in range(min(5000, prime * 3)):
        hidden = rng.randrange(prime)
        multiplier = rng.randrange(1, prime)
        offset = rng.randrange(prime)
        shifted_offset = offset * pow(multiplier, -1, prime) % prime
        left = qchar(multiplier * hidden + offset, prime)
        right = qchar(multiplier, prime) * qchar(hidden + shifted_offset, prime)
        if left != right:
            raise AssertionError("affine query did not reduce to shifted Legendre")
        affine_checks += 1

    query_count = math.ceil(2 * math.log2(prime)) + 12
    positions: list[int] = []
    used: set[int] = set()
    while len(positions) < query_count:
        position = rng.randrange(prime)
        if position not in used:
            used.add(position)
            positions.append(position)

    signatures: dict[tuple[int, ...], int] = {}
    for shift in range(prime):
        signature = tuple(sequence[(position + shift) % prime] for position in positions)
        if signature in signatures:
            raise AssertionError("predeclared fingerprint positions did not distinguish all shifts")
        signatures[signature] = shift

    return {
        "order": prime,
        "correlation_checks": correlation_checks,
        "hamming_checks": hamming_checks,
        "affine_reduction_checks": affine_checks,
        "nonzero_shift_correlation": -1,
        "pairwise_hamming_distance": expected_hamming,
        "fingerprint_queries": query_count,
        "fingerprint_table_entries": prime,
        "fingerprint_table_symbols": prime * query_count,
        "all_shift_signatures_unique": len(signatures) == prime,
        "full_correlation_query_cost": prime,
        "full_correlation_arithmetic_cost_softO": prime,
    }


def secp_certificate() -> dict[str, object]:
    n = SECP_N
    fingerprint_queries = math.ceil(2 * math.log2(n)) + 12
    sqrt_n = math.isqrt(n - 1) + 1
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "ceil_sqrt_n": sqrt_n,
        "information_theoretic_fingerprint_queries": fingerprint_queries,
        "full_signature_table_entries": n,
        "full_signature_table_symbols": n * fingerprint_queries,
        "pollard_scale": sqrt_n,
        "affine_oracle_normal_form": "chi_n(k+x) up to a public multiplier",
        "known_quantum_shifted_legendre_status": "polylogarithmic-query algorithm known",
        "known_unconditional_classical_subsqrt_status": "not established in this package",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("shifted_legendre_classical_recovery_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "SHIFTED-LEGENDRE-CLASSICAL-RECOVERY-041",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_correlation_checks": sum(case["correlation_checks"] for case in cases),
            "total_hamming_checks": sum(case["hamming_checks"] for case in cases),
            "total_affine_reduction_checks": sum(case["affine_reduction_checks"] for case in cases),
            "all_shift_signatures_unique": all(case["all_shift_signatures_unique"] for case in cases),
            "all_nonzero_correlations_minus_one": True,
            "all_affine_queries_reduce_to_shift": True,
        },
        "secp256k1": secp_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
