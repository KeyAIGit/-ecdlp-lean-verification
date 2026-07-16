#!/usr/bin/env python3
"""Squarefreeness certificates for secp256k1's division polynomials (node B4 @ small n).

For E : y^2 = x^3 + 7 over F_p (p = 2^256 - 2^32 - 977), the odd division polynomials
psi_n are univariate in x, and "psi_n squarefree" — separability of [n] in polynomial
clothing (notes/SEPARABILITY_ROUTES.md, route B, node B4) — is EQUIVALENT (char p does
not divide the leading coefficient n or n!) to gcd(psi_n, psi_n') = 1. We certify this
at n = 3, 5, 7 with explicit Bezout cofactors u, v over GF(p):

    u * psi_n + v * psi_n' = 1.

Pipeline (all checks must pass before anything is emitted):
  (a) build psi_n independently from the division-polynomial recurrence over Q
      (reducing y^2 -> x^3 + 7), and match the known univariate forms
      psi_3 = 3x^4 + 84x, psi_5 = 5x^12 + 2660x^9 - 11760x^6 - 548800x^3 - 614656,
      and the degree-24 psi_7 (= Lean's `secp256k1.preΨ' 7`, CI-verified in
      Ecdlp/Proved/CoprimePsi3Psi7.lean);
  (b) extended Euclid over GF(p) (pure-integer coefficient lists, inverses via
      pow(a, p-2, p)) to get u, v; verify u*psi_n + v*psi_n' == 1 by direct
      polynomial multiplication mod p; verify gcd(psi_n, psi_n') = 1 over Q
      (sympy — the discriminant Delta != 0 structure) and that no leading
      coefficient vanishes mod p;
  (c) emit the private Lean constants (decimal), the FULL list of residue
      equations (each coefficient of u*psi_n + v*psi_n' - 1 vanishes mod p; these
      are the `native_decide` goals), and the collapsing `key` identity RHS,
      ready to paste into Ecdlp/Proved/DivisionPolynomialSquarefree.lean.

Prints CERT_OK iff every check passes.
"""
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

# odd psi_n are univariate in x — extract and match the expected concrete forms
for n in (3, 5, 7):
    assert sp.degree(sp.Poly(psi[n], y), y) <= 0, f"psi_{n} not univariate"

psi3 = sp.expand(psi[3])
psi5 = sp.expand(psi[5])
psi7 = sp.expand(psi[7])

assert psi3 == 3 * x**4 + 84 * x, psi3
assert psi5 == 5 * x**12 + 2660 * x**9 - 11760 * x**6 - 548800 * x**3 - 614656, psi5
# psi_7 must equal the CI-verified concrete form of `secp256k1.preΨ' 7`
psi7_expected = (7 * x**24 + 27608 * x**21 - 2101904 * x**18 - 284585728 * x**15
                 - 2228742656 * x**12 - 26142548992 * x**9 - 330576748544 * x**6
                 - 661153497088 * x**3 + 377801998336)
assert psi7 == psi7_expected, psi7

# gcd(psi_n, psi_n') constant over Q (squarefreeness over Q; Delta = -16*27*49 != 0 structure).
# Over Z the gcd may be a content constant (e.g. 3 for psi_3); constant <=> coprime over Q.
for n, f in ((3, psi3), (5, psi5), (7, psi7)):
    df = sp.diff(f, x)
    g = sp.gcd(sp.Poly(f, x, domain='QQ'), sp.Poly(df, x, domain='QQ'))
    assert g.total_degree() == 0 and g.as_expr() != 0, f"psi_{n} not squarefree over Q"

Delta = -16 * (4 * a_inv**3 + 27 * b_inv**2)
assert Delta == -21168 and Delta % p != 0


# ---------------------------------------------------------------------------
# (b) polynomial extended Euclid over GF(p), pure integer coefficient lists
# ---------------------------------------------------------------------------
def to_coeffs(f):
    """sympy expr -> dense little-endian coefficient list of ints."""
    return [int(c) for c in reversed(sp.Poly(f, x).all_coeffs())]


def trim(f):
    while f and f[-1] % p == 0:
        f.pop()
    return f


def padd(f, g):
    n = max(len(f), len(g))
    return trim([((f[i] if i < len(f) else 0) + (g[i] if i < len(g) else 0)) % p
                 for i in range(n)])


def pscale(c, f):
    return trim([(c * a) % p for a in f])


def pmul(f, g):
    if not f or not g:
        return []
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] = (out[i + j] + a * b) % p
    return trim(out)


def pdivmod(f, g):
    """f = q*g + r over GF(p), deg r < deg g."""
    f = trim([c % p for c in f])
    g = trim([c % p for c in g])
    assert g, "division by zero polynomial"
    ginv = pow(g[-1], p - 2, p)
    q = [0] * max(len(f) - len(g) + 1, 1)
    r = f[:]
    while r and len(r) >= len(g):
        c = (r[-1] * ginv) % p
        d = len(r) - len(g)
        q[d] = c
        for i, b in enumerate(g):
            r[i + d] = (r[i + d] - c * b) % p
        r = trim(r)
    return trim(q), r


def ext_euclid(f, g):
    """u, v with u*f + v*g = 1 over GF(p) (asserts gcd is a nonzero constant)."""
    r0, r1 = trim([c % p for c in f]), trim([c % p for c in g])
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


def derivative_Z(f):
    """Derivative over Z (signed integer coefficients, for Lean literals)."""
    out = [i * f[i] for i in range(1, len(f))]
    while out and out[-1] == 0:
        out.pop()
    return out


SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def lean_poly(coeffs_Z, const_C=False):
    """Signed integer coefficient list -> Lean polynomial text like the repo's concrete forms."""
    terms = []
    for i in range(len(coeffs_Z) - 1, -1, -1):
        c = coeffs_Z[i]
        if c == 0:
            continue
        mag = abs(c)
        if i == 0:
            body = f"C {mag}" if const_C else f"{mag}"
        elif i == 1:
            body = f"{mag} * X"
        else:
            body = f"{mag} * X ^ {i}"
        if not terms:
            terms.append(body if c > 0 else f"-{body}")
        else:
            terms.append(("+ " if c > 0 else "- ") + body)
    return " ".join(terms) if terms else "0"


def cofactor_lean(name_prefix, coeffs):
    """GF(p) coefficient list -> (list of (lean_name, exp, value), Lean sum expression)."""
    consts, parts = [], []
    for i in range(len(coeffs) - 1, -1, -1):
        c = coeffs[i] % p
        if c == 0:
            continue
        nm = f"{name_prefix}{i}"
        consts.append((nm, i, c))
        if i == 0:
            parts.append(f"C {nm}")
        elif i == 1:
            parts.append(f"C {nm} * X")
        else:
            parts.append(f"C {nm} * X ^ {i}")
    return consts, " + ".join(parts)


def residue_expr(k, fZ, u_consts, dZ, v_consts):
    """Text of the X^k coefficient of u*f + v*f' as a Z-linear form in the U/V names."""
    terms = []
    for nm, i, _ in u_consts:
        j = k - i
        if 0 <= j < len(fZ) and fZ[j] != 0:
            terms.append((fZ[j], nm))
    for nm, i, _ in v_consts:
        j = k - i
        if 0 <= j < len(dZ) and dZ[j] != 0:
            terms.append((dZ[j], nm))
    out = ""
    for t, (c, nm) in enumerate(terms):
        mag = abs(c)
        piece = f"{mag} * {nm}"
        if t == 0:
            out = piece if c > 0 else f"-{piece}"
        else:
            out += (" + " if c > 0 else " - ") + piece
    return out, terms


print("=" * 78)
emitted = {}
for n, f_expr, lean_obj, u_name, v_name in (
        (3, psi3, "secp256k1.Ψ₃", "u3_", "v3_"),
        (5, psi5, "secp256k1.preΨ' 5", "u5_", "v5_"),
        (7, psi7, "secp256k1.preΨ' 7", "u7_", "v7_")):
    fZ = to_coeffs(f_expr)                      # signed ints (as given over Q/Z)
    dZ = derivative_Z(fZ)                       # signed ints — Lean derivative literals
    fp_ = trim([c % p for c in fZ])             # GF(p)
    dp_ = derivative(fp_)
    assert [c % p for c in dZ] == dp_, "derivative mismatch Z vs GF(p)"

    # leading coefficients do not vanish mod p
    assert fZ[-1] % p != 0 and dZ[-1] % p != 0, f"leading coeff vanishes mod p (n={n})"
    assert len(fp_) == len(fZ) and len(dp_) == len(dZ)

    u, v = ext_euclid(fp_, dp_)
    # sanity: identity by direct polynomial multiplication mod p
    assert padd(pmul(u, fp_), pmul(v, dp_)) == [1], f"Bezout identity fails (n={n})"
    assert len(u) - 1 < len(dp_) - 1 + 1 and len(v) - 1 < len(fp_) - 1 + 1  # deg bounds

    u_consts, u_lean = cofactor_lean(u_name, u)
    v_consts, v_lean = cofactor_lean(v_name, v)

    # residue equations: every coefficient of u*f + v*f' is 0 mod p except X^0, which is 1.
    prod = padd(pmul(u, fp_), pmul(v, dp_))
    maxdeg = (len(u) - 1) + (len(fp_) - 1)
    residues = []
    for k in range(maxdeg, -1, -1):
        expr, terms = residue_expr(k, fZ, u_consts, dZ, v_consts)
        if not terms:
            continue
        val = sum(c * dict((nm2, cv) for nm2, _, cv in u_consts + v_consts)[nm]
                  for c, nm in terms) % p
        want = 1 if k == 0 else 0
        assert val == want, f"residue X^{k} (n={n}) = {val}, want {want}"
        residues.append((k, expr, want))
    # the residue list must cover every nonzero structural coefficient position
    assert residues[-1][0] == 0 and residues[-1][2] == 1

    emitted[n] = dict(fZ=fZ, dZ=dZ, u_consts=u_consts, v_consts=v_consts,
                      u_lean=u_lean, v_lean=v_lean, residues=residues, lean_obj=lean_obj)

    # ------------------------------- emit Lean -------------------------------
    print(f"-- ========== n = {n}: {lean_obj} ==========")
    print(f"-- psi_{n}  = {lean_poly(fZ)}")
    print(f"-- psi_{n}' = {lean_poly(dZ)}")
    print(f"-- {len(u_consts)} u-constants, {len(v_consts)} v-constants, "
          f"{len(residues)} residue equations")
    for nm, _, c in u_consts + v_consts:
        print(f"private def {nm} : ZMod Secp256k1.p :=\n  {c}")
    print(f"-- refine ⟨{u_lean},\n--   {v_lean}, ?_⟩")
    for k, expr, want in residues:
        print(f"have e{n}_{k} : ({expr} : ZMod Secp256k1.p) = {want} := by native_decide")
    print("-- key identity RHS (one C per power of X):")
    key = " + ".join(f"C ({expr}) * X ^ {k}" if k > 0 else f"C ({expr})"
                     for k, expr, _ in residues)
    print("--   " + key)
    print()

print("=" * 78)
print("constant counts: " + ", ".join(
    f"n={n}: {len(d['u_consts']) + len(d['v_consts'])} constants / "
    f"{len(d['residues'])} residue equations" for n, d in emitted.items()))
print("CERT_OK")
