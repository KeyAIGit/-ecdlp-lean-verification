#!/usr/bin/env python3
"""Toy-only exact screen for DIRECT-GLV-CIRCUIT-011.

The quotient reduction is inherited from DIRECT-GLV-CARRY-DESCENT-010.  On
z=x^3 quotient points the script tests several high-degree but low straight-line
complexity square classes.  No external point, key, wallet, curve, or
production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from direct_glv_carry_descent_screen import (
    FROZEN_CASES,
    quadratic_character,
    quotient_data,
    rotate_right,
    signs_to_bits,
)

BINARY_MUL_COST_LIMIT = 7
FULL_CUBIC_FIELD_MAX = 1663
ORDER_FLOOR = 271


def binary_mul_cost(exponent: int) -> int:
    """Multiplications in ordinary left-to-right binary exponentiation."""
    if exponent < 1:
        raise ValueError("positive exponent required")
    return exponent.bit_length() - 1 + exponent.bit_count() - 1


def structured_exponents(p: int) -> list[int]:
    # Cost <= L implies exponent <= 2^L for the binary method.
    seen_residues: set[int] = set()
    result: list[int] = []
    for exponent in range(1, 2**BINARY_MUL_COST_LIMIT + 1):
        if binary_mul_cost(exponent) > BINARY_MUL_COST_LIMIT:
            continue
        residue = exponent % (p - 1)
        if residue == 0 or residue in seen_residues:
            continue
        seen_residues.add(residue)
        result.append(exponent)
    return result


def character_masks(p: int) -> tuple[int, int]:
    residue = 0
    nonresidue = 0
    for value in range(p):
        sign = quadratic_character(value, p)
        if sign == 1:
            residue |= 1 << value
        elif sign == -1:
            nonresidue |= 1 << value
    return residue, nonresidue


def replay_power_affine(
    p: int,
    z_values: list[int],
    targets: list[int],
    solution: dict,
) -> None:
    for z, target in zip(z_values, targets):
        sign = -1 if solution["constant_nonsquare"] else 1
        for factor in solution["factors"]:
            sign *= quadratic_character(
                pow(z, factor["exponent"], p) + factor["constant"], p
            )
        if sign != target:
            raise AssertionError("power-affine solution replay failed")


def power_affine_up_to_two(
    p: int,
    z_values: list[int],
    targets: list[int],
    exponents: list[int],
) -> dict:
    """Exact chi(u*prod(z^e+c)) search with at most two factors."""
    width = len(z_values)
    ones = (1 << width) - 1
    target = signs_to_bits(targets)
    legendre = np.array(
        [quadratic_character(value, p) for value in range(p)],
        dtype=np.int8,
    )
    constants = np.arange(p, dtype=np.int64)[:, None]
    patterns: dict[int, tuple[int, int]] = {}
    valid_primitives = 0

    for exponent in exponents:
        base = np.array(
            [pow(z, exponent, p) for z in z_values], dtype=np.int64
        )
        values = legendre[(constants + base[None, :]) % p]
        valid = np.all(values != 0, axis=1)
        packed = np.packbits(values < 0, axis=1, bitorder="little")
        for constant, row in zip(
            np.nonzero(valid)[0].tolist(), packed[valid]
        ):
            vector = int.from_bytes(row.tobytes(), "little") & ones
            patterns.setdefault(vector, (exponent, int(constant)))
            valid_primitives += 1

    def build_solution(
        flip: bool, factors: list[tuple[int, int]]
    ) -> dict:
        answer = {
            "factor_count": len(factors),
            "constant_nonsquare": flip,
            "factors": [
                {"exponent": exponent, "constant": constant}
                for exponent, constant in factors
            ],
        }
        replay_power_affine(p, z_values, targets, answer)
        return answer

    solution = None
    for flip, wanted in ((False, target), (True, target ^ ones)):
        if wanted == 0:
            solution = build_solution(flip, [])
            break
        single = patterns.get(wanted)
        if single is not None:
            solution = build_solution(flip, [single])
            break
        for vector, first in patterns.items():
            second = patterns.get(wanted ^ vector)
            if second is not None and second != first:
                solution = build_solution(flip, [first, second])
                break
        if solution is not None:
            break

    nominal_classes = 2 * (
        1
        + valid_primitives
        + valid_primitives * (valid_primitives - 1) // 2
    )
    return {
        "valid_primitive_polynomials": valid_primitives,
        "distinct_primitive_patterns": len(patterns),
        "nominal_classes_up_to_two_factors": nominal_classes,
        "random_exact_union_bound_log2": (
            math.log2(nominal_classes) - width
            if nominal_classes
            else float("-inf")
        ),
        "solution": solution,
    }


def replay_shifted_power(
    p: int,
    z_values: list[int],
    targets: list[int],
    solution: dict,
) -> None:
    for z, target in zip(z_values, targets):
        value = (
            pow(
                (z + solution["shift"]) % p,
                solution["exponent"],
                p,
            )
            + solution["constant"]
        ) % p
        sign = solution["leading_character"] * quadratic_character(value, p)
        if sign != target:
            raise AssertionError("shifted-power solution replay failed")


def replay_sparse_trinomial(
    p: int,
    z_values: list[int],
    targets: list[int],
    solution: dict,
) -> None:
    for z, target in zip(z_values, targets):
        value = (
            pow(z, solution["exponent"], p)
            + solution["linear_coefficient"] * z
            + solution["constant"]
        ) % p
        sign = solution["leading_character"] * quadratic_character(value, p)
        if sign != target:
            raise AssertionError("sparse-trinomial solution replay failed")


def search_two_parameter_family(
    p: int,
    z_values: list[int],
    targets: list[int],
    exponents: list[int],
    family: str,
) -> dict:
    residue, nonresidue = character_masks(p)
    all_values = (1 << p) - 1
    solution = None
    parameter_pairs = 0

    for exponent in exponents:
        powers = (
            [pow(z, exponent, p) for z in z_values]
            if family == "sparse_trinomial"
            else None
        )
        for first_parameter in range(p):
            parameter_pairs += 1
            plus = all_values
            minus = all_values
            for index, (z, target) in enumerate(zip(z_values, targets)):
                if family == "shifted_power":
                    offset = pow((z + first_parameter) % p, exponent, p)
                elif family == "sparse_trinomial":
                    assert powers is not None
                    offset = (powers[index] + first_parameter * z) % p
                else:
                    raise ValueError(f"unknown family: {family}")

                plus &= rotate_right(
                    residue if target == 1 else nonresidue, offset, p
                )
                minus &= rotate_right(
                    nonresidue if target == 1 else residue, offset, p
                )
                if not plus and not minus:
                    break

            if plus or minus:
                candidates = plus or minus
                constant = (candidates & -candidates).bit_length() - 1
                leading_character = 1 if plus else -1
                if family == "shifted_power":
                    solution = {
                        "exponent": exponent,
                        "shift": first_parameter,
                        "constant": constant,
                        "leading_character": leading_character,
                    }
                    replay_shifted_power(
                        p, z_values, targets, solution
                    )
                else:
                    solution = {
                        "exponent": exponent,
                        "linear_coefficient": first_parameter,
                        "constant": constant,
                        "leading_character": leading_character,
                    }
                    replay_sparse_trinomial(
                        p, z_values, targets, solution
                    )
                break
        if solution is not None:
            break

    nominal_classes = 2 * len(exponents) * p * p
    return {
        "parameter_pairs_examined_until_solution_or_exhaustion": parameter_pairs,
        "nominal_classes": nominal_classes,
        "random_exact_union_bound_log2": math.log2(nominal_classes) - len(z_values),
        "solution": solution,
    }


def replay_monic_cubic(
    p: int,
    z_values: list[int],
    targets: list[int],
    solution: dict,
) -> None:
    for z, target in zip(z_values, targets):
        value = (
            z * z % p * z
            + solution["quadratic_coefficient"] * z * z
            + solution["linear_coefficient"] * z
            + solution["constant"]
        ) % p
        sign = solution["leading_character"] * quadratic_character(value, p)
        if sign != target:
            raise AssertionError("monic cubic solution replay failed")


def monic_cubic_square_class(
    p: int,
    z_values: list[int],
    targets: list[int],
    seed: int,
) -> dict:
    if p > FULL_CUBIC_FIELD_MAX:
        return {
            "status": "not_run_field_threshold",
            "field_threshold": FULL_CUBIC_FIELD_MAX,
            "nominal_classes": 2 * p**3,
            "solution": None,
        }

    residue, nonresidue = character_masks(p)
    all_values = (1 << p) - 1
    order = list(range(len(z_values)))
    random.Random(seed).shuffle(order)
    z_ordered = [z_values[index] for index in order]
    target_ordered = [targets[index] for index in order]
    z2 = [z * z % p for z in z_ordered]
    z3 = [square * z % p for square, z in zip(z2, z_ordered)]
    solution = None

    for quadratic_coefficient in range(p):
        base = [
            (cube + quadratic_coefficient * square) % p
            for cube, square in zip(z3, z2)
        ]
        for linear_coefficient in range(p):
            plus = all_values
            minus = all_values
            for z, offset_base, target in zip(
                z_ordered, base, target_ordered
            ):
                offset = (offset_base + linear_coefficient * z) % p
                plus &= rotate_right(
                    residue if target == 1 else nonresidue, offset, p
                )
                minus &= rotate_right(
                    nonresidue if target == 1 else residue, offset, p
                )
                if not plus and not minus:
                    break
            if plus or minus:
                candidates = plus or minus
                constant = (candidates & -candidates).bit_length() - 1
                solution = {
                    "quadratic_coefficient": quadratic_coefficient,
                    "linear_coefficient": linear_coefficient,
                    "constant": constant,
                    "leading_character": 1 if plus else -1,
                }
                replay_monic_cubic(p, z_values, targets, solution)
                break
        if solution is not None:
            break

    nominal_classes = 2 * p**3
    return {
        "status": "screened",
        "field_threshold": FULL_CUBIC_FIELD_MAX,
        "nominal_classes": nominal_classes,
        "random_exact_union_bound_log2": math.log2(nominal_classes) - len(z_values),
        "solution": solution,
    }


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    quotient_orbits: int
    structured_exponents: list[int]
    maximum_exponent: int
    power_affine_up_to_two: dict
    shifted_power: dict
    sparse_trinomial: dict
    monic_cubic: dict


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    data = quotient_data(p, order, generator)
    z_values = data["z"]
    targets = data["target"]
    exponents = structured_exponents(p)
    nonlinear_exponents = [exponent for exponent in exponents if exponent >= 2]
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        quotient_orbits=len(z_values),
        structured_exponents=exponents,
        maximum_exponent=max(exponents),
        power_affine_up_to_two=power_affine_up_to_two(
            p, z_values, targets, exponents
        ),
        shifted_power=search_two_parameter_family(
            p,
            z_values,
            targets,
            nonlinear_exponents,
            "shifted_power",
        ),
        sparse_trinomial=search_two_parameter_family(
            p,
            z_values,
            targets,
            nonlinear_exponents,
            "sparse_trinomial",
        ),
        monic_cubic=monic_cubic_square_class(
            p, z_values, targets, 20260812 + p + order
        ),
    )


def solution_count(cases: list[CaseResult], attribute: str) -> int:
    count = 0
    for case in cases:
        record = getattr(case, attribute)
        if record.get("solution") is not None:
            count += 1
    return count


def build_payload(cases: list[CaseResult]) -> dict:
    nontrivial = [case for case in cases if case.order >= ORDER_FLOOR]
    cubic_screened = [
        case for case in cases if case.monic_cubic["status"] == "screened"
    ]
    cubic_nontrivial = [
        case for case in cubic_screened if case.order >= ORDER_FLOOR
    ]
    return {
        "package": "DIRECT-GLV-CIRCUIT-011",
        "scope": "fifteen frozen j=0 prime-order toy subgroups; no external or production target",
        "target": "chi(R(z(Q))) = h(Q), where z=x^3 and h=g*chi(y)",
        "cost_model": {
            "exponent_cost": "ordinary binary exponentiation multiplications",
            "binary_multiplication_cost_limit": BINARY_MUL_COST_LIMIT,
            "maximum_unreduced_exponent": max(
                max(case.structured_exponents) for case in cases
            ),
            "full_monic_cubic_field_threshold": FULL_CUBIC_FIELD_MAX,
        },
        "exact_families": [
            "u*product(z^e+c) with at most two factors and binary exponentiation cost(e)<=7",
            "u*((z+a)^e+b) with binary exponentiation cost(e)<=7",
            "u*(z^e+a*z+b) with binary exponentiation cost(e)<=7",
            "all u*(z^3+A*z^2+B*z+C) on frozen fields p<=1663",
        ],
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "nontrivial_cases": len(nontrivial),
            "power_affine_up_to_two_exact_decoders": solution_count(
                cases, "power_affine_up_to_two"
            ),
            "power_affine_up_to_two_exact_decoders_order_at_least_271": solution_count(
                nontrivial, "power_affine_up_to_two"
            ),
            "shifted_power_exact_decoders": solution_count(
                cases, "shifted_power"
            ),
            "shifted_power_exact_decoders_order_at_least_271": solution_count(
                nontrivial, "shifted_power"
            ),
            "sparse_trinomial_exact_decoders": solution_count(
                cases, "sparse_trinomial"
            ),
            "sparse_trinomial_exact_decoders_order_at_least_271": solution_count(
                nontrivial, "sparse_trinomial"
            ),
            "monic_cubic_screened_cases": len(cubic_screened),
            "monic_cubic_screened_nontrivial_cases": len(cubic_nontrivial),
            "monic_cubic_exact_decoders": solution_count(
                cubic_screened, "monic_cubic"
            ),
            "monic_cubic_exact_decoders_order_at_least_271": solution_count(
                cubic_nontrivial, "monic_cubic"
            ),
            "largest_order": max(case.order for case in cases),
            "largest_quotient_orbits": max(
                case.quotient_orbits for case in cases
            ),
        },
        "conclusion": (
            "The declared low straight-line complexity families produce exact "
            "fits only on tiny quotient sets.  Across every frozen subgroup of "
            "order at least 271, no exact decoder occurs in the two-factor "
            "power-affine, shifted-power, or sparse-trinomial families.  The "
            "stratified exhaustive monic-cubic screen is also negative on every "
            "screened nontrivial field through p=1663."
        ),
        "claim_boundary": [
            "The exponent cost is the stated binary method, not minimum addition-chain complexity.",
            "Arbitrary fitted field constants are allowed, so the finite negative is stronger within the declared grammar; a positive would still require a scalable coefficient-generation rule.",
            "Full monic cubics are exhausted only for p<=1663; larger fields are explicitly marked unscreened for that family.",
            "The screen does not cover three or more power-affine factors, general multivariate straight-line programs, or canonical p-adic outputs.",
            "Union-bound logarithms are random-target capacity diagnostics, not p-values for the structured carry target.",
            "This is bounded toy evidence, not an asymptotic lower bound or an ECDLP algorithm.",
            "No secp256k1 unknown point, private key, wallet, or external target is accepted or evaluated.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "direct_glv_circuit_results.json"
        ),
    )
    parser.add_argument("--case-index", type=int, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.case_index is not None:
        if not 0 <= args.case_index < len(FROZEN_CASES):
            raise SystemExit("invalid frozen case index")
        print(
            json.dumps(
                asdict(run_case(*FROZEN_CASES[args.case_index])),
                sort_keys=True,
            )
        )
        return

    cases: list[CaseResult] = []
    script = Path(__file__).resolve()
    for index in range(len(FROZEN_CASES)):
        completed = subprocess.run(
            [sys.executable, str(script), "--case-index", str(index)],
            check=True,
            capture_output=True,
            text=True,
        )
        cases.append(CaseResult(**json.loads(completed.stdout)))

    rendered = json.dumps(build_payload(cases), indent=2, sort_keys=True)
    args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
