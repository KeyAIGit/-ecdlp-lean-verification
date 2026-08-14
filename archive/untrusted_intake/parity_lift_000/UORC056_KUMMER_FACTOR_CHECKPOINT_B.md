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
| B7A oriented principal Pell factor | exact generator-oriented principal section and polynomial-Pell norm equation | positive target normal form; direct construction remains large |
| B8 alternating Miller primitive | exact oriented potential `H_G` found; norm and two-step edge are compact Miller data | positive structural reduction |
| B9 alternating Miller segment | exact segment composition; explicit support `min(2m+2,n)`; norm gives reflected quotient only | endpoint primitive still missing |
| B10 sigma multiplication period | parity half has trivial translation stabilizer; prime cycle has no proper nontrivial subgroup period | full kernel norm only |
| B11 Miller monomial support | direct ordinary Miller/line representation needs linearly many atoms, even after quotient correction | short monomial closed |
| B12 cyclic elliptic factorial | exact elliptic shifted-factorial presentation | candidate presentation, not a separate algorithm |
| B13 Hilbert-90 integration | projective local cocycle has `O(log n)` SLP; exact normalization is a cyclic norm; standard lift has `n` terms | compact local derivative, dense standard global lift |
| B14 endpoint/factorial equivalence | endpoint ratios and global cyclic factorial differ only by one public anchor scalar | the two open items are one mechanism |
| B15 standard cyclic-factorial boundary | root-of-unity shadow has dense half factors and all nonzero frequencies; standard q-holonomic/block routes meet square-root frontier and need hidden index or dual phase | standard special-function routes scoped closed |

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

B13 strengthens the local result. For the B7A principal factor `f_G`, the
translation cocycle

```text
h_G(P)=f_G(P+2G)/f_G(P)
```

has a projective representative consisting of one 255-bit Miller loop plus two
line factors. On secp256k1 that is 445 Miller line steps plus two external line
factors. The missing operations are its exact cyclic normalization and the
distinguished multiplicative Hilbert-90 lift.

## The two former open items are one

For any nonzero potential `F`, put

```text
E(P,Q)=F(Q)/F(P).
```

Then

```text
E(P,Q)E(Q,R)=E(P,R).
```

Conversely, any exact endpoint function with this composition law is recovered
from one public anchor row:

```text
F_(P0)(Q)=E(P0,Q),
E(P,Q)=F_(P0)(Q)/F_(P0)(P).
```

Therefore:

```text
endpoint-only segment evaluator
    <=> cyclic elliptic factorial/global-potential evaluator
```

up to one harmless scalar gauge. B14 closes them as two separate research
routes. It does not construct the common evaluator.

## Exact cost boundaries obtained in B

For secp256k1:

```text
standard two-set index work                 >= 2^128-1,
explicit higher-arity resultant root state  >= 240615969168004511545033772477625056927,
translation-polynomial support               = n,
standard linear CM character support         = n,
corrected direct Miller/line atom count       >= 14474011154664524427946373126085988481604695534884363047825645392689770186793,
standard explicit Hilbert-90/orbit state      = n,
standard two-level factorial/segment cost     >= 481231938336009023090067544955250113854.
```

The last bound is the exact ceiling obtained from

```text
w^2 >= 4M,
M=(n-1)/2.
```

It is a 129-bit quantity and therefore does not meet any fixed-epsilon
`n^(1/2-epsilon)` gate.

These are scoped representation/model bounds, not a universal arithmetic-
circuit lower bound.

## Standard cyclic-factorial closure

The closest toric shadow is

```text
O_n(X)=product_(j=0)^(M-1)(1-X q^(2j+1)),
E_n(X)=product_(j=1)^M    (1-X q^(2j)),
R_n(X)=O_n(X)/E_n(X).
```

It satisfies

```text
O_n(X)E_n(X)=(1-X^n)/(1-X),
R_n(q^2X)/R_n(X)=(1-X)(1-q^2X)/(1-qX)^2.
```

Thus the local q-difference is constant-size, but both half polynomials have
all `M+1` coefficients nonzero. The alternating exponent vector has every
nonzero additive Fourier frequency, with value

```text
(z-1)/(z+1)
```

at a nontrivial `n`-th root `z`.

Known indexed q-holonomic algorithms and ordinary baby-step/giant-step product
methods operate at the square-root frontier. They also require the numerical
term index or `q^m`. In the elliptic endpoint input that index is hidden, while
an analogue of `q^m` is a faithful dual character. On secp256k1 the base field
contains no nontrivial order-`n` root, and an explicit dual phase has extension
degree `(n-1)/6`.

Hence the standard q-factorial, cyclic-dilogarithm-state, smooth-subgroup FFT,
and two-level block mechanisms do not supply the required endpoint evaluator.

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
short products of ordinary Miller and line atoms,
explicit n-state Hilbert-90/circulant systems,
ordinary two-level factorial block products,
direct import of indexed q-holonomic algorithms,
root-of-unity states supplied as uncharged advice.
```

## Remaining central object

After B14 the two named open items are no longer separate. The one remaining
object is:

```text
compact distinguished global integration of the public Miller cocycle,
```

or equivalently:

```text
evaluate f_G(Q), H_G(Q), B_G^pol(x(Q))/A_G^pol(x(Q)),
or Y_G(x(Q))/y(Q)
without an explicit orbit state, hidden index, dual phase, or square-root-width
intermediate.
```

A positive result must be a genuinely nonlinear base-field identity or uniform
arithmetic circuit outside every scoped class above. A general impossibility
result would require a new circuit lower bound and has not been proved.

## Current verdict

```text
Endpoint-only segment evaluator as separate route        closed by equivalence
Cyclic factorial standard evaluator classes              scoped closed
Common unrestricted nonlinear evaluator                  open
Public parity evaluator                                  absent
Absolute EDS-residue evaluator                           absent
All-in sub-square-root algorithm                         absent
Positive compact local cocycle                           obtained
Remaining bottleneck                                     distinguished global integration
```