#!/usr/bin/env python3
"""Deterministic production arithmetic for secp256k1-like toy curves.

The P1 assay uses prime fields with ``p % 12 == 7`` and the exact short
Weierstrass equation ``y^2 = x^3 + 7``.  This preserves the j=0 shape,
``p % 4 == 3`` square-root shortcut, and a non-trivial cube-root endomorphism.

This module is the producer implementation.  The independent validator uses
``experiments/framework/ec_oracle.py`` and does not import this file.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Iterable


Point = tuple[int, int] | None


def is_prime(value: int) -> bool:
    """Deterministic Miller-Rabin primality for the 32-bit catalog range."""
    if value < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    odd = value - 1
    exponent = 0
    while odd % 2 == 0:
        exponent += 1
        odd //= 2
    for base in (2, 3, 5, 7, 11):
        if base >= value:
            continue
        witness = pow(base, odd, value)
        if witness in (1, value - 1):
            continue
        for _ in range(exponent - 1):
            witness = witness * witness % value
            if witness == value - 1:
                break
        else:
            return False
    return True


def tonelli_shanks(value: int, prime: int) -> int | None:
    """Return one square root modulo an odd prime, or ``None``."""
    value %= prime
    if value == 0:
        return 0
    if pow(value, (prime - 1) // 2, prime) != 1:
        return None
    if prime % 4 == 3:
        return pow(value, (prime + 1) // 4, prime)
    odd = prime - 1
    exponent = 0
    while odd % 2 == 0:
        exponent += 1
        odd //= 2
    non_residue = 2
    while pow(non_residue, (prime - 1) // 2, prime) != prime - 1:
        non_residue += 1
    root = pow(value, (odd + 1) // 2, prime)
    residue_power = pow(value, odd, prime)
    generator = pow(non_residue, odd, prime)
    remaining = exponent
    while residue_power != 1:
        index = 1
        squared = residue_power * residue_power % prime
        while index < remaining and squared != 1:
            squared = squared * squared % prime
            index += 1
        if index == remaining:
            return None
        correction = pow(generator, 1 << (remaining - index - 1), prime)
        root = root * correction % prime
        residue_power = residue_power * correction * correction % prime
        generator = correction * correction % prime
        remaining = index
    return root


@dataclass(frozen=True)
class Curve:
    p: int
    a: int = 0
    b: int = 7

    def __post_init__(self) -> None:
        if self.p <= 3 or not is_prime(self.p):
            raise ValueError("toy curve requires a prime field with p > 3")
        discriminant = (
            4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)
        ) % self.p
        if discriminant == 0:
            raise ValueError("singular toy curve")

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            0 <= x < self.p
            and 0 <= y < self.p
            and (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0
        )

    def negate(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        if not self.is_on_curve(left) or not self.is_on_curve(right):
            raise ValueError("point is not on the curve")
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.is_on_curve(result):
            raise AssertionError("curve arithmetic produced an off-curve point")
        return result

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.scalar_mul(-scalar, self.negate(point))
        if not self.is_on_curve(point):
            raise ValueError("point is not on the curve")
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            remaining >>= 1
        return result


def derive_integer(domain: bytes, modulus: int, counter: int = 0) -> int:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    sample_space = 1 << 256
    acceptance_limit = sample_space - sample_space % modulus
    attempt = counter
    while True:
        digest = hashlib.sha256(domain + attempt.to_bytes(8, "big")).digest()
        candidate = int.from_bytes(digest, "big")
        if candidate < acceptance_limit:
            return candidate % modulus
        attempt += 1


def deterministic_point(curve: Curve, domain: bytes) -> Point:
    """Find a deterministic non-infinity point without enumerating the curve."""
    for counter in range(1_000_000):
        x = derive_integer(domain, curve.p, counter)
        rhs = (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p
        y = tonelli_shanks(rhs, curve.p)
        if y is None:
            continue
        if (hashlib.sha256(domain + counter.to_bytes(8, "big")).digest()[0] & 1) != (
            y & 1
        ):
            y = curve.p - y
        point = (x, y)
        if point != (0, 0) and curve.is_on_curve(point):
            return point
    raise RuntimeError("failed to derive a toy-curve point")


def hasse_bounds(prime: int) -> tuple[int, int, int]:
    bound = math.isqrt(4 * prime)
    return prime + 1 - bound, prime + 1 + bound, bound


def _point_key(point: Point) -> tuple[int, int] | None:
    return point


def candidate_orders_from_hasse_bsgs(curve: Curve, point: Point) -> list[int]:
    """Return group-order candidates that annihilate ``point`` in Hasse range.

    The search solves ``[t]P = [p+1]P`` for ``|t| <= 2 sqrt(p)`` by an
    interval baby-step giant-step search and maps each trace candidate to
    ``#E = p + 1 - t``.
    """
    if point is None:
        raise ValueError("point must not be infinity")
    lower, upper, bound = hasse_bounds(curve.p)
    interval_size = 2 * bound + 1
    width = math.isqrt(interval_size)
    if width * width < interval_size:
        width += 1
    baby: dict[tuple[int, int] | None, list[int]] = {}
    current: Point = None
    for offset in range(width):
        baby.setdefault(_point_key(current), []).append(offset)
        current = curve.add(current, point)
    giant_stride = curve.scalar_mul(width, point)
    target = curve.scalar_mul(curve.p + 1 + bound, point)
    negative_stride = curve.negate(giant_stride)
    candidates: set[int] = set()
    giant_count = (interval_size + width - 1) // width
    current = target
    for giant_index in range(giant_count + 1):
        for baby_index in baby.get(_point_key(current), []):
            shifted_trace = giant_index * width + baby_index
            if shifted_trace >= interval_size:
                continue
            trace = shifted_trace - bound
            order = curve.p + 1 - trace
            if lower <= order <= upper and curve.scalar_mul(order, point) is None:
                candidates.add(order)
        current = curve.add(current, negative_stride)
    return sorted(candidates)


def prime_order_certificate(curve: Curve, point: Point) -> int | None:
    """Find a prime curve order and verify the Hasse uniqueness certificate."""
    _, upper, _ = hasse_bounds(curve.p)
    for order in candidate_orders_from_hasse_bsgs(curve, point):
        if (
            is_prime(order)
            and 2 * order > upper
            and curve.scalar_mul(order, point) is None
        ):
            return order
    return None


def cube_roots_of_unity(prime: int) -> tuple[int, int]:
    root = tonelli_shanks(-3, prime)
    if root is None:
        raise ValueError("field has no non-trivial cube roots of unity")
    inverse_two = pow(2, -1, prime)
    candidates = {
        (-1 + root) * inverse_two % prime,
        (-1 - root) * inverse_two % prime,
    }
    nontrivial = sorted(value for value in candidates if value != 1)
    if len(nontrivial) != 2 or any(pow(value, 3, prime) != 1 for value in nontrivial):
        raise AssertionError("invalid cube roots of unity")
    return nontrivial[0], nontrivial[1]


def glv_parameters(curve: Curve, order: int, generator: Point) -> tuple[int, int]:
    """Return ``(beta, lambda)`` with phi(x,y)=(beta*x,y)=[lambda](x,y)."""
    if generator is None:
        raise ValueError("generator must not be infinity")
    beta_candidates = cube_roots_of_unity(curve.p)
    lambda_candidates = cube_roots_of_unity(order)
    for beta in beta_candidates:
        image = (beta * generator[0] % curve.p, generator[1])
        if not curve.is_on_curve(image):
            continue
        for eigenvalue in lambda_candidates:
            if curve.scalar_mul(eigenvalue, generator) == image:
                return beta, eigenvalue
    raise RuntimeError("failed to match the j=0 GLV eigenvalue")


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    remainder = value
    divisor = 2
    while divisor * divisor <= remainder:
        if remainder % divisor == 0:
            factors.append(divisor)
            while remainder % divisor == 0:
                remainder //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remainder > 1:
        factors.append(remainder)
    return factors


def multiplicative_order(value: int, prime: int) -> int:
    """Return the multiplicative order of ``value`` modulo ``prime``."""
    value %= prime
    if value == 0:
        raise ValueError("value must be nonzero modulo prime")
    order = prime - 1
    for factor in prime_factors(order):
        while order % factor == 0 and pow(value, order // factor, prime) == 1:
            order //= factor
    return order


def prime_candidates(bits: int, domain: bytes) -> Iterable[int]:
    """Yield exact-width primes congruent to 7 modulo 12 in deterministic order."""
    if not 8 <= bits <= 32:
        raise ValueError("toy catalog supports field widths from 8 to 32 bits")
    lower = 1 << (bits - 1)
    upper = 1 << bits
    first = lower + (7 - lower) % 12
    slots = ((upper - 1 - first) // 12) + 1
    start_slot = derive_integer(domain, slots)
    for offset in range(slots):
        candidate = first + 12 * ((start_slot + offset) % slots)
        if is_prime(candidate):
            yield candidate


def search_curve(
    bits: int,
    curve_index: int,
    used_primes: set[int],
    catalog_nonce: str,
) -> dict[str, object]:
    """Search one certified prime-order ``a=0,b=7`` toy curve."""
    if not catalog_nonce:
        raise ValueError("toy catalog nonce must be non-empty")
    domain = (
        f"keyai/p1-toy-curve/v2/{catalog_nonce}/{bits}/{curve_index}"
    ).encode("utf-8")
    examined = 0
    for prime in prime_candidates(bits, domain):
        if prime in used_primes:
            continue
        examined += 1
        curve = Curve(prime, 0, 7)
        point = deterministic_point(curve, domain + prime.to_bytes(4, "big"))
        order = prime_order_certificate(curve, point)
        if (
            order is None
            or order.bit_length() != bits
            or order == prime
        ):
            continue
        beta, eigenvalue = glv_parameters(curve, order, point)
        embedding_degree = multiplicative_order(prime, order)
        if embedding_degree <= 100:
            continue
        lower, upper, bound = hasse_bounds(prime)
        return {
            "id": f"toy-secp-j0-b{bits}-c{curve_index}-p{prime}",
            "field_bits": bits,
            "field_p": prime,
            "curve_a": 0,
            "curve_b": 7,
            "group_order": order,
            "cofactor": 1,
            "anomalous": False,
            "embedding_degree": embedding_degree,
            "base_point": [point[0], point[1]],
            "hasse": {
                "lower": lower,
                "upper": upper,
                "trace_bound": bound,
                "twice_order_exceeds_upper": 2 * order > upper,
            },
            "glv": {
                "beta": beta,
                "lambda": eigenvalue,
                "beta_polynomial_zero": (beta * beta + beta + 1) % prime == 0,
                "lambda_polynomial_zero": (
                    eigenvalue * eigenvalue + eigenvalue + 1
                )
                % order
                == 0,
                "eigenpair_checked": True,
            },
            "search": {"prime_candidates_examined": examined},
        }
    raise RuntimeError(f"no certified toy curve found for {bits} bits")


def derive_generators(entry: dict[str, object], count: int) -> list[dict[str, object]]:
    curve = Curve(
        int(entry["field_p"]), int(entry["curve_a"]), int(entry["curve_b"])
    )
    order = int(entry["group_order"])
    base_raw = entry["base_point"]
    if not isinstance(base_raw, list) or len(base_raw) != 2:
        raise ValueError("invalid base point")
    base = (int(base_raw[0]), int(base_raw[1]))
    generators: list[dict[str, object]] = []
    used: set[Point] = set()
    used_multiplier_orbits: set[int] = set()
    glv = entry.get("glv")
    if not isinstance(glv, dict):
        raise ValueError("catalog entry lacks GLV parameters")
    eigenvalue = int(glv["lambda"])

    def multiplier_orbit(multiplier: int) -> set[int]:
        orbit: set[int] = set()
        current = multiplier % order
        for _ in range(3):
            orbit.add(current)
            orbit.add((-current) % order)
            current = current * eigenvalue % order
        return orbit

    for index in range(count):
        domain = f"keyai/p1-toy-generator/v1/{entry['id']}/{index}".encode("ascii")
        multiplier = 1 + derive_integer(domain, order - 1)
        point = curve.scalar_mul(multiplier, base)
        orbit = multiplier_orbit(multiplier)
        while (
            point in used
            or point is None
            or bool(orbit & used_multiplier_orbits)
        ):
            multiplier = 1 + (multiplier % (order - 1))
            point = curve.scalar_mul(multiplier, base)
            orbit = multiplier_orbit(multiplier)
        used.add(point)
        used_multiplier_orbits.update(orbit)
        generators.append(
            {
                "id": f"{entry['id']}-g{index}",
                "point": [point[0], point[1]],
                "base_multiplier": multiplier,
            }
        )
    return generators
