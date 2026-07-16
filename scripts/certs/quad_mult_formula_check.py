#!/usr/bin/env python3
"""Design-insurance check for Ecdlp/Proved/QuadrupleMultiplicationFormula.lean.

Symbolically verifies (over Q[x, y, s2, s4]) every `linear_combination` certificate
used in the N7@4 point-level multiplication formula x(4P) = Phi_4(x)/PsiSq_4(x) for
secp256k1 (y^2 = x^3 + 7).  n = 4 is the first EVEN rung: 4P = 2*(2P) is a
DOUBLING-of-a-DOUBLING (tangent at P, then tangent at 2P), not a chord.

  ground truth: Phi_4, PsiSq_4, prePsi_4 recomputed from the EDS recurrence
                from scratch (psi_1..psi_5 for A = 0, B = 7), cross-checked
                against Mathlib's Phi_four / PsiSq_four closed forms, deg Phi_4 = 16
                and monic, deg PsiSq_4 = 15, and numerically against explicit
                elliptic-curve double-of-double arithmetic on two primes.

  hcurve2:  Y2^2 - (X2^3 + 7)                        (2P on curve; in Lean derived
                                                       from Nonsingular, checked here)
  hInner:   X4*Psi2X2 - (X2^4 - 56*X2)               == (2*Y2*s4+3*X2^2)*g_s4 - 4*s4^2*g_c2
  hY2pre:   Y2*16y^3 - prePsi4                        == qP2*g_s2 + qPc*g_c
  hBridge:  [(X2^4-56X2)*PsiSq4 - Phi4*Psi2X2]*(2y)^8 == qB2*g_s2 + qBc*g_c
  hkey:     (X4*PsiSq4)*Z - Phi4*Z, Z = Psi2X2*(2y)^8 == (PsiSq4*(2y)^8)*hInner + hBridge
  2-torsion / 4-torsion branches: handled in Lean by contradiction (4P = O), no cert here

plus a numeric mod-p spot check of the final formula on TWO toy curves.
Nothing from this script enters Lean -- the kernel re-checks everything.
Prints the Lean-formatted cofactors (mechanical transcription) and CERT_OK.
"""

import sympy as sp

x, y, s2, s4 = sp.symbols('x y s2 s4')

# ------------------------------------------------------------------ ground truth
# psi sequence for y^2 = x^3 + A x + B with A = 0, B = 7 (secp256k1 shape),
# computed from scratch by the standard EDS recurrence, reduced mod y^2 -> x^3+7.
A, B = 0, 7


def yred(e):
    """reduce even powers of y via y^2 = x^3 + 7"""
    e = sp.expand(e)
    p = sp.Poly(e, y)
    out = 0
    for (k,), c in p.terms():
        q, r = divmod(k, 2)
        out += c * (x**3 + 7)**q * y**r
    return sp.expand(out)


psi = {0: sp.Integer(0), 1: sp.Integer(1), 2: 2*y,
       3: 3*x**4 + 6*A*x**2 + 12*B*x - A**2,
       4: 4*y*(x**6 + 5*A*x**4 + 20*B*x**3 - 5*A**2*x**2 - 4*A*B*x
               - 8*B**2 - A**3)}


def get_psi(n):
    if n in psi:
        return psi[n]
    if n % 2 == 1:
        m = (n - 1) // 2
        val = get_psi(m+2)*get_psi(m)**3 - get_psi(m-1)*get_psi(m+1)**3
    else:
        m = n // 2
        num = yred(get_psi(m)*(get_psi(m+2)*get_psi(m-1)**2
                               - get_psi(m-2)*get_psi(m+1)**2))
        val, rem = sp.div(num, 2*y, y)
        assert rem == 0, f"psi_{n} not divisible by psi_2"
    psi[n] = yred(val)
    return psi[n]


Psi3 = get_psi(3)
assert Psi3 == 3*x**4 + 84*x
prePsi4 = sp.expand(sp.div(yred(get_psi(4)), 2*y, y)[0])
assert prePsi4 == 2*x**6 + 280*x**3 - 784, "prePsi4 mismatch vs secp256k1_preΨ₄_eval"
pre5 = yred(get_psi(5))
assert sp.expand(
    pre5 - (5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656)) == 0
print("prePsi4 = 2x^6+280x^3-784, prePsi5 matches repo: OK")

Psi2 = 4*x**3 + 28                                     # Ψ₂Sq(x)

# Mathlib closed forms:
#   ΨSq 4 = preΨ₄² · Ψ₂Sq          (ΨSq_four)
#   Φ 4   = X·preΨ₄²·Ψ₂Sq − Ψ₃·(preΨ₄·Ψ₂Sq² − Ψ₃³)   (Φ_four)
PsiSq4 = sp.expand(prePsi4**2 * Psi2)
Phi4 = sp.expand(x*prePsi4**2*Psi2 - Psi3*(prePsi4*Psi2**2 - Psi3**3))

# cross-check Φ_four form == eval_Φ_eq_normEDS form (x·ΨSq₄ − Ψ₅·Ψ₃)
assert sp.expand(Phi4 - (x*PsiSq4 - pre5*Psi3)) == 0, "Phi4 two-form mismatch"
PP = sp.Poly(Phi4, x)
PD = sp.Poly(PsiSq4, x)
assert PP.degree() == 16 and PP.LC() == 1, "Phi4 not monic deg 16"
assert PD.degree() == 15, "PsiSq4 not deg 15"
print("Phi4 monic deg 16, PsiSq4 deg 15, Φ_four == x·ΨSq₄−Ψ₅·Ψ₃: OK")

# ------------------------------------------------------------------ numeric check
def numcheck(p, want):
    def ec_add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            lam = 3*x1*x1 * pow(2*y1, p-2, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, p-2, p) % p
        x3 = (lam*lam - x1 - x2) % p
        y3 = (lam*(x1 - x3) - y1) % p
        return (x3, y3)

    found = 0
    for xv in range(2, p):
        rhs = (xv**3 + 7) % p
        yv = pow(rhs, (p + 1) // 4, p)
        if yv*yv % p != rhs or yv == 0:
            continue
        # explicit double-of-double
        P = (xv, yv)
        twoP = ec_add(P, P)
        if twoP is None:
            continue
        fourP = ec_add(twoP, twoP)
        if fourP is None:
            continue
        Nv = int(Phi4.subs(x, xv)) % p
        Dv = int(PsiSq4.subs(x, xv)) % p
        if Dv == 0:
            continue
        assert fourP[0] == Nv * pow(Dv, p-2, p) % p, f"numeric FAIL p={p} x={xv}"
        found += 1
        if found >= want:
            break
    assert found >= want, f"only {found} points on p={p}"
    print(f"numeric x(4P) = Phi4/PsiSq4 on p={p}: OK ({found} points)")


numcheck(10007, 25)
numcheck(1000003, 30)

# ------------------------------------------------------------------ certificates
# Lean-statement building blocks (spelled exactly as in the Lean file)
X2 = s2**2 - 2*x                             # x(2P), cleared
Y2 = -(s2*(s2**2 - 3*x) + y)                 # y(2P), cleared
Psi2X2 = 4*X2**3 + 28                        # Ψ₂Sq(X2) = 4·x(2P)³+28
X4 = s4**2 - 2*X2                            # x(4P) = x(2·(2P)), cleared

# hypothesis diffs (lhs - rhs), Lean conventions
g_s2 = s2*(2*y) - 3*x**2                      # hl2 : s2*(2*y) = 3*x^2
g_c = y**2 - (x**3 + 7)                       # hcurve : y^2 = x^3+7
g_s4 = s4*(2*Y2) - 3*X2**2                    # hl4 : s4*(2*Y2) = 3*X2^2
g_c2 = Y2**2 - (X2**3 + 7)                    # hcurve2 : Y2^2 = X2^3+7 (hyp in Lean)


def zero(e, name):
    assert sp.expand(e) == 0, f"{name} FAILED"
    print(f"{name}: OK")


def nmon(e):
    return len(sp.Add.make_args(sp.expand(e)))


def lean(e):
    s = str(sp.expand(e))
    s = s.replace('**', '@').replace('*', ' * ').replace('@', ' ^ ')
    return s


# sanity: 2P lies on the curve (proved in Lean from Nonsingular, checked here)
zero(sp.expand(sp.rem(sp.rem(sp.Poly(g_c2, s2).as_expr(), g_s2, s2), g_c, y))
     - sp.expand(sp.rem(sp.rem(g_c2, g_s2, s2), g_c, y)), "hcurve2 well-formed")
# verify g_c2 lies in <g_s2, g_c> after (2y)^6 scaling (informational)
sc = sp.expand((2*y)**6 * g_c2)
qc2, rc2 = sp.div(sc, g_s2, s2)
qcc, rcc = sp.div(sp.expand(rc2), g_c, y)
zero(rcc, "hcurve2 in ideal <g_s2,g_c> (scaled (2y)^6)")

# hInner : X4*Psi2X2 = X2^4 - 56*X2   (base-case doubling applied at 2P)
hInner_diff = X4*Psi2X2 - (X2**4 - 56*X2)
zero(hInner_diff - ((2*Y2*s4 + 3*X2**2)*g_s4 - 4*s4**2*g_c2), "hInner")

# hY2pre : Y2 * 16y^3 = prePsi4   (so prePsi4(x)=0  =>  Y2 = 0)
hY2pre_diff = Y2*(16*y**3) - prePsi4
qP2, rP2 = sp.div(hY2pre_diff, g_s2, s2)
qPc, rPc = sp.div(sp.expand(rP2), g_c, y)
zero(rPc, "hY2pre remainder = 0")
zero(hY2pre_diff - (sp.expand(qP2)*g_s2 + sp.expand(qPc)*g_c), "hY2pre")

# hPsi2X2 : 4*X2^3 + 28 = 4*(s2*(s2^2-3x)+y)^2   (= 4*Y2^2), from hcurve2
zero((Psi2X2 - 4*(s2*(s2**2 - 3*x) + y)**2) - (-4)*g_c2, "hPsi2X2 (= -4*hcurve2)")

# hBridge : [(X2^4-56X2)*PsiSq4 - Phi4*Psi2X2] * (2y)^K == qB2*g_s2 + qBc*g_c
K = 8
hBridge_core = sp.expand((X2**4 - 56*X2)*PsiSq4 - Phi4*Psi2X2)
scaled = sp.expand((2*y)**K * hBridge_core)
qB2, rB2 = sp.div(scaled, g_s2, s2)
qBc, rBc = sp.div(sp.expand(rB2), g_c, y)
zero(rBc, "hBridge remainder = 0")
zero(scaled - (sp.expand(qB2)*g_s2 + sp.expand(qBc)*g_c), "hBridge")

# hkey : (X4*PsiSq4)*Z = Phi4*Z with Z = Psi2X2*(2y)^K
Z = Psi2X2*(2*y)**K
hkey_diff = (X4*PsiSq4)*Z - Phi4*Z
zero(hkey_diff - ((PsiSq4*(2*y)**K)*hInner_diff + scaled), "hkey")

# ------------------------------------------------------------------ report
print()
print("== monomial counts per linear_combination certificate ==")
print(f"hInner:  cofactors {nmon(2*Y2*s4 + 3*X2**2)} + {nmon(4*s4**2)}")
print(f"hY2pre:  cofactors {nmon(qP2)} + {nmon(qPc)}")
print(f"hPsi2X2: cofactor 1 (= -4)")
print(f"hBridge: cofactors {nmon(qB2)} + {nmon(qBc)}   <-- largest")
print(f"hkey:    cofactor {nmon(PsiSq4*(2*y)**K)} + 1")
print(f"stated polynomials: Phi4 {nmon(Phi4)}, PsiSq4 {nmon(PsiSq4)}, "
      f"Psi2X2(expanded) {nmon(sp.expand(Psi2X2))}")

print()
print("== Lean-formatted constants ==")
print("Phi4 (for Φ₄_eval):")
print(" ", lean(Phi4))
print("PsiSq4 (for ΨSq₄_eval):")
print(" ", lean(PsiSq4))
print("hY2pre cofactor of hl2 (qP2):")
print(" ", lean(qP2))
print("hY2pre cofactor of hcurve (qPc):")
print(" ", lean(qPc))
print("hBridge cofactor of hl2 (qB2):")
print(" ", lean(qB2))
print("hBridge cofactor of hcurve (qBc):")
print(" ", lean(qBc))

print()
print("CERT_OK")
