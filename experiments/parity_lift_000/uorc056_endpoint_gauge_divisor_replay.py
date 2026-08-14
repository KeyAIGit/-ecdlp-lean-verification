#!/usr/bin/env python3
"""Lightweight exact divisor replay for UORC056 C13.

This verifies the compact line-bundle cocycle and endpoint-gauge decomposition
on the six frozen prime orders. It uses no unknown scalar or external point.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FROZEN_ORDERS = (19, 31, 67, 271, 397, 433)


def shift(v: list[int], s: int) -> list[int]:
    n = len(v)
    out = [0] * n
    for k, value in enumerate(v):
        out[(k + s) % n] += value
    return out


def add(u: list[int], v: list[int]) -> list[int]:
    return [a + b for a, b in zip(u, v)]


def sub(u: list[int], v: list[int]) -> list[int]:
    return [a - b for a, b in zip(u, v)]


def factor_divisor(n: int) -> list[int]:
    m = (n - 1) // 2
    out = [0] * n
    out[(1 + m) % n] += 1
    out[(1 - m) % n] += 1
    out[1] -= 2
    return out


def primitive(n: int) -> list[int]:
    m = (n - 1) // 2
    return [
        -1 if (k & 1 and 1 <= k <= m)
        else 1 if (not (k & 1) and m < k < n)
        else 0
        for k in range(n)
    ]


def class_formula(n: int) -> tuple[int, int]:
    r = (n + 1) // 4 if n % 4 == 3 else (n - 1) // 4
    a = r * (2 * r - 1) % n if n % 4 == 3 else r * (2 * r + 1) % n
    return r, a


def check_order(n: int) -> dict[str, object]:
    m = (n - 1) // 2
    S = 2
    b = factor_divisor(n)
    D = primitive(n)
    r, a = class_formula(n)
    assert sum(D) == 0
    assert sum(k * D[k] for k in range(n)) % n == a != 0
    assert sub(D, shift(D, S)) == b

    D0 = [0] * n
    D0[a] = 1
    D0[0] = -1
    E = sub(D, D0)
    assert sum(E) == 0
    assert sum(k * E[k] for k in range(n)) % n == 0
    degree = sum(max(x, 0) for x in E)
    assert degree == sum(max(-x, 0) for x in E)
    assert degree in (r, r + 1)

    compact_one = sub(D0, shift(D0, S))
    gauge_one = sub(E, shift(E, S))
    assert add(compact_one, gauge_one) == b

    accumulated = [0] * n
    checks = 0
    for L in range(n + 1):
        endpoint = (L * S) % n
        compact = sub(D0, shift(D0, endpoint))
        gauge = sub(E, shift(E, endpoint))
        assert add(compact, gauge) == accumulated
        checks += 1
        if L < n:
            accumulated = add(accumulated, shift(b, endpoint))
    assert not any(accumulated)

    target_endpoint = (m * S) % n
    assert target_endpoint == n - 1
    target_compact = sub(D0, shift(D0, target_endpoint))
    support = [k for k, value in enumerate(target_compact) if value]
    assert set(support).issubset({0, a, n - 1, (a - 1) % n})

    return {
        "n": n,
        "m": m,
        "r": r,
        "class_index_a": a,
        "endpoint_gauge_degree": degree,
        "all_L_checks": checks,
        "target_compact_support": support,
        "passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = [check_order(n) for n in FROZEN_ORDERS]
    payload = {
        "experiment": "UORC056_C13_ENDPOINT_GAUGE_DIVISOR_REPLAY",
        "cases": cases,
        "aggregate": {
            "orders": len(cases),
            "all_L_divisor_checks": sum(int(c["all_L_checks"]) for c in cases),
            "compact_line_bundle_cocycle_found": True,
            "endpoint_gauge_degree_is_r_or_r_plus_one": True,
            "sub_sqrt_evaluator_found": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
