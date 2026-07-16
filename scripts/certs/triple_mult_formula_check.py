#!/usr/bin/env python3
"""Design-insurance check for Ecdlp/Proved/TripleMultiplicationFormula.lean.

Symbolically verifies (over Q[x, y, l2, l3]) every `linear_combination` certificate
used in the N7@3 point-level multiplication formula x(3P) = Phi_3(x)/PsiSq_3(x):

  hId:     (l2^2-3x)*(4y^2) + (3x^4+84x)                      == (2yl2+3x^2)*g1 - 12x*g3
  hBF:     X3*(l2^2-3x)^2 - [(A+2y)^2 - (l2^2-x)(l2^2-3x)^2]  == (d*l3 - (A+2y))*g2
  hIdsq:   (l2^2-3x)^2*16y^4 - (3x^4+84x)^2                   == (d*4y^2 - Psi3)*hId_diff
  hmaster: M*64y^6 - N*(4x^3+28)                              == c1*g1 + c3*g3
  hkey:    the full chain assembling X3*D*4y^2 = N*4y^2
  2-torsion branch: x*D - N == (2x^6+280x^3-784)*(4x^3+28 - 0)

plus a numeric mod-p spot check of the final formula on a toy curve point.
Nothing from this script enters Lean — the kernel re-checks everything.
Prints CERT_OK on success.
"""

import sympy as sp

x, y, l2, l3 = sp.symbols('x y l2 l3')

d = l2**2 - 3 * x
A = l2 * d
X3 = l3**2 - (l2**2 - 2 * x) - x
N = x**9 - 672 * x**6 + 2352 * x**3 + 21952
D = 9 * x**8 + 504 * x**5 + 7056 * x**2
Psi3 = 3 * x**4 + 84 * x
M = (A + 2 * y)**2 - (l2**2 - x) * d**2

# hypothesis diffs (lhs - rhs), Lean conventions
g1 = l2 * (2 * y) - 3 * x**2                      # hl2 : l2*(2*y) = 3*x^2
g3 = y**2 - (x**3 + 7)                            # hcurve : y^2 = x^3+7
g2 = d * l3 - (-(A + y) - y)                      # hl3


def zero(e, name):
    assert sp.expand(e) == 0, f"{name} FAILED"
    print(f"{name}: OK")


# D = Psi3^2 (pure ring)
zero(D - Psi3**2, "hden (D = Psi3^2)")

# hId
hId_diff = d * (4 * y**2) + Psi3
zero(hId_diff - ((l2 * (2 * y) + 3 * x**2) * g1 - 12 * x * g3), "hId")

# hBF
hBF_diff = X3 * d**2 - M
zero(hBF_diff - (d * l3 - (A + 2 * y)) * g2, "hBF")

# hIdsq  (uses hId as the hypothesis)
hIdsq_diff = d**2 * (16 * y**4) - Psi3**2
zero(hIdsq_diff - (d * (4 * y**2) - Psi3) * hId_diff, "hIdsq")

# hmaster
c1 = (32 * l2**3 * x * y**5 + 48 * l2**2 * x**3 * y**4 + 128 * l2**2 * y**6
      + 72 * l2 * x**5 * y**3 + 108 * x**7 * y**2 - 384 * x * y**6)
c3 = (4 * x**9 - 320 * x**6 * y**2 - 2688 * x**6 - 320 * x**3 * y**4
      - 448 * x**3 * y**2 + 9408 * x**3 + 256 * y**6 + 1792 * y**4
      + 12544 * y**2 + 87808)
hmaster_diff = M * (64 * y**6) - N * (4 * x**3 + 28)
zero(hmaster_diff - (c1 * g1 + c3 * g3), "hmaster")

# hkey: X3*D*4y^2 - N*4y^2 ==
#   (-(X3)*(4y^2))*hIdsq_diff + (64y^6)*hBF_diff + hmaster_diff + (-4N)*g3
hkey_diff = X3 * D * (4 * y**2) - N * (4 * y**2)
zero(hkey_diff - ((-(X3) * (4 * y**2)) * hIdsq_diff + (64 * y**6) * hBF_diff
                  + hmaster_diff + (-4 * N) * g3), "hkey")

# 2-torsion branch: goal x*D = N given hPsi2z : 4x^3+28 = 0
zero((x * D - N) - (2 * x**6 + 280 * x**3 - 784) * (4 * x**3 + 28), "two-torsion branch")

# numeric spot check of the final formula on a toy j=0 curve (y^2 = x^3 + 7 mod p)
p = 10007
found = 0
for xv in range(2, p):
    rhs = (xv**3 + 7) % p
    yv = pow(rhs, (p + 1) // 4, p)
    if p % 4 == 3 and yv * yv % p == rhs and yv != 0:
        # tangent slope, double, chord, triple — generic-position guards
        l2v = 3 * xv * xv * pow(2 * yv, p - 2, p) % p
        X2 = (l2v * l2v - 2 * xv) % p
        Y2 = (-(l2v * (X2 - xv) + yv)) % p
        if (X2 - xv) % p == 0:
            continue
        l3v = (Y2 - yv) * pow(X2 - xv, p - 2, p) % p
        X3v = (l3v * l3v - X2 - xv) % p
        Nv = (xv**9 - 672 * xv**6 + 2352 * xv**3 + 21952) % p
        Dv = (9 * xv**8 + 504 * xv**5 + 7056 * xv**2) % p
        if Dv == 0:
            continue
        assert X3v == Nv * pow(Dv, p - 2, p) % p, f"numeric FAIL at x={xv}"
        found += 1
        if found >= 25:
            break
assert found >= 25
print(f"numeric x(3P) = Phi3/PsiSq3 spot check: OK ({found} points)")

print("CERT_OK")
