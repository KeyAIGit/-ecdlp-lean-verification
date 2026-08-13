#!/usr/bin/env python3
"""Exact toy-only gate for MIXED-WEIGHT-GLV-RESOLVENT-C042.

The package studies the first translated C3 characteristic determinant

    M^+_{ij}(Q,R) = x(phi^i Q + phi^j R)

and its anti-Kummer plus/minus combinations. The determinant is decomposed by
the C3 discrete Fourier transform and then screened together with three other
anti-invariant DFT-derived coordinate components.

The strongest finite gate tests every pair of scalar pullbacks m,l, every
coefficient c in F_p, and both global square classes in

    chi_p(F([m]Q) + c G([l]Q)) = carry(Q)

for declared medium toy groups. No external point, key, wallet, or production
target is accepted.
"""
from __future__ import annotations
import argparse
import json
import time
from typing import Optional

Point = Optional[tuple[int, int]]
B = 7
FROZEN = {
    271: (1087, 271, (1017, 688)),
    433: (1663, 433, (126, 1375)),
}
BASE_PAIRS = {
    271: (
        ("det_anti", "det_anti"),
        ("x0_anti", "x2_anti"),
        ("det_anti", "x0_anti"),
        ("det_anti", "x2_anti"),
        ("x0x2_anti", "det_anti"),
    ),
    433: (
        ("det_anti", "det_anti"),
        ("x0_anti", "x2_anti"),
        ("det_anti", "x0_anti"),
        ("det_anti", "x2_anti"),
    ),
}


def qchar(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


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
    if ec_add(point, generator, p) is not None or len(set(points)) != order:
        raise AssertionError("invalid subgroup orbit")
    return points


def primitive_cube_root(p: int) -> int:
    for seed in range(2, p):
        beta = pow(seed, (p - 1) // 3, p)
        if beta != 1 and pow(beta, 3, p) == 1:
            return beta
    raise AssertionError("primitive cube root missing")


def build_case(order: int) -> dict:
    p, n, generator = FROZEN[order]
    points = orbit(generator, n, p)
    beta = primitive_cube_root(p)
    scalar_of = {point: k for k, point in enumerate(points)}
    lam = scalar_of[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % n
    if (1 + lam + lam2) % n:
        raise AssertionError("invalid GLV eigenvalue")
    carry = [0] * n
    for k in range(1, n):
        total = k + lam * k % n + lam2 * k % n
        if total not in (n, 2 * n):
            raise AssertionError("invalid carry")
        carry[k] = 1 if total == 2 * n else -1
    return {
        "p": p,
        "n": n,
        "generator": generator,
        "points": points,
        "beta": beta,
        "lam": lam,
        "carry": carry,
    }


def r4(A: int, Z: int, p: int) -> int:
    return (
        A**4 + 20*A**3*B + 31*A**3*Z + 32*A**2*B**2
        + 124*A**2*B*Z + 80*A**2*Z**2 + 80*A*B**2*Z
        + 124*A*B*Z**2 + 31*A*Z**3 + 32*B**2*Z**2
        + 20*B*Z**3 + Z**4
    ) % p


def q3(A: int, Z: int, p: int) -> int:
    return (
        A**3 + 8*A**2*B + 17*A**2*Z + 20*A*B*Z
        + 17*A*Z**2 + 8*B*Z**2 + Z**3
    ) % p


def base_sequences(data: dict) -> dict[str, list[int]]:
    p, n = data["p"], data["n"]
    points = data["points"]
    X, _ = data["generator"]
    A = pow(X, 3, p)
    seqs = {
        name: [0] * n
        for name in ("det_anti", "x0_anti", "x2_anti", "x0x2_anti")
    }
    for k in range(1, n):
        x, y = points[k]
        Z = pow(x, 3, p)
        seqs["det_anti"][k] = y * Z % p * r4(A, Z, p) % p
        seqs["x0_anti"][k] = x * y % p * (2 * A + Z) % p
        seqs["x2_anti"][k] = y * (A + 2 * Z) % p
        seqs["x0x2_anti"][k] = x * y % p * q3(A, Z, p) % p
    for name, seq in seqs.items():
        if any(seq[k] == 0 for k in range(1, n)):
            raise AssertionError(f"{name} has a zero on the declared subgroup")
        if any(seq[n-k] != (-seq[k]) % p for k in range(1, n)):
            raise AssertionError(f"{name} is not anti-Kummer")
    return seqs


def p_az(A: int, Z: int, W: int, p: int) -> int:
    return (-A*A - 4*A*B + 4*A*W - 5*A*Z - 2*B*Z + 2*W*Z) % p


def p_za(A: int, Z: int, W: int, p: int) -> int:
    return (-Z*Z - 4*Z*B + 4*Z*W - 5*Z*A - 2*B*A + 2*W*A) % p


def dft_identity_checks(data: dict) -> int:
    p, n = data["p"], data["n"]
    points, beta = data["points"], data["beta"]
    X, Y = data["generator"]
    A = pow(X, 3, p)
    checks = 0
    for k in range(1, n):
        x, y = points[k]
        Z = pow(x, 3, p)
        if Z == A:
            continue
        q = []
        for j in range(3):
            translated = ec_add((x, y), (X * pow(beta, j, p) % p, Y), p)
            if translated is None:
                raise AssertionError("unexpected translated infinity")
            q.append(translated[0])
        h0 = sum(q) % p
        h1 = (q[0] + beta*q[1] + beta*beta*q[2]) % p
        h2 = (q[0] + beta*beta*q[1] + beta*q[2]) % p
        W = Y * y % p
        den = (Z - A) % p
        f0 = -3 * x * p_az(A, Z, W, p) * pow(den, -2, p) % p
        f1 = pow(3 * X * x * (y - Y) * pow(den, -1, p), 2, p)
        f2 = -3 * X * p_za(A, Z, W, p) * pow(den, -2, p) % p
        if (h0, h1, h2) != (f0, f1, f2):
            raise AssertionError("DFT component identity failed")
        matrix = []
        for i in range(3):
            row = []
            Qi = (x * pow(beta, i, p) % p, y)
            for j in range(3):
                value = ec_add(Qi, (X * pow(beta, j, p) % p, Y), p)
                if value is None:
                    raise AssertionError("unexpected matrix infinity")
                row.append(value[0])
            matrix.append(row)
        det = (
            matrix[0][0] * (matrix[1][1]*matrix[2][2]-matrix[1][2]*matrix[2][1])
            - matrix[0][1] * (matrix[1][0]*matrix[2][2]-matrix[1][2]*matrix[2][0])
            + matrix[0][2] * (matrix[1][0]*matrix[2][1]-matrix[1][1]*matrix[2][0])
        ) % p
        if det != h0 * h1 % p * h2 % p:
            raise AssertionError("circulant determinant factorization failed")
        checks += 1
    return checks


def shift_masks(p: int) -> tuple[list[int], list[int]]:
    positive = [0] * p
    negative = [0] * p
    for ratio in range(p):
        plus = minus = 0
        for c in range(p):
            sign = qchar(c + ratio, p)
            if sign == 1:
                plus |= 1 << c
            elif sign == -1:
                minus |= 1 << c
        positive[ratio] = plus
        negative[ratio] = minus
    return positive, negative


def exact_two_pullback(data: dict, left: list[int], right: list[int]) -> dict:
    p, n = data["p"], data["n"]
    target = data["carry"]
    positive, negative = shift_masks(p)
    all_coefficients = (1 << p) - 1
    inv = [0] * p
    char = [0] * p
    for value in range(1, p):
        inv[value] = pow(value, -1, p)
        char[value] = qchar(value, p)
    solutions = []
    multiplier_pairs = 0
    for m in range(1, n):
        left_pullback = [left[m*k % n] for k in range(1, n)]
        for ell in range(1, n):
            mask_plus = all_coefficients
            mask_minus = all_coefficients
            for offset, k in enumerate(range(1, n)):
                f = left_pullback[offset]
                h = right[ell*k % n]
                desired = target[k]
                if h:
                    ratio = f * inv[h] % p
                    signed = desired * char[h]
                    mask_plus &= positive[ratio] if signed == 1 else negative[ratio]
                    mask_minus &= negative[ratio] if signed == 1 else positive[ratio]
                else:
                    fchar = char[f]
                    if fchar != desired:
                        mask_plus = 0
                    if fchar != -desired:
                        mask_minus = 0
                if not (mask_plus or mask_minus):
                    break
            if mask_plus:
                c = (mask_plus & -mask_plus).bit_length() - 1
                solutions.append({"m": m, "ell": ell, "c": c, "constant_sign": 1})
            if mask_minus:
                c = (mask_minus & -mask_minus).bit_length() - 1
                solutions.append({"m": m, "ell": ell, "c": c, "constant_sign": -1})
            multiplier_pairs += 1
    return {
        "multiplier_pairs": multiplier_pairs,
        "coefficients_per_pair": p,
        "nominal_formula_instances": multiplier_pairs * p,
        "exact_decoders": solutions,
    }


def run(order: int) -> dict:
    started = time.time()
    data = build_case(order)
    seqs = base_sequences(data)
    searches = []
    for left_name, right_name in BASE_PAIRS[order]:
        result = exact_two_pullback(data, seqs[left_name], seqs[right_name])
        result["left"] = left_name
        result["right"] = right_name
        searches.append(result)
    return {
        "p": data["p"],
        "n": data["n"],
        "dft_identity_checks": dft_identity_checks(data),
        "base_zero_counts": {
            name: sum(value == 0 for value in seq[1:])
            for name, seq in seqs.items()
        },
        "searches": searches,
        "aggregate_nominal_formula_instances":
            sum(item["nominal_formula_instances"] for item in searches),
        "aggregate_exact_decoders":
            sum(len(item["exact_decoders"]) for item in searches),
        "seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, choices=sorted(FROZEN))
    parser.add_argument("--out")
    args = parser.parse_args()
    orders = [args.order] if args.order else sorted(FROZEN)
    results = [run(order) for order in orders]
    payload = {
        "schema_version": 1,
        "results": results,
        "aggregate_nominal_formula_instances":
            sum(item["aggregate_nominal_formula_instances"] for item in results),
        "aggregate_exact_decoders":
            sum(item["aggregate_exact_decoders"] for item in results),
        "claim_boundary":
            "toy-only exact search; no secp256k1 target and no decoder claim",
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
