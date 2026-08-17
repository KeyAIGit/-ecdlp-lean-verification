#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
B = 7

FROZEN_CASES = (
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
    (1051, 1093, (3, 385)),
    (1303, 1249, (1, 201)),
    (3571, 3469, (4, 1706)),
    (3931, 4021, (4, 1427)),
)

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def ec_add(left: Point, right: Point, prime: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        if y1 % prime == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, prime) % prime
    else:
        slope = (y2 - y1) * pow((x2 - x1) % prime, -1, prime) % prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    return x3, y3


def orbit(generator: tuple[int, int], order: int, prime: int) -> list[Point]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, prime)
        points.append(point)
    if ec_add(point, generator, prime) is not None:
        raise AssertionError("declared order failed")
    if len(set(points)) != order:
        raise AssertionError("early orbit collision")
    return points


def qchar(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-binary value")


def primitive_cube_root(prime: int) -> int:
    if (prime - 1) % 3:
        raise AssertionError("base field has no nontrivial cube root")
    for seed in range(2, prime):
        beta = pow(seed, (prime - 1) // 3, prime)
        if beta != 1 and pow(beta, 3, prime) == 1:
            return beta
    raise AssertionError("primitive cube root not found")


def c6_orbit(scalar: int, order: int, lam: int) -> frozenset[int]:
    lam2 = lam * lam % order
    return frozenset(
        {
            scalar % order,
            (-scalar) % order,
            lam * scalar % order,
            (-lam * scalar) % order,
            lam2 * scalar % order,
            (-lam2 * scalar) % order,
        }
    )


def quotient_representatives(order: int, lam: int) -> list[int]:
    seen: set[int] = set()
    representatives: list[int] = []
    for scalar in range(1, order):
        if scalar in seen:
            continue
        orbit6 = c6_orbit(scalar, order, lam)
        if len(orbit6) != 6:
            raise AssertionError("C6 action was not free off zero")
        seen.update(orbit6)
        representatives.append(min(orbit6))
    if len(seen) != order - 1:
        raise AssertionError("C6 quotient did not cover nonzero scalars")
    return representatives


def run_case(prime: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    if order % 12 != 1:
        raise AssertionError("order must be one modulo twelve")

    points = orbit(generator, order, prime)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    beta = primitive_cube_root(prime)
    glv_point = (beta * generator[0] % prime, generator[1])
    lam = point_to_scalar[glv_point]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("GLV scalar does not have order three")

    units = {
        1,
        order - 1,
        lam,
        (-lam) % order,
        lam * lam % order,
        (-(lam * lam % order)) % order,
    }
    if len(units) != 6:
        raise AssertionError("CM unit image did not have size six")
    if any(qchar(unit, order) != 1 for unit in units):
        raise AssertionError("CM unit was not a scalar square")

    representatives = quotient_representatives(order, lam)
    if len(representatives) != (order - 1) // 6:
        raise AssertionError("unexpected ray-class quotient size")

    weber = [0] * order
    for scalar in range(1, order):
        point = points[scalar]
        assert point is not None
        weber[scalar] = pow(point[0], 3, prime)

    c6_invariance_checks = 0
    for scalar in range(1, order):
        base_value = weber[scalar]
        for member in c6_orbit(scalar, order, lam):
            if weber[member] != base_value:
                raise AssertionError("x^3 was not C6 invariant")
            if qchar(member, order) != qchar(scalar, order):
                raise AssertionError("quadratic character did not descend through C6")
            c6_invariance_checks += 1

    base_resolvent = sum(qchar(rep, order) * weber[rep] for rep in representatives) % prime
    if base_resolvent == 0:
        raise AssertionError("base ray-class resolvent vanished")

    full_s3 = sum(qchar(scalar, order) * weber[scalar] for scalar in range(1, order)) % prime
    if full_s3 != 6 * base_resolvent % prime:
        raise AssertionError("S3 was not six times the ray-class resolvent")

    base_trace = sum(weber[rep] for rep in representatives) % prime
    scaling_checks = 0
    trace_checks = 0
    square_checks = 0

    for hidden in range(1, order):
        resolvent = sum(
            qchar(rep, order) * weber[rep * hidden % order]
            for rep in representatives
        ) % prime
        expected = qchar(hidden, order) * base_resolvent % prime
        if resolvent != expected:
            raise AssertionError("ray-class resolvent scaling failed")
        scaling_checks += 1

        trace = sum(weber[rep * hidden % order] for rep in representatives) % prime
        if trace != base_trace:
            raise AssertionError("unweighted ray-class trace retained orientation")
        trace_checks += 1

        if resolvent * resolvent % prime != base_resolvent * base_resolvent % prime:
            raise AssertionError("squared ray-class resolvent retained orientation")
        square_checks += 1

    return {
        "p": prime,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "ray_class_order": len(representatives),
        "quadratic_half_orbit": len(representatives) // 2,
        "base_resolvent": base_resolvent,
        "full_s3": full_s3,
        "base_trace": base_trace,
        "c6_invariance_checks": c6_invariance_checks,
        "resolvent_scaling_checks": scaling_checks,
        "trace_invariance_checks": trace_checks,
        "square_invariance_checks": square_checks,
        "ceil_sqrt_order": math.isqrt(order - 1) + 1,
    }


def secp_certificate() -> dict[str, object]:
    n = SECP_N
    sqrt_n = math.isqrt(n - 1) + 1
    ray_order = (n - 1) // 6
    quadratic_half = (n - 1) // 12
    return {
        "p": SECP_P,
        "n": n,
        "n_mod_12": n % 12,
        "ray_class_order": ray_order,
        "quadratic_half_orbit": quadratic_half,
        "ceil_sqrt_n": sqrt_n,
        "ray_class_order_over_sqrt_floor": ray_order // sqrt_n,
        "quadratic_half_over_sqrt_floor": quadratic_half // sqrt_n,
        "direct_resolvent_terms": ray_order,
        "generic_curve_rational_decoder_degree_lower_bound": (n - 1) // 2,
        "c6_quotient_polynomial_degree_lower_bound": quadratic_half,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("cm_ray_class_torus_orientation_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "CM-RAY-CLASS-TORUS-ORIENTATION-040",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "all_base_resolvents_nonzero": all(case["base_resolvent"] != 0 for case in cases),
            "total_c6_invariance_checks": sum(case["c6_invariance_checks"] for case in cases),
            "total_resolvent_scaling_checks": sum(case["resolvent_scaling_checks"] for case in cases),
            "total_trace_invariance_checks": sum(case["trace_invariance_checks"] for case in cases),
            "total_square_invariance_checks": sum(case["square_invariance_checks"] for case in cases),
            "all_s3_equals_six_resolvent": True,
        },
        "secp256k1": secp_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
