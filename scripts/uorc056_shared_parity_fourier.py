#!/usr/bin/env python3
"""Odd-cycle Fourier arithmetic for UORC-056 V19."""
from __future__ import annotations

import math
from collections.abc import Sequence


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


def prime_factors(n: int) -> tuple[int, ...]:
    if n <= 0:
        raise ValueError("n must be positive")
    out: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        out.append(n)
    return tuple(out)


def find_root_field(order: int) -> tuple[int, int]:
    if order <= 1 or order % 2 == 0:
        raise ValueError("order must be odd and greater than one")
    factors = prime_factors(order)
    multiplier = 1
    while True:
        modulus = multiplier * order + 1
        if is_prime(modulus):
            exponent = (modulus - 1) // order
            for base in range(2, modulus):
                root = pow(base, exponent, modulus)
                if root != 1 and pow(root, order, modulus) == 1 and all(
                    pow(root, order // factor, modulus) != 1
                    for factor in factors
                ):
                    return modulus, root
        multiplier += 1


def parity_values(order: int, modulus: int) -> list[int]:
    return [1 if k % 2 == 0 else modulus - 1 for k in range(order)]


def dft(values: Sequence[int], root: int, modulus: int) -> list[int]:
    order = len(values)
    if pow(root, order, modulus) != 1:
        raise ValueError("root order is incompatible")
    out: list[int] = []
    for frequency in range(order):
        ratio = pow(root, (-frequency) % order, modulus)
        power = 1
        total = 0
        for value in values:
            total = (total + value * power) % modulus
            power = power * ratio % modulus
        out.append(total)
    return out


def parity_dft_formula(order: int, root: int, modulus: int) -> list[int]:
    if order % 2 == 0:
        raise ValueError("odd order required")
    out: list[int] = []
    for frequency in range(order):
        denominator = (
            1 + pow(root, (-frequency) % order, modulus)
        ) % modulus
        if denominator == 0:
            raise AssertionError("-1 cannot be an odd-order root")
        out.append(2 * pow(denominator, -1, modulus) % modulus)
    return out


def support(values: Sequence[int]) -> tuple[int, ...]:
    return tuple(i for i, value in enumerate(values) if value != 0)


def pair_sum_cover_bound(target: int) -> int:
    if target < 0:
        raise ValueError("target must be nonnegative")
    value = max(0, (math.isqrt(1 + 8 * target) - 1) // 2)
    while value * (value + 1) // 2 < target:
        value += 1
    while value and (value - 1) * value // 2 >= target:
        value -= 1
    return value


def bilinear_leaf_sum_bound(target: int) -> int:
    if target <= 0:
        return 0
    total = 2 * math.isqrt(target)
    while (total // 2) * ((total + 1) // 2) < target:
        total += 1
    while total and ((total - 1) // 2) * (total // 2) >= target:
        total -= 1
    return total
