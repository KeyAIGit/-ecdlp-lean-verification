#!/usr/bin/env python3
"""No-go certificate: the 2-torsion and 5-torsion x-loci of E : y^2 = x^3 + 7 are DISJOINT.

Reasoning (the "hard" part): a common root of Psi2Sq = psi_2^2 = 4x^3 + 28 and psi_5 would be
the x-coordinate of a point that is simultaneously 2-torsion and 5-torsion, forcing its order
to divide gcd(2, 5) = 1 — impossible for a nonzero point. Hence gcd(Psi2Sq, psi_5) = 1 over
the algebraic closure and the resultant is a nonzero constant whose prime support lies in the
bad-reduction primes {2, 3, 7} of y^2 = x^3 + 7.

Machine-checkable consequence (this file, run offline with sympy):
  1. gcd(Psi2Sq, psi_5) = 1                                  (disjoint over Qbar)
  2. Res(Psi2Sq, psi_5) = 2^24 * 3^18 * 7^12                 (exact, nonzero, support {2,3,7})
  3. an explicit Bezout identity u*Psi2Sq + v*psi_5 = Res with u, v in Z[x]
  4. the GF(p) Bezout identity used verbatim by the Lean proof, with sparse cofactors
     supported on exponents = 0 mod 3, collapsing onto X^12,X^9,X^6,X^3,X^0
     -> the five residue equations e12..e0 = 0,0,0,0,1.

Prints CERT_OK iff every check passes.
"""
import sympy as sp

x = sp.symbols('x')

# Psi2Sq = psi_2^2 and psi_5 for y^2 = x^3 + 7 (a = 0, b = 7), univariate in x.
Psi2Sq = 4*x**3 + 28
psi5 = 5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656

p2, p5 = sp.Poly(Psi2Sq, x), sp.Poly(psi5, x)

# 1. disjoint loci
assert sp.gcd(p2, p5).as_expr() == 1, "Psi2Sq, psi5 share a root — loci NOT disjoint"

# 2. exact resultant and its prime support
R = sp.resultant(Psi2Sq, psi5, x)
assert R != 0
assert sp.factorint(R) == {2: 24, 3: 18, 7: 12}, sp.factorint(R)
supp = set(sp.factorint(abs(R)).keys())

# bad-reduction primes of y^2 = x^3 + 7: Delta = -16*(4*0^3 + 27*7^2) = -2^4 * 3^3 * 7^2
Delta = -16 * (4*0**3 + 27*7**2)
bad = set(sp.factorint(abs(Delta)).keys())
assert bad == {2, 3, 7}, bad
assert supp <= bad, (supp, bad)

# 3. explicit Bezout identity u*Psi2Sq + v*psi5 = Res, cofactors in Z[x]
u_q, v_q, _h = sp.gcdex(p2, p5)          # u_q*Psi2Sq + v_q*psi5 = _h = 1 over Q
u = sp.Poly((u_q * R).as_expr(), x, domain='QQ')
v = sp.Poly((v_q * R).as_expr(), x, domain='QQ')
assert all(c.is_integer for c in u.all_coeffs()), "u not integral"
assert all(c.is_integer for c in v.all_coeffs()), "v not integral"
assert sp.expand((u.as_expr()*Psi2Sq + v.as_expr()*psi5) - R) == 0, "Bezout identity fails"

# 4. field Bezout used verbatim by the Lean proof: u*Psi2Sq + v*psi5 = 1 over GF(p), with
#    SPARSE cofactors (both inputs live on exponents = 0 mod 3, so u is supported on
#    X^9,X^6,X^3,X^0 and v is the constant V0); the product collapses onto
#    X^12,X^9,X^6,X^3,X^0 -> five residue equations e12..e0 = 0,0,0,0,1.
p = 115792089237316195423570985008687907853269984665640564039457584007908834671663
U9 = 99142778494795567484546243715572291300534481701196779994490370184439965604459
U6 = 59310642212701184203405681774582306662379778255696243390989127279915174764288
U3 = 69446565655999351689642756084092762405069646257957980847129963197823042378350
U0 = 90429242334511927848674557712301290372769783732852059149176628780622904835439
V0 = 82794702136406219605362384039705237954150393170939365659648321463520396056761
uF = U9*x**9 + U6*x**6 + U3*x**3 + U0
vF = V0
prodF = sp.Poly(sp.expand(uF*Psi2Sq + vF*psi5), x)
assert all((c % p) == (1 if e == (0,) else 0) for e, c in prodF.terms()), "GF(p) Bezout != 1"
assert (4*U9 + 5*V0) % p == 0                               # e12
assert (28*U9 + 4*U6 + 2660*V0) % p == 0                    # e9
assert (28*U6 + 4*U3 - 11760*V0) % p == 0                   # e6
assert (28*U3 + 4*U0 - 548800*V0) % p == 0                  # e3
assert (28*U0 - 614656*V0) % p == 1                         # e0

# cross-check the cofactors are the canonical extended-Euclid output over GF(p)
F2 = sp.Poly(Psi2Sq, x, domain=sp.GF(p))
F5 = sp.Poly(psi5, x, domain=sp.GF(p))
uG, vG, hG = F2.gcdex(F5)
assert hG.as_expr() == 1
assert {e[0]: int(c) % p for e, c in uG.terms()} == {9: U9, 6: U6, 3: U3, 0: U0}
assert {e[0]: int(c) % p for e, c in vG.terms()} == {0: V0}

print("Res(Psi2Sq, psi5) =", sp.factorint(R))
print("resultant prime support", supp, "subset of bad-reduction primes {2, 3, 7}")
print("CERT_OK")
