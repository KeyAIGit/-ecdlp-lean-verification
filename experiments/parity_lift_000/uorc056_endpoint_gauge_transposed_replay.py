#!/usr/bin/env python3
"""Lightweight exact index-space replay for UORC056 C15.

No curve point, unknown scalar, wallet, or production target is accepted. The
script verifies the endpoint/target divisor relation, seven-source anti-resolvent,
cyclic translate-rank certificates, and the public secp256k1 GLV floor-sum count.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FROZEN_ORDERS = (19, 31, 67, 271, 397, 433)
CERT_PRIME = 1_000_003
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
SECP_LAMBDA = int("5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72", 16)


def trim(poly: list[int], p: int) -> list[int]:
    out = [x % p for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_divmod(num: list[int], den: list[int], p: int) -> tuple[list[int], list[int]]:
    num, den = trim(num, p), trim(den, p)
    if den == [0]:
        raise ZeroDivisionError
    if len(num) < len(den):
        return [0], num
    q = [0] * (len(num) - len(den) + 1)
    r = num[:]
    inv_lead = pow(den[-1], -1, p)
    while r != [0] and len(r) >= len(den):
        shift = len(r) - len(den)
        scale = r[-1] * inv_lead % p
        q[shift] = scale
        for i, coefficient in enumerate(den):
            r[i + shift] = (r[i + shift] - scale * coefficient) % p
        r = trim(r, p)
    return trim(q, p), r


def poly_gcd(left: list[int], right: list[int], p: int) -> list[int]:
    left, right = trim(left, p), trim(right, p)
    while right != [0]:
        _, rem = poly_divmod(left, right, p)
        left, right = right, rem
    inv_lead = pow(left[-1], -1, p)
    return trim([inv_lead * x for x in left], p)


def primitive(n: int) -> list[int]:
    m = (n - 1) // 2
    return [
        -1 if (k & 1 and 1 <= k <= m)
        else 1 if (not (k & 1) and m < k < n)
        else 0
        for k in range(n)
    ]


def class_index(n: int) -> tuple[int, int]:
    if n % 4 == 3:
        r = (n + 1) // 4
        return r, r * (2 * r - 1) % n
    r = (n - 1) // 4
    return r, r * (2 * r + 1) % n


def next_shift(vector: list[int]) -> list[int]:
    n = len(vector)
    return [vector[(k + 1) % n] for k in range(n)]


def add(left: list[int], right: list[int]) -> list[int]:
    return [a + b for a, b in zip(left, right)]


def anti_resolvent(source: list[int]) -> list[int]:
    total = [0] * len(source)
    term = source[:]
    sign = 1
    for _ in range(len(source)):
        total = [a + sign * b for a, b in zip(total, term)]
        term = next_shift(term)
        sign = -sign
    return total


def check_order(n: int) -> dict[str, object]:
    m = (n - 1) // 2
    r, a = class_index(n)
    d = primitive(n)
    gauge = d[:]
    gauge[a] -= 1
    gauge[0] += 1
    z = [gauge[k] - gauge[(k + 1) % n] for k in range(n)]

    q = [0] * n
    q[a] += 1
    q[n - 1] += 1
    q[(a - 1) % n] -= 1
    q[0] -= 1

    target = [1 if k % 2 == 0 else -1 for k in range(n)]
    target[m] -= 1
    if add(z, q) != target:
        raise AssertionError("endpoint-target relation failed")

    source = add(z, next_shift(z))
    expected = [0] * n
    for index, coefficient in (
        (0, 1), ((a - 2) % n, 1), (a, -1),
        ((m - 1) % n, -1), (m, -1), (n - 2, -1), (n - 1, 2),
    ):
        expected[index] += coefficient
    if source != expected or anti_resolvent(source) != [2 * x for x in z]:
        raise AssertionError("seven-source anti-resolvent failed")

    cycle = [(-1) % CERT_PRIME] + [0] * (n - 1) + [1]
    gcd = poly_gcd([x % CERT_PRIME for x in z], cycle, CERT_PRIME)
    if gcd != [CERT_PRIME - 1, 1]:
        raise AssertionError("rank certificate failed")

    return {
        "n": n,
        "m": m,
        "r": r,
        "class_index": a,
        "gauge_degree": sum(max(-x, 0) for x in gauge),
        "endpoint_support": sum(x != 0 for x in z),
        "source": {str(k): x for k, x in enumerate(source) if x},
        "source_support": sum(x != 0 for x in source),
        "rational_translate_rank": n - 1,
        "passed": True,
    }


def floor_sum(n: int, m: int, a: int, b: int) -> int:
    answer = 0
    while True:
        if a >= m:
            answer += (n - 1) * n * (a // m) // 2
            a %= m
        if b >= m:
            answer += n * (b // m)
            b %= m
        y = a * n + b
        if y < m:
            return answer
        n = y // m
        b = y % m
        m, a = a, m


def count_mod_lt(count: int, modulus: int, a: int, b: int, bound: int) -> int:
    ge = floor_sum(count, modulus, a, b + modulus - bound) - floor_sum(
        count, modulus, a, b
    )
    return count - ge


def secp_certificate() -> dict[str, object]:
    n, lam = SECP_N, SECP_LAMBDA
    if n % 16 != 1 or (lam * lam + lam + 1) % n or pow(lam, 3, n) != 1:
        raise AssertionError("secp constants failed")
    s = (n - 1) // 8
    c = ((lam - 1) * pow(2, -1, n)) % n
    intersection = count_mod_lt(2 * s, n, lam, c, 2 * s)
    partial = 2 * s - intersection
    if intersection != s // 2 + 20 or partial != 3 * s // 2 - 20:
        raise AssertionError("secp floor-sum formula failed")
    return {
        "n": str(n),
        "lambda": str(lam),
        "s": str(s),
        "intersection": str(intersection),
        "intersection_formula": "s/2+20",
        "partial_glv_orbits": str(partial),
        "partial_formula": "3s/2-20",
        "partial_bit_length": partial.bit_length(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = [check_order(n) for n in FROZEN_ORDERS]
    payload = {
        "experiment": "ENDPOINT-GAUGE-TRANSPOSED-FUNCTIONAL-065-C15-LIGHT",
        "scope": "index-space frozen orders and public secp256k1 constants only",
        "cases": cases,
        "secp256k1": secp_certificate(),
        "aggregate": {
            "orders": len(cases),
            "all_endpoint_target_relations": True,
            "all_seven_source_equations": True,
            "all_anti_resolvent_reconstructions": True,
            "all_rational_translate_ranks_n_minus_1": True,
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
