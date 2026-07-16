#!/usr/bin/env python3
"""No-go certificate: the 2-torsion and 7-torsion x-loci of E : y^2 = x^3 + 7 are DISJOINT.

A common root of Psi2Sq = psi_2^2 = 4x^3 + 28 and psi_7 (= Lean's `secp256k1.preΨ' 7`,
degree 24) would be the x-coordinate of a nonzero point whose order divides
gcd(2, 7) = 1 — impossible. Hence gcd(Psi2Sq, psi_7) = 1, certified constructively with
an explicit Bezout identity u*Psi2Sq + v*psi_7 = 1 over GF(p),
p = 2^256 - 2^32 - 977. Both inputs live on exponents = 0 (mod 3), so extended Euclid
stays inside GF(p)[x^3]: u is sparse on X^21,X^18,...,X^3,X^0 (8 constants), v is the
constant V0 (1 constant), and the Bezout product collapses onto the nine powers
X^24,X^21,...,X^3,X^0 — nine residue equations, the nine-power sibling of the
five-power CoprimePsi2Psi5 (mirrors scripts/certs/torsion_disjoint_2_5.py and the
emission pipeline of scripts/certs/psi_squarefree_certs.py).

Pipeline (all checks must pass before anything is emitted):
  (a) build psi_7 independently from the division-polynomial recurrence over Q
      (reducing y^2 -> x^3 + 7) and match the CI-verified concrete form of
      `secp256k1.preΨ' 7` (Ecdlp/Proved/CoprimePsi3Psi7.lean); build Psi2Sq = psi_2^2
      reduced on the curve and match 4x^3 + 28;
  (b) extended Euclid over GF(p) (pure-integer coefficient lists, inverses via
      pow(a, p-2, p)) to get u, v; verify u*Psi2Sq + v*psi_7 == 1 by direct polynomial
      multiplication mod p; verify sparsity (u on exponents = 0 mod 3, v constant);
      verify gcd(Psi2Sq, psi_7) = 1 over Q (sympy);
  (c) closure/numeric insurance for the real p: psi_7 squarefree mod p
      (gcd(psi_7, psi_7') constant) and gcd(psi_7, x^3 + 7) = 1 mod p — the exact
      facts the E[7] structure count consumes (24 distinct roots, y != 0 at each);
  (d) emit Ecdlp/Proved/CoprimePsi2Psi7.lean in full (constants, residue equations,
      collapsing key identity) — zero hand transcription.

Prints CERT_OK iff every check passes.
"""
import os
import sympy as sp

x, y = sp.symbols('x y')

p = 2**256 - 2**32 - 977
assert p == 115792089237316195423570985008687907853269984665640564039457584007908834671663


# ---------------------------------------------------------------------------
# (a) division polynomials for y^2 = x^3 + 7 from the recurrence, over Q
# ---------------------------------------------------------------------------
def reduce_y(e):
    """Reduce an expression in Z[x, y] modulo y^2 - (x^3 + 7) (replace y^2 repeatedly)."""
    e = sp.expand(e)
    while sp.degree(sp.Poly(e, y), y) >= 2:
        e = sp.expand(e.subs(y**2, x**3 + 7))
    return e


a_inv, b_inv = 0, 7  # curve invariants a, b of y^2 = x^3 + a x + b
psi = {
    0: sp.Integer(0),
    1: sp.Integer(1),
    2: 2 * y,
    3: 3 * x**4 + 6 * a_inv * x**2 + 12 * b_inv * x - a_inv**2,
    4: 4 * y * (x**6 + 5 * a_inv * x**4 + 20 * b_inv * x**3 - 5 * a_inv**2 * x**2
                - 4 * a_inv * b_inv * x - 8 * b_inv**2 - a_inv**3),
}
for n in range(5, 9):
    if n % 2 == 1:                       # n = 2m + 1
        m = n // 2
        psi[n] = reduce_y(psi[m + 2] * psi[m]**3 - psi[m - 1] * psi[m + 1]**3)
    else:                                # n = 2m
        m = n // 2
        psi[n] = reduce_y(sp.cancel(
            psi[m] * (psi[m + 2] * psi[m - 1]**2 - psi[m - 2] * psi[m + 1]**2) / (2 * y)))

# Psi2Sq = psi_2^2 reduced on the curve: (2y)^2 = 4(x^3 + 7).
Psi2Sq = reduce_y(psi[2]**2)
assert Psi2Sq == 4 * x**3 + 28, Psi2Sq

# psi_7 must be univariate and equal the CI-verified concrete form of `secp256k1.preΨ' 7`.
assert sp.degree(sp.Poly(psi[7], y), y) <= 0, "psi_7 not univariate"
psi7 = sp.expand(psi[7])
psi7_expected = (7 * x**24 + 27608 * x**21 - 2101904 * x**18 - 284585728 * x**15
                 - 2228742656 * x**12 - 26142548992 * x**9 - 330576748544 * x**6
                 - 661153497088 * x**3 + 377801998336)
assert psi7 == psi7_expected, psi7

# disjoint loci over Q (hence over Qbar): gcd is a nonzero constant
g = sp.gcd(sp.Poly(Psi2Sq, x, domain='QQ'), sp.Poly(psi7, x, domain='QQ'))
assert g.total_degree() == 0 and g.as_expr() != 0, "Psi2Sq, psi7 NOT coprime over Q"


# ---------------------------------------------------------------------------
# (b) polynomial extended Euclid over GF(p), pure integer coefficient lists
#     (verbatim helpers from scripts/certs/psi_squarefree_certs.py)
# ---------------------------------------------------------------------------
def to_coeffs(f):
    """sympy expr -> dense little-endian coefficient list of ints."""
    return [int(c) for c in reversed(sp.Poly(f, x).all_coeffs())]


def trim(f):
    while f and f[-1] % p == 0:
        f.pop()
    return f


def padd(f, g_):
    n = max(len(f), len(g_))
    return trim([((f[i] if i < len(f) else 0) + (g_[i] if i < len(g_) else 0)) % p
                 for i in range(n)])


def pscale(c, f):
    return trim([(c * a) % p for a in f])


def pmul(f, g_):
    if not f or not g_:
        return []
    out = [0] * (len(f) + len(g_) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g_):
            out[i + j] = (out[i + j] + a * b) % p
    return trim(out)


def pdivmod(f, g_):
    """f = q*g + r over GF(p), deg r < deg g."""
    f = trim([c % p for c in f])
    g_ = trim([c % p for c in g_])
    assert g_, "division by zero polynomial"
    ginv = pow(g_[-1], p - 2, p)
    q = [0] * max(len(f) - len(g_) + 1, 1)
    r = f[:]
    while r and len(r) >= len(g_):
        c = (r[-1] * ginv) % p
        d = len(r) - len(g_)
        q[d] = c
        for i, b in enumerate(g_):
            r[i + d] = (r[i + d] - c * b) % p
        r = trim(r)
    return trim(q), r


def ext_euclid(f, g_):
    """u, v with u*f + v*g = 1 over GF(p) (asserts gcd is a nonzero constant)."""
    r0, r1 = trim([c % p for c in f]), trim([c % p for c in g_])
    u0, u1 = [1], []
    v0, v1 = [], [1]
    while r1:
        q, r = pdivmod(r0, r1)
        r0, r1 = r1, r
        u0, u1 = u1, padd(u0, pscale(p - 1, pmul(q, u1)))
        v0, v1 = v1, padd(v0, pscale(p - 1, pmul(q, v1)))
    assert len(r0) == 1, "gcd not constant over GF(p)"
    cinv = pow(r0[0], p - 2, p)
    return pscale(cinv, u0), pscale(cinv, v0)


def derivative(f):
    return trim([(i * f[i]) % p for i in range(1, len(f))])


fZ = to_coeffs(Psi2Sq)                  # [28, 0, 0, 4]
gZ = to_coeffs(psi7)                    # degree 24, signed ints
fp_ = trim([c % p for c in fZ])
gp_ = trim([c % p for c in gZ])
assert len(fp_) == len(fZ) and len(gp_) == len(gZ), "leading coeff vanishes mod p"

u, v = ext_euclid(fp_, gp_)
assert padd(pmul(u, fp_), pmul(v, gp_)) == [1], "GF(p) Bezout identity fails"
# degree bounds and x^3-lattice sparsity
assert len(u) - 1 <= 21 and len(v) - 1 == 0, (len(u) - 1, len(v) - 1)
assert all(c == 0 for i, c in enumerate(u) if i % 3 != 0), "u not sparse on exponents = 0 mod 3"

# cross-check against sympy's GF(p) extended gcd
F2 = sp.Poly(Psi2Sq, x, domain=sp.GF(p))
F7 = sp.Poly(psi7, x, domain=sp.GF(p))
uG, vG, hG = F2.gcdex(F7)
assert hG.as_expr() == 1
assert {e[0]: int(c) % p for e, c in uG.terms()} == {i: c for i, c in enumerate(u) if c}
assert {e[0]: int(c) % p for e, c in vG.terms()} == {i: c for i, c in enumerate(v) if c}


# ---------------------------------------------------------------------------
# (c) closure/numeric insurance mod the real p: 24 distinct roots, all with y != 0
# ---------------------------------------------------------------------------
# psi_7 squarefree mod p: gcd(psi_7, psi_7') is a nonzero constant over GF(p)
u7, v7 = ext_euclid(gp_, derivative(gp_))          # raises if gcd not constant
assert padd(pmul(u7, gp_), pmul(v7, derivative(gp_))) == [1]
# gcd(psi_7, x^3 + 7) = 1 mod p (the y = 0 locus avoids every psi_7 root)
cubic = trim([7 % p, 0, 0, 1])
uc, vc = ext_euclid(gp_, cubic)                    # raises if gcd not constant
assert padd(pmul(uc, gp_), pmul(vc, cubic)) == [1]
print("closure invariants OK: psi_7 squarefree mod p; gcd(psi_7, x^3+7) = 1 mod p")


# ---------------------------------------------------------------------------
# (d) emit Ecdlp/Proved/CoprimePsi2Psi7.lean — zero hand transcription
# ---------------------------------------------------------------------------
SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def cname(prefix, i):
    return prefix + str(i).translate(SUB)


u_consts = [(cname('U', i), i, u[i]) for i in range(len(u) - 1, -1, -1) if u[i]]
v_consts = [(cname('V', i), i, v[i]) for i in range(len(v) - 1, -1, -1) if v[i]]
assert [i for _, i, _ in u_consts] == [21, 18, 15, 12, 9, 6, 3, 0]
assert [i for _, i, _ in v_consts] == [0]
assert len(u_consts) + len(v_consts) == 9


def monomial(body_c, i):
    if i == 0:
        return body_c
    if i == 1:
        return f"{body_c} * X"
    return f"{body_c} * X ^ {i}"


u_lean = " + ".join(monomial(f"C {nm}", i) for nm, i, _ in u_consts)
v_lean = " + ".join(monomial(f"C {nm}", i) for nm, i, _ in v_consts)


def lean_poly_numeral(coeffs_Z):
    """Signed integer coefficient list -> Lean numeral polynomial text (repo style)."""
    parts = []
    for i in range(len(coeffs_Z) - 1, -1, -1):
        c = coeffs_Z[i]
        if c == 0:
            continue
        body = monomial(str(abs(c)), i)
        parts.append(body if not parts and c > 0 else
                     (f"-{body}" if not parts else ("+ " if c > 0 else "- ") + body))
    return " ".join(parts)


psi7_lean = lean_poly_numeral(gZ)
assert psi7_lean == ("7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15 "
                     "- 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6 "
                     "- 661153497088 * X ^ 3 + 377801998336"), psi7_lean

# residue equations: coefficient of X^k in u*Psi2Sq + v*psi_7, as Z-linear forms
residues = []
for k in range(24, -1, -1):
    if k % 3 != 0:
        continue
    terms = []
    for nm, i, _ in u_consts:
        j = k - i
        if 0 <= j < len(fZ) and fZ[j] != 0:
            terms.append((fZ[j], nm))
    for nm, i, _ in v_consts:
        j = k - i
        if 0 <= j < len(gZ) and gZ[j] != 0:
            terms.append((gZ[j], nm))
    assert terms, f"no structural terms at X^{k}"
    expr = ""
    for t, (c, nm) in enumerate(terms):
        piece = f"{abs(c)} * {nm}"
        expr = (piece if c > 0 else f"-{piece}") if t == 0 else \
            expr + (" + " if c > 0 else " - ") + piece
    val = sum(c * dict((n2, cv) for n2, _, cv in u_consts + v_consts)[nm]
              for c, nm in terms) % p
    want = 1 if k == 0 else 0
    assert val == want, f"residue X^{k} = {val}, want {want}"
    residues.append((k, expr, want))
assert residues[-1] == (0, residues[-1][1], 1) and len(residues) == 9

haves = "\n".join(
    f"  have e{k} : ({expr} : ZMod Secp256k1.p) = {want} := by native_decide"
    for k, expr, want in residues)
key_rhs = "\n".join(
    ("      = " if t == 0 else "        + ") + f"C ({expr})" + ("" if k == 0 else f" * X ^ {k}")
    for t, (k, expr, _) in enumerate(residues))
const_defs = "\n".join(f"private def {nm} : ZMod Secp256k1.p :=\n  {c}"
                       for nm, _, c in u_consts + v_consts)
e_names = ", ".join(f"e{k}" for k, _, _ in residues)

# pre-wrapped long lines (f-string expressions cannot contain backslashes)
u_lean_refine = u_lean.replace("C U₁₂ * X ^ 12", "C U₁₂ * X ^ 12\n    ")
u_lean_key = u_lean.replace("C U₁₂ * X ^ 12", "C U₁₂ * X ^ 12\n        ")
psi7_lean_key = psi7_lean.replace(
    " - 2228742656 * X ^ 12", "\n          - 2228742656 * X ^ 12").replace(
    " - 661153497088 * X ^ 3", "\n          - 661153497088 * X ^ 3")

LEAN = f'''import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi7

/-!
# `Ψ₂Sq` and `preΨ' 7` are coprime for secp256k1 — the 2- and 7-torsion loci are disjoint (`E[2] ⊥ E[7]`)

The 2- and 7-division polynomials of `E : Y² = X³ + 7` share no root: **no nonidentity point is
simultaneously 2-torsion and 7-torsion.** A common root would be the `x`-coordinate of a nonzero
point whose order divides `gcd(2, 7) = 1` — impossible. Equivalently `gcd(ψ₂², ψ₇) = 1`, a
coprimality that is **not** in Mathlib. We certify it constructively with an explicit **Bézout
certificate** `u·Ψ₂Sq + v·(preΨ' 7) = 1` whose cofactors come from extended-Euclid over `𝔽_p`
(CAS; `scripts/certs/psi2_psi7_coprime_cert.py`, prints `CERT_OK`, and also generates this file —
zero hand transcription).

Both `Ψ₂Sq = 4X³+28` and the degree-24 `preΨ' 7` (concrete form `secp256k1_preΨ₇`,
`CoprimePsi3Psi7.lean`) live on exponents `≡ 0 (mod 3)`, so extended-Euclid stays inside
`𝔽_p[X³]`: the cofactors are **maximally sparse** (`u` on `X²¹,X¹⁸,…,X³,X⁰` and `v` a constant)
and the Bézout product collapses onto the nine powers `X²⁴,X²¹,…,X³,X⁰` — nine residue equations
in `ZMod p` discharged by `native_decide`, the nine-power sibling of the five-power
`CoprimePsi2Psi5`. Its role in the E[7] program: transported to `𝔽̄_p` it says `y ≠ 0` at every
root of `preΨ₇` — the `±y`-pairing input of the count `#E[7](𝔽̄_p) = 49`
(`SevenTorsionStructure.lean`). No new axioms beyond the compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = U₂₁X²¹+U₁₈X¹⁸+…+U₃X³+U₀`
(deg 21, sparse on exponents `≡ 0 mod 3`) and `v = V₀` (a constant), with
`u·Ψ₂Sq + v·(preΨ' 7) = 1`. (Fresh values — not the same-named private constants of
`CoprimePsi2Psi5`.) -/
{const_defs}

/-- **`Ψ₂Sq` and `preΨ' 7` are coprime — the 2-torsion and 7-torsion `x`-loci are disjoint**
(`E[2] ⊥ E[7]`). Their only possible common root would be a nonzero point whose order divides
`gcd(2, 7) = 1` (impossible); realized here by an explicit Bézout certificate over `𝔽_p`.
This coprimality is missing from Mathlib. Mirrors `CoprimePsi2Psi5` one rung up
(nine collapsed powers instead of five). -/
theorem secp256k1_isCoprime_Ψ₂Sq_preΨ₇ :
    IsCoprime secp256k1.Ψ₂Sq (secp256k1.preΨ' 7) := by
  refine ⟨{u_lean_refine}, {v_lean}, ?_⟩
  rw [secp256k1_Ψ₂Sq, secp256k1_preΨ₇]
{haves}
  -- collapse the sparse Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : ({u_lean_key})
        * (C 4 * X ^ 3 + C 28)
      + {v_lean}
        * ({psi7_lean_key})
{key_rhs} := by
    simp only [map_add, map_sub, map_mul, map_ofNat]; ring
  rw [key, {e_names}]
  simp

end Ecdlp.Curve
'''

repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = os.path.join(repo, 'Ecdlp', 'Proved', 'CoprimePsi2Psi7.lean')
with open(out, 'w') as fh:
    fh.write(LEAN)
print(f"wrote {out}")

print("constants: " + ", ".join(f"{nm}" for nm, _, _ in u_consts + v_consts))
for nm, _, c in u_consts + v_consts:
    print(f"  {nm} = {c}")
print(f"{len(u_consts) + len(v_consts)} constants / {len(residues)} residue equations")
print("CERT_OK")
