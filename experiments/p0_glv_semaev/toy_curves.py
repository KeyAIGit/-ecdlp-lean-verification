#!/usr/bin/env python3
"""Toy `j = 0` curve family for HYP_GLV_SEMAEV_001.

Generates curves `E_b : y^2 = x^3 + b` over primes `p = 1 (mod 3)` with a large prime subgroup,
a generator of that subgroup, and the GLV data (a primitive cube root `beta` of unity mod p, so
`phi(x, y) = (beta*x, y)` is the order-3 automorphism whose orbits the experiment symmetrizes).

Point counting uses the `j = 0` CM structure (discriminant -3): if `p = a^2 + 3 b^2` (solvable
exactly for `p = 1 mod 3`), the six sextic-twist traces are `{+-2a, +-(a+3b), +-(a-3b)}`, all
satisfying `4p - t^2 = 3 s^2`. The actual order of a *specific* `E_b` is the unique one of the six
candidates that annihilates sampled points — fast and correct, no Schoof needed at toy sizes.

Deterministic given (bits, seed): no Math.random-style nondeterminism, so runs are reproducible.

Self-test:  python3 experiments/p0_glv_semaev/toy_curves.py
"""
from __future__ import annotations

import random
from dataclasses import dataclass

import sympy
from math import isqrt


def cornacchia3(p: int):
    """Solve x^2 + 3 y^2 = p (Cornacchia's algorithm). Returns (x, y) or None.

    Solvable iff p = 1 (mod 3) (for prime p > 3). sympy has no `cornacchia` in this version,
    so it is implemented directly: reduce sqrt(-3) mod p by the Euclidean descent until the
    remainder drops below sqrt(p), then read off x and check (p - x^2)/3 is a perfect square.
    """
    if p == 3:
        return (0, 1)
    r = sympy.sqrt_mod((-3) % p, p)
    if r is None:
        return None
    r = int(r)
    if r < p // 2:
        r = p - r
    a, b = p, r
    lim = isqrt(p)
    while b > lim:
        a, b = b, a % b
    rem = p - b * b
    if rem % 3 != 0:
        return None
    y2 = rem // 3
    y = isqrt(y2)
    if y * y != y2:
        return None
    return (b, y)


# ------------------------------------------------------------------ EC arithmetic over F_p

def ec_add(P, Q, a, p):
    """Affine addition on y^2 = x^3 + a*x + b over F_p. Point at infinity is None."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        m = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(k, P, a, p):
    """Scalar multiple k*P by double-and-add."""
    if k < 0:
        if P is None:
            return None
        x, y = P
        return ec_mul(-k, (x, (-y) % p), a, p)
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R


# ------------------------------------------------------------------ curve family

@dataclass
class ToyCurve:
    p: int                # field prime, p = 1 mod 3
    b: int                # curve: y^2 = x^3 + b   (a-coeff is 0 for j=0)
    order: int            # #E(F_p)
    ell: int              # large prime subgroup order
    cofactor: int         # order = cofactor * ell
    gen: tuple            # a generator of the order-ell subgroup
    beta: int             # primitive cube root of unity mod p (GLV: phi(x,y)=(beta*x,y))
    lam: int              # matching eigenvalue: phi(gen) = [lam]gen in the ell-subgroup
    bits: int

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - x * x * x - self.b) % self.p == 0

    def phi(self, P):
        """The GLV automorphism phi(x,y) = (beta*x, y)."""
        if P is None:
            return None
        x, y = P
        return ((self.beta * x) % self.p, y)


def next_prime_1mod3(n: int) -> int:
    q = sympy.nextprime(n - 1)
    while q % 3 != 1:
        q = sympy.nextprime(q)
    return q


def candidate_orders(p: int) -> list[int]:
    """The six possible #E for a j=0 curve over p, from p = a^2 + 3 b^2 (D = -3 CM)."""
    sol = cornacchia3(p)
    if sol is None:
        raise ValueError(f"{p} not represented by x^2+3y^2 (need p = 1 mod 3)")
    a, b = sol
    traces = {2 * a, -2 * a, a + 3 * b, -(a + 3 * b), a - 3 * b, -(a - 3 * b)}
    return sorted(p + 1 - t for t in traces)


def exact_curve_order(p: int, b: int) -> int:
    """Count ``#E_b(F_p)`` exactly by a Legendre-symbol sum.

    This is deliberately O(p), so it is an independent oracle only for small test
    fields.  It is used to audit the much faster CM candidate discriminator, never
    in scaling measurements.
    """
    total = 1  # point at infinity
    for x in range(p):
        rhs = (x * x * x + b) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            total += 2
    return total


def curve_order(p: int, b: int, rng: random.Random, max_samples: int = 64) -> int:
    """Discriminate the exact ``#E_b`` from the six CM candidates.

    Every sampled point eliminates candidates that do not annihilate it.  The
    function returns only after exactly one candidate survives.  Ambiguity is a
    hard error: silently taking the first survivor would corrupt every downstream
    subgroup and relation claim.
    """
    survivors = candidate_orders(p)
    samples = 0
    attempts = 0
    # Always consume at least four on-curve samples to preserve the deterministic
    # sequence used by legacy manifests; continue beyond four only if ambiguity remains.
    while (samples < 4 or len(survivors) > 1) and samples < max_samples and attempts < 20 * max_samples:
        attempts += 1
        x = rng.randrange(p)
        rhs = (x * x * x + b) % p
        y = sympy.sqrt_mod(rhs, p)
        if y is not None:
            P = (x, int(y))
            samples += 1
            survivors = [N for N in survivors if ec_mul(N, P, 0, p) is None]
    if len(survivors) != 1:
        raise RuntimeError(
            f"CM order discrimination ambiguous for p={p}, b={b}: "
            f"{len(survivors)} survivors after {samples} points: {survivors}"
        )
    return survivors[0]


def cube_root_of_unity(p: int, rng: random.Random) -> int:
    """A primitive cube root of unity mod p (p = 1 mod 3)."""
    e = (p - 1) // 3
    while True:
        g = rng.randrange(2, p)
        beta = pow(g, e, p)
        if beta != 1 and pow(beta, 3, p) == 1:
            return beta


def glv_lambda_candidates(ell: int) -> tuple[int, ...]:
    """Roots of ``X^2 + X + 1`` modulo the prime subgroup order ``ell``."""
    if ell == 3:
        return (1,)
    roots = sympy.sqrt_mod((-3) % ell, ell, all_roots=True)
    if not roots:
        return ()
    inv2 = pow(2, -1, ell)
    values = {
        ((-1 + int(root)) * inv2) % ell
        for root in roots
    }
    return tuple(sorted(lam for lam in values if (lam * lam + lam + 1) % ell == 0))


def matching_glv_lambda(p: int, ell: int, G, beta: int) -> int:
    """Choose the root ``lam`` satisfying ``phi(G) = [lam]G`` exactly."""
    phi_G = ((beta * G[0]) % p, G[1])
    matches = [lam for lam in glv_lambda_candidates(ell) if ec_mul(lam, G, 0, p) == phi_G]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one GLV eigenvalue match for ell={ell}, got {matches}"
        )
    return matches[0]


def find_toy_curve(
    bits: int,
    seed: int = 0,
    min_ell: int | None = None,
    *,
    require_cofactor_one: bool = False,
    max_prime_tries: int = 64,
) -> ToyCurve:
    """A j=0 curve at ~`bits` whose best sextic twist has a large prime subgroup.

    Scans `b` over the six twist classes, keeps the twist whose largest prime factor `ell`
    (the DLP subgroup order) is biggest, and requires `ell >= min_ell` (default ~sqrt(p), so
    the subgroup is a meaningful DLP instance). No fixed cofactor-fraction — j=0 orders always
    carry small factors, so demanding a near-prime full order needlessly rejects good curves.
    """
    rng = random.Random((seed << 16) ^ bits)
    p = next_prime_1mod3(1 << bits)
    best_seen = None
    for _prime_try in range(max_prime_tries):
        threshold = min_ell if min_ell is not None else isqrt(p)
        best = None  # (ell, b, order)
        seen_orders: set[int] = set()
        for b in range(1, 120):
            order = curve_order(p, b, rng)
            if order in seen_orders:
                continue
            seen_orders.add(order)
            factors = sympy.factorint(order)
            eligible = [int(q) for q, e in factors.items() if e == 1]
            if not eligible:
                continue
            ell = max(eligible)
            cofactor = order // ell
            if require_cofactor_one and cofactor != 1:
                if len(seen_orders) >= 6:
                    break
                continue
            if best is None or ell > best[0]:
                best = (ell, b, order)
            if best_seen is None or ell > best_seen[0]:
                best_seen = (ell, p, b, order)
            if len(seen_orders) >= 6:  # all sextic-twist orders seen
                break
        if best is not None and best[0] >= threshold:
            ell, b, order = best
            cof = order // ell
            for _ in range(400):
                x = rng.randrange(p)
                rhs = (x * x * x + b) % p
                y = sympy.sqrt_mod(rhs, p)
                if y is None:
                    continue
                G = ec_mul(cof, (x, int(y)), 0, p)
                if G is None or ec_mul(ell, G, 0, p) is not None:
                    continue
                beta = cube_root_of_unity(p, rng)
                lam = matching_glv_lambda(p, int(ell), G, beta)
                return ToyCurve(p, b, order, int(ell), int(cof), G, beta, lam, bits)
            raise RuntimeError(f"found order at {bits} bits but no generator of the ell-subgroup")
        p = next_prime_1mod3(p + 1)
    raise RuntimeError(
        f"no suitable curve at {bits} bits after {max_prime_tries} field primes; "
        f"best={best_seen}, require_cofactor_one={require_cofactor_one}"
    )


def _selftest() -> None:
    for bits in (16, 20, 24):
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        assert C.on_curve(C.gen)
        assert ec_mul(C.ell, C.gen, 0, C.p) is None, "gen order != ell"
        assert C.cofactor * C.ell == C.order
        assert C.cofactor == 1, "index-calculus toy family must stay in <G>"
        assert C.order % (C.ell * C.ell) != 0, "ell-primary subgroup must be cyclic"
        assert pow(C.beta, 3, C.p) == 1 and C.beta != 1
        assert (C.lam * C.lam + C.lam + 1) % C.ell == 0
        pG = C.phi(C.gen)
        assert C.on_curve(pG)
        assert ec_mul(C.lam, C.gen, 0, C.p) == pG, "phi(G) != [lambda]G"
        if bits <= 20:
            assert exact_curve_order(C.p, C.b) == C.order, "CM order != exact oracle"
        print(f"[{bits:2d}b] p={C.p} b={C.b} #E={C.order} ell={C.ell} "
              f"cof={C.cofactor} beta^3=1 lambda={C.lam} phi(G)=[lambda]G OK")
    print("toy_curves self-test OK")


if __name__ == "__main__":
    _selftest()
