#!/usr/bin/env python3
"""Lightweight exact index-space replay for UORC056 C16.

No curve point, unknown scalar, wallet, private key, or external target is
accepted. The script verifies the odd GLV norm support and degree theorem on
six frozen prime orders and records the exact secp256k1 lower bound.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FROZEN_ORDERS = (19, 31, 67, 271, 397, 433)
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)


def primitive(n: int) -> list[int]:
    m = (n - 1) // 2
    return [
        -1 if (k & 1 and 1 <= k <= m)
        else 1 if (not (k & 1) and m < k < n)
        else 0
        for k in range(n)
    ]


def class_index(n: int) -> int:
    if n % 4 == 3:
        r = (n + 1) // 4
        return r * (2 * r - 1) % n
    r = (n - 1) // 4
    return r * (2 * r + 1) % n


def endpoint_and_exception(n: int) -> tuple[list[int], list[int]]:
    m = (n - 1) // 2
    a = class_index(n)
    d = primitive(n)
    gauge = d[:]
    gauge[a] -= 1
    gauge[0] += 1
    z = [gauge[k] - gauge[(k + 1) % n] for k in range(n)]
    exception = [0] * n
    exception[m] += 1
    exception[a] += 1
    exception[n - 1] += 1
    exception[(a - 1) % n] -= 1
    exception[0] -= 1
    parity = [1 if k % 2 == 0 else -1 for k in range(n)]
    if z != [parity[k] - exception[k] for k in range(n)]:
        raise AssertionError("endpoint decomposition failed")
    return z, exception


def roots(n: int) -> list[int]:
    return [x for x in range(2, n) if (x * x + x + 1) % n == 0]


def orbits(n: int, lam: int) -> list[list[int]]:
    visited = {0}
    out = []
    for k in range(1, n):
        if k in visited:
            continue
        orbit = [k, lam * k % n, lam * lam * k % n]
        if len(set(orbit)) != 3:
            raise AssertionError("bad orbit")
        visited.update(orbit)
        out.append(orbit)
    if len(visited) != n:
        raise AssertionError("orbit cover failed")
    return out


def check_order(n: int) -> dict[str, object]:
    z, exception = endpoint_and_exception(n)
    exception_support = {k for k, value in enumerate(exception) if value}
    rows = []
    for lam in roots(n):
        orbit_rows = orbits(n, lam)
        nonzero = 0
        positive = max(z[0], 0)
        negative = max(-z[0], 0)
        exceptional = 0
        guaranteed = 0
        histogram: dict[str, int] = {}
        for orbit in orbit_rows:
            coefficient = sum(z[k] for k in orbit)
            histogram[str(coefficient)] = histogram.get(str(coefficient), 0) + 1
            if coefficient:
                nonzero += 1
                positive += max(coefficient, 0)
                negative += max(-coefficient, 0)
            if exception_support.intersection(orbit):
                exceptional += 1
            else:
                parity_sum = sum(1 if k % 2 == 0 else -1 for k in orbit)
                if coefficient != parity_sum or coefficient == 0:
                    raise AssertionError("nonexceptional odd sum vanished")
                guaranteed += 1
        if positive != negative:
            raise AssertionError("descended divisor degree mismatch")
        total = (n - 1) // 3
        support_bound = total - min(4, total)
        pole_bound = (support_bound + 1) // 2
        if guaranteed < support_bound or nonzero < support_bound or negative < pole_bound:
            raise AssertionError("odd norm lower bound failed")
        rows.append({
            "lambda": lam,
            "total_orbits": total,
            "exceptional_orbits": exceptional,
            "guaranteed_nonzero_orbits": guaranteed,
            "actual_nonzero_orbits": nonzero,
            "coefficient_histogram": dict(sorted(histogram.items(), key=lambda item: int(item[0]))),
            "descended_pole_degree": negative,
            "support_lower_bound": support_bound,
            "pole_degree_lower_bound": pole_bound,
        })
    if len(rows) != 2:
        raise AssertionError("expected two order-three roots")
    return {
        "n": n,
        "exception_support": sorted(exception_support),
        "roots": rows,
        "passed": True,
    }


def secp() -> dict[str, object]:
    n = SECP_N
    total = (n - 1) // 3
    support = total - 4
    pole = (n - 1) // 6 - 2
    if pole != support // 2:
        raise AssertionError("secp bound arithmetic failed")
    return {
        "n": str(n),
        "nonzero_glv_orbits": str(total),
        "nonzero_quotient_support_at_least": str(support),
        "descended_pole_degree_at_least": str(pole),
        "pole_degree_bit_length": pole.bit_length(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = [check_order(n) for n in FROZEN_ORDERS]
    payload = {
        "experiment": "ODD-GLV-NORM-BRANCH-SELECTION-066-C16-LIGHT",
        "scope": "six frozen prime index cycles and public secp256k1 order",
        "cases": cases,
        "secp256k1": secp(),
        "aggregate": {
            "orders": len(cases),
            "roots_checked": 2 * len(cases),
            "all_nonexceptional_orbit_sums_nonzero": True,
            "all_support_bounds_pass": True,
            "all_pole_degree_bounds_pass": True,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
        },
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
