#!/usr/bin/env python3
"""Dependency-independent replay of the fixed-target GLV scaling certificate.

INDEPENDENCE POSTURE. This validator shares **no** derivation code with the producer:

* it does not import `generate_fixed_target.py`, `generate.py`, or `validate.py`;
* it does not use sympy — all polynomial arithmetic is implemented here over `Z` with sparse
  exponent-vector monomials;
* it builds `S4` from the `4 x 4` Sylvester determinant by an explicit Leibniz expansion, not from
  the closed quadratic-resultant formula;
* it recomputes every witness **before** reading any claimed value from the certificate, and only
  then compares. The producer's asserted witness integers, excluded characteristics and zero-slice
  stabilizer are never used as inputs to the recomputation.

What it can establish: the certificate's algebra — support, per-`(e, keep-class)` pure-`r`
witnesses, the witness integers, the derived excluded-characteristic set, and the `r = 0` slice
stabilizer. What it cannot establish: that the author of this file is independent of the author of
the producer. That remains a source-review obligation.

Run:  python3 validate_fixed_target.py     # exit 0 on agreement, 1 otherwise
"""

from __future__ import annotations

import hashlib
import json
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = HERE / "fixed_target_certificate.json"
SHA = HERE / "fixed_target_certificate.sha256"

# Monomials are exponent tuples over (x1, x2, x3, b, r); polynomials are {monomial: int}.
NV = 5
X1, X2, X3, B, R = range(NV)
FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def const(n: int):
    return {} if n == 0 else {(0,) * NV: n}


def var(i: int):
    m = [0] * NV
    m[i] = 1
    return {tuple(m): 1}


def add(p, q):
    out = dict(p)
    for m, c in q.items():
        v = out.get(m, 0) + c
        if v:
            out[m] = v
        else:
            out.pop(m, None)
    return out


def neg(p):
    return {m: -c for m, c in p.items()}


def sub(p, q):
    return add(p, neg(q))


def mul(p, q):
    out: dict = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + bb for a, bb in zip(m1, m2))
            v = out.get(m, 0) + c1 * c2
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def smul(n: int, p):
    return {} if n == 0 else {m: n * c for m, c in p.items()}


def square(p):
    return mul(p, p)


def slice_coeffs(u, v):
    """The three quadratic-slice coefficients of S3(u, v, X) in X, as polynomials."""
    two_b = smul(2, var(B))
    f2 = square(sub(u, v))
    f1 = neg(smul(2, add(mul(add(u, v), mul(u, v)), two_b)))
    f0 = sub(square(mul(u, v)), smul(4, mul(var(B), add(u, v))))
    return f2, f1, f0


def determinant(rows):
    """Leibniz expansion; 4x4 means 24 terms, so this stays cheap and obviously correct."""
    n = len(rows)
    total: dict = {}
    for perm in permutations(range(n)):
        sign = 1
        seen = list(perm)
        for i in range(n):
            for j in range(i + 1, n):
                if seen[i] > seen[j]:
                    sign = -sign
        term = const(sign)
        for i in range(n):
            term = mul(term, rows[i][perm[i]])
        total = add(total, term)
    return total


def build_fixed_target():
    """F_r(x1,x2,x3) = Res_X(S3(x1,x2,X), S3(x3,r,X)) via the 4x4 Sylvester determinant."""
    f2, f1, f0 = slice_coeffs(var(X1), var(X2))
    g2, g1, g0 = slice_coeffs(var(X3), var(R))
    zero: dict = {}
    rows = [
        [g0, zero, f0, zero],
        [g1, g0, f1, f0],
        [g2, g1, f2, f1],
        [zero, g2, zero, f2],
    ]
    return determinant(rows)


def support_in_x(poly):
    """Group by the (x1,x2,x3) exponent vector; coefficient stays a polynomial in (b,r)."""
    out: dict = {}
    for m, c in poly.items():
        key = (m[X1], m[X2], m[X3])
        rest = (m[B], m[R])
        out.setdefault(key, {})[rest] = out.setdefault(key, {}).get(rest, 0) + c
    return {k: {m: c for m, c in v.items() if c} for k, v in out.items() if any(v.values())}


def pure_r_witness(coeff_br):
    """`coeff_br` is {(b_exp, r_exp): int}. Return (|N|, k) if it is N*r^k with k>=1, no b."""
    if len(coeff_br) != 1:
        return None
    (eb, er), c = next(iter(coeff_br.items()))
    if eb != 0 or er < 1:
        return None
    return (abs(c), er)


def recompute():
    """Everything, computed from scratch, with no reference to the certificate."""
    sup = support_in_x(build_fixed_target())
    rows = []
    for e in product(range(3), repeat=3):
        if not any(e):
            continue
        for c in range(3):
            must = [co for a, co in sup.items()
                    if sum(ei * ai for ei, ai in zip(e, a)) % 3 != c]
            wits = [w for w in (pure_r_witness(co) for co in must) if w is not None]
            rows.append({
                "exponents": list(e), "keep_class": c,
                "witness": ({"integer_abs": min(wits)[0], "r_power": min(wits)[1]}
                            if wits else None),
            })
    ints = sorted({row["witness"]["integer_abs"] for row in rows if row["witness"]})

    def primes_of(n):
        out, d, m = set(), 2, n
        while d * d <= m:
            while m % d == 0:
                out.add(d); m //= d
            d += 1
        if m > 1:
            out.add(m)
        return out

    primes = sorted({q for n in ints for q in primes_of(n)})

    # r = 0 slice: substitute r -> 0 by discarding every monomial with positive r-degree
    zero_poly = {m: c for m, c in build_fixed_target().items() if m[R] == 0}
    zsup = list(support_in_x(zero_poly).keys())
    zstab = []
    for e in product(range(3), repeat=3):
        vals = {sum(ei * ai for ei, ai in zip(e, a)) % 3 for a in zsup}
        if len(vals) == 1:
            zstab.append({"exponents": list(e), "multiplier_beta_exponent": vals.pop()})

    return {"support_size": len(sup), "rows": rows, "integers": ints,
            "primes": primes, "zero_stabilizer": zstab}


def main() -> int:
    if not CERT.exists():
        print("fixed_target_certificate.json is missing")
        return 1

    mine = recompute()                                    # computed FIRST, independently
    cert = json.loads(CERT.read_text(encoding="utf-8"))   # only now is the claim read

    # hash binding
    payload = (json.dumps(cert, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
    if SHA.exists():
        want = SHA.read_text(encoding="utf-8").strip()
        got = hashlib.sha256(payload).hexdigest()
        if want != got:
            fail(f"certificate sha256 mismatch: recorded {want}, recomputed {got}")

    alg = cert.get("algebra", {})
    if alg.get("support_size") != mine["support_size"]:
        fail(f"support size: certificate {alg.get('support_size')} vs replay {mine['support_size']}")

    claimed = {(tuple(row["exponents"]), row["keep_class"]): row
               for row in cert.get("fixed_target_witnesses", [])}
    replay = {(tuple(row["exponents"]), row["keep_class"]): row for row in mine["rows"]}
    if set(claimed) != set(replay):
        fail("the (e, keep-class) index sets differ between certificate and replay")
    for key, row in replay.items():
        other = claimed.get(key)
        if other is None:
            continue
        if (other.get("witness") or None) != (row["witness"] or None):
            fail(f"witness mismatch at e={key[0]} class={key[1]}: "
                 f"certificate {other.get('witness')} vs replay {row['witness']}")

    summary = cert.get("witness_summary", {})
    if summary.get("distinct_minimal_witness_integers") != mine["integers"]:
        fail(f"witness integers: certificate {summary.get('distinct_minimal_witness_integers')} "
             f"vs replay {mine['integers']}")
    if summary.get("primes_dividing_some_witness_integer") != mine["primes"]:
        fail(f"witness primes: certificate {summary.get('primes_dividing_some_witness_integer')} "
             f"vs replay {mine['primes']}")
    if summary.get("excluded_characteristics") != sorted(set(mine["primes"]) | {3}):
        fail("excluded-characteristic set does not follow from the replayed witnesses")
    if summary.get("rows_without_pure_r_witness") != sum(
            1 for row in mine["rows"] if row["witness"] is None):
        fail("count of rows without a pure-r witness disagrees")

    zclaim = cert.get("zero_slice", {}).get("stabilizer", [])
    if sorted(map(json.dumps, zclaim, )) != sorted(map(json.dumps, mine["zero_stabilizer"])):
        fail(f"r=0 slice stabilizer: certificate {zclaim} vs replay {mine['zero_stabilizer']}")

    # the load-bearing derived conclusion, re-derived here rather than trusted
    if any(row["witness"] is None for row in mine["rows"]):
        fail("some (e, keep-class) pair has NO pure-r witness: the fixed-target conclusion "
             "does not follow for every nonzero target")
    if 2 not in mine["primes"] or len(mine["primes"]) != 1:
        fail(f"expected the witness primes to be exactly [2]; replay gives {mine['primes']}")

    if FAILURES:
        print("FIXED-TARGET REPLAY FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1

    print(
        "fixed-target replay OK: "
        f"support {mine['support_size']} monomials; {len(mine['rows'])} (e,class) rows all carry a "
        f"pure-r witness; witness integers {mine['integers']} (primes {mine['primes']}); "
        f"excluded characteristics {sorted(set(mine['primes']) | {3})}; "
        f"r=0 stabilizer has order {len(mine['zero_stabilizer'])}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
