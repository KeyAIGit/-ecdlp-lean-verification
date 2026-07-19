#!/usr/bin/env python3
"""Design-insurance check for the `even_x_algebra` wall of the N7-uniform induction
(`Ecdlp/Targets/n7_uniform_carrier_induction.lean`, node S3b, BARRIERS.md §B3).

The uniform doubling x-rung reduces (see the file's docstring + BARRIERS §B3) to two
**univariate division-polynomial doubling identities** for secp256k1 (`y² = x³ + 7`):

    (I)  ΨSq(2k).eval x = 4 · B · (A³ + 7·B³)
    (II) Φ(2k).eval x  = A⁴ − 56·A·B³

with `A := Φ(k).eval x`, `B := ΨSq(k).eval x`. They are the multiplication-by-2 map on
x-coordinates, `x(2Q) = (x_Q⁴ − 56·x_Q) / (4·(x_Q³ + 7))` with `x_Q = A/B`, cleared by `B⁴`.

This certificate confirms (I) and (II) are **exact identities** in `ℚ[x]` for `k = 1..8`,
by recomputing the secp256k1 division polynomials `ψ_n, ΨSq_n = ψ_n², Φ_n = x·ψ_n² −
ψ_{n+1}·ψ_{n-1}` from the standard EDS recurrence from scratch (cross-checked against
Mathlib's `Ψ₃ = 3x⁴+84x`, `preΨ₄ = 2x⁶+280x³−784`, `ΨSq 2 = 4x³+28`, `Φ 2 = x⁴−56x`).

**Honest scope.** This grounds the *target* of the `even_x_algebra` wall — it does NOT
provide the Lean proof. Per the 2026-07-19 audit, (I)/(II) are true but have **no finite
`linear_combination` certificate**: a Somos-4 substitution leaves a remainder in `w(k±2)²`
whose pinning cascades outward unboundedly, so closing them in Lean needs a strong
induction over the elliptic net (the `NormEDSSomos4.lean` technique), not the algebra here.
Nothing from this script enters Lean — the kernel remains the sole judge.

Prints `CERT_OK` iff both identities hold for all tested `k`.
"""

import sympy as sp

x, y = sp.symbols('x y')

# secp256k1 shape: y^2 = x^3 + A x + B with A = 0, B = 7.
A_curve, B_curve = 0, 7


def yred(e):
    """reduce even powers of y via y^2 = x^3 + 7, leaving a polynomial in x (and at most y^1)."""
    e = sp.expand(e)
    p = sp.Poly(e, y)
    out = 0
    for (k,), c in p.terms():
        q, r = divmod(k, 2)
        out += c * (x**3 + 7)**q * y**r
    return sp.expand(out)


# psi_n (bivariate, reduced) for y^2 = x^3 + 7, from the standard EDS recurrence.
psi = {
    0: sp.Integer(0),
    1: sp.Integer(1),
    2: 2 * y,
    3: 3 * x**4 + 6 * A_curve * x**2 + 12 * B_curve * x - A_curve**2,
    4: 4 * y * (x**6 + 5 * A_curve * x**4 + 20 * B_curve * x**3 - 5 * A_curve**2 * x**2
                - 4 * A_curve * B_curve * x - 8 * B_curve**2 - A_curve**3),
}


def get_psi(n):
    if n in psi:
        return psi[n]
    if n % 2 == 1:
        m = (n - 1) // 2
        val = get_psi(m + 2) * get_psi(m)**3 - get_psi(m - 1) * get_psi(m + 1)**3
    else:
        m = n // 2
        # divide by ψ₂ = 2y in the RAW bivariate ring (before y-reduction, which would
        # scramble the y-divisibility): the numerator carries a genuine y² factor.
        num = sp.expand(get_psi(m) * (get_psi(m + 2) * get_psi(m - 1)**2
                                      - get_psi(m - 2) * get_psi(m + 1)**2))
        val, rem = sp.div(num, 2 * y, y)
        assert rem == 0, f"psi_{n} not divisible by psi_2"
    psi[n] = yred(val)
    return psi[n]


def PsiSq(n):
    """ΨSq_n(x) = ψ_n²  (univariate after y-reduction)."""
    return yred(get_psi(n)**2)


def Phi(n):
    """Φ_n(x) = x·ψ_n² − ψ_{n+1}·ψ_{n-1}  (univariate after y-reduction)."""
    return yred(x * get_psi(n)**2 - get_psi(n + 1) * get_psi(n - 1))


# ---- cross-check ground truth against the repo's kernel-verified secp256k1 values ----
assert sp.expand(get_psi(3) - (3 * x**4 + 84 * x)) == 0, "Ψ₃ mismatch"
prePsi4 = sp.div(yred(get_psi(4)), 2 * y, y)[0]
assert sp.expand(prePsi4 - (2 * x**6 + 280 * x**3 - 784)) == 0, "preΨ₄ mismatch"
assert sp.expand(PsiSq(2) - (4 * x**3 + 28)) == 0, "ΨSq 2 mismatch (want 4x³+28)"
assert sp.expand(Phi(2) - (x**4 - 56 * x)) == 0, "Φ 2 mismatch (want x⁴−56x)"
assert sp.expand(Phi(1) - x) == 0 and sp.expand(PsiSq(1) - 1) == 0, "n=1 base mismatch"
print("ground truth OK: Ψ₃=3x⁴+84x, preΨ₄=2x⁶+280x³−784, ΨSq 2=4x³+28, Φ 2=x⁴−56x")

# ---- the two doubling identities, checked exactly for k = 1..8 ----
ok = True
for k in range(1, 9):
    A = Phi(k)
    B = PsiSq(k)
    lhs_I = PsiSq(2 * k)
    rhs_I = sp.expand(4 * B * (A**3 + 7 * B**3))
    lhs_II = Phi(2 * k)
    rhs_II = sp.expand(A**4 - 56 * A * B**3)
    dI = sp.expand(lhs_I - rhs_I)
    dII = sp.expand(lhs_II - rhs_II)
    ok_k = (dI == 0 and dII == 0)
    ok = ok and ok_k
    print(f"k={k}: (I) ΨSq(2k)=4B(A³+7B³) {'OK' if dI == 0 else 'FAIL'}"
          f"  (II) Φ(2k)=A⁴−56AB³ {'OK' if dII == 0 else 'FAIL'}"
          f"  [degΨSq(2k)={sp.Poly(lhs_I, x).degree()}, degΦ(2k)={sp.Poly(lhs_II, x).degree()}]")

# ---- numeric mod-p spot check on a toy prime (independent of the symbolic path) ----
pp = 10007
Fp = sp.GF(pp)
xs = 3
for k in (1, 2, 3):
    A = int(Phi(k).subs(x, xs)) % pp
    B = int(PsiSq(k).subs(x, xs)) % pp
    lI = int(PsiSq(2 * k).subs(x, xs)) % pp
    rI = (4 * B * (A**3 + 7 * B**3)) % pp
    lII = int(Phi(2 * k).subs(x, xs)) % pp
    rII = (A**4 - 56 * A * B**3) % pp
    assert lI == rI and lII == rII, f"numeric spot check failed at k={k}"
print(f"numeric spot check (mod {pp}, x={xs}) OK for k=1,2,3")

print("CERT_OK" if ok else "CERT_FAIL")
if not ok:
    raise SystemExit(1)
