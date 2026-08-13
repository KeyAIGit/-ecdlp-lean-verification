#!/usr/bin/env python3
"""Exact toy replay for UORC056 MILLER KERNEL EDGE B2.

No external curve, point, key, wallet, unknown scalar, or production-sized
ECDLP target is accepted. Miller functions are represented exactly as
(A(x)+B(x)y)/D(x) in F_p(E), with y^2=x^3+7.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from nonlocal_odd_anchor_screen import (
    division_polynomial_evaluator,
    ec_add,
    orbit,
    quadratic_character,
)

Point = Optional[tuple[int, int]]
B_CURVE = 7
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (13, 7, (7, 5)),
    (43, 31, (2, 12)),
    (61, 61, (2, 25)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (97, 79, (1, 28)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
    (211, 199, (3, 33)),
    (349, 313, (2, 109)),
)
CENTRES = (1, 2, 3, 5, 7)


def trim(poly: list[int], p: int) -> list[int]:
    result = [coefficient % p for coefficient in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[int], right: list[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return trim([
        ((left[index] if index < len(left) else 0)
         + (right[index] if index < len(right) else 0)) % p
        for index in range(size)
    ], p)


def poly_neg(poly: list[int], p: int) -> list[int]:
    return trim([(-coefficient) % p for coefficient in poly], p)


def poly_sub(left: list[int], right: list[int], p: int) -> list[int]:
    return poly_add(left, poly_neg(right, p), p)


def poly_scale(poly: list[int], scalar: int, p: int) -> list[int]:
    return trim([(scalar * coefficient) % p for coefficient in poly], p)


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, left_coefficient in enumerate(left):
        for j, right_coefficient in enumerate(right):
            result[i + j] = (
                result[i + j] + left_coefficient * right_coefficient
            ) % p
    return trim(result, p)


def poly_divmod(
    numerator: list[int], denominator: list[int], p: int
) -> tuple[list[int], list[int]]:
    numerator = trim(numerator.copy(), p)
    denominator = trim(denominator.copy(), p)
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    if len(numerator) < len(denominator):
        return [0], numerator
    quotient = [0] * (len(numerator) - len(denominator) + 1)
    inverse_lead = pow(denominator[-1], -1, p)
    while numerator != [0] and len(numerator) >= len(denominator):
        shift = len(numerator) - len(denominator)
        coefficient = numerator[-1] * inverse_lead % p
        quotient[shift] = coefficient
        for index, value in enumerate(denominator):
            numerator[index + shift] = (
                numerator[index + shift] - coefficient * value
            ) % p
        numerator = trim(numerator, p)
    return trim(quotient, p), numerator


def poly_exact_div(
    numerator: list[int], denominator: list[int], p: int
) -> list[int]:
    quotient, remainder = poly_divmod(numerator, denominator, p)
    if remainder != [0]:
        raise AssertionError("inexact polynomial division")
    return quotient


def poly_gcd(left: list[int], right: list[int], p: int) -> list[int]:
    left = trim(left.copy(), p)
    right = trim(right.copy(), p)
    while right != [0]:
        _, remainder = poly_divmod(left, right, p)
        left, right = right, remainder
    if left == [0]:
        return [0]
    return poly_scale(left, pow(left[-1], -1, p), p)


def poly_eval(poly: list[int], value: int, p: int) -> int:
    result = 0
    for coefficient in reversed(poly):
        result = (result * value + coefficient) % p
    return result


@dataclass
class FunctionFieldElement:
    numerator_x: list[int]
    numerator_y: list[int]
    denominator: list[int]
    p: int

    @classmethod
    def one(cls, p: int) -> "FunctionFieldElement":
        return cls([1], [0], [1], p)

    def normalize(self) -> "FunctionFieldElement":
        common = poly_gcd(
            poly_gcd(self.numerator_x, self.numerator_y, self.p),
            self.denominator,
            self.p,
        )
        if common != [1]:
            self.numerator_x = poly_exact_div(self.numerator_x, common, self.p)
            self.numerator_y = poly_exact_div(self.numerator_y, common, self.p)
            self.denominator = poly_exact_div(self.denominator, common, self.p)
        inverse_lead = pow(self.denominator[-1], -1, self.p)
        self.numerator_x = poly_scale(self.numerator_x, inverse_lead, self.p)
        self.numerator_y = poly_scale(self.numerator_y, inverse_lead, self.p)
        self.denominator = poly_scale(self.denominator, inverse_lead, self.p)
        return self

    def multiply(
        self, other: "FunctionFieldElement"
    ) -> "FunctionFieldElement":
        curve_rhs = [B_CURVE, 0, 0, 1]
        numerator_x = poly_add(
            poly_mul(self.numerator_x, other.numerator_x, self.p),
            poly_mul(
                poly_mul(self.numerator_y, other.numerator_y, self.p),
                curve_rhs,
                self.p,
            ),
            self.p,
        )
        numerator_y = poly_add(
            poly_mul(self.numerator_x, other.numerator_y, self.p),
            poly_mul(self.numerator_y, other.numerator_x, self.p),
            self.p,
        )
        denominator = poly_mul(self.denominator, other.denominator, self.p)
        return FunctionFieldElement(
            numerator_x, numerator_y, denominator, self.p
        ).normalize()

    def square(self) -> "FunctionFieldElement":
        return self.multiply(self)

    def evaluate(self, point: tuple[int, int]) -> Optional[int]:
        x_coordinate, y_coordinate = point
        denominator = poly_eval(self.denominator, x_coordinate, self.p)
        if denominator == 0:
            return None
        numerator = (
            poly_eval(self.numerator_x, x_coordinate, self.p)
            + y_coordinate * poly_eval(self.numerator_y, x_coordinate, self.p)
        ) % self.p
        return numerator * pow(denominator, -1, self.p) % self.p


def miller_line(
    left: tuple[int, int], right: tuple[int, int], p: int
) -> FunctionFieldElement:
    x_left, y_left = left
    x_right, y_right = right
    point_sum = ec_add(left, right, p)
    if x_left == x_right and (y_left + y_right) % p == 0:
        return FunctionFieldElement(
            [(-x_left) % p, 1], [0], [1], p
        ).normalize()
    if left == right:
        slope = 3 * x_left * x_left * pow(2 * y_left, -1, p) % p
    else:
        slope = (
            (y_right - y_left) * pow((x_right - x_left) % p, -1, p)
        ) % p
    line_x = [(slope * x_left - y_left) % p, (-slope) % p]
    line_y = [1]
    vertical = [1] if point_sum is None else [(-point_sum[0]) % p, 1]
    return FunctionFieldElement(line_x, line_y, vertical, p).normalize()


def miller_function(
    point: tuple[int, int], scalar: int, p: int
) -> tuple[FunctionFieldElement, int]:
    function = FunctionFieldElement.one(p)
    running = point
    line_steps = 0
    for bit in bin(scalar)[3:]:
        function = function.square().multiply(miller_line(running, running, p))
        running = ec_add(running, running, p)
        line_steps += 1
        if bit == "1":
            function = function.multiply(miller_line(running, point, p))
            running = ec_add(running, point, p)
            line_steps += 1
    if running is not None:
        raise AssertionError("Miller scalar did not annihilate the torsion point")
    return function, line_steps


def run_case(p: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, order, p)
    psi = division_polynomial_evaluator(generator, p)
    rho = {
        index: quadratic_character(psi(index), p)
        for index in range(-(order - 1), order)
        if index != 0
    }
    if any(value not in (-1, 1) for value in rho.values()):
        raise AssertionError("residue sign vanished away from zero")

    centre_results: list[dict[str, object]] = []
    total_character_checks = 0
    total_gauge_checks = 0
    total_parity_matches = 0
    total_parity_mismatches = 0
    maximum_line_steps = 0

    for centre in CENTRES:
        if centre >= order:
            continue
        centre_point = points[centre]
        if centre_point is None:
            raise AssertionError("public centre was the identity")
        miller, line_steps = miller_function(centre_point, order, p)
        maximum_line_steps = max(maximum_line_steps, line_steps)
        constants: set[int] = set()
        matches = 0
        mismatches = 0
        checks = 0
        for scalar in range(1, order):
            if scalar == centre:
                continue
            query = points[scalar]
            if query is None:
                raise AssertionError("nonzero query was the identity")
            value = miller.evaluate(query)
            if value in (None, 0):
                raise AssertionError("Miller function was singular off its divisor")
            miller_character = quadratic_character(value, p)
            edge = rho[scalar - centre] * rho[scalar]
            constants.add(miller_character * edge)
            if (-rho[scalar - centre]) * (-rho[scalar]) != edge:
                raise AssertionError("global residue gauge changed a Miller edge")
            parity = 1 if scalar % 2 == 0 else -1
            if miller_character == parity:
                matches += 1
            else:
                mismatches += 1
            checks += 1
            total_character_checks += 1
            total_gauge_checks += 1
        if len(constants) != 1:
            raise AssertionError("Miller/EDS endpoint constant depended on query")
        centre_results.append(
            {
                "centre_scalar": centre,
                "line_steps": line_steps,
                "miller_degree_x": len(miller.numerator_x) - 1,
                "miller_degree_y_coefficient": len(miller.numerator_y) - 1,
                "checks": checks,
                "endpoint_constant": next(iter(constants)),
                "parity_matches": matches,
                "parity_mismatches": mismatches,
                "not_parity_up_to_global_sign": matches not in (0, checks),
            }
        )
        total_parity_matches += matches
        total_parity_mismatches += mismatches

    if not all(result["not_parity_up_to_global_sign"] for result in centre_results):
        raise AssertionError("a frozen Miller centre matched parity up to sign")

    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "centres": centre_results,
        "character_checks": total_character_checks,
        "gauge_checks": total_gauge_checks,
        "parity_matches": total_parity_matches,
        "parity_mismatches": total_parity_mismatches,
        "maximum_line_steps": maximum_line_steps,
        "all_endpoint_constants_query_independent": True,
        "all_edges_gauge_invariant": True,
        "all_screened_centres_reject_parity": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    inverse_n_mod_p_minus_one = pow(SECP_N, -1, SECP_P - 1)
    return {
        "p": SECP_P,
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "gcd_n_p_minus_one": math.gcd(SECP_N, SECP_P - 1),
        "inverse_n_mod_p_minus_one_is_odd": inverse_n_mod_p_minus_one % 2 == 1,
        "maximum_binary_miller_line_steps": (
            SECP_N.bit_length() - 1 + bin(SECP_N).count("1") - 1
        ),
        "miller_residual_eds_weight": 2,
        "finite_multiplicative_miller_products_are_gauge_even": True,
        "does_standard_miller_kernel_data_select_absolute_root": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-COMPACT-FROBENIUS-KERNEL-B3",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_miller_kernel_edge_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-MILLER-KERNEL-EDGE-B2",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "centres": sum(len(case["centres"]) for case in cases),
            "character_checks": sum(case["character_checks"] for case in cases),
            "gauge_checks": sum(case["gauge_checks"] for case in cases),
            "parity_matches": sum(case["parity_matches"] for case in cases),
            "parity_mismatches": sum(case["parity_mismatches"] for case in cases),
            "maximum_line_steps": max(case["maximum_line_steps"] for case in cases),
            "all_endpoint_constants_query_independent": all(
                case["all_endpoint_constants_query_independent"] for case in cases
            ),
            "all_edges_gauge_invariant": all(
                case["all_edges_gauge_invariant"] for case in cases
            ),
            "all_screened_centres_reject_parity": all(
                case["all_screened_centres_reject_parity"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Standard O(log n) Miller kernel functions are serious public "
            "candidates, but their quadratic characters replay as one "
            "query-independent constant times the relative EDS edge "
            "rho(k-r)rho(k). Every finite multiplicative combination is "
            "therefore invariant under the global EDS sign gauge and cannot "
            "select the absolute generator-oriented root Y_G."
        ),
        "claim_boundary": [
            "The finite-field replay is exact on the declared cofactor-one toy curves.",
            "The endpoint character law is scoped to the standard Miller/Weil normalization.",
            "The Lean core formalizes gauge invariance after that endpoint law is supplied.",
            "Sums, derivatives with new normalization, and arbitrary nonlinear circuits are not closed.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
