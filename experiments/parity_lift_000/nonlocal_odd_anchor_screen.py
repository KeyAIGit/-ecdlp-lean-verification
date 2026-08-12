#!/usr/bin/env python3
"""Toy-only screen for NONLOCAL-ODD-ANCHOR-004.

Scope:
  * frozen prime-order subgroups on E/F_p: y^2 = x^3 + 7;
  * no external curve, point, key, wallet, or production-sized target;
  * test the first genuinely odd GLV-orbit EDS aggregate and the exact
    carry-cocycle obstruction for affine elliptic-net pullbacks.

The hidden target is rho_G([k]G) = chi(psi_k(G)).  On Kummer-invariant
instances, the order-three GLV orbit gives the odd aggregate

    R3(k) = rho(k) rho(lambda*k) rho(lambda^2*k).

R3 is invariant under Q -> -Q and under the order-three GLV orbit, so it is a
well-defined function on C6-orbits.  It contains three hidden EDS-residue
factors, hence has odd gauge weight.  The screen asks whether the smallest
natural public GLV-invariant characters chi(x(Q)^3 + a) decode it.

The script also verifies the exact carry identities that make every fixed
rank-two affine net pullback collapse to already-public point-function labels.
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
NULL_TRIALS = 200

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
        if y1 % p == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, p)
        points.append(point)
    if ec_add(point, generator, p) is not None:
        raise AssertionError("declared order failed")
    if len(set(points)) != order:
        raise AssertionError("early orbit collision")
    return points


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


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


def primitive_cube_root(p: int) -> int:
    if (p - 1) % 3:
        raise AssertionError("field has no nontrivial cube root of unity")
    for seed in range(2, p):
        beta = pow(seed, (p - 1) // 3, p)
        if beta != 1 and pow(beta, 3, p) == 1:
            return beta
    raise AssertionError("primitive cube root not found")


def sign_vector_to_bits(signs: list[int]) -> int:
    result = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            result |= 1 << index
        elif sign != 1:
            raise AssertionError("non-binary sign")
    return result


def berlekamp_massey_complexity(signs: list[int]) -> int:
    """Linear complexity over F_2 after +1 -> 0 and -1 -> 1."""
    bits = [0 if sign == 1 else 1 for sign in signs]
    connection = 1
    previous = 1
    length = 0
    last_update = -1
    for index in range(len(bits)):
        discrepancy = bits[index]
        for offset in range(1, length + 1):
            if (connection >> offset) & 1:
                discrepancy ^= bits[index - offset]
        if discrepancy:
            old = connection
            connection ^= previous << (index - last_update)
            if 2 * length <= index:
                length = index + 1 - length
                previous = old
                last_update = index
    return length


def random_c6_target(order: int, lam: int, rng: random.Random) -> int:
    values = [1] * order
    visited: set[int] = set()
    for scalar in range(1, order):
        if scalar in visited:
            continue
        l1 = lam * scalar % order
        l2 = lam * l1 % order
        orbit6 = {
            scalar,
            order - scalar,
            l1,
            order - l1,
            l2,
            order - l2,
        }
        visited.update(orbit6)
        sign = -1 if rng.getrandbits(1) else 1
        for member in orbit6:
            values[member] = sign
    return sign_vector_to_bits(values[1:])


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    status: str
    beta: int
    lam: int
    rho_kummer_invariant: bool
    c3_triple_kummer_invariant: bool
    c3_triple_glv_invariant: bool
    carry_complement_checks: int
    affine_carry_cancellation_checks: int
    c3_orbits: int
    rho_linear_complexity: int
    c3_linear_complexity: int
    prefix_linear_complexity: int
    invariant_character_candidates: int
    exact_single_decoder: bool
    exact_pair_decoder: bool
    best_single_accuracy: float
    null_trials: int
    null_median_best_accuracy: float
    null_q95_best_accuracy: float
    empirical_null_percentile: float


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]
    if any(sign not in (-1, 1) for sign in rho[1:]):
        raise AssertionError("rho vanished off the identity")

    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    glv_point = (beta * generator[0] % p, generator[1])
    lam = point_to_scalar[glv_point]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("GLV scalar does not have order three")

    rho_kummer = all(rho[k] == rho[order - k] for k in range(1, order))
    if not rho_kummer:
        return CaseResult(
            p=p,
            order=order,
            generator=generator,
            status="excluded_non_kummer_residue",
            beta=beta,
            lam=lam,
            rho_kummer_invariant=False,
            c3_triple_kummer_invariant=False,
            c3_triple_glv_invariant=False,
            carry_complement_checks=0,
            affine_carry_cancellation_checks=0,
            c3_orbits=0,
            rho_linear_complexity=berlekamp_massey_complexity(rho[1:]),
            c3_linear_complexity=0,
            prefix_linear_complexity=0,
            invariant_character_candidates=0,
            exact_single_decoder=False,
            exact_pair_decoder=False,
            best_single_accuracy=0.0,
            null_trials=0,
            null_median_best_accuracy=0.0,
            null_q95_best_accuracy=0.0,
            empirical_null_percentile=0.0,
        )

    point_scale_character = -1

    triple = [0] * order
    carry = [0] * order
    carry_checks = 0
    affine_checks = 0

    for k in range(1, order):
        k1 = lam * k % order
        k2 = lam * k1 % order
        scalar_sum = k + k1 + k2
        if scalar_sum not in (order, 2 * order):
            raise AssertionError("GLV canonical lifts do not sum to n or 2n")
        carry[k] = scalar_sum // order
        triple[k] = rho[k] * rho[k1] * rho[k2]

        for a in range(-4, 5):
            for b in range(-4, 5):
                linear = a + b * k
                t = linear % order
                if t == 0:
                    continue
                c = (linear - t) // order
                if b & 1:
                    if (c + t + k - a) % 2:
                        raise AssertionError("odd-affine carry parity failed")
                    left = (
                        (point_scale_character if c & 1 else 1)
                        * rho[t]
                        * rho[k]
                    )
                    public = (
                        (point_scale_character if t & 1 else 1)
                        * rho[t]
                        * (point_scale_character if k & 1 else 1)
                        * rho[k]
                    )
                else:
                    if (c + t - a) % 2:
                        raise AssertionError("even-affine carry parity failed")
                    left = (
                        (point_scale_character if c & 1 else 1)
                        * rho[t]
                    )
                    public = (
                        (point_scale_character if t & 1 else 1)
                        * rho[t]
                    )
                fixed = point_scale_character if a & 1 else 1
                if left != fixed * public:
                    raise AssertionError("affine carry-cocycle cancellation failed")
                affine_checks += 1

    for k in range(1, order):
        if carry[order - k] != 3 - carry[k]:
            raise AssertionError("GLV carry complement failed")
        carry_checks += 1

    triple_kummer = all(
        triple[k] == triple[order - k] for k in range(1, order)
    )
    triple_glv = all(
        triple[k] == triple[lam * k % order] for k in range(1, order)
    )
    if not triple_kummer or not triple_glv:
        raise AssertionError("C3 residue aggregate lost its required symmetry")

    c3_orbits = {
        tuple(sorted({k, lam * k % order, lam * lam * k % order}))
        for k in range(1, order)
    }

    prefix = []
    running = 1
    for k in range(1, order):
        running *= rho[k]
        prefix.append(running)

    target = sign_vector_to_bits(triple[1:])
    complement = (1 << (order - 1)) - 1

    candidates: dict[int, int] = {}
    for shift in range(p):
        signs = []
        for k in range(1, order):
            point = points[k]
            assert point is not None
            value = quadratic_character(pow(point[0], 3, p) + shift, p)
            if value == 0:
                break
            signs.append(value)
        else:
            candidates.setdefault(sign_vector_to_bits(signs), shift)

    candidate_vectors = set(candidates)
    exact_single = target in candidate_vectors or (target ^ complement) in candidate_vectors
    exact_pair = False
    for vector in candidate_vectors:
        if (
            target ^ vector in candidate_vectors
            or target ^ complement ^ vector in candidate_vectors
        ):
            exact_pair = True
            break

    def best_accuracy(label: int) -> float:
        best = 0.5
        for vector in candidate_vectors:
            distance = (vector ^ label).bit_count()
            best = max(best, max(distance, order - 1 - distance) / (order - 1))
        return best

    observed = best_accuracy(target)
    rng = random.Random(20260812 + p + order)
    null = [
        best_accuracy(random_c6_target(order, lam, rng))
        for _ in range(NULL_TRIALS)
    ]
    null.sort()
    q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]
    percentile = sum(value <= observed for value in null) / NULL_TRIALS

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        status="screened",
        beta=beta,
        lam=lam,
        rho_kummer_invariant=True,
        c3_triple_kummer_invariant=triple_kummer,
        c3_triple_glv_invariant=triple_glv,
        carry_complement_checks=carry_checks,
        affine_carry_cancellation_checks=affine_checks,
        c3_orbits=len(c3_orbits),
        rho_linear_complexity=berlekamp_massey_complexity(rho[1:]),
        c3_linear_complexity=berlekamp_massey_complexity(triple[1:]),
        prefix_linear_complexity=berlekamp_massey_complexity(prefix),
        invariant_character_candidates=len(candidate_vectors),
        exact_single_decoder=exact_single,
        exact_pair_decoder=exact_pair,
        best_single_accuracy=observed,
        null_trials=NULL_TRIALS,
        null_median_best_accuracy=statistics.median(null),
        null_q95_best_accuracy=q95,
        empirical_null_percentile=percentile,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("nonlocal_odd_anchor_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    screened = [case for case in cases if case.status == "screened"]

    payload = {
        "scope": (
            "fifteen frozen prime-order j=0 toy subgroups on y^2=x^3+7; "
            "only Kummer-invariant EDS-residue cases enter the odd-anchor screen"
        ),
        "package": "NONLOCAL-ODD-ANCHOR-004",
        "hidden_target": "rho_G([k]G)=chi(psi_k(G))",
        "odd_aggregate": (
            "R3(Q)=rho_G(Q)*rho_G(phi(Q))*rho_G(phi^2(Q)); "
            "three nonpublic EDS-residue factors"
        ),
        "exact_carry_identity": (
            "for L=a+b*k=t+c*n, fixed affine rank-two net pullbacks reduce "
            "after canonicalization to s^a times public point-function labels"
        ),
        "public_candidate_family": "chi(x(Q)^3+a), a in F_p, plus exact pairs",
        "protocol": {
            "null_trials_per_case": NULL_TRIALS,
            "null_labels": "random labels constant on each C6 orbit",
            "global_sign_allowed": True,
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases_total": len(cases),
            "cases_screened": len(screened),
            "non_kummer_cases_excluded": len(cases) - len(screened),
            "carry_complement_checks": sum(
                case.carry_complement_checks for case in screened
            ),
            "affine_carry_cancellation_checks": sum(
                case.affine_carry_cancellation_checks for case in screened
            ),
            "all_c3_aggregates_have_required_symmetry": all(
                case.c3_triple_kummer_invariant
                and case.c3_triple_glv_invariant
                for case in screened
            ),
            "exact_single_decoders": sum(
                case.exact_single_decoder for case in screened
            ),
            "exact_pair_decoders": sum(
                case.exact_pair_decoder for case in screened
            ),
            "cases_above_matched_null_q95": sum(
                case.best_single_accuracy > case.null_q95_best_accuracy
                for case in screened
            ),
            "maximum_empirical_null_percentile": max(
                case.empirical_null_percentile for case in screened
            ),
            "largest_order": max(case.order for case in screened),
        },
        "conclusion": (
            "The C3 orbit product is the first explicit Kummer-invariant object "
            "in this line with odd EDS-residue gauge weight. It is not decoded "
            "by the smallest natural GLV-invariant character algebra, and its "
            "linear complexity remains approximately half the orbit length. "
            "Every fixed affine rank-two net pullback still collapses exactly "
            "because the period carry cocycle restores the point-function gauge."
        ),
        "claim_boundary": [
            "Bounded toy structural evidence, not an asymptotic theorem.",
            "R3 is a sharply localized hidden target, not a public algorithm.",
            "The screen does not cover unbounded-degree circuits, global theta monodromy, p-adic continuation, or arbitrary nonlocal sections.",
            "No external point, key, wallet, or production-sized target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
