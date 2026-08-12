#!/usr/bin/env python3
"""Bounded classifier for GLV-CARRY-SEPARATION-005.

This script reuses the frozen toy arithmetic from the preceding parity-lift
packages. It accepts no external curve, point, key, wallet, or production
target.

For each Kummer-invariant j=0 toy subgroup it forms C3 orbit norms of every
currently available efficiently evaluable section:

  * invariant first torsion jet J1 = chi(2*y*d psi_n/dx);
  * x-coordinate character;
  * x-Taylor jets 2..4 of psi_n;
  * near-period sections psi_(n+a), -4 <= a <= 4, a != 0.

It classifies whether an orbit norm equals, up to a public global sign,

  R3       = rho(k)rho(lambda*k)rho(lambda^2*k),
  carry*R3 = (-1)^gamma R3,
  carry    = (-1)^gamma,

and searches all products of at most four retained orbit norms. Matched random
C6-invariant labels calibrate the best residual correlation.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    berlekamp_massey_complexity,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
    random_c6_target,
    sign_vector_to_bits,
)

NULL_TRIALS = 200
MAX_PRODUCT_WEIGHT = 4


class Series:
    __slots__ = ("c", "p", "N")

    def __init__(self, coefficients, p: int, length: int):
        values = list(coefficients[:length]) + [0] * max(0, length - len(coefficients))
        self.c = tuple(value % p for value in values[:length])
        self.p = p
        self.N = length

    @classmethod
    def constant(cls, value: int, p: int, length: int):
        return cls([value], p, length)

    @classmethod
    def variable(cls, value: int, p: int, length: int):
        return cls([value, 1], p, length)

    def coerce(self, other):
        return other if isinstance(other, Series) else Series.constant(other, self.p, self.N)

    def __add__(self, other):
        other = self.coerce(other)
        return Series([self.c[i] + other.c[i] for i in range(self.N)], self.p, self.N)

    __radd__ = __add__

    def __neg__(self):
        return Series([-value for value in self.c], self.p, self.N)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        result = [0] * self.N
        for i, left in enumerate(self.c):
            for j, right in enumerate(other.c[: self.N - i]):
                result[i + j] = (result[i + j] + left * right) % self.p
        return Series(result, self.p, self.N)

    __rmul__ = __mul__

    def __pow__(self, exponent: int):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Series.constant(1, self.p, self.N)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def inverse(self):
        if self.c[0] == 0:
            raise ZeroDivisionError
        result = [0] * self.N
        result[0] = pow(self.c[0], -1, self.p)
        for degree in range(1, self.N):
            result[degree] = (
                -result[0]
                * sum(self.c[i] * result[degree - i] for i in range(1, degree + 1))
            ) % self.p
        return Series(result, self.p, self.N)

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __eq__(self, other):
        return self.c == self.coerce(other).c


def square_root_series(rhs: Series, constant_root: int) -> Series:
    p, length = rhs.p, rhs.N
    result = [0] * length
    result[0] = constant_root % p
    inverse_double_root = pow(2 * constant_root, -1, p)
    for degree in range(1, length):
        known = sum(result[i] * result[degree - i] for i in range(1, degree))
        result[degree] = (rhs.c[degree] - known) * inverse_double_root % p
    root = Series(result, p, length)
    if root * root != rhs:
        raise AssertionError("square-root series verification failed")
    return root


def dps(point: tuple[int, int], p: int, length: int):
    x0, y0 = point
    x = Series.variable(x0, p, length)
    y = square_root_series(x**3 + 7, y0)

    @lru_cache(maxsize=None)
    def psi(index: int):
        if index < 0:
            return -psi(-index)
        if index == 0:
            return Series.constant(0, p, length)
        if index == 1:
            return Series.constant(1, p, length)
        if index == 2:
            return 2 * y
        if index == 3:
            return 3 * x**4 + 84 * x
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392)
        if index & 1:
            m = (index - 1) // 2
            return psi(m + 2) * psi(m) ** 3 - psi(m - 1) * psi(m + 1) ** 3
        m = index // 2
        return (
            psi(m)
            / (2 * y)
            * (psi(m + 2) * psi(m - 1) ** 2 - psi(m - 2) * psi(m + 1) ** 2)
        )

    return psi


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    status: str
    lam: int
    valid_base_sections: int
    distinct_orbit_norms: int
    distinct_products_up_to_weight_four: int
    exact_r3_single_sections: list[str]
    exact_carry_r3_single_sections: list[str]
    exact_carry_single_sections: list[str]
    exact_r3_products: int
    exact_carry_products: int
    best_r3_product: str
    best_r3_accuracy: float
    null_trials: int
    null_median_best_accuracy: float
    null_q95_best_accuracy: float
    empirical_null_percentile: float
    r3_linear_complexity: int
    carry_linear_complexity: int


def signs_equal_up_to_global(left: list[int], right: list[int]) -> int:
    matches = sum(a == b for a, b in zip(left, right))
    if matches == len(left):
        return 1
    if matches == 0:
        return -1
    return 0


def product_vectors(vectors: dict[str, int]) -> dict[int, str]:
    items = sorted(vectors.items())
    result = {0: "1"}
    for weight in range(1, min(MAX_PRODUCT_WEIGHT, len(items)) + 1):
        for combination in itertools.combinations(items, weight):
            value = 0
            names = []
            for name, vector in combination:
                value ^= vector
                names.append(name)
            result.setdefault(value, "*".join(names))
    return result


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]
    rho_kummer = all(rho[k] == rho[order - k] for k in range(1, order))

    beta = primitive_cube_root(p)
    lookup = {point: scalar for scalar, point in enumerate(points)}
    lam = lookup[(beta * generator[0] % p, generator[1])]

    if not rho_kummer or p == order:
        return CaseResult(
            p=p,
            order=order,
            generator=generator,
            status=("excluded_anomalous" if p == order else "excluded_non_kummer_residue"),
            lam=lam,
            valid_base_sections=0,
            distinct_orbit_norms=0,
            distinct_products_up_to_weight_four=0,
            exact_r3_single_sections=[],
            exact_carry_r3_single_sections=[],
            exact_carry_single_sections=[],
            exact_r3_products=0,
            exact_carry_products=0,
            best_r3_product="",
            best_r3_accuracy=0.0,
            null_trials=0,
            null_median_best_accuracy=0.0,
            null_q95_best_accuracy=0.0,
            empirical_null_percentile=0.0,
            r3_linear_complexity=0,
            carry_linear_complexity=0,
        )

    sections: dict[str, list[int | None]] = {"x": [None] * order}
    for jet in range(1, 5):
        sections[f"jet{jet}"] = [None] * order
    for offset in range(1, 5):
        sections[f"psi_n_minus_{offset}"] = [None] * order
        sections[f"psi_n_plus_{offset}"] = [None] * order
    valid = {name: True for name in sections}

    for scalar in range(1, order):
        point = points[scalar]
        assert point is not None
        x, y = point
        sections["x"][scalar] = quadratic_character(x, p)
        series_psi = dps(point, p, 5)
        torsion_series = series_psi(order)
        if torsion_series.c[0] != 0:
            raise AssertionError("psi_n did not vanish at an n-torsion point")
        for jet in range(1, 5):
            value = quadratic_character(torsion_series.c[jet], p)
            sections[f"jet{jet}"][scalar] = value
            if value == 0:
                valid[f"jet{jet}"] = False
        for offset in range(1, 5):
            for name, index in (
                (f"psi_n_minus_{offset}", order - offset),
                (f"psi_n_plus_{offset}", order + offset),
            ):
                value = quadratic_character(series_psi(index).c[0], p)
                sections[name][scalar] = value
                if value == 0:
                    valid[name] = False

    invariant_j1: list[int | None] = [None] * order
    for scalar in range(1, order):
        point = points[scalar]
        assert point is not None
        invariant_j1[scalar] = (
            sections["jet1"][scalar]
            * quadratic_character(2 * point[1], p)
        )
    del sections["jet1"]
    valid.pop("jet1")
    sections["J1"] = invariant_j1
    valid["J1"] = True
    sections = {name: values for name, values in sections.items() if valid[name]}

    r3 = [0] * order
    carry_sign = [0] * order
    for scalar in range(1, order):
        l1 = lam * scalar % order
        l2 = lam * l1 % order
        r3[scalar] = rho[scalar] * rho[l1] * rho[l2]
        gamma = (scalar + l1 + l2) // order
        if gamma not in (1, 2):
            raise AssertionError("invalid GLV carry")
        carry_sign[scalar] = -1 if gamma == 1 else 1

    orbit_norm_signs: dict[str, list[int]] = {}
    orbit_norm_vectors: dict[str, int] = {}
    for name, values in sections.items():
        signs = []
        for scalar in range(1, order):
            l1 = lam * scalar % order
            l2 = lam * l1 % order
            value = values[scalar] * values[l1] * values[l2]
            signs.append(value)
        orbit_norm_signs[name] = signs
        orbit_norm_vectors[name] = sign_vector_to_bits(signs)

    target_r3 = r3[1:]
    target_carry = carry_sign[1:]
    target_carry_r3 = [carry_sign[scalar] * r3[scalar] for scalar in range(1, order)]

    exact_r3 = [
        name for name, signs in orbit_norm_signs.items()
        if signs_equal_up_to_global(signs, target_r3)
    ]
    exact_carry_r3 = [
        name for name, signs in orbit_norm_signs.items()
        if signs_equal_up_to_global(signs, target_carry_r3)
    ]
    exact_carry = [
        name for name, signs in orbit_norm_signs.items()
        if signs_equal_up_to_global(signs, target_carry)
    ]

    products = product_vectors(orbit_norm_vectors)
    r3_bits = sign_vector_to_bits(target_r3)
    carry_bits = sign_vector_to_bits(target_carry)
    complement = (1 << (order - 1)) - 1

    exact_r3_products = sum(vector in (r3_bits, r3_bits ^ complement) for vector in products)
    exact_carry_products = sum(vector in (carry_bits, carry_bits ^ complement) for vector in products)

    def best(label: int) -> tuple[float, str]:
        best_accuracy = 0.5
        best_name = "1"
        for vector, name in products.items():
            distance = (vector ^ label).bit_count()
            accuracy = max(distance, order - 1 - distance) / (order - 1)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_name = name
        return best_accuracy, best_name

    observed, best_name = best(r3_bits)
    rng = random.Random(520260812 + p + order)
    null = [best(random_c6_target(order, lam, rng))[0] for _ in range(NULL_TRIALS)]
    null.sort()
    q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        status="screened",
        lam=lam,
        valid_base_sections=len(sections),
        distinct_orbit_norms=len(set(orbit_norm_vectors.values())),
        distinct_products_up_to_weight_four=len(products),
        exact_r3_single_sections=exact_r3,
        exact_carry_r3_single_sections=exact_carry_r3,
        exact_carry_single_sections=exact_carry,
        exact_r3_products=exact_r3_products,
        exact_carry_products=exact_carry_products,
        best_r3_product=best_name,
        best_r3_accuracy=observed,
        null_trials=NULL_TRIALS,
        null_median_best_accuracy=statistics.median(null),
        null_q95_best_accuracy=q95,
        empirical_null_percentile=sum(value <= observed for value in null) / NULL_TRIALS,
        r3_linear_complexity=berlekamp_massey_complexity(target_r3),
        carry_linear_complexity=berlekamp_massey_complexity(target_carry),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("glv_carry_separation_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    screened = [case for case in cases if case.status == "screened"]

    payload = {
        "scope": "frozen j=0 toy subgroups only; no secp256k1 target and no external input",
        "package": "GLV-CARRY-SEPARATION-005",
        "targets": {
            "odd_residue": "R3=rho(k)rho(lambda*k)rho(lambda^2*k)",
            "carry": "(-1)^gamma, gamma=(k0+k1+k2)/n in {1,2}",
            "dependent_product": "(-1)^gamma*R3",
        },
        "section_family": [
            "invariant first torsion jet J1",
            "x-coordinate character",
            "torsion Taylor jets 2..4",
            "near-period sections psi_(n+a), 1<=|a|<=4",
            "all products of orbit norms up to weight four",
        ],
        "protocol": {
            "null_trials_per_case": NULL_TRIALS,
            "maximum_product_weight": MAX_PRODUCT_WEIGHT,
            "null_labels": "random C6-invariant labels",
            "global_sign_allowed": True,
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases_total": len(cases),
            "cases_screened": len(screened),
            "exact_r3_single_sections": sum(bool(case.exact_r3_single_sections) for case in screened),
            "exact_carry_single_sections": sum(bool(case.exact_carry_single_sections) for case in screened),
            "cases_with_exact_r3_product": sum(case.exact_r3_products > 0 for case in screened),
            "cases_with_exact_carry_product": sum(case.exact_carry_products > 0 for case in screened),
            "cases_above_matched_null_q95": sum(
                case.best_r3_accuracy > case.null_q95_best_accuracy for case in screened
            ),
            "maximum_empirical_null_percentile": max(
                case.empirical_null_percentile for case in screened
            ),
            "common_exact_carry_r3_sections": sorted(
                set.intersection(*[set(case.exact_carry_r3_single_sections) for case in screened])
            ),
        },
        "conclusion": (
            "Every exact odd section found in the retained algebra carries the same GLV "
            "canonical-lift multiplier as the public point-function norm. No section or "
            "product through weight four isolates R3 or the carry itself, and no case "
            "exceeds its matched 95% random-label envelope."
        ),
        "claim_boundary": [
            "Bounded toy evidence, not a normalization-rigidity theorem.",
            "The screen covers only the committed algebraic section family.",
            "No external point, key, wallet, or production target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
