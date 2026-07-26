#!/usr/bin/env python3
"""Independent standard-library replay for the sextic-twist CM screen.

The validator intentionally does not import generate.py and uses Jacobian point
arithmetic rather than the producer's affine arithmetic.
"""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

EXPECTED_P = 2**256 - 2**32 - 977
EXPECTED_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
EXPECTED_B = 6
EXPECTED_ORDER = 115792089237316195423570985008687907853941316518124263683276670604605579899084
EXPECTED_ROOT_FACTORS = {
    2: 2,
    7: 2,
    10903: 1,
    5290657: 1,
    10833080827: 1,
    22921299619447: 1,
    41245443549316649091297836755593555342121: 1,
}


def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION_FAILED: {message}")


def multiply_factorization(factors: dict[int, int]) -> int:
    out = 1
    for q, exponent in factors.items():
        if q < 2 or exponent < 1:
            fail("invalid factorization entry")
        out *= q**exponent
    return out


def small_prime_by_division(n: int) -> bool:
    if n < 2:
        return False
    for divisor in range(2, math.isqrt(n) + 1):
        if n % divisor == 0:
            return n == divisor
    return True


def validate_prime_certificate(n: int, records: dict[int, dict[str, dict[int, int]]], cache: dict[int, bool]) -> bool:
    if n in cache:
        return cache[n]
    if n not in records:
        result = small_prime_by_division(n)
        cache[n] = result
        return result

    entry = records[n]
    factors = entry["factors"]
    witnesses = entry["witnesses"]
    if set(factors) != set(witnesses):
        cache[n] = False
        return False
    if multiply_factorization(factors) != n - 1:
        cache[n] = False
        return False

    known_part = multiply_factorization(factors)
    if known_part <= math.isqrt(n):
        cache[n] = False
        return False

    for q in factors:
        if not validate_prime_certificate(q, records, cache):
            cache[n] = False
            return False
        witness = witnesses[q]
        if not 1 < witness < n:
            cache[n] = False
            return False
        if pow(witness, n - 1, n) != 1:
            cache[n] = False
            return False
        residue = (pow(witness, (n - 1) // q, n) - 1) % n
        if math.gcd(residue, n) != 1:
            cache[n] = False
            return False

    cache[n] = True
    return True


# Jacobian coordinates. The identity is any triple with Z == 0.
Jacobian = tuple[int, int, int]


def infinity() -> Jacobian:
    return 0, 1, 0


def is_infinity(point: Jacobian, p: int) -> bool:
    return point[2] % p == 0


def jacobian_double(point: Jacobian, p: int) -> Jacobian:
    x1, y1, z1 = point
    if z1 % p == 0 or y1 % p == 0:
        return infinity()
    yy = y1 * y1 % p
    s = 4 * x1 * yy % p
    m = 3 * x1 * x1 % p
    x3 = (m * m - 2 * s) % p
    yyyy = yy * yy % p
    y3 = (m * (s - x3) - 8 * yyyy) % p
    z3 = 2 * y1 * z1 % p
    return x3, y3, z3


def jacobian_add(left: Jacobian, right: Jacobian, p: int) -> Jacobian:
    if is_infinity(left, p):
        return right
    if is_infinity(right, p):
        return left
    x1, y1, z1 = left
    x2, y2, z2 = right
    z1_sq = z1 * z1 % p
    z2_sq = z2 * z2 % p
    u1 = x1 * z2_sq % p
    u2 = x2 * z1_sq % p
    s1 = y1 * z2 * z2_sq % p
    s2 = y2 * z1 * z1_sq % p
    h = (u2 - u1) % p
    r = (s2 - s1) % p
    if h == 0:
        return jacobian_double(left, p) if r == 0 else infinity()
    hh = h * h % p
    hhh = h * hh % p
    v = u1 * hh % p
    x3 = (r * r - hhh - 2 * v) % p
    y3 = (r * (v - x3) - s1 * hhh) % p
    z3 = h * z1 * z2 % p
    return x3, y3, z3


def jacobian_multiply(k: int, affine: tuple[int, int], p: int) -> Jacobian:
    accumulator = infinity()
    running = (affine[0], affine[1], 1)
    while k:
        if k & 1:
            accumulator = jacobian_add(accumulator, running, p)
        running = jacobian_double(running, p)
        k >>= 1
    return accumulator


def derive_point(label: str, p: int, b: int) -> tuple[int, int]:
    x = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big") % p
    start = x
    while True:
        rhs = (pow(x, 3, p) + b) % p
        if rhs == 0:
            return x, 0
        legendre = pow(rhs, (p - 1) // 2, p)
        if legendre == 1:
            candidate = pow(rhs, (p + 1) // 4, p)
            if candidate * candidate % p == rhs:
                return x, candidate
        x = (x + 1) % p
        if x == start:
            fail("deterministic point search cycled")


def zomega_product(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    # omega^2 + omega + 1 = 0
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def zomega_conjugate(value: tuple[int, int]) -> tuple[int, int]:
    a, b = value
    return a - b, -b


def zomega_norm(value: tuple[int, int]) -> int:
    return zomega_product(value, zomega_conjugate(value))[0]


def exact_zomega_quotient(numerator: tuple[int, int], denominator: tuple[int, int]) -> tuple[int, int]:
    norm = zomega_norm(denominator)
    expanded = zomega_product(numerator, zomega_conjugate(denominator))
    if expanded[0] % norm or expanded[1] % norm:
        fail("claimed Eisenstein divisibility is false")
    return expanded[0] // norm, expanded[1] // norm


def canonical_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def parse_int_map(raw: dict[str, Any]) -> dict[int, int]:
    return {int(key): int(value) for key, value in raw.items()}


def validate() -> None:
    root = Path(__file__).resolve().parent
    artifact_path = root / "artifact.json"
    digest_path = root / "artifact.sha256"
    artifact_bytes = artifact_path.read_bytes()
    payload = json.loads(artifact_bytes)

    if artifact_bytes != canonical_bytes(payload):
        fail("artifact is not canonical JSON")
    calculated_digest = hashlib.sha256(artifact_bytes).hexdigest()
    if digest_path.read_text(encoding="utf-8").strip() != calculated_digest:
        fail("artifact hash mismatch")

    if payload.get("status") != "arithmetic_screen_only_non_executable":
        fail("unexpected authority status")
    p = int(payload["field_prime"])
    n = int(payload["target_group_order"])
    b = int(payload["auxiliary_curve"]["b"])
    if (p, n, b) != (EXPECTED_P, EXPECTED_N, EXPECTED_B):
        fail("parameter mismatch")
    if p % 4 != 3:
        fail("validator square-root path requires p mod 4 = 3")

    trace = p + 1 - n
    radicand_numerator = 4 * p - trace * trace
    if radicand_numerator % 3:
        fail("CM radicand is nonintegral")
    v = math.isqrt(radicand_numerator // 3)
    if trace * trace + 3 * v * v != 4 * p:
        fail("CM identity failed")
    traces = [trace, -trace, (trace + 3 * v) // 2, -(trace + 3 * v) // 2, (trace - 3 * v) // 2, -(trace - 3 * v) // 2]
    orders = [p + 1 - value for value in traces]
    if orders[3] != EXPECTED_ORDER:
        fail("expected E6 order is not candidate index 3")

    cm_record = payload["cm_trace_reconstruction"]
    if [int(value) for value in cm_record["trace_candidates"]] != traces:
        fail("trace candidates drift")
    if [int(value) for value in cm_record["order_candidates"]] != orders:
        fail("order candidates drift")
    if int(cm_record["selected_order"]) != EXPECTED_ORDER or int(cm_record["selected_order_index"]) != 3:
        fail("selected order drift")

    artifact_points = payload["deterministic_points"]
    if len(artifact_points) < 3:
        fail("insufficient deterministic points")
    for expected_index, row in enumerate(artifact_points):
        expected_label = f"E6-point-{expected_index}"
        if row["label"] != expected_label:
            fail("point label sequence drift")
        point = derive_point(expected_label, p, b)
        if point != (int(row["x"]), int(row["y"])):
            fail("deterministic point mismatch")
        if (point[1] * point[1] - point[0] ** 3 - b) % p:
            fail("point is not on E6")
        annihilating = [index for index, order in enumerate(orders) if is_infinity(jacobian_multiply(order, point, p), p)]
        if annihilating != [3] or row["annihilating_order_indices"] != [3]:
            fail("order discrimination failed")

    root_factors = parse_int_map(payload["order_factorization"])
    if root_factors != EXPECTED_ROOT_FACTORS:
        fail("order factorization drift")
    if multiply_factorization(root_factors) != EXPECTED_ORDER:
        fail("factorization product mismatch")
    if int(payload["order_factor_product"]) != EXPECTED_ORDER:
        fail("recorded factor product mismatch")

    raw_certs = payload["pocklington_certificates"]
    certs: dict[int, dict[str, dict[int, int]]] = {}
    for n_text, entry in raw_certs.items():
        certs[int(n_text)] = {
            "factors": parse_int_map(entry["factors"]),
            "witnesses": parse_int_map(entry["witnesses"]),
        }
    prime_cache: dict[int, bool] = {}
    for q in root_factors:
        if not validate_prime_certificate(q, certs, prime_cache):
            fail(f"primality certificate failed for {q}")

    smooth = payload["smooth_part"]
    smooth_factors = parse_int_map(smooth["factorization"])
    if max(smooth_factors) != 22921299619447:
        fail("unexpected smooth-part largest factor")
    if multiply_factorization(smooth_factors) != int(smooth["value"]):
        fail("smooth-part factorization mismatch")

    frow = payload["frobenius_eisenstein"]
    frobenius = int(frow["a"]), int(frow["b"])
    if zomega_norm(frobenius) != p:
        fail("Frobenius norm mismatch")
    if 2 * frobenius[0] - frobenius[1] != traces[3]:
        fail("Frobenius trace mismatch")
    pi_minus_one = frobenius[0] - 1, frobenius[1]

    seen_q: set[int] = set()
    for row in payload["rational_kernel_candidates"]:
        q = int(row["q"])
        alpha = int(row["a"]), int(row["b"])
        if q in seen_q:
            fail("duplicate rational-kernel factor")
        seen_q.add(q)
        if zomega_norm(alpha) != q or int(row["norm"]) != q:
            fail("endomorphism norm mismatch")
        quotient = exact_zomega_quotient(pi_minus_one, alpha)
        recorded = row["pi_minus_one_quotient"]
        if quotient != (int(recorded["a"]), int(recorded["b"])):
            fail("Eisenstein quotient mismatch")
        if zomega_product(alpha, quotient) != pi_minus_one:
            fail("Eisenstein reconstruction mismatch")
    if seen_q != {10903, 5290657, 10833080827, 22921299619447}:
        fail("rational-kernel factor set mismatch")

    getcontext().prec = 50
    for row in payload["relation_yield_screen"]:
        m = int(row["m"])
        factors = parse_int_map(row["factorization"])
        divisor = multiply_factorization(factors)
        if divisor != int(row["divisor"]):
            fail("relation divisor mismatch")
        numerator = divisor**m
        denominator = math.factorial(m) * p
        if numerator != int(row["numerator"]) or denominator != int(row["denominator"]):
            fail("relation-yield rational mismatch")
        reported = Decimal(row["estimate_decimal"])
        actual = Decimal(numerator) / Decimal(denominator)
        tolerance = Decimal("1e-16") * max(Decimal(1), abs(actual))
        if abs(reported - actual) > tolerance:
            fail("relation-yield decimal mismatch")

    print("VALIDATION_OK")
    print(calculated_digest)


if __name__ == "__main__":
    validate()
