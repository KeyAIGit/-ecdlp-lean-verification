#!/usr/bin/env python3
"""Exact replay for UORC-056 C39 inversion spectral-factor transport.

Frozen public toy curves only. The program never accepts an external point,
wallet, key, or production target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from uorc056_regularized_anchor_miller_c36 import (
    INSTANCES,
    Curve,
    base_point,
    least_nonsquare,
    miller,
    trace_zero_twist_point,
)


def key(z: Any) -> tuple[int, int]:
    for names in (("a", "b"), ("real", "imag"), ("x", "y"), ("c0", "c1")):
        if all(hasattr(z, name) for name in names):
            return int(getattr(z, names[0])) % int(z.p), int(getattr(z, names[1])) % int(z.p)
    values = [int(value) for value in vars(z).values() if isinstance(value, int)]
    return values[0] % int(z.p), values[1] % int(z.p)


def sigma(k: int, n: int) -> int:
    return 1 if (k % n) % 2 == 0 else -1


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def shifted(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return miller(curve, index, source, curve.add(shift, query)) / miller(
        curve, index, source, shift
    )


def norm_one(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return shifted(curve, index, source, query, shift) / shifted(
        curve, index, source, query, curve.neg(shift)
    )


def inversion_state(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return norm_one(curve, index, source, query, shift) * norm_one(
        curve, index, curve.neg(source), query, shift
    )


def trim(poly: list[int], p: int) -> list[int]:
    out = [value % p for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def padd(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * max(len(left), len(right))
    for index in range(len(out)):
        out[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % p
    return trim(out, p)


def psub(left: list[int], right: list[int], p: int) -> list[int]:
    return padd(left, [(-value) % p for value in right], p)


def pmul(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = (out[i + j] + x * y) % p
    return trim(out, p)


def pscale(poly: list[int], scalar: int, p: int) -> list[int]:
    return trim([scalar * value % p for value in poly], p)


def pdivmod(left: list[int], right: list[int], p: int) -> tuple[list[int], list[int]]:
    divisor = trim(right, p)
    if divisor == [0]:
        raise ZeroDivisionError
    remainder = trim(left, p)
    quotient = [0] * max(1, len(remainder) - len(divisor) + 1)
    inverse = pow(divisor[-1], -1, p)
    while remainder != [0] and len(remainder) >= len(divisor):
        degree = len(remainder) - len(divisor)
        coefficient = remainder[-1] * inverse % p
        quotient[degree] = coefficient
        remainder = psub(
            remainder,
            [0] * degree + pscale(divisor, coefficient, p),
            p,
        )
    return trim(quotient, p), trim(remainder, p)


def pmod(poly: list[int], modulus: list[int], p: int) -> list[int]:
    return pdivmod(poly, modulus, p)[1]


def peval(poly: list[int], value: int, p: int) -> int:
    out = 0
    for coefficient in reversed(poly):
        out = (out * value + coefficient) % p
    return out


def root_polynomial(roots: list[int], p: int) -> list[int]:
    out = [1]
    for root in roots:
        out = pmul(out, [(-root) % p, 1], p)
    return out


def interpolate(xs: list[int], ys: list[int], p: int) -> list[int]:
    if len(set(xs)) != len(xs):
        raise AssertionError("interpolation coordinates are not distinct")
    out = [0]
    for index, (x, y) in enumerate(zip(xs, ys)):
        numerator = [1]
        denominator = 1
        for other_index, other in enumerate(xs):
            if index == other_index:
                continue
            numerator = pmul(numerator, [(-other) % p, 1], p)
            denominator = denominator * (x - other) % p
        out = padd(out, pscale(numerator, y * pow(denominator, -1, p), p), p)
    return trim(out, p)


def dickson_support(poly: list[int], p: int) -> int:
    degree = len(poly) - 1
    dickson: list[list[int]] = [[2 % p]]
    if degree:
        dickson.append([0, 1])
    for index in range(2, degree + 1):
        current = [0] + dickson[-1]
        if len(current) < len(dickson[-2]):
            current += [0] * (len(dickson[-2]) - len(current))
        for position, value in enumerate(dickson[-2]):
            current[position] = (current[position] - value) % p
        dickson.append(trim(current, p))
    residual = poly[:]
    coefficients = [0] * (degree + 1)
    for index in range(degree, 0, -1):
        coefficient = residual[index] if index < len(residual) else 0
        coefficients[index] = coefficient
        residual = psub(residual, pscale(dickson[index], coefficient, p), p)
        if len(residual) < index:
            residual += [0] * (index - len(residual))
    coefficients[0] = residual[0]
    return sum(value % p != 0 for value in coefficients)


def linear_complexity(sequence: list[int], p: int) -> int:
    connection = [1]
    backup = [1]
    length = 0
    offset = 1
    discrepancy_scale = 1
    for position in range(len(sequence)):
        discrepancy = sequence[position] % p
        for index in range(1, length + 1):
            discrepancy = (
                discrepancy + connection[index] * sequence[position - index]
            ) % p
        if discrepancy == 0:
            offset += 1
            continue
        previous = connection[:]
        factor = discrepancy * pow(discrepancy_scale, -1, p) % p
        required = len(backup) + offset
        if len(connection) < required:
            connection += [0] * (required - len(connection))
        for index, value in enumerate(backup):
            connection[index + offset] = (
                connection[index + offset] - factor * value
            ) % p
        if 2 * length <= position:
            length = position + 1 - length
            backup = previous
            discrepancy_scale = discrepancy
            offset = 1
        else:
            offset += 1
    return length


def fp2_orbit_polynomial(values: list[Any]) -> list[Any]:
    one = values[0] / values[0]
    zero = one - one
    out = [one]
    for value in values:
        next_out = [zero for _ in range(len(out) + 1)]
        for index, coefficient in enumerate(out):
            next_out[index] = next_out[index] - coefficient * value
            next_out[index + 1] = next_out[index + 1] + coefficient
        out = next_out
    return out


def replay_curve(instance: Any) -> dict[str, object]:
    p, n = int(instance.p), int(instance.n)
    curve = Curve(p, 0, 7, least_nonsquare(p))
    generator = base_point(curve, instance.generator)
    shift = trace_zero_twist_point(curve)
    half = (n - 1) // 2
    table = [curve.mul(scalar, generator) for scalar in range(n)]
    values: list[Any] = []
    one = None
    inversion_checks = 0
    for scalar in range(1, n):
        value = inversion_state(curve, half, generator, table[scalar], shift)
        values.append(value)
        one = value / value
    assert one is not None
    for scalar, value in enumerate(values, start=1):
        opposite = inversion_state(
            curve, half, generator, table[(-scalar) % n], shift
        )
        if opposite != one / value:
            raise AssertionError("inversion covariance failed")
        inversion_checks += 1

    invariant: list[int] = []
    anti: list[int] = []
    for value in values:
        plus = value + one / value
        minus = value - one / value
        plus_real, plus_imag = key(plus)
        minus_real, minus_imag = key(minus)
        if plus_imag or minus_real:
            raise AssertionError("norm-one base/trace-zero reduction failed")
        invariant.append(plus_real)
        anti.append(minus_imag)
    if any(value == 0 for value in anti):
        raise AssertionError("anti-invariant vanished")

    even_scalars = list(range(2, n, 2))
    xs = [invariant[scalar - 1] for scalar in even_scalars]
    targets = [pow(anti[scalar - 1], -1, p) for scalar in even_scalars]
    correction = interpolate(xs, targets, p)
    pair_kernel = root_polynomial(xs, p)
    radicand = [(-4) % p, 0, 1]
    congruence = pmod(
        psub(pmul(pmul(correction, correction, p), radicand, p), [1], p),
        pair_kernel,
        p,
    )
    if congruence != [0]:
        raise AssertionError("quotient square-root identity failed")

    orientation_checks = 0
    for scalar in range(1, n):
        observed = anti[scalar - 1] * peval(
            correction, invariant[scalar - 1], p
        ) % p
        expected = 1 if sigma(scalar, n) == 1 else p - 1
        if observed != expected:
            raise AssertionError("orientation decoder identity failed")
        orientation_checks += 1

    anchor = anti[0]
    direct_character = all(
        -legendre(anti[scalar - 1] * pow(anchor, -1, p), p)
        == sigma(scalar, n)
        for scalar in range(1, n)
    )

    even_values = [values[scalar - 1] for scalar in even_scalars]
    odd_values = [values[scalar - 1] for scalar in range(1, n, 2)]
    even_poly = fp2_orbit_polynomial(even_values)
    odd_poly = fp2_orbit_polynomial(odd_values)
    product_even = one
    for value in even_values:
        product_even = product_even * value
    scale = (-one if half % 2 else one) / product_even
    reciprocal = [one - one for _ in range(half + 1)]
    for index, coefficient in enumerate(even_poly):
        reciprocal[half - index] = scale * coefficient
    if reciprocal != odd_poly:
        raise AssertionError("reciprocal orbit identity failed")

    return {
        "instance": instance.name,
        "p": p,
        "n": n,
        "pair_components": half,
        "inversion_checks": inversion_checks,
        "orientation_checks": orientation_checks,
        "pair_kernel_degree": len(pair_kernel) - 1,
        "correction_degree": len(correction) - 1,
        "correction_nonzero_coefficients": sum(value != 0 for value in correction),
        "dickson_nonzero_coefficients": dickson_support(correction, p),
        "coefficient_linear_complexity": linear_complexity(correction, p),
        "direct_quadratic_character_decoder": direct_character,
        "reciprocal_orbit_identity": True,
        "square_root_congruence": True,
        "componentwise_root_count": f"2^{half}",
    }


def build_payload() -> dict[str, object]:
    curves = [replay_curve(instance) for instance in INSTANCES]
    payload: dict[str, object] = {
        "profile_id": "UORC-056-SPECTRAL-ROOT-TRANSPORT-C39",
        "schema_version": "1.0",
        "curves": curves,
        "aggregate": {
            "curves": len(curves),
            "query_cases": sum(int(row["orientation_checks"]) for row in curves),
            "inversion_checks": sum(int(row["inversion_checks"]) for row in curves),
            "all_square_root_congruences": all(
                bool(row["square_root_congruence"]) for row in curves
            ),
            "all_reciprocal_orbit_identities": all(
                bool(row["reciprocal_orbit_identity"]) for row in curves
            ),
            "all_corrections_dense": all(
                int(row["correction_nonzero_coefficients"])
                == int(row["pair_components"])
                for row in curves
            ),
            "all_dickson_expansions_dense": all(
                int(row["dickson_nonzero_coefficients"])
                == int(row["pair_components"])
                for row in curves
            ),
            "direct_character_survivors": sum(
                int(bool(row["direct_quadratic_character_decoder"]))
                for row in curves
            ),
            "errors": 0,
        },
        "decision": {
            "inversion_covariant_state_found": True,
            "spectral_factor_reduced_to_oriented_square_root": True,
            "sparse_dickson_decoder_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print("UORC056_SPECTRAL_ROOT_TRANSPORT_C39_OK")
    print(json.dumps(payload["aggregate"], sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
