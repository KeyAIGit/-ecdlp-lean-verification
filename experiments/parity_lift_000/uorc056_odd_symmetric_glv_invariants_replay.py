#!/usr/bin/env python3
"""Lightweight theorem replay for UORC056 C17.

The script regenerates the public seven-curve extension corpus, verifies the
order-three GLV data and negation orbit counts, checks the trace/e2/norm cubic
identities on deterministic scalar samples, and validates the committed C17
summary. It accepts no external point or unknown scalar.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def curve_order(p: int) -> int:
    total = 1
    for x in range(p):
        rhs = (x * x * x + 7) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            total += 2
    return total


def first_affine_point(p: int) -> tuple[int, int]:
    for x in range(p):
        rhs = (x * x * x + 7) % p
        for y in range(p):
            if y * y % p == rhs:
                return x, y
    raise AssertionError("curve has no affine point")


def inv(value: int, p: int) -> int:
    return pow(value % p, -1, p)


def ec_add(
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
    p: int,
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = 3 * x1 * x1 * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def subgroup_points(
    p: int, n: int, generator: tuple[int, int]
) -> list[tuple[int, int] | None]:
    points: list[tuple[int, int] | None] = [None]
    current = None
    for _ in range(1, n):
        current = ec_add(current, generator, p)
        if current is None:
            raise AssertionError("generator order below n")
        points.append(current)
    if ec_add(current, generator, p) is not None:
        raise AssertionError("generator order is not n")
    return points


def public_corpus(limit: int = 7) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    p = 7
    while len(cases) < limit:
        if is_prime(p) and p % 3 == 1:
            n = curve_order(p)
            if is_prime(n) and n % 3 == 1 and n > 7:
                generator = first_affine_point(p)
                beta = next(
                    value
                    for value in range(2, p)
                    if (value * value + value + 1) % p == 0
                )
                points = subgroup_points(p, n, generator)
                target = (beta * generator[0] % p, generator[1])
                lam = points.index(target)
                if (lam * lam + lam + 1) % n:
                    raise AssertionError("GLV eigenvalue relation failed")
                cases.append(
                    {
                        "p": p,
                        "n": n,
                        "G": list(generator),
                        "beta": beta,
                        "lambda": lam,
                    }
                )
        p += 1
    return cases


def parity_orbit_counts(n: int, lam: int) -> list[int]:
    visited = {0}
    counts = [0, 0, 0, 0]
    for k in range(1, n):
        if k in visited:
            continue
        orbit = [k, lam * k % n, lam * lam * k % n]
        if len(set(orbit)) != 3:
            raise AssertionError("GLV orbit is not length three")
        visited.update(orbit)
        counts[sum(index % 2 == 0 for index in orbit)] += 1
    if counts[0] != counts[3] or counts[1] != counts[2]:
        raise AssertionError("negation pairing failed")
    if counts[2] + counts[3] != (n - 1) // 6:
        raise AssertionError("paired orbit count failed")
    return counts


def check_cubic_identities(p: int, beta: int) -> int:
    checks = 0
    for seed in range(128):
        c0 = (3 * seed + 1) % p
        c1 = (5 * seed + 2) % p
        c2 = (7 * seed + 3) % p
        x = (11 * seed + 4) % p
        t = pow(x, 3, p)
        conjugates = [
            (
                c0
                + pow(beta, j, p) * x * c1
                + pow(beta, 2 * j, p) * x * x * c2
            )
            % p
            for j in range(3)
        ]
        trace = sum(conjugates) % p
        e2 = (
            conjugates[0] * conjugates[1]
            + conjugates[1] * conjugates[2]
            + conjugates[2] * conjugates[0]
        ) % p
        norm = conjugates[0] * conjugates[1] * conjugates[2] % p
        expected_trace = 3 * c0 % p
        expected_e2 = 3 * (c0 * c0 - t * c1 * c2) % p
        expected_norm = (
            pow(c0, 3, p)
            + t * pow(c1, 3, p)
            + t * t * pow(c2, 3, p)
            - 3 * t * c0 * c1 * c2
        ) % p
        if (trace, e2, norm) != (
            expected_trace,
            expected_e2,
            expected_norm,
        ):
            raise AssertionError("cubic invariant identity failed")
        checks += 1
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    generated = public_corpus(7)
    expected_core = [
        {key: row[key] for key in ("p", "n", "G", "beta", "lambda")}
        for row in summary["cases"]
    ]
    if generated != expected_core:
        raise AssertionError("public corpus does not match committed summary")

    rows = []
    identity_checks = 0
    for generated_row, summary_row in zip(generated, summary["cases"]):
        n = int(generated_row["n"])
        lam = int(generated_row["lambda"])
        counts = parity_orbit_counts(n, lam)
        if counts != summary_row["parity_orbit_counts"]:
            raise AssertionError("orbit counts do not match summary")
        if counts[2] + counts[3] != summary_row["paired_orbit_support_exact"]:
            raise AssertionError("paired support count does not match summary")
        checks = check_cubic_identities(
            int(generated_row["p"]), int(generated_row["beta"])
        )
        identity_checks += checks
        rows.append(
            {
                **generated_row,
                "parity_orbit_counts": counts,
                "cubic_identity_checks": checks,
            }
        )

    support = (SECP_N - 1) // 6 - 4
    pole_degree = (SECP_N - 1) // 12 - 2
    secp = summary["secp256k1"]
    if str(support) != secp["odd_linear_span_quotient_support_at_least"]:
        raise AssertionError("secp support arithmetic failed")
    if str(pole_degree) != secp["odd_linear_span_pole_degree_at_least"]:
        raise AssertionError("secp pole-degree arithmetic failed")

    payload = {
        "experiment": "ODD-SYMMETRIC-GLV-INVARIANTS-067-C17-LIGHT",
        "cases": rows,
        "aggregate": {
            "curves": len(rows),
            "cubic_identity_checks": identity_checks,
            "all_public_corpus_checks": True,
            "all_negation_pair_counts_pass": True,
            "all_trace_e2_norm_identities_pass": True,
            "full_result_sha256": summary["full_result_sha256"],
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
        },
        "secp256k1": {
            "support_lower_bound": str(support),
            "pole_degree_lower_bound": str(pole_degree),
            "support_bit_length": support.bit_length(),
            "pole_degree_bit_length": pole_degree.bit_length(),
        },
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
