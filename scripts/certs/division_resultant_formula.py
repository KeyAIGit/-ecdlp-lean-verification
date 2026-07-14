#!/usr/bin/env python3
"""Independent exact checks for secp256k1 division-polynomial resultants.

This script does not read Lean source or generated Lean output.  It rebuilds the
univariate auxiliary division polynomials over ZZ from their defining recurrence,
computes exact resultants for the requested small pairs and fresh pairs involving
index 11, and checks

    Res(prePsi_m, prePsi_n) = Delta^((m^2 - 1)(n^2 - 1) / 24)

for the selected coprime odd indices.  It also checks that every prime divisor of
each resultant belongs to the bad-reduction set {2, 3, 7}.

The x^3 sparsity of the j = 0 model is used only as an exact resultant identity:
Res(F(x^3), G(x^3)) = Res(F(t), G(t))^3.  All reconstruction identities are
asserted symbolically before that compression is used.
"""

from __future__ import annotations

import sympy as sp


x, t = sp.symbols("x t")
ZZ = sp.ZZ
DELTA = -21168
BAD_PRIMES = {2, 3, 7}


def poly(expr: sp.Expr) -> sp.Poly:
    """Normalize an expression as an exact polynomial in x over ZZ."""

    return sp.Poly(sp.expand(expr), x, domain=ZZ)


def build_prepsi(limit: int) -> dict[int, sp.Poly]:
    """Build Mathlib's prePsi' recurrence for y^2 = x^3 + 7 over ZZ."""

    psi2sq = poly(4 * x**3 + 28)
    q: dict[int, sp.Poly] = {
        0: poly(0),
        1: poly(1),
        2: poly(1),
        3: poly(3 * x**4 + 84 * x),
        4: poly(2 * x**6 + 280 * x**3 - 784),
    }

    for n in range(5, limit + 1):
        if n % 2 == 1:
            m = (n - 5) // 2
            left_extra = psi2sq**2 if m % 2 == 0 else poly(1)
            right_extra = poly(1) if m % 2 == 0 else psi2sq**2
            q[n] = poly(
                q[m + 4].as_expr()
                * q[m + 2].as_expr() ** 3
                * left_extra.as_expr()
                - q[m + 1].as_expr()
                * q[m + 3].as_expr() ** 3
                * right_extra.as_expr()
            )
        else:
            m = n // 2 - 3
            q[n] = poly(
                q[m + 2].as_expr() ** 2
                * q[m + 3].as_expr()
                * q[m + 5].as_expr()
                - q[m + 1].as_expr()
                * q[m + 3].as_expr()
                * q[m + 4].as_expr() ** 2
            )

    return q


def x3_compression(f: sp.Poly) -> tuple[int, sp.Poly]:
    """Return a and F with f(x) = x^a F(x^3), checking the identity exactly."""

    nonzero_terms = [(monomial[0], coeff) for monomial, coeff in f.terms() if coeff]
    assert nonzero_terms
    valuation = min(exponent for exponent, _ in nonzero_terms)
    compressed_terms: list[tuple[int, int]] = []
    for exponent, coeff in nonzero_terms:
        shifted = exponent - valuation
        assert shifted % 3 == 0
        compressed_terms.append((shifted // 3, int(coeff)))

    compressed = sp.Poly(
        sum(coeff * t**exponent for exponent, coeff in compressed_terms),
        t,
        domain=ZZ,
    )
    reconstructed = x**valuation * compressed.as_expr().subs(t, x**3)
    assert sp.expand(f.as_expr() - reconstructed) == 0
    return valuation, compressed


def sparse_resultant(f: sp.Poly, g: sp.Poly) -> int:
    """Compute Res_x(f, g) from exact x^3-compressed resultants."""

    a, compressed_f = x3_compression(f)
    b, compressed_g = x3_compression(g)
    assert a == 0 or b == 0

    result = int(sp.resultant(compressed_f, compressed_g, t)) ** 3
    if a:
        result *= int(g.eval(0)) ** a
    if b:
        result *= ((-1) ** (f.degree() * b)) * int(f.eval(0)) ** b
    return result


def exponent(m: int, n: int) -> int:
    numerator = (m * m - 1) * (n * n - 1)
    assert numerator % 24 == 0
    return numerator // 24


def main() -> None:
    q = build_prepsi(11)

    # Anchor the recurrence against the already independently known small forms.
    assert q[5] == poly(
        5 * x**12
        + 2660 * x**9
        - 11760 * x**6
        - 548800 * x**3
        - 614656
    )
    assert q[7] == poly(
        7 * x**24
        + 27608 * x**21
        - 2101904 * x**18
        - 284585728 * x**15
        - 2228742656 * x**12
        - 26142548992 * x**9
        - 330576748544 * x**6
        - 661153497088 * x**3
        + 377801998336
    )

    checked_pairs = ((3, 5), (3, 7), (5, 7), (3, 11), (5, 11), (7, 11))
    for m, n in checked_pairs:
        assert sp.gcd(m, n) == 1
        result = sparse_resultant(q[m], q[n])
        e = exponent(m, n)
        expected = DELTA**e
        assert result == expected

        prime_support = set(sp.factorint(abs(result)))
        assert prime_support <= BAD_PRIMES
        print(
            f"PAIR_OK m={m} n={n} exponent={e} "
            f"prime_support={sorted(prime_support)} digits={len(str(abs(result)))}"
        )

    print("CERT_OK")


if __name__ == "__main__":
    main()
