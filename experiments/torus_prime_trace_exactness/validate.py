#!/usr/bin/env python3
"""Exact toy audit for the odd-order norm-one torus trace circuit.

This certificate does not run a Semaev or Groebner solver.  It checks the
algebraic interface that must be exact before such a run can be authorized:

* subgroup traces in the norm-one torus;
* roots of the Dickson polynomial D_N(X) - 2;
* the squarefree trace polynomial and inversion-fiber counts;
* the odd-N factorization through Lucas/Dickson recurrences;
* a logarithmic-depth fast recurrence against the literal recurrence;
* curve-lift histograms for j=0 and non-j=0 controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import factorial


TOY_CASES = (
    (43, 11),
    (67, 17),
    (103, 13),
    (163, 41),
    (211, 53),
    (283, 71),
    (331, 83),
)

SECP_P = 2**256 - 2**32 - 977
SECP_PPLUS1_FACTORS = (16, 7_322_137, 45_422_601_869_677)


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors


def is_prime(n: int) -> bool:
    return n >= 2 and prime_factors(n) == [n]


def is_prime_u64(n: int) -> bool:
    """Deterministic Miller-Rabin for n < 2^64."""
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if n % prime == 0:
            return n == prime
    d, power = n - 1, 0
    while d % 2 == 0:
        d //= 2
        power += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        value = pow(base % n, d, n)
        if value in (1, n - 1):
            continue
        for _ in range(power - 1):
            value = value * value % n
            if value == n - 1:
                break
        else:
            return False
    return True


@dataclass(frozen=True)
class Fp2:
    a: int
    b: int
    p: int
    nu: int = -1

    def __mul__(self, other: "Fp2") -> "Fp2":
        assert self.p == other.p and self.nu == other.nu
        return Fp2(
            (self.a * other.a + self.nu * self.b * other.b) % self.p,
            (self.a * other.b + self.b * other.a) % self.p,
            self.p,
            self.nu,
        )

    def __pow__(self, exponent: int) -> "Fp2":
        result = Fp2(1, 0, self.p, self.nu)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result


def find_torus_generator(p: int) -> Fp2:
    """Find an element of exact order p+1 by exhaustive toy search."""
    order = p + 1
    one = Fp2(1, 0, p)
    for a in range(p):
        for b in range(p):
            # Norm(a+b*w) = a^2+b^2 because w^2=-1 and p=3 mod 4.
            if (a * a + b * b) % p != 1:
                continue
            candidate = Fp2(a, b, p)
            if candidate**order != one:
                continue
            if all(candidate ** (order // r) != one for r in prime_factors(order)):
                return candidate
    raise AssertionError(f"no torus generator for p={p}")


def poly_trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_add(left: list[int], right: list[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    result = [0] * size
    for index in range(size):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % p
    return poly_trim(result)


def poly_scale(poly: list[int], scalar: int, p: int) -> list[int]:
    return poly_trim([(scalar * coefficient) % p for coefficient in poly])


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % p
    return poly_trim(result)


def poly_eval(poly: list[int], x: int, p: int) -> int:
    value = 0
    for coefficient in reversed(poly):
        value = (value * x + coefficient) % p
    return value


def poly_derivative(poly: list[int], p: int) -> list[int]:
    if len(poly) == 1:
        return [0]
    return poly_trim([(i * poly[i]) % p for i in range(1, len(poly))])


def dickson_polynomial(n: int, p: int) -> list[int]:
    """D_0=2, D_1=X, D_n=X*D_(n-1)-D_(n-2)."""
    if n == 0:
        return [2]
    previous, current = [2], [0, 1]
    for _ in range(2, n + 1):
        following = poly_add(
            poly_mul([0, 1], current, p),
            poly_scale(previous, -1, p),
            p,
        )
        previous, current = current, following
    return current


def lucas_u_polynomial(n: int, p: int) -> list[int]:
    """U_0=1, U_1=X, U_n=X*U_(n-1)-U_(n-2)."""
    if n == 0:
        return [1]
    previous, current = [1], [0, 1]
    for _ in range(2, n + 1):
        following = poly_add(
            poly_mul([0, 1], current, p),
            poly_scale(previous, -1, p),
            p,
        )
        previous, current = current, following
    return current


def dickson_literal(n: int, x: int, p: int) -> int:
    if n == 0:
        return 2
    previous, current = 2, x
    for _ in range(2, n + 1):
        previous, current = current, (x * current - previous) % p
    return current


def dickson_fast_pair(n: int, x: int, p: int) -> tuple[int, int, int]:
    """Return (D_n, D_(n+1), nonlinear-gate count) in O(log n)."""
    if n == 0:
        return 2, x, 0
    a, b, gates = dickson_fast_pair(n // 2, x, p)
    even = (a * a - 2) % p
    odd = (a * b - x) % p
    next_even = (b * b - 2) % p
    if n % 2 == 0:
        return even, odd, gates + 3
    return odd, next_even, gates + 3


def root_product(roots: set[int], p: int) -> list[int]:
    polynomial = [1]
    for root in sorted(roots):
        polynomial = poly_mul(polynomial, [(-root) % p, 1], p)
    return polynomial


def lift_histogram(roots: set[int], p: int, a: int, b: int) -> tuple[int, int, int]:
    histogram = [0, 0, 0]
    for x in roots:
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            histogram[1] += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            histogram[2] += 1
        else:
            histogram[0] += 1
    return tuple(histogram)


def audit_case(p: int, order: int) -> dict[str, object]:
    assert is_prime(p)
    assert p % 4 == 3
    assert is_prime(order)
    assert (p + 1) % order == 0

    torus_generator = find_torus_generator(p)
    subgroup_generator = torus_generator ** ((p + 1) // order)
    one = Fp2(1, 0, p)
    assert subgroup_generator**order == one
    assert subgroup_generator != one

    elements = [subgroup_generator**index for index in range(order)]
    traces = {(2 * element.a) % p for element in elements}
    fibers = {
        trace: sum((2 * element.a) % p == trace for element in elements)
        for trace in traces
    }
    assert len(traces) == (order + 1) // 2
    assert sorted(fibers.values()).count(1) == 1
    assert all(size in (1, 2) for size in fibers.values())

    raw = dickson_polynomial(order, p)
    raw[0] = (raw[0] - 2) % p
    raw = poly_trim(raw)
    roots = {x for x in range(p) if poly_eval(raw, x, p) == 0}
    assert roots == traces

    derivative = poly_derivative(raw, p)
    fixed = {2 % p}
    assert all(poly_eval(derivative, x, p) != 0 for x in fixed)
    assert all(poly_eval(derivative, x, p) == 0 for x in roots - fixed)

    squarefree = root_product(roots, p)
    squarefree_derivative = poly_derivative(squarefree, p)
    assert len(squarefree) - 1 == len(traces)
    assert all(poly_eval(squarefree_derivative, x, p) != 0 for x in roots)

    half = (order - 1) // 2
    u_half = lucas_u_polynomial(half, p)
    u_before = lucas_u_polynomial(half - 1, p)
    factor = poly_add(u_half, u_before, p)
    factored = poly_mul(
        [(-2) % p, 1],
        poly_mul(factor, factor, p),
        p,
    )
    assert raw == factored

    max_gates = 0
    for x in range(p):
        fast, _, gates = dickson_fast_pair(order, x, p)
        assert fast == dickson_literal(order, x, p)
        max_gates = max(max_gates, gates)
    assert max_gates <= 3 * order.bit_length()

    j0_lifts = lift_histogram(roots, p, 0, 7)
    control_lifts = lift_histogram(roots, p, 1, 7)
    assert sum(j0_lifts) == len(roots)
    assert sum(control_lifts) == len(roots)

    return {
        "p": p,
        "order": order,
        "trace_roots": len(traces),
        "fiber_histogram": {
            "one": sum(size == 1 for size in fibers.values()),
            "two": sum(size == 2 for size in fibers.values()),
        },
        "raw_degree": len(raw) - 1,
        "squarefree_degree": len(squarefree) - 1,
        "fast_nonlinear_gates": max_gates,
        "j0_lifts_0_1_2": j0_lifts,
        "control_lifts_0_1_2": control_lifts,
    }


def audit_secp_parameters() -> dict[str, int]:
    two_power, small_odd, large_odd = SECP_PPLUS1_FACTORS
    smooth_component = two_power * small_odd * large_odd
    assert (SECP_P + 1) % smooth_component == 0
    cofactor = (SECP_P + 1) // smooth_component
    assert is_prime_u64(small_odd)
    assert is_prime_u64(large_odd)

    small_trace_degree = (small_odd + 1) // 2
    large_trace_degree = (large_odd + 1) // 2
    assert large_trace_degree**6 > factorial(6) * SECP_P
    assert large_trace_degree**6 < 2**6 * factorial(6) * SECP_P
    assert small_trace_degree**14 > factorial(14) * SECP_P

    return {
        "smooth_component": smooth_component,
        "cofactor": cofactor,
        "small_odd_factor": small_odd,
        "small_trace_degree": small_trace_degree,
        "large_odd_factor": large_odd,
        "large_trace_degree": large_trace_degree,
    }


def main() -> int:
    secp = audit_secp_parameters()
    print(
        "SECP_PARAMETER_AUDIT",
        f"smooth_component={secp['smooth_component']}",
        f"small_H={secp['small_odd_factor']}",
        f"small_D={secp['small_trace_degree']}",
        f"large_H={secp['large_odd_factor']}",
        f"large_D={secp['large_trace_degree']}",
        f"remaining_cofactor={secp['cofactor']}",
    )
    rows = [audit_case(p, order) for p, order in TOY_CASES]
    assert len(rows) >= 5
    assert len({row["p"] for row in rows}) == len(rows)
    for row in rows:
        print(
            "CASE",
            f"p={row['p']}",
            f"H={row['order']}",
            f"roots={row['trace_roots']}",
            f"raw_degree={row['raw_degree']}",
            f"squarefree_degree={row['squarefree_degree']}",
            f"gates={row['fast_nonlinear_gates']}",
            f"j0={row['j0_lifts_0_1_2']}",
            f"control={row['control_lifts_0_1_2']}",
        )
    print(
        "CERT_OK TORUS-PRIME-TRACE-EXACTNESS-GATE-001 "
        f"cases={len(rows)} solver_runs=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
