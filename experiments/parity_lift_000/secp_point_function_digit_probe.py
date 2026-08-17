#!/usr/bin/env python3
"""Fixed-public-parameter secp256k1 probe for point-function radix digits.

The program accepts no external point, key, wallet, or unknown scalar.  It uses
a deterministic set of known scalars and the fixed secp256k1 generator.  It
computes the raw public point function

    Phi([k]G) = Phi(G)^(k^2) * psi_k(G)

and tests the order-7 and order-13441 power-residue phases available because
both divide p-1.  The probe asks whether phase, phase plus public y orientation,
or a low-degree polynomial in k mod q gives an exact radix digit on the sample.

A positive sample identity is not yet a proof.  A negative sample is not a
lower bound.  No production target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from nonlocal_odd_anchor_screen import division_polynomial_evaluator, quadratic_character

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)
CHARACTER_ORDERS = (7, 13441)
SEQUENTIAL_SAMPLES = 4096
RANDOM_SAMPLES = 512
MAX_POLYNOMIAL_DEGREE = 6
Point = Optional[tuple[int, int]]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor*divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def ec_add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1+y2) % P == 0:
        return None
    if left == right:
        slope = 3*x1*x1*pow(2*y1, -1, P) % P
    else:
        slope = (y2-y1)*pow((x2-x1) % P, -1, P) % P
    x3 = (slope*slope-x1-x2) % P
    y3 = (slope*(x1-x3)-y1) % P
    return x3, y3


def ec_mul(scalar: int, point: Point = G) -> Point:
    result: Point = None
    addend = point
    scalar %= N
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        scalar >>= 1
    return result


def half_sign(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    return 1 if 2*value < P else -1


def raw_phi_generator() -> int:
    evaluator = division_polynomial_evaluator(G, P)
    numerator = evaluator(P-1)
    denominator = evaluator(P-1+N)
    if numerator == 0 or denominator == 0:
        raise AssertionError("raw point-function ratio vanished")
    if math.gcd(N*N, P-1) != 1:
        raise AssertionError("n^2 root was not unique")
    exponent = pow((N*N) % (P-1), -1, P-1)
    return pow(numerator*pow(denominator, -1, P) % P, exponent, P)


def canonical_character_root(q: int) -> tuple[int, dict[int, int]]:
    if (P-1) % q:
        raise AssertionError("character order did not divide p-1")
    if not is_prime(q):
        raise AssertionError("probe expects prime character order")
    root = None
    for seed in range(2, 1000):
        candidate = pow(seed, (P-1)//q, P)
        if candidate != 1 and pow(candidate, q, P) == 1:
            root = candidate
            break
    if root is None:
        raise AssertionError("character root not found")
    powers = [pow(root, exponent, P) for exponent in range(1, q)]
    root = min(powers)
    table = {}
    current = 1
    for exponent in range(q):
        table[current] = exponent
        current = current*root % P
    if len(table) != q:
        raise AssertionError("character root did not have exact order")
    return root, table


def phase_index(value: int, q: int, table: dict[int, int]) -> int:
    phase = pow(value, (P-1)//q, P)
    return table[phase]


def solve_polynomial(xs: list[int], ys: list[int], degree: int, modulus: int):
    selected = []
    seen = set()
    for x, y in zip(xs, ys):
        x %= modulus
        if x in seen:
            continue
        selected.append((x, y % modulus))
        seen.add(x)
        if len(selected) == degree+1:
            break
    if len(selected) < degree+1:
        return None

    matrix = [
        [pow(x, power, modulus) for power in range(degree+1)] + [y]
        for x, y in selected
    ]
    rows = degree+1
    for column in range(rows):
        pivot = next((row for row in range(column, rows) if matrix[row][column] % modulus), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        inverse = pow(matrix[column][column], -1, modulus)
        matrix[column] = [(value*inverse) % modulus for value in matrix[column]]
        for row in range(rows):
            if row == column:
                continue
            factor = matrix[row][column] % modulus
            if factor:
                matrix[row] = [
                    (left-factor*right) % modulus
                    for left, right in zip(matrix[row], matrix[column])
                ]
    return tuple(matrix[row][-1] for row in range(rows))


def polynomial_accuracy(coefficients, xs, ys, modulus: int) -> float:
    correct = 0
    for x, y in zip(xs, ys):
        value = 0
        power = 1
        for coefficient in coefficients:
            value = (value+coefficient*power) % modulus
            power = power*(x % modulus) % modulus
        correct += value == y
    return correct/len(ys)


def state_purity(states, digits, q: int):
    state_digits = {}
    state_counts = {}
    for state, digit in zip(states, digits):
        state_digits.setdefault(state, set()).add(digit)
        counts = state_counts.setdefault(state, [0]*q)
        counts[digit] += 1
    exact = all(len(values) == 1 for values in state_digits.values())
    majority = sum(max(counts) for counts in state_counts.values())/len(digits)
    return exact, majority, len(state_digits), sum(len(values)>1 for values in state_digits.values())


@dataclass(frozen=True)
class StateResult:
    formula: str
    states: int
    exact_digit_function: bool
    majority_accuracy: float
    conflicting_states: int


@dataclass(frozen=True)
class PolynomialResult:
    degree: int
    coefficients: tuple[int, ...] | None
    accuracy: float
    exact_on_sample: bool


@dataclass(frozen=True)
class CharacterResult:
    q: int
    root: int
    samples: int
    distinct_digits: int
    distinct_phases: int
    state_results: tuple[StateResult, ...]
    polynomial_results: tuple[PolynomialResult, ...]
    phase_from_digit_exact: bool
    digit_from_phase_exact: bool
    best_state_formula: str
    best_state_accuracy: float
    best_polynomial_degree: int
    best_polynomial_accuracy: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("secp_point_function_digit_probe_results.json"),
    )
    args = parser.parse_args()

    phi_g = raw_phi_generator()
    evaluator = division_polynomial_evaluator(G, P)

    sequential_scalars = list(range(1, SEQUENTIAL_SAMPLES+1))
    rng = random.Random(20260812)
    random_scalars = []
    seen = set(sequential_scalars)
    while len(random_scalars) < RANDOM_SAMPLES:
        scalar = rng.randrange(1, N)
        if scalar not in seen:
            seen.add(scalar)
            random_scalars.append(scalar)
    scalars = sequential_scalars + random_scalars

    sequential_points = {}
    point: Point = None
    for scalar in sequential_scalars:
        point = ec_add(point, G)
        assert point is not None
        sequential_points[scalar] = point

    phi_values = []
    points = []
    for scalar in scalars:
        psi = evaluator(scalar)
        phi = pow(phi_g, scalar*scalar, P)*psi % P
        phi_values.append(phi)
        point = sequential_points.get(scalar)
        if point is None:
            point = ec_mul(scalar)
        assert point is not None
        points.append(point)

    results = []
    for q in CHARACTER_ORDERS:
        root, table = canonical_character_root(q)
        phases = [phase_index(value, q, table) for value in phi_values]
        digits = [scalar % q for scalar in scalars]
        states = {
            "phase": [(phase,) for phase in phases],
            "phase+half_y": [
                (phase, half_sign(point[1]))
                for phase, point in zip(phases, points)
            ],
            "phase+chi_y": [
                (phase, quadratic_character(point[1], P))
                for phase, point in zip(phases, points)
            ],
            "phase+half_phi": [
                (phase, half_sign(phi))
                for phase, phi in zip(phases, phi_values)
            ],
            "phase+chi_phi": [
                (phase, quadratic_character(phi, P))
                for phase, phi in zip(phases, phi_values)
            ],
            "phase+half_y+chi_phi": [
                (phase, half_sign(point[1]), quadratic_character(phi, P))
                for phase, point, phi in zip(phases, points, phi_values)
            ],
        }
        state_results = []
        for name, values in states.items():
            exact, majority, count, conflicts = state_purity(values, digits, q)
            state_results.append(StateResult(
                formula=name,
                states=count,
                exact_digit_function=exact,
                majority_accuracy=majority,
                conflicting_states=conflicts,
            ))

        polynomial_results = []
        xs = [scalar % q for scalar in scalars]
        for degree in range(MAX_POLYNOMIAL_DEGREE+1):
            coefficients = solve_polynomial(xs, phases, degree, q)
            accuracy = 0.0 if coefficients is None else polynomial_accuracy(coefficients, xs, phases, q)
            polynomial_results.append(PolynomialResult(
                degree=degree,
                coefficients=coefficients,
                accuracy=accuracy,
                exact_on_sample=accuracy == 1.0,
            ))

        phase_from_digit = all(
            len({phase for phase, digit2 in zip(phases, digits) if digit2 == digit}) <= 1
            for digit in set(digits)
        )
        digit_from_phase = all(
            len({digit for phase2, digit in zip(phases, digits) if phase2 == phase}) <= 1
            for phase in set(phases)
        )
        best_state = max(state_results, key=lambda row: (row.majority_accuracy, row.formula))
        best_poly = max(polynomial_results, key=lambda row: (row.accuracy, -row.degree))
        results.append(CharacterResult(
            q=q,
            root=root,
            samples=len(scalars),
            distinct_digits=len(set(digits)),
            distinct_phases=len(set(phases)),
            state_results=tuple(state_results),
            polynomial_results=tuple(polynomial_results),
            phase_from_digit_exact=phase_from_digit,
            digit_from_phase_exact=digit_from_phase,
            best_state_formula=best_state.formula,
            best_state_accuracy=best_state.majority_accuracy,
            best_polynomial_degree=best_poly.degree,
            best_polynomial_accuracy=best_poly.accuracy,
        ))

    payload = {
        "scope": (
            "fixed public secp256k1 parameters; deterministic known scalars only; "
            "no external point, key, wallet, or unknown target"
        ),
        "package": "SECP-POINT-FUNCTION-DIGIT-PROBE-022",
        "parameters": {
            "p": P,
            "n": N,
            "lambda": LAMBDA,
            "beta": BETA,
            "generator": G,
            "sequential_samples": SEQUENTIAL_SAMPLES,
            "random_samples": RANDOM_SAMPLES,
        },
        "phi_generator": phi_g,
        "characters": [asdict(result) for result in results],
        "aggregate": {
            "samples": len(scalars),
            "character_orders": list(CHARACTER_ORDERS),
            "exact_digit_state_formulas": {
                str(result.q): [
                    row.formula for row in result.state_results if row.exact_digit_function
                ]
                for result in results
            },
            "exact_low_degree_phase_polynomials": {
                str(result.q): [
                    row.degree for row in result.polynomial_results if row.exact_on_sample
                ]
                for result in results
            },
        },
        "claim_boundary": [
            "All scalars are known to the test harness; no unknown target is accepted.",
            "An exact sample identity requires independent samples and a proof before becoming an oracle.",
            "A nonexact sample does not rule out a more complicated phase formula.",
            "No ECDLP complexity claim is made by this probe alone.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
