#!/usr/bin/env python3
"""Exact cycle replay for UORC056 TRANSPOSED KERNEL EVALUATION B6.

No external point, key, wallet, unknown scalar, or production-sized target is
accepted. The replay uses only frozen public odd orders.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)


def shift_forward(vector: list[int], amount: int) -> list[int]:
    size = len(vector)
    return [vector[(index + amount) % size] for index in range(size)]


def run_case(order: int) -> dict[str, object]:
    if order % 2 == 0:
        raise AssertionError("order must be odd")

    parity = [1 if index % 2 == 0 else -1 for index in range(order)]
    shifted = shift_forward(parity, 1)
    defect = [left + right for left, right in zip(parity, shifted, strict=True)]
    nonzero_defect = [index for index, value in enumerate(defect) if value]
    if nonzero_defect != [order - 1] or defect[-1] != 2:
        raise AssertionError("canonical parity did not have one wrap defect")

    delta = [0] * order
    delta[order - 1] = 1
    reconstructed = [0] * order
    basis_positions: list[int] = []
    for power in range(order):
        shifted_delta = shift_forward(delta, power)
        support = [index for index, value in enumerate(shifted_delta) if value]
        if len(support) != 1:
            raise AssertionError("shifted delta was not a basis vector")
        basis_positions.append(support[0])
        coefficient = -1 if power % 2 else 1
        reconstructed = [
            value + coefficient * delta_value
            for value, delta_value in zip(
                reconstructed, shifted_delta, strict=True
            )
        ]

    if reconstructed != parity:
        raise AssertionError("dense alternating inverse failed")
    if len(set(basis_positions)) != order:
        raise AssertionError("translation powers did not span distinct basis vectors")

    deletion_checks = 0
    for deleted_power in range(order):
        candidate = reconstructed.copy()
        shifted_delta = shift_forward(delta, deleted_power)
        coefficient = -1 if deleted_power % 2 else 1
        candidate = [
            value - coefficient * delta_value
            for value, delta_value in zip(candidate, shifted_delta, strict=True)
        ]
        if candidate == parity:
            raise AssertionError("a dense inverse coefficient was redundant")
        deletion_checks += 1

    return {
        "order": order,
        "parity_values": order,
        "wrap_defect_index": order - 1,
        "wrap_defect_value": 2,
        "alternating_inverse_support": order,
        "distinct_shifted_delta_vectors": len(set(basis_positions)),
        "coefficient_deletion_checks": deletion_checks,
        "dense_inverse_reconstructs_parity": True,
        "every_translation_coefficient_is_necessary": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "alternating_inverse_support": SECP_N,
        "support_bit_length": SECP_N.bit_length(),
        "pollard_scale": 2**128,
        "sparse_translation_polynomial_is_subroot": False,
        "transposition_requires_oriented_input_state": True,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-CM-RECURRENCE-STATE-B7",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_transposed_kernel_evaluation_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-TRANSPOSED-KERNEL-EVALUATION-B6",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "parity_values": sum(case["parity_values"] for case in cases),
            "coefficient_deletion_checks": sum(
                case["coefficient_deletion_checks"] for case in cases
            ),
            "all_dense_inverses_reconstruct_parity": all(
                case["dense_inverse_reconstructs_parity"] for case in cases
            ),
            "all_translation_coefficients_necessary": all(
                case["every_translation_coefficient_is_necessary"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Canonical parity is the unique solution of (I+T)a=2*delta_cut. "
            "The inverse is the alternating sum of every translation power, "
            "and in the regular representation every coefficient is necessary. "
            "Transposed linear evaluation does not create the missing oriented "
            "sample vector and a sparse translation-polynomial circuit is not "
            "a sub-square-root evaluator."
        ),
        "claim_boundary": [
            "The cyclic shift identities and coefficient necessity are exact.",
            "The closure applies to explicit sparse translation-polynomial and ordinary transposed-linear representations.",
            "It does not close a genuinely compressed endpoint-segment state or nonlinear coordinate circuit.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
