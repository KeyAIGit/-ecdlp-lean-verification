# NONLOCAL-ODD-ANCHOR-004

Date: 2026-08-11

Status: **isolated, non-executable theorem-first and toy-scaling package**.
This package targets no external point, key, wallet, or production discrete-log
instance. It changes no canonical Research Engine state, authorizes no attack
run, and makes no asymptotic-improvement claim.

## 1. Exact objective

Let `G` generate a cyclic subgroup of odd prime order `n`, and write

```text
Q = [k]G,        0 < k < n,
rho_G(Q) = chi(psi_k(G)).
```

Previous packages established three obstructions:

1. fixed-rank elliptic-net identities give relative residue labels but preserve
   one global sign gauge;
2. bounded root covers and fixed isogenies are reparameterizations of the same
   prime-order group;
3. the first absolute order-`n` torsion jet exists and is fast, but its
   normalization character equals the already-public point-function character.

The present package asks for an **odd absolute anchor**: a public section whose
character law contains an odd number of nonpublic `rho_G` factors after every
quadratic-net normalization, period carry, isogeny factor, and public
point-function term has been removed.

A multiplicative expression has odd EDS gauge weight when it changes sign under

```text
rho(.) -> -rho(.).
```

Pairwise labels have even weight. A product of three residue labels has odd
weight.

## 2. Correction: canonical period carry is part of every affine net pullback

Let

```text
L = a + b*k = t + c*n,        0 <= t < n.
```

The elliptic-net transformation formula naturally produces the
**integer-index** residue

```text
rho_int(L) = chi(psi_L(G)),
```

not directly the canonical point label `rho(t)`. If

```text
s = chi(phi_raw(G)),
C(t) = chi(phi_raw([t]G)) = s^t rho(t),
```

then periodic normalization gives

```text
rho_int(L) = s^c rho(t).
```

For a fixed rank-two affine pullback, the character form of the net
transformation is

```text
nu_(a,b)(Q) * r(k)^(a*b)
  = rho_int(a+b*k) * rho(k)^(b^2),
```

where `nu_(a,b)` and the adjacent ratio `r(k)` are public.

Because `n` is odd, the carry equation implies:

```text
b even:  c+t       = a  (mod 2),
b odd:   c+t+k     = a  (mod 2).
```

Consequently the hidden side becomes exactly

```text
b even:
  s^c rho(t) = s^a C(t),

b odd:
  s^c rho(t)rho(k) = s^a C(t)C(k).
```

Thus the apparent canonical comparison oracle disappears. The wrap carry
restores precisely the point-function gauge that seemed to have been removed.

The frozen verifier checks this cancellation for every nonzero scalar on all
eight secp256k1-like Kummer-invariant toy cases and for

```text
-4 <= a,b <= 4.
```

Total exact affine carry-cocycle checks:

```text
701,728.
```

This strengthens `RELATIVE-RESIDUE-GAUGE-001`: fixed affine rank-two pulls do
not merely leave an unspecified sign; after canonicalization they reduce to a
literal public identity.

## 3. The first genuine odd hidden aggregate

Let the `j=0` GLV automorphism be

```text
phi(x,y) = (beta*x,y),
```

and let its scalar eigenvalue satisfy

```text
phi(G) = [lambda]G,
lambda^2 + lambda + 1 = 0 mod n.
```

For `Q=[k]G`, define the canonical GLV orbit

```text
Q0 = Q,
Q1 = phi(Q),
Q2 = phi^2(Q),
```

and the odd residue aggregate

```text
R3(Q)
  = rho_G(Q0) rho_G(Q1) rho_G(Q2).
```

This object has exactly three nonpublic EDS-residue factors. On a
Kummer-invariant residue instance it satisfies

```text
R3(-Q) = R3(Q),
R3(phi(Q)) = R3(Q).
```

Therefore `R3` is a well-defined binary function on the public `C6` orbit of
`Q`. It is the first explicit object in the parity line that simultaneously:

1. has odd EDS gauge weight;
2. is Kummer invariant;
3. respects the concrete secp256k1 GLV symmetry;
4. is not a pairwise relative label.

This is a positive structural localization. `R3` is still hidden; no public
decoder has been obtained.

## 4. The GLV orbit carry

Let `k_i` be the canonical scalar representative of `Q_i`. Since

```text
Q0 + Q1 + Q2 = O,
```

one has

```text
k_0 + k_1 + k_2 = gamma(Q)*n,
gamma(Q) in {1,2}.
```

The bit `gamma` is an orientation of the canonical scalar lifts of the
zero-sum GLV triple. It obeys

```text
gamma(-Q) = 3-gamma(Q).
```

For secp256k1, where `s=chi(phi_raw(G))=-1`, the public point-function orbit
product is

```text
C3(Q)
  = product_i chi(phi_raw(Q_i))
  = (-1)^gamma(Q) R3(Q).                  (P)
```

Thus a decoder for `R3` would also decode the GLV carry bit `gamma`, and vice
versa given the public value `C3`.

The carry is not an artificial bookkeeping error. It is the remaining
nonlocal canonical-lift orientation after the local EDS gauge has been
removed.

## 5. Why the first absolute torsion jet does not separate the carry

Let

```text
J_n(P) = D_omega psi_n(P)
```

be the first absolute torsion jet from `ABSOLUTE-EDS-SECTION-003`, and put

```text
b_G = chi(J_n(G)).
```

Its exact character law on secp256k1-like cases is

```text
chi(J_n([t]G)) = b_G (-1)^(t-1) rho(t).
```

Taking the product over the three GLV orbit points gives

```text
J3(Q)
  = product_i chi(J_n(Q_i))
  = b_G (-1)^(gamma(Q)+1) R3(Q).
```

Combining with (P):

```text
J3(Q) = -b_G C3(Q).
```

So the first public absolute section does contain three hidden residues in its
raw transformation law, but the same carry exponent appears and the result is
exactly dependent on the already-public point-function norm.

This identifies the next precise requirement:

> A successful odd section must have a GLV-orbit normalization character
> different from the point-function character, so that two public orbit norms
> give independent equations for `R3` and `gamma`.

## 6. Smallest public GLV-invariant character algebra

On

```text
E: y^2=x^3+7,
```

the basic GLV/Kummer coordinate is

```text
u(Q)=x(Q)^3.
```

The bounded screen tests every nonvanishing character vector

```text
chi(u(Q)+a),       a in F_p,
```

and every exact product of two such vectors against `R3`.

Protocol:

```text
15 frozen j=0 prime-order toy subgroups,
8 Kummer-invariant cases retained,
orders up to 3469,
200 matched random C6-invariant label controls per case,
one public global sign allowed.
```

Results:

```text
exact single decoders:              0
exact pair decoders:                0
cases above matched 95% null:       0
maximum empirical null percentile:  0.915
```

For the largest retained subgroup:

```text
order:                   3469
observed best accuracy:  0.572664
matched null median:     0.577855
matched null 95%:        0.589965
```

The observed correlation is below the matched random-label median.

**Disposition:** the smallest natural GLV-invariant rational-character algebra
does not decode the odd aggregate and shows no positive cross-order signal.

## 7. Nonlocal prefix section

A mathematically exact global primitive is

```text
H(k) = product_(j=1)^k rho(j),
H(k)/H(k-1) = rho(k).
```

Unlike pairwise net labels, `H` fixes an absolute gauge once `H(0)=1` is chosen.
It is therefore a genuine nonlocal odd section.

The difficulty is evaluation: its definition follows the unknown canonical
path from `O` to `[k]G`. No polylogarithmic algebraic evaluation from `Q` is
known.

As a limited recurrence diagnostic, the frozen screen computes the binary
Berlekamp-Massey linear complexity of `rho`, `R3`, and `H`. On the largest
retained case of order `3469`:

```text
linear complexity rho:   1734
linear complexity R3:    1734
linear complexity H:     1734
available sequence:      3468 terms
```

The same approximately half-length behavior occurs across the larger cases.
This is consistent with pseudorandom recurrence behavior and gives no evidence
for a short linear recurrence. It is not a circuit lower bound.

## 8. Exact result of this package

The package obtains both a positive and a negative result.

### Positive structural result

An explicit odd, Kummer-invariant, GLV-compatible hidden section exists:

```text
R3(Q)=rho(Q)rho(phi Q)rho(phi^2 Q).
```

Moreover, public absolute orbit norms have transformation laws containing this
odd product.

### Negative cryptanalytic result

For the first torsion jet the odd product remains multiplied by exactly the
same GLV carry character as the public point-function norm, so the equations
are dependent. Fixed affine net pulls collapse by an exact carry cocycle. The
smallest natural `chi(x^3+a)` algebra gives no exact or statistically
distinguished decoder.

No sub-square-root EDS-residue algorithm has been obtained.

## 9. New bottleneck

The search is now narrower than “find an absolute section.”

The required object is:

```text
a public absolute section A(Q)
such that its C3 orbit norm obeys

product_i chi(A(phi^i Q))
  = constant * (-1)^(epsilon*gamma(Q)) * R3(Q),

with epsilon different from the point-function orbit exponent.
```

Equivalently, we need either:

1. a second section with a different GLV carry multiplier;
2. a public decoder for the canonical GLV carry `gamma(Q)`;
3. a direct public decoder for `R3(Q)`;
4. a global theta or sigma monodromy whose trivialization is not the standard
   quadratic EDS normalization.

The highest-value successor is provisionally named:

```text
GLV-CARRY-SEPARATION-005.
```

Its first task is to classify the GLV-orbit multiplier of every efficiently
evaluable algebraic section already present in the repository. If all of them
share the point-function multiplier, that becomes a scoped normalization
rigidity theorem. If one differs, the two orbit equations isolate `R3`.

## 10. Frozen artifacts

- `experiments/parity_lift_000/nonlocal_odd_anchor_screen.py`
- `experiments/parity_lift_000/nonlocal_odd_anchor_results.json`

## Primary mathematical anchors

- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*, especially the perfectly periodic point function and the public
  adjacent residue ratio.
- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*, especially the
  quadratic equivalence of elliptic nets and the integral-matrix
  transformation formula.
- Repository packages `RELATIVE-RESIDUE-GAUGE-001`,
  `ABSOLUTE-EDS-SECTION-003`, and the secp256k1 GLV covariance results.
