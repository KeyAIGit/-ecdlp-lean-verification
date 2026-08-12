#!/usr/bin/env python3
"""Toy-only covariance and generator-blindness audit for package 027.

The public subgroup H=<G> is unchanged when G is replaced by [u]G.  The
generator-relative GLV carry is not unchanged: if Q=[k]G then its label relative
to G'=[u]G is the original carry at [u^{-1}]Q.  Consequently the oriented
half-kernel root set is transported by [u].

This screen exhaustively checks the covariance on the frozen j=0 toy groups,
counts distinct generator-oriented signatures, and verifies that:
  * the stabilizer of one signature is exactly <lambda>;
  * the complementary signature is exactly the coset -<lambda>;
  * G and -G have the same subgroup/kernel but opposite oriented root halves.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    orbit,
    primitive_cube_root,
)


def carry_sign(k: int, lam: int, order: int) -> int:
    k %= order
    if k == 0:
        raise ValueError("carry is defined only on nonzero scalars")
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("canonical GLV representatives did not sum to n or 2n")


def c3_orbit(k: int, lam: int, order: int) -> frozenset[int]:
    lam2 = lam * lam % order
    return frozenset((k % order, lam * k % order, lam2 * k % order))


def c6_orbit(k: int, lam: int, order: int) -> frozenset[int]:
    positive = c3_orbit(k, lam, order)
    return frozenset(positive | {(-member) % order for member in positive})


def c6_representatives(lam: int, order: int) -> list[int]:
    return sorted(
        {
            min(c6_orbit(k, lam, order) - {0})
            for k in range(1, order)
        }
    )


def orientation_signature(
    generator_multiplier: int,
    representatives: list[int],
    lam: int,
    order: int,
) -> int:
    inverse = pow(generator_multiplier, -1, order)
    signature = 0
    for index, scalar in enumerate(representatives):
        if carry_sign(inverse * scalar % order, lam, order) == 1:
            signature |= 1 << index
    return signature


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    c6_orbits: int
    orientation_signatures: int
    expected_signatures_mod_c3: int
    same_signature_stabilizer: tuple[int, ...]
    expected_c3_stabilizer: tuple[int, ...]
    opposite_signature_coset: tuple[int, ...]
    expected_negative_c3_coset: tuple[int, ...]
    generator_covariance_checks: int
    generator_covariance_exact: bool
    negation_root_covariance_exact: bool
    kernel_blind_collision_witnessed: bool


def run_case(
    p: int,
    order: int,
    generator: tuple[int, int],
) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order
    if {1, lam, lam2} == {0} or pow(lam, 3, order) != 1 or lam == 1:
        raise AssertionError("invalid order-three GLV scalar")

    representatives = c6_representatives(lam, order)
    expected_orbits = (order - 1) // 6
    if len(representatives) != expected_orbits:
        raise AssertionError("C6 orbit count changed")

    base_signature = orientation_signature(1, representatives, lam, order)
    complement_mask = (1 << len(representatives)) - 1
    complement_signature = base_signature ^ complement_mask

    signatures: dict[int, int] = {}
    covariance_checks = 0
    covariance_exact = True
    for u in range(1, order):
        inverse = pow(u, -1, order)
        signatures[u] = orientation_signature(u, representatives, lam, order)
        for scalar in range(1, order):
            transported = u * scalar % order
            if carry_sign(inverse * transported % order, lam, order) != carry_sign(
                scalar, lam, order
            ):
                covariance_exact = False
                break
            covariance_checks += 1
        if not covariance_exact:
            break

    same = tuple(
        sorted(u for u, signature in signatures.items() if signature == base_signature)
    )
    opposite = tuple(
        sorted(
            u
            for u, signature in signatures.items()
            if signature == complement_signature
        )
    )
    expected_same = tuple(sorted({1, lam, lam2}))
    expected_opposite = tuple(
        sorted({(-1) % order, (-lam) % order, (-lam2) % order})
    )

    # Direct root-half check for G versus -G.  Each C6 orbit consists of one
    # horizontal C3 orbit with y and its negative with -y.
    visited: set[int] = set()
    roots_g: list[int] = []
    roots_neg_g: list[int] = []
    for scalar in range(1, order):
        if scalar in visited:
            continue
        positive = c3_orbit(scalar, lam, order)
        negative = {(-member) % order for member in positive}
        visited.update(positive | negative)
        point = points[scalar]
        if point is None:
            raise AssertionError("nonzero scalar mapped to identity")
        y = point[1]
        if any(points[member][1] != y for member in positive):
            raise AssertionError("GLV C3 orbit lost its common y coordinate")
        if any(points[member][1] != (-y) % p for member in negative):
            raise AssertionError("negative C3 orbit lost its -y coordinate")
        if carry_sign(scalar, lam, order) == 1:
            roots_g.append(y)
            roots_neg_g.append((-y) % p)
        else:
            roots_g.append((-y) % p)
            roots_neg_g.append(y)

    negation_root_covariance = sorted(roots_neg_g) == sorted(
        (-root) % p for root in roots_g
    )

    distinct = len(set(signatures.values()))
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        c6_orbits=len(representatives),
        orientation_signatures=distinct,
        expected_signatures_mod_c3=(order - 1) // 3,
        same_signature_stabilizer=same,
        expected_c3_stabilizer=expected_same,
        opposite_signature_coset=opposite,
        expected_negative_c3_coset=expected_opposite,
        generator_covariance_checks=covariance_checks,
        generator_covariance_exact=covariance_exact,
        negation_root_covariance_exact=negation_root_covariance,
        kernel_blind_collision_witnessed=(
            base_signature != complement_signature
            and expected_same == same
            and expected_opposite == opposite
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "generator_oriented_half_kernel_covariance_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; exhaustive generator "
            "reindexing; no external point, key, wallet, or production target"
        ),
        "package": "GENERATOR-ORIENTED-HALF-KERNEL-027",
        "exact_covariance": (
            "S_[uG] = [u] S_G, equivalently "
            "g_[uG](Q)=g_G([u^-1]Q)"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "largest_order": max(case.order for case in cases),
            "generator_covariance_checks": sum(
                case.generator_covariance_checks for case in cases
            ),
            "all_generator_covariance_exact": all(
                case.generator_covariance_exact for case in cases
            ),
            "all_negation_root_covariance_exact": all(
                case.negation_root_covariance_exact for case in cases
            ),
            "all_signature_counts_equal_n_minus_1_over_3": all(
                case.orientation_signatures
                == case.expected_signatures_mod_c3
                for case in cases
            ),
            "all_stabilizers_equal_C3": all(
                case.same_signature_stabilizer
                == case.expected_c3_stabilizer
                for case in cases
            ),
            "all_complement_cosets_equal_negative_C3": all(
                case.opposite_signature_coset
                == case.expected_negative_c3_coset
                for case in cases
            ),
            "all_kernel_blind_collisions_witnessed": all(
                case.kernel_blind_collision_witnessed for case in cases
            ),
        },
        "decision": (
            "A construction depending only on the subgroup kernel or its CM "
            "isogeny cannot select the generator-oriented half: G and -G have "
            "the same kernel but require complementary factors. Any surviving "
            "theta/CM construction must include an explicit generator-sensitive "
            "linearization or equivalent dual-character datum."
        ),
        "claim_boundary": [
            "The abstract G versus -G contradiction is a theorem; the exact full stabilizer counts are exhaustive toy evidence.",
            "The screen does not prove that every generator-sensitive circuit is expensive.",
            "The screen does not construct a carry, R3, parity, or discrete-log decoder.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
