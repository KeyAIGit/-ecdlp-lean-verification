#!/usr/bin/env python3
"""Convention certificate for `Ecdlp/Proved/DivisionPolynomialEvalBridge.lean`.

The bridge identities L2a/L2b connect Mathlib's division polynomials `ΨSq`/`Φ`
(evaluated at a point `x₀`) to the scalar EDS `normEDS`. They hold *structurally*
from Mathlib's twist conventions — no property of the `preNormEDS` recurrence is
used — so this script verifies exactly that twist algebra symbolically, treating
the `preNormEDS(β⁴,..)` values at `n-1, n, n+1` and `β, x₀` as free symbols.

Mathlib conventions being certified (pinned rev, DivisionPolynomial/Basic.lean and
NumberTheory/EllipticDivisibilitySequence.lean):

    preΨ n          := preNormEDS (Ψ₂Sq ^ 2) Ψ₃ preΨ₄ n
    ΨSq n           := preΨ n ^ 2 * (Ψ₂Sq if Even n else 1)
    Φ n             := X * ΨSq n - preΨ (n+1) * preΨ (n-1) * (1 if Even n else Ψ₂Sq)
    normEDS b c d n := preNormEDS (b ^ 4) c d n * (b if Even n else 1)

With `β² = Ψ₂Sq.eval x₀`, `w k := normEDS β (Ψ₃.eval x₀) (preΨ₄.eval x₀) k`, and
`P k := preNormEDS (β⁴) .. k`, the claims are

    L2a  (ΨSq n).eval x₀ = w n ^ 2
    L2b  (Φ  n).eval x₀ = x₀ * w n ^ 2 - w (n+1) * w (n-1)

Nothing from this script enters Lean; it is transcription insurance for the
even/odd twist placement. Prints CERT_OK on success, exits 1 otherwise.
"""
from __future__ import annotations

import sys

import sympy as sp


def check() -> bool:
    x0, beta = sp.symbols("x0 beta")
    Pm, Pn, Pp = sp.symbols("P_nm1 P_n P_np1")  # preNormEDS(β⁴,..) at n-1, n, n+1
    b2sq = beta**2                               # Ψ₂Sq(x₀) = β²

    def twist(p, even):                          # normEDS twist: * β if even else 1
        return p * beta if even else p

    ok = True
    for even_n in (True, False):                 # n even?  n±1 have opposite parity
        even_np1 = even_nm1 = not even_n
        wn = twist(Pn, even_n)
        wnp1 = twist(Pp, even_np1)
        wnm1 = twist(Pm, even_nm1)
        psi_sq_eval = Pn**2 * (b2sq if even_n else 1)
        phi_eval = x0 * psi_sq_eval - Pp * Pm * (1 if even_n else b2sq)
        d_a = sp.simplify(psi_sq_eval - wn**2)
        d_b = sp.simplify(phi_eval - (x0 * wn**2 - wnp1 * wnm1))
        print(f"n {'even' if even_n else 'odd '}:  L2a diff = {d_a}   L2b diff = {d_b}")
        ok = ok and d_a == 0 and d_b == 0
    return ok


if __name__ == "__main__":
    if check():
        print("CERT_OK")
        sys.exit(0)
    print("CERT_FAIL")
    sys.exit(1)
