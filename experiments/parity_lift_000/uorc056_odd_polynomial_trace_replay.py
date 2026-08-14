#!/usr/bin/env python3
"""Lightweight theorem replay for UORC056 C18.

Regenerates the public seven-curve corpus, endpoint correction, GLV orbit types,
and Newton power-sum identities. No external point or unknown scalar is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
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


def inv(a: int, p: int) -> int:
    return pow(a % p, -1, p)


def ec_add(P, Q, p: int):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    slope = (
        3 * x1 * x1 * inv(2 * y1, p)
        if P == Q
        else (y2 - y1) * inv(x2 - x1, p)
    ) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def first_point(p: int):
    for x in range(p):
        rhs = (x * x * x + 7) % p
        for y in range(p):
            if y * y % p == rhs:
                return x, y
    raise AssertionError("no affine point")


def points(p: int, n: int, G):
    out = [None]
    R = None
    for _ in range(1, n):
        R = ec_add(R, G, p)
        if R is None:
            raise AssertionError("short generator order")
        out.append(R)
    if ec_add(R, G, p) is not None:
        raise AssertionError("wrong generator order")
    return out


def public_corpus(limit: int = 7):
    out = []
    p = 7
    while len(out) < limit:
        if is_prime(p) and p % 3 == 1:
            n = curve_order(p)
            if is_prime(n) and n % 3 == 1 and n > 7:
                G = first_point(p)
                beta = next(b for b in range(2, p) if (b * b + b + 1) % p == 0)
                subgroup = points(p, n, G)
                lam = subgroup.index((beta * G[0] % p, G[1]))
                if (lam * lam + lam + 1) % n:
                    raise AssertionError("GLV eigenvalue failed")
                out.append({"p": p, "n": n, "G": list(G), "beta": beta, "lambda": lam})
        p += 1
    return out


def gauge(n: int) -> list[int]:
    m = (n - 1) // 2
    d = [
        -1 if (k & 1 and 1 <= k <= m)
        else 1 if (not (k & 1) and m < k < n)
        else 0
        for k in range(n)
    ]
    if n % 4 == 3:
        r = (n + 1) // 4
        a = r * (2 * r - 1) % n
    else:
        r = (n - 1) // 4
        a = r * (2 * r + 1) % n
    d[a] -= 1
    d[0] += 1
    if sum(d) or sum(k * d[k] for k in range(n)) % n:
        raise AssertionError("gauge is not principal")
    return d


def orbit_rows(n: int, lam: int, correction: set[int]):
    visited = {0}
    rows = []
    for k in range(1, n):
        if k in visited:
            continue
        orbit = [k, lam * k % n, lam * lam * k % n]
        visited.update(orbit)
        rows.append({
            "orbit": orbit,
            "type": sum(index % 2 == 0 for index in orbit),
            "exceptional": bool(correction.intersection(orbit)),
        })
    if len(visited) != n:
        raise AssertionError("orbit cover failed")
    return rows


def newton_checks(p: int, samples: int = 128) -> int:
    checks = 0
    for seed in range(samples):
        z = [(3 * seed + 1) % p, (5 * seed + 2) % p, (7 * seed + 3) % p]
        e1 = sum(z) % p
        e2 = (z[0] * z[1] + z[1] * z[2] + z[2] * z[0]) % p
        e3 = z[0] * z[1] * z[2] % p
        S = [3 % p, e1, (e1 * e1 - 2 * e2) % p]
        for _degree in range(3, 8):
            S.append((e1 * S[-1] - e2 * S[-2] + e3 * S[-3]) % p)
        for degree in (1, 3, 5, 7):
            if S[degree] != sum(pow(value, degree, p) for value in z) % p:
                raise AssertionError("Newton recurrence failed")
            checks += 1
    return checks


def check_case(core: dict[str, object]) -> dict[str, object]:
    n = int(core["n"])
    lam = int(core["lambda"])
    d = gauge(n)
    endpoint = [d[k] - d[(k + 1) % n] for k in range(n)]
    parity = [1 if k % 2 == 0 else -1 for k in range(n)]
    correction = {k for k in range(1, n) if endpoint[k] != parity[k]}
    if len(correction) > 4:
        raise AssertionError("too many correction indices")
    rows = orbit_rows(n, lam, correction)
    counts = [sum(row["type"] == t for row in rows) for t in range(4)]
    if counts[0] != counts[3] or counts[1] != counts[2]:
        raise AssertionError("negation pairing failed")
    if counts[2] + counts[3] != (n - 1) // 6:
        raise AssertionError("type-2 plus type-3 count failed")
    nonexceptional2 = 0
    nonexceptional3 = 0
    valuation_checks = 0
    exceptional = 0
    for row in rows:
        values = [endpoint[index] for index in row["orbit"]]
        if row["exceptional"]:
            exceptional += 1
            continue
        expected = [1 if index % 2 == 0 else -1 for index in row["orbit"]]
        if values != expected:
            raise AssertionError("nonexceptional parity law failed")
        valuation_checks += 3
        if row["type"] == 2:
            if sorted(values) != [-1, 1, 1]:
                raise AssertionError("type-2 pattern failed")
            nonexceptional2 += 1
        elif row["type"] == 3:
            if values != [1, 1, 1]:
                raise AssertionError("type-3 pattern failed")
            nonexceptional3 += 1
    guaranteed = nonexceptional2 + nonexceptional3
    if guaranteed < max(0, (n - 1) // 6 - 4):
        raise AssertionError("support bound failed")
    return {
        **core,
        "endpoint_correction_indices": sorted(correction),
        "parity_orbit_counts": counts,
        "nonexceptional_type2": nonexceptional2,
        "nonexceptional_type3": nonexceptional3,
        "exceptional_orbits": exceptional,
        "guaranteed_quotient_support": guaranteed,
        "orbit_valuation_checks": valuation_checks,
        "newton_scalar_checks": newton_checks(int(core["p"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    corpus = public_corpus()
    expected = [
        {key: row[key] for key in ("p", "n", "G", "beta", "lambda")}
        for row in summary["cases"]
    ]
    if corpus != expected:
        raise AssertionError("public corpus mismatch")
    cases = [check_case(row) for row in corpus]
    for actual, committed in zip(cases, summary["cases"]):
        for key in (
            "endpoint_correction_indices", "parity_orbit_counts",
            "nonexceptional_type2", "nonexceptional_type3",
            "exceptional_orbits", "orbit_valuation_checks", "newton_scalar_checks",
        ):
            if actual[key] != committed[key]:
                raise AssertionError(f"summary mismatch for {key}")
    support = (SECP_N - 1) // 6 - 4
    pole = (SECP_N - 1) // 12 - 2
    secp = summary["secp256k1"]
    if str(support) != secp["odd_polynomial_trace_quotient_support_at_least"]:
        raise AssertionError("secp support mismatch")
    if str(pole) != secp["odd_polynomial_trace_pole_degree_at_least"]:
        raise AssertionError("secp pole mismatch")
    payload = {
        "experiment": "ODD-POLYNOMIAL-TRACE-FUNCTIONAL-068-C18-LIGHT",
        "cases": cases,
        "aggregate": {
            "curves": 7,
            "orbit_valuation_checks": sum(row["orbit_valuation_checks"] for row in cases),
            "newton_scalar_checks": sum(row["newton_scalar_checks"] for row in cases),
            "full_result_sha256": summary["full_result_sha256"],
            "all_public_corpus_checks": True,
            "all_type2_type3_patterns_pass": True,
            "all_support_bounds_pass": True,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
        },
        "secp256k1": {
            "support_lower_bound": str(support),
            "pole_degree_lower_bound": str(pole),
            "support_bit_length": support.bit_length(),
            "pole_degree_bit_length": pole.bit_length(),
        },
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.write_text(encoded + "\n")


if __name__ == "__main__":
    main()
