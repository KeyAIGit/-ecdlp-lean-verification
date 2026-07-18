#!/usr/bin/env python3
"""Design-insurance check for Ecdlp/Proved/QuintupleMultiplicationFormula.lean.

Symbolically verifies (over Q[x, y, s2, s3, s5]) every `linear_combination`
certificate used in the N7@5 point-level multiplication formula
x(5P) = Phi_5(x)/PsiSq_5(x) for secp256k1 (y^2 = x^3 + 7):

  ground truth: Phi_5, PsiSq_5, prePsi_6 recomputed from the EDS recurrence
                from scratch (psi_1..psi_6 for A = 0, B = 7), cross-checked
                against the repo's prePsi_5 and Mathlib's prePsi'_even shape,
                deg Phi_5 = 25 and monic, and numerically against explicit
                elliptic-curve arithmetic on >= 25 points mod 10007;
  hId:      (d)*(4y^2) + Psi3                        == (2ys2+3x^2)*g1 - 12x*gc
  hIdsq:    d^2*16y^4 - Psi3^2                       == (d*4y^2 - Psi3)*hId
  hs3D:     D53*d^2 - D1                             == (d*s3 + A)*g3
  hpsi5:    D1*64y^6 + prePsi5                       == c1*g1 + cc*gc
  hquint:   D53*d^2*64y^6 + prePsi5                  == 64y^6*hs3D + hpsi5
  hquintsq: D53^2*d^4*4096y^12 - prePsi5^2           == (..)*hquint
  hBF5:     X5*D53^2 - F                             == (D53*s5 + Ydiff)*g5
  hs3Y:     Ydiff*d^3 - Y1                           == cY*g3
  hs3E:     (s3^2-x)*d^2 - E1                        == (d*s3 + A)*g3
  hs3F:     F*d^6 - G                                == chain of hs3Y/hs3E/hs3D
  hmaster:  G*(2y)^16 - Phi5*Psi3^2                  == qM1*g1 + qMc*gc
  hkey:     the full chain assembling X5*PsiSq5*Z = Phi5*Z, Z = d^2*(2y)^16
  2-torsion branch:  x*PsiSq5 - Phi5      == Tcoef*(4x^3+28)
  3-torsion branch:  (x^4-56x)*PsiSq5 - Phi5*(4x^3+28) == Ucoef*(3x^4+84x)
  small branch facts: hd2ne / hPsi2z combinations

plus a numeric mod-p spot check of the final formula on a toy curve.
Nothing from this script enters Lean — the kernel re-checks everything.
Prints the Lean-formatted cofactors (mechanical transcription) and CERT_OK.
"""

import sympy as sp

x, y, s2, s3, s5 = sp.symbols('x y s2 s3 s5')

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
        if rem != 0:
            # num came out y-free: replace one factor (x^3+7) by y^2 first
            h, r2 = sp.div(num, x**3 + 7, x)
            assert r2 == 0, f"psi_{n} not divisible by psi_2"
            val = sp.expand(y*h/2)
    psi[n] = yred(val)
    return psi[n]


psi3 = get_psi(3)
assert psi3 == 3*x**4 + 84*x
pre4 = sp.expand(sp.div(yred(get_psi(4)), 2*y, y)[0])
assert pre4 == 2*x**6 + 280*x**3 - 784
pre5 = yred(get_psi(5))
assert sp.expand(
    pre5 - (5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656)) == 0, \
    "prePsi5 mismatch vs secp256k1_psi5_evalEval"
print("prePsi5 matches secp256k1_psi5_evalEval: OK")

pre6 = sp.expand(sp.div(yred(get_psi(6)), 2*y, y)[0])
assert sp.degree(pre6, y) == 0
# Mathlib preΨ'_even at m = 0: preΨ'6 = Ψ₃·preΨ'5 − Ψ₃·preΨ₄²
assert sp.expand(pre6 - psi3*(pre5 - pre4**2)) == 0, "prePsi6 recurrence mismatch"
print("prePsi6 = Psi3*(prePsi5 - prePsi4^2): OK")

# Mathlib Φ_ofNat at n = 4 (even): Φ 5 = X·preΨ'5² − preΨ'6·preΨ₄·Ψ₂Sq
Phi5 = sp.expand(x*pre5**2 - pre6*pre4*(4*x**3 + 28))
PsiSq5 = sp.expand(pre5**2)
P5 = sp.Poly(Phi5, x)
assert P5.degree() == 25 and P5.LC() == 1
print("Phi5 monic of degree 25: OK")

# ------------------------------------------------------------------ numeric check
p = 10007


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
    Q = None
    for _ in range(5):
        Q = ec_add(Q, (xv, yv))
    if Q is None:
        continue
    Nv = int(Phi5.subs(x, xv)) % p
    Dv = int(PsiSq5.subs(x, xv)) % p
    if Dv == 0:
        continue
    assert Q[0] == Nv * pow(Dv, p-2, p) % p, f"numeric FAIL at x={xv}"
    found += 1
    if found >= 25:
        break
assert found >= 25
print(f"numeric x(5P) = Phi5/PsiSq5 spot check: OK ({found} points)")

# ------------------------------------------------------------------ certificates
# Lean-statement building blocks (spelled exactly as in the Lean file)
d = s2**2 - 3*x                                    # x(2P) - x, cleared
Ae = -(s2*d + y) - y                               # rhs of hl3 (= d*s3)
D53 = s3**2 - 2*s2**2 + 3*x                        # X3 - X2, cleared
Yd = -(s3*D53) + 2*(s2*d + y)                      # Y3 - Y2, cleared
X5v = s5**2 - (s3**2 - s2**2 + x) - (s2**2 - 2*x)  # chord x(5P)
Sd = s2*d + 2*y                                    # = -Ae
Y1 = Sd**3 - (2*s2**2 - 3*x)*(d**2*Sd) + 2*((s2*d + y)*d**3)
D1 = Ae**2 - (2*(s2**2 - 2*x) + x)*d**2
E1 = Sd**2 - x*d**2
F = Yd**2 - ((s3**2 - s2**2 + x) + (s2**2 - 2*x))*D53**2
G = Y1**2 - E1*D1**2

# hypothesis diffs (lhs - rhs), Lean conventions
g1 = s2*(2*y) - 3*x**2                             # hl2 : s2*(2*y) = 3*x^2
gc = y**2 - (x**3 + 7)                             # hcurve : y^2 = x^3+7
g3 = d*s3 - Ae                                     # hl3
g5 = D53*s5 - Yd                                   # hl5


def zero(e, name):
    assert sp.expand(e) == 0, f"{name} FAILED"
    print(f"{name}: OK")


def nmon(e):
    return len(sp.Add.make_args(sp.expand(e)))


def lean(e):
    """print a sympy polynomial in ready-to-paste Lean syntax"""
    s = str(sp.expand(e))
    s = s.replace('**', '@')
    s = s.replace('*', ' * ').replace('@', ' ^ ')
    return s


# hden : PsiSq5 = prePsi5^2 (pure ring, used for hdenne)
zero(PsiSq5 - pre5**2, "hden (PsiSq5 = prePsi5^2)")

# hId
hId_diff = d*(4*y**2) + psi3
zero(hId_diff - ((s2*(2*y) + 3*x**2)*g1 - 12*x*gc), "hId")

# hIdsq
hIdsq_diff = d**2*(16*y**4) - psi3**2
zero(hIdsq_diff - (d*(4*y**2) - psi3)*hId_diff, "hIdsq")

# hs3D : D53*d^2 = D1
hs3D_diff = D53*d**2 - D1
zero(hs3D_diff - (d*s3 + Ae)*g3, "hs3D")

# hpsi5 : D1*(64y^6) = -prePsi5  (five_core cofactors, re-verified)
c1 = (-32*s2**5*y**5 - 48*s2**4*x**2*y**4 - 72*s2**3*x**4*y**3
      + 288*s2**3*x*y**5 - 108*s2**2*x**6*y**2 + 432*s2**2*x**3*y**4
      + 128*s2**2*y**6 - 162*s2*x**8*y + 648*s2*x**5*y**3
      - 672*s2*x**2*y**5 - 243*x**10 + 972*x**7*y**2 - 1008*x**4*y**4
      - 384*x*y**6)
cc = (724*x**9 - 2192*x**6*y**2 - 7728*x**6 + 832*x**3*y**4
      + 7616*x**3*y**2 + 65856*x**3 + 256*y**6 + 1792*y**4 + 12544*y**2
      + 87808)
hpsi5_diff = D1*(64*y**6) + pre5
zero(hpsi5_diff - (c1*g1 + cc*gc), "hpsi5")

# hquint : D53*(d^2*64y^6) = -prePsi5
hquint_diff = D53*(d**2*(64*y**6)) + pre5
zero(hquint_diff - ((64*y**6)*hs3D_diff + hpsi5_diff), "hquint")

# hquintsq : D53^2*(d^4*4096y^12) = prePsi5^2
hquintsq_diff = D53**2*(d**4*(4096*y**12)) - pre5**2
zero(hquintsq_diff - (D53*(d**2*(64*y**6)) - pre5)*hquint_diff, "hquintsq")

# hBF5 : X5*D53^2 = F (eliminates s5)
hBF5_diff = X5v*D53**2 - F
zero(hBF5_diff - (D53*s5 + Yd)*g5, "hBF5")

# hs3Y : Ydiff*d^3 = Y1 (eliminates s3 from the chord-Y difference)
hs3Y_diff = Yd*d**3 - Y1
cY = (2*s2**2 - 3*x)*d**2 - ((d*s3)**2 + Ae*(d*s3) + Ae**2)
zero(hs3Y_diff - cY*g3, "hs3Y")

# hs3E : (s3^2-x)*d^2 = E1
hs3E_diff = (s3**2 - x)*d**2 - E1
zero(hs3E_diff - (d*s3 + Ae)*g3, "hs3E")

# hs3F : F*d^6 = G (assembles the three bricks; certificate is a
# linear_combination of the three PROVEN equalities, not raw g3)
hs3F_diff = F*d**6 - G
zero(hs3F_diff - ((Yd*d**3 + Y1)*hs3Y_diff
                  - D53**2*d**4*hs3E_diff
                  - E1*(D53*d**2 + D1)*hs3D_diff), "hs3F")

# hmaster : G*(2y)^16 = Phi5*Psi3^2 — cofactors from cofactor-tracked
# pseudo-division (recomputed here, embedded below for transcription)
Gx = sp.expand(G)
assert sp.degree(Gx, s2) == 16 and sp.degree(Gx, s3) == 0
qM1, rM1 = sp.div(sp.expand((2*y)**16 * Gx), g1, s2)
qMc, rMc = sp.div(sp.expand(rM1), gc, y)
zero(sp.expand((2*y)**16*Gx) - (sp.expand(qM1)*g1 + sp.expand(qMc)*gc
                                + sp.expand(rMc)), "hmaster decomposition")
hmaster_diff = G*(2*y)**16 - Phi5*psi3**2
zero(sp.expand(rMc) - sp.expand(Phi5*psi3**2), "hmaster remainder = Phi5*Psi3^2")
zero(hmaster_diff - (sp.expand(qM1)*g1 + sp.expand(qMc)*gc), "hmaster")

# hkey : (X5*PsiSq5)*Z = Phi5*Z with Z = d^2*(2y)^16
Z = d**2*(2*y)**16
hkey_diff = (X5v*PsiSq5)*Z - Phi5*Z
zero(hkey_diff - ((-X5v*(d**2*(2*y)**16))*hquintsq_diff
                  + (268435456*y**28*d**6)*hBF5_diff
                  + (268435456*y**28)*hs3F_diff
                  + (4096*y**12)*hmaster_diff
                  + (-(4096*y**12)*Phi5)*hIdsq_diff), "hkey")

# ------------------------------------------------------------------ branches
# 2-torsion branch (y = 0, 5P = P): goal x*PsiSq5 = Phi5 given 4x^3+28 = 0
Tcoef, rT = sp.div(sp.expand(x*PsiSq5 - Phi5), 4*x**3 + 28, x)
assert rT == 0
zero(sp.expand(x*PsiSq5 - Phi5) - Tcoef*(4*x**3 + 28), "two-torsion branch")
# 3-torsion branch (3P = 0, 5P = 2P): goal (x^4-56x)*PsiSq5 = Phi5*(4x^3+28)
# given 3x^4+84x = 0
Ucoef, rU = sp.div(sp.expand((x**4 - 56*x)*PsiSq5 - Phi5*(4*x**3 + 28)),
                   3*x**4 + 84*x, x)
assert rU == 0
zero(sp.expand((x**4 - 56*x)*PsiSq5 - Phi5*(4*x**3 + 28))
     - Ucoef*(3*x**4 + 84*x), "three-torsion branch")
# hd2ne combination in the 3-torsion branch: (2y)*(2y) = 0 from hcurve + hcz
zero((2*y)*(2*y) - 0 - (4*gc + (4*x**3 + 28 - 0)), "hd2ne combination")
# hPsi2z in the 2-torsion branch: 4x^3+28 = 0 from y=0 in hcurve
zero((4*x**3 + 28 - 0) - (-4)*(0 - (x**3 + 7)), "hPsi2z combination")

# ------------------------------------------------------------------ report
print()
print("== monomial counts per linear_combination certificate ==")
print(f"hId: coeffs {nmon(s2*(2*y) + 3*x**2)} + {nmon(12*x)}")
print(f"hIdsq: coeff {nmon(d*(4*y**2) - psi3)}")
print(f"hs3D/hs3E: coeff {nmon(d*s3 + Ae)}")
print(f"hpsi5: coeffs {nmon(c1)} + {nmon(cc)}")
print(f"hquint: coeffs 1 + 1")
print(f"hquintsq: coeff {nmon(D53*(d**2*(64*y**6)) - pre5)}")
print(f"hBF5: coeff {nmon(D53*s5 + Yd)}")
print(f"hs3Y: coeff {nmon(cY)}")
print(f"hs3F: coeffs {nmon(Yd*d**3 + Y1)} + {nmon(D53**2*d**4)} + "
      f"{nmon(E1*(D53*d**2 + D1))} (factored in Lean source)")
print(f"hmaster: coeffs {nmon(qM1)} + {nmon(qMc)}  <-- largest")
print(f"hkey: coeffs {nmon(X5v*(d**2*(2*y)**16))} + {nmon(268435456*y**28*d**6)}"
      f" + 1 + 1 + {nmon(4096*y**12*Phi5)}")
print(f"2-torsion: coeff {nmon(Tcoef)};  3-torsion: coeff {nmon(Ucoef)}")
print(f"stated polynomials: G {nmon(G)}, F {nmon(F)}, Phi5 {nmon(Phi5)}, "
      f"PsiSq5 {nmon(PsiSq5)}, prePsi6 {nmon(pre6)}")

print()
print("== Lean-formatted constants ==")
print("prePsi6 (for secp256k1_preΨ₆, in X):")
print(" ", lean(pre6).replace('x', 'X'))
print("Phi5 (for Φ₅_eval):")
print(" ", lean(Phi5))
print("PsiSq5 (for ΨSq₅_eval):")
print(" ", lean(PsiSq5))
print("hmaster cofactor of hl2 (qM1):")
print(" ", lean(qM1))
print("hmaster cofactor of hcurve (qMc):")
print(" ", lean(qMc))
print("2-torsion cofactor of hΨ2z (Tcoef):")
print(" ", lean(Tcoef))
print("3-torsion cofactor of h34 (Ucoef):")
print(" ", lean(Ucoef))

print()
print("CERT_OK")
