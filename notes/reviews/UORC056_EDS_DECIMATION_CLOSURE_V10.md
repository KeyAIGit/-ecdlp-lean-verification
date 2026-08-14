# UORC-056 EDS decimation audit V10

Date: 2026-08-14

## Status

The attempted Ward-only universal no-go is retracted. Exact even EDS
parity decimations genuinely exist on small odd prime-order curves.

The pure single-division-polynomial route is nevertheless closed for
secp256k1 by two separate companion results:

```text
UORC056_EVEN_DIVPOLY_FOURIER_COLLAPSE_V10,
UORC056_EDS_PALEY_OBSTRUCTION_V10.
```

This distinction is essential. The corrected Ward recurrence permits the small
mechanism. The large-order Fourier and Paley bounds prevent that pure mechanism
from scaling to secp256k1.

The central target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

## 1. Surviving division-polynomial family before the V10 closures

The covariance

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q)
```

excludes odd `m` and excludes even `m` when `chi(-1)=+1`. The only case left by
V9 for secp256k1 was

```text
m even,
chi(-1)=-1,
D_m([k]G)=chi(psi_m([k]G)).
```

## 2. Exact re-marking equivalence

Let `n` be odd prime, let `m` be even with `n` not dividing `m`, and put

```text
P=[m]G.
```

The chain rule in the two orders gives

```text
psi_(mk)(G)=psi_m([k]G) psi_k(G)^(m^2)
           =psi_k(P) psi_m(G)^(k^2).
```

Therefore

```text
D_m([k]G)=(-1)^k for every 1<=k<n
```

if and only if

```text
rho_m(G)=chi(psi_m(G))=-1
```

and

```text
chi(psi_k(P))=+1 for every 1<=k<n.       (V10.1)
```

This equivalence is exact and remains useful as a structural description of
the small witnesses.

## 3. Ward normalization correction

The first Ward-based no-go used the wrong neighboring terms for the torsion
quasi-period constants. Silverman, Theorem 8, uses

```text
F_(s*n+k)(P)=a^(s*k) b^(s^2) F_k(P),
```

with

```text
a=F_(n+2)(P)/(F_2(P)F_(n+1)(P)),
b=F_2(P)F_(n+1)(P)^2/F_(n+2)(P).
```

Condition (V10.1) does not force both constants to be residues. In the exact
examples below,

```text
chi(a)=+1,
chi(b)=-1,
```

which is fully compatible with the EDS recurrence when `chi(-1)=-1`.

The corrected Lean file deliberately formalizes only the valid chain-rule and
sign reductions. It does not encode the retracted contradiction.

## 4. Exact small parity-decimation witnesses

The executable audit freezes two exact mechanisms on curves
`y^2=x^3+7`.

### Order 5

```text
F_59,
G=(22,25),
n=5,
m=2,
P=[2]G=(31,11).
```

Exactly,

```text
chi(psi_2([k]G))=(-1)^k,
k=1,2,3,4.
```

Also `rho_2(G)=-1`, while

```text
chi(psi_k(P))=+1,
k=1,2,3,4.
```

### Order 7

```text
F_83,
G=(70,36),
n=7,
m=2,
P=[2]G=(74,5).
```

Again,

```text
chi(psi_2([k]G))=(-1)^k,
k=1,...,6,
```

and the re-marked generator has an all-residue nonzero EDS row.

Both examples have `q=3 mod 4`. The corrected Ward formula and the specialized
EDS recurrence are checked exactly.

These examples prove that no unconditional statement of the form

```text
no even EDS decimation can ever compute parity
```

is true.

## 5. Why secp256k1 is still excluded

### 5.1 Exact Fourier collapse

Every even index can be written `m=2u`. The normalized chain rule gives

```text
psi_(2u)(Q)=psi_2([u]Q)*psi_u(Q)^4.
```

On an odd subgroup with `gcd(u,n)=1`, taking the quadratic character removes
the fourth power:

```text
chi(psi_(2u)(Q))=chi(psi_2([u]Q)).       (V10.2)
```

Thus the apparent arbitrary-index EDS decimation is only a permutation of the
fixed sign sequence `chi(2y([k]G))`.

Canonical parity has a subgroup Fourier coefficient of magnitude

```text
cot(pi/(2n)).
```

Shparlinski and Stange, Lemma 5, bound every subgroup Fourier coefficient of
`chi(psi_2)` by

```text
2*deg(psi_2)*sqrt(q)=6*sqrt(q),
```

because `deg(psi_2)=deg(2y)=3`. Hence a necessary condition is

```text
cot(pi/(2n)) <= 6*sqrt(q).               (V10.3)
```

The exact secp256k1 certificate verifies

```text
(98*n^2-121)^2 > 36*(154*n)^2*p,
```

which is a rational lower certificate for the strict reverse of (V10.3). The
Fourier peak exceeds `6*sqrt(p)` by approximately `2^124.76`.

Therefore no pure `chi(psi_m(Q))`, for any index `m`, computes canonical parity
on secp256k1.

### 5.2 Independent Paley obstruction

A separate argument assumes an exact even-index candidate and normalizes the
re-marked generator so that every nonzero `psi_k` value is a square. The
standard division-polynomial difference identity then makes the half-orbit
x-coordinates a transitive subtournament of the Paley tournament.

If

```text
t=(n-1)/2,
```

the Paley character matrix and the transitive sign matrix imply the necessary
condition

```text
t^2 <= 3q+1.                             (V10.4)
```

secp256k1 violates (V10.4) by a huge exact integer margin. This supplies an
independent cross-check of the Fourier conclusion.

## 6. Frozen-corpus status

The original five discovery curves have no exact even decimation class modulo
`2n`.

Across the full 18-curve transfer corpus:

- the published `6*sqrt(q)` inequality closes 14 curves;
- the remaining four are closed by exhaustive scans of all invertible
  multiplier classes and both global phases;
- no exact pure candidate remains.

The separate order-5 and order-7 witnesses are intentionally outside that
transfer corpus and below the large-order obstruction threshold.

## 7. Scientific conclusion

The corrected conclusion is not

```text
EDS decimation never works.
```

It is

```text
EDS decimation is a real finite mechanism,
but one pure division-polynomial factor cannot scale to secp256k1 parity.
```

This is stronger and more informative than either the retracted Ward no-go or
the earlier bounded search through `m<=4096`.

## 8. Next frontier

Searching larger values of a single index `m` is obsolete. Identity (V10.2)
classifies all such indices at once.

The next rational-character frontier is genuinely multi-factor:

```text
chi(prod_i psi_(m_i)(Q) / prod_j psi_(r_j)(Q)),
```

with exact divisor cancellation and all representation costs charged.

The high-leverage theoretical question is whether a product of `s` independent
pullbacks has Fourier or Paley complexity at most `O(s*sqrt(q))`. Such a theorem
would force

```text
s=Omega(n/sqrt(q)),
```

which is `Omega(sqrt(n))` when `n` and `q` are comparable.

Separate open routes are:

- direct field-valued evaluation of `Y_G(x(Q))/y(Q)`;
- compact integration of the oriented Miller cocycle;
- theta or elliptic-unit constructions;
- adaptive branching and non-character outputs.

## 9. Source lock

- J. H. Silverman, *p-adic properties of division polynomials and elliptic
  divisibility sequences*, Math. Ann. 332 (2005), Theorem 8.
- I. E. Shparlinski and K. E. Stange, *Character Sums with Division
  Polynomials*, Canadian Mathematical Bulletin 55 (2012), especially Lemma 5.
- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in
  Number Theory 12:53 (2026), recurrence and chain rule.
- `UORC056_EVEN_DIVPOLY_FOURIER_COLLAPSE_V10.md`.
- `UORC056_EDS_PALEY_OBSTRUCTION_V10.md`.

## Claim boundary

This audit proves the corrected Ward normalization, the exact re-marking
equivalence and exact small witnesses. The secp256k1 no-go is supplied by the
companion Fourier and Paley theorems, not by the Ward recurrence alone. Products
or ratios of multiple division-polynomial factors remain open. No unknown
production scalar is used or recovered.
