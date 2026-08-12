# MIXED-Y-HYBRID-TRANSFER-016

Date: 2026-08-12

Status: **conditional analytic boundary plus exact frozen Fourier replay**.

No external point, key, wallet, or production-sized discrete-log target is
accepted. This package constructs no carry oracle, no EDS-residue decoder, and
no unconditional sub-square-root secp256k1 algorithm.

## 1. Motivation

`PUBLIC-COORDINATE-SPECTRAL-BARRIER-014` closed the direct low-field-Fourier-L1
x-coordinate routes. In particular,

```text
half_x
field_carry_x
```

have only `O(log(p)/sqrt(p))` scalar-domain Fourier coefficients after the
field-to-group transfer. The strongest candidates remaining in the corrected
public census contain `y` or a multiplicative character of `y`:

```text
half_y
chi_y
field_carry_x * half_y
field_carry_x * chi_y
```

On the largest frozen order `4021`, their maximum normalized scalar-domain
Fourier coefficients are approximately:

```text
half_y                       0.0485515
chi_y                        0.0311209
field_carry_x * half_y       0.0626249
field_carry_x * chi_y        0.0565126
```

After multiplication by `sqrt(n)`, the values remain in a small constant range.
This package explains the exact Fourier bookkeeping and isolates the only
external theorem needed to turn that observation into a scoped analytic bound.

## 2. Scalar-domain setup

Let `E/F_p` be an ordinary elliptic curve and let `G` generate a cyclic subgroup
of order `n`. For a public point observable `H`, define

```text
h_H(k) = H([k]G),
hat_h_H(j) = (1/n) sum_k h_H(k) e_n(-j*k).
```

The target of a local sparse-Fourier route is an inverse-polylogarithmic
nonzero coefficient:

```text
|hat_h_H(j)| >= 1/polylog(n).
```

A coefficient of size `polylog(p)/sqrt(p)` is insufficient because the local
SFT runtime is polynomial in the reciprocal threshold.

## 3. Half-interval in the y-coordinate

For odd `p`, define the centered half-interval sign

```text
A_p(0) = 0,
A_p(y) = +1 for 1 <= [y]_p <= (p-1)/2,
A_p(y) = -1 for (p+1)/2 <= [y]_p <= p-1.
```

Its normalized additive Fourier transform satisfies

```text
||hat_A_p||_1 <= H_((p-1)/2) + 1 = O(log p).
```

Fourier inversion gives

```text
A_p(y(P)) = sum_b hat_A_p(b) e_p(b*y(P)).
```

Therefore

```text
hat_h_half_y(j)
  = sum_b hat_A_p(b)
      * (1/n) sum_k e_p(b*y([k]G)) e_n(-j*k).
```

The required analytic input is the uniform complete hybrid estimate

```text
sum_k e_p(b*y([k]G)) e_n(-j*k) = O(sqrt(p))
```

for nonzero `b` and nontrivial scalar character `j`. Under this input and
`n = p + O(sqrt(p))`, we obtain

```text
max_(j != 0) |hat_h_half_y(j)| = O(log(p)/sqrt(p)).
```

## 4. Quadratic character of y

Let `kappa` be the quadratic character of `F_p`, extended by `kappa(0)=0`.
Its additive Fourier transform is a normalized quadratic Gauss sum:

```text
|hat_kappa(b)| = 1/sqrt(p) for b != 0,
hat_kappa(0) = 0,
||hat_kappa||_1 = (p-1)/sqrt(p).
```

Using this field Fourier `L1` directly with only additive hybrid sums would lose
a factor `sqrt(p)` and produce no useful bound. The right analytic object is
instead the complete Kummer hybrid sum

```text
sum_k kappa(y([k]G)) e_n(-j*k).
```

For a fixed rational function `y` which is not a square on the curve, the
standard fixed-conductor Kummer plus group-character estimate is expected to be

```text
O(sqrt(p)).
```

Under that theorem,

```text
max_(j != 0) |hat_h_chi_y(j)| = O(1/sqrt(p)).
```

This is stronger than the half-interval bound, but the theorem is an external
algebro-geometric input and is not formalized in this repository.

## 5. Field carry times half-y

The public field GLV carry is

```text
C_beta(x)
  = 2 * (B_p(x) + B_p(beta*x) + B_p(beta^2*x)),
```

where `B_p` is the centered sawtooth. Its normalized field Fourier `L1` obeys

```text
||hat_C_beta||_1 <= 3 H_((p-1)/2) = O(log p).
```

The product observable has the two-dimensional expansion

```text
C_beta(x(P)) A_p(y(P))
  = sum_(a,b) hat_C_beta(a) hat_A_p(b)
      e_p(a*x(P) + b*y(P)).
```

The tensor `L1` norm factors exactly:

```text
sum_(a,b) |hat_C_beta(a) hat_A_p(b)|
  = ||hat_C_beta||_1 ||hat_A_p||_1
  = O(log(p)^2).
```

Assuming the complete two-coordinate hybrid estimate

```text
sum_k e_p(a*x([k]G)+b*y([k]G)) e_n(-j*k)
  = O(sqrt(p))
```

uniformly for nonzero `(a,b)`, the scalar-domain coefficient satisfies

```text
max_(j != 0)
  |widehat(C_beta(x)*A_p(y))(j)|
    = O(log(p)^2/sqrt(p)).
```

## 6. Field carry times chi-y

The multiplicative observable

```text
C_beta(x(P)) kappa(y(P))
```

should not be bounded by first expanding `kappa` additively, because that has
field Fourier `L1` of order `sqrt(p)`. Instead expand only the carry:

```text
C_beta(x(P)) kappa(y(P))
  = sum_a hat_C_beta(a)
      e_p(a*x(P)) kappa(y(P)).
```

The required external estimate is the additive-Kummer hybrid sum

```text
sum_k e_p(a*x([k]G)) kappa(y([k]G)) e_n(-j*k)
  = O(sqrt(p)).
```

Combined with `||hat_C_beta||_1=O(log p)`, this gives

```text
max_(j != 0)
  |widehat(C_beta(x)*kappa(y))(j)|
    = O(log(p)/sqrt(p)).
```

## 7. Exact finite transfer envelope

`Ecdlp/Proved/MixedYHybridTransferBoundary.lean` proves the finite arithmetic
step used in each transfer:

```text
if hybridNorm(i) <= M for every i,
then sum_i coefficientNorm(i)*hybridNorm(i)
     <= M * sum_i coefficientNorm(i).
```

It also proves exact tensor `L1` factorization. Lean does not prove that the
hybrid sums themselves have the required square-root bounds.

## 8. Frozen replay

`experiments/parity_lift_000/mixed_y_hybrid_transfer.py` checks:

```text
half-interval field Fourier L1 bounds,
quadratic-character Gauss-spectrum magnitudes,
field-carry centered-sawtooth identity,
field-carry field Fourier L1 bounds,
tensor L1 factorization for carry*half and carry*chi,
selected scalar-domain spectra from the normalization-aware census.
```

For every selected candidate and every frozen case with order at least `500`,
the measured maximum scalar-domain coefficient is below `1/log(n)`.

The `sqrt(n)`-scaled coefficients remain bounded by small constants across the
large frozen cases. This is evidence consistent with the conditional analytic
bounds above, not an independent asymptotic theorem.

## 9. Conditional complexity consequence

Under the stated fixed-conductor complete hybrid-sum estimates, the four
selected observables have thresholds at most

```text
half_y                       O(log(p)/sqrt(p))
chi_y                        O(1/sqrt(p))
field_carry_x * half_y       O(log(p)^2/sqrt(p))
field_carry_x * chi_y        O(log(p)/sqrt(p))
```

Their reciprocal thresholds are exponential in the bit length `log p`, up to
polylogarithmic factors. None of these routes supplies a polynomial-time local
SFT reduction for secp256k1.

## 10. What this closes and what remains

Conditionally closed named candidates:

```text
half_y
chi_y
field_carry_x * half_y
field_carry_x * chi_y
```

Still open:

```text
field-permutation orientation and products containing it,
high-field-Fourier-L1 point circuits,
high-conductor or order-dependent rational functions,
non-coordinate analytic or p-adic monodromy,
a direct public R3 decoder,
a direct public cyclotomic carry section,
Lean formalization of the required Weil-Deligne or character-sheaf theorem.
```

The most structured next target is the integer ordering predicate

```text
field_permutation(x)
  = sign((x0-x1)(x1-x2)(x2-x0)),
```

where `x0`, `x1`, `x2` are the canonical integer representatives of the field
GLV orbit. Its frozen field Fourier `L1` appears logarithmic and its principal
coefficient appears close to `1/pi`, but no exact decomposition has yet been
proved.

Proposed next package:

```text
FIELD-PERMUTATION-FOURIER-017
```

## 11. Frozen artifacts

```text
experiments/parity_lift_000/mixed_y_hybrid_transfer.py
Ecdlp/Proved/MixedYHybridTransferBoundary.lean
.github/workflows/mixed-y-hybrid-transfer.yml
```

## Primary anchors

1. Adi Akavia, *Finding Significant Fourier Transform Coefficients
   Deterministically and Locally*, for the dependence on the Fourier threshold
   and `L1` norm.
2. Omran Ahmadi and Igor Shparlinski, *Exponential Sums over Points of Elliptic
   Curves*, for the square-root scale of complete twisted elliptic sums in the
   x-coordinate case and the general function-field framework.
3. The standard Weil-Deligne theory of fixed-conductor Artin-Schreier, Kummer,
   and mixed character sheaves for the three y-dependent hybrid estimates.
4. Kristin Lauter and Katherine Stange, *The Elliptic Curve Discrete Logarithm
   Problem and Equivalent Hard Problems for Elliptic Divisibility Sequences*,
   for the parity-oracle and EDS-residue reductions.

## Claim boundary

The finite field Fourier identities, Gauss-spectrum identities, tensor `L1`
factorization, and frozen scalar spectra are checked directly. The mixed-y
square-root estimates are external analytic inputs and remain unformalized.
This is a conditional scoped no-go statement for four explicit observables, not
a universal lower bound for all public predicates or all ECDLP algorithms.
