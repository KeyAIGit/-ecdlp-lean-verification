#!/usr/bin/env python3
"""Exact frozen replay for UORC-056 C39 spectral-root transport."""
from __future__ import annotations

import argparse
import hashlib
import json
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


def fp2_key(value: Any) -> tuple[int, int]:
    for names in (("a", "b"), ("real", "imag"), ("x", "y"), ("c0", "c1")):
        if all(hasattr(value, name) for name in names):
            return (
                int(getattr(value, names[0])) % int(value.p),
                int(getattr(value, names[1])) % int(value.p),
            )
    integers = [int(item) for item in vars(value).values() if isinstance(item, int)]
    return integers[0] % int(value.p), integers[1] % int(value.p)


def sigma(scalar: int, order: int) -> int:
    return 1 if (scalar % order) % 2 == 0 else -1


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


def add(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * max(len(left), len(right))
    for index in range(len(out)):
        out[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % p
    return trim(out, p)


def sub(left: list[int], right: list[int], p: int) -> list[int]:
    return add(left, [(-value) % p for value in right], p)


def mul(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = (out[i + j] + x * y) % p
    return trim(out, p)


def scale(poly: list[int], scalar: int, p: int) -> list[int]:
    return trim([scalar * value % p for value in poly], p)


def divmod_poly(left: list[int], right: list[int], p: int) -> tuple[list[int], list[int]]:
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
        remainder = sub(
            remainder,
            [0] * degree + scale(divisor, coefficient, p),
            p,
        )
    return trim(quotient, p), trim(remainder, p)


def mod(poly: list[int], modulus: list[int], p: int) -> list[int]:
    return divmod_poly(poly, modulus, p)[1]


def evaluate(poly: list[int], value: int, p: int) -> int:
    out = 0
    for coefficient in reversed(poly):
        out = (out * value + coefficient) % p
    return out


def root_polynomial(roots: list[int], p: int) -> list[int]:
    out = [1]
    for root in roots:
        out = mul(out, [(-root) % p, 1], p)
    return out


def interpolate(xs: list[int], ys: list[int], p: int) -> list[int]:
    if len(set(xs)) != len(xs):
        raise AssertionError("pair coordinates are not distinct")
    out = [0]
    for index, (x, y) in enumerate(zip(xs, ys)):
        numerator = [1]
        denominator = 1
        for other_index, other in enumerate(xs):
            if index == other_index:
                continue
            numerator = mul(numerator, [(-other) % p, 1], p)
            denominator = denominator * (x - other) % p
        out = add(out, scale(numerator, y * pow(denominator, -1, p), p), p)
    return trim(out, p)


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
    for scalar in range(1, n):
        value = inversion_state(curve, half, generator, table[scalar], shift)
        values.append(value)
        one = value / value
    assert one is not None

    inversion_checks = 0
    invariant: list[int] = []
    anti: list[int] = []
    for scalar, value in enumerate(values, start=1):
        opposite = inversion_state(
            curve, half, generator, table[(-scalar) % n], shift
        )
        if opposite != one / value:
            raise AssertionError("W(-Q)=W(Q)^-1 failed")
        inversion_checks += 1
        symmetric = value + one / value
        antisymmetric = value - one / value
        symmetric_real, symmetric_imag = fp2_key(symmetric)
        antisymmetric_real, antisymmetric_imag = fp2_key(antisymmetric)
        if symmetric_imag != 0 or antisymmetric_real != 0:
            raise AssertionError("base/trace-zero reduction failed")
        invariant.append(symmetric_real)
        anti.append(antisymmetric_imag)
    if any(value == 0 for value in anti):
        raise AssertionError("antisymmetric coordinate vanished")

    even_scalars = list(range(2, n, 2))
    pair_coordinates = [invariant[scalar - 1] for scalar in even_scalars]
    correction_targets = [pow(anti[scalar - 1], -1, p) for scalar in even_scalars]
    correction = interpolate(pair_coordinates, correction_targets, p)
    pair_kernel = root_polynomial(pair_coordinates, p)
    radicand = [(-4) % p, 0, 1]
    congruence = mod(
        sub(mul(mul(correction, correction, p), radicand, p), [1], p),
        pair_kernel,
        p,
    )
    if congruence != [0]:
        raise AssertionError("oriented quotient-root congruence failed")

    orientation_checks = 0
    for scalar in range(1, n):
        observed = anti[scalar - 1] * evaluate(
            correction, invariant[scalar - 1], p
        ) % p
        expected = 1 if sigma(scalar, n) == 1 else p - 1
        if observed != expected:
            raise AssertionError("orientation identity failed")
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
    reciprocal_scale = (-one if half % 2 else one) / product_even
    reciprocal = [one - one for _ in range(half + 1)]
    for index, coefficient in enumerate(even_poly):
        reciprocal[half - index] = reciprocal_scale * coefficient
    if reciprocal != odd_poly:
        raise AssertionError("reciprocal spectral-factor identity failed")

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
        "direct_character_decoder": direct_character,
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
            "direct_character_survivors": sum(
                int(bool(row["direct_character_decoder"])) for row in curves
            ),
            "errors": 0,
        },
        "decision": {
            "inversion_covariant_state_found": True,
            "spectral_factor_reduced_to_oriented_square_root": True,
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
