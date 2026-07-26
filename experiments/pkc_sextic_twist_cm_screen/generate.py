#!/usr/bin/env python3
"""Generate the non-executable sextic-twist CM arithmetic screen artifact.

This is a deterministic arithmetic certificate producer. It does not run an
ECDLP solver, collect target relations, or authorize any experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

P = 2**256 - 2**32 - 977
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
CURVE_B = 6
EXPECTED_ORDER = 115792089237316195423570985008687907853941316518124263683276670604605579899084
EXPECTED_FACTORS = {
    2: 2,
    7: 2,
    10903: 1,
    5290657: 1,
    10833080827: 1,
    22921299619447: 1,
    41245443549316649091297836755593555342121: 1,
}

# Full n-1 factorizations and Pocklington witnesses for every nontrivial
# certificate node. Leaves not listed here are proven by trial division.
POCKLINGTON: dict[int, dict[str, dict[int, int]]] = {
    1409: {"factors": {2: 7, 11: 1}, "witnesses": {2: 3, 11: 2}},
    2819: {"factors": {2: 1, 1409: 1}, "witnesses": {2: 2, 1409: 2}},
    5333: {"factors": {2: 2, 31: 1, 43: 1}, "witnesses": {2: 2, 31: 2, 43: 2}},
    7873: {"factors": {2: 6, 3: 1, 41: 1}, "witnesses": {2: 5, 3: 3, 41: 2}},
    10831: {"factors": {2: 1, 3: 1, 5: 1, 19: 2}, "witnesses": {2: 3, 3: 2, 5: 2, 19: 2}},
    10903: {"factors": {2: 1, 3: 1, 23: 1, 79: 1}, "witnesses": {2: 3, 3: 3, 23: 2, 79: 2}},
    31123: {"factors": {2: 1, 3: 2, 7: 1, 13: 1, 19: 1}, "witnesses": {2: 2, 3: 2, 7: 3, 13: 2, 19: 2}},
    63997: {"factors": {2: 2, 3: 1, 5333: 1}, "witnesses": {2: 2, 3: 2, 5333: 2}},
    81619: {"factors": {2: 1, 3: 1, 61: 1, 223: 1}, "witnesses": {2: 2, 3: 3, 61: 2, 223: 2}},
    124493: {"factors": {2: 2, 31123: 1}, "witnesses": {2: 2, 31123: 2}},
    1670281: {"factors": {2: 3, 3: 1, 5: 1, 31: 1, 449: 1}, "witnesses": {2: 11, 3: 2, 5: 3, 31: 2, 449: 2}},
    5290657: {"factors": {2: 5, 3: 1, 7: 1, 7873: 1}, "witnesses": {2: 5, 3: 2, 7: 2, 7873: 2}},
    450975871: {"factors": {2: 1, 3: 3, 5: 1, 1670281: 1}, "witnesses": {2: 3, 3: 2, 5: 2, 1670281: 2}},
    10833080827: {"factors": {2: 1, 3: 1, 101: 1, 103: 1, 197: 1, 881: 1}, "witnesses": {2: 2, 3: 2, 101: 2, 103: 2, 197: 2, 881: 2}},
    31340226859: {"factors": {2: 1, 3: 1, 63997: 1, 81619: 1}, "witnesses": {2: 2, 3: 2, 63997: 2, 81619: 2}},
    2115501083477: {"factors": {2: 2, 11: 1, 137: 1, 2819: 1, 124493: 1}, "witnesses": {2: 2, 11: 2, 137: 2, 2819: 2, 124493: 2}},
    10154233502317: {"factors": {2: 2, 3: 4, 31340226859: 1}, "witnesses": {2: 2, 3: 2, 31340226859: 2}},
    22921299619447: {"factors": {2: 1, 3: 1, 43: 1, 197: 1, 450975871: 1}, "witnesses": {2: 3, 3: 2, 43: 2, 197: 2, 450975871: 2}},
    41245443549316649091297836755593555342121: {
        "factors": {2: 3, 3: 8, 5: 1, 23: 1, 43: 1, 683: 1, 10831: 1, 2115501083477: 1, 10154233502317: 1},
        "witnesses": {2: 7, 3: 5, 5: 2, 23: 2, 43: 2, 683: 2, 10831: 2, 2115501083477: 2, 10154233502317: 2},
    },
}

ALPHAS = {
    10903: (91, -23),
    5290657: (2513, 512),
    10833080827: (68582, -51181),
    22921299619447: (5435218, 1842907),
}

RELATION_DIVISORS = {
    3: {7: 2, 10903: 1, 5290657: 1, 22921299619447: 1},
    4: {2: 2, 7: 2, 10903: 1, 22921299619447: 1},
    5: {7: 2, 10903: 1, 10833080827: 1},
    6: {22921299619447: 1},
}


def int_product(factors: dict[int, int]) -> int:
    result = 1
    for prime, exponent in factors.items():
        result *= prime**exponent
    return result


def trial_prime(n: int) -> bool:
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


def prove_prime(n: int, memo: dict[int, bool] | None = None) -> bool:
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n not in POCKLINGTON:
        answer = trial_prime(n)
        memo[n] = answer
        return answer

    record = POCKLINGTON[n]
    factors = record["factors"]
    witnesses = record["witnesses"]
    if int_product(factors) != n - 1:
        memo[n] = False
        return False
    if n - 1 <= math.isqrt(n):
        memo[n] = False
        return False
    for q in factors:
        if not prove_prime(q, memo):
            memo[n] = False
            return False
        a = witnesses[q]
        if pow(a, n - 1, n) != 1:
            memo[n] = False
            return False
        if math.gcd(pow(a, (n - 1) // q, n) - 1, n) != 1:
            memo[n] = False
            return False
    memo[n] = True
    return True


Point = tuple[int, int] | None


def inverse(value: int) -> int:
    if value % P == 0:
        raise ZeroDivisionError("inverse of zero")
    return pow(value, P - 2, P)


def affine_add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = 3 * x1 * x1 * inverse(2 * y1 % P) % P
    else:
        slope = (y2 - y1) * inverse((x2 - x1) % P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def affine_mul(scalar: int, point: Point) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = affine_add(result, addend)
        addend = affine_add(addend, addend)
        scalar >>= 1
    return result


def deterministic_point(label: str) -> tuple[int, int]:
    x = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big") % P
    origin = x
    while True:
        rhs = (pow(x, 3, P) + CURVE_B) % P
        if rhs == 0:
            return x, 0
        if pow(rhs, (P - 1) // 2, P) == 1:
            y = pow(rhs, (P + 1) // 4, P)
            if y * y % P == rhs:
                return x, y
        x = (x + 1) % P
        if x == origin:
            raise RuntimeError("point search exhausted field")


def eisenstein_mul(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def eisenstein_conj(value: tuple[int, int]) -> tuple[int, int]:
    a, b = value
    return a - b, -b


def eisenstein_norm(value: tuple[int, int]) -> int:
    a, b = value
    return a * a - a * b + b * b


def eisenstein_divide(numerator: tuple[int, int], denominator: tuple[int, int]) -> tuple[int, int]:
    norm = eisenstein_norm(denominator)
    raw = eisenstein_mul(numerator, eisenstein_conj(denominator))
    if raw[0] % norm != 0 or raw[1] % norm != 0:
        raise ValueError("not divisible in Z[omega]")
    return raw[0] // norm, raw[1] // norm


def canonical_json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def build_artifact() -> dict[str, Any]:
    base_trace = P + 1 - N
    radicand = (4 * P - base_trace * base_trace) // 3
    v = math.isqrt(radicand)
    assert 3 * v * v + base_trace * base_trace == 4 * P

    traces = [
        base_trace,
        -base_trace,
        (base_trace + 3 * v) // 2,
        -(base_trace + 3 * v) // 2,
        (base_trace - 3 * v) // 2,
        -(base_trace - 3 * v) // 2,
    ]
    orders = [P + 1 - trace for trace in traces]
    assert orders[3] == EXPECTED_ORDER

    points: list[dict[str, Any]] = []
    for index in range(5):
        label = f"E6-point-{index}"
        point = deterministic_point(label)
        assert (point[1] * point[1] - point[0] ** 3 - CURVE_B) % P == 0
        zero_indices = [candidate_index for candidate_index, order in enumerate(orders) if affine_mul(order, point) is None]
        assert zero_indices == [3]
        points.append({"label": label, "x": str(point[0]), "y": str(point[1]), "annihilating_order_indices": zero_indices})

    factor_product = int_product(EXPECTED_FACTORS)
    assert factor_product == EXPECTED_ORDER
    prime_memo: dict[int, bool] = {}
    for factor in EXPECTED_FACTORS:
        assert prove_prime(factor, prime_memo)

    smooth_factors = {q: e for q, e in EXPECTED_FACTORS.items() if q != 41245443549316649091297836755593555342121}
    smooth_part = int_product(smooth_factors)

    trace_e6 = traces[3]
    frobenius_b = math.isqrt((4 * P - trace_e6 * trace_e6) // 3)
    frobenius_a = (trace_e6 + frobenius_b) // 2
    frobenius = (frobenius_a, frobenius_b)
    assert eisenstein_norm(frobenius) == P
    assert 2 * frobenius_a - frobenius_b == trace_e6

    alpha_rows: list[dict[str, Any]] = []
    pi_minus_one = (frobenius_a - 1, frobenius_b)
    for q, alpha in ALPHAS.items():
        assert eisenstein_norm(alpha) == q
        quotient = eisenstein_divide(pi_minus_one, alpha)
        assert eisenstein_mul(alpha, quotient) == pi_minus_one
        alpha_rows.append({
            "q": str(q),
            "a": str(alpha[0]),
            "b": str(alpha[1]),
            "norm": str(eisenstein_norm(alpha)),
            "pi_minus_one_quotient": {"a": str(quotient[0]), "b": str(quotient[1])},
        })

    getcontext().prec = 40
    relation_rows: list[dict[str, Any]] = []
    for m, factors in RELATION_DIVISORS.items():
        divisor = int_product(factors)
        numerator = divisor**m
        denominator = math.factorial(m) * P
        estimate = Decimal(numerator) / Decimal(denominator)
        relation_rows.append({
            "m": m,
            "divisor": str(divisor),
            "factorization": {str(q): e for q, e in sorted(factors.items())},
            "numerator": str(numerator),
            "denominator": str(denominator),
            "estimate_decimal": format(estimate, ".18g"),
            "log2_divisor": format(math.log2(divisor), ".15f"),
        })

    pocklington_json = {
        str(n): {
            "factors": {str(q): e for q, e in sorted(record["factors"].items())},
            "witnesses": {str(q): a for q, a in sorted(record["witnesses"].items())},
        }
        for n, record in sorted(POCKLINGTON.items())
    }

    return {
        "schema_version": "0.1",
        "artifact_id": "pkc-sextic-twist-cm-screen-v0",
        "status": "arithmetic_screen_only_non_executable",
        "claim_boundary": "Exact arithmetic and heuristic relation-yield screening only. No solver, asymptotic, route-promotion, or secp256k1-break claim.",
        "issue": 252,
        "field_prime": str(P),
        "target_group_order": str(N),
        "auxiliary_curve": {"model": "y^2 = x^3 + b", "b": CURVE_B},
        "cm_trace_reconstruction": {
            "base_trace": str(base_trace),
            "v": str(v),
            "trace_candidates": [str(value) for value in traces],
            "order_candidates": [str(value) for value in orders],
            "selected_order_index": 3,
            "selected_trace": str(trace_e6),
            "selected_order": str(EXPECTED_ORDER),
        },
        "deterministic_points": points,
        "order_factorization": {str(q): e for q, e in sorted(EXPECTED_FACTORS.items())},
        "order_factor_product": str(factor_product),
        "smooth_part": {
            "factorization": {str(q): e for q, e in sorted(smooth_factors.items())},
            "value": str(smooth_part),
            "log2": format(math.log2(smooth_part), ".15f"),
        },
        "pocklington_certificates": pocklington_json,
        "frobenius_eisenstein": {"a": str(frobenius_a), "b": str(frobenius_b), "norm": str(P), "trace": str(trace_e6)},
        "rational_kernel_candidates": alpha_rows,
        "relation_yield_screen": relation_rows,
        "required_follow_up": [
            "independent source and prior-art review",
            "exact subgroup and coset structure",
            "circuit saturation and recovery semantics",
            "full matched cost model before any execution",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check committed artifact instead of rewriting it")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    artifact_path = root / "artifact.json"
    digest_path = root / "artifact.sha256"
    payload = build_artifact()
    encoded = canonical_json_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()

    if args.check:
        if not artifact_path.exists() or not digest_path.exists():
            raise SystemExit("missing committed artifact")
        if artifact_path.read_bytes() != encoded:
            raise SystemExit("artifact.json is stale")
        if digest_path.read_text(encoding="utf-8").strip() != digest:
            raise SystemExit("artifact.sha256 is stale")
        print("CERT_OK")
        return 0

    artifact_path.write_bytes(encoded)
    digest_path.write_text(digest + "\n", encoding="utf-8")
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
