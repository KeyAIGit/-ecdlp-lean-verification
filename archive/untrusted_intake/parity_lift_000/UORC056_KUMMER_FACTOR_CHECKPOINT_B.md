# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 - KUMMER/CM TRACK B CHECKPOINT

Date: 2026-08-14

Central target, unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
all-in cost O(n^(1/2-epsilon)).
```

## Completed mechanism classes

| Package | Exact result | Disposition |
|---|---|---|
| B1 prime-norm CM factor | `Norm(alpha)=n` prime prevents a proper lower-degree CM-isogeny chain | closed scoped class |
| B2 Miller kernel edge | fast Miller character is a relative two-endpoint EDS edge | no absolute orientation |
| B3 compact Frobenius kernel | `Frob-id` yields the rational kernel, `K_H^2`, and local squares | generator-blind |
| B4 oriented half-divisor | parity half has Picard class `[M]G` of order `n`; even/odd x-multisets coincide | branch is line-bundle data |
| B4 standard sqrt-Velu index | every two-set index system has work at least `ceil(sqrt(n))-1` | square-root frontier |
| B5 higher-arity explicit resultants | root of any explicit binary resultant tree has state `Omega(sqrt(M))` | square-root frontier |
| B6 transposed linear evaluation | `(I+T)^(-1)` for parity has exact translation support `n` | dense linear state |
| B7 linear CM recurrence | nontrivial eigenline is a full order-`n` character; parity uses all frequencies | no bounded linear state |
| B8 alternating Miller primitive | exact oriented potential `H_G` found; norm and two-step edge are compact Miller data | positive structural reduction |
| B9 alternating Miller segment | exact segment composition; explicit support `min(2m+2,n)`; norm gives reflected quotient only | endpoint primitive still missing |
| B10 sigma multiplication period | parity half has trivial translation stabilizer; prime cycle has no proper nontrivial subgroup period | full kernel norm only |
| B11 Miller monomial support | direct ordinary Miller/line representation needs linearly many atoms, even after quotient correction | short monomial closed |
| B12 cyclic elliptic factorial | exact special-function candidate specified; no finite-field sub-root evaluator identified | open nonlinear candidate |

## Strongest positive result of track B

Define

```text
H_G(P)=product_(j=1)^M g_([(2j-1)]G,G)(P),
n=2M+1.
```

Then

```text
div(H_G)=-Delta_G+M(G)-M(O),
```

and

```text
div(f_(M,G)/H_G)=Delta_G-([M]G)+(O).
```

Away from the one public exceptional point `[M]G`, the local order of this ratio is exactly canonical scalar parity.

Furthermore:

```text
H_G(P)H_G(-P)
 = public constant
   * f_(n,G)(P) f_(M,-G)(P)/f_(M+1,G)(P),
```

and

```text
H_G(P+2G)/H_G(P)
```

has a four-point generalized-Miller divisor. Thus the local oriented edge is compact and public.

The missing operation is now exactly:

```text
from public endpoints P,Q=P+[2m]G,
evaluate H_G(Q)/H_G(P)
without knowing or walking m.
```

This is the concrete structured segment primitive handed to track A.

## Exact cost boundaries obtained in B

For secp256k1:

```text
standard two-set index work               >= 2^128-1,
explicit higher-arity resultant root state >= 240615969168004511545033772477625056927,
translation-polynomial support             = n,
standard linear CM character support       = n,
corrected direct Miller/line atom count     >= 14474011154664524427946373126085988481604695534884363047825645392689770186793.
```

These are scoped representation bounds, not a universal arithmetic-circuit lower bound.

## What B no longer needs to repeat

Do not repeat:

```text
symmetric kernel products,
ordinary Velu/index systems,
more explicit resultant levels,
transposed interpolation with oriented samples supplied,
linear combinations of finitely many CM characters,
full dual-character or pairing representations,
proper-period subgroup sigma products,
short products of ordinary Miller and line atoms.
```

## Remaining B-only possibility

The alternating Miller product can be written, under sigma uniformization and up to a point-independent factor, as a ratio of finite elliptic shifted factorials with step `2G`. This is the only clearly identified B-specific nonlinear candidate.

A positive result must give an exact base-field evaluator for that cyclic elliptic factorial without:

```text
walking the unknown segment,
expanding M factors,
materializing a square-root-degree intermediate,
using a full dual phase,
or storing the oriented Kummer table.
```

The external literature confirms that elliptic shifted factorials and root-of-unity cyclic-dilogarithm identities are genuine special-function classes. The present audit did not identify a formula satisfying this finite-field evaluator and cost gate. This is absence of a found construction, not a theorem of nonexistence.

## Current verdict

```text
Public parity evaluator                         absent
Absolute EDS-residue evaluator                  absent
All-in sub-square-root algorithm                absent
Positive compact local cocycle                  obtained
Remaining bottleneck                            endpoint integration / cyclic elliptic factorial evaluation
```