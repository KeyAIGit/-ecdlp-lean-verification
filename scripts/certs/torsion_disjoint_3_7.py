#!/usr/bin/env python3
"""No-go certificate: the 3-torsion and 7-torsion x-loci of E : y^2 = x^3 + 7 are DISJOINT.

Reasoning (the "hard" part): if a point P of order 3 and a point Q of order 7 shared an
x-coordinate then Q = ±P, forcing order(Q) = order(P); but 3 != 7, contradiction. Hence the
division polynomials psi_3 and psi_7 (whose roots are exactly the x-coordinates of the nonzero
3- and 7-torsion) share no root over the algebraic closure, so gcd(psi_3, psi_7) = 1 and their
resultant is a nonzero constant whose prime support lies in the bad-reduction primes {2, 3, 7}.

Machine-checkable consequence (this file, run offline with sympy):
  1. gcd(psi_3, psi_7) = 1                                   (disjoint over Qbar)
  2. Res(psi_3, psi_7) = 2^64 * 3^48 * 7^32                  (exact, nonzero, support {2,3,7})
  3. an explicit Bezout identity u*psi_3 + v*psi_7 = Res with u, v in Z[x]
  4. the GF(p) Bezout identity used verbatim by the Lean proof, with SPARSE cofactors
     (u on exponents = 2 mod 3, v on exponents = 0 mod 3), collapsing onto the ten powers
     X^27,X^24,...,X^3,X^0 -> the ten residue equations e27..e0 = 0,...,0,1.

Prints CERT_OK iff every check passes.
"""
import sympy as sp

x = sp.symbols('x')

# Division polynomials for y^2 = x^3 + 7 (a = 0, b = 7), as univariate polynomials in x.
psi3 = 3*x**4 + 84*x
psi7 = (7*x**24 + 27608*x**21 - 2101904*x**18 - 284585728*x**15 - 2228742656*x**12
        - 26142548992*x**9 - 330576748544*x**6 - 661153497088*x**3 + 377801998336)

p3, p7 = sp.Poly(psi3, x), sp.Poly(psi7, x)

# 1. disjoint loci
assert sp.gcd(p3, p7).as_expr() == 1, "psi3, psi7 share a root — loci NOT disjoint"

# 2. exact resultant and its prime support
R = sp.resultant(psi3, psi7, x)
assert R != 0
assert sp.factorint(R) == {2: 64, 3: 48, 7: 32}, sp.factorint(R)
supp = set(sp.factorint(abs(R)).keys())

# bad-reduction primes of y^2 = x^3 + 7: Delta = -16*(4*0^3 + 27*7^2) = -2^4 * 3^3 * 7^2
Delta = -16 * (4*0**3 + 27*7**2)
bad = set(sp.factorint(abs(Delta)).keys())
assert bad == {2, 3, 7}, bad
assert supp <= bad, (supp, bad)

# 3. explicit Bezout identity u*psi3 + v*psi7 = Res, cofactors in Z[x]
u_q, v_q, _h = sp.gcdex(p3, p7)          # u_q*psi3 + v_q*psi7 = _h = 1 over Q
u = sp.Poly((u_q * R).as_expr(), x, domain='QQ')
v = sp.Poly((v_q * R).as_expr(), x, domain='QQ')
assert all(c.is_integer for c in u.all_coeffs()), "u not integral"
assert all(c.is_integer for c in v.all_coeffs()), "v not integral"
assert sp.expand((u.as_expr()*psi3 + v.as_expr()*psi7) - R) == 0, "Bezout identity fails"

# 4. field Bezout used verbatim by the Lean proof: u*psi3 + v*psi7 = 1 over GF(p).
#    psi3 lives on exponents = 1 mod 3 and psi7 on exponents = 0 mod 3, so the cofactors are
#    sparse (u on = 2 mod 3: X^23,X^20,...,X^2; v on = 0 mod 3: X^3,X^0) and the product
#    collapses onto X^27,X^24,...,X^0 -> the ten residue equations e27..e0 = 0,...,0,1.
p = 115792089237316195423570985008687907853269984665640564039457584007908834671663
U23 = 68944590336790336836930321036541054571108089578262445502128972569398365568457
U20 = 63845044986596127917238406587884911877349497474344308019160463221897999565952
U17 = 22253398887951985727697958014689324670722641885893013284809964241804939424547
U14 = 101374513400142574387640111079567503864672689695122863264029523801075956397009
U11 = 3391696775842707751069407080766688069554051883385740844231428252699398029752
U8  = 101664364752688042620528964726208266071132221721823193954668754045372792705489
U5  = 106134497956017148058902191656989031970877659139882974899542335172254439863475
U2  = 75607205217650409999754433938468414630184630497968841867273699652761192112281
V3  = 3535772494894482905193000986821807427602242942356255938932607186803224662565
V0  = 104312091503547336002174865974034599278343573453365127323364127481039549803657
uF = (U23*x**23 + U20*x**20 + U17*x**17 + U14*x**14 + U11*x**11 + U8*x**8
      + U5*x**5 + U2*x**2)
vF = V3*x**3 + V0
prodF = sp.Poly(sp.expand(uF*psi3 + vF*psi7), x)
assert all((c % p) == (1 if e == (0,) else 0) for e, c in prodF.terms()), "GF(p) Bezout != 1"
assert (3*U23 + 7*V3) % p == 0                                          # e27
assert (84*U23 + 3*U20 + 27608*V3 + 7*V0) % p == 0                      # e24
assert (84*U20 + 3*U17 - 2101904*V3 + 27608*V0) % p == 0                # e21
assert (84*U17 + 3*U14 - 284585728*V3 - 2101904*V0) % p == 0            # e18
assert (84*U14 + 3*U11 - 2228742656*V3 - 284585728*V0) % p == 0         # e15
assert (84*U11 + 3*U8 - 26142548992*V3 - 2228742656*V0) % p == 0        # e12
assert (84*U8 + 3*U5 - 330576748544*V3 - 26142548992*V0) % p == 0       # e9
assert (84*U5 + 3*U2 - 661153497088*V3 - 330576748544*V0) % p == 0      # e6
assert (84*U2 + 377801998336*V3 - 661153497088*V0) % p == 0             # e3
assert (377801998336*V0) % p == 1                                       # e0

# cross-check the cofactors are the canonical extended-Euclid output over GF(p)
F3 = sp.Poly(psi3, x, domain=sp.GF(p))
F7 = sp.Poly(psi7, x, domain=sp.GF(p))
uG, vG, hG = F3.gcdex(F7)
assert hG.as_expr() == 1
assert {e[0]: int(c) % p for e, c in uG.terms()} == {
    23: U23, 20: U20, 17: U17, 14: U14, 11: U11, 8: U8, 5: U5, 2: U2}
assert {e[0]: int(c) % p for e, c in vG.terms()} == {3: V3, 0: V0}

# 5. univariate 7-division polynomial from the preΨ'_odd(1) route (exposes psi7 in Lean).
#    Mathlib: preΨ'_odd m : preΨ' (2*(m+2)+1) = preΨ' (m+4) * preΨ' (m+2)^3
#      * (if Even m then Ψ₂Sq^2 else 1)
#      - preΨ' (m+1) * preΨ' (m+3)^3 * (if Even m then 1 else Ψ₂Sq^2).
#    At m = 1 (Even 1 is False, both ifs take the else branch):
#      preΨ' 7 = preΨ' 5 * preΨ' 3^3 * 1 - preΨ' 2 * preΨ' 4^3 * Ψ₂Sq^2
#              = preΨ'5 * Ψ₃^3 - preΨ₄^3 * Ψ₂Sq^2   (preΨ' 2 = 1).
pre1 = sp.Integer(1)
pre2 = sp.Integer(1)          # preΨ' 2 = 1 (Mathlib preΨ'_two)
pre3 = psi3
pre4 = 2*x**6 + 280*x**3 - 784
pre5 = 5*x**12 + 2660*x**9 - 11760*x**6 - 548800*x**3 - 614656
Psi2Sq = 4*x**3 + 28
# m = 1 (odd): preΨ' 7 = preΨ' 5 * preΨ' 3^3 * 1 - preΨ' 2 * preΨ' 4^3 * Ψ₂Sq^2
assert sp.expand(pre5*pre3**3 - pre2*pre4**3*Psi2Sq**2 - psi7) == 0, "psi7 explicit form fails"

print("Res(psi3, psi7) =", sp.factorint(R))
print("resultant prime support", supp, "subset of bad-reduction primes {2, 3, 7}")
print("CERT_OK")
