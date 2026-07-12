#!/usr/bin/env python3
"""Ward normalized elliptic divisibility sequences (EDS) for `HYP_WARD_EDS_001`.

Given a point ``P = (x, y)`` on ``E : y^2 = x^3 + a x + b`` over ``F_p`` (this experiment's
toy family has ``a = 0``, ``E_b : y^2 = x^3 + b``), the *normalized* EDS ``W_n = W_n(P)`` is the
value of the ``n``-th division polynomial ``psi_n(P)``. This module computes ``W_n mod p`` two
mutually reinforcing ways and exposes the torsion / rank-of-apparition structure that ``run.py``
measures and ``validate.py`` independently re-checks against real ``ec_mul``.

Closed forms (over any commutative ring; here reduced mod p), with ``W_0 = 0``, ``W_1 = 1``:

    W_2 = 2 y
    W_3 = 3 x^4 + 6 a x^2 + 12 b x - a^2
    W_4 = 4 y (x^6 + 5 a x^4 + 20 b x^3 - 5 a^2 x^2 - 4 a b x - 8 b^2 - a^3)

Extension to all ``n`` uses the two doubling specializations of Ward's master recurrence
``W_{m+n} W_{m-n} W_1^2 = W_{m+1} W_{m-1} W_n^2 - W_{n+1} W_{n-1} W_m^2`` (with ``W_1 = 1``):

    odd:   W_{2k+1} = W_{k+2} W_k^3        - W_{k-1} W_{k+1}^3            (division-free)
    even:  W_{2k}   = W_k (W_{k+2} W_{k-1}^2 - W_{k-2} W_{k+1}^2) / W_2

The even step divides by ``W_2 = 2y``; in a prime-order subgroup every non-identity point has
odd order, so ``y != 0`` and ``W_2`` is invertible mod p (the code guards the 2-torsion case).

Correctness here is not assumed: the self-test triangulates the recurrence output against
(1) the closed forms for ``W_0..W_4``, (2) Ward's *full* master recurrence at random ``(m, n)``
(an identity NOT used to generate the sequence — the generator only uses the ``n=1`` odd step and
the ``m=k+1, n=k-1`` even step, so checking general ``(m, n)`` is a genuine cross-check), and
(3) the ``n=2`` Somos-4 slice proved in ``Ecdlp/Proved/NormEDSSomos4.lean``. The decisive
end-to-end check — ``W_n ≡ 0 (mod p) ⟺ [n]P = O`` — is done in ``run.py``/``validate.py`` against
independent ``ec_mul``.

This module MEASURES known structure. It makes no claim of any ECDLP advantage; EDS re-encode
point arithmetic and give no known prime-field DLP handle (see RESULTS.md).
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

# Reuse P0 EC arithmetic verbatim (no reimplementation of the group law).
_P0 = Path(__file__).resolve().parent.parent / "p0_glv_semaev"
if str(_P0) not in sys.path:
    sys.path.insert(0, str(_P0))

from toy_curves import ec_add, ec_mul  # noqa: E402  (independent EC oracle)


# ------------------------------------------------------------------ closed forms

def eds_closed_forms(x: int, y: int, a: int, b: int, p: int) -> list[int]:
    """Return ``[W_0, W_1, W_2, W_3, W_4] mod p`` from the closed forms above."""
    W0 = 0
    W1 = 1
    W2 = (2 * y) % p
    W3 = (3 * x ** 4 + 6 * a * x * x + 12 * b * x - a * a) % p
    W4 = (4 * y * (x ** 6 + 5 * a * x ** 4 + 20 * b * x ** 3
                   - 5 * a * a * x * x - 4 * a * b * x - 8 * b * b - a ** 3)) % p
    return [W0, W1, W2, W3, W4]


# ------------------------------------------------------------------ sequence mod p

def eds_sequence(x: int, y: int, a: int, b: int, p: int, N: int) -> list[int]:
    """``[W_0, ..., W_N] mod p`` via closed forms (n<=4) then the doubling recurrence.

    Raises ``ValueError`` if ``W_2 = 2y ≡ 0 (mod p)`` (a 2-torsion / y=0 point), where the
    even doubling step is undefined. Non-identity points of odd order never hit this.
    """
    if N < 0:
        raise ValueError("N must be >= 0")
    base = eds_closed_forms(x, y, a, b, p)
    W = base + [0] * max(0, N - 4)
    W = W[:max(N + 1, 5)]
    W2 = base[2]
    if W2 % p == 0:
        raise ValueError("W_2 = 2y ≡ 0 mod p: even doubling step undefined (2-torsion / y=0)")
    inv2 = pow(W2, -1, p)
    for n in range(5, N + 1):
        k = n >> 1
        if n & 1:
            wk = W[k]
            wk1 = W[k + 1]
            W[n] = (W[k + 2] * (wk * wk % p * wk % p)
                    - W[k - 1] * (wk1 * wk1 % p * wk1 % p)) % p
        else:
            wk1 = W[k + 1]
            wkm1 = W[k - 1]
            inner = (W[k + 2] * (wkm1 * wkm1 % p) - W[k - 2] * (wk1 * wk1 % p)) % p
            W[n] = (W[k] * inner % p * inv2) % p
    return W[:N + 1]


def rank_of_apparition(x: int, y: int, a: int, b: int, p: int, n_max: int) -> int | None:
    """Least ``n > 0`` with ``W_n ≡ 0 (mod p)``, or ``None`` if none in ``[1, n_max]``.

    This is the EDS-side prediction of ``ord(P)``; ``run.py`` confirms it with ``ec_mul``.
    """
    W = eds_sequence(x, y, a, b, p, n_max)
    for n in range(1, n_max + 1):
        if W[n] % p == 0:
            return n
    return None


def zero_set(W: list[int], p: int) -> list[int]:
    """Indices ``n`` in ``[1, len(W)-1]`` with ``W_n ≡ 0 (mod p)``."""
    return [n for n in range(1, len(W)) if W[n] % p == 0]


def eds_term(x: int, y: int, a: int, b: int, p: int, n: int) -> int:
    """A single ``W_n mod p`` in ``O(log n)`` via memoized doubling (no full sequence).

    Uses the same odd/even doubling formulas as ``eds_sequence`` but recurses on ``n/2``,
    so a large index (e.g. ``n = ord(P)``) is reachable without materializing ``[W_0..W_n]``.
    The self-test checks this equals ``eds_sequence`` termwise.
    """
    W2 = (2 * y) % p
    if W2 == 0:
        raise ValueError("W_2 = 2y ≡ 0 mod p: even doubling step undefined (2-torsion / y=0)")
    inv2 = pow(W2, -1, p)
    base = eds_closed_forms(x, y, a, b, p)
    cache: dict[int, int] = {i: base[i] for i in range(5)}

    def w(m: int) -> int:
        if m < 0:
            # normalized EDS is odd: W_{-m} = -W_m
            return (-w(-m)) % p
        if m in cache:
            return cache[m]
        k = m >> 1
        if m & 1:
            wk = w(k)
            wk1 = w(k + 1)
            val = (w(k + 2) * (wk * wk % p * wk % p)
                   - w(k - 1) * (wk1 * wk1 % p * wk1 % p)) % p
        else:
            wk1 = w(k + 1)
            wkm1 = w(k - 1)
            inner = (w(k + 2) * (wkm1 * wkm1 % p) - w(k - 2) * (wk1 * wk1 % p)) % p
            val = (w(k) * inner % p * inv2) % p
        cache[m] = val
        return val

    return w(n)


# ------------------------------------------------------------------ integer EDS (growth demo)

def eds_sequence_Z(x: int, y: int, a: int, b: int, N: int) -> list[int]:
    """``[W_0, ..., W_N]`` over the integers (no reduction) for an INTEGER point on E over Q.

    Requires ``(x, y)`` to be an integer point of ``E : y^2 = x^3 + a x + b``. The EDS
    divisibility property ``W_2 | W_{2k}`` then makes the even step an EXACT integer division;
    the code asserts this. Used only for a tiny ``|W_n|`` growth illustration over Z.
    """
    assert y * y == x ** 3 + a * x + b, "not an integer point on E"
    W = [0, 1,
         2 * y,
         3 * x ** 4 + 6 * a * x * x + 12 * b * x - a * a,
         4 * y * (x ** 6 + 5 * a * x ** 4 + 20 * b * x ** 3
                  - 5 * a * a * x * x - 4 * a * b * x - 8 * b * b - a ** 3)]
    W = W[:max(N + 1, 5)] + [0] * max(0, N - 4)
    W2 = W[2]
    for n in range(5, N + 1):
        k = n >> 1
        if n & 1:
            W[n] = W[k + 2] * W[k] ** 3 - W[k - 1] * W[k + 1] ** 3
        else:
            num = W[k] * (W[k + 2] * W[k - 1] ** 2 - W[k - 2] * W[k + 1] ** 2)
            assert num % W2 == 0, "EDS divisibility W_2 | W_{2k} failed over Z"
            W[n] = num // W2
    return W[:N + 1]


# ------------------------------------------------------------------ cross-checks (self-test only)

def ward_master_holds(W: list[int], p: int, m: int, n: int) -> bool:
    """Check Ward's master recurrence at a single ``(m, n)`` (all indices within range)."""
    lhs = W[m + n] * W[m - n] * (W[1] * W[1] % p) % p
    rhs = (W[m + 1] * W[m - 1] % p * (W[n] * W[n] % p)
           - W[n + 1] * W[n - 1] % p * (W[m] * W[m] % p)) % p
    return lhs == rhs


def somos4_slice_holds(W: list[int], p: int, m: int, b_curve: int, y: int) -> bool:
    """Check the ``n=2`` Somos-4 slice (cf. NormEDSSomos4.lean) at index ``m``.

    In normalized-EDS form: ``W_{m+2} W_{m-2} = W_2^2 W_{m+1} W_{m-1} - W_3 W_m^2`` (W_1=1).
    """
    W2sq = W[2] * W[2] % p
    lhs = W[m + 2] * W[m - 2] % p
    rhs = (W2sq * (W[m + 1] * W[m - 1] % p) - W[3] * (W[m] * W[m] % p)) % p
    return lhs == rhs


def _selftest() -> None:
    C = _find(16)
    x, y = C.gen
    a, b, p = 0, C.b, C.p

    # (1) closed forms consistency: sequence[0..4] == closed forms.
    N = 300
    W = eds_sequence(x, y, a, b, p, N)
    assert W[:5] == eds_closed_forms(x, y, a, b, p), "sequence disagrees with closed forms"

    # (2) Ward master recurrence at many random (m, n) — genuine cross-check.
    rng = random.Random(20240712)
    checks = 0
    for _ in range(2000):
        m = rng.randrange(1, N - 1)
        n = rng.randrange(1, m + 1)
        if m + n <= N and m - n >= 1 and n + 1 <= N and n - 1 >= 0 and m + 1 <= N:
            assert ward_master_holds(W, p, m, n), f"Ward master recurrence failed at m={m}, n={n}"
            checks += 1
    assert checks > 500

    # (3) Somos-4 (n=2) slice.
    for m in range(2, N - 2):
        assert somos4_slice_holds(W, p, m, b, y), f"Somos-4 slice failed at m={m}"

    # (4) torsion property spot-check against ec_mul: W_n≡0 ⟺ [n]P=O.
    for n in range(1, N + 1):
        eds_zero = (W[n] % p == 0)
        ec_zero = (ec_mul(n, C.gen, 0, p) is None)
        assert eds_zero == ec_zero, f"torsion mismatch at n={n}: eds={eds_zero} ec={ec_zero}"

    # (4b) O(log n) single-term eds_term must match the full sequence everywhere in [0, N],
    #      and must reproduce the large apparition index W_ell ≡ 0 (== ord(G)) directly.
    for n in range(0, N + 1):
        assert eds_term(x, y, a, b, p, n) == W[n], f"eds_term != eds_sequence at n={n}"
    assert eds_term(x, y, a, b, p, C.ell) % p == 0, "eds_term(ell) should vanish (apparition)"
    assert eds_term(x, y, a, b, p, C.ell - 1) % p != 0, "eds_term(ell-1) should not vanish"

    # (5a) integer EDS over Q for an INFINITE-order point P=(3,5) on y^2 = x^3 - 2:
    #      |W_n| grows doubly-exponentially, no zeros (apparition = infinity).
    WZ = eds_sequence_Z(3, 5, 0, -2, 10)
    assert WZ[:5] == [0, 1, 10, 171, -7660]
    assert all(w != 0 for w in WZ[1:]), "infinite-order point should have no EDS zeros"
    assert abs(WZ[10]) > abs(WZ[6]) > abs(WZ[3])  # magnitude grows fast
    Wmodp = eds_sequence(3, 5, 0, -2, p, 10)
    assert [w % p for w in WZ] == Wmodp, "Z-EDS reduced mod p disagrees with mod-p EDS"

    # (5b) integer EDS for the TORSION point P=(2,3) on y^2 = x^3 + 1 (order 6 over Q):
    #      apparition over Z is 6 — the same W_n≡0 ⟺ [n]P=O law, now with the zero exact.
    WT = eds_sequence_Z(2, 3, 0, 1, 12)
    assert WT[:5] == [0, 1, 6, 72, 2592]
    assert WT[6] == 0 and WT[12] == 0 and all(WT[n] != 0 for n in range(1, 6))

    print(f"eds self-test OK: {checks} Ward-master checks, Somos-4 slice + torsion spot-check "
          f"(N={N}) on 16-bit curve p={p}, b={b}; integer growth |W_10|={abs(WZ[10])} "
          f"(digits={len(str(abs(WZ[10])))}), torsion point apparition_Z=6")


def _find(bits: int):
    from toy_curves import find_toy_curve
    return find_toy_curve(bits, seed=1, require_cofactor_one=True)


if __name__ == "__main__":
    _selftest()
