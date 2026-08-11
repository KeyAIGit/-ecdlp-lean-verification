# CHAR-PARITY-001: finite-field character decoders

Date: 2026-08-11

Status: **untrusted theorem draft plus bounded toy evidence**. This file is
quarantined from canonical evidence and Research Engine state. It authorizes no
production-sized computation and claims no ECDLP improvement.

## 1. Candidate class

Let `E/F_q` have a cyclic odd prime-order rational group

```text
E(F_q) = <G>,    #E(F_q)=n.
```

Let `chi` be the quadratic character of `F_q`. The candidate decoder class is

```text
chi(f(Q)) = (-1)^k,    Q=[k]G,    0<=k<n,
```

where `f` is a public rational, theta, division-polynomial, or otherwise
structured expression that is nonzero and finite on every rational group point.

This class survives the Kummer obstruction because `chi(f(Q))` may be
sign-sensitive even when `f` takes many field values.

## 2. Exact Fourier demand imposed by parity

Put

```text
zeta = exp(2*pi*i/n),
eta_j([k]G) = zeta^(-j*k).
```

For the parity sign `s(k)=(-1)^k`,

```text
S(j) = sum_(k=0)^(n-1) s(k) eta_j([k]G)
     = 2 / (1 + zeta^(-j)).
```

Every coefficient is nonzero. For

```text
j = (n-1)/2,
```

one has

```text
|S(j)| = 1 / sin(pi/(2*n)) >= 2*n/pi.
```

Therefore an exact character decoder forces the complete mixed sum

```text
sum_(P in E(F_q)) chi(f(P)) eta_j(P)
```

to have magnitude at least `2*n/pi` for this nontrivial order-`n` group
character.

## 3. Sheaf-theoretic conductor bound

The following is a precise draft theorem, conditional only on the standard
rank-one trace-function and cohomological facts listed below.

Let `S` be the geometric zeros and poles of `f` at which the valuation of `f`
is odd, and put `r=#S`. Over

```text
U = E minus S,
```

consider:

1. the quadratic Kummer local system pulled back by `f`;
2. the rank-one Lang local system whose Frobenius trace on `E(F_q)` is `eta_j`;
3. their tensor product `F`.

The Lang construction is explicit: for a connected algebraic group over a
finite field, a character of its rational points determines a rank-one local
system through the Lang covering, and its Frobenius trace recovers that
character. An accessible primary implementation is Section 2.1 of
Dobrovolska, Ginzburg and Travkin, arXiv:1612.01733.

When `r>0`, the tensor product is tame of rank one and geometrically
nontrivial. On the genus-one curve with `r` punctures, the
Grothendieck-Ogg-Shafarevich formula gives

```text
dim H_c^1(U_bar,F) = r,
```

provided `H_c^0=H_c^2=0`. Deligne's weight bound then gives

```text
|sum_(P in E(F_q)) chi(f(P)) eta_j(P)| <= r*sqrt(q).
```

Combining this with the exact parity Fourier coefficient yields

```text
r >= 1 / (sqrt(q)*sin(pi/(2*n)))
  >= 2*n/(pi*sqrt(q)).
```

If `d` is the degree of the pole divisor of `f`, then `r<=2*d`, so

```text
d >= 1 / (2*sqrt(q)*sin(pi/(2*n)))
  >= n/(pi*sqrt(q)).
```

### Unramified exceptional case

If `r=0`, the Kummer local system is geometrically unramified and has order at
most two. The Lang local system for `eta_j` has odd prime order `n`. Their
tensor cannot be geometrically trivial. On a complete genus-one curve a
nontrivial unramified rank-one local system has zero compactly supported Euler
characteristic and no degree-zero or degree-two cohomology, hence its complete
trace sum is zero. This contradicts the nonzero parity Fourier coefficient.

Thus an exact decoder in this class must have `r>0` and satisfy the displayed
conductor bound.

### Rational exceptions

If a decoder special-cases `e` rational group points, the Fourier coefficient
can change by at most `e` in absolute value. The bound becomes approximately

```text
r*sqrt(q) >= 1/sin(pi/(2*n)) - e.
```

A bounded exceptional set does not alter the square-root-scale conclusion.

## 4. Primary-curve numerical consequence

For the standard secp256k1 values

```text
q = p = 2^256 - 2^32 - 977,
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
```

the draft lower bounds are approximately

```text
r >= 216630482969909636093804454941121895873,
d >= 108315241484954818046902227470560947937,
log2(d) >= 126.3485.
```

Interpretation: an exact quadratic-character parity decoder cannot come from a
bounded-degree or small-level rational/theta expression. Its geometric
conductor must already be near the square-root scale.

## 5. Critical limitation: degree is not evaluation time

The preceding result is not a time lower bound.

A rational expression may have very high algebraic degree and still admit a
short evaluation circuit. Division polynomials are the main warning: their
degrees grow quadratically in the index, but addition-chain and recurrence
formulas can evaluate them without expanding every coefficient.

Consequently `CHAR-PARITY-001` closes low-degree and low-conductor decoders, but
it does not close structured high-degree observables.

This moves the highest-value live question to
`STRUCTURED-CHAR-PARITY-002`:

```text
Can chi(psi_m(Q)), a ratio/product of division polynomials, an EDS term, or a
theta multiplication expression equal canonical scalar parity while retaining
polylogarithmic or otherwise sub-square-root evaluation cost?
```

Shparlinski and Stange, arXiv:0912.5246, obtain nontrivial bounds for quadratic
character sums of division-polynomial values. Later work studies shifted
correlations and multiplicatively twisted versions. These sources are directly
relevant to ruling in or ruling out the structured loophole.

## 6. Bounded toy screen

The reproducible program

```text
experiments/parity_lift_000/char_parity_toy_screen.py
```

uses only the five frozen prime-order curves

```text
y^2=x^3+7 over F_43, F_67, F_79, F_127, F_163.
```

It exhaustively enumerates projectively normalized affine forms

```text
L(x,y)=A*x+B*y+C
```

that are nonzero on the nonidentity cyclic orbit, represents each sign sequence
`chi(L([k]G))` as a bit vector, and tests products by XOR and
meet-in-the-middle search.

### Negative bounded results

Across all five curves:

- `chi(y)` is not exact for any generator choice or global sign;
- no single valid affine line gives exact parity;
- no product or ratio of two valid affine lines gives exact parity.

The best `chi(y)` accuracies after optimizing the generator and global sign are:

| p | n | best matches | accuracy |
|---:|---:|---:|---:|
| 43 | 31 | 24/30 | 0.8000 |
| 67 | 79 | 50/78 | 0.6410 |
| 79 | 67 | 46/66 | 0.6970 |
| 127 | 127 | 76/126 | 0.6032 |
| 163 | 139 | 84/138 | 0.6087 |

The deep bounded search additionally finds:

- no product of at most four valid lines over `F_67`;
- no product of at most three valid lines over `F_79`.

### Exact toy counterexample

Over

```text
E/F_43: y^2=x^3+7,
G=(2,12),
#E(F_43)=31,
```

the following exact identity holds for every `1<=k<31`:

```text
chi(
  (x([k]G)+17)
  *(x([k]G)+y([k]G)+41)
  *(x([k]G)+42*y([k]G)+41)
  *y([k]G)
) = (-1)^k.
```

The exhaustive line-factor search proves that weight four is minimal within
this frozen product-of-affine-lines family: no weight one, two, or three
solution exists.

This is not an attack. The formula is generator-specific finite interpolation
on 30 nonidentity points. Its value is conceptual:

1. nonlinear character decoders are not universally impossible on finite toy
   groups;
2. the obstruction must be quantitative and scaling-sensitive;
3. low-degree successes may exist sporadically while their required conductor
   grows with the group;
4. the next experiment must measure formula complexity across increasing
   independently held-out curves, not merely search for one toy identity.

## 7. Current disposition

| question | answer |
|---|---|
| Can a bounded-degree character decoder work uniformly at cryptographic scale? | The draft conductor bound says no. |
| Can an exact nonlinear decoder exist on a finite toy group? | Yes; the `F_43` four-line identity proves existence. |
| Does the toy identity scale or reveal a construction? | No evidence. |
| Are structured high-degree, fast-evaluation decoders closed? | No. This is the principal surviving line. |

## 8. Validation and remaining proof obligations

Completed:

- exact parity Fourier transform;
- high-precision secp256k1 numerical evaluation;
- toy curve, orbit, character, line enumeration, and meet-in-the-middle replay;
- explicit `F_43` identity verification;
- exact no-solution statements inside the declared bounded line-factor spaces.

Still required before promotion from untrusted draft:

1. pin exact theorem statements for the Lang character local system,
   Grothendieck-Ogg-Shafarevich formula, and Deligne weight bound;
2. audit geometric nontriviality in both ramified and unramified cases;
3. formalize treatment of zeros, poles, and rational exceptions;
4. independently replay the numerical and toy artifacts;
5. distinguish conductor, straight-line program, recurrence, preprocessing, and
   online evaluation costs;
6. test the structured division-polynomial and EDS family without using
   production-sized targets.
