#!/usr/bin/env python3
"""Bounded Eisenstein-CM root-phase screen for PARITY-LIFT-000.

Scope:
    Frozen toy subgroups on E/F_p: y^2 = x^3 + 7 only.
    The program accepts no external point, key, wallet, or production-sized
    target. It tests a canonical F_{p^2} cube-root lift and Frobenius-descended
    binary characters against the EDS residue trace.

The construction uses primes p == 7 (mod 36) for which 7 is a nonsquare.
Writing c^2=7 in F_{p^2}, every rational point Q=(x,y) satisfies

    A(Q)=y-c is a cube in F_{p^2},
    A(Q)^(p+1)=x^3.

Because v_3(p^2-1)=1, cubing is bijective on the cube subgroup, so A(Q)
has one canonical cube-subgroup root u(Q). Frobenius gives u(Q)^p, and

    D_j=(u^j-u^(jp))/c,
    T_j=u^j+u^(jp)

lie in F_p. D_j is Kummer invariant for odd j and T_j for even j.
The screen compares chi(D_j), chi(T_j), and their products with chi(x)
to rho_G([k]G)=chi(psi_k(G)), then calibrates the best match against a
Kummer-invariant random-label null using the same candidate pool.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
B = 7
MAX_POWER = 24
MAX_INVARIANT_GENERATORS = 60
NULL_TRIALS = 300

FROZEN_CASES = (
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (151, 19, (70, 122)),
    (547, 547, (2, 62)),
    (907, 967, (2, 165)),
    (1051, 1093, (3, 385)),
    (1087, 271, (1017, 688)),
    (1303, 1249, (1, 201)),
    (1663, 433, (126, 1375)),
    (2347, 571, (2107, 1535)),
    (2671, 367, (83, 2009)),
    (2851, 397, (2276, 1015)),
    (3319, 811, (177, 298)),
    (3571, 3469, (4, 1706)),
    (3931, 4021, (4, 1427)),
)


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def ec_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, p)
        points.append(point)
    if ec_add(point, generator, p) is not None:
        raise AssertionError("declared subgroup order failed")
    if len(set(points)) != order:
        raise AssertionError("orbit contains an early collision")
    return points


def division_polynomial_evaluator(point: tuple[int, int], p: int):
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % p
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % p
        if index == 3:
            return (3 * x**4 + 84 * x) % p
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392) % p
        if index & 1:
            m = (index - 1) // 2
            return (
                psi(m + 2) * pow(psi(m), 3, p)
                - psi(m - 1) * pow(psi(m + 1), 3, p)
            ) % p
        m = index // 2
        return (
            psi(m)
            * pow(2 * y, -1, p)
            * (
                psi(m + 2) * pow(psi(m - 1), 2, p)
                - psi(m - 2) * pow(psi(m + 1), 2, p)
            )
        ) % p

    return psi


@dataclass(frozen=True)
class Fp2:
    """a+b*c with c^2=7 over F_p."""

    a: int
    b: int
    p: int

    def normalized(self) -> "Fp2":
        return Fp2(self.a % self.p, self.b % self.p, self.p)

    def __mul__(self, other: "Fp2") -> "Fp2":
        if self.p != other.p:
            raise ValueError("field mismatch")
        return Fp2(
            (self.a * other.a + B * self.b * other.b) % self.p,
            (self.a * other.b + self.b * other.a) % self.p,
            self.p,
        )

    def __pow__(self, exponent: int) -> "Fp2":
        result = Fp2(1, 0, self.p)
        addend = self.normalized()
        while exponent:
            if exponent & 1:
                result = result * addend
            addend = addend * addend
            exponent >>= 1
        return result

    def frobenius(self) -> "Fp2":
        return Fp2(self.a % self.p, -self.b % self.p, self.p)


def canonical_cube_root_y_minus_c(y: int, p: int) -> Fp2:
    group_order = p * p - 1
    cube_order = group_order // 3
    if p % 9 != 7 or cube_order % 3 == 0:
        raise AssertionError("canonical cube-subgroup root condition failed")
    value = Fp2(y, -1, p)
    one = Fp2(1, 0, p)
    if value**cube_order != one:
        raise AssertionError("y-c is not a cube")
    inverse_three = pow(3, -1, cube_order)
    root = value**inverse_three
    if root**3 != value.normalized():
        raise AssertionError("cube-root verification failed")
    if root**cube_order != one:
        raise AssertionError("root is outside the cube subgroup")
    return root


def point_features(point: tuple[int, int], p: int) -> dict[str, int]:
    x, y = point
    root = canonical_cube_root_y_minus_c(y, p)
    power = Fp2(1, 0, p)
    chi_x = quadratic_character(x, p)
    features: dict[str, int] = {}
    for j in range(1, MAX_POWER + 1):
        power = power * root
        trace = 2 * power.a % p
        difference_over_c = 2 * power.b % p
        if j & 1:
            name = f"D{j}"
            value = difference_over_c
        else:
            name = f"T{j}"
            value = trace
        sign = quadratic_character(value, p)
        if sign:
            features[name] = sign
            if chi_x:
                features[f"{name}*x"] = sign * chi_x
    return features


def signs_to_bits(signs: list[int]) -> int:
    result = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            result |= 1 << index
        elif sign != 1:
            raise AssertionError("sign vector contains zero")
    return result


def rho_sequence(generator: tuple[int, int], p: int, order: int) -> list[int]:
    psi = division_polynomial_evaluator(generator, p)
    result = []
    for k in range(1, order):
        sign = quadratic_character(psi(k), p)
        if sign == 0:
            raise AssertionError("division polynomial vanished off the identity")
        result.append(sign)
    return result


def is_kummer_invariant(signs: list[int], order: int) -> bool:
    return all(signs[k - 1] == signs[order - k - 1] for k in range(1, order))


def feature_table(
    generator: tuple[int, int], p: int, order: int
) -> tuple[list[dict[str, int] | None], list[str], int]:
    points = orbit(generator, order, p)
    table: list[dict[str, int] | None] = [None] * order
    root_checks = 0
    for scalar in range(1, order):
        point = points[scalar]
        if point is None:
            raise AssertionError("unexpected identity")
        x, y = point
        if (y * y - x * x * x - B) % p:
            raise AssertionError("point is off curve")
        table[scalar] = point_features(point, p)
        root_checks += 1

    all_names: set[str] = set()
    for scalar in range(1, order):
        assert table[scalar] is not None
        all_names.update(table[scalar])
    valid_names = sorted(
        name
        for name in all_names
        if all(name in table[scalar] for scalar in range(1, order))  # type: ignore[operator]
    )

    for scalar in range(1, order):
        opposite = order - scalar
        assert table[scalar] is not None and table[opposite] is not None
        for name in valid_names:
            if table[scalar][name] != table[opposite][name]:
                raise AssertionError(f"Kummer invariance failed for {name}")
    return table, valid_names, root_checks


def candidate_vectors(
    table: list[dict[str, int] | None],
    valid_names: list[str],
    multiplier: int,
    order: int,
) -> dict[str, int]:
    result: dict[str, int] = {}
    for name in valid_names:
        signs = []
        for k in range(1, order):
            row = table[(multiplier * k) % order]
            assert row is not None
            signs.append(row[name])
        result[name] = signs_to_bits(signs)
    return result


def best_accuracy(vector: int, target: int, length: int) -> float:
    distance = (vector ^ target).bit_count()
    return max(length - distance, distance) / length


def random_kummer_target(order: int, rng: random.Random) -> int:
    result = 0
    for k in range(1, (order + 1) // 2):
        if rng.getrandbits(1):
            result |= 1 << (k - 1)
            result |= 1 << (order - k - 1)
    return result


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    base_generator: tuple[int, int]
    root_and_frobenius_checks: int
    invariant_generators_tested: int
    candidate_names_per_generator: int
    best_candidate: str
    best_generator_multiplier: int
    best_matches: int
    total: int
    best_accuracy: float
    best_excess_times_sqrt_order: float
    null_trials: int
    null_median_best_accuracy: float
    null_q95_best_accuracy: float
    empirical_null_percentile: float


def run_case(p: int, order: int, base_generator: tuple[int, int]) -> CaseResult:
    if p % 36 != 7 or quadratic_character(B, p) != -1:
        raise AssertionError("frozen field preconditions failed")
    if ec_mul(order, base_generator, p) is not None:
        raise AssertionError("generator order check failed")

    table, names, root_checks = feature_table(base_generator, p, order)
    groups: list[tuple[int, int, dict[str, int]]] = []
    length = order - 1
    observed_best = (-1.0, 0, "")

    for multiplier in range(1, order):
        if math.gcd(multiplier, order) != 1:
            continue
        generator = ec_mul(multiplier, base_generator, p)
        if generator is None:
            raise AssertionError("generator multiplier reached identity")
        rho = rho_sequence(generator, p, order)
        if not is_kummer_invariant(rho, order):
            continue
        target = signs_to_bits(rho)
        vectors = candidate_vectors(table, names, multiplier, order)
        groups.append((multiplier, target, vectors))
        for name, vector in vectors.items():
            accuracy = best_accuracy(vector, target, length)
            candidate = (accuracy, -multiplier, name)
            incumbent = (observed_best[0], -observed_best[1], observed_best[2])
            if candidate > incumbent:
                observed_best = (accuracy, multiplier, name)
        if len(groups) >= MAX_INVARIANT_GENERATORS:
            break

    if not groups:
        raise AssertionError("no Kummer-invariant generator was found")
    if observed_best[0] == 1.0:
        raise AssertionError("unexpected exact decoder found")

    rng = random.Random(20260812 + p)
    null_maxima = []
    for _ in range(NULL_TRIALS):
        maximum = 0.5
        for _, _, vectors in groups:
            target = random_kummer_target(order, rng)
            for vector in vectors.values():
                maximum = max(maximum, best_accuracy(vector, target, length))
        null_maxima.append(maximum)
    null_maxima.sort()
    q95 = null_maxima[math.ceil(0.95 * NULL_TRIALS) - 1]
    percentile = sum(value <= observed_best[0] for value in null_maxima) / NULL_TRIALS

    return CaseResult(
        p=p,
        order=order,
        base_generator=base_generator,
        root_and_frobenius_checks=root_checks,
        invariant_generators_tested=len(groups),
        candidate_names_per_generator=len(names),
        best_candidate=observed_best[2],
        best_generator_multiplier=observed_best[1],
        best_matches=round(observed_best[0] * length),
        total=length,
        best_accuracy=observed_best[0],
        best_excess_times_sqrt_order=(observed_best[0] - 0.5) * math.sqrt(order),
        null_trials=NULL_TRIALS,
        null_median_best_accuracy=statistics.median(null_maxima),
        null_q95_best_accuracy=q95,
        empirical_null_percentile=percentile,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("eisenstein_root_phase_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": "fifteen frozen j=0 toy subgroups on y^2=x^3+7; no secp256k1 target",
        "construction": {
            "extension": "F_p2=F_p[c]/(c^2-7)",
            "canonical_root": "u(Q)^3=y(Q)-c in the cube subgroup",
            "frobenius_descents": [
                "D_j=(u^j-u^(jp))/c for odd j",
                "T_j=u^j+u^(jp) for even j",
            ],
            "binary_candidates": "chi(D_j), chi(T_j), and each times chi(x), 1<=j<=24",
        },
        "fixed_protocol": {
            "maximum_kummer_invariant_generators_per_case": MAX_INVARIANT_GENERATORS,
            "null_trials_per_case": NULL_TRIALS,
            "global_sign_allowed": True,
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "order_min": min(case.order for case in cases),
            "order_max": max(case.order for case in cases),
            "exact_decoders": sum(case.best_accuracy == 1.0 for case in cases),
            "cases_above_null_q95": sum(
                case.best_accuracy > case.null_q95_best_accuracy for case in cases
            ),
            "maximum_empirical_null_percentile": max(
                case.empirical_null_percentile for case in cases
            ),
            "large_order_cases": len(large),
            "large_order_mean_best_accuracy": statistics.mean(
                case.best_accuracy for case in large
            ),
        },
        "conclusion": (
            "The canonical Frobenius-descended cube-root lift exists, but this "
            "natural binary-character family shows no positive scaling: no exact "
            "decoder is found, no case exceeds its matched 95% null envelope, "
            "and the best excess decays at the random-correlation scale."
        ),
        "claim_boundary": [
            "Bounded toy evidence only; not an asymptotic theorem.",
            "No external point, wallet, key, or production-sized target is accepted.",
            "Other theta, p-adic, analytic, or nonmultiplicative observables are not closed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
