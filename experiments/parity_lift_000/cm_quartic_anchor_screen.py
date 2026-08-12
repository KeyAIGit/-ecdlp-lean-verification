#!/usr/bin/env python3
"""Frozen toy screen for an absolute quartic CM root phase.

The screen accepts no external curves, points, keys, wallets, or production
instances. It compares

    kappa(P) = x(P)^((p-1)/4) in {+1,-1}

with the EDS residue

    rho_G([k]G) = chi(psi_k(G))

on four fixed j=1728 curves y^2=x^3+A*x over p=1 mod 4.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path

Point = tuple[int, int] | None

FROZEN_CASES = (
    ("J1728-P569-A1-R17", 569, 1, 17, (562, 315)),
    ("J1728-P953-A4-R29", 953, 4, 29, (142, 278)),
    ("J1728-P2477-A1-R37", 2477, 1, 37, (948, 2124)),
    ("J1728-P569-A3-R53", 569, 3, 53, (319, 470)),
)


def add(P: Point, Q: Point, p: int, A: int) -> Point:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def mul(k: int, P: Point, p: int, A: int) -> Point:
    result: Point = None
    addend = P
    while k:
        if k & 1:
            result = add(result, addend, p, A)
        addend = add(addend, addend, p, A)
        k >>= 1
    return result


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def division_polynomial(point: tuple[int, int], p: int, A: int):
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
            return (3 * x**4 + 6 * A * x**2 - A**2) % p
        if index == 4:
            return 4 * y * (x**6 + 5 * A * x**4 - 5 * A**2 * x**2 - A**3) % p
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


def quartic_phase(point: tuple[int, int], p: int) -> int:
    x = point[0] % p
    if p % 4 != 1 or quadratic_character(x, p) != 1:
        raise AssertionError("quartic phase is not defined on this frozen point")
    value = pow(x, (p - 1) // 4, p)
    if value == 1:
        return 1
    if value == p - 1:
        return -1
    raise AssertionError("square x-coordinate did not yield a sign")


def run_case(case_id: str, p: int, A: int, order: int, base: tuple[int, int]) -> dict:
    if (base[1] * base[1] - base[0] ** 3 - A * base[0]) % p:
        raise AssertionError("frozen generator is off curve")
    if mul(order, base, p, A) is not None:
        raise AssertionError("frozen generator has the wrong order")

    rows = []
    for multiplier in range(1, order):
        generator = mul(multiplier, base, p, A)
        assert generator is not None
        psi = division_polynomial(generator, p, A)
        rho = [quadratic_character(psi(k), p) for k in range(1, order)]
        points = [mul(k, generator, p, A) for k in range(1, order)]
        if any(point is None for point in points) or 0 in rho:
            raise AssertionError("invalid frozen subgroup orbit")
        phase = [quartic_phase(point, p) for point in points if point is not None]

        direct = sum(left == right for left, right in zip(phase, rho))
        negated = order - 1 - direct
        best = max(direct, negated)
        rows.append(
            {
                "multiplier": multiplier,
                "multiplier_quadratic_character_mod_order": (
                    1 if pow(multiplier, (order - 1) // 2, order) == 1 else -1
                ),
                "best_matches": best,
                "total": order - 1,
                "best_accuracy": best / (order - 1),
                "global_sign": 1 if direct >= negated else -1,
                "exact": best == order - 1,
            }
        )

    maximum = max(row["best_accuracy"] for row in rows)
    return {
        "id": case_id,
        "p": p,
        "A": A,
        "B": 0,
        "order": order,
        "generator": list(base),
        "exact_generator_multipliers": [
            row["multiplier"] for row in rows if row["exact"]
        ],
        "maximum_accuracy": maximum,
        "best_matches": max(row["best_matches"] for row in rows),
        "total": order - 1,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("cm_quartic_anchor_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    positive = cases[0]
    expected_exact = [1, 2, 4, 8, 9, 13, 15, 16]
    if positive["exact_generator_multipliers"] != expected_exact:
        raise AssertionError("frozen order-17 positive witness drifted")
    if any(case["exact_generator_multipliers"] for case in cases[1:]):
        raise AssertionError("a larger frozen control unexpectedly became exact")

    payload = {
        "scope": "four frozen toy j=1728 curves only; no secp256k1 target",
        "observable": "kappa(P)=x(P)^((p-1)/4) in {+1,-1}",
        "target": "rho_G([k]G)=chi(psi_k(G))",
        "cases": cases,
        "aggregate": {
            "positive_case_order": 17,
            "positive_case_exact_generators": len(
                positive["exact_generator_multipliers"]
            ),
            "larger_control_orders": [29, 37, 53],
            "larger_controls_with_exact_generator": 0,
        },
        "claim_boundary": [
            "This is bounded positive toy evidence, not an asymptotic result.",
            "The exact order-17 match does not persist in the three frozen larger controls.",
            "The construction uses j=1728, rational 2-torsion, and a quartic character.",
            "secp256k1 has j=0, no rational 2-torsion, and p congruent to 3 modulo 4.",
            "No external curve, key, wallet, or production-sized target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
