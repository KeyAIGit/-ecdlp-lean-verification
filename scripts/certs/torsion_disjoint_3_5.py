#!/usr/bin/env python3
"""No-go certificate: the 3-torsion and 5-torsion x-loci of E : y^2 = x^3 + 7 are DISJOINT.

Reasoning (the "hard" part): if a point P of order 3 and a point Q of order 5 shared an
x-coordinate then Q = ±P, forcing order(Q) = order(P); but 3 != 5, contradiction. Hence the
division polynomials psi_3 and psi_5 (whose roots are exactly the x-coordinates of the nonzero
3- and 5-torsion) share no root over the algebraic closure, so gcd(psi_3, psi_5) = 1 and their
resultant is a nonzero constant whose prime support lies in the bad-reduction primes {2,3,7}.

Machine-checkable consequence (this file, run offline with sympy):
  1. gcd(psi_3, psi_5) = 1                                   (disjoint over Qbar)
  2. Res(psi_3, psi_5) is nonzero with prime support {2,3,7} (bad-reduction primes of y^2=x^3+7)
  3. an explicit Bezout identity u*psi_3 + v*psi_5 = Res with u, v in Z[x]

Prints CERT_OK iff every check passes.
"""
import sympy as sp

x = sp.symbols('x')

# Division polynomials for y^2 = x^3 + 7 (a = 0, b = 7), as univariate polynomials in x.
psi3 = 3*x**4 + 84*x
psi5 = 5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656

p3, p5 = sp.Poly(psi3, x), sp.Poly(psi5, x)

# 1. disjoint loci
assert sp.gcd(p3, p5).as_expr() == 1, "psi3, psi5 share a root — loci NOT disjoint"

# 2. exact resultant and its prime support
R = sp.resultant(psi3, psi5, x)
assert R != 0
supp = set(sp.factorint(abs(R)).keys())

# bad-reduction primes of y^2 = x^3 + 7: Delta = -16*(4*0^3 + 27*7^2) = -2^4 * 3^3 * 7^2
Delta = -16 * (4*0**3 + 27*7**2)
bad = set(sp.factorint(abs(Delta)).keys())
assert bad == {2, 3, 7}, bad
assert supp <= bad, (supp, bad)

# 3. explicit Bezout identity u*psi3 + v*psi5 = Res, cofactors in Z[x]
u_q, v_q, _h = sp.gcdex(p3, p5)          # u_q*psi3 + v_q*psi5 = _h = 1 over Q
u = sp.Poly((u_q * R).as_expr(), x, domain='QQ')
v = sp.Poly((v_q * R).as_expr(), x, domain='QQ')
assert all(c.is_integer for c in u.all_coeffs()), "u not integral"
assert all(c.is_integer for c in v.all_coeffs()), "v not integral"
assert sp.expand((u.as_expr()*psi3 + v.as_expr()*psi5) - R) == 0, "Bezout identity fails"

# 4. field Bezout used verbatim by the Lean proof (Ecdlp/Proved/CoprimePsi3Psi5.lean):
#    u*psi3 + v*psi5 = 1 over GF(p), with the SPARSE cofactors whose product collapses onto
#    the powers X^15,X^12,X^9,X^6,X^3,X^0 -> the six residue equations e15..e0 = 0,0,0,0,0,1.
p = 115792089237316195423570985008687907853269984665640564039457584007908834671663
U11 = 31177840712345204383440702675357104180201715313433862087315362139048932203702
U8  = 50833951204485227496364311484852378098102338386479880943844279992526584060117
U5  = 69970874983990339768432868587673310710667172024916395574625392522883749089112
U2  = 43425072435009501839400542569054573740197890917139190071633944342682153936688
V3  = 27610131267519355539363972398260900633186964678195908363393816319734174546444
V0  = 111153103857739796084256904440306667401884537566138730673360705418592607296042
uF = U11*x**11 + U8*x**8 + U5*x**5 + U2*x**2
vF = V3*x**3 + V0
prodF = sp.Poly(sp.expand(uF*psi3 + vF*psi5), x)
assert all((c % p) == (1 if e == (0,) else 0) for e, c in prodF.terms()), "GF(p) Bezout != 1"
assert (3*U11 + 5*V3) % p == 0                              # e15
assert (84*U11 + 3*U8 + 2660*V3 + 5*V0) % p == 0            # e12
assert (84*U8 + 3*U5 - 11760*V3 + 2660*V0) % p == 0        # e9
assert (84*U5 + 3*U2 - 548800*V3 - 11760*V0) % p == 0      # e6
assert (84*U2 - 614656*V3 - 548800*V0) % p == 0            # e3
assert (-614656*V0) % p == 1                                # e0

# 5. univariate 5-division polynomial from the preΨ'_odd(0) route (exposes psi5 in Lean):
#    preΨ' 5 = preΨ₄ · Ψ₂Sq² − Ψ₃³  (no curve relation needed, odd index).
pre4, Psi2Sq = 2*x**6 + 280*x**3 - 784, 4*x**3 + 28
assert sp.expand(pre4*Psi2Sq**2 - psi3**3 - psi5) == 0, "psi5 explicit form fails"

print("Res(psi3, psi5) =", sp.factorint(R))
print("resultant prime support", supp, "subset of bad-reduction primes {2, 3, 7}")
print("CERT_OK")
