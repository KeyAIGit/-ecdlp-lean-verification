#!/usr/bin/env python3
"""No-go certificate: the 5-torsion and 7-torsion x-loci of E : y^2 = x^3 + 7 are DISJOINT.

Reasoning (short, the "hard" part): if a point P of order 5 and a point Q of order 7 shared an
x-coordinate then Q = ±P, forcing order(Q) = order(P); but 5 != 7, contradiction. Hence the
division polynomials psi_5 and psi_7 (whose roots are exactly the x-coordinates of the nonzero
5- and 7-torsion) share no root over the algebraic closure, so gcd(psi_5, psi_7) = 1 and their
resultant is a nonzero constant.

Machine-checkable consequence (this file, run offline with sympy):
  1. gcd(psi_5, psi_7) = 1                                   (disjoint over Qbar)
  2. Res(psi_5, psi_7) = 2^192 * 3^144 * 7^96                (exact, nonzero)
  3. an explicit Bezout identity u*psi_5 + v*psi_7 = Res with u, v in Z[x]
The prime support of the resultant is exactly {2, 3, 7} = the primes of bad reduction of
y^2 = x^3 + 7 (discriminant Delta = -2^4 * 3^3 * 7^2): the ONLY primes p modulo which the
5- and 7-torsion x-coordinates can collide. Everywhere else the loci stay disjoint on reduction.

Prints CERT_OK iff every check passes.
"""
import sympy as sp

x = sp.symbols('x')

# Division polynomials for y^2 = x^3 + 7 (a = 0, b = 7), as polynomials in x (odd n).
psi5 = 5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656
psi7 = (7*x**24 + 27608*x**21 - 2101904*x**18 - 284585728*x**15 - 2228742656*x**12
        - 26142548992*x**9 - 330576748544*x**6 - 661153497088*x**3 + 377801998336)

p5, p7 = sp.Poly(psi5, x), sp.Poly(psi7, x)

# 1. disjoint loci
assert sp.gcd(p5, p7).as_expr() == 1, "psi5, psi7 share a root — loci NOT disjoint"

# 2. exact resultant and its prime support
R = sp.resultant(psi5, psi7, x)
assert R != 0
assert sp.factorint(R) == {2: 192, 3: 144, 7: 96}, sp.factorint(R)

# 3. explicit Bezout identity u*psi5 + v*psi7 = Res, cofactors in Z[x]
#    (over Q via extended gcd, then cleared to the integer resultant)
u_q, v_q, _h = sp.gcdex(p5, p7)          # u_q*psi5 + v_q*psi7 = _h = 1 over Q
u = sp.Poly((u_q * R).as_expr(), x, domain='QQ')
v = sp.Poly((v_q * R).as_expr(), x, domain='QQ')
assert all(c.is_integer for c in u.all_coeffs()), "u not integral"
assert all(c.is_integer for c in v.all_coeffs()), "v not integral"
assert sp.expand((u.as_expr()*psi5 + v.as_expr()*psi7) - R) == 0, "Bezout identity fails"

# bad-reduction primes of y^2 = x^3 + 7: Delta = -16*(4*0^3 + 27*7^2) = -2^4 * 3^3 * 7^2
Delta = -16 * (4*0**3 + 27*7**2)
assert set(sp.factorint(abs(Delta)).keys()) == {2, 3, 7} == set(sp.factorint(R).keys())

print("Res(psi5, psi7) =", sp.factorint(R))
print("bad-reduction primes match resultant support: {2, 3, 7}")
print("CERT_OK")
