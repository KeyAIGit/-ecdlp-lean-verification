#!/usr/bin/env python3
"""Exact scalar-cycle core for UORC-056 C55."""
from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Iterable

from uorc056_c54_transfer_core import Curve, state, chi, point_count, is_prime

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)
SECP_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE", 16
)
SECP_LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72", 16
)
SECP_ORD2 = (SECP_N - 1) // 64

INHERITED = (
    (43, 31, (2, 12), 6, 5),
    (67, 79, (2, 22), 29, 23),
    (97, 79, (1, 28), 35, 55),
    (211, 199, (3, 33), 14, 106),
    (907, 967, (2, 165), 384, 824),
    (2143, 2089, (1, 505), 1793, 1262),
)
NEW = (
    (2677, 2647, (4, 116), 1643, 185),
    (3343, 3391, (1, 153), 1918, 2835),
    (4597, 4513, (3, 1863), 377, 814),
    (5197, 5209, (3, 125), 1878, 1192),
)
ALL = INHERITED + NEW


def multiplicative_order_two(prime: int) -> int:
    value = 1
    for order in range(1, prime):
        value = 2 * value % prime
        if value == 1:
            return order
    raise AssertionError("2 has no multiplicative order")


def doubling_cycles(prime: int) -> list[list[int]]:
    seen: set[int] = set()
    cycles: list[list[int]] = []
    for start in range(1, prime):
        if start in seen:
            continue
        cycle: list[int] = []
        value = start
        while value not in seen:
            seen.add(value)
            cycle.append(value)
            value = 2 * value % prime
        if value != start:
            raise AssertionError("doubling orbit merged into an earlier cycle")
        cycles.append(cycle)
    return cycles


def canonical_cycle_representative(cycle: Iterable[int]) -> int:
    return min(cycle)


def cycle_label(scalar: int, order: int, ord_two: int) -> int:
    """Exact full-cycle label k^ord_2(2) in mu_index subset F_n^*."""
    return pow(scalar % order, ord_two, order)


def pair_cycle_label(scalar: int, order: int, ord_two: int) -> int:
    """Negation-invariant label k^(2*ord_2(2))."""
    return pow(scalar % order, 2 * ord_two, order)


def parity_sign(scalar: int) -> int:
    return -1 if scalar & 1 else 1


def cycle_orientation_norm(cycle: Iterable[int]) -> int:
    out = 1
    for scalar in cycle:
        out *= parity_sign(scalar)
    return out


def cycle_carries(cycle: list[int], order: int) -> list[int]:
    carries = []
    for index, scalar in enumerate(cycle):
        target = cycle[(index + 1) % len(cycle)]
        numerator = 2 * scalar - target
        if numerator not in (0, order):
            raise AssertionError("invalid canonical doubling carry")
        carries.append(numerator // order)
    return carries


def mixed_parity(cycle: Iterable[int]) -> bool:
    values = {scalar & 1 for scalar in cycle}
    return values == {0, 1}


def ceil_sqrt(value: int) -> int:
    root = isqrt(value)
    return root if root * root == value else root + 1


def verify_curve_fixture(row: tuple[int, int, tuple[int, int], int, int]) -> None:
    p, n, generator, beta, lam = row
    curve = Curve(p)
    if point_count(curve) != n or not is_prime(n):
        raise AssertionError("curve order contract")
    if not curve.on_curve(generator) or curve.mul(n, generator) is not None:
        raise AssertionError("generator contract")
    if beta in (0, 1) or pow(beta, 3, p) != 1:
        raise AssertionError("field cube root")
    if lam in (0, 1) or (lam * lam + lam + 1) % n:
        raise AssertionError("scalar cube root")
    if curve.mul(lam, generator, n) != (beta * generator[0] % p, generator[1]):
        raise AssertionError("GLV action")
    if multiplicative_order_two(n) % 2 != 1:
        raise AssertionError("C55 corpus requires odd doubling order")


def cycle_phase_index(cycle: list[int], scalar: int) -> int:
    try:
        return cycle.index(scalar)
    except ValueError as exc:
        raise AssertionError("scalar not in cycle") from exc


def bsgs_generic_cost(order: int) -> int:
    return ceil_sqrt(order)


def secp_certificate() -> dict[str, int | bool | str]:
    factors = (
        3,
        149,
        631,
        107361793816595537,
        174723607534414371449,
        341948486974166000522343609283189,
    )
    if pow(2, SECP_ORD2, SECP_N) != 1:
        raise AssertionError("wrong secp doubling order")
    minimality = {
        str(prime): pow(2, SECP_ORD2 // prime, SECP_N) != 1
        for prime in factors
    }
    if not all(minimality.values()):
        raise AssertionError("secp order minimality failed")
    index = (SECP_N - 1) // SECP_ORD2
    if index != 64 or SECP_ORD2 % 2 != 1:
        raise AssertionError("secp cycle index")
    if pow(2, SECP_ORD2 // 3, SECP_N) != pow(SECP_LAMBDA, 2, SECP_N):
        raise AssertionError("lambda is not in the doubling subgroup")
    degree_lower_bound = (SECP_N - 1 + 4) // 5
    return {
        "n": SECP_N,
        "p": SECP_P,
        "ord_n_2": SECP_ORD2,
        "ord_n_2_bits": SECP_ORD2.bit_length(),
        "ord_n_2_is_odd": True,
        "full_cycle_count": index,
        "pair_cycle_count": index // 2,
        "full_cycle_label_states": index,
        "pair_cycle_label_states": index // 2,
        "lambda_in_doubling_subgroup": True,
        "cycle_label_formula": "L(k)=k^ord_n(2) mod n in mu_64",
        "pair_label_formula": "L_pair(k)=k^(2 ord_n(2)) mod n in mu_32",
        "generic_within_cycle_bsgs_cost": bsgs_generic_cost(SECP_ORD2),
        "generic_within_cycle_bsgs_cost_bits": bsgs_generic_cost(SECP_ORD2).bit_length(),
        "rational_cycle_invariant_pole_degree_lower_bound": degree_lower_bound,
        "rational_cycle_invariant_pole_degree_lower_bound_bits": degree_lower_bound.bit_length(),
        "minimality_checks": minimality,
    }
