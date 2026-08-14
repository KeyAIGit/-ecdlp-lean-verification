# UORC-056 even division-polynomial Fourier collapse V10

## Status

V10 closes the pure single-division-polynomial character route left open by
V9. The secp256k1 conclusion no longer depends on the provisional V8 sheaf
constant: it follows from the published subgroup character-sum estimate of
Shparlinski and Stange.

Two exact facts drive the result:

```text
psi_(2u)(Q)=psi_2([u]Q)*psi_u(Q)^4,

max_r |sum_{k=1}^{n-1} (-1)^k exp(-2*pi*i*r*k/n)|
  = cot(pi/(2n)).
```

The first collapses every even index to a pullback of the fixed function
`psi_2=2y`. The second says that exact parity forces a Fourier coefficient of
size `cot(pi/(2n))`.

For `psi_2`, the published theorem gives the sufficient upper bound
`6*sqrt(q)`. A sharper `4*sqrt(q)` conductor calculation is retained as a
provisional refinement, not as the basis of the secp256k1 claim.

## 1. Setting

Let

```text
E/F_q,
H=<G>,
|H|=n,
```

where `q` is odd and `n>=3` is odd. Let `chi` be the quadratic character. The
pure route asks whether there are a positive integer `m` and one global phase
`epsilon in {+1,-1}` such that

```text
epsilon*chi(psi_m([k]G))=(-1)^k,
1<=k<n.
```

If `gcd(m,n)>1`, a nonzero subgroup point is an `m`-torsion zero of `psi_m`, so
an everywhere-defined sign evaluator is impossible. Only `gcd(m,n)=1` needs
analysis.

## 2. Odd indices fail covariance

Division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q).
```

For odd `m`, `chi(psi_m(Q))` is invariant under `Q -> -Q`. Canonical parity on
an odd cycle is anti-invariant:

```text
(-1)^(n-k)=-(-1)^k.
```

Hence every odd index is excluded.

## 3. Every even index collapses to psi_2

Write

```text
m=2u.
```

The normalized chain rule is

```text
psi_(ab)=(psi_a o [b])*psi_b^(a^2).
```

With `a=2`,

```text
psi_(2u)(Q)=psi_2([u]Q)*psi_u(Q)^4.
```

Because `gcd(u,n)=1`, `psi_u` is nonzero on the nonzero marked orbit. Taking
the quadratic character removes the fourth power:

```text
chi(psi_(2u)(Q))=chi(psi_2([u]Q)).
```

Thus an arbitrarily large even index does not create a new sign sequence. It
only permutes the fixed sequence

```text
tau(k)=chi(psi_2([k]G))=chi(2y([k]G)).
```

The executable replay checks this identity on 53,754 point-index pairs across
the five discovery curves for even indices through 256.

## 4. Fourier peak forced by parity

Take the near-half frequency

```text
r=(n-1)/2.
```

The exact parity coefficient has magnitude

```text
|sum_{k=1}^{n-1} (-1)^k exp(-2*pi*i*r*k/n)|
  = cot(pi/(2n)).
```

Multiplication by an invertible `u mod n` merely permutes the subgroup and
changes the frequency. Therefore an exact even-index evaluator would force
some subgroup Fourier coefficient of `chi(psi_2)` to have magnitude
`cot(pi/(2n))`.

## 5. Published 6*sqrt(q) bound

Shparlinski and Stange prove the following subgroup character-sum estimate. For
a subgroup `H`, a group character `omega`, a multiplicative character `chi`
and a rational function `f` that is not a perfect power of the relevant order,

```text
|sum_{Q in H} omega(Q)*chi(f(Q))|
  <= 2*deg(f)*sqrt(q).
```

For the classical second division polynomial,

```text
psi_2=2y,
deg(psi_2:E->P^1)=3.
```

It is not a square in the function field. Hence every subgroup Fourier
coefficient of `chi(psi_2)` satisfies

```text
|S| <= 6*sqrt(q).
```

A necessary condition for any pure division-polynomial parity formula is
therefore

```text
cot(pi/(2n)) <= 6*sqrt(q).                (V10.1)
```

This bound is published and is the primary secp256k1 certificate.

## 6. Sharper provisional 4*sqrt(q) refinement

The divisor of `psi_2` is

```text
div(psi_2)
 = sum_{T in E[2] minus {O}} [T] - 3[O].
```

Its geometric odd-valuation support has four points. The V8 Kummer-sheaf
conductor calculation therefore suggests the sharper bound

```text
|S| <= 4*sqrt(q),
```

and the stronger necessary condition

```text
cot(pi/(2n)) <= 4*sqrt(q).                (V10.2)
```

This refinement remains subject to specialist review. No secp256k1 conclusion
in V10 depends on accepting it.

## 7. secp256k1 certificate

The machine certificate uses the rational lower bound

```text
cot(pi/(2n)) > (98*n^2-121)/(154*n).
```

For the published estimate it verifies the exact integer inequality

```text
(98*n^2-121)^2 > 36*(154*n)^2*p.
```

For secp256k1,

```text
cot(pi/(2n))/(6*sqrt(p))
  approximately 3.610508049498494e37,

log2 of this ratio
  approximately 124.763541369807.
```

Therefore no positive integer `m` and no one-bit global phase can make

```text
chi(psi_m(Q))
```

equal canonical parity on every nonzero secp256k1 subgroup point.

The independent Paley-tournament theorem in
`UORC056_EDS_PALEY_OBSTRUCTION_V10.md` reaches the same secp256k1 conclusion by
a different argument.

## 8. Frozen-corpus result

The published `6*sqrt(q)` inequality closes 14 of the 18 frozen curves. The
four curves outside that numerical inequality are

```text
(p,n)=(43,31), (79,67), (61,61), (97,79).
```

For all four, and also as a redundant check for the other fourteen, V10 scans
every invertible multiplier class `u mod n` and both global phases. No exact
candidate exists anywhere in the 18-curve corpus.

The sharper provisional `4*sqrt(q)` inequality closes 17 of the 18 curves; only
`p=43,n=31` then needs the finite scan. On that smallest curve the best class
is

```text
u=8,
24/30 matches.
```

## 9. Compatibility with exact small witnesses

The corrected Ward audit freezes exact small mechanisms on separate curves of
orders 5 and 7:

```text
chi(psi_2([k]G))=(-1)^k.
```

These examples do not contradict V10. Both lie below the large-order Fourier
threshold, so condition (V10.1) does not exclude them. Their role is important:
they refute an unconditional algebraic no-go, while the Fourier and Paley
arguments explain why the same pure mechanism cannot scale to secp256k1.

## 10. What is closed

V10 closes:

- every odd-index pure division-polynomial character by negation covariance;
- every even-index pure character satisfying the published inequality
  `cot(pi/(2n))>6*sqrt(q)`;
- every positive index on secp256k1;
- every positive index on the declared 18-curve corpus, combining the theorem
  with complete multiplier scans;
- the V9 open pure EDS-decimation branch for secp256k1.

## 11. What remains open

V10 does not close:

1. products or ratios of several independently pulled division-polynomial
   factors;
2. shared arithmetic circuits whose final character does not collapse to one
   `chi(psi_m)`;
3. direct field-valued evaluation of `Y_G(x(Q))/y(Q)`;
4. theta or elliptic-unit constructions;
5. adaptive branching and non-character output models.

The next rational-character target should be a bounded multi-factor theorem,
not a larger search over a single index `m`. A natural question is whether a
product of `s` low-conductor pullbacks can be reduced to at most `O(s)` base
trace functions and therefore needs `s=Omega(n/sqrt(q))` to reproduce the
parity Fourier peak.

## 12. Primary references

- I. E. Shparlinski and K. E. Stange, *Character Sums with Division
  Polynomials*, Canadian Mathematical Bulletin 55 (2012), 850-857. Lemma 5
  gives the subgroup bound `2*deg(f)*sqrt(q)`.
- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in
  Number Theory 12 (2026), Article 53, for normalized division-polynomial
  recurrences and chain rules.
- J. H. Silverman, *p-adic properties of division polynomials and elliptic
  divisibility sequences*, Mathematische Annalen 332 (2005), 443-471.

## Claim boundary

This is a scoped no-go theorem for one quadratic character of one classical
division polynomial, with one optional global phase. The published
`6*sqrt(q)` estimate is sufficient for secp256k1. The sharper `4*sqrt(q)`
constant remains provisional. The package does not prove a lower bound for all
arithmetic circuits and does not recover any unknown scalar.
